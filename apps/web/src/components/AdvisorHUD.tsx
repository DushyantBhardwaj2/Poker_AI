import React, { useState } from 'react';
import {
  BrainCircuit,
  Target,
  ShieldAlert,
  ShieldCheck,
  Zap,
  BookOpen,
  Eye,
  BarChart,
  AlertTriangle,
  Info,
  CreditCard,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Tooltip } from './Tooltip';
import type { FullAnalysisResponse } from '../lib/api';

interface AdvisorHUDProps {
    analysis: FullAnalysisResponse | null;
    loading: boolean;
    onRefresh: () => void;
    hasCards?: boolean;
}

type ViewMode = 'strategic' | 'tactical';

const CONFIDENCE_STYLES: Record<string, { border: string; shadow: string; text: string; glow: string; bg: string; dashed: boolean }> = {
    High: { border: 'border-green-500/20', shadow: 'shadow-green-500/5', text: 'text-green-400', glow: 'bg-green-500', bg: 'bg-green-500/5', dashed: false },
    Medium: { border: 'border-gold/20', shadow: 'shadow-gold-subtle', text: 'text-gold', glow: 'bg-gold', bg: 'bg-gold/5', dashed: false },
    Low: { border: 'border-orange-500/30', shadow: 'shadow-orange-500/10', text: 'text-orange-400', glow: 'bg-orange-500', bg: 'bg-orange-500/10', dashed: true },
    Speculative: { border: 'border-red-500/30', shadow: 'shadow-red-500/10', text: 'text-red-400', glow: 'bg-red-500', bg: 'bg-red-500/10', dashed: true },
};

