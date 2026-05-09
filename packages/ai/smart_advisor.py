import re
import random
from typing import List, Tuple, Optional
from packages.domain.models import (
    ActionType,
    AdvisorResponse,
    ConfidenceLevel,
    StrategicTheme,
    Explanation,
    TacticalData,
    KeyFactor,
    DataQuality,
)
from .move_recommender import MoveRecommender

# Template-based narrative system for fluid, natural summaries
NARRATIVE_TEMPLATES = {
    "strong_value": [
        "Your hand has strong showdown value and appears to be ahead of {opponent}'s calling range.",
        "The board texture favors your hand strength. A value bet may extract capital.",
        "With {equity:.0%} equity, you hold a mathematical edge in this spot.",
    ],
    "bluff_catch": [
        "The opponent's betting pattern suggests potential aggression. Calling preserves equity.",
        "Your hand has sufficient showdown value to justify calling. The opponent may be bluffing.",
        "Given the bet size and board texture, this appears to be a bluff-catching spot.",
    ],
    "semi_bluff": [
        "Your draw has equity potential. Raising adds fold equity to natural equity.",
        "A semi-bluff raise applies pressure while maintaining a profitable line.",
        "With a draw in hand, converting to a bet captures fold probability.",
    ],
    "marginal": [
        "The spot is mathematically close. Pot odds vs equity suggest a marginal +EV call.",
        "This appears to be a borderline decision. Proceed based on opponent read.",
        "Limited data suggests playing conservatively in this spot.",
    ],
    "strong_fold": [
        "The bet size represents strength. Folding preserves capital.",
        "Pot odds do not justify continuing with marginal holdings.",
        "Given the action, folding appears to be the higher EV play.",
    ],
    "low_confidence": [
        "Limited data makes this a speculative spot.",
        "Insufficient history to generate a confident read.",
        "Recommendation based on general theory rather than opponent-specific data.",
    ],
}

BLUFF_CONTEXT_TEMPLATES = [
    "Historical patterns suggest elevated aggression in similar spots ({bluff_prob:.0%}).",
    "The opponent's betting rhythm in this session indicates potential bluffing ({bluff_prob:.0%}).",
    "Limited but consistent signals suggest a bluffing tendency ({bluff_prob:.0%}).",
]

DECAY_REASONS = [
    "Insufficient data: This is a new opponent.",
    "Low reliability: Very small hand sample.",
    "Medium-low reliability: Sample size is still stabilizing.",
    "Moderate reliability: Building a representative history.",
    "Undefined playstyle: Opponent behavior is inconsistent.",
    "Gaps in hand history may affect accuracy.",
    "Marginal spot: Decision is highly sensitive to small equity shifts.",
]

