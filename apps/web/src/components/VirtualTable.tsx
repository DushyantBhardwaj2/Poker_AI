import React, { useState, useEffect, useRef } from 'react';
import { User, Wallet, Coins, Target, UserPlus, UserMinus, XCircle, Plus } from 'lucide-react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';
import type { GameState, Player, ActionType, Card, PlayerStatus } from '../lib/api';
import { CardComponent, CardBack } from './CardComponent';

// --- Adaptive Spatial Layout Helpers ---
// Calculate radial position based on player count with protected center safe-zone
const getAdaptiveRadius = (numPlayers: number) => {
  // Scale down with more players to prevent overlap with center
  const baseRadius = 42;
  const shrinkFactor = Math.max(0, numPlayers - 6) * 2;
  return {
    rx: baseRadius - shrinkFactor,
    ry: 38 - shrinkFactor,
    // Pod size scales down for larger games
    podScale: numPlayers >= 7 ? 0.75 : numPlayers >= 5 ? 0.85 : 1
  };
};

const getPlayerPosition = (index: number, numPlayers: number) => {
  const { rx, ry } = getAdaptiveRadius(numPlayers);
  const angle = (index * (360 / numPlayers) - 90) * (Math.PI / 180);

  return {
    left: `${50 + Math.cos(angle) * rx}%`,
    top: `${50 + Math.sin(angle) * ry}%`
  };
};

interface PlayerPodProps {
  player: Player;
  index: number;
  numPlayers: number;
  isActive: boolean;
  isDealer: boolean;
  onSitOut?: (idx: number) => void;
  onLeave?: (idx: number) => void;
  onUpdateStack?: (idx: number, amount: number) => void;
  onDragStart?: (idx: number) => void;
  onDragOver?: (idx: number) => void;
  onDrop?: (idx: number) => void;
  position: { top: string; left: string };
  scale: number;
}

