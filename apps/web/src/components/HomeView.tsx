import React, { useState, useEffect, useMemo, memo, useCallback } from 'react';
import { Play, BookOpen, ChevronRight, UserPlus, Zap, Target, Brain, Eye, TrendingUp, Users, Lightbulb, BarChart3, Gauge, Ghost } from 'lucide-react';
import { motion, useMotionValue } from 'framer-motion';
import { authClient } from '../lib/auth';
import { AuthProvider } from './AuthProvider';

// Animation presets
const easeOut = { duration: 0.5, ease: [0.22, 1, 0.36, 1] };
const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.07, delayChildren: 0.1 } }
};
const itemVariants = {
  hidden: { opacity: 0, y: 25 },
  visible: { opacity: 1, y: 0, transition: { ...easeOut } }
};

// ═══════════════════════════════════════════════════════════════
// FLOATING PARTICLES
// ═══════════════════════════════════════════════════════════════

const Particle = memo(({ delay, size, left, top, type }: { delay: number; size: number; left: string; top: string; type: 'chip' | 'card' | 'glow' }) => {
  const getParticle = () => {
    if (type === 'chip') {
      return (
        <svg viewBox="0 0 24 24" className="w-full h-full" style={{ opacity: 0.12 }}>
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
          <circle cx="12" cy="12" r="6" fill="none" stroke="currentColor" strokeWidth="0.5" />
        </svg>
      );
    }
    if (type === 'card') {
      return (
        <svg viewBox="0 0 24 24" className="w-full h-full" style={{ opacity: 0.1 }}>
          <rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" strokeWidth="1" />
          <circle cx="8" cy="10" r="1.5" fill="currentColor" />
          <circle cx="12" cy="10" r="1.5" fill="currentColor" />
          <circle cx="16" cy="10" r="1.5" fill="currentColor" />
        </svg>
      );
    }
    return <div className="w-full h-full rounded-full" style={{ background: 'radial-gradient(circle, rgba(212,175,55,0.25) 0%, transparent 70%)' }} />;
  };

  const yRange = type === 'chip' ? -12 : type === 'card' ? -20 : -15;
  return (
    <motion.div
      className="absolute pointer-events-none text-gold"
      style={{ width: size, height: size, left, top }}
      animate={{ y: [0, yRange, 0], opacity: [0.06, 0.2, 0.06], scale: [1, 1.03, 1] }}
      transition={{ duration: type === 'chip' ? 5 + Math.random() * 2 : 4 + Math.random() * 3, delay, repeat: Infinity, ease: "easeInOut" }}
    >
      {getParticle()}
    </motion.div>
  );
});
Particle.displayName = 'Particle';

const FloatingParticles = memo(() => {
  const particles = useMemo(() => {
    const items = [];
    for (let i = 0; i < 3; i++) items.push({ id: `c-${i}`, d: i * 0.7, s: 10 + Math.random() * 6, l: `${12 + Math.random() * 76}%`, t: `${18 + Math.random() * 64}%`, type: 'chip' as const });
    for (let i = 0; i < 2; i++) items.push({ id: `d-${i}`, d: i * 0.6 + 0.4, s: 18 + Math.random() * 8, l: `${8 + Math.random() * 84}%`, t: `${14 + Math.random() * 72}%`, type: 'card' as const });
    for (let i = 0; i < 3; i++) items.push({ id: `g-${i}`, d: i * 0.9 + 0.2, s: 28 + Math.random() * 16, l: `${5 + Math.random() * 90}%`, t: `${12 + Math.random() * 76}%`, type: 'glow' as const });
    return items;
  }, []);
  return <>{particles.map(p => <Particle key={p.id} delay={p.d} size={p.s} left={p.l} top={p.t} type={p.type} />)}</>;
});
FloatingParticles.displayName = 'FloatingParticles';

// ═══════════════════════════════════════════════════════════════
// AI PULSE INDICATOR
// ═══════════════════════════════════════════════════════════════

const AIPulse = memo(() => (
  <div className="relative w-7 h-7">
    <motion.div className="absolute inset-0 rounded-full border border-gold/15" animate={{ scale: [1, 1.5], opacity: [0.3, 0] }} transition={{ duration: 2, repeat: Infinity }} />
    <motion.div className="absolute inset-1 rounded-full border border-gold/25" animate={{ scale: [1, 1.35], opacity: [0.2, 0] }} transition={{ duration: 2, delay: 0.3, repeat: Infinity }} />
    <div className="absolute inset-2 rounded-full bg-gold shadow-[0_0_6px_rgba(212,175,55,0.5)]" />
  </div>
));
AIPulse.displayName = 'AIPulse';

// ═══════════════════════════════════════════════════════════════
// CTA BUTTON
// ═══════════════════════════════════════════════════════════════

