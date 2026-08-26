"""The bluff detector against the live model artifact.

This exercises the real `.joblib` in packages/ai/models, not a stub, so it is the
test that catches a feature-order change between training and inference: the model
is fed a plain array, so a reordered column is silently wrong rather than an error.

It used to open a database session, look up a user, create an opponent, and then
never use any of it, printing two probabilities and asserting nothing.
"""

import pytest

from packages.ai.bluff_detector import BluffDetector
from packages.ai.feature_mapper import FeatureMapper
from packages.domain.models import (
    ActionRecord,
    ActionType,
    Card,
    GameRound,
    GameState,
    Player,
    Rank,
    Suit,
)

pytestmark = pytest.mark.integration

# The 16 columns the model was trained on, in order. Recomputed at inference by
# packages/ai/bluff_detector.py and documented in ml_modules/MAKING_OF_ML_MODULE.md.
EXPECTED_FEATURES = [
    "street",
    "rel_bet_size",
    "bet_spike",
    "dryness",
    "dryness_delta",
    "bet_bin",
    "vpip",
    "pfr",
    "spr",
    "bet_size_diff",
    "is_monotonic",
    "range_miss",
    "dryness_bet_interaction",
    "vpip_bet_interaction",
    "tightness_bet_interaction",
    "agg_profile",
]

DRY_BOARD = [
    Card(rank=Rank.ACE, suit=Suit.HEARTS),
    Card(rank=Rank.TWO, suit=Suit.DIAMONDS),
    Card(rank=Rank.SEVEN, suit=Suit.CLUBS),
    Card(rank=Rank.QUEEN, suit=Suit.SPADES),
    Card(rank=Rank.THREE, suit=Suit.HEARTS),
]

WET_BOARD = [
    Card(rank=Rank.EIGHT, suit=Suit.SPADES),
    Card(rank=Rank.SEVEN, suit=Suit.SPADES),
    Card(rank=Rank.SIX, suit=Suit.SPADES),
    Card(rank=Rank.FIVE, suit=Suit.CLUBS),
    Card(rank=Rank.TWO, suit=Suit.HEARTS),
]


@pytest.fixture(scope="module")
def detector():
    """Loading the artifact takes long enough to be worth doing once."""
    return BluffDetector()


def river_overbet(board, vpip, pfr):
    """An opponent firing 1500 into a 2500 pot on the river."""
    state = GameState(
        players=[
            Player(
                name="Hero",
                stack=4000,
                hole_cards=[
                    Card(rank=Rank.ACE, suit=Suit.SPADES),
                    Card(rank=Rank.KING, suit=Suit.SPADES),
                ],
            ),
            Player(name="Opponent", stack=3000, hole_cards=[]),
        ],
        community_cards=board,
        pot=2500,
        round=GameRound.RIVER,
        small_blind=10,
        big_blind=20,
        current_player_index=1,
    )
    history = [
        ActionRecord(
            player_name="Opponent",
            action_type=ActionType.RAISE,
            amount=1500,
            street=GameRound.RIVER,
        )
    ]
    return FeatureMapper.map_to_live_state(state, history, {"vpip": vpip, "pfr": pfr})


def test_the_feature_vector_matches_what_the_model_was_trained_on(detector):
    read = detector.predict(river_overbet(DRY_BOARD, vpip=0.15, pfr=0.12))
    assert list(read["features_snapshot"]) == EXPECTED_FEATURES


def test_a_prediction_is_a_probability_with_a_verdict(detector):
    read = detector.predict(river_overbet(DRY_BOARD, vpip=0.15, pfr=0.12))

    assert 0.0 <= read["bluff_probability"] <= 1.0
    assert read["is_bluff"] is (read["bluff_probability"] >= read["threshold"])
    assert read["street_rank"] == 3  # river


def test_the_same_overbet_reads_looser_from_a_looser_player(detector):
    """The tightness/bet interaction is the feature this is really testing.

    An identical bet size has to mean different things depending on who made it,
    which a tree cannot work out from vpip and rel_bet_size separately.
    """
    nit = detector.predict(river_overbet(DRY_BOARD, vpip=0.15, pfr=0.12))
    maniac = detector.predict(river_overbet(WET_BOARD, vpip=0.75, pfr=0.60))

    assert maniac["bluff_probability"] > nit["bluff_probability"]


@pytest.mark.parametrize("board", [DRY_BOARD, WET_BOARD])
def test_the_threshold_is_flat_across_streets(detector, board):
    """Pins a known limitation so it cannot drift out of the documentation.

    Training calibrates a threshold for 70% precision and only logs it; both
    inference paths hardcode 0.4 regardless of street, even though turn and river
    precision differ by 22 points at that cutoff. If this assertion ever fails
    because the threshold became street-aware, that is the fix landing, and the
    Limitations sections of README.md and ml_modules/MAKING_OF_ML_MODULE.md need
    updating with it.
    """
    read = detector.predict(river_overbet(board, vpip=0.30, pfr=0.20))
    assert read["threshold"] == 0.4