const PlayerPod: React.FC<PlayerPodProps> = ({
  player,
  index,
  numPlayers,
  isActive,
  isDealer,
  onSitOut,
  onLeave,
  onUpdateStack,
  onDragStart,
  onDragOver,
  onDrop,
  position,
  scale
}) => {
  const [isEditingStack, setIsEditingStack] = React.useState(false);
  const [tempStack, setTempStack] = React.useState(player.stack.toString());
  const [showMenu, setShowMenu] = React.useState(false);

  // Adaptive sizing based on player count
  const compact = scale < 0.9;
  const podSizes = {
    container: compact ? 'w-32 h-32 p-2 rounded-2xl' : 'w-40 h-40 p-2.5 rounded-3xl',
    avatar: compact ? 'w-8 h-8' : 'w-10 h-10',
    name: compact ? 'text-[10px]' : 'text-xs',
    stack: compact ? 'text-[9px]' : 'text-[10px]',
    cards: compact ? 'gap-0.5 -bottom-6' : 'gap-1 -bottom-8'
  };

  const getStatusBorder = () => {
    if (player.status === 'folded') return 'border-red-900/30 opacity-40 grayscale';
    if (player.status === 'sitting-out') return 'border-white/5 opacity-25 grayscale';
    if (player.status === 'all-in') return 'border-amber-warm/50 shadow-gold-subtle';
    if (isActive) return 'border-gold/60 shadow-gold-subtle ring-1 ring-gold/10';
    return 'border-white/8';
  };

  const handleStackSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const amount = parseInt(tempStack);
    if (!isNaN(amount)) {
      onUpdateStack?.(index, amount);
    }
    setIsEditingStack(false);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1, top: position.top, left: position.left }}
      transition={{ type: 'spring', damping: 20, stiffness: 100 }}
      className={`absolute -translate-x-1/2 -translate-y-1/2 z-10 cursor-grab active:cursor-grabbing`}
      draggable
      onDragStart={() => onDragStart?.(index)}
      onDragOver={(e) => {
        e.preventDefault();
        onDragOver?.(index);
      }}
      onDrop={() => onDrop?.(index)}
    >
      <div className={`relative group ${podSizes.container} bg-charcoal-dark/95 border-2 backdrop-blur-sm flex flex-col items-center justify-center transition-all duration-300 ${isActive ? 'scale-110 z-20' : 'scale-100 hover:scale-105 z-10'} ${getStatusBorder()}`}>
        
        {/* Management Overlay */}
        <AnimatePresence>
            {showMenu && (
                <motion.div 
                    initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
                    animate={{ opacity: 1, backdropFilter: 'blur(4px)' }}
                    exit={{ opacity: 0, backdropFilter: 'blur(0px)' }}
                    className="absolute inset-0 bg-black/80 rounded-3xl flex flex-col items-center justify-center gap-2 z-30"
                    onClick={(e) => {
                        e.stopPropagation();
                        setShowMenu(false);
                    }}
                >
                <div className="grid grid-cols-2 gap-2 p-4">
                        {player.status === 'sitting-out' ? (
                            <button onClick={() => onSitOut?.(index)} className="flex flex-col items-center gap-1 p-2 bg-green-500/20 text-green-400 rounded-xl hover:bg-green-500 hover:text-white transition-all">
                                <UserPlus size={20} />
                                <span className="text-[8px] font-black uppercase">Join</span>
                            </button>
                        ) : (
                            <button onClick={() => onSitOut?.(index)} title="Sit Out" className="flex flex-col items-center gap-1 p-2 bg-white/10 text-white/60 rounded-xl hover:bg-amber-warm hover:text-charcoal-dark transition-all">
                                <UserMinus size={20} />
                                <span className="text-[8px] font-black uppercase">Away</span>
                            </button>
                        )}
                        <button onClick={() => onLeave?.(index)} title="Remove" className="flex flex-col items-center gap-1 p-2 bg-red-600/10 text-red-500 rounded-xl hover:bg-red-600 hover:text-white transition-all">
                            <XCircle size={20} />
                            <span className="text-[8px] font-black uppercase">Kick</span>
                        </button>
                        <button onClick={() => setIsEditingStack(true)} title="Edit Stack" className="flex flex-col items-center gap-1 p-2 bg-gold/10 text-gold rounded-xl hover:bg-gold hover:text-black transition-all">
                            <Plus size={20} />
                            <span className="text-[8px] font-black uppercase">Stack</span>
                        </button>
                        <button className="flex flex-col items-center gap-1 p-2 bg-white/5 text-white/30 rounded-xl">
                            <User size={20} />
                            <span className="text-[8px] font-black uppercase">Close</span>
                        </button>
                </div>
                </motion.div>
            )}
        </AnimatePresence>

        {/* Dealer Button */}
        {isDealer && (
          <motion.div
            layoutId="dealer-button"
            initial={{ scale: 0.5, rotate: -45 }}
            animate={{ scale: 1, rotate: 0 }}
            className={`absolute -top-2 -right-2 ${compact ? 'w-6 h-6 text-[8px]' : 'w-8 h-8 text-[10px]'} bg-cream text-charcoal-dark rounded-full border-2 border-gold shadow-lg flex items-center justify-center font-black z-40`}
          >
            D
          </motion.div>
        )}

        {/* Action Status Ring */}
        {isActive && (
          <motion.div
            className={`absolute inset-0 ${compact ? 'rounded-2xl' : 'rounded-3xl'} border-2 border-gold shadow-[0_0_20px_rgba(212,175,55,0.4)] pointer-events-none`}
            animate={{
                opacity: [0.3, 0.7, 0.3],
                scale: [1, 1.02, 1]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}

        {/* Player Name & Avatar */}
        <div className="text-center space-y-1" onClick={() => setShowMenu(!showMenu)}>
          <motion.div
            className={`${podSizes.avatar} mx-auto rounded-xl flex items-center justify-center mb-1 transition-transform duration-300 ${isActive ? 'bg-gold text-charcoal-dark shadow-gold' : 'bg-charcoal border border-white/10 text-gold/40'} ${showMenu ? 'scale-90' : 'scale-100'}`}
            whileHover={{ scale: 1.1 }}
          >
            {index === 0 ? <Target size={compact ? 14 : 18} /> : <User size={compact ? 14 : 18} />}
          </motion.div>
          <h4 className={`${podSizes.name} font-black text-white uppercase tracking-tighter truncate w-24`}>
            {player.name}
          </h4>

          {isEditingStack ? (
            <form onSubmit={handleStackSubmit} className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
              <input
                autoFocus
                type="number"
                value={tempStack}
                onChange={(e) => setTempStack(e.target.value)}
                onBlur={() => handleStackSubmit()}
                className="w-16 bg-black/40 border border-gold/30 rounded px-1 py-0.5 text-xs text-gold font-mono outline-none focus:border-gold"
              />
            </form>
          ) : (
            <div
              className={`${podSizes.stack} flex items-center justify-center gap-0.5 font-mono text-gold/60 cursor-pointer hover:text-gold transition-colors`}
              onClick={(e) => {
                e.stopPropagation();
                setTempStack(player.stack.toString());
                setIsEditingStack(true);
              }}
            >
               <Coins size={10} /> ${player.stack.toLocaleString()}
            </div>
          )}
        </div>

        {/* Current Bet Display */}
        <AnimatePresence>
            {player.current_bet > 0 && (
                <motion.div 
                    initial={{ y: 20, opacity: 0, scale: 0.5 }}
                    animate={{ y: 0, opacity: 1, scale: 1 }}
                    exit={{ y: -20, opacity: 0, scale: 0.5 }}
                    className="absolute -bottom-12 left-1/2 -translate-x-1/2 bg-gold text-charcoal-dark px-4 py-1.5 rounded-full font-black font-mono text-xs shadow-gold whitespace-nowrap z-20"
                >
                    ${player.current_bet}
                </motion.div>
            )}
        </AnimatePresence>

        {/* Cards Display */}
        <div className={`absolute left-1/2 -translate-x-1/2 flex gap-0.5 z-20 ${podSizes.cards}`}>
            {index === 0 && player.hole_cards.length === 2 && (
                player.hole_cards.map((c, ci) => {
                    const dealerPos = getPlayerPosition(isDealer ? index : (index + 1) % numPlayers, numPlayers);
                    return (
                        <motion.div
                            key={ci}
                            initial={{
                                y: 100,
                                x: (parseFloat(dealerPos.left) - parseFloat(position.left)) * 10,
                                opacity: 0,
                                rotate: -180,
                                scale: 0
                            }}
                            animate={{ y: 0, x: 0, opacity: 1, rotate: ci === 0 ? -5 : 5, scale: 1 }}
                            transition={{ type: 'spring', damping: 20, stiffness: 100, delay: ci * 0.1 }}
                            whileHover={{ y: -5, scale: 1.1, rotate: 0 }}
                        >
                            <CardComponent card={c} size={compact ? 'xs' : 'sm'} />
                        </motion.div>
                    );
                })
            )}
            {index !== 0 && player.hole_cards.length === 2 && player.status === 'active' && (
                <>
                    <motion.div
                        initial={{ y: 100, opacity: 0, rotate: -180, scale: 0 }}
                        animate={{ y: 0, opacity: 1, rotate: 0, scale: 1 }}
                        transition={{ type: 'spring', damping: 20, delay: 0.2 }}
                    >
                        <CardBack size={compact ? 'xs' : 'sm'} />
                    </motion.div>
                    <motion.div
                        initial={{ y: 100, opacity: 0, rotate: -180, scale: 0 }}
                        animate={{ y: 0, opacity: 1, rotate: 0, scale: 1 }}
                        transition={{ type: 'spring', damping: 20, delay: 0.3 }}
                    >
                        <CardBack size={compact ? 'xs' : 'sm'} />
                    </motion.div>
                </>
            )}
        </div>

        {/* Status Indicators */}
        {index !== 0 && (player.status === 'folded' || player.status === 'sitting-out') && (
          <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[8px] font-bold text-red-500/50 uppercase tracking-widest">
            {player.status === 'folded' ? 'Folded' : 'Away'}
          </div>
        )}
      </div>
    </motion.div>
  );
};

// --- Chip Particle for Animation ---
type ChipType = 'bet' | 'win';

const ChipParticle: React.FC<{
    start: { x: number, y: number },
    end: { x: number, y: number },
    type?: ChipType,
    onComplete: () => void
}> = ({ start, end, type = 'bet', onComplete }) => (
    <motion.div
        initial={{
            x: start.x,
            y: start.y - 80,
            scale: 0,
            opacity: 0,
            rotate: -45
        }}
        animate={{
            x: [start.x, end.x + (Math.random() - 0.5) * 30],
            y: [start.y - 80, end.y],
            scale: type === 'bet' ? [0, 1.3, 0.9, 1] : [0, 1.4, 1.1, 1],
            opacity: [0, 1, 1, 0],
            rotate: type === 'bet' ? [180, -30, 15, 0] : [-180, 30, -15, 0]
        }}
        transition={{
            duration: 0.6,
            ease: [0.34, 1.56, 0.64, 1],
            times: [0, 0.4, 0.7, 1]
        }}
        onAnimationComplete={onComplete}
        className={`fixed w-6 h-6 rounded-full border-2 shadow-lg z-[100] flex items-center justify-center pointer-events-none ${
            type === 'bet' ? 'bg-gold border-gold-dark shadow-gold/50' : 'bg-green-500 border-green-600 shadow-green-500/50'
        }`}
    >
        <div className={`w-3 h-3 rounded-full border ${type === 'bet' ? 'border-white/20' : 'border-white/40'}`} />
    </motion.div>
);

interface VirtualTableProps {
  gameState: GameState;
  onAction: (type: ActionType, amount?: number) => void;
  onOpenCardInput: () => void;
  onRefillStack: (playerIndex: number, amount: number) => void;
  onUpdatePlayerStatus?: (index: number, status: PlayerStatus) => void;
  onRemovePlayer?: (index: number) => void;
  onUpdateStack?: (index: number, amount: number) => void;
  onReorderPlayers?: (from: number, to: number) => void;
  onRotateDealer?: (dir: 'cw' | 'ccw') => void;
  onUndo?: () => void;
  hasUndo?: boolean;
}

export const VirtualTable: React.FC<VirtualTableProps> = ({
  gameState,
  onAction,
  onOpenCardInput,
  onRefillStack,
  onUpdatePlayerStatus,
  onRemovePlayer,
  onUpdateStack,
  onReorderPlayers,
  onRotateDealer,
  onUndo,
  hasUndo
}) => {
  const numPlayers = gameState.players.length;
  const [draggedIdx, setDraggedIdx] = React.useState<number | null>(null);
  
  // Chip Animation State
  const [chips, setChips] = useState<{ id: number, start: { x: number, y: number }, end: { x: number, y: number }, type?: ChipType }[]>([]);
  const lastPotRef = useRef(gameState.pot);
  const lastRoundRef = useRef(gameState.round);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const potIncreased = gameState.pot > lastPotRef.current;
    const roundChanged = gameState.round !== lastRoundRef.current;
    
    // Convert % to px relative to container
    const getPosPx = (pos: { left: string, top: string }) => {
        if (!containerRef.current) return { x: 0, y: 0 };
        const rect = containerRef.current.getBoundingClientRect();
        return {
            x: rect.left + (parseFloat(pos.left) / 100) * rect.width,
            y: rect.top + (parseFloat(pos.top) / 100) * rect.height
        };
    };

    if (potIncreased) {
      // Pot increased, spawn chips from current acting player (or previous acting player)
      const actingIdx = (gameState.current_player_index - 1 + numPlayers) % numPlayers;
      const start = getPosPx(getPlayerPosition(actingIdx, numPlayers));
      const end = getCenterPoint();
      
      const newChips = Array.from({ length: 8 }).map((_, i) => ({
          id: Math.random() + i,
          start: { x: start.x + (Math.random() - 0.5) * 60, y: start.y + (Math.random() - 0.5) * 60 },
          end: { x: end.x + (Math.random() - 0.5) * 40, y: end.y + (Math.random() - 0.5) * 40 },
          type: 'bet' as ChipType
      }));
      
      setChips(prev => [...prev, ...newChips]);
    }

    // Logic for winning chips (pot to winner)
    if (gameState.pot === 0 && lastPotRef.current > 0) {
        const center = getCenterPoint();
        // Fallback: spawn chips to the first active player or dealer
        const targetIdx = gameState.dealer_index; 
        const end = getPosPx(getPlayerPosition(targetIdx, numPlayers));

        const winChips = Array.from({ length: 15 }).map((_, i) => ({
            id: Math.random() + i,
            start: { x: center.x + (Math.random() - 0.5) * 50, y: center.y + (Math.random() - 0.5) * 50 },
            end: { x: end.x + (Math.random() - 0.5) * 80, y: end.y + (Math.random() - 0.5) * 80 },
            type: 'win' as ChipType
        }));
        setChips(prev => [...prev, ...winChips]);
    }

    lastPotRef.current = gameState.pot;
    lastRoundRef.current = gameState.round;
  }, [gameState.pot, gameState.round, numPlayers]); // Added numPlayers to deps

  const getCenterPoint = () => {
    if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    }
    return { x: 0, y: 0 };
  };

  return (
    <div ref={containerRef} className="w-full aspect-[16/9] lg:aspect-[16/8] relative animate-fade-in mb-24">
      {/* Chip Animation Layer */}
      {chips.map(chip => (
          <ChipParticle
            key={chip.id}
            start={chip.start}
            end={getCenterPoint()}
            onComplete={() => setChips(prev => prev.filter(c => c.id !== chip.id))}
          />
      ))}

      {/* Undo Button */}
      {hasUndo && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onUndo}
          className="absolute top-2 left-2 z-40 p-2 bg-white/5 hover:bg-gold/10 text-gold/40 hover:text-gold border border-white/10 rounded-xl transition-all flex items-center gap-2 group"
        >
          <Target size={14} className="rotate-180 group-hover:rotate-90 transition-transform" />
          <span className="text-[9px] font-black uppercase tracking-widest">Undo</span>
        </motion.button>
      )}

      {/* Dealer Rotation */}
      <div className="absolute top-2 right-2 z-40 flex gap-1.5">
         <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => onRotateDealer?.('ccw')}
          className="p-2 bg-white/5 hover:bg-gold/10 text-gold/40 hover:text-gold border border-white/10 rounded-xl transition-all"
          title="Rotate Dealer CCW"
        >
          <Target size={14} className="-scale-x-100" />
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => onRotateDealer?.('cw')}
          className="p-2 bg-white/5 hover:bg-gold/10 text-gold/40 hover:text-gold border border-white/10 rounded-xl transition-all"
          title="Rotate Dealer CW"
        >
          <Target size={14} />
        </motion.button>
      </div>

      {/* The Central "Felt" - Protected Safe Zone */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-[85%] h-[80%] bg-gradient-to-b from-charcoal/10 to-charcoal-dark/30 border-[2px] border-white/5 rounded-[160px] shadow-[inset_0_0_60px_rgba(0,0,0,0.4)] relative overflow-hidden">
           {/* Tactical Grid */}
           <div className="absolute inset-0 bg-[linear-gradient(rgba(212,175,55,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(212,175,55,0.015)_1px,transparent_1px)] bg-[size:60px_60px] pointer-events-none"></div>

           {/* Center Pot & Community Cards - Compact */}
           <div className="absolute inset-0 flex flex-col items-center justify-center gap-6">
              <div className="text-center">
                <span className="text-[10px] font-black text-gold/40 uppercase tracking-[0.3em] mb-1 block">Pot</span>
                <motion.div
                    key={gameState.pot}
                    initial={{ scale: 0.9, opacity: 0.8 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="text-4xl font-black text-white font-mono drop-shadow-gold"
                >
                  ${gameState.pot.toLocaleString()}
                </motion.div>
                <AnimatePresence>
                    {gameState.pots.length > 1 && (
                    <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex gap-1.5 justify-center mt-2"
                    >
                        {gameState.pots.map((p, i) => (
                        <span key={i} className="text-[8px] bg-white/5 border border-white/10 px-1.5 py-0.5 rounded text-gold/60 font-mono">
                            {i === 0 ? 'M' : `S${i}`}: ${p.amount}
                        </span>
                        ))}
                    </motion.div>
                    )}
                </AnimatePresence>
              </div>

              <div className="flex gap-3 bg-black/20 p-4 rounded-2xl border border-white/5 backdrop-blur-sm min-w-[280px] justify-center min-h-[100px] items-center group relative">
                <AnimatePresence mode="popLayout">
                    {gameState.community_cards.length > 0 ? (
                        gameState.community_cards.map((c, i) => {
                            const dealerPos = getPlayerPosition(gameState.dealer_index, numPlayers);
                            return (
                                <motion.div
                                    key={`${c.rank}-${c.suit}-${i}`}
                                    initial={{
                                        scale: 0,
                                        rotate: -90,
                                        x: (parseFloat(dealerPos.left) - 50) * 10,
                                        y: (parseFloat(dealerPos.top) - 50) * 10,
                                        opacity: 0
                                    }}
                                    animate={{ scale: 1, rotate: 0, x: 0, y: 0, opacity: 1 }}
                                    transition={{
                                        type: 'spring',
                                        damping: 20,
                                        stiffness: 120,
                                        delay: i * 0.1
                                    }}
                                >
                                    <CardComponent card={c} size="md" />
                                </motion.div>
                            );
                        })
                    ) : (
                        <span className="text-[9px] font-black text-gold/20 uppercase tracking-[0.2em] italic">Awaiting Cards</span>
                    )}
                </AnimatePresence>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onOpenCardInput}
                  className="absolute -right-3 -top-3 w-10 h-10 bg-gold text-charcoal-dark rounded-full flex items-center justify-center shadow-gold transition-all z-30"
                >
                   <Target size={20} />
                </motion.button>
              </div>

              <motion.div
                layout
                className="flex items-center gap-2 bg-gold/5 px-4 py-1.5 rounded-full border border-gold/20"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse"></span>
                <span className="text-[9px] font-black text-gold uppercase tracking-widest">{gameState.round}</span>
              </motion.div>
           </div>
        </div>
      </div>

      {/* Player Pods */}
      {gameState.players.map((p, i) => {
        const { podScale } = getAdaptiveRadius(numPlayers);
        return (
        <PlayerPod
          key={p.name}
          player={p}
          index={i}
          numPlayers={numPlayers}
          isActive={gameState.current_player_index === i}
          isDealer={gameState.dealer_index === i}
          position={getPlayerPosition(i, numPlayers)}
          scale={podScale}
          onSitOut={(idx) => onUpdatePlayerStatus?.(idx, 'sitting-out')}
          onLeave={(idx) => onRemovePlayer?.(idx)}
          onUpdateStack={onUpdateStack}
          onDragStart={(idx) => setDraggedIdx(idx)}
          onDrop={(idx) => {
            if (draggedIdx !== null && draggedIdx !== idx) {
              onReorderPlayers?.(draggedIdx, idx);
            }
            setDraggedIdx(null);
          }}
        />
        );
      })}
    </div>
  );
};
