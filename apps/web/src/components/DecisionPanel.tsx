import React from 'react';
import { Target, TrendingUp, AlertTriangle, Info, Zap } from 'lucide-react';
import { Tooltip } from './Tooltip';

interface DecisionPanelProps {
  winProb: number | null;
  bluffProb: number | null;
  recommendation: { action: string; ev: number; pot_odds: number; explanation: string } | null;
  loading: boolean;
  onRunAnalysis: () => void;
  theoryMode?: boolean;
}

export function DecisionPanel({ winProb, bluffProb, recommendation, loading, onRunAnalysis, theoryMode }: DecisionPanelProps) {
  return (
    <div className="glass-dark border border-gold/10 rounded-2xl p-6 flex flex-col gap-6 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
        <Target size={120} />
      </div>
      
      <div className="flex justify-between items-center border-b border-gold/5 pb-4 relative z-10">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-black tracking-widest uppercase text-gold">Decision Engine</h2>
            {theoryMode && (
              <Tooltip content="Theory-Assisted Mode Active: Analysis includes Sklansky's Strategic Pillars.">
                <Zap size={12} className="text-gold animate-pulse-gold fill-gold" />
              </Tooltip>
            )}
          </div>
          <p className="text-[10px] text-gold/40 tracking-[0.2em] mt-1 uppercase font-bold">Real-Time Intelligence</p>
        </div>
        <button 
          onClick={onRunAnalysis}
          disabled={loading}
          className={`
            px-4 sm:px-5 py-2.5 sm:py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all relative overflow-hidden active:scale-95
            ${loading 
              ? 'bg-gold/5 text-gold/40 cursor-wait' 
              : 'bg-gold/10 hover:bg-gold/20 text-gold border border-gold/20 shadow-sm hover:shadow-gold/10'
            }
          `}
        >
          {loading ? 'Analyzing...' : 'Refresh AI'}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 relative z-10">
        <Tooltip content="The mathematical probability that your hand will win at showdown against random opponent ranges.">
          <div className="bg-black/40 border border-gold/5 rounded-xl p-4 flex flex-col items-center justify-center cursor-help hover:border-gold/20 transition-colors">
            <span className="text-[9px] text-gold/50 tracking-widest uppercase mb-2 font-black flex items-center gap-1">
              Win Chance <Info size={8} />
            </span>
            <span className="text-3xl font-black text-cream">
              {winProb !== null ? `${(winProb * 100).toFixed(1)}%` : '--%'}
            </span>
          </div>
        </Tooltip>
        
        <Tooltip content="The likelihood that the current bet against you is a bluff, based on bet sizing and board texture.">
          <div className="bg-black/40 border border-gold/5 rounded-xl p-4 flex flex-col items-center justify-center cursor-help hover:border-gold/20 transition-colors">
            <span className="text-[9px] text-gold/50 tracking-widest uppercase mb-2 font-black flex items-center gap-1">
              Bluff Prob <Info size={8} />
            </span>
            <span className="text-3xl font-black text-amber-500">
              {bluffProb !== null ? `${(bluffProb * 100).toFixed(1)}%` : '--%'}
            </span>
          </div>
        </Tooltip>
      </div>

      {recommendation && (
        <div className="bg-gradient-to-br from-gold/10 to-transparent border border-gold/20 rounded-xl p-5 mt-2 relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <TrendingUp className="text-gold" size={16} />
            <h3 className="text-[10px] font-black tracking-widest uppercase text-gold">Optimal Strategy</h3>
          </div>
          <div className="text-4xl font-black text-cream mb-2 uppercase tracking-wider italic">
            {recommendation.action}
          </div>
          
          <div className="flex flex-wrap gap-3 mt-4">
            <Tooltip content="Expected Value: The average amount you stand to win (positive) or lose (negative) per hand with this move.">
              <span className="bg-black/50 px-3 py-1.5 rounded-lg border border-white/5 text-[9px] font-bold text-cream/70 flex items-center gap-2 cursor-help uppercase tracking-widest">
                EV: <span className={recommendation.ev >= 0 ? "text-green-400" : "text-red-400"}>
                  {recommendation.ev > 0 ? '+' : ''}{recommendation.ev.toFixed(2)}
                </span>
              </span>
            </Tooltip>
            
            <Tooltip content="The percentage of the total pot you need to win for a call to be mathematically break-even.">
              <span className="bg-black/50 px-3 py-1.5 rounded-lg border border-white/5 text-[9px] font-bold text-cream/70 flex items-center gap-2 cursor-help uppercase tracking-widest">
                Odds: {(recommendation.pot_odds * 100).toFixed(1)}%
              </span>
            </Tooltip>
          </div>
        </div>
      )}
    </div>
  );
}
