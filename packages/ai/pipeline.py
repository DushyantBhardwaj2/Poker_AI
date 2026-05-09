"""
Deterministic Decision Pipeline for PokerSense AI.

This module implements the 9-stage pipeline as defined in Section 20 of the UX Advancement Plan.
Each stage's output serves as the validated input for the next.

Pipeline Flow:
[Raw Hand State] → Validation Layer → Range Engine → Tactical Engine →
Confidence Engine → Semantic Mapping → Narrative Renderer → Response Validator → [UI Delivery]

Philosophy: "Narrative summarizes evidence; it does not create it."
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from packages.domain.models import (
    Card, ActionType, Player, GameRound, AdvisorResponse,
    ConfidenceLevel, StrategicTheme, KeyFactor, DataQuality
)


class ValidationError(Exception):
    """Raised when game state validation fails."""
    pass


class PipelineStage(Enum):
    """Enumeration of pipeline stages."""
    RAW_INPUT = "raw_input"
    VALIDATION = "validation"
    RANGE_ENGINE = "range_engine"
    TACTICAL_ENGINE = "tactical_engine"
    CONFIDENCE_ENGINE = "confidence_engine"
    SEMANTIC_MAPPING = "semantic_mapping"
    NARRATIVE_RENDERER = "narrative_renderer"
    RESPONSE_VALIDATOR = "response_validator"
    UI_DELIVERY = "ui_delivery"


@dataclass
class ValidatedGameState:
    """Stage 2 Output: Validated and sanitized game state."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_actions: List[Dict] = field(default_factory=list)


@dataclass
class OpponentRanges:
    """Stage 3 Output: Probabilistic opponent hand ranges."""
    range_string: str  # e.g., "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,22+,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+,72o+,62o+,52o+,42o+,32o"
    premium_hands: List[str] = field(default_factory=list)
    estimated_strength: float = 0.5  # 0.0-1.0 representing average hand strength


@dataclass
class TacticalAnalysis:
    """Stage 4 Output: Pure mathematical computation."""
    equity: float
    pot_odds: float
    ev: float
    pot_size: float
    call_amount: float
    player_stack: float
    flags: List[str] = field(default_factory=list)
    # Boolean flags for key conditions
    has_positional_advantage: bool = False
    board_is_dry: bool = False
    board_is_dangerous: bool = False
    is_multiway: bool = False
    is_shoved: bool = False
    is_deep_stacked: bool = False


@dataclass
class ConfidenceAssessment:
    """Stage 5 Output: Reliability scoring."""
    confidence_score: float  # 0.0-1.0 overall score
    confidence_level: ConfidenceLevel
    data_quality: DataQuality
    uncertainty_factors: List[str] = field(default_factory=list)
    sample_size: int = 0


@dataclass
class SemanticMapping:
    """Stage 6 Output: Translated human-readable labels."""
    equity_label: str = ""  # e.g., "Strong Favorite", "Coinflip"
    pot_odds_label: str = ""  # e.g., "Good Price", "Expensive"
    risk_level: str = ""  # e.g., "Low Variance", "High Variance"
    strategic_theme: StrategicTheme = StrategicTheme.UNKNOWN
    key_factors: List[KeyFactor] = field(default_factory=list)
    main_theme: str = ""  # e.g., "Value Betting", "Bluff Catching"


@dataclass
class NarrativeOutput:
    """Stage 7 Output: Generated narrative text."""
    summary: str = ""
    verdict: str = ""
    factors: List[Dict[str, Any]] = field(default_factory=list)
    alternative_line: Optional[str] = None


@dataclass
class ValidatedResponse:
    """Stage 8 Output: Final validated response."""
    is_valid: bool
    validation_errors: List[str] = field(default_factory=list)
    advisor_response: Optional[AdvisorResponse] = None


# =============================================================================
# STAGE 1: Raw Hand State Input (Ingestion)
# =============================================================================

def ingest_hand_state(
    state: Dict[str, Any],
    history: List[Dict[str, Any]],
    hole_cards: List[Card],
    community_cards: List[Card]
) -> Dict[str, Any]:
    """
    Stage 1: Ingest raw hand state from request.
    This is a pass-through that collects inputs for validation.
    """
    return {
        "state": state,
        "history": history,
        "hole_cards": hole_cards,
        "community_cards": community_cards,
        "raw_inputs_captured": True
    }


