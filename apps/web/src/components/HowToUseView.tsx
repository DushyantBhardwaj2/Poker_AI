import React, { useState } from 'react';
import {
  Play,
  Target,
  TrendingUp,
  BrainCircuit,
  Shield,
  Eye,
  Wallet,
  Users,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  Zap,
  BookOpen,
  Activity,
  BarChart3,
  Clock,
  Crosshair,
  Lightbulb,
  Gauge,
  WalletCards,
  MousePointerClick,
  CircleDollarSign,
  FlaskConical,
  Workflow
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SECTION_TABS = [
  { id: 'quickstart', label: 'Quick Start', icon: Zap },
  { id: 'interface', label: 'Interface', icon: MousePointerClick },
  { id: 'gameplay', label: 'Gameplay', icon: Play },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'theories', label: 'Theories', icon: BookOpen },
  { id: 'tips', label: 'Real Game Tips', icon: Lightbulb },
];

export const HowToUseView: React.FC = () => {
  const [activeTab, setActiveTab] = useState('quickstart');

  return (
    <div className="max-w-5xl mx-auto w-full space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 bg-gold/5 border border-gold/20 px-3 py-1.5 rounded-full">
          <Gauge size={14} className="text-gold" />
          <span className="text-[10px] font-black uppercase tracking-widest text-gold">Comprehensive Guide</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter">
          How to Use <span className="text-gold">PokerSense AI</span>
        </h1>
        <p className="text-cream/50 max-w-xl mx-auto text-sm leading-relaxed">
          Master real-time poker analysis with Monte Carlo simulations and behavioral profiling.
          This guide covers everything from setup to advanced strategic uso.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap justify-center gap-2">
        {SECTION_TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-widest transition-all
              ${activeTab === tab.id
                ? 'bg-gold text-charcoal-dark shadow-gold'
                : 'bg-charcoal-light border border-white/5 text-cream/50 hover:text-cream hover:border-gold/20'}
            `}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Sections */}
      <div className="bg-charcoal-dark border border-white/5 rounded-3xl p-6 md:p-8">
        <AnimatePresence mode="wait">
          {activeTab === 'quickstart' && <QuickStartSection key="quickstart" />}
          {activeTab === 'interface' && <InterfaceSection key="interface" />}
          {activeTab === 'gameplay' && <GameplaySection key="gameplay" />}
          {activeTab === 'analytics' && <AnalyticsSection key="analytics" />}
          {activeTab === 'theories' && <TheoriesSection key="theories" />}
          {activeTab === 'tips' && <TipsSection key="tips" />}
        </AnimatePresence>
      </div>

      {/* Bottom CTA */}
      <div className="flex justify-center gap-4 pt-4">
        <a href="/play" className="group flex items-center gap-2 bg-gold hover:bg-gold-light text-charcoal-dark px-6 py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-gold-strong">
          <Play size={16} />
          Start Playing
          <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
        </a>
        <a href="/theory" className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-cream px-6 py-3 rounded-xl font-black text-xs uppercase tracking-widest border border-white/10 transition-all">
          <BookOpen size={16} />
          Study Theory
        </a>
      </div>
    </div>
  );
};

// --- Quick Start Section ---
const QuickStartSection = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="space-y-6"
  >
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold">
        <Zap size={20} />
      </div>
      <h2 className="text-xl font-black text-white uppercase tracking-wider">Quick Start Guide</h2>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {[
        {
          step: '01',
          title: 'Create Your Hand',
          desc: 'Input your two hole cards by clicking the card icons. Select cards from the popup selector.',
        },
        {
          step: '02',
          title: 'Set the Table',
          desc: 'Add opponents and set community cards (flop/turn/river) to define the game state.',
        },
        {
          step: '03',
          title: 'Get AI Analysis',
          desc: 'Click "Analyze" to receive real-time EV recommendations with strategic reasoning.',
        },
        {
          step: '04',
          title: 'Make Your Decision',
          desc: 'Review the recommendation, pot odds, and opponent reads, then act accordingly.',
        }
      ].map((item) => (
        <div key={item.step} className="bg-charcoal-light border border-white/5 p-4 rounded-2xl">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-2xl font-black text-gold/20">{item.step}</span>
            <h3 className="text-sm font-bold text-white uppercase">{item.title}</h3>
          </div>
          <p className="text-xs text-cream/50 leading-relaxed">{item.desc}</p>
        </div>
      ))}
    </div>

    <div className="bg-gold/5 border border-gold/20 rounded-xl p-4 mt-4">
      <div className="flex items-start gap-3">
        <AlertTriangle size={16} className="text-gold shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-gold uppercase tracking-wider mb-1">Important Note</h4>
          <p className="text-xs text-cream/60">
            For best results, input at least 3-5 hands of observations on opponents before relying on behavioral analysis.
            The more hands you track, the more accurate the opponent profiling becomes.
          </p>
        </div>
      </div>
    </div>
  </motion.div>
);

// --- Interface Section ---
const InterfaceSection = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="space-y-6"
  >
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold">
        <MousePointerClick size={20} />
      </div>
      <h2 className="text-xl font-black text-white uppercase tracking-wider">Interface Overview</h2>
    </div>

    <div className="space-y-4">
      <InterfaceCard
        title="Virtual Poker Table"
        icon={WalletCards}
        description="The interactive table where you input hands, view community cards, and track player positions. Click on seat positions to set stacks and hole cards."
      />
      <InterfaceCard
        title="AI Advisor Panel"
        icon={BrainCircuit}
        description="Real-time strategic recommendations including recommended action, expected value (EV), pot odds requirements, and confidence level."
      />
      <InterfaceCard
        title="Opponent Reads"
        icon={Users}
        description="Behavioral profiling showing opponent archetypes (TAG, LAG, Rock, etc.) with VPIP/PFR statistics and exploitation recommendations."
      />
      <InterfaceCard
        title="Action Bar"
        icon={Target}
        description="Fold, Check, Call, Raise, and All-In buttons for recording your actions. Shows current player turn and stack sizes."
      />
    </div>

    <div className="bg-charcoal-light border border-white/5 rounded-xl p-4">
      <h3 className="text-xs font-bold text-gold uppercase tracking-wider mb-3">Keyboard Shortcuts</h3>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex justify-between"><span className="text-cream/40">Fold</span><kbd className="bg-black/40 px-2 py-0.5 rounded text-cream/60">F</kbd></div>
        <div className="flex justify-between"><span className="text-cream/40">Check/Call</span><kbd className="bg-black/40 px-2 py-0.5 rounded text-cream/60">C</kbd></div>
        <div className="flex justify-between"><span className="text-cream/40">Raise</span><kbd className="bg-black/40 px-2 py-0.5 rounded text-cream/60">R</kbd></div>
        <div className="flex justify-between"><span className="text-cream/40">All-In</span><kbd className="bg-black/40 px-2 py-0.5 rounded text-cream/60">A</kbd></div>
      </div>
    </div>
  </motion.div>
);

const InterfaceCard = ({ title, icon: Icon, description }: { title: string, icon: any, description: string }) => (
  <div className="bg-charcoal-light border border-white/5 p-4 rounded-xl flex gap-3">
    <div className="w-8 h-8 bg-gold/10 rounded-lg flex items-center justify-center text-gold shrink-0">
      <Icon size={16} />
    </div>
    <div>
      <h4 className="text-xs font-bold text-white uppercase mb-1">{title}</h4>
      <p className="text-xs text-cream/50 leading-relaxed">{description}</p>
    </div>
  </div>
);

// --- Gameplay Section ---
const GameplaySection = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="space-y-6"
  >
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold">
        <Play size={20} />
      </div>
      <h2 className="text-xl font-black text-white uppercase tracking-wider">How Gameplay Works</h2>
    </div>

    <div className="space-y-4">
      <StepCard
        number="1"
        title="Setup the Hand"
        content="Enter the game parameters: number of players, big blind amount, and starting stacks. Assign hole cards to each player."
      />
      <StepCard
        number="2"
        title="Input Community Cards"
        content="As the hand progresses through pre-flop, flop, turn, and river, update the community cards. Click the eye icon on the table to edit."
      />
      <StepCard
        number="3"
        title="Record Actions"
        content="Use the action bar to record each player's decisions. The system tracks who acted, the action type, and bet sizing."
      />
      <StepCard
        number="4"
        title="Get AI Analysis"
        content="At any point, click 'Analyze' to receive strategic advice. The AI considers your hand, opponent ranges, and behavioral data."
      />
      <StepCard
        number="5"
        title="Resolve Showdown"
        content="At showdown, input the winning hand or let the system evaluate. Player stats are updated based on results."
      />
    </div>

    <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4">
      <div className="flex items-start gap-3">
        <TrendingUp size={16} className="text-green-500 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-green-500 uppercase tracking-wider mb-1">Session Tracking</h4>
          <p className="text-xs text-cream/60">
            Your decisions are tracked across hands. The analytics page shows your VPIP, PFR, win rate, and detected strategic leaks over time.
          </p>
        </div>
      </div>
    </div>
  </motion.div>
);

const StepCard = ({ number, title, content }: { number: string, title: string, content: string }) => (
  <div className="flex gap-4">
    <div className="w-6 h-6 bg-gold/10 rounded-full flex items-center justify-center text-gold text-xs font-bold shrink-0 mt-0.5">
      {number}
    </div>
    <div>
      <h4 className="text-sm font-bold text-white uppercase mb-1">{title}</h4>
      <p className="text-xs text-cream/50 leading-relaxed">{content}</p>
    </div>
  </div>
);

// --- Analytics Section ---
const AnalyticsSection = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="space-y-6"
  >
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold">
        <BarChart3 size={20} />
      </div>
      <h2 className="text-xl font-black text-white uppercase tracking-wider">Understanding Analytics</h2>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <StatCard
        label="Total Profit/Loss"
        desc="Net earnings from the current session. Green = profitable, red = losing session."
      />
      <StatCard
        label="Win Rate"
        desc="Percentage of hands won at showdown. Professional players aim for 50%+."
      />
      <StatCard
        label="VPIP (Voluntarily Put $ In)"
        desc="% of hands you play. TAG: 15-25%, LAG: 30-45%+."
      />
      <StatCard
        label="PFR (Preflop Raise)"
        desc="% of hands you raise preflop. Indicates aggression level."
      />
      <StatCard
        label="Hands Tracked"
        desc="Total hands played in the session. More hands = more reliable stats."
      />
      <StatCard
        label="Strategic Leaks"
        desc="Detected mistakes in your play. Focus on fixing these to improve."
      />
    </div>

    <div className="bg-charcoal-light border border-white/5 rounded-xl p-4">
      <h3 className="text-xs font-bold text-gold uppercase tracking-wider mb-3">Reading Your Stats</h3>
      <div className="space-y-3 text-xs">
        <div className="flex justify-between items-center">
          <span className="text-cream/50">Tight & Aggressive (TAG)</span>
          <span className="text-gold">VPIP 18-25%, PFR 12-20%</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-cream/50">Loose & Aggressive (LAG)</span>
          <span className="text-gold">VPIP 30-45%, PFR 20-30%</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-cream/50">Loose Passive (Fish)</span>
          <span className="text-gold">VPIP 40%+, PFR &lt; 10%</span>
        </div>
      </div>
    </div>
  </motion.div>
);

const StatCard = ({ label, desc }: { label: string, desc: string }) => (
  <div className="bg-charcoal-light border border-white/5 p-3 rounded-xl">
    <h4 className="text-xs font-bold text-white uppercase mb-1">{label}</h4>
    <p className="text-xs text-cream/50">{desc}</p>
  </div>
);

// --- Theories Section ---
const TheoriesSection = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="space-y-6"
  >
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold">
        <BookOpen size={20} />
      </div>
      <h2 className="text-xl font-black text-white uppercase tracking-wider">Poker Theory Integration</h2>
    </div>

    <div className="space-y-4">
      <TheoryCard
        title="Fundamental Theorem of Poker"
        content="The essence of poker strategy: you should play hands differently than your opponents would play them if they could see your cards. PokerSense identifies when opponents make mistakes and exploits them."
      />
      <TheoryCard
        title="Pot Odds & Implied Odds"
        content="Every call is mathematical. PokerSense calculates the exact pot odds you need and considers implied odds (future betting) for draws."
      />
      <TheoryCard
        title="Position & Range Thinking"
        content="Hands should be played differently from different positions. PokerSense accounts for positional advantage when generating recommendations."
      />
      <TheoryCard
        title="Bluff Detection"
        content="The system analyzes opponent betting patterns to detect when they might be bluffing. Look for the 'Bluff Probability' in tactical view."
      />
      <TheoryCard
        title="Reverse Implied Odds"
        content="Sometimes calling is -EV even with the best hand because of potential future action. PokerSense flags these situations."
      />
    </div>

    <div className="bg-gold/5 border border-gold/20 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <FlaskConical size={14} className="text-gold" />
        <h3 className="text-xs font-bold text-gold uppercase tracking-wider">Theory Mode</h3>
      </div>
      <p className="text-xs text-cream/60">
        Toggle Theory Mode in the sidebar to enable detailed theoretical explanations with every recommendation.
        Every decision links back to core poker theory principles from David Sklansky's work.
      </p>
    </div>
  </motion.div>
);

const TheoryCard = ({ title, content }: { title: string, content: string }) => (
  <div className="bg-charcoal-light border border-white/5 p-4 rounded-xl">
    <h4 className="text-xs font-bold text-white uppercase mb-2">{title}</h4>
    <p className="text-xs text-cream/50 leading-relaxed">{content}</p>
  </div>
);

// --- Real Game Tips Section ---
const TipsSection = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="space-y-6"
  >
    <div className="flex items-center gap-3 mb-6">
      <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold">
        <Lightbulb size={20} />
      </div>
      <h2 className="text-xl font-black text-white uppercase tracking-wider">Using PokerSense in Real Games</h2>
    </div>

    <div className="space-y-3">
      <TipCard
        icon={Clock}
        title="Use Before Acting"
        content="Review the AI recommendation BEFORE you look at your cards in a real game. This prevents anchoring bias."
      />
      <TipCard
        icon={Eye}
        title="Track First, Then Decide"
        content="In live games, quickly note opponent actions, then check PokerSense for confirmation. Don't use it to think for you."
      />
      <TipCard
        icon={Target}
        title="Focus on Exploitation"
        content="Look at the Opponent Reads panel. If you identify a weak player, exploit their mistakes rather than playing GTO."
      />
      <TipCard
        icon={BrainCircuit}
        title="Trust the Math"
        content="When the pot odds justify a call, trust the mathematics even if it 'feels' wrong. Variance happens, but +EV decisions compound."
      />
      <TipCard
        icon={AlertTriangle}
        title="Watch for Tells"
        content="PokerSense detects betting pattern 'tells.' If it flags an opponent as 'frequently continuation betting,' exploit this with check-raises."
      />
      <TipCard
        icon={TrendingUp}
        title="Review Sessions"
        content="After each session, check the Analytics page. Look for patterns in your leaks and work to fix them one at a time."
      />
    </div>

    <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle size={16} className="text-red-500 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold text-red-500 uppercase tracking-wider mb-1">Common Mistakes to Avoid</h4>
          <ul className="text-xs text-cream/60 space-y-1">
            <li>• Chasing draws without proper pot odds</li>
            <li>• Calling too many hands from early position</li>
            <li>• Not adjusting to player types</li>
            <li>• Ignoring position in hand selection</li>
          </ul>
        </div>
      </div>
    </div>

    <div className="bg-gold/5 border border-gold/20 rounded-xl p-4">
      <h4 className="text-xs font-bold text-gold uppercase tracking-wider mb-2">Pro Tips</h4>
      <div className="space-y-2 text-xs text-cream/60">
        <p>• Use the 'Undo' feature to correct mistakes during setup</p>
        <p>• Enable Theory Mode to learn WHY recommendations make sense</p>
        <p>• Build opponent reads by tracking at least 10+ hands per player</p>
        <p>• Review your leaks weekly to identify patterns</p>
      </div>
    </div>
  </motion.div>
);

const TipCard = ({ icon: Icon, title, content }: { icon: any, title: string, content: string }) => (
  <div className="flex gap-3 items-start">
    <div className="w-6 h-6 bg-gold/10 rounded-lg flex items-center justify-center text-gold shrink-0">
      <Icon size={12} />
    </div>
    <div>
      <h4 className="text-xs font-bold text-white uppercase mb-1">{title}</h4>
      <p className="text-xs text-cream/50 leading-relaxed">{content}</p>
    </div>
  </div>
);