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
  dealerIndex: number = 0
): Promise<GameState> {
  const res = await fetch(`${API_URL}/game/start`, {
    method: 'POST',
    headers: await getHeaders(),
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

export async function getAllStats(): Promise<Record<string, OpponentProfile & { total_hands: number }>> {
  const res = await fetch(`${API_URL}/stats`, {
    method: 'GET',
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

