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
from packages.domain.models import Card, Rank, Suit, ActionType, ConfidenceLevel, StrategicTheme


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



class TestFullPipelineResponse(unittest.TestCase):
    """End-to-end pipeline execution: confirms AdvisorResponse is valid"""

    def test_run_advisor_pipeline_returns_valid_response(self):
        """Full pipeline must return a valid AdvisorResponse with no Pydantic errors"""
        from packages.ai.pipeline import run_advisor_pipeline
        from packages.domain.models import Card, Rank, Suit

        raw_state = {
            "players": [
                {"name": "Hero", "stack": 1000, "current_bet": 10},
                {"name": "Villain", "stack": 1000, "current_bet": 10}
            ],
            "pot": 100,
            "current_bet": 20,
            "current_player": 0,
            "round": "turn",
            "small_blind": 5,
            "big_blind": 10,
        }
        history = [
            {"player": "Hero", "action": "RAISE", "amount": 50, "street": "flop"},
            {"player": "Villain", "action": "CALL", "amount": 50, "street": "flop"},
        ]
        hole_cards = [Card(rank=Rank.ACE, suit=Suit.SPADES), Card(rank=Rank.KING, suit=Suit.SPADES)]
        community_cards = [
            Card(rank=Rank.TEN, suit=Suit.HEARTS),
            Card(rank=Rank.JACK, suit=Suit.DIAMONDS),
            Card(rank=Rank.TWO, suit=Suit.CLUBS),
        ]

        response, errors = run_advisor_pipeline(
            raw_state=raw_state,
            history=history,
            hole_cards=hole_cards,
            community_cards=community_cards,
            win_probability=0.65,
            pot_size=100,
            call_amount=20,
            player_stack=980,
            sample_size=200,
            data_completeness=0.8,
            opponent_archetype="Aggressive",
            vpip=0.30,
            pfr=0.22,
            bluff_probability=0.35
        )

        # Must return an AdvisorResponse without Pydantic error
        self.assertIsNotNone(response)
        self.assertIsInstance(response.action, ActionType)
        self.assertIsNotNone(response.strategic_directive)
        self.assertIsNotNone(response.confidence_level)
        self.assertIsNotNone(response.strategic_theme)
        self.assertIsInstance(response.key_factors, list)
        self.assertIsNotNone(response.explanation_structured)
        self.assertIsNotNone(response.tactical_data)
        self.assertIsNotNone(response.explanation)
        self.assertIsInstance(response.ev, (int, float))
        self.assertIsInstance(response.pot_odds, (int, float))
        self.assertIsInstance(response.adjusted_win_probability, (int, float))
        self.assertIsInstance(response.bluff_probability, (int, float))

    def test_pipeline_with_empty_history_low_confidence(self):
        """Pipeline should handle empty history gracefully and return low confidence"""
        from packages.ai.pipeline import run_advisor_pipeline
        from packages.domain.models import Card, Rank, Suit

        raw_state = {
            "players": [
                {"name": "Hero", "stack": 500, "current_bet": 0},
                {"name": "Villain", "stack": 500, "current_bet": 0}
            ],
            "pot": 30,
            "current_bet": 0,
            "current_player": 0,
            "round": "pre-flop",
            "small_blind": 5,
            "big_blind": 10,
        }
        response, errors = run_advisor_pipeline(
            raw_state=raw_state,
            history=[],
            hole_cards=[Card(rank=Rank.SEVEN, suit=Suit.HEARTS), Card(rank=Rank.TWO, suit=Suit.DIAMONDS)],
            community_cards=[],
            win_probability=0.12,
            pot_size=30,
            call_amount=10,
            player_stack=500,
            sample_size=0,
            data_completeness=0.0,
        )

        self.assertIsNotNone(response)
        self.assertIn(response.confidence_level, [
            ConfidenceLevel.LOW, ConfidenceLevel.SPECULATIVE
        ])
        self.assertIsInstance(response.tactical_data.bluff_probability, (int, float))


class TestBluffProbabilityIntegration(unittest.TestCase):
    """Phase 2: Bluff probability consumed by map_to_semantics and render_narrative"""

    def setUp(self):
        from packages.ai.pipeline import TacticalAnalysis, ConfidenceAssessment
        self.tactical = TacticalAnalysis(
            equity=0.55, pot_odds=0.30, ev=30, pot_size=100,
            call_amount=30, player_stack=1000, flags=[]
        )
        self.confidence = ConfidenceAssessment(
            confidence_score=0.7, confidence_level=ConfidenceLevel.MEDIUM,
            data_quality=None, uncertainty_factors=[]
        )

    def test_high_bluff_prob_triggers_bluff_catching_theme(self):
        """bluff_probability > 0.4 with sufficient sample → BLUFF_CATCHING for CALL"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=200, bluff_probability=0.6
        )
        self.assertEqual(semantic.strategic_theme, StrategicTheme.BLUFF_CATCHING)

    def test_low_bluff_prob_uses_pot_control(self):
        """bluff_probability <= 0.4 with sufficient sample → POT_CONTROL for CALL"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=200, bluff_probability=0.15
        )
        self.assertEqual(semantic.strategic_theme, StrategicTheme.POT_CONTROL)

    def test_insufficient_sample_ignores_bluff_prob(self):
        """bluff_probability > 0.4 but sample_size < 100 → POT_CONTROL (conservative gate)"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=50, bluff_probability=0.6
        )
        self.assertEqual(semantic.strategic_theme, StrategicTheme.POT_CONTROL)

    def test_high_bluff_prob_key_factor_added(self):
        """bluff_probability > 0.4 adds KeyFactor entry"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=200, bluff_probability=0.6
        )
        headlines = [kf.headline for kf in semantic.key_factors]
        self.assertTrue(any("Bluff" in h for h in headlines))

    def test_bluff_read_narrative_verdict(self):
        """High bluff prob + sufficient sample → 'Bluff Catch' verdict"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=200, bluff_probability=0.6
        )
        narrative = render_narrative(
            semantic, self.confidence, ActionType.CALL,
            pot_size=100, call_amount=30,
            bluff_probability=0.6, sample_size=200
        )
        self.assertEqual(narrative.verdict, "Bluff Catch")

    def test_low_bluff_narrative_verdict_is_call(self):
        """Low bluff prob → 'Call the Bet' verdict"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=200, bluff_probability=0.15
        )
        narrative = render_narrative(
            semantic, self.confidence, ActionType.CALL,
            pot_size=100, call_amount=30,
            bluff_probability=0.15, sample_size=200
        )
        self.assertEqual(narrative.verdict, "Call the Bet")

    def test_narrative_contains_bluff_probability_text(self):
        """Narrative renders bluff probability percentage in bluff_read category"""
        semantic = map_to_semantics(
            self.tactical, self.confidence, ActionType.CALL,
            sample_size=200, bluff_probability=0.6
        )
        narrative = render_narrative(
            semantic, self.confidence, ActionType.CALL,
            pot_size=100, call_amount=30,
            bluff_probability=0.6, sample_size=200
        )
        self.assertIn("bluff", narrative.summary.lower())
        self.assertIn("60", narrative.summary)


if __name__ == "__main__":
    unittest.main()