export type Suit = 's' | 'h' | 'd' | 'c';
export type Rank = '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | 'T' | 'J' | 'Q' | 'K' | 'A';

export interface Card {
  rank: Rank;
  suit: Suit;
}

export type ActionType = 'fold' | 'check' | 'call' | 'raise' | 'all-in';

export interface Action {
  player_index: number;
  action_type: ActionType;
  amount: number;
}

export type PlayerStatus = 'active' | 'folded' | 'all-in' | 'sitting-out';

export interface Player {
  id?: string;
  name: string;
  stack: number;
  hole_cards: Card[];
  current_bet: number;
  total_contributed: number;
  is_folded: boolean;
  is_all_in: boolean;
  status: PlayerStatus;
  has_acted: boolean;
  vpip_this_hand?: boolean;
  pfr_this_hand?: boolean;
  vpip?: number;
  pfr?: number;
  bet?: number; // Added for compatibility with usePokerStore
}

export interface Pot {
  amount: number;
  eligible_player_indices: number[];
}

export type GameRound = 'pre-flop' | 'flop' | 'turn' | 'river' | 'showdown';

export interface GameState {
  players: Player[];
  community_cards: Card[];
  pots: Pot[];
  pot: number;
  current_bet: number;
  last_raise_amount: number;
  current_player_index: number;
  dealer_index: number;
  round: GameRound;
  small_blind: number;
  big_blind: number;
  sessionId?: string | null;  // Optional session ID for analytics
}

export interface ActionRecord {
  player_name: string;
  action_type: ActionType;
  amount: number;
  street: GameRound;
}

export interface WinAnalysis {
  win_probability: number;
  tie_probability: number;
  equity: number;
}

export interface BluffAnalysis {
  bluff_probability: number;
  is_bluff: boolean;
  threshold: number;
  street_rank: number;
}

export interface KeyFactor {
  headline: string;
  description: string;
}

export interface ExplanationStructured {
  main: string;
  pot_odds_theory?: string;
  fundamental_theorem?: string;
  bluff_context?: string;
}

export interface TacticalDataV2 {
  win_probability: number;
  adjusted_win_probability: number;
  bluff_probability: number;
  pot_odds: number;
  expected_value: number;
}

export interface DataQualityV2 {
  sample_size: number;
  data_completeness: number;
  confidence_score: number;
  degradation_reasons: string[];
}

export interface AdvisorResponse {
  action: ActionType;
  strategic_directive: string;
  confidence_level: 'High' | 'Medium' | 'Low' | 'Speculative';
  strategic_theme: string;
  key_factors: KeyFactor[];
  explanation_structured: ExplanationStructured;
  tactical_data: TacticalDataV2;
  data_quality?: DataQualityV2;
  opponent_archetype?: string;
  // Legacy fields
  explanation: string;
  ev: number;
  pot_odds: number;
  adjusted_win_probability: number;
  bluff_probability: number;
  theory_tip?: string;
}

export interface OpponentProfile {
  total_hands: number;
  hands_played: number;  // Required for cold start check
  vpip: number;
  pfr: number;
  aggression: number;
  bluffs: number;
  cbet_success_rate: number;
  three_bet_rate: number;
  wtsd: number;
  archetype: string;
  reliability: 'Low' | 'Medium' | 'High';
  notes: string;
  last_seen: string | null;
}

export interface OpponentProfileDetail extends OpponentProfile {
  cbet_rate: number;
  three_bet_rate: number;
  fold_to_river: number;
  session_vpip: number;
  is_shifting: boolean;
  shift_direction: 'more_passive' | 'more_aggressive' | 'stable';
}

export interface RecentOpponent {
  player_name: string;
  archetype: string;
  last_seen: string | null;
  hands_played: number;
}

export interface FullAnalysisResponse {
  win_analysis: WinAnalysis;
  bluff_analysis: BluffAnalysis;
  advice: AdvisorResponse;
  opponent_profile: OpponentProfile;
  hands_played?: number;  // For cold start check
}

// --- New SmartAdvisor Response Schema (from ux_advance_plan.md) ---

export interface HandPotential {
  current_strength: string;
  draw_strength: string;
  improvement_chance: string;
}

export interface NewBluffAnalysis {
  likelihood: string;
  reason: string;
}

export interface BoardAnalysis {
  texture: string;
  range_advantage: string;
  volatility: string;
}

export interface Factor {
  type: 'positive' | 'warning';
  title: string;
  detail: string;
  priority: number;
}

export interface Advice {
  action: string;
  verdict: string;
  summary: string;
  strategic_theme: string;
  confidence_label: string;
  risk_level: string;
  hand_potential: HandPotential;
  bluff_analysis: NewBluffAnalysis;
  board_analysis: BoardAnalysis;
  factors: Factor[];
  alternative_line: string;
}

