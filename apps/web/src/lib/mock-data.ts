import type { SmartAdvisorResponse } from './api';

/**
 * IMPORTANT: The AI Advisor interprets BEHAVIOR and PROBABILITIES.
 * It does NOT know hidden opponent cards.
 *
 * All narrative text must reflect this uncertainty and behavioral inference.
 * Phrases should use: "appears", "suggests", "consistent with", "tendency"
 * Avoid: "is", "definitely", "certainly", "knows"
 */

// Template variations for narrative generation (Phase 5)
export const NARRATIVE_TEMPLATES = {
    strong_value: [
        "Your hand has strong showdown value and appears to be ahead of {opponent}'s calling range.",
        "The board texture favors your hand strength. A value bet may extract capital.",
        "With {equity:.0%} equity, you hold a mathematical edge in this spot.",
    ],
    bluff_catch: [
        "The opponent's betting pattern suggests potential aggression. Calling preserves equity.",
        "Your hand has sufficient showdown value to justify calling. The opponent may be bluffing.",
        "Given the bet size and board texture, this appears to be a bluff-catching spot.",
    ],
    semi_bluff: [
        "Your draw has equity potential. Raising adds fold equity to natural equity.",
        "A semi-bluff raise applies pressure while maintaining a profitable line.",
        "With a draw in hand, converting to a bet captures fold probability.",
    ],
    marginal: [
        "The spot is mathematically close. Pot odds vs equity suggest a marginal +EV call.",
        "This appears to be a borderline decision. Proceed based on opponent read.",
        "Limited data suggests playing conservatively in this spot.",
    ],
    strong_fold: [
        "The bet size represents strength. Folding preserves capital.",
        "Pot odds do not justify continuing with marginal holdings.",
        "Given the action, folding appears to be the higher EV play.",
    ],
    low_confidence: [
        "Limited data makes this a speculative spot.",
        "Insufficient history to generate a confident read.",
        "Recommendation based on general theory rather than opponent-specific data.",
    ],
};

export const BLUFF_CONTEXT_VARIATIONS = [
    "Historical patterns suggest elevated aggression in similar spots ({bluff_prob:.0%}).",
    "The opponent's betting rhythm in this session indicates potential bluffing ({bluff_prob:.0%}).",
    "Limited but consistent signals suggest a bluffing tendency ({bluff_prob:.0%}).",
];

export const CONFIDENCE_DECAY_REASONS = [
    "Insufficient data: This is a new opponent.",
    "Low reliability: Very small hand sample.",
    "Medium-low reliability: Sample size is still stabilizing.",
    "Moderate reliability: Building a representative history.",
    "Undefined playstyle: Opponent behavior is inconsistent.",
    "Gaps in hand history may affect accuracy.",
    "Marginal spot: Decision is highly sensitive to small equity shifts.",
];
export const mockSmartAdvisorResponse: SmartAdvisorResponse = {
  advice: {
    action: "CALL",
    verdict: "Consider Calling",
    summary: "The opponent's betting pattern on this dry board appears aggressive and may represent a bluff attempt based on their historical over-betting tendencies. Your hand has showdown value and sits at the boundary of calling for value, though the pot odds make this a marginal +EV situation.",
    strategic_theme: "Bluff Catching",
    confidence_label: "Medium Confidence",
    risk_level: "Medium Variance",

    hand_potential: {
      current_strength: "Medium Pair",
      draw_strength: "Strong Flush Draw",
      improvement_chance: "High"
    },

    bluff_analysis: {
      likelihood: "Moderate",
      reason: "Based on your recorded history, this opponent shows a pattern of over-betting dry boards - though with limited sample size, interpret cautiously."
    },

    board_analysis: {
      texture: "Dry",
      range_advantage: "Even",
      volatility: "Low"
    },

    factors: [
      {
        type: "positive",
        title: "Pot Odds Favor Calling",
        detail: "The current pot odds suggest calling is mathematically justifiable at this price point.",
        priority: 1
      },
      {
        type: "positive",
        title: "Opponent Pattern Detected",
        detail: "Historical data suggests this opponent increases aggression in similar spots, potentially indicating a bluff.",
        priority: 2
      },
      {
        type: "warning",
        title: "Polarized Bet Sizing",
        detail: "The large bet size typically represents either a very strong hand or a pure bluff - difficult to distinguish without more history.",
        priority: 1
      }
    ],

    alternative_line: "A tighter player might fold here. If you believe this opponent plays more value-heavy than bluff-heavy, consider folding."
  },

  tactical_data: {
    equity: 45,
    ev: 0.8,
    pot_odds: 28,
    opponent_stats: {
      vpip: 35,
      pfr: 28,
      agg_freq: 2.8
    }
  },
  data_quality: {
      sample_size: 42,
      reliability: "Medium",
      confidence_decay_active: true,
      decay_reason: "Limited hands recorded for this opponent. Advice weights toward general poker theory over opponent-specific reads."
  }
};

