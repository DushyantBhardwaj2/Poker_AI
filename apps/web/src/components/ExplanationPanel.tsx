import React from 'react';
import { BookOpen, BrainCircuit, Activity, Info } from 'lucide-react';
import { Tooltip } from './Tooltip';

interface ExplanationPanelProps {
  explanation: string | null;
  theoryReasons?: string[];
  drawChances?: { flush?: number; straight?: number };
}

export function ExplanationPanel({ explanation, theoryReasons, drawChances }: ExplanationPanelProps) {
  if (!explanation && !drawChances && (!theoryReasons || theoryReasons.length === 0)) return null;

  return (
    <div className="glass-dark border border-white/10 rounded-2xl p-6 relative">
      <div className="flex items-center gap-3 mb-4 border-b border-white/5 pb-3">
        <BrainCircuit className="text-gold/70" size={18} />
        <h3 className="text-sm font-black tracking-widest uppercase text-cream/90">Reasoning & Logic</h3>
      </div>

      <div className="space-y-5">
        {theoryReasons && theoryReasons.length > 0 && (
          <div className="space-y-2">
            {theoryReasons.map((reason, i) => (
              <div key={i} className="flex gap-3 items-start group">
                <div className="w-1 h-1 bg-gold rounded-full mt-1.5 shrink-0 group-hover:scale-150 transition-transform" />
                <p className="text-[10px] font-bold text-cream/80 leading-relaxed uppercase tracking-wider">{reason}</p>
              </div>
            ))}
          </div>
        )}

        {explanation && (
          <div className="bg-black/30 rounded-xl p-4 border border-white/5 italic">
            <p className="text-[11px] text-cream/50 leading-relaxed font-medium">
              "{explanation}"
            </p>
          </div>
        )}

        {drawChances && (Object.keys(drawChances).length > 0) && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <h4 className="text-[9px] font-black tracking-[0.2em] uppercase text-gold/40 flex items-center gap-2">
                <Activity size={10} />
                Draw Analysis
              </h4>
              <Tooltip content="Outs calculation: Probability of improving your hand on the next street.">
                <Info size={10} className="text-gold/20 hover:text-gold transition-colors cursor-help" />
              </Tooltip>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              {drawChances.flush !== undefined && (
                <div className="bg-black/40 border border-gold/10 rounded-xl p-3 flex justify-between items-center hover:border-gold/30 transition-colors">
                  <span className="text-[9px] font-black uppercase text-cream/40">Flush</span>
                  <span className="text-xs font-black text-gold">{(drawChances.flush * 100).toFixed(1)}%</span>
                </div>
              )}
              {drawChances.straight !== undefined && (
                <div className="bg-black/40 border border-gold/10 rounded-xl p-3 flex justify-between items-center hover:border-gold/30 transition-colors">
                  <span className="text-[9px] font-black uppercase text-cream/40">Straight</span>
                  <span className="text-xs font-black text-gold">{(drawChances.straight * 100).toFixed(1)}%</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