export interface TacticalData {
  equity: number;
  ev: number;
  pot_odds: number;
  opponent_stats: {
    vpip: number;
    pfr: number;
    agg_freq: number;
  };
}

export interface DataQuality {
  sample_size: number;
  reliability: 'Low' | 'Medium' | 'High';
  confidence_decay_active: boolean;
  decay_reason: string;
}

export interface SmartAdvisorResponse {
  advice: Advice;
  tactical_data: TacticalData;
  data_quality: DataQuality;
}

// Unified API URL Configuration
const getBaseUrl = () => {
  // 1. PUBLIC_API_URL is the primary source for both SSR and Client-side
  const envUrl = import.meta.env.PUBLIC_API_URL;
  if (envUrl) {
    return envUrl.replace(/\/+$/, '');
  }
  
  // 2. Browser-aware fallback
  if (typeof window !== 'undefined') {
    // We prefer relative paths in the browser to leverage Vite proxy and avoid CORS
    return '/api/v1';
  }

  // 3. SSR fallback (for Astro build/server context)
  // During build time or SSR, we default to localhost unless PUBLIC_API_URL is provided.
  return 'http://localhost:8000/api/v1';
};

const API_URL = getBaseUrl();

import { getSessionToken } from './auth';

/**
 * Internal helper for Authorization and other headers.
 * Enforces session token requirement in the browser.
 */
const getHeaders = async () => {
  const isBrowser = typeof window !== 'undefined';
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (isBrowser) {
    const token = await getSessionToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      // In a production environment, we might want to redirect here,
      // but for now we'll throw an error that the caller can handle.
      throw new Error('AUTHENTICATION_REQUIRED');
    }
  }

  return headers;
};

async function handleResponse(res: Response) {
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || `API Error: ${res.status}`);
  }
  return res.json();
}

// --- Stateless API (Functional) ---

export async function startGame(
  playerNames: string[],
  initialStacks: number[],
  smallBlind: number,
  bigBlind: number,
  dealerIndex: number = 0,
  sbIndex: number = -1,
  bbIndex: number = -1
): Promise<GameState> {
  const res = await fetch(`${API_URL}/game/start`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify({
      player_names: playerNames,
      initial_stacks: initialStacks,
      small_blind: smallBlind,
      big_blind: bigBlind,
      dealer_index: dealerIndex,
      sb_index: sbIndex,
      bb_index: bbIndex
    }),
  });
  return handleResponse(res);
}

export async function processAction(state: GameState, action: Action): Promise<GameState> {
  const res = await fetch(`${API_URL}/game/action`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify({ state, action }),
  });
  return handleResponse(res);
}

export async function showdown(state: GameState, blufferNames: string[] = []): Promise<{ new_state: GameState; result: any }> {
  const res = await fetch(`${API_URL}/game/showdown`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify({ state, bluffer_names: blufferNames }),
  });
  return handleResponse(res);
}

export async function analyzeFull(
  state: GameState,
  history: ActionRecord[],
  opponentName: string,
  holeCards: Card[],
  numSimulations = 500
): Promise<FullAnalysisResponse> {
  const res = await fetch(`${API_URL}/ai/analyze-full`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify({
      state,
      history,
      opponent_name: opponentName,
      hole_cards: holeCards,
      num_simulations: numSimulations,
    }),
  });
  return handleResponse(res);
}

export async function getWinProbability(
  holeCards: Card[],
  communityCards: Card[],
  numOpponents: number,
  numSimulations = 500
): Promise<WinAnalysis> {
  const res = await fetch(`${API_URL}/ai/win-probability`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify({
      hole_cards: holeCards,
      community_cards: communityCards,
      num_opponents: numOpponents,
      num_simulations: numSimulations,
    }),
  });
  return handleResponse(res);
}

export async function getAllStats(): Promise<Record<string, OpponentProfile>> {
  const res = await fetch(`${API_URL}/stats`, {
    method: 'GET',
    headers: await getHeaders(),
  });
  return handleResponse(res);
}

export async function getRecentOpponents(limit = 10): Promise<RecentOpponent[]> {
  const res = await fetch(`${API_URL}/stats/recent?limit=${limit}`, {
    method: 'GET',
    headers: await getHeaders(),
  });
  return handleResponse(res);
}

export async function getOpponentProfile(playerName: string): Promise<OpponentProfileDetail> {
  const res = await fetch(`${API_URL}/stats/player/${encodeURIComponent(playerName)}`, {
    method: 'GET',
    headers: await getHeaders(),
  });
  return handleResponse(res);
}

export async function updateOpponentNotes(playerName: string, notes: string): Promise<void> {
  const res = await fetch(`${API_URL}/stats/notes`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify({ player_name: playerName, notes }),
  });
  return handleResponse(res);
}