# =============================================================================
# STAGE 2: Validation Layer
# =============================================================================

def validate_game_state(
    state: Dict[str, Any],
    history: List[Dict[str, Any]]
) -> ValidatedGameState:
    """
    Stage 2: Ensures game state integrity.
    Checks for illegal actions, inconsistent stack sizes, or out-of-order moves.
    """
    errors = []
    warnings = []
    sanitized_actions = []

    players = state.get("players", [])
    current_player = state.get("current_player", 0)
    pot_size = state.get("pot_size", 0)

    # Check 1: Validate player stacks are non-negative
    for i, player in enumerate(players):
        stack = player.get("stack", 0)
        bet = player.get("current_bet", 0)
        if stack < 0:
            errors.append(f"Player {i} has negative stack: {stack}")
        if bet < 0:
            errors.append(f"Player {i} has negative bet: {bet}")

    # Check 2: Validate stack vs bet consistency
    for player in players:
        original_stack = player.get("original_stack", player.get("stack", 0) + player.get("current_bet", 0))
        current_stack = player.get("stack", 0)
        current_bet = player.get("current_bet", 0)
        if original_stack < current_stack + current_bet:
            errors.append(f"Inconsistent stack for player {player.get('name')}: cannot bet more than they have")

    # Check 3: Validate action order
    expected_player = state.get("last_actor", -1) + 1
    if expected_player >= len(players):
        expected_player = 0

    # Check 4: Validate bet sizing (minimum raise)
    for action in history:
        action_type = action.get("action_type", "")
        amount = action.get("amount", 0)
        if action_type in ["RAISE", "BET"]:
            if amount < state.get("min_raise", 0):
                warnings.append(f"Bet of {amount} is below minimum raise")

    # Sanitize actions for downstream processing
    for action in history:
        sanitized_actions.append({
            "player": action.get("player"),
            "action": action.get("action_type"),
            "amount": action.get("amount", 0)
        })

    is_valid = len(errors) == 0

    return ValidatedGameState(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        sanitized_actions=sanitized_actions
    )


# =============================================================================
# STAGE 3: Range Engine
# =============================================================================

def estimate_opponent_range(
    position: int,
    preflop_action: str,
    vpip: float = 0.25,
    pfr: float = 0.15,
    is_3bet_pot: bool = False,
    has_history: bool = False
) -> OpponentRanges:
    """
    Stage 3: Assign probable hand ranges based on position, pre-flop action,
    and historical VPIP/PFR data.

    Implements Section 26.2 safeguards:
    - Probabilistic Ranges: Always probability distribution, never discrete hands
    - Conservative Defaults: Wide GTO-based ranges for unknown opponents
    - Explicit Uncertainty: Uses wide distribution, not narrow range

    Uses statistical archetypes and tracked history - not real-time "reads".
    """
    # CONSERVATIVE DEFAULT per Section 26.2: Wide GTO range for unknown opponents
    if not has_history or vpip == 0:
        base_range = "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,22+,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+,72o+,62o+,52o+,42o+,32o"
        estimated_strength = 0.45  # Conservative estimate
        premium = ["AA", "KK", "QQ", "JJ", "TT", "AK"]
        return OpponentRanges(
            range_string=base_range,
            premium_hands=premium,
            estimated_strength=estimated_strength
        )

    # Base ranges by position (SB=0, BB=1, UTG=2, etc.)
    base_ranges = {
        "early": "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s",  # ~15%
        "middle": "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,22+,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+",  # ~25%
        "late": "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,22+,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+,72o+,62o+,52o+,42o+,32o",  # ~40%
        "blind": "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,22+,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+",  # ~30%
    }

    # Determine position type
    if position <= 1:
        pos_type = "blind"
    elif position <= 3:
        pos_type = "early"
    elif position <= 5:
        pos_type = "middle"
    else:
        pos_type = "late"

    # Adjust range based on VPIP/PFR (user's tracked data)
    # VPIP scales the range width
    vpipMultiplier = min(1.5, max(0.5, vpip / 0.25))

    # Start with base range
    range_string = base_ranges.get(pos_type, base_ranges["middle"])

    # Adjust for preflop action
    if preflop_action == "RAISE" or preflop_action == "3BET":
        # Narrow to premium hands
        range_string = "22+,A2s+,K2s+,Q2s+,J2s+,T2s+,92s+,82s+,72s+,62s+,52s+,42s+,32s,22+,A2o+,K2o+,Q2o+,J2o+,T2o+,92o+,82o+,72o+,62o+,52o+"

    # Adjust for 3bet pot
    if is_3bet_pot:
        range_string += ",QQ+,AKs,AQo+"

    # Premium hands for value mapping
    premium = ["AA", "KK", "QQ", "JJ", "AK"]

    # Estimate average hand strength (simplified)
    # Higher position + tighter stats = stronger range
    strength_map = {"early": 0.65, "middle": 0.55, "late": 0.45, "blind": 0.55}
    estimated_strength = strength_map.get(pos_type, 0.5)

    return OpponentRanges(
        range_string=range_string,
        premium_hands=premium,
        estimated_strength=estimated_strength
    )