const CTAButton = memo(({ href, primary, children, icon: Icon }: { href: string; primary?: boolean; children: React.ReactNode; icon?: any }) => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const onMove = useCallback((e: React.MouseEvent<HTMLAnchorElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    x.set((e.clientX - r.left - r.width / 2) * 0.12);
    y.set((e.clientY - r.top - r.height / 2) * 0.12);
  }, [x, y]);

  const onLeave = useCallback(() => { x.set(0); y.set(0); }, [x, y]);

  return (
    <motion.a
      href={href}
      className={`relative overflow-hidden rounded-xl font-bold text-[11px] uppercase tracking-[0.16em] flex items-center justify-center gap-2.5 transition-all ${primary ? "bg-gold hover:bg-gold-light text-charcoal-dark shadow-[0_0_20px_rgba(212,175,55,0.3)] hover:shadow-[0_0_35px_rgba(212,175,55,0.45)]" : "bg-white/[0.04] hover:bg-white/[0.08] text-cream border border-white/[0.06] hover:border-gold/25"} px-6 py-3`}
      style={{ x, y }}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <motion.div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/12 to-transparent" initial={{ x: "-100%" }} whileHover={{ x: "100%" }} transition={{ duration: 0.6 }} />
      <span className="relative z-10 flex items-center gap-2.5">{children}{Icon && <Icon size={13} strokeWidth={2} />}</span>
    </motion.a>
  );
});
CTAButton.displayName = 'CTAButton';

// ═══════════════════════════════════════════════════════════════
// HOW TO PLAY - STEP CARD
// ═══════════════════════════════════════════════════════════════

const StepCard = memo(({ num, title, desc, icon: Icon, delay }: { num: number; title: string; desc: string; icon: any; delay: number }) => (
  <motion.div
    className="group relative bg-charcoal-light/60 border border-white/[0.04] p-4 rounded-xl overflow-hidden"
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ ...easeOut, delay: delay * 0.08 }}
    whileHover={{ y: -3, transition: { duration: 0.3 } }}
  >
    <motion.div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-400" style={{ background: "radial-gradient(ellipse at top, rgba(212,175,55,0.08) 0%, transparent 60%)" }} />
    <div className="relative z-10 flex gap-3.5">
      <div className="flex-shrink-0 w-8 h-8 bg-gold/[0.08] rounded-lg flex items-center justify-center text-gold/80 text-xs font-bold">{num}</div>
      <div className="flex-1 space-y-1.5">
        <div className="flex items-center gap-2">
          <Icon size={14} className="text-gold/70" />
          <h4 className="text-sm font-semibold text-white">{title}</h4>
        </div>
        <p className="text-xs text-cream/40 leading-relaxed">{desc}</p>
      </div>
    </div>
  </motion.div>
));
StepCard.displayName = 'StepCard';

// ═══════════════════════════════════════════════════════════════════════
// QUICK FEATURE - Small feature badge
// ═══════════════════════════════════════════════════════════════

const QuickFeature = memo(({ icon: Icon, label, delay }: { icon: any; label: string; delay: number }) => (
  <motion.div
    className="flex items-center gap-2 text-cream/50"
    initial={{ opacity: 0, x: -10 }}
    whileInView={{ opacity: 1, x: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.4, delay }}
  >
    <div className="w-5 h-5 bg-gold/[0.08] rounded flex items-center justify-center">
      <Icon size={10} className="text-gold/70" />
    </div>
    <span className="text-[11px]">{label}</span>
  </motion.div>
));
QuickFeature.displayName = 'QuickFeature';

// ═══════════════════════════════════════════════════════════════════════
// SECTION DIVIDER
// ═══════════════════════════════════════════════════════════════

const SectionDivider = memo(() => (
  <motion.div className="flex items-center justify-center gap-3 pt-12" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 0.5 }}>
    <div className="h-px w-12 bg-gradient-to-r from-transparent to-gold/30" />
    <div className="w-1.5 h-1.5 rotate-45 bg-gold/25" />
    <div className="h-px w-12 bg-gradient-to-l from-transparent to-gold/30" />
  </motion.div>
));
SectionDivider.displayName = 'SectionDivider';

// ═══════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════

