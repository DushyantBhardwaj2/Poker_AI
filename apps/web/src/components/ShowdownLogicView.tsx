import React, { useState } from 'react';
import { Trophy, ArrowRight, Eye, EyeOff } from 'lucide-react';
import type { GameState, Player, Card } from '../lib/api';
import { CardComponent } from './CardComponent';
import { CardInputView } from './CardInputView';

interface ShowdownLogicViewProps {
  gameState: GameState;
  onFinalize: (playerHands: { playerIndex: number; cards: Card[] }[], blufferNames: string[]) => void;
}

const InlineCardPicker = ({ player, initialCards, takenCards, onConfirm, onCancel }: { player: Player, initialCards: Card[], takenCards: Card[], onConfirm: (cards: Card[]) => void, onCancel: () => void }) => {
  const [tempCards, setTempCards] = useState<Card[]>(initialCards);

  return (
    <div className="w-full animate-fade-in flex flex-col items-center">
      <h3 className="text-2xl font-display font-black text-gold mb-6 uppercase tracking-widest text-center border-b border-gold/20 pb-4">
        Record Cards: <span className="text-white">{player.name}</span>
      </h3>
      <CardInputView 
        pickingFor="hole" 
        selectedCards={tempCards} 
        onCardSelect={(c) => {
          const isSelected = tempCards.some(tc => tc.rank === c.rank && tc.suit === c.suit);
          if (isSelected) setTempCards(tempCards.filter(tc => !(tc.rank === c.rank && tc.suit === c.suit)));
          else if (tempCards.length < 2) setTempCards([...tempCards, c]);
        }} 
        onConfirm={() => onConfirm(tempCards)} 
        onReset={onCancel} 
        takenCards={takenCards}
      />
    </div>
  );
};

