from packages.domain.models import ActionRecord, ActionType, GameRound


class TestActionHistoryDomain:
    def test_action_record_creation(self):
        record = ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.RIVER)
        assert record.player_name == "Villain"
        assert record.action_type == ActionType.RAISE
        assert record.amount == 1500
        assert record.street == GameRound.RIVER

    def test_action_record_all_types(self):
        for action_type in ActionType:
            record = ActionRecord(player_name="Test", action_type=action_type, amount=100, street=GameRound.FLOP)
            assert record.action_type == action_type

    def test_action_record_streets(self):
        for street in GameRound:
            record = ActionRecord(player_name="Test", action_type=ActionType.CALL, amount=50, street=street)
            assert record.street == street

    def test_action_history_accumulation(self):
        history = [
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=200, street=GameRound.PRE_FLOP),
            ActionRecord(player_name="Hero", action_type=ActionType.CALL, amount=200, street=GameRound.PRE_FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=500, street=GameRound.FLOP),
            ActionRecord(player_name="Hero", action_type=ActionType.CALL, amount=500, street=GameRound.FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1500, street=GameRound.TURN),
        ]
        assert len(history) == 5
        assert history[-1].player_name == "Villain"
        assert history[-1].action_type == ActionType.RAISE
        assert history[-1].street == GameRound.TURN

    def test_action_history_empty(self):
        history = []
        assert len(history) == 0

    def test_aggressive_action_detection(self):
        records = [
            ActionRecord(player_name="Villain", action_type=ActionType.FOLD, amount=0, street=GameRound.FLOP),
            ActionRecord(player_name="Hero", action_type=ActionType.RAISE, amount=300, street=GameRound.FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.CALL, amount=300, street=GameRound.FLOP),
        ]
        raises = [r for r in records if r.action_type in (ActionType.RAISE, ActionType.ALL_IN)]
        assert len(raises) == 1
        assert raises[0].player_name == "Hero"

    def test_multiple_streets_preserves_sequence(self):
        history = [
            ActionRecord(player_name="Hero", action_type=ActionType.RAISE, amount=100, street=GameRound.PRE_FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.CALL, amount=100, street=GameRound.PRE_FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=400, street=GameRound.FLOP),
            ActionRecord(player_name="Hero", action_type=ActionType.CALL, amount=400, street=GameRound.FLOP),
            ActionRecord(player_name="Villain", action_type=ActionType.RAISE, amount=1200, street=GameRound.TURN),
            ActionRecord(player_name="Hero", action_type=ActionType.RAISE, amount=2500, street=GameRound.TURN),
            ActionRecord(player_name="Villain", action_type=ActionType.CALL, amount=1300, street=GameRound.TURN),
        ]
        assert len(history) == 7
        last_raise = [r for r in history if r.action_type in (ActionType.RAISE, ActionType.ALL_IN)][-1]
        assert last_raise.player_name == "Hero"
        assert last_raise.amount == 2500
        assert last_raise.street == GameRound.TURN