export const HomeView: React.FC = () => {
  const [mounted, setMounted] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    setMounted(true);
    const fetchSession = async () => {
      try {
        const { data: session } = await authClient.getSession();
        setUser(session?.user || null);
      } catch (err) { console.error("[HomeView] Session error:", err); }
    };
    fetchSession();
  }, []);

  return (
    <AuthProvider>
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute inset-0 bg-charcoal-dark" />
        <motion.div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[700px] h-[550px] rounded-full" style={{ background: "radial-gradient(ellipse, rgba(212,175,55,0.06) 0%, transparent 55%)" }} animate={{ opacity: [0.4, 0.7, 0.4] }} transition={{ duration: 6, repeat: Infinity }} />
        <motion.div className="absolute bottom-[-8%] right-[-8%] w-[400px] h-[400px] rounded-full" style={{ background: "radial-gradient(circle, rgba(212,175,55,0.03) 0%, transparent 60%)" }} animate={{ opacity: [0.2, 0.35, 0.2] }} transition={{ duration: 7, repeat: Infinity }} />
        <motion.div className="absolute inset-0 opacity-[0.01]" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")` }} />
        <FloatingParticles />
      </div>

      <div className="max-w-4xl mx-auto w-full space-y-14 py-12">
        {/* HERO SECTION */}
        <motion.section className="text-center space-y-5" variants={containerVariants} initial="hidden" animate="visible">
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2.5 bg-gold/[0.05] border border-gold/12 px-4 py-2 rounded-full">
            <AIPulse />
            <span className="text-[9px] font-bold uppercase tracking-[0.14em] text-gold/70">AI-Powered Poker Intelligence</span>
          </motion.div>

          <motion.h1 variants={itemVariants} className="text-4xl md:text-5xl lg:text-5xl font-bold text-white tracking-tight leading-[1.15]">
            Your Winning Edge<br />
            <span className="text-gold relative">In Real-Time
              <motion.span className="absolute inset-0" initial={{ x: "-100%" }} animate={{ x: "100%" }} transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }} style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)" }} />
            </span>
          </motion.h1>

          <motion.p variants={itemVariants} className="max-w-lg mx-auto text-cream/50 text-[14px] leading-relaxed">
            Get instant AI analysis on every hand. Read opponents. Make smarter calls._train like a pro from your very first game.
          </motion.p>

          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row justify-center gap-3 pt-6">
            <CTAButton href="/play" primary>Start Playing <Play /></CTAButton>
            {mounted && !user && <CTAButton href="/auth/sign-up">Create Account <UserPlus /></CTAButton>}
            <CTAButton href="/guide">How It Works <BookOpen /></CTAButton>
          </motion.div>
        </motion.section>

        {/* HOW TO PLAY SECTION */}
        <motion.section className="space-y-6" initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-20px" }}>
          <motion.div className="text-center">
            <h2 className="text-lg font-bold text-white uppercase tracking-[0.1em]">How To Play</h2>
            <p className="text-xs text-cream/40 mt-1">Get started in under a minute</p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { n: 1, t: "Add Players", d: "Enter player names and starting stacks", i: Users },
              { n: 2, t: "Start a Hand", d: "Deal hole cards to each player", i: Play },
              { n: 3, t: "Get AI Insights", d: "Receive real-time EV and strategy advice", i: Lightbulb },
              { n: 4, t: "Track Tendencies", d: "Build opponent profiles over time", i: BarChart3 }
            ].map((s, i) => <StepCard key={s.n} num={s.n} title={s.t} desc={s.d} icon={s.i} delay={i + 1} />)}
          </div>

          <div className="flex justify-center pt-2">
            <CTAButton href="/how-to-use">View Full Guide <ChevronRight /></CTAButton>
          </div>
        </motion.section>

        <SectionDivider />

        {/* PLAY GAME SECTION */}
        <motion.section className="space-y-6" initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-20px" }}>
          <motion.div className="text-center">
            <h2 className="text-lg font-bold text-white uppercase tracking-[0.1em]">Play Smarter</h2>
            <p className="text-xs text-cream/40 mt-1">Powerful features in a simple interface</p>
          </motion.div>

          {/* Feature highlights grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { i: Zap, l: "Real-Time EV" },
              { i: Eye, l: "Bluff Detection" },
              { i: Target, l: "Pot Odds" },
              { i: Ghost, l: "GTO Reference" }
            ].map((f, idx) => (
              <motion.div
                key={idx}
                className="bg-charcoal-light/40 border border-white/[0.04] p-3 rounded-lg text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ ...easeOut, delay: idx * 0.08 }}
              >
                <f.i size={18} className="text-gold/70 mx-auto mb-2" />
                <p className="text-[10px] text-cream/60 uppercase tracking-wider">{f.l}</p>
              </motion.div>
            ))}
          </div>

          {/* Quick stats row */}
          <motion.div className="flex flex-wrap justify-center gap-x-6 gap-y-2 pt-2" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.3 }}>
            <QuickFeature icon={Gauge} label="94% EV Accuracy" delay={0} />
            <QuickFeature icon={Brain} label="Bluff Patterns" delay={0.1} />
            <QuickFeature icon={TrendingUp} label="2.4K Hands Tracked" delay={0.2} />
          </motion.div>

          <div className="flex justify-center pt-3">
            <CTAButton href="/play" primary>Begin Session <Play /></CTAButton>
          </div>
        </motion.section>
      </div>
    </AuthProvider>
  );
};

export default HomeView;