import React from 'react';
import { Users, Crosshair, Eye, TrendingUp, Info } from 'lucide-react';
import { Tooltip } from './Tooltip';

interface PlayerStatsProps {
  stats: Record<string, any>;
  currentPlayer?: string;
}

export function PlayerStats({ stats, currentPlayer }: PlayerStatsProps) {
  const displayStats = Object.keys(stats).length > 0 ? stats : {};

  return (
    <div className="glass-dark border border-white/10 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-5 border-b border-white/5 pb-3">
        <div className="flex items-center gap-3">
          <Users className="text-gold/70" size={18} />
          <h3 className="text-sm font-black tracking-widest uppercase text-cream/90">Player Models</h3>
        </div>
        <Tooltip content="VPIP: Hands played voluntarily. PFR: Hands raised preflop. AGG: Frequency of aggressive actions.">
          <Info size={14} className="text-gold/30 hover:text-gold transition-colors cursor-help" />
        </Tooltip>
      </div>

      <div className="space-y-4">
        {Object.entries(displayStats).length === 0 ? (
          <div className="text-center py-4">
            <p className="text-[10px] text-cream/20 font-black uppercase tracking-widest italic">Awaiting showdown to build profiles...</p>
          </div>
        ) : (
          Object.entries(displayStats).map(([name, data]) => {
            if (name === "You") return null; 
            const isActive = name === currentPlayer;
            
            return (
              <div key={name} className={`bg-black/40 border ${isActive ? 'border-gold/50' : 'border-white/5'} rounded-xl p-4 transition-all hover:border-gold/20 group`}>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-sm font-bold text-cream">{name}</span>
                  {data.classification && (
                    <Tooltip content={data.description || "Player style classification"}>
                      <span className="text-[9px] font-black tracking-widest uppercase px-2 py-1 bg-gold/10 rounded text-gold cursor-help group-hover:bg-gold/20 transition-all">
                        {data.classification}
                      </span>
                    </Tooltip>
                  )}
                </div>
                
                <div className="grid grid-cols-3 gap-2">
                  <div className="flex flex-col">
                    <span className="text-[8px] text-white/40 font-bold uppercase tracking-wider mb-1 flex items-center gap-1">VPIP</span>
                    <span className="text-xs font-black text-cream/90">{(data.vpip * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[8px] text-white/40 font-bold uppercase tracking-wider mb-1 flex items-center gap-1">PFR</span>
                    <span className="text-xs font-black text-cream/90">{(data.pfr * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[8px] text-white/40 font-bold uppercase tracking-wider mb-1 flex items-center gap-1">AGG</span>
                    <span className="text-xs font-black text-amber-500/90">{data.agg_freq ? `${(data.agg_freq * 100).toFixed(0)}%` : 'N/A'}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
