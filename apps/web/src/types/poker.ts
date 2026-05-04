export type GameRound = 'pre-flop' | 'flop' | 'turn' | 'river' | 'showdown';
export type ActionType = 'fold' | 'check' | 'call' | 'raise' | 'all-in';
export type PlayerStatus = 'active' | 'folded' | 'all-in' | 'sitting-out';

export interface Player {
  id: string;
  name: string;
  stack: number;
  bet: number;
  status: PlayerStatus;
  cards?: string[]; // e.g., ['Ah', 'Kd']
  vpip?: number;
  pfr?: number;
  bluff_freq?: number;
  play_style?: 'TAG' | 'LAG' | 'Nit' | 'Unknown';
}

export interface GameState {
  sessionId: string | null;
  players: Player[];
  currentStreet: GameRound;
  potSize: number;
  activePlayerIndex: number;
  boardCards: string[];
  isProcessing: boolean;
  error: string | null;
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
  features_snapshot: Record<string, any>;
}

export interface OpponentProfile {
  vpip: number;
  pfr: number;
  classification: string;
  description: string;
}

export interface StrategicAdvice {
  action: string;
  ev: number;
  pot_odds: number;
  explanation: string;
  adjusted_win_probability: number;
  theory_tip?: string;
}

export interface FullAnalysisResponse {
  win_analysis: WinAnalysis;
  bluff_analysis: BluffAnalysis;
  advice: StrategicAdvice;
  opponent_profile: OpponentProfile;
}
