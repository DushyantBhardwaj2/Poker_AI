import React from 'react';
import { usePokerStore } from '../../stores/usePokerStore';
import { ChevronRight } from 'lucide-react';

export default function Board() {
  const { pot, round, community_cards, advanceStreet } = usePokerStore();

  const handleNextStreet = () => {
    const streets: typeof round[] = ['pre-flop', 'flop', 'turn', 'river', 'showdown'];
    const nextIdx = streets.indexOf(round) + 1;
    if (nextIdx < streets.length) {
      // In a real app, this would trigger a card selector modal before advancing
      advanceStreet(streets[nextIdx]);
    }
  };

  // Ensure we always have 5 slots
  const displayCards = [...community_cards];

  return (
    <div className="flex flex-col h-full border border-gray-800 bg-gray-900/40 relative">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 bg-gray-950 px-4 py-1 text-xs tracking-widest text-emerald-500 border-x border-b border-gray-800 font-mono">
        {round.toUpperCase()}
      </div>

      <div className="flex-1 flex flex-col items-center justify-center p-8">
        
        <div className="text-center mb-12">
          <div className="text-sm tracking-widest text-gray-500 font-mono mb-2 uppercase">Total Pot</div>
          <div className="text-6xl font-bold font-mono text-emerald-400 tracking-tighter drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]">
            ${pot}
          </div>
        </div>

        <div className="flex gap-4 justify-center w-full mb-12">
          {Array.from({ length: 5 }).map((_, idx) => {
            const card = displayCards[idx];
            return (
              <div 
                key={idx}
                className={`
                  w-20 h-28 border flex items-center justify-center text-xl font-bold
                  transition-all duration-500
                  ${card ? 'bg-gray-100 text-gray-900 border-gray-300' : 'bg-gray-950/50 border-gray-800 border-dashed'}
                `}
                style={{
                  boxShadow: card ? 'inset 0 0 10px rgba(0,0,0,0.1)' : 'none'
                }}
              >
                {card ? `${card.rank}${card.suit}` : <span className="text-gray-800 text-xs font-mono">{idx + 1}</span>}
              </div>
            );
          })}
        </div>

      </div>

      <div className="p-4 border-t border-gray-800 bg-gray-900/80">
        <button 
          onClick={handleNextStreet}
          disabled={round === 'showdown'}
          className="w-full flex items-center justify-center gap-2 bg-transparent border border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-400 py-4 font-mono tracking-widest text-sm transition-all disabled:opacity-30 disabled:pointer-events-none"
        >
          NEXT_STREET <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Decorative Grid Lines */}
      <div className="absolute inset-0 pointer-events-none opacity-5 bg-[linear-gradient(rgba(255,255,255,1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,1)_1px,transparent_1px)] bg-[size:40px_40px]"></div>
    </div>
  );
}