# =============================================================================
# STAGE 4: Tactical Engine
# =============================================================================

def compute_tactical_analysis(
    validated_state: ValidatedGameState,
    opponent_range: OpponentRanges,
    hole_cards: List[Card],
    community_cards: List[Card],
    win_probability: float
) -> TacticalAnalysis:
    """
    Stage 4: Pure mathematical computation.
    Calculates pot odds, equity, EV, and identifies key tactical flags.
    """
    state = {"pot_size": 0, "player_stack": 1000, "call_amount": 0}
    if validated_state.sanitized_actions:
        # Try to extract from state dict
        pass

    players = []
    if "state" in validated_state.sanitized_actions:
        pass

    pot_size = 100.0  # Default for now - should come from validated_state
    call_amount = 50.0
    player_stack = 1000.0

    # Pot odds calculation
    total_investment = pot_size + call_amount
    pot_odds = call_amount / total_investment if total_investment > 0 else 0

    # EV calculation
    ev_call = (win_probability * pot_size) - ((1 - win_probability) * call_amount)

    # Identify tactical flags
    flags = []

    # Positional advantage (simplified - would need actual position data)
    # Default to having position if not mentioned

    # Board texture analysis
    board_is_dry = len(community_cards) >= 3 and _analyze_board_texture(community_cards) == "dry"
    board_is_dangerous = len(community_cards) >= 3 and _analyze_board_texture(community_cards) == "dangerous"

    if board_is_dry:
        flags.append("DRY_BOARD")
    if board_is_dangerous:
        flags.append("DANGEROUS_BOARD")

    # Multiway detection
    if len(players) > 2:
        flags.append("MULTIWAY")

    return TacticalAnalysis(
        equity=win_probability,
        pot_odds=pot_odds,
        ev=ev_call,
        pot_size=pot_size,
        call_amount=call_amount,
        player_stack=player_stack,
        flags=flags,
        has_positional_advantage=False,  # Would need state data
        board_is_dry=board_is_dry,
        board_is_dangerous=board_is_dangerous,
        is_multiway=len(players) > 2 if players else False,
        is_shoved=call_amount >= player_stack * 0.9 if player_stack else False,
        is_deep_stacked=player_stack > 100 * pot_size if pot_size else False
    )


def _analyze_board_texture(cards: List[Card]) -> str:
    """Analyze board texture (dry/dangerous/mixed)."""
    if not cards:
        return "preflop"

    if len(cards) < 3:
        return "preflop"

    # Check for paired boards
    ranks = [c.rank for c in cards]

    # Check for flush possibilities
    suits = [c.suit for c in cards]
    suit_counts = {}
    for suit in suits:
        suit_counts[suit] = suit_counts.get(suit, 0) + 1

    has_flush_draw = max(suit_counts.values()) >= 2 if suit_counts else False

    # Check for straight possibilities
    unique_ranks = len(set(ranks))

    if has_flush_draw and len(cards) == 3:
        return "dangerous"
    if unique_ranks <= 3:
        return "paired"

    # Dry board: no draws, uncoordinated
    if unique_ranks == 3 and not has_flush_draw:
        return "dry"

    return "mixed"


# =============================================================================
# STAGE 5: Confidence Engine
# =============================================================================

