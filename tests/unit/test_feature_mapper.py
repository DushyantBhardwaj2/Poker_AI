from packages.domain.models import GameState, Player, Card, Rank, Suit, GameRound, ActionRecord, ActionType
from packages.ai.feature_mapper import FeatureMapper


def make_state(round=GameRound.RIVER, pot=2500, current_bet=1500, players=None, current_player_index=0):
    if players is None:
        players = [
            Player(name="Hero", stack=4000, hole_cards=[
                Card(rank=Rank.ACE, suit=Suit.SPADES), Card(rank=Rank.KING, suit=Suit.SPADES)
            ]),
            Player(name="Villain", stack=3000, hole_cards=[])
        ]
    return GameState(
        players=players,
        community_cards=[
            Card(rank=Rank.ACE, suit=Suit.HEARTS),
            Card(rank=Rank.TWO, suit=Suit.DIAMONDS),
            Card(rank=Rank.SEVEN, suit=Suit.CLUBS),
            Card(rank=Rank.QUEEN, suit=Suit.SPADES),
            Card(rank=Rank.THREE, suit=Suit.HEARTS)
        ],
        pot=pot,
        current_bet=current_bet,
        round=round,
        small_blind=10,
        big_blind=20,
        current_player_index=current_player_index
    )


class TestFeatureMapper:
    def test_empty_history_falls_back_safely(self):
        state = make_state()
        live = FeatureMapper.map_to_live_state(state, [], {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount == 0.0
        assert live.pot_before > 0
        assert live.prev_street_max_bet == 0.0
        assert live.prev_action_bet_size == 0.0
        assert live.street == 3
        assert live.vpip == 0.25
        assert live.pfr == 0.18

    def test_raise_sets_bet_amount(self):
        state = make_state()
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount > 0
        assert live.bet_amount == 1500 / 20

    def test_prev_street_max_bet_computed(self):
        state = make_state()
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=800, street=GameRound.TURN),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.prev_street_max_bet > 0
        assert live.prev_street_max_bet == 800 / 20

    def test_all_in_sets_bet_amount(self):
        state = make_state(pot=5000, current_bet=3000)
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.ALL_IN, amount=3000, street=GameRound.RIVER)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount > 0

    def test_call_not_treated_as_aggressive_if_raise_exists(self):
        state = make_state()
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.CALL, amount=200, street=GameRound.FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount == 1500 / 20

    def test_call_fallback_when_no_raise(self):
        state = make_state()
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.CALL, amount=200, street=GameRound.RIVER)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount == 200 / 20

    def test_multiple_actions_prev_action_bet_size(self):
        state = make_state()
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.TURN),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.prev_action_bet_size > 0

    def test_sparse_history_one_action(self):
        state = make_state(round=GameRound.TURN, pot=1000, current_bet=500)
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.TURN)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.street == 2
        assert live.bet_amount > 0

    def test_preflop_no_history(self):
        state = make_state(round=GameRound.PRE_FLOP, pot=30, current_bet=20)
        live = FeatureMapper.map_to_live_state(state, [], {"vpip": 0.25, "pfr": 0.18})
        assert live.street == 0
        assert live.bet_amount == 0.0

    # ----- New correctness tests for current-street / opponent_name logic -----

    def test_old_street_raise_not_current_bet_when_current_bet_zero(self):
        """Previous-street raise must NOT become the current bet when current_bet == 0."""
        state = make_state(round=GameRound.TURN, pot=1000, current_bet=0)
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.FLOP)
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount == 0.0, f"Expected 0, got {live.bet_amount}"

    def test_opponent_name_excludes_hero_raise(self):
        """
        Hero raises, villain calls. opponent_name='Villain' should use villain's
        CALL as fallback, NOT the hero's RAISE.
        """
        state = make_state(round=GameRound.TURN, pot=600, current_bet=200)
        history = [
            ActionRecord(player_name="Hero", action_type=ActionType.RAISE, amount=200, street=GameRound.TURN),
            ActionRecord(player_name="Villain", action_type=ActionType.CALL, amount=200, street=GameRound.TURN),
        ]
        live = FeatureMapper.map_to_live_state(
            state, history, {"vpip": 0.25, "pfr": 0.18},
            opponent_name="Villain"
        )
        # Hero's RAISE is excluded — only CALL remains, which is fallback
        assert live.bet_amount == 200 / 20, f"Expected {200/20}, got {live.bet_amount}"

    def test_opponent_name_multiway_selects_correct_player(self):
        """
        Multiway hand: VillainA raises, VillainB calls.
        opponent_name='VillainB' should use VillainB's CALL, not VillainA's RAISE.
        """
        players = [
            Player(name="Hero", stack=4000),
            Player(name="VillainA", stack=3000),
            Player(name="VillainB", stack=3000),
        ]
        state = make_state(round=GameRound.TURN, pot=1200, current_bet=400, players=players)
        history = [
            ActionRecord(player_name="VillainA", action_type=ActionType.RAISE, amount=400, street=GameRound.TURN),
            ActionRecord(player_name="VillainB", action_type=ActionType.CALL, amount=400, street=GameRound.TURN),
        ]
        live = FeatureMapper.map_to_live_state(
            state, history, {"vpip": 0.25, "pfr": 0.18},
            opponent_name="VillainB"
        )
        # VillainA's RAISE is excluded — only VillainB's CALL is in candidates
        assert live.bet_amount == 400 / 20, f"Expected {400/20}, got {live.bet_amount}"

    def test_call_fallback_only_for_target_opponent(self):
        """
        VillainA raised and VillainB only called.  With opponent_name='VillainA',
        the RAISE by VillainA should be used (not the CALL by VillainB).
        """
        players = [
            Player(name="Hero", stack=4000),
            Player(name="VillainA", stack=3000),
            Player(name="VillainB", stack=3000),
        ]
        state = make_state(round=GameRound.TURN, pot=1200, current_bet=400, players=players)
        history = [
            ActionRecord(player_name="VillainA", action_type=ActionType.RAISE, amount=400, street=GameRound.TURN),
            ActionRecord(player_name="VillainB", action_type=ActionType.CALL, amount=400, street=GameRound.TURN),
        ]
        live = FeatureMapper.map_to_live_state(
            state, history, {"vpip": 0.25, "pfr": 0.18},
            opponent_name="VillainA"
        )
        assert live.bet_amount == 400 / 20, f"Expected {400/20}, got {live.bet_amount}"

    def test_opponent_name_no_current_street_actions_returns_zero(self):
        """
        opponent_name set, but the named player has no current-street actions.
        Should return bet_amount=0 rather than picking a different player's action.
        """
        state = make_state(round=GameRound.TURN, pot=1000, current_bet=0)
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.FLOP),
        ]
        live = FeatureMapper.map_to_live_state(
            state, history, {"vpip": 0.25, "pfr": 0.18},
            opponent_name="Villain"
        )
        assert live.bet_amount == 0.0, f"Expected 0, got {live.bet_amount}"

    def test_backward_compatibility_no_opponent_name(self):
        """
        When opponent_name is not provided, the mapper must still work
        and consider current-street actions without player filtering.
        """
        state = make_state(round=GameRound.RIVER, pot=2500, current_bet=1500)
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER),
        ]
        live = FeatureMapper.map_to_live_state(state, history, {"vpip": 0.25, "pfr": 0.18})
        assert live.bet_amount == 1500 / 20

    def test_prev_street_max_bet_still_uses_whole_history(self):
        """
        Temporal features like prev_street_max_bet must still use whole-hand
        history even when opponent_name is set.
        """
        state = make_state(round=GameRound.RIVER, pot=2500, current_bet=1500)
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=800, street=GameRound.TURN),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER),
        ]
        live = FeatureMapper.map_to_live_state(
            state, history, {"vpip": 0.25, "pfr": 0.18},
            opponent_name="Villain"
        )
        assert live.prev_street_max_bet == 800 / 20, (
            f"Expected {800/20}, got {live.prev_street_max_bet}"
        )
