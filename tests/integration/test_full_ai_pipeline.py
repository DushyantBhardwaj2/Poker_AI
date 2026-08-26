"""End-to-end pass over the three AI layers, with no HTTP and no database.

This file used to be a script: it printed each stage and asserted nothing, so the
only failure it could report was a crash. It reported one, too, because it read
the advisor's result as a dict (`advice['action']`) long after `recommend()`
started returning an `AdvisorResponse` model, and nobody noticed until pytest was
pointed at the directory.
"""

import pytest

from packages.ai.bluff_detector import BluffDetector
from packages.ai.feature_mapper import FeatureMapper
from packages.ai.smart_advisor import SmartAdvisor
from packages.ai.win_probability import WinProbabilityCalculator
from packages.domain.models import (
    ActionRecord,
    ActionType,
    Card,
    ConfidenceLevel,
    GameRound,
    GameState,
    Player,
    Rank,
    Suit,
)

pytestmark = pytest.mark.integration

POT = 1000.0
CALL_AMOUNT = 500.0
STACK = 5000.0
TIGHT_VPIP = 0.20
TIGHT_PFR = 0.15


@pytest.fixture
def flop_state():
    """Hero holds A-K on an A-7-2 flop; the opponent has bet half pot into it."""
    hole_cards = [
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.KING, suit=Suit.HEARTS),
    ]
    community = [
        Card(rank=Rank.ACE, suit=Suit.DIAMONDS),
        Card(rank=Rank.SEVEN, suit=Suit.CLUBS),
        Card(rank=Rank.TWO, suit=Suit.HEARTS),
    ]
    state = GameState(
        players=[
            Player(name="Hero", stack=STACK, hole_cards=hole_cards),
            Player(name="Opponent", stack=STACK),
        ],
        community_cards=community,
        pot=POT,
        round=GameRound.FLOP,
        current_bet=CALL_AMOUNT,
        current_player_index=0,
        small_blind=10,
        big_blind=20,
    )
    history = [
        ActionRecord(
            player_name="Opponent",
            action_type=ActionType.RAISE,
            amount=CALL_AMOUNT,
            street=GameRound.FLOP,
        )
    ]
    return state, history, hole_cards, community


def test_pipeline_produces_a_coherent_recommendation(flop_state):
    state, history, hole_cards, community = flop_state

    equity = WinProbabilityCalculator.calculate(
        hole_cards,
        community,
        num_opponents=1,
        # Keyword arguments on purpose. The fourth positional parameter is the
        # simulation count, not the pot, and passing 1000 for "pot" happened to
        # match the default so the mistake was invisible.
        num_simulations=200,
        opponent_vpip=TIGHT_VPIP,
    )
    win_probability = equity["win_probability"]
    # Top pair, top kicker against one range-restricted opponent. The band is wide
    # on purpose: this asserts the simulation is wired up, not its exact variance.
    assert 0.70 < win_probability < 1.0

    live_state = FeatureMapper.map_to_live_state(
        state, history, {"vpip": TIGHT_VPIP, "pfr": TIGHT_PFR}
    )
    read = BluffDetector().predict(live_state)
    bluff_probability = read["bluff_probability"]
    assert 0.0 <= bluff_probability <= 1.0
    assert read["is_bluff"] is (bluff_probability >= read["threshold"])

    advice = SmartAdvisor.recommend(
        win_probability=win_probability,
        bluff_probability=bluff_probability,
        pot_size=POT,
        call_amount=CALL_AMOUNT,
        player_stack=STACK,
    )

    assert isinstance(advice.action, ActionType)
    assert isinstance(advice.confidence_level, ConfidenceLevel)
    assert advice.explanation.strip()
    assert advice.explanation_structured.main.strip()

    tactical = advice.tactical_data
    assert tactical.win_probability == pytest.approx(win_probability)
    # 500 to call into a 1000 pot.
    assert tactical.pot_odds == pytest.approx(CALL_AMOUNT / (POT + CALL_AMOUNT))
    assert advice.pot_odds == pytest.approx(tactical.pot_odds)
    assert advice.ev == pytest.approx(tactical.expected_value)

    # A hand this far ahead of the price is a raise, not a call.
    assert advice.action == ActionType.RAISE
    assert tactical.adjusted_win_probability > tactical.win_probability


def test_a_bluff_read_only_ever_helps_the_call(flop_state):
    """The whole point of the behavioral layer: it raises effective equity."""
    _, _, hole_cards, community = flop_state
    win_probability = 0.45

    adjusted = [
        SmartAdvisor.recommend(
            win_probability=win_probability,
            bluff_probability=p,
            pot_size=POT,
            call_amount=CALL_AMOUNT,
            player_stack=STACK,
            opponent_sample_size=100,
        ).tactical_data.adjusted_win_probability
        for p in (0.0, 0.3, 0.6, 0.9)
    ]

    assert adjusted == sorted(adjusted)
    assert adjusted[0] == pytest.approx(win_probability, abs=0.01)


def test_a_thin_sample_is_shrunk_toward_the_baseline(flop_state):
    """With no history on an opponent the model's read is mostly ignored."""
    kwargs = dict(
        win_probability=0.45,
        bluff_probability=0.90,
        pot_size=POT,
        call_amount=CALL_AMOUNT,
        player_stack=STACK,
    )

    cold = SmartAdvisor.recommend(**kwargs, opponent_sample_size=0)
    warm = SmartAdvisor.recommend(**kwargs, opponent_sample_size=50)

    # weight = hands / 50, so at zero hands only the 15% baseline survives.
    assert cold.tactical_data.bluff_probability == pytest.approx(0.15)
    assert warm.tactical_data.bluff_probability == pytest.approx(0.90)
    assert cold.data_quality is None or cold.data_quality.sample_size == 0
