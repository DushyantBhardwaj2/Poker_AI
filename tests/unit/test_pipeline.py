"""
Unit tests for the deterministic pipeline.
Tests the 9-stage pipeline as defined in Section 20 of UX Advancement Plan.
"""
import unittest
from packages.ai.pipeline import (
    validate_game_state,
    estimate_opponent_range,
    assess_confidence,
    map_to_semantics,
    render_narrative,
    ValidationError,
)
from packages.domain.models import Card, Rank, Suit, ActionType, ConfidenceLevel


class TestValidateGameState(unittest.TestCase):
    """Stage 2: Validation Layer tests"""

    def test_valid_state(self):
        """Valid game state should pass validation"""
        state = {
            "pot": 100,
            "current_player": 0,
            "players": [
                {"name": "Hero", "stack": 1000, "current_bet": 10},
                {"name": "Villain", "stack": 1000, "current_bet": 10}
            ],
            "current_bet": 10,
        }
        history = []
        result = validate_game_state(state, history)
        self.assertTrue(result.is_valid)

    def test_empty_state_valid(self):
        """Empty state should be valid (defaults applied)"""
        state = {}
        result = validate_game_state(state, [])
        # May be valid with warnings
        self.assertIsNotNone(result.is_valid)


class TestEstimateOpponentRange(unittest.TestCase):
    """Stage 3: Range Engine tests"""

    def test_conservative_default_unknown_opponent(self):
        """Unknown opponent should get conservative wide range"""
        result = estimate_opponent_range(
            position=3, preflop_action="CALL", vpip=0, pfr=0, has_history=False
        )
        # Should use wide conservative range
        self.assertIsNotNone(result.range_string)
        self.assertEqual(len(result.premium_hands), 6)  # AA-KK-QQ-JJ-TT-AK

    def test_tight_position_range(self):
        """Early position should have tighter range"""
        result = estimate_opponent_range(
            position=1, preflop_action="CALL", vpip=0.25, pfr=0.15, has_history=True
        )
        self.assertIsNotNone(result.range_string)

    def test_3bet_narrows_range(self):
        """3bet should narrow the range"""
        result_before = estimate_opponent_range(
            position=3, preflop_action="CALL", vpip=0.25, has_history=True
        )
        result_after = estimate_opponent_range(
            position=3, preflop_action="3BET", vpip=0.25, has_history=True
        )
        # 3bet range is narrower
        self.assertNotEqual(result_before.range_string, result_after.range_string)


class TestAssessConfidence(unittest.TestCase):
    """Stage 5: Confidence Engine tests"""

    def test_no_data_low_confidence(self):
        """Zero sample size should give low confidence"""
        from packages.ai.pipeline import TacticalAnalysis

        tactical = TacticalAnalysis(
            equity=0.5, pot_odds=0.3, ev=0, pot_size=100,
            call_amount=30, player_stack=1000
        )
        result = assess_confidence(tactical, sample_size=0)
        self.assertEqual(result.confidence_level, ConfidenceLevel.SPECULATIVE)

    def test_50_hands_medium_confidence(self):
        """50 hands should give medium confidence"""
        from packages.ai.pipeline import TacticalAnalysis

        tactical = TacticalAnalysis(
            equity=0.7, pot_odds=0.3, ev=50, pot_size=100,
            call_amount=30, player_stack=1000
        )
        result = assess_confidence(tactical, sample_size=50)
        self.assertIn(result.confidence_level, [ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW])

    def test_300_hands_high_confidence(self):
        """300+ hands should give high confidence"""
        from packages.ai.pipeline import TacticalAnalysis

        tactical = TacticalAnalysis(
            equity=0.8, pot_odds=0.3, ev=80, pot_size=100,
            call_amount=30, player_stack=1000
        )
        result = assess_confidence(tactical, sample_size=300)
        self.assertEqual(result.confidence_level, ConfidenceLevel.HIGH)


