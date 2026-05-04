import React from 'react';
import { User, Wallet, Coins, Target } from 'lucide-react';
import type { GameState, Player, ActionType, Card } from '../lib/api';
import { CardComponent } from './CardComponent';

interface PlayerPodProps {
  player: Player;
  index: number;
  isActive: boolean;
  isDealer: boolean;
  onSitOut?: (idx: number) => void;
  onLeave?: (idx: number) => void;
  position: { top: string; left: string };
}

export const PlayerPod: React.FC<PlayerPodProps> = ({
  player,
  index,
  isActive,
  isDealer,
  onSitOut,
  onLeave,
  position
}) => {
  const getStatusBorder = () => {
    if (player.status === 'folded') return 'border-red-900/40 opacity-50 grayscale';
    if (player.status === 'sitting-out') return 'border-white/5 opacity-30 grayscale';
    if (player.status === 'all-in') return 'border-amber-warm shadow-[0_0_15px_rgba(255,191,0,0.3)]';
    if (isActive) return 'border-gold shadow-[0_0_20px_rgba(212,175,55,0.4)] ring-2 ring-gold/20';
    return 'border-white/10';
  };

  return (
    <div 
      className={`absolute transition-all duration-700 ease-in-out transform -translate-x-1/2 -translate-y-1/2 z-10`}
      style={{ top: position.top, left: position.left }}
    >
      <div className={`relative group w-32 h-32 rounded-3xl bg-charcoal-dark/90 border-2 backdrop-blur-md flex flex-col items-center justify-center p-2 transition-all ${isActive ? 'scale-110' : 'scale-100 hover:scale-105'} ${getStatusBorder()}`}>
        
        {/* Management Overlay (Hidden by default, shown on hover) */}
        <div className="absolute inset-0 bg-black/60 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 z-30">
           {player.status === 'sitting-out' ? (
              <button onClick={() => onSitOut?.(index)} className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500 hover:text-white transition-all">
                <UserPlus size={16} />
              </button>
           ) : (
              <button onClick={() => onSitOut?.(index)} title="Sit Out" className="p-2 bg-white/10 text-white/60 rounded-lg hover:bg-amber-warm hover:text-charcoal-dark transition-all">
                <UserMinus size={16} />
              </button>
           )}
           <button onClick={() => onLeave?.(index)} title="Remove" className="p-2 bg-red-600/10 text-red-500 rounded-lg hover:bg-red-600 hover:text-white transition-all">
              <XCircle size={16} />
           </button>
        </div>

        {/* Dealer Button */}
        {isDealer && (
          <div className="absolute -top-3 -right-3 w-8 h-8 bg-cream text-charcoal-dark rounded-full border-2 border-gold shadow-lg flex items-center justify-center font-black text-[10px] z-20">
            D
          </div>
        )}

        {/* Action Status Ring */}
        {isActive && (
          <div className="absolute inset-0 rounded-3xl border-2 border-gold animate-pulse-gold pointer-events-none" />
        )}

        {/* Player Name & Avatar */}
        <div className="text-center space-y-1">
          <div className={`w-10 h-10 mx-auto rounded-xl flex items-center justify-center mb-1 ${isActive ? 'bg-gold text-charcoal-dark' : 'bg-charcoal border border-white/10 text-gold/40'}`}>
            {index === 0 ? <Target size={18} /> : <User size={18} />}
          </div>
          <h4 className="text-[11px] font-black text-white uppercase tracking-tighter truncate w-24">
            {player.name}
          </h4>
          <div className="flex items-center justify-center gap-1 text-[10px] font-mono text-gold/60">
             <Coins size={10} /> ${player.stack}
          </div>
        </div>

        {/* Current Bet Display */}
        {player.current_bet > 0 && (
          <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 bg-gold text-charcoal-dark px-3 py-1 rounded-full font-black font-mono text-[10px] shadow-gold whitespace-nowrap animate-slide-up z-20">
            ${player.current_bet}
          </div>
        )}

        {/* Mini Cards (For You) */}
        {index === 0 && player.hole_cards.length === 2 && (
          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 flex gap-1 animate-slide-up z-20">
            {player.hole_cards.map((c, ci) => (
              <CardComponent key={ci} card={c} size="xs" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

interface VirtualTableProps {
  gameState: GameState;
  onAction: (type: ActionType, amount?: number) => void;
  onOpenCardInput: () => void;
  onRefillStack: (playerIndex: number, amount: number) => void;
  onUpdatePlayerStatus?: (index: number, status: PlayerStatus) => void;
  onRemovePlayer?: (index: number) => void;
}

export const VirtualTable: React.FC<VirtualTableProps> = ({
  gameState,
  onAction,
  onOpenCardInput,
  onRefillStack,
  onUpdatePlayerStatus,
  onRemovePlayer
}) => {
  const numPlayers = gameState.players.length;

  const getPlayerPosition = (index: number) => {
    // Elliptical layout logic
    const angle = (index * (360 / numPlayers) - 90) * (Math.PI / 180);
    const rx = 40; // horizontal radius %
    const ry = 35; // vertical radius %
    
    return {
      left: `${50 + Math.cos(angle) * rx}%`,
      top: `${50 + Math.sin(angle) * ry}%`
    };
  };

  return (
    <div className="w-full h-[600px] relative animate-fade-in mb-24">
      {/* The Central "Felt" */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-[85%] h-[75%] bg-gradient-to-b from-charcoal/20 to-charcoal-dark/40 border-[3px] border-gold/10 rounded-[120px] shadow-[inset_0_0_100px_rgba(0,0,0,0.5)] relative overflow-hidden">
           {/* Tactical Grid */}
           <div className="absolute inset-0 bg-[linear-gradient(rgba(212,175,55,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(212,175,55,0.03)_1px,transparent_1px)] bg-[size:50px_50px] pointer-events-none"></div>
           
           {/* Center Pot & Community Cards */}
           <div className="absolute inset-0 flex flex-col items-center justify-center space-y-6">
              <div className="text-center">
                <span className="text-[10px] font-black text-gold/40 uppercase tracking-[0.4em] mb-1 block">Total Pot</span>
                <div className="text-4xl font-black text-white font-mono drop-shadow-gold">
                  ${gameState.pot}
                </div>
                {gameState.pots.length > 1 && (
                  <div className="flex gap-2 justify-center mt-2">
                    {gameState.pots.map((p, i) => (
                      <span key={i} className="text-[9px] bg-white/5 border border-white/10 px-2 py-0.5 rounded text-gold/60 font-mono">
                        {i === 0 ? 'M' : `S${i}`}: ${p.amount}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex gap-3 bg-black/20 p-4 rounded-3xl border border-white/5 backdrop-blur-sm min-w-[200px] justify-center min-h-[100px] items-center group relative">
                {gameState.community_cards.length > 0 ? (
                  gameState.community_cards.map((c, i) => (
                    <div key={i} className="animate-scale-in">
                      <CardComponent card={c} size="md" />
                    </div>
                  ))
                ) : (
                  <span className="text-[10px] font-black text-gold/20 uppercase tracking-[0.2em] italic">Awaiting Cards</span>
                )}
                <button 
                  onClick={onOpenCardInput}
                  className="absolute -right-4 -top-4 w-10 h-10 bg-gold text-charcoal-dark rounded-full flex items-center justify-center shadow-gold transition-all hover:scale-110 active:scale-90"
                >
                   <Target size={20} />
                </button>
              </div>
              
              <div className="flex items-center gap-2 bg-gold/5 px-4 py-1.5 rounded-full border border-gold/20">
                <span className="w-2 h-2 rounded-full bg-gold animate-pulse"></span>
                <span className="text-[10px] font-black text-gold uppercase tracking-widest">{gameState.round}</span>
              </div>
           </div>
        </div>
      </div>

      {/* Player Pods */}
      {gameState.players.map((p, i) => (
        <PlayerPod 
          key={i}
          player={p}
          index={i}
          isActive={gameState.current_player_index === i}
          isDealer={gameState.dealer_index === i}
          position={getPlayerPosition(i)}
          onSitOut={(idx) => onUpdatePlayerStatus?.(idx, 'sitting-out')}
          onLeave={(idx) => onRemovePlayer?.(idx)}
        />
      ))}
    </div>
  );
};