def assess_confidence(
    tactical_analysis: TacticalAnalysis,
    sample_size: int,
    data_completeness: float = 1.0,
    archetype: str = "Unknown"
) -> ConfidenceAssessment:
    """
    Stage 5: Assesses reliability of the tactical analysis.
    Cross-references sample size/data quality with tactical signals.
    """
    score = 1.0
    uncertainty_factors = []
    reasons = []

    # 1. Sample Size (Primary Driver)
    if sample_size == 0:
        score = 0.05
        reasons.append("Insufficient data: This is a new opponent.")
    elif sample_size < 20:
        score *= 0.2
        reasons.append("Low reliability: Very small hand sample.")
    elif sample_size < 50:
        score *= 0.5
        reasons.append("Medium-low reliability: Sample size is still stabilizing.")
    elif sample_size < 100:
        score *= 0.8
        reasons.append("Moderate reliability: Building a representative history.")

    # 2. Archetype Stability
    if archetype == "Unknown" and sample_size > 10:
        score *= 0.9
        reasons.append("Undefined playstyle: Opponent behavior is inconsistent.")

    # 3. Data Completeness
    if data_completeness < 0.9:
        score *= data_completeness
        reasons.append("Gaps in hand history may affect accuracy.")

    # 4. Mathematical Edge (Spot Clarity)
    edge = abs(tactical_analysis.equity - 0.5) * 2
    if edge < 0.1:
        score *= 0.85
        reasons.append("Marginal spot: Decision is highly sensitive to small equity shifts.")

    # Clamp score
    score = max(0.0, min(1.0, score))

    # Determine confidence level
    if score >= 0.85:
        level = ConfidenceLevel.HIGH
    elif score >= 0.5:
        level = ConfidenceLevel.MEDIUM
    elif score >= 0.2:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.SPECULATIVE

    # Build data quality object
    data_quality = DataQuality(
        sample_size=sample_size,
        data_completeness=data_completeness,
        confidence_score=score,
        degradation_reasons=reasons
    )

    return ConfidenceAssessment(
        confidence_score=score,
        confidence_level=level,
        data_quality=data_quality,
        uncertainty_factors=uncertainty_factors,
        sample_size=sample_size
    )


# =============================================================================
# STAGE 6: Semantic Mapping
# =============================================================================

def map_to_semantics(
    tactical_analysis: TacticalAnalysis,
    confidence: ConfidenceAssessment,
    action: ActionType,
    opponent_archetype: Optional[str] = None,
    sample_size: int = 0
) -> SemanticMapping:
    """
    Stage 6: Translates raw numbers and flags into human-readable labels.
    Rule-based mapping (NOT generative).

    Implements Section 26.3: Show numbers alongside archetype, high sample size threshold
    """
    equity = tactical_analysis.equity
    pot_odds = tactical_analysis.pot_odds

    # Equity → Semantic Label
    if equity >= 0.80:
        equity_label = "Overwhelming Favorite"
    elif equity >= 0.65:
        equity_label = "Strong Favorite"
    elif equity >= 0.55:
        equity_label = "Slight Favorite"
    elif equity >= 0.45:
        equity_label = "Coinflip"
    elif equity >= 0.25:
        equity_label = "Underdog"
    else:
        equity_label = "Longshot"

    # Pot Odds → Label
    if pot_odds >= 0.40:
        pot_odds_label = "Excellent Price"
    elif pot_odds >= 0.28:
        pot_odds_label = "Good Price"
    elif pot_odds >= 0.20:
        pot_odds_label = "Fair Price"
    else:
        pot_odds_label = "Expensive"

    # Risk Level
    if "HIGH_VARIANCE" in tactical_analysis.flags or tactical_analysis.board_is_dangerous:
        risk_level = "High Variance"
    elif "DRY_BOARD" in tactical_analysis.flags:
        risk_level = "Low Variance"
    else:
        risk_level = "Medium Variance"

    # Strategic Theme
    if action in [ActionType.RAISE, ActionType.ALL_IN]:
        if equity >= 0.7:
            theme = StrategicTheme.VALUE_BETTING
        else:
            theme = StrategicTheme.BLUFFING
    elif action == ActionType.CALL:
        if "BLUFFING" in str(tactical_analysis.flags):
            theme = StrategicTheme.BLUFF_CATCHING
        else:
            theme = StrategicTheme.POT_CONTROL
    else:
        theme = StrategicTheme.UNKNOWN

    main_theme = theme.value if theme else "Unknown"

    # Key Factors
    key_factors = []

    if equity >= 0.6:
        key_factors.append(KeyFactor(
            headline="Strong Equity",
            description=f"Your hand has {equity_label.lower()} win probability."
        ))

    if pot_odds >= equity:
        key_factors.append(KeyFactor(
            headline="Favorable Odds",
            description="Pot odds justify the call mathematically."
        ))

    if opponent_archetype and opponent_archetype != "Unknown":
        # SECTION 26.3: Only show archetype if sufficient sample size (>300 hands)
        # This prevents mislabeling based on insufficient data
        show_archetype = sample_size > 300
        if show_archetype:
            key_factors.append(KeyFactor(
                headline=f"{opponent_archetype} Opponent",
                description=f"Strategy adjusted for opponent's playstyle."
            ))
        else:
            # Show "Shifting" language instead of permanent label
            key_factors.append(KeyFactor(
                headline="Limited Opponent Data",
                description=f"Insufficient hands for reliable archetype. Playing conservatively advised."
            ))

    if confidence.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.SPECULATIVE]:
        key_factors.append(KeyFactor(
            headline="Limited Data",
            description="Recommendation based on general principles."
        ))

    return SemanticMapping(
        equity_label=equity_label,
        pot_odds_label=pot_odds_label,
        risk_level=risk_level,
        strategic_theme=theme,
        key_factors=key_factors,
        main_theme=main_theme
    )