/**
 * Creates a new advisor response with behavior-based language
 */
export function createAdvisorResponse(
  action: string,
  verdict: string,
  equity: number,
  potOdds: number,
  opponentVPIP: number,
  opponentPFR: number,
  sampleSize: number,
  hasBluffTendency: boolean
): SmartAdvisorResponse {
  const reliability = sampleSize >= 500 ? "High" : sampleSize >= 100 ? "Medium" : "Low";
  const confidenceLabel = reliability === "High" ? "High Confidence" : reliability === "Medium" ? "Medium Confidence" : "Low Confidence";

  const equitySuffix = equity >= 60 ? "Strong favorite" : equity >= 45 ? "Slight edge" : equity >= 35 ? "Underdog" : "Long shot";
  const potOddsVsEquity = equity - potOdds;
  const isPositiveEV = potOddsVsEquity > 0;

  // Generate probabilistic summary
  const summary = hasBluffTendency
    ? `Based on available data, your hand has ${equity}% equity (${equitySuffix}). The opponent's betting pattern suggests potential bluffing frequency, but with only ${sampleSize} hands recorded, interpret cautiously. Pot odds of ${potOdds}% ${isPositiveEV ? 'favor' : 'slightly disfavor'} a call.`
    : `Your hand has ${equity}% equity (${equitySuffix}). The opponent's stats (VPIP ${opponentVPIP}%, PFR ${opponentPFR}%) suggest a ${opponentVPIP > 30 ? 'loose' : opponentVPIP < 20 ? 'tight' : 'standard'} range. Pot odds of ${potOdds}% ${isPositiveEV ? 'justify' : 'barely justify'} continuing.`;

  const factors: any[] = [
    {
      type: potOddsVsEquity > 0 ? "positive" : "warning",
      title: potOddsVsEquity > 0 ? "Favorable Math" : "Marginal Math",
      detail: potOddsVsEquity > 0
        ? `Your ${equity}% equity exceeds the ${potOdds}% pot odds - mathematically sound.`
        : `Pot odds (${potOdds}%) slightly exceed equity (${equity}%) - relies on implied odds or opponent folding.`,
      priority: 1
    }
  ];

  if (sampleSize < 50) {
    factors.push({
      type: "warning",
      title: "Limited History",
      detail: `Only ${sampleSize} hands recorded. Advice leans heavily on general poker theory.`,
      priority: 2
    });
  }

  if (hasBluffTendency) {
    factors.push({
      type: "positive",
      title: "Bluff Pattern Detected",
      detail: "Opponent shows increased aggression in similar spots historically.",
      priority: 2
    });
  }

  return {
    advice: {
      action,
      verdict,
      summary,
      strategic_theme: equity > 50 ? "Value Betting" : potOdds > equity ? "Defensive Call" : "Bluff Catch",
      confidence_label: confidenceLabel,
      risk_level: Math.abs(potOdds - equity) < 10 ? "Medium Variance" : "Low Variance",
      hand_potential: {
        current_strength: equity > 70 ? "Strong Hand" : equity > 40 ? "Medium Pair" : "Weak Hand",
        draw_strength: "None",
        improvement_chance: "Unknown"
      },
      bluff_analysis: {
        likelihood: hasBluffTendency ? "Moderate" : "Low",
        reason: hasBluffTendency
          ? "Betting pattern aligns with historically elevated aggression in this spot type."
          : "Insufficient data to detect clear bluff patterns. Defaulting to value-heavy range."
      },
      board_analysis: {
        texture: "Dry",
        range_advantage: "Even",
        volatility: "Low"
      },
      factors,
      alternative_line: reliability === "Low"
        ? "With limited history, consider playing conservatively."
        : "A tighter line is also reasonable if your hand has no showdown value."
    },
    tactical_data: {
      equity,
      ev: potOddsVsEquity > 0 ? 1.2 : -0.5,
      pot_odds: potOdds,
      opponent_stats: {
        vpip: opponentVPIP,
        pfr: opponentPFR,
        agg_freq: opponentPFR / Math.max(1, opponentVPIP)
      }
    },
    data_quality: {
      sample_size: sampleSize,
      reliability,
      confidence_decay_active: sampleSize < 50,
      decay_reason: sampleSize < 50
        ? `Low sample size (${sampleSize} hands). Confidence reduced.`
        : ""
    }
  };
}