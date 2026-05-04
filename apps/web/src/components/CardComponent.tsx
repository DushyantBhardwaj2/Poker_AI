import React from 'react';
import type { Card, Suit } from '../lib/api';

const suitColor: Record<Suit, string> = {
  's': 'text-charcoal-dark',
  'c': 'text-charcoal-dark',
  'h': 'text-red-700',
  'd': 'text-blue-800'
};

const suitSymbol: Record<Suit, string> = {
  's': '♠',
  'c': '♣',
  'h': '♥',
  'd': '♦'
};

const rankDisplay: Record<string, string> = {
  'T': '10', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
};

interface CardProps {
  card: Card;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  className?: string;
}

export const CardComponent: React.FC<CardProps> = ({ card, size = 'md', className = '' }) => {
  const displayRank = rankDisplay[card.rank] || card.rank;
  
  const sizeClasses = {
    xs: 'w-8 h-12 text-xs',
    sm: 'w-10 h-14 text-sm',
    md: 'w-16 h-24 text-xl',
    lg: 'w-20 h-32 text-2xl'
  };

  const cornerSize = size === 'xs' ? 'text-[8px]' : size === 'sm' ? 'text-[10px]' : 'text-xs';

  return (
    <div className={`
      relative bg-cream rounded-lg shadow-xl border-2 border-gold/40
      flex flex-col items-center justify-center font-bold tracking-tighter
      card-hover select-none overflow-hidden
      ${sizeClasses[size]}
      ${suitColor[card.suit]}
      ${className}
    `}>
      {/* Corner Rank/Suit - Top Left */}
      <div className={`absolute top-1 left-1.5 flex flex-col items-center leading-none ${cornerSize}`}>
        <span>{displayRank}</span>
        <span>{suitSymbol[card.suit]}</span>
      </div>

      {/* Center Rank/Suit */}
      <div className="flex flex-col items-center leading-tight">
        <span className={size === 'sm' ? 'text-lg' : 'text-3xl'}>{displayRank}</span>
        <span className={size === 'sm' ? 'text-xl' : 'text-4xl'}>{suitSymbol[card.suit]}</span>
      </div>

      {/* Corner Rank/Suit - Bottom Right (Rotated) */}
      <div className={`absolute bottom-1 right-1.5 flex flex-col items-center leading-none rotate-180 ${cornerSize}`}>
        <span>{displayRank}</span>
        <span>{suitSymbol[card.suit]}</span>
      </div>

      {/* Decorative inner border */}
      <div className="absolute inset-1 border border-gold/10 rounded-[4px] pointer-events-none"></div>
    </div>
  );
};