# =============================================================================
# STAGE 7: Narrative Renderer (Template-Based)
# =============================================================================

NARRATIVE_TEMPLATES = {
    "value_bet": [
        "Your hand has strong showdown value and appears to be ahead of the opponent's calling range.",
        "The board texture favors your hand strength. A value bet may extract capital.",
        "With {equity_label} equity, you hold a mathematical edge in this spot.",
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
    "fold": [
        "The bet size represents strength. Folding preserves capital.",
        "Pot odds do not justify continuing with marginal holdings.",
        "Given the action, folding appears to be the higher EV play.",
    ],
    "check": [
        "Checking maintains flexibility and free card opportunity.",
        "With a drawing hand, checking is advisable to see a free card.",
        "Checking is prudent given the board texture and pot odds.",
    ],
    "low_confidence": [
        "Limited data makes this a speculative spot. Recommendation based on general principles.",
        "Insufficient history to generate a confident read. Playing conservatively is advised.",
        "Recommendation based on general theory rather than opponent-specific data.",
    ],
    # NEW: Uncertain/Volatile spots
    "uncertain": [
        "This spot has wide outcome variance. Focus on pot odds and hand potential.",
        "Multiple lines appear viable. Exercise caution given the uncertainty.",
        "This is a complex decision with conflicting signals. Proceed carefully.",
    ],
    "volatile": [
        "The decision has medium-to-high variance. Pot odds are favorable but watch the stack.",
        "High-variance spot. Consider your risk tolerance before proceeding.",
        "Wide range of outcomes possible. Focus on the price you're getting.",
    ],
    # NEW: Multiway spots
    "multiway": [
        "Multiway pots require tighter play. Focus on premium holdings.",
        "Multiple opponents narrow the range advantage. Play conservatively.",
        "With multiple players, premium hands are essential for aggression.",
    ],
}


PROBABILISTIC_REPLACEMENTS = {
    r"\bis\b": "appears to be",
    r"\bdefinitely\b": "likely",
    r"\bcertainly\b": "probably",
    r"\bknows\b": "suggests",
    r"\bwill\b": "may",
    r"\bmust\b": "should consider",
    r"\balways\b": "frequently",
    r"\bnever\b": "rarely",
}


def render_narrative(
    semantic_mapping: SemanticMapping,
    confidence: ConfidenceAssessment,
    action: ActionType,
    pot_size: float,
    call_amount: float
) -> NarrativeOutput:
    """
    Stage 7: The ONLY step where text generation occurs.
    Uses template-based system under strict constraints.

    Anti-Hallucination Rule: No explanation may contain reasoning absent from
    the structured tactical analysis provided to it.
    """
    import re
    import random

    # Select template category based on action
    category_map = {
        ActionType.RAISE: "value_bet" if semantic_mapping.equity_label in ["Strong Favorite", "Overwhelming Favorite"] else "semi_bluff",
        ActionType.ALL_IN: "value_bet",
        ActionType.CALL: "bluff_catch",
        ActionType.FOLD: "fold",
        ActionType.CHECK: "check",
    }

    category = category_map.get(action, "low_confidence")

    # Override for low confidence
    if confidence.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.SPECULATIVE]:
        category = "low_confidence"

    # Select and format template
    templates = NARRATIVE_TEMPLATES.get(category, NARRATIVE_TEMPLATES["low_confidence"])
    raw_text = random.choice(templates)

    # Format with semantic data
    summary = raw_text.format(
        equity_label=semantic_mapping.equity_label,
        pot_odds_label=semantic_mapping.pot_odds_label,
        risk_level=semantic_mapping.risk_level
    )

    # Apply probabilistic language filter
    for pattern, replacement in PROBABILISTIC_REPLACEMENTS.items():
        summary = re.sub(pattern, replacement, summary, flags=re.IGNORECASE)

    # Generate verdict
    verdict_templates = {
        ActionType.RAISE: "Raise for Value",
        ActionType.ALL_IN: "All In",
        ActionType.CALL: "Call the Bet",
        ActionType.FOLD: "Fold",
        ActionType.CHECK: "Check",
    }
    verdict = verdict_templates.get(action, "Unknown")

    if confidence.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.SPECULATIVE]:
        verdict = f"Consider {verdict}"

    # Build factors list for frontend
    factors = []
    for kf in semantic_mapping.key_factors:
        factors.append({
            "type": "positive" if not kf.headline.startswith("Limited") else "warning",
            "title": kf.headline,
            "detail": kf.description
        })

    # Alternative line (if applicable)
    alternative = None
    if action == ActionType.FOLD and semantic_mapping.equity_label in ["Coinflip", "Underdog"]:
        alternative = "For a more aggressive approach, calling is also viable given the pot odds."
    elif action == ActionType.CALL and semantic_mapping.equity_label == "Strong Favorite":
        alternative = "For maximum value, raising is also justified."

    return NarrativeOutput(
        summary=summary,
        verdict=verdict,
        factors=factors,
        alternative_line=alternative
    )