class SmartAdvisor:
    """
    Advanced recommendation engine that synthesizes mathematical probability
    and behavioral bluff detection into a structured, narrative-driven response.
    Includes a hallucination filter to ensure probabilistic language.
    """
    
    @staticmethod
    def _select_template(category: str, **kwargs) -> str:
        """Select and format a narrative template based on category."""
        templates = NARRATIVE_TEMPLATES.get(category, NARRATIVE_TEMPLATES["marginal"])
        selected = random.choice(templates)
        try:
            return selected.format(**kwargs)
        except KeyError:
            return selected

    @staticmethod
    def _filter_narrative(text: str) -> str:
        """
        Enforces probabilistic language by replacing deterministic statements.
        """
        replacements = {
            r"\bis\b": "appears to be",
            r"\bdefinitely\b": "likely",
            r"\bcertainly\b": "probably",
            r"\bknows\b": "suggests",
            r"\bwill\b": "may",
            r"\bmust\b": "should consider",
            r"\balways\b": "frequently",
            r"\bnever\b": "rarely",
        }
        
        filtered = text
        for pattern, replacement in replacements.items():
            # Use case-insensitive regex for the replacement while preserving original capitalization is hard,
            # but for our simple poker phrases, this basic swap is a good start.
            filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)
        
        return filtered

    @staticmethod
    def _calculate_confidence(
        sample_size: int,
        completeness: float,
        win_prob: float,
        bluff_prob: float,
        archetype: Optional[str] = None
    ) -> Tuple[ConfidenceLevel, DataQuality]:
        score = 1.0
        reasons = []

        # 1. Sample Size (The Primary Reliability Driver)
        if sample_size == 0:
            score = 0.05
            reasons.append(DECAY_REASONS[0])
        elif sample_size < 20:
            score *= 0.2
            reasons.append(DECAY_REASONS[1])
        elif sample_size < 50:
            score *= 0.5
            reasons.append(DECAY_REASONS[2])
        elif sample_size < 100:
            score *= 0.8
            reasons.append(DECAY_REASONS[3])

        # 2. Archetype Stability
        if archetype == "Unknown" and sample_size > 10:
            score *= 0.9
            reasons.append(DECAY_REASONS[4])

        # 3. Data Completeness (Backend tracking coverage)
        if completeness < 0.9:
            score *= completeness
            reasons.append(DECAY_REASONS[5])

        # 4. Mathematical Edge (Clarity of the spot)
        edge = abs(win_prob - 0.5) * 2
        if edge < 0.1:
            score *= 0.85
            reasons.append(DECAY_REASONS[6])

        score = max(0.0, min(1.0, score))

        if score >= 0.85:
            level = ConfidenceLevel.HIGH
        elif score >= 0.5:
            level = ConfidenceLevel.MEDIUM
        elif score >= 0.2:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.SPECULATIVE

        return level, DataQuality(
            sample_size=sample_size,
            data_completeness=completeness,
            confidence_score=score,
            degradation_reasons=reasons
        )

    @staticmethod
    def _determine_theme(
        action: ActionType,
        win_prob: float,
        bluff_prob: float,
        pot_odds: float
    ) -> StrategicTheme:
        if action == ActionType.RAISE or action == ActionType.ALL_IN:
            if win_prob > 0.7:
                return StrategicTheme.VALUE_BETTING
            if bluff_prob > 0.5:
                return StrategicTheme.BLUFFING
            return StrategicTheme.SEMI_BLUFF
        
        if action == ActionType.CALL:
            if bluff_prob > 0.4:
                return StrategicTheme.BLUFFING # Hero calling a bluff
            if win_prob < pot_odds:
                return StrategicTheme.POT_CONTROL
        
        return StrategicTheme.UNKNOWN

    @staticmethod
    def recommend(
        win_probability: float,
        bluff_probability: float,
        pot_size: float,
        call_amount: float,
        player_stack: float,
        opponent_sample_size: int = 20,
        data_completeness: float = 1.0,
        opponent_archetype: Optional[str] = "Unknown",
        is_shifting: bool = False,
        shift_direction: str = "stable"
    ) -> AdvisorResponse:
        """
        Adjusts mathematical recommendations based on the likelihood of an opponent's bluff
        and returns a comprehensive, structured recommendation.
        Now includes adaptive intelligence for behavioral drift.
        """
        # 1. Reliability Weighting (Bayesian approach)
        # If we have no data, we don't trust the bluff detector at all (default to GTO baseline)
        # We need a sample of ~50 hands before we fully trust the ML bluff detection
        bluff_weight = min(1.0, opponent_sample_size / 50.0)
        
        # Baseline bluff probability (GTO-ish baseline or session average)
        # In a vacuum, we assume ~15% bluff frequency for a standard opponent
        baseline_bluff = 0.15 
        
        weighted_bluff_prob = (bluff_probability * bluff_weight) + (baseline_bluff * (1.0 - bluff_weight))

        # 1b. Adaptive Intelligence: Adjust bluff probability based on behavioral shift
        # If opponent is shifting to 'more_aggressive', we slightly boost bluff probability
        if is_shifting:
            if shift_direction == "more_aggressive":
                weighted_bluff_prob = min(0.99, weighted_bluff_prob * 1.2)
            elif shift_direction == "more_passive":
                weighted_bluff_prob = weighted_bluff_prob * 0.8
        
        # 2. Calculate Adjusted Win Probability using weighted bluff
        p_bluff = weighted_bluff_prob
        p_value = 1.0 - p_bluff
        
        # If opponent bluffs, we win almost always (assuming they fold or we have best hand)
        adjusted_win_prob = (win_probability * p_value) + (0.98 * p_bluff)
        adjusted_win_prob = min(0.99, adjusted_win_prob)
        
        # 3. Get base recommendation from MoveRecommender
        base_advice = MoveRecommender.recommend(
            adjusted_win_prob,
            pot_size,
            call_amount,
            player_stack
        )
        
        action = ActionType(base_advice["action"])
        pot_odds = base_advice["pot_odds"]
        ev = base_advice["ev"]

        # 4. Confidence and Data Quality
        conf_level, data_quality = SmartAdvisor._calculate_confidence(
            opponent_sample_size,
            data_completeness,
            win_probability,
            weighted_bluff_prob,
            opponent_archetype
        )

        # 5. Strategic Context
        theme = SmartAdvisor._determine_theme(action, win_probability, weighted_bluff_prob, pot_odds)

        # 6. Narrative Construction (Template-based, Probabilistic Language)
        # Select narrative category based on action and probabilities
        if win_probability > 0.7 and action in [ActionType.RAISE, ActionType.ALL_IN]:
            narrative_category = "strong_value"
        elif p_bluff > 0.4 and action == ActionType.CALL:
            narrative_category = "bluff_catch"
        elif win_probability > 0.35 and win_probability < 0.55 and action in [ActionType.RAISE, ActionType.ALL_IN]:
            narrative_category = "semi_bluff"
        elif conf_level == ConfidenceLevel.LOW or conf_level == ConfidenceLevel.SPECULATIVE:
            narrative_category = "low_confidence"
        elif pot_odds > win_probability:
            narrative_category = "marginal"
        else:
            narrative_category = "bluff_catch" if action == ActionType.CALL else "strong_value"

        main_explanation = SmartAdvisor._select_template(
            narrative_category,
            opponent=opponent_archetype or "opponent",
            equity=win_probability
        ) if conf_level != ConfidenceLevel.SPECULATIVE else SmartAdvisor._select_template("low_confidence")

        # Add probabilistic filter
        main_explanation = SmartAdvisor._filter_narrative(main_explanation)

        # Fallback to base advice explanation if template fails
        if not main_explanation:
            main_explanation = SmartAdvisor._filter_narrative(base_advice["explanation"])

        # Refine main explanation to be more probabilistic if confidence is low
        if conf_level in [ConfidenceLevel.LOW, ConfidenceLevel.SPECULATIVE]:
            main_explanation = f"With limited data, this appears to be {action.value}. {main_explanation}"

        # Bluff context using templates
        bluff_context = ""
        if opponent_sample_size >= 10:
            if p_bluff > 0.3:
                bluff_context = random.choice(BLUFF_CONTEXT_TEMPLATES).format(bluff_prob=p_bluff)
        
        # Add Behavioral Drift info to bluff context
        if is_shifting:
            shift_text = "more aggressive" if shift_direction == "more_aggressive" else "more passive"
            bluff_context += f" Warning: Opponent is playing significantly {shift_text} this session compared to their long-term baseline."

        pot_odds_theory = None
        fundamental_theorem = None
        if p_bluff > 0.5 and action == ActionType.CALL:
             fundamental_theorem = "Fundamental Theorem: You gain when they bluff and you call. Current patterns indicate a probable bluffing line."
        elif win_probability < pot_odds:
             pot_odds_theory = f"Mathematical Odds: Your hand equity ({win_probability:.1%}) is below the pot price ({pot_odds:.1%}). This call relies on the likelihood of a bluff."

        # Key Factors
        key_factors = []
        if win_probability > 0.6:
            key_factors.append(KeyFactor(headline="Strong Equity", description="Your hand has high natural win probability."))
        
        if opponent_sample_size >= 20:
            if p_bluff > 0.4:
                key_factors.append(KeyFactor(headline="Bluff Pattern", description="Opponent's betting pattern deviates from value-range norms."))
            if opponent_archetype and opponent_archetype != "Unknown":
                key_factors.append(KeyFactor(headline=f"{opponent_archetype} Opponent", description=f"Strategy adjusted for opponent's '{opponent_archetype}' tendencies."))
        
        # Add Behavioral Drift as a Key Factor
        if is_shifting:
            shift_title = "Aggression Spike" if shift_direction == "more_aggressive" else "Passive Shift"
            shift_desc = "Opponent is deviating from baseline. Exercise caution as historical reads may be less reliable."
            key_factors.append(KeyFactor(headline=shift_title, description=shift_desc))

        if ev > 100:
            key_factors.append(KeyFactor(headline="High EV", description="This action has significant long-term expected value."))
        
        if conf_level == ConfidenceLevel.SPECULATIVE:
            key_factors.append(KeyFactor(headline="Uncertain Read", description="Analysis is based on sparse data; recommend playing conservatively."))

        # Directive
        directive = f"{action.name.replace('_', ' ').title()} appears to be the most viable play."
        if conf_level == ConfidenceLevel.SPECULATIVE:
            directive = f"Speculative {action.value}: Data is currently insufficient for a high-confidence read."

        return AdvisorResponse(
            action=action,
            strategic_directive=directive,
            confidence_level=conf_level,
            strategic_theme=theme,
            key_factors=key_factors,
            explanation_structured=Explanation(
                main=main_explanation,
                bluff_context=bluff_context or None,
                pot_odds_theory=pot_odds_theory,
                fundamental_theorem=fundamental_theorem,
            ),
            tactical_data=TacticalData(
                win_probability=win_probability,
                adjusted_win_probability=adjusted_win_prob,
                bluff_probability=p_bluff,
                pot_odds=pot_odds,
                expected_value=ev,
            ),
            data_quality=data_quality,
            opponent_archetype=opponent_archetype,
            explanation=f"{main_explanation} {bluff_context}".strip(),
            ev=ev,
            pot_odds=pot_odds,
            adjusted_win_probability=adjusted_win_prob,
            bluff_probability=p_bluff,
            theory_tip=fundamental_theorem or pot_odds_theory,
        )
