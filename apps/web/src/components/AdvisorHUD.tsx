import React from 'react';
import { 
  BrainCircuit, 
  Target, 
  TrendingUp, 
  ShieldAlert, 
  Info, 
  ChevronRight,
  User,
  Zap,
  BookOpen
} from 'lucide-react';
import { Tooltip } from './Tooltip';
import type { FullAnalysisResponse } from '../types/poker';

interface AdvisorHUDProps {
  analysis: FullAnalysisResponse | null;
  loading: boolean;
  onRefresh: () => void;
}

export function AdvisorHUD({ analysis, loading, onRefresh }: AdvisorHUDProps) {
  if (!analysis && !loading) {
    return (
      <div className="glass-dark border border-gold/10 rounded-2xl p-10 flex flex-col items-center justify-center text-center gap-4">
        <BrainCircuit size={48} className="text-gold/20" />
        <div>
          <h3 className="text-gold font-black uppercase tracking-widest">Intelligence Offline</h3>
          <p className="text-cream/40 text-[10px] uppercase font-bold tracking-wider mt-1">Initialize analysis to receive strategic advice</p>
        </div>
        <button 
          onClick={onRefresh}
          className="mt-4 px-6 py-2 bg-gold/10 hover:bg-gold/20 text-gold border border-gold/20 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all"
        >
          Begin Analysis
        </button>
      </div>
    );
  }

  const { win_analysis, bluff_analysis, advice, opponent_profile } = analysis || {};

  return (
    <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* 1. TOP BAR: ACTION BANNER */}
      <div className={`
        relative overflow-hidden rounded-2xl p-6 border transition-all duration-500
        ${loading ? 'bg-gold/5 border-gold/10 animate-pulse' : 'bg-gradient-to-r from-gold/20 via-gold/5 to-transparent border-gold/30 shadow-2xl shadow-gold/5'}
      `}>
        <div className="flex justify-between items-start relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 rounded-full bg-gold animate-pulse shadow-[0_0_8px_rgba(212,175,55,0.8)]" />
              <h2 className="text-[10px] font-black tracking-[0.3em] uppercase text-gold/60">Strategic Directive</h2>
            </div>
            <h1 className="text-5xl font-black text-cream italic uppercase tracking-tighter drop-shadow-sm">
              {loading ? 'CALCULATING...' : advice?.action}
            </h1>
          </div>
          <button 
            onClick={onRefresh}
            disabled={loading}
            className="p-2 rounded-full bg-black/40 border border-white/10 text-gold hover:bg-gold hover:text-black transition-all active:scale-90 disabled:opacity-50"
          >
            <Zap size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
        
        {!loading && (
          <div className="mt-4 flex items-center gap-4 border-t border-gold/10 pt-4">
            <div className="flex flex-col">
              <span className="text-[8px] font-black uppercase text-gold/40 tracking-widest">EV Projection</span>
              <span className={`text-sm font-black ${advice?.ev! >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {advice?.ev! > 0 ? '+' : ''}{advice?.ev?.toFixed(2)}
              </span>
            </div>
            <div className="w-px h-8 bg-gold/10" />
            <div className="flex flex-col">
              <span className="text-[8px] font-black uppercase text-gold/40 tracking-widest">Pot Odds</span>
              <span className="text-sm font-black text-cream/80">{(advice?.pot_odds! * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}

        {/* Decorative Background Elements */}
        <div className="absolute -right-4 -bottom-8 opacity-5 pointer-events-none rotate-12">
          <Target size={180} className="text-gold" />
        </div>
      </div>

      {/* 2. CORE METRICS GRID */}
      <div className="grid grid-cols-2 gap-4">
        {/* Win Probability Gauge */}
        <div className="glass-dark border border-white/10 rounded-2xl p-4 flex flex-col items-center justify-center relative group overflow-hidden">
          <div className="absolute inset-0 bg-gold/0 group-hover:bg-gold/[0.02] transition-colors" />
          <span className="text-[9px] font-black uppercase text-gold/40 tracking-widest mb-2 flex items-center gap-1">
            Hand Equity <Info size={8} />
          </span>
          <div className="relative w-24 h-24 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90">
              <circle
                cx="48" cy="48" r="40"
                fill="none" stroke="currentColor"
                strokeWidth="4" className="text-white/5"
              />
              <circle
                cx="48" cy="48" r="40"
                fill="none" stroke="currentColor"
                strokeWidth="4"
                strokeDasharray={251}
                strokeDashoffset={251 - (251 * (win_analysis?.win_probability || 0))}
                className="text-gold transition-all duration-1000 ease-out"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-xl font-black text-cream">
                {loading ? '--' : `${((win_analysis?.win_probability || 0) * 100).toFixed(0)}%`}
              </span>
            </div>
          </div>
        </div>

        {/* Bluff Probability Gauge */}
        <div className="glass-dark border border-white/10 rounded-2xl p-4 flex flex-col items-center justify-center relative group overflow-hidden">
          <div className="absolute inset-0 bg-amber-500/0 group-hover:bg-amber-500/[0.02] transition-colors" />
          <span className="text-[9px] font-black uppercase text-amber-500/40 tracking-widest mb-2 flex items-center gap-1">
            Bluff Threat <Info size={8} />
          </span>
          <div className="relative w-24 h-24 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90">
              <circle
                cx="48" cy="48" r="40"
                fill="none" stroke="currentColor"
                strokeWidth="4" className="text-white/5"
              />
              <circle
                cx="48" cy="48" r="40"
                fill="none" stroke="currentColor"
                strokeWidth="4"
                strokeDasharray={251}
                strokeDashoffset={251 - (251 * (bluff_analysis?.bluff_probability || 0))}
                className="text-amber-500 transition-all duration-1000 ease-out"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-xl font-black text-cream">
                {loading ? '--' : `${((bluff_analysis?.bluff_probability || 0) * 100).toFixed(0)}%`}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. BEHAVIORAL INTEL */}
      <div className="glass-dark border border-white/10 rounded-2xl p-5">
        <div className="flex items-center gap-3 mb-4 opacity-60">
          <User size={14} className="text-gold" />
          <h3 className="text-[10px] font-black tracking-widest uppercase text-cream/90">Opponent Profile</h3>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gold/5 border border-gold/20 flex items-center justify-center">
            <span className="text-gold font-black text-xs uppercase tracking-tighter">
              {opponent_profile?.classification.split('-').map(s => s[0]).join('')}
            </span>
          </div>
          <div className="flex-1">
            <h4 className="text-xs font-black text-cream uppercase tracking-wider mb-1">
              {opponent_profile?.classification}
            </h4>
            <p className="text-[10px] text-cream/40 font-bold leading-tight">
              {opponent_profile?.description}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-white/5">
          <div className="flex justify-between items-center">
            <span className="text-[9px] font-black uppercase text-cream/30">VPIP</span>
            <span className="text-[11px] font-black text-gold">{(opponent_profile?.vpip! * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[9px] font-black uppercase text-cream/30">PFR</span>
            <span className="text-[11px] font-black text-gold">{(opponent_profile?.pfr! * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* 4. REASONING & THEORY */}
      <div className="glass-dark border border-gold/20 rounded-2xl p-6 relative overflow-hidden">
        {/* Subtle Decorative Grid */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#d4af37_1px,transparent_1px)] [background-size:16px_16px]" />
        
        <div className="relative z-10 space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen size={16} className="text-gold" />
            <h3 className="text-[10px] font-black tracking-widest uppercase text-gold">Strategic Rationale</h3>
          </div>

          <p className="text-[11px] text-cream/80 leading-relaxed font-bold uppercase tracking-tight italic">
            "{advice?.explanation}"
          </p>

          {advice?.theory_tip && (
            <div className="bg-gold/5 border-l-2 border-gold p-3 rounded-r-lg mt-4 animate-in fade-in slide-in-from-left-2 duration-1000">
              <div className="flex items-center gap-2 mb-1">
                <Zap size={10} className="text-gold fill-gold" />
                <span className="text-[8px] font-black uppercase text-gold/60 tracking-widest">Theoretical Insight</span>
              </div>
              <p className="text-[10px] text-gold font-bold leading-tight">
                {advice.theory_tip}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
