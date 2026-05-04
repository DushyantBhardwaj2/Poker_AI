import { create } from 'zustand';
import type { GameState, Player, ActionType, GameRound } from '../types/poker';

interface PokerStore extends GameState {
  // Actions
  setSession: (id: string) => void;
  setPlayers: (players: Player[]) => void;
  updatePlayerAction: (name: string, action: ActionType, amount?: number) => void;
  advanceStreet: (street: GameRound, cards?: string[]) => void;
  setError: (msg: string | null) => void;
  setProcessing: (isProcessing: boolean) => void;
  nextPlayer: () => void;
  resetGame: () => void;
  updateBoardCards: (cards: string[]) => void;
}

const initialState = {
  sessionId: null,
  players: [],
  currentStreet: 'pre-flop' as GameRound,
  potSize: 0,
  activePlayerIndex: 0,
  boardCards: [],
  isProcessing: false,
  error: null,
};

export const usePokerStore = create<PokerStore>((set) => ({
  ...initialState,

  setSession: (id) => set({ sessionId: id }),
  
  setPlayers: (players) => set({ players }),

  updatePlayerAction: (name, action, amount = 0) => set((state) => {
    // Optimistic UI updates
    const updatedPlayers = state.players.map(p => {
      if (p.name === name) {
        let newStack = p.stack;
        let newBet = p.bet;
        let newStatus = p.status;

        if (action === 'fold') {
          newStatus = 'folded';
        } else if (action === 'call' || action === 'raise' || action === 'all-in') {
          // Adjust amount to be only the additional amount put in? 
          // Assuming amount is the total amount they are putting in this action
          const deduct = Math.min(newStack, amount);
          newStack -= deduct;
          newBet += deduct;
          if (newStack === 0) newStatus = 'all-in';
        }

        return { ...p, stack: newStack, bet: newBet, status: newStatus };
      }
      return p;
    });

    return { 
      players: updatedPlayers,
      potSize: state.potSize + amount 
    };
  }),

  advanceStreet: (street, cards = []) => set((state) => ({ 
    currentStreet: street, 
    boardCards: [...state.boardCards, ...cards],
    // Reset bets for the new street
    players: state.players.map(p => ({ ...p, bet: 0 }))
  })),

  updateBoardCards: (cards) => set({ boardCards: cards }),

  setError: (msg) => set({ error: msg }),

  setProcessing: (isProcessing) => set({ isProcessing }),

  nextPlayer: () => set((state) => {
    // Find next active player
    let nextIndex = (state.activePlayerIndex + 1) % state.players.length;
    let loopCount = 0;
    while (
      state.players[nextIndex].status === 'folded' || 
      state.players[nextIndex].status === 'all-in' ||
      state.players[nextIndex].status === 'sitting-out'
    ) {
      nextIndex = (nextIndex + 1) % state.players.length;
      loopCount++;
      if (loopCount > state.players.length) break; // Infinite loop prevention
    }
    return { activePlayerIndex: nextIndex };
  }),

  resetGame: () => set({ ...initialState })
}));
