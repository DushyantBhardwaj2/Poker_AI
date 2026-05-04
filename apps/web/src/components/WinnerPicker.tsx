import React from 'react';
import { Trophy, User, ArrowRight } from 'lucide-react';
import type { GameState } from '../lib/api';

interface WinnerPickerProps {
  gameState: GameState;
  onSelectWinner: (idx: number) => void;
}

export const WinnerPicker: React.FC<WinnerPickerProps> = ({ gameState, onSelectWinner }) => {
  const activePlayers = gameState.players.map((p, i) => ({ ...p, originalIdx: i }))
    .filter(p => !p.is_folded);

  return (
    <div className="max-w-2xl w-full glass-dark border border-gold/30 rounded-[40px] p-10 animate-scale-in shadow-gold-strong">
      <div className="text-center space-y-4 mb-10">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gold/10 border border-gold/20 rounded-full mb-2">
          <Trophy size={40} className="text-gold" />
        </div>
        <h2 className="text-4xl font-black text-white uppercase tracking-tighter italic">Hand Concluded</h2>
        <p className="text-cream/50 font-bold uppercase tracking-[0.2em] text-xs">Who claimed the pot of <span className="text-gold">${gameState.pot}</span>?</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {activePlayers.map((p) => (
          <button
            key={p.originalIdx}
            onClick={() => onSelectWinner(p.originalIdx)}
            className="group flex items-center gap-6 bg-white/5 hover:bg-gold/10 border border-white/5 hover:border-gold/30 p-6 rounded-3xl transition-all text-left"
          >
            <div className="w-14 h-14 bg-charcoal rounded-2xl flex items-center justify-center text-gold/40 group-hover:text-gold border border-white/5 group-hover:border-gold/20 transition-all">
              <User size={28} />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-black text-cream uppercase tracking-wider">{p.name}</h3>
              <p className="text-[10px] text-cream/30 font-bold uppercase tracking-widest mt-1">
                {p.originalIdx === 0 ? 'USER' : `PLAYER ${p.originalIdx + 1}`} // ACTIVE
              </p>
            </div>
            <div className="w-10 h-10 rounded-full bg-white/5 group-hover:bg-gold flex items-center justify-center text-cream/20 group-hover:text-charcoal transition-all">
              <ArrowRight size={20} />
            </div>
          </button>
        ))}
      </div>

      <div className="mt-10 pt-8 border-t border-white/5 text-center">
        <p className="text-[9px] text-cream/20 font-black uppercase tracking-[0.3em]">Theoretical analysis will follow selection</p>
      </div>
    </div>
  );
};
