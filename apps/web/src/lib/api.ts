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
  name: string;
  stack: number;
  hole_cards: Card[];
  current_bet: number;
  total_contributed: number;
  is_folded: boolean;
  is_all_in: boolean;
  status: PlayerStatus;
  has_acted: boolean;
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

export interface FullAnalysisResponse {
  win_analysis: {
    win_probability: number;
    tie_probability: number;
    equity: number;
  };
  bluff_analysis: {
    bluff_probability: number;
    is_bluff: boolean;
    threshold: number;
    street_rank: number;
  };
  advice: {
    action: string;
    ev: number;
    pot_odds: number;
    explanation: string;
    theory_tip?: string;
  };
  opponent_profile: {
    vpip: number;
    pfr: number;
    classification: string;
    description: string;
  };
}

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Internal helper for X-User-Id
const getHeaders = () => {
  const userId = typeof window !== 'undefined' ? localStorage.getItem('user_id') || '4895a071-3647-4e88-9c45-9e0e247946db' : '4895a071-3647-4e88-9c45-9e0e247946db';
  return {
    'Content-Type': 'application/json',
    'X-User-Id': userId
  };
};

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
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function processAction(state: GameState, action: Action): Promise<GameState> {
  const res = await fetch(`${API_URL}/game/action`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ state, action }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function showdown(state: GameState, blufferNames: string[] = []): Promise<{ new_state: GameState; result: unknown }> {
  const res = await fetch(`${API_URL}/game/showdown`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ state, bluffer_names: blufferNames }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
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
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getWinProbability(
  holeCards: Card[],
  communityCards: Card[],
  numOpponents: number,
  numSimulations = 500
): Promise<{ win_probability: number; tie_probability: number; equity: number }> {
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
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function recommendMove(
  winProbability: number,
  potSize: number,
  callAmount: number,
  playerStack: number
): Promise<{ action: ActionType; ev: number; pot_odds: number; explanation: string }> {
  const res = await fetch(`${API_URL}/ai/recommend-move`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      win_probability: winProbability,
      pot_size: potSize,
      call_amount: callAmount,
      player_stack: playerStack,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getAllStats(): Promise<Record<string, { total_hands: number; vpip: number; pfr: number; classification: string; description: string }>> {
  const res = await fetch(`${API_URL}/stats`, {
    method: 'GET',
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}