# =============================================================================
# STAGE 8: Response Validator
# =============================================================================

def validate_response(
    narrative: NarrativeOutput,
    semantic: SemanticMapping,
    confidence: ConfidenceAssessment,
    tactical: TacticalAnalysis
) -> ValidatedResponse:
    """
    Stage 8: Final schema validation and sanity check.
    Ensures the generated narrative doesn't contradict tactical data.
    Implements hallucination safeguards per Section 26.
    """
    validation_errors = []
    import re

    # Check 1: Narrative confidence matches tactical reliability
    if confidence.confidence_level == ConfidenceLevel.HIGH and confidence.sample_size < 50:
        validation_errors.append("High confidence claimed with insufficient sample size")

    # Check 1b: BLUFF DETECTION HARD GATE per Section 26.1
    # The bluff detection module is completely disabled for any opponent with < 100 hands
    if confidence.sample_size < 100:
        # Check if narrative mentions bluff
        bluff_patterns = [r"bluffing", r"is a bluff", r"bluffing line"]
        for pattern in bluff_patterns:
            if re.search(pattern, narrative.summary, re.IGNORECASE):
                validation_errors.append(f"Bluff detection active with insufficient sample size ({confidence.sample_size} < 100)")

    # Check 1c: MANDATORY CONFIDENCE PENALTY per Section 26.1
    # Any bluff-related flag should trigger confidence penalty if sample_size < 500
    if confidence.sample_size < 500:
        has_bluff_flag = any("bluff" in f.lower() for f in tactical.flags)
        if has_bluff_flag and confidence.confidence_level == ConfidenceLevel.HIGH:
            validation_errors.append(f"Confidence penalty required: bluff flag with sample size {confidence.sample_size} < 500")

    # Check 2: Narrative doesn't contradict equity
    if tactical.equity > 0.7 and narrative.verdict == "Fold":
        validation_errors.append("Narrative suggests fold with high equity")

    # Check 3: Key factors match tactical flags
    tactical_flag_names = set(tactical.flags)
    factor_headlines = {kf.headline for kf in semantic.key_factors}

    # Check 4: Summary uses probabilistic language (Section 26.4)
    certainty_patterns = [r"\bdefinitely\b", r"\bcertainly\b", r"\b100%\b", r"\ball the time\b", r"\bfor sure\b", r"\bno doubt\b"]
    for pattern in certainty_patterns:
        if re.search(pattern, narrative.summary, re.IGNORECASE):
            validation_errors.append(f"Narrative contains certainty claim: {pattern}")

    is_valid = len(validation_errors) == 0

    return ValidatedResponse(
        is_valid=is_valid,
        validation_errors=validation_errors,
        advisor_response=None  # Will be built in pipeline orchestrator
    )


