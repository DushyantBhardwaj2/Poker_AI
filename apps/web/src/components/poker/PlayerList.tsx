import React from 'react';
import { usePokerStore } from '../../stores/usePokerStore';

export default function PlayerList() {
  const { players, activePlayerIndex } = usePokerStore();

  return (
    <div className="flex flex-col gap-3 h-full">
      <div className="text-xs tracking-widest text-emerald-500/70 uppercase mb-2">Target Operators</div>
      
      {players.map((player, index) => {
        const isActive = index === activePlayerIndex;
        const isFolded = player.status === 'folded';
        const isAllIn = player.status === 'all-in';

        return (
          <div 
            key={player.id} 
            className={`
              relative p-4 border transition-all duration-300
              ${isActive ? 'border-amber-400 bg-amber-400/5 shadow-[0_0_15px_rgba(251,191,36,0.15)]' : 'border-gray-800 bg-gray-900'}
              ${isFolded ? 'opacity-40 grayscale' : ''}
              ${isAllIn ? 'border-red-500/50 bg-red-500/5' : ''}
            `}
          >
            {/* Active Indicator Pulse */}
            {isActive && (
              <div className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-amber-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(251,191,36,0.8)]" />
            )}

            <div className="flex justify-between items-start mb-2">
              <div className="font-mono text-lg font-bold tracking-wider text-gray-100 flex items-center gap-2">
                {player.name}
                {isFolded && <span className="text-[10px] bg-gray-800 text-gray-400 px-1 py-0.5 rounded-sm">FOLD</span>}
                {isAllIn && <span className="text-[10px] bg-red-900/50 text-red-400 px-1 py-0.5 rounded-sm border border-red-500/30">ALL-IN</span>}
              </div>
              <div className="text-sm font-mono text-amber-400">
                ${player.stack}
              </div>
            </div>

            <div className="flex justify-between items-end">
              <div className="text-xs text-gray-500 font-mono flex flex-col">
                <span>VPIP: {player.vpip || 0}%</span>
                <span>PFR: {player.pfr || 0}%</span>
              </div>
              {player.bet > 0 && (
                <div className="text-emerald-400 font-mono text-sm bg-emerald-950/50 px-2 py-1 border border-emerald-900/50">
                  Bet: ${player.bet}
                </div>
              )}
            </div>

            {/* Corner Accents */}
            <div className={`absolute top-0 left-0 w-2 h-2 border-t border-l ${isActive ? 'border-amber-400' : 'border-gray-700'}`}></div>
            <div className={`absolute bottom-0 right-0 w-2 h-2 border-b border-r ${isActive ? 'border-amber-400' : 'border-gray-700'}`}></div>
          </div>
        );
      })}
    </div>
  );
}
