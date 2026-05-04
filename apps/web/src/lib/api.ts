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

export interface StrategicAdvice {
  action: string;
  ev: number;
  pot_odds: number;
  explanation: string;
  theory_tip?: string;
}

export interface OpponentProfile {
  vpip: number;
  pfr: number;
  classification: string;
  description: string;
}

export interface FullAnalysisResponse {
  win_analysis: WinAnalysis;
  bluff_analysis: BluffAnalysis;
  advice: StrategicAdvice;
  opponent_profile: OpponentProfile;
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
    // If we're on localhost but no API URL is set, assume the default dev backend
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://localhost:8000/api/v1';
    }

    // PROD ALERT: In production (non-localhost), if no PUBLIC_API_URL is set, 
    // we fallback to a relative path assuming a proxy or same-domain deploy.
    return '/api/v1';
  }

  // 3. SSR fallback (for Astro build/server context)
  // During build time or SSR, we default to localhost unless PUBLIC_API_URL is provided.
  return 'http://localhost:8000/api/v1';
};

const API_URL = getBaseUrl();

// Internal helper for X-User-Id and other headers
const getHeaders = () => {
  const isBrowser = typeof window !== 'undefined';
  const defaultUserId = '4895a071-3647-4e88-9c45-9e0e247946db';
  
  let userId = defaultUserId;
  if (isBrowser) {
    try {
      userId = localStorage.getItem('user_id') || defaultUserId;
    } catch (e) {
      console.warn('Failed to access localStorage:', e);
    }
  }

  return {
    'Content-Type': 'application/json',
    'X-User-Id': userId
  };
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
  dealerIndex: number = 0
): Promise<GameState> {
  const res = await fetch(`${API_URL}/game/start`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      player_names: playerNames,
      initial_stacks: initialStacks,
      small_blind: smallBlind,
      big_blind: bigBlind,
      dealer_index: dealerIndex
    }),
  });
  return handleResponse(res);
}

export async function processAction(state: GameState, action: Action): Promise<GameState> {
  const res = await fetch(`${API_URL}/game/action`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ state, action }),
  });
  return handleResponse(res);
}

export async function showdown(state: GameState, blufferNames: string[] = []): Promise<{ new_state: GameState; result: any }> {
  const res = await fetch(`${API_URL}/game/showdown`, {
    method: 'POST',
    headers: getHeaders(),
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
    headers: getHeaders(),
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
    headers: getHeaders(),
    body: JSON.stringify({
      hole_cards: holeCards,
      community_cards: communityCards,
      num_opponents: numOpponents,
      num_simulations: numSimulations,
    }),
  });
  return handleResponse(res);
}

export async function getAllStats(): Promise<Record<string, OpponentProfile & { total_hands: number }>> {
  const res = await fetch(`${API_URL}/stats`, {
    method: 'GET',
    headers: getHeaders(),
  });
  return handleResponse(res);
}

// --- Session-based API (Object-style for compatibility) ---

export const PokerAPI = {
  startSession: () => 
    fetch(`${API_URL}/game/session/start`, { method: 'POST', headers: getHeaders() }).then(handleResponse),
  
  addPlayer: (sessionId: string, playerName: string, stack: number) =>
    fetch(`${API_URL}/game/session/add_player`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ session_id: sessionId, player_name: playerName, stack })
    }).then(handleResponse),
    
  recordAction: (sessionId: string, playerName: string, actionType: string, amount: number) =>
    fetch(`${API_URL}/game/session/record_action`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ session_id: sessionId, player_name: playerName, action_type: actionType, amount })
    }).then(handleResponse),
    
  nextStreet: (sessionId: string, nextStreet: string) =>
    fetch(`${API_URL}/game/session/next_street`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ session_id: sessionId, next_street: nextStreet })
    }).then(handleResponse),
    
  showdown: (sessionId: string, payload: any) =>
    fetch(`${API_URL}/game/session/showdown`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ session_id: sessionId, ...payload })
    }).then(handleResponse),
  
  analyzeFull: (payload: any) => 
    fetch(`${API_URL}/ai/analyze-full`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    }).then(handleResponse),
  
  getStats: () => 
    fetch(`${API_URL}/stats`, { method: 'GET', headers: getHeaders() }).then(handleResponse)
};