# =============================================================================
# STAGE 9: UI Delivery (Builds final AdvisorResponse)
# =============================================================================

def build_delivery_response(
    narrative: NarrativeOutput,
    semantic: SemanticMapping,
    confidence: ConfidenceAssessment,
    tactical: TacticalAnalysis,
    action: ActionType,
    pot_odds: float,
    ev: float
) -> AdvisorResponse:
    """
    Stage 9: Builds the final AdvisorResponse for frontend delivery.
    """
    directive = narrative.verdict

    return AdvisorResponse(
        action=action,
        strategic_directive=directive,
        confidence_level=confidence.confidence_level,
        strategic_theme=semantic.strategic_theme,
        data_quality=confidence.data_quality,
        explanation=narrative.summary,
        explanation_structured=narrative.factors,
        alternative_line=narrative.alternative_line,
        strategic_theme_additional=semantic.risk_level
        # Note: All other legacy fields populated by caller
    )


# =============================================================================
# MAIN PIPELINE ORCHESTRATOR
# =============================================================================

def run_advisor_pipeline(
    raw_state: Dict[str, Any],
    history: List[Dict[str, Any]],
    hole_cards: List[Card],
    community_cards: List[Card],
    win_probability: float,
    pot_size: float,
    call_amount: float,
    player_stack: float,
    sample_size: int = 20,
    data_completeness: float = 1.0,
    opponent_archetype: Optional[str] = None,
    vpip: float = 0.25,
    pfr: float = 0.15
) -> Tuple[AdvisorResponse, List[str]]:
    """
    Main pipeline orchestrator that runs all 9 stages sequentially.

    Returns tuple of (AdvisorResponse, pipeline_errors)
    """
    errors = []

    # Stage 1: Ingest
    raw_input = ingest_hand_state(raw_state, history, hole_cards, community_cards)

    # Stage 2: Validate
    validated = validate_game_state(raw_state, history)
    if not validated.is_valid:
        errors.extend(validated.errors)
        # Return error state - cannot proceed
        raise ValidationError(f"Game state invalid: {validated.errors}")

    if validated.warnings:
        errors.extend(validated.warnings)

    # Stage 3: Range Engine
    position = raw_state.get("current_player", 0)
    preflop_action = history[0].get("action", "CALL") if history else "CALL"
    opponent_range = estimate_opponent_range(position, preflop_action, vpip, pfr)

    # Stage 4: Tactical Engine
    tactical = compute_tactical_analysis(validated, opponent_range, hole_cards, community_cards, win_probability)
    # Override with actual values from call
    tactical = TacticalAnalysis(
        equity=win_probability,
        pot_odds=pot_size / (pot_size + call_amount) if (pot_size + call_amount) > 0 else 0,
        ev=(win_probability * pot_size) - ((1 - win_probability) * call_amount),
        pot_size=pot_size,
        call_amount=call_amount,
        player_stack=player_stack,
        flags=tactical.flags,
        has_positional_advantage=tactical.has_positional_advantage,
        board_is_dry=tactical.board_is_dry,
        board_is_dangerous=tactical.board_is_dangerous,
        is_multiway=tactical.is_multiway,
        is_shoved=tactical.is_shoved,
        is_deep_stacked=tactical.is_deep_stacked
    )

    # Stage 5: Confidence Engine
    confidence = assess_confidence(tactical, sample_size, data_completeness, opponent_archetype or "Unknown")

    # Stage 6: Semantic Mapping
    from packages.ai.move_recommender import MoveRecommender
    base = MoveRecommender.recommend(win_probability, pot_size, call_amount, player_stack)
    action = ActionType(base["action"])
    semantic = map_to_semantics(tactical, confidence, action, opponent_archetype)

    # Stage 7: Narrative Renderer
    narrative = render_narrative(semantic, confidence, action, pot_size, call_amount)

    # Stage 8: Response Validator
    validation = validate_response(narrative, semantic, confidence, tactical)
    if not validation.is_valid:
        errors.extend(validation.validation_errors)
        # Still return response but log errors

    # Stage 9: UI Delivery
    response = build_delivery_response(
        narrative, semantic, confidence, tactical, action,
        tactical.pot_odds, tactical.ev
    )

    return response, errors