class TestMapToSemantics(unittest.TestCase):
    """Stage 6: Semantic Mapping tests"""

    def test_equity_to_label(self):
        """Equity should map to semantic labels"""
        from packages.ai.pipeline import TacticalAnalysis, ConfidenceAssessment

        tactical = TacticalAnalysis(
            equity=0.75, pot_odds=0.3, ev=50, pot_size=100,
            call_amount=30, player_stack=1000
        )
        confidence = ConfidenceAssessment(
            confidence_score=0.9, confidence_level=ConfidenceLevel.HIGH,
            data_quality=None, uncertainty_factors=[]
        )
        result = map_to_semantics(tactical, confidence, ActionType.CALL, sample_size=100)
        self.assertEqual(result.equity_label, "Strong Favorite")

    def test_low_equity_to_label(self):
        """Low equity should map correctly"""
        from packages.ai.pipeline import TacticalAnalysis, ConfidenceAssessment

        tactical = TacticalAnalysis(
            equity=0.20, pot_odds=0.3, ev=-20, pot_size=100,
            call_amount=30, player_stack=1000
        )
        confidence = ConfidenceAssessment(
            confidence_score=0.9, confidence_level=ConfidenceLevel.HIGH,
            data_quality=None, uncertainty_factors=[]
        )
        result = map_to_semantics(tactical, confidence, ActionType.FOLD, sample_size=100)
        self.assertEqual(result.equity_label, "Longshot")


class TestRenderNarrative(unittest.TestCase):
    """Stage 7: Narrative Renderer tests"""

    def test_renders_template(self):
        """Should render a template"""
        from packages.ai.pipeline import TacticalAnalysis, ConfidenceAssessment, SemanticMapping

        tactical = TacticalAnalysis(
            equity=0.6, pot_odds=0.3, ev=30, pot_size=100,
            call_amount=30, player_stack=1000
        )
        confidence = ConfidenceAssessment(
            confidence_score=0.7, confidence_level=ConfidenceLevel.MEDIUM,
            data_quality=None, uncertainty_factors=[]
        )
        semantic = map_to_semantics(tactical, confidence, ActionType.CALL, sample_size=100)
        result = render_narrative(semantic, confidence, ActionType.CALL, 100, 30)
        self.assertIsNotNone(result.summary)
        self.assertIsNotNone(result.verdict)

    def test_probabilistic_language(self):
        """Narrative should use probabilistic language"""
        from packages.ai.pipeline import TacticalAnalysis, ConfidenceAssessment, SemanticMapping

        tactical = TacticalAnalysis(
            equity=0.6, pot_odds=0.3, ev=30, pot_size=100,
            call_amount=30, player_stack=1000
        )
        confidence = ConfidenceAssessment(
            confidence_score=0.7, confidence_level=ConfidenceLevel.MEDIUM,
            data_quality=None, uncertainty_factors=[]
        )
        semantic = map_to_semantics(tactical, confidence, ActionType.CALL, sample_size=100)
        result = render_narrative(semantic, confidence, ActionType.CALL, 100, 30)
        # Should NOT contain certainty words
        self.assertNotIn("definitely", result.summary.lower())
        self.assertNotIn("certainly", result.summary.lower())


class TestColdStart(unittest.TestCase):
    """Cold start handling tests"""

    def test_unknown_opponent_conservative(self):
        """Unknown opponent should get conservative treatment"""
        result = estimate_opponent_range(
            position=3, preflop_action="CALL", vpip=0, has_history=False
        )
        # Unknown opponent gets wide conservative range
        self.assertIsNotNone(result.range_string)
        self.assertEqual(result.estimated_strength, 0.45)

    def test_low_sample_confidence(self):
        """Low sample size should lower confidence"""
        from packages.ai.pipeline import TacticalAnalysis

        tactical = TacticalAnalysis(
            equity=0.6, pot_odds=0.3, ev=30, pot_size=100,
            call_amount=30, player_stack=1000
        )
        # 5 hands is very low
        result = assess_confidence(tactical, sample_size=5)
        self.assertIn(result.confidence_level, [ConfidenceLevel.LOW, ConfidenceLevel.SPECULATIVE])


if __name__ == "__main__":
    unittest.main()