export const ShowdownLogicView: React.FC<ShowdownLogicViewProps> = ({ gameState, onFinalize }) => {
  const [playerReveals, setPlayerReveals] = useState<Record<number, { status: 'show' | 'muck' | 'pending'; cards: Card[]; isBluff: boolean }>>(() => {
    const initial: Record<number, { status: 'show' | 'muck' | 'pending'; cards: Card[]; isBluff: boolean }> = {};
    gameState.players.forEach((p, i) => {
      if (!p.is_folded) {
        initial[i] = { 
          status: p.hole_cards && p.hole_cards.length === 2 ? 'show' : 'pending', 
          cards: p.hole_cards || [],
          isBluff: false
        };
      }
    });
    return initial;
  });

  const [pickingCardsFor, setPickingCardsFor] = useState<number | null>(null);
  
  const activePlayerIndices = Object.keys(playerReveals).map(Number);
  
  const canFinalize = activePlayerIndices.every(idx => playerReveals[idx].status !== 'pending');

  const handleSetStatus = (idx: number, status: 'show' | 'muck') => {
    if (status === 'show') {
      if (playerReveals[idx].cards.length === 2) {
        setPlayerReveals(prev => ({ ...prev, [idx]: { ...prev[idx], status: 'show' } }));
      } else {
        setPickingCardsFor(idx);
      }
    } else {
      setPlayerReveals(prev => ({ ...prev, [idx]: { ...prev[idx], status: 'muck', cards: [] } }));
      setPickingCardsFor(null);
    }
  };

  const toggleBluff = (idx: number) => {
    setPlayerReveals(prev => ({ ...prev, [idx]: { ...prev[idx], isBluff: !prev[idx].isBluff } }));
  };

  const handleCardsPicked = (cards: Card[]) => {
    if (pickingCardsFor !== null) {
      setPlayerReveals(prev => ({ ...prev, [pickingCardsFor]: { ...prev[pickingCardsFor], status: 'show', cards } }));
      setPickingCardsFor(null);
    }
  };

  const handleFinalizeClick = () => {
    const playerHands = activePlayerIndices
      .filter(idx => playerReveals[idx].status === 'show')
      .map(idx => ({ playerIndex: idx, cards: playerReveals[idx].cards }));
    
    const blufferNames = activePlayerIndices
      .filter(idx => playerReveals[idx].isBluff)
      .map(idx => gameState.players[idx].name);

    onFinalize(playerHands, blufferNames);
  };

  if (pickingCardsFor !== null) {
    const player = gameState.players[pickingCardsFor];
    const initialCards = playerReveals[pickingCardsFor].cards;
    const takenCards = [
      ...gameState.community_cards,
      ...Object.entries(playerReveals)
        .filter(([id]) => Number(id) !== pickingCardsFor)
        .flatMap(([_, r]) => r.cards)
    ];
    return (
      <InlineCardPicker 
        player={player} 
        initialCards={initialCards}
        takenCards={takenCards} 
        onConfirm={handleCardsPicked} 
        onCancel={() => setPickingCardsFor(null)} 
      />
    );
  }

  return (
    <div className="max-w-4xl w-full bg-charcoal-dark border border-gold/30 rounded-3xl p-8 animate-scale-in shadow-[0_0_60px_rgba(212,175,55,0.15)] relative overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none opacity-50"></div>

      <div className="text-center space-y-4 mb-10 relative z-10 border-b border-gold/10 pb-8">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-gold-dark to-charcoal-dark border-2 border-gold rounded-full mb-2 shadow-[0_0_20px_rgba(212,175,55,0.4)]">
          <Trophy size={40} className="text-gold-light" />
        </div>
        <h2 className="text-5xl font-display font-black text-white uppercase tracking-[0.1em] drop-shadow-md">Showdown Resolution</h2>
        <p className="text-gold font-mono uppercase tracking-[0.3em] text-xs">Total Pot: <span className="font-bold text-white">${gameState.pot}</span></p>
      </div>

      <div className="relative z-10 space-y-8 animate-slide-up">
        <div className="flex justify-between items-end mb-4 border-b border-white/5 pb-2">
          <h3 className="text-xl font-display font-bold text-white uppercase tracking-widest">Declare Hands</h3>
          <span className="text-[10px] font-mono text-gold/60 uppercase tracking-widest">Show or Muck</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {activePlayerIndices.map((idx) => {
            const p = gameState.players[idx];
            const revealStatus = playerReveals[idx].status;
            
            return (
              <div key={idx} className={`p-5 rounded-2xl border transition-all duration-300 ${
                revealStatus === 'show' ? 'bg-gold/10 border-gold shadow-[0_0_15px_rgba(212,175,55,0.2)]' :
                revealStatus === 'muck' ? 'bg-black/50 border-white/5 opacity-60 grayscale' :
                'bg-charcoal border-gold/20 hover:border-gold/50'
              }`}>
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      idx === 0 ? 'bg-gold text-black' : 'bg-charcoal-light text-white'
                    }`}>
                      {idx === 0 ? 'U' : idx + 1}
                    </div>
                    <div>
                      <h4 className="font-display font-bold text-lg text-white uppercase">{p.name}</h4>
                      <p className="text-[10px] font-mono text-gold/60 uppercase">Stack: ${p.stack}</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => toggleBluff(idx)}
                    className={`px-3 py-1.5 rounded-lg border text-[10px] font-black uppercase tracking-widest transition-all ${
                      playerReveals[idx].isBluff 
                      ? 'bg-amber-warm text-charcoal-dark border-amber-warm shadow-gold' 
                      : 'bg-white/5 text-white/40 border-white/10 hover:border-gold/30'
                    }`}
                  >
                    {playerReveals[idx].isBluff ? 'Flagged Bluff' : 'Mark Bluff?'}
                  </button>
                </div>

                {revealStatus === 'pending' && (
                  <div className="flex gap-2">
                    <button onClick={() => handleSetStatus(idx, 'show')} className="flex-1 py-3 bg-charcoal-light hover:bg-gold hover:text-black border border-gold/20 rounded-xl font-mono text-sm font-bold flex items-center justify-center gap-2 transition-all">
                      <Eye size={16} /> SHOW
                    </button>
                    <button onClick={() => handleSetStatus(idx, 'muck')} className="flex-1 py-3 bg-charcoal-light hover:bg-red-500/20 hover:text-red-400 border border-white/10 rounded-xl font-mono text-sm font-bold flex items-center justify-center gap-2 transition-all text-white/50">
                      <EyeOff size={16} /> MUCK
                    </button>
                  </div>
                )}

                {revealStatus === 'show' && (
                  <div className="flex justify-between items-center bg-black/40 p-3 rounded-xl border border-gold/20">
                    <div className="flex gap-2">
                      {playerReveals[idx].cards.map((c, i) => (
                        <CardComponent key={i} card={c} size="sm" />
                      ))}
                    </div>
                    <button onClick={() => setPickingCardsFor(idx)} className="text-[10px] font-mono text-gold/60 hover:text-gold uppercase tracking-widest underline decoration-gold/30 underline-offset-4">
                      Edit
                    </button>
                  </div>
                )}

                {revealStatus === 'muck' && (
                  <div className="py-3 text-center bg-black/60 rounded-xl border border-white/5 text-white/30 font-mono text-xs uppercase tracking-[0.2em]">
                    Hand Mucked
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex justify-end mt-8">
          <button 
            onClick={handleFinalizeClick}
            disabled={!canFinalize}
            className="px-8 py-4 bg-gradient-to-r from-gold-dark via-gold to-gold-light text-black rounded-xl font-display font-black text-lg uppercase flex items-center gap-3 transition-all disabled:opacity-30 disabled:grayscale hover:shadow-[0_0_20px_rgba(212,175,55,0.4)] active:scale-95"
          >
            Evaluate Hands & Distribute Pots <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};