export interface UpdateStatsRequest {
  player_name: string;
  vpip_this_hand: boolean;
  pfr_this_hand: boolean;
  is_bluff?: boolean;
  made_cbet?: boolean;
  cbet_succeeded?: boolean;
  made_three_bet?: boolean;
  three_bet_succeeded?: boolean;
  fold_to_river?: boolean;
  called_showdown?: boolean;
  won_showdown?: boolean;
  bet_amount?: number;
  call_amount?: number;
}

export async function updatePlayerStats(request: UpdateStatsRequest): Promise<{ status: string; hands_played: number }> {
  const res = await fetch(`${API_URL}/stats/update_stats`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse(res);
}

export async function resetSessionStats(): Promise<{ status: string }> {
  const res = await fetch(`${API_URL}/stats/reset_session`, {
    method: 'POST',
    headers: await getHeaders(),
  });
  return handleResponse(res);
}

// --- Session-based API (Object-style for compatibility) ---

export const PokerAPI = {
  startSession: async () => 
    fetch(`${API_URL}/game/session/start`, { method: 'POST', headers: await getHeaders() }).then(handleResponse),
  
  addPlayer: async (sessionId: string, playerName: string, stack: number) =>
    fetch(`${API_URL}/game/session/add_player`, {
      method: 'POST',
      headers: await getHeaders(),
      body: JSON.stringify({ session_id: sessionId, player_name: playerName, stack })
    }).then(handleResponse),
    
  recordAction: async (sessionId: string, playerName: string, actionType: string, amount: number) =>
    fetch(`${API_URL}/game/session/record_action`, {
      method: 'POST',
      headers: await getHeaders(),
      body: JSON.stringify({ session_id: sessionId, player_name: playerName, action_type: actionType, amount })
    }).then(handleResponse),
    
  nextStreet: async (sessionId: string, nextStreet: string) =>
    fetch(`${API_URL}/game/session/next_street`, {
      method: 'POST',
      headers: await getHeaders(),
      body: JSON.stringify({ session_id: sessionId, next_street: nextStreet })
    }).then(handleResponse),
    
  showdown: async (sessionId: string, payload: any) =>
    fetch(`${API_URL}/game/session/showdown`, {
      method: 'POST',
      headers: await getHeaders(),
      body: JSON.stringify({ session_id: sessionId, ...payload })
    }).then(handleResponse),
  
  analyzeFull: async (payload: any) => 
    fetch(`${API_URL}/ai/analyze-full`, {
      method: 'POST',
      headers: await getHeaders(),
      body: JSON.stringify(payload)
    }).then(handleResponse),
  
  getStats: async () =>
    fetch(`${API_URL}/stats`, { method: 'GET', headers: await getHeaders() }).then(handleResponse)
};

// --- Phase 6: Session Analytics & Post-Game Review ---

export interface HandHistory {
  hand_id: string;
  street: GameRound;
  pot_size: number;
  your_cards: Card[];
  community_cards: Card[];
  result?: 'win' | 'loss' | 'tie';
  amount_won?: number;
  action_count: number;
  duration_seconds: number;
  tactical_data?: any;
  leak_detected?: boolean;
  leak_description?: string;
  timestamp: string;
}

export interface SessionSummary {
  session_id: string;
  start_time: string;
  end_time: string | null;
  total_hands: number;
  hands_played: number;
  vpip_hands: number;
  pfr_hands: number;
  total_winnings: number;
  biggest_pot: number;
  biggest_loss: number;
  showdown_wins: number;
  showdown_losses: number;
  folds: number;
  avg_position: number;
}

export interface SessionAnalytics {
  summary: SessionSummary;
  recent_hands: HandHistory[];
  vpip_percentage: number;
  pfr_percentage: number;
  win_rate: number;
  showdown_rate: number;
  avg_hand_duration: number;
  most_played_opponent: string | null;
}

export async function getAllHandHistory(limit = 50): Promise<HandHistory[]> {
  const res = await fetch(`${API_URL}/stats/history?limit=${limit}`, {
    method: 'GET',
    headers: await getHeaders(),
  });
  return handleResponse(res);
}

export async function getSessionAnalytics(sessionId: string): Promise<SessionAnalytics> {
  const url = sessionId 
    ? `${API_URL}/stats/session/${sessionId}/analytics`
    : `${API_URL}/stats/session/latest/analytics`;
  
  const res = await fetch(url, {
    method: 'GET',
    headers: await getHeaders(),
  });
  return handleResponse(res);
}

export async function recordHandResult(request: {
  hand_id?: string;
  session_id?: string;
  result: 'win' | 'loss' | 'tie';
  amount_won: number;
  street: GameRound;
  action_count?: number;
  duration_seconds?: number;
  pot_size: number;
  your_cards?: Card[];
  community_cards?: Card[];
  tactical_data?: any;
}): Promise<{ status: string; hand_id: string }> {
  const res = await fetch(`${API_URL}/stats/hand_result`, {
    method: 'POST',
    headers: await getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse(res);
}