export function AdvisorHUD({ analysis, loading, onRefresh, hasCards = true }: AdvisorHUDProps) {
    const [mode, setMode] = useState<ViewMode>('strategic');
    const [showDecayDetails, setShowDecayDetails] = useState(false);

    // Mode transition animation variants
    const modeTransition = {
        initial: { opacity: 0, x: mode === 'strategic' ? -20 : 20 },
        animate: { opacity: 1, x: 0 },
        exit: { opacity: 0, x: mode === 'strategic' ? 20 : -20 },
        transition: { duration: 0.25, ease: "easeInOut" }
    };

    // Low confidence pulse animation
    const lowConfidencePulse = {
        boxShadow: [
            '0 0 0 0 rgba(249, 115, 22, 0)',
            '0 0 20px 5px rgba(249, 115, 22, 0.3)',
            '0 0 0 0 rgba(249, 115, 22, 0)'
        ],
        transition: {
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
        }
    };

    if (!hasCards) {
        return <CardsRequired />;
    }

    if (!analysis && !loading) {
        return <IntelligenceOffline onBeginAnalysis={onRefresh} />;
    }

    const advice = analysis?.advice;
    const confidence = advice?.confidence_level || 'Medium';

    // Confidence-based styling
    const confidenceStyles = CONFIDENCE_STYLES[confidence] || CONFIDENCE_STYLES.Medium;

    // Check for low confidence states
    const isLowConfidence = confidence === 'Low' || confidence === 'Speculative';

    return (
        <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <motion.div
            className={`glass-dark border ${confidenceStyles.border} ${confidenceStyles.dashed ? 'border-dashed' : ''} rounded-xl p-4 md:p-5 transition-all duration-700 ${confidenceStyles.shadow}`}
            animate={isLowConfidence ? lowConfidencePulse : {}}
          >
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-2">
                <BrainCircuit size={18} className={confidenceStyles.text} />
                <h2 className={`text-base font-black tracking-wide uppercase ${confidenceStyles.text}`}>
                  AI Advisor
                </h2>
                {confidence === 'Speculative' && (
                    <Tooltip content="Recommendation based on very limited data.">
                        <AlertTriangle size={14} className="text-red-500 animate-pulse" />
                    </Tooltip>
                )}
                {isLowConfidence && (
                    <motion.button
                        onClick={() => setShowDecayDetails(!showDecayDetails)}
                        className="flex items-center gap-1 px-2 py-1 bg-black/20 border border-white/5 rounded-md hover:bg-white/5 transition-colors cursor-pointer"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <span className={`text-[10px] font-medium ${confidenceStyles.text}`}>Details</span>
                        {showDecayDetails ? <ChevronUp size={12} className={confidenceStyles.text} /> : <ChevronDown size={12} className={confidenceStyles.text} />}
                    </motion.button>
                )}
              </div>
              <ModeToggle mode={mode} onModeChange={setMode} confidenceStyles={confidenceStyles} />
            </div>

            {/* Decay Details - collapsible */}
            <AnimatePresence>
                {showDecayDetails && advice?.data_quality?.degradation_reasons && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                    >
                        <div className={`${confidenceStyles.bg} border border-dashed ${confidenceStyles.border} rounded-lg p-3 mb-4`}>
                            <h4 className={`text-[10px] font-bold uppercase tracking-wide mb-2 ${confidenceStyles.text}`}>Confidence Decay Reasons</h4>
                            <ul className="space-y-1">
                                {advice.data_quality.degradation_reasons.map((reason, i) => (
                                    <li key={i} className="text-[9px] text-cream/60 flex items-start gap-2">
                                        <span className={`mt-1 w-1 h-1 rounded-full shrink-0 ${confidenceStyles.glow}`} />
                                        {reason}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence mode="wait">
              {mode === 'strategic' ? (
                <motion.div key="strategic" {...modeTransition}>
                  <StrategicView analysis={analysis} loading={loading} styles={confidenceStyles} />
                </motion.div>
              ) : (
                <motion.div key="tactical" {...modeTransition}>
                  <TacticalView analysis={analysis} loading={loading} onRefresh={onRefresh} styles={confidenceStyles} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          <ExplanationSection analysis={analysis} />
          <DataQualitySection
            analysis={analysis}
            confidenceStyles={confidenceStyles}
            onToggleDetails={() => setShowDecayDetails(!showDecayDetails)}
            showDetails={showDecayDetails}
          />
        </div>
    );
}

// --- Mode Toggle ---
const ModeToggle: React.FC<{ mode: ViewMode, onModeChange: (m: ViewMode) => void, confidenceStyles: any }> = ({ mode, onModeChange, confidenceStyles }) => (
    <motion.div
        className="flex items-center gap-1 p-0.5 rounded-full bg-black/20 border border-white/[0.05]"
        layout
    >
      <motion.button
        onClick={() => onModeChange('strategic')}
        className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${mode === 'strategic' ? 'bg-gold/90 text-charcoal-dark shadow-gold-subtle' : 'text-cream/40 hover:text-cream/70 hover:bg-white/[0.03]'}`}
        whileTap={{ scale: 0.95 }}
        layout
      >
        <div className="flex items-center gap-2"><Eye size={12} /><span>Strategic</span></div>
      </motion.button>
      <motion.button
        onClick={() => onModeChange('tactical')}
        className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${mode === 'tactical' ? 'bg-gold/90 text-charcoal-dark shadow-gold-subtle' : 'text-cream/40 hover:text-cream/70 hover:bg-white/[0.03]'}`}
        whileTap={{ scale: 0.95 }}
        layout
      >
        <div className="flex items-center gap-2"><BarChart size={12} /><span>Tactical</span></div>
      </motion.button>
    </motion.div>
);

// --- Strategic View ---
const StrategicView: React.FC<{ analysis: FullAnalysisResponse | null, loading: boolean, styles: any }> = ({ analysis, loading, styles }) => {
    if (!analysis || loading) return <AnalysisSkeleton />;
    const { advice } = analysis;
    const isLowReliability = advice.data_quality && advice.data_quality.confidence_score < 0.4;

    return (
      <motion.div
        className="flex flex-col gap-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className={`relative bg-gradient-to-br from-gold/5 via-transparent to-transparent border border-white/5 rounded-xl p-4 text-center transition-all`}>
            {isLowReliability && (
                <div className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-1 bg-orange-500/10 border border-orange-500/20 rounded-full">
                    <AlertTriangle size={12} className="text-orange-400" />
                    <span className="text-[9px] font-black text-orange-400 uppercase tracking-tighter">Low Read</span>
                </div>
            )}
            <h3 className="text-gold/50 text-[10px] font-bold tracking-wider uppercase">Strategic Directive</h3>
            <h1 className="text-2xl md:text-3xl font-black text-cream/90 italic uppercase tracking-tight my-2">
                {advice.strategic_directive}
            </h1>
            <p className="text-base text-cream/70 max-w-prose mx-auto font-medium leading-relaxed">
                "{advice.explanation_structured.main}"
            </p>
        </div>

        <div className="grid grid-cols-2 gap-2 text-center">
            <InfoBadge
              label="Opponent"
              value={analysis.opponent_profile?.hands_played >= 10
                ? (advice.opponent_archetype || 'Unknown')
                : 'Building Read'
              }
              color={analysis.opponent_profile?.hands_played >= 10 ? styles.text : 'text-orange-400'}
            />
            <InfoBadge label="Confidence" value={advice.confidence_level} color={styles.text} />
        </div>
        {analysis.opponent_profile && analysis.opponent_profile.hands_played < 10 && (
          <div className="text-center">
            <p className="text-[10px] text-orange-400/70 font-medium">
              Need {10 - analysis.opponent_profile.hands_played} more hands to see playstyle
            </p>
          </div>
        )}
      </motion.div>
    );
};

const InfoBadge: React.FC<{ label: string; value: string; color?: string }> = ({ label, value, color = "text-cream/90" }) => (
    <motion.div
        className="bg-black/10 border border-white/5 rounded-xl p-3 hover:bg-white/[0.03] transition-colors"
        whileHover={{ scale: 1.02 }}
    >
        <h4 className="text-[10px] text-gold/40 font-bold uppercase tracking-wider">{label}</h4>
        <p className={`text-base font-semibold truncate mt-0.5 ${color}`}>{value}</p>
    </motion.div>
)

// --- Tactical View ---
const TacticalView: React.FC<{ analysis: FullAnalysisResponse | null, loading: boolean, onRefresh: () => void, styles: any }> = ({ analysis, loading, onRefresh, styles }) => {
    if (!analysis || loading) return <AnalysisSkeleton />;
    const { advice } = analysis;

    return (
        <motion.div
            className="flex flex-col gap-3"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
        >
            <div className={`
                relative overflow-hidden rounded-xl p-4 md:p-5 border transition-all duration-300
                bg-gradient-to-r from-gold/10 via-gold/3 to-transparent border-gold/20 shadow-gold-subtle
            `}>
                <div className="flex justify-between items-start relative z-10">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <motion.span
                                className={`w-2.5 h-2.5 rounded-full ${styles.glow} shadow-lg`}
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                            />
                            <h2 className="text-[10px] font-black tracking-wider uppercase text-gold/60">Primary Action</h2>
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black text-cream italic uppercase tracking-tighter drop-shadow-sm">
                            {advice.action}
                        </h1>
                    </div>
                    <motion.button
                        onClick={onRefresh}
                        disabled={loading}
                        className="p-3 rounded-full bg-black/40 border border-white/10 text-gold hover:bg-gold hover:text-black transition-all disabled:opacity-50"
                        whileTap={{ scale: 0.9 }}
                        whileHover={{ scale: 1.05 }}
                    >
                        <Zap size={20} className={loading ? 'animate-spin' : ''} />
                    </motion.button>
                </div>

                <div className="mt-4 flex items-center gap-4 border-t border-gold/10 pt-3">
                    <div className="flex flex-col">
                        <span className="text-[9px] font-black uppercase text-gold/40 tracking-wide">EV</span>
                        <motion.span
                            className={`text-lg font-black ${advice.ev >= 0 ? 'text-green-400' : 'text-red-400'}`}
                            key={advice.ev}
                            initial={{ opacity: 0.5 }}
                            animate={{ opacity: 1 }}
                        >
                            {advice.ev > 0 ? '+' : ''}{advice.ev.toFixed(2)}
                        </motion.span>
                    </div>
                    <div className="w-px h-10 bg-gold/10" />
                    <div className="flex flex-col">
                        <span className="text-[9px] font-black uppercase text-gold/40 tracking-wide">Pot Odds Req.</span>
                        <span className="text-lg font-black text-cream/80">{(advice.pot_odds * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
                <Gauge label="Hand Equity" value={advice.tactical_data.win_probability} color="text-gold" />
                <Gauge label="Bluff Threat" value={advice.tactical_data.bluff_probability} color="text-amber-500" />
            </div>
        </motion.div>
    );
};

const Gauge: React.FC<{label: string, value: number, color: string}> = ({ label, value, color }) => (
    <motion.div
        className="glass-dark border border-white/5 rounded-xl p-4 flex flex-col items-center justify-center relative group overflow-hidden"
        whileHover={{ scale: 1.02 }}
    >
        <span className="text-[10px] font-bold uppercase text-gold/40 tracking-wider mb-2 flex items-center gap-1">{label}</span>
        <div className="relative w-24 h-24 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90">
                <circle cx="48" cy="48" r="44" fill="none" stroke="currentColor" strokeWidth="4" className="text-white/[0.03]" />
                <motion.circle
                    cx="48" cy="48" r="44"
                    fill="none" stroke="currentColor"
                    strokeWidth="4"
                    strokeDasharray={277}
                    initial={{ strokeDashoffset: 277 }}
                    animate={{ strokeDashoffset: 277 - (277 * (value || 0)) }}
                    transition={{ duration: 0.7, ease: "easeOut" }}
                    className={`${color}`}
                    strokeLinecap="round"
                />
            </svg>
            <div className="absolute flex flex-col items-center">
                <span className="text-2xl font-bold text-cream/90">{`${((value || 0) * 100).toFixed(0)}%`}</span>
            </div>
        </div>
    </motion.div>
);

// --- Explanation Section ---
const ExplanationSection: React.FC<{analysis: FullAnalysisResponse | null}> = ({ analysis }) => {
    if (!analysis) return null;
    const { key_factors, explanation_structured } = analysis.advice;

    return (
      <motion.div
        className="glass-dark border border-white/5 rounded-xl p-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BookOpen size={16} className="text-gold/60" />
            <h3 className="text-sm font-bold tracking-wide uppercase text-gold/70">Strategic Logic</h3>
          </div>
          {explanation_structured.bluff_context && (
             <Tooltip content={explanation_structured.bluff_context}>
               <div className="flex items-center gap-1.5 px-2 py-1 bg-gold/10 border border-gold/20 rounded-md">
                 <ShieldAlert size={12} className="text-gold" />
                 <span className="text-[10px] font-black text-gold uppercase tracking-tighter">Behavioral</span>
               </div>
             </Tooltip>
          )}
        </div>
        <div className="space-y-2">
          {key_factors.map((factor, i) => {
            const isShift = factor.headline.includes('Spike') || factor.headline.includes('Shift');
            return (
              <motion.div
                  key={i}
                  className={`flex gap-3 items-start p-3 bg-black/10 rounded-xl border ${isShift ? 'border-orange-500/30' : 'border-white/[0.02]'} hover:border-white/[0.05] transition-colors`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05 }}
                  whileHover={{ scale: 1.01 }}
              >
                <div className="mt-0.5 shrink-0">
                   {isShift ? (
                     <AlertTriangle size={18} className="text-orange-400" />
                   ) : (
                     <ShieldCheck size={18} className="text-gold/60" />
                   )}
                </div>
                <div>
                  <h4 className={`font-semibold ${isShift ? 'text-orange-400' : 'text-cream/90'} text-base leading-tight`}>{factor.headline}</h4>
                  <p className="text-sm text-cream/60 leading-relaxed mt-1">{factor.description}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    );
  };

// --- Data Quality Section ---
interface DataQualityProps {
    analysis: FullAnalysisResponse | null;
    confidenceStyles: any;
    onToggleDetails: () => void;
    showDetails: boolean;
}

const DataQualitySection: React.FC<DataQualityProps> = ({ analysis, confidenceStyles, onToggleDetails, showDetails }) => {
    const dq = analysis?.advice?.data_quality;
    if (!dq || (dq.confidence_score > 0.9 && dq.degradation_reasons.length === 0)) return null;

    const reliabilityLabel = dq.confidence_score > 0.8 ? 'High' : dq.confidence_score > 0.5 ? 'Moderate' : dq.confidence_score > 0.2 ? 'Low' : 'Speculative';
    const reliabilityColor = dq.confidence_score > 0.8 ? 'text-green-400' : dq.confidence_score > 0.5 ? 'text-gold' : dq.confidence_score > 0.2 ? 'text-orange-400' : 'text-red-400';

    // Use color shift based on confidence
    const progressColor = dq.confidence_score > 0.7 ? 'bg-green-500' : dq.confidence_score > 0.4 ? 'bg-gold' : 'bg-red-500';

    return (
        <motion.div
            className={`glass-dark border ${confidenceStyles.dashed ? 'border-dashed' : 'border-white/5'} rounded-xl p-4`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
        >
            <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-2">
                    <ShieldAlert size={16} className="text-gold/60" />
                    <h3 className="text-sm font-bold tracking-wide uppercase text-gold/70">Read Reliability</h3>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-black uppercase tracking-tighter ${reliabilityColor}`}>{reliabilityLabel}</span>
                    {dq.confidence_score < 0.5 && (
                        <motion.button
                            onClick={onToggleDetails}
                            className="flex items-center gap-1 px-2 py-1 bg-black/20 border border-white/5 rounded-md hover:bg-white/5 transition-colors cursor-pointer"
                            whileTap={{ scale: 0.98 }}
                        >
                            <span className={`text-[10px] font-medium ${confidenceStyles.text}`}>{showDetails ? 'Hide' : 'Details'}</span>
                        </motion.button>
                    )}
                </div>
            </div>

            <motion.div
                className="flex items-center gap-3 mb-3"
                layout
            >
                <div className="flex-1 h-2 bg-black/40 rounded-full overflow-hidden">
                    <motion.div
                        className={`h-full ${progressColor}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${dq.confidence_score * 100}%` }}
                        transition={{ duration: 1, ease: "easeOut" }}
                    />
                </div>
                <span className="text-[10px] font-bold text-cream/40 uppercase">{(dq.confidence_score * 100).toFixed(0)}%</span>
            </motion.div>

            <AnimatePresence>
                {(!showDetails || dq.degradation_reasons.length > 0) && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-2"
                    >
                        <p className="text-sm text-cream/50 leading-relaxed border-l-2 border-gold/20 pl-3">
                            Trust in AI advice degrades when signals are conflicting or data is sparse. Review the factors below.
                        </p>
                        <ul className="space-y-1.5 pt-1">
                            {dq.degradation_reasons.map((reason, i) => (
                                <motion.li
                                    key={i}
                                    className="text-sm text-cream/50 flex items-start gap-2 leading-tight"
                                    initial={{ opacity: 0, x: -5 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                >
                                    <span className="mt-1 w-1.5 h-1.5 rounded-full bg-gold/30 shrink-0" />
                                    {reason}
                                </motion.li>
                            ))}
                        </ul>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

// --- Intelligence Offline ---
const IntelligenceOffline: React.FC<{ onBeginAnalysis: () => void }> = ({ onBeginAnalysis }) => (
    <motion.div
        className="glass-dark border border-gold/10 rounded-2xl p-10 flex flex-col items-center justify-center text-center gap-4"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
    >
      <BrainCircuit size={48} className="text-gold/20" />
      <div>
        <h3 className="text-gold font-black uppercase tracking-wide">Intelligence Offline</h3>
        <p className="text-cream/40 text-[10px] uppercase font-bold tracking-wide mt-1">Initialize analysis to receive strategic advice</p>
      </div>
      <motion.button
        onClick={onBeginAnalysis}
        className="mt-4 px-6 py-2 bg-gold/10 hover:bg-gold/20 text-gold border border-gold/20 rounded-lg text-[10px] font-black uppercase tracking-wide transition-all"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Begin Analysis
      </motion.button>
    </motion.div>
);

// --- Cards Required Placeholder ---
const CardsRequired: React.FC = () => (
    <motion.div
        className="glass-dark border border-white/5 rounded-2xl p-10 flex flex-col items-center justify-center text-center gap-4"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
    >
      <CreditCard size={48} className="text-white/10" />
      <div>
        <h3 className="text-cream/60 font-black uppercase tracking-wide">Hole Cards Missing</h3>
        <p className="text-cream/30 text-[10px] uppercase font-bold tracking-wide mt-1">Input your cards to enable AI analysis</p>
      </div>
    </motion.div>
);

const AnalysisSkeleton = () => (
    <motion.div
        className="space-y-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
    >
        <div className="h-32 bg-white/5 rounded-xl" />
        <div className="grid grid-cols-2 gap-2.5">
            <div className="h-16 bg-white/5 rounded-xl" />
            <div className="h-16 bg-white/5 rounded-xl" />
        </div>
    </motion.div>
);