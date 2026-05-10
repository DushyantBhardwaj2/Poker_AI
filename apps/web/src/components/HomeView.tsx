import React, { useState, useEffect, useMemo } from 'react';
import { Play, BookOpen, GraduationCap, ChevronRight, Award, Target, Brain, UserPlus, TrendingUp, Activity, Zap, Crosshair } from 'lucide-react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { authClient } from '../lib/auth';
import { AuthProvider } from './AuthProvider';

// Optimized animation settings for performance
const springTransition = { type: "spring", stiffness: 120, damping: 20 };
const easeOutTransition = { duration: 0.6, ease: [0.22, 1, 0.36, 1] };

// Staggered animation variants - GPU accelerated
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.15 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { ...easeOutTransition } }
};

const fadeInVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.8, ease: "easeOut" } }
};

// Floating particle component - GPU accelerated
const FloatingParticle = ({ delay, size, left, top }: { delay: number; size: number; left: string; top: string }) => (
  <motion.div
    className="absolute rounded-full bg-gold/5 pointer-events-none"
    style={{ width: size, height: size, left, top }}
    animate={{
      y: [0, -20, 0],
      opacity: [0.1, 0.3, 0.1],
      scale: [1, 1.1, 1]
    }}
    transition={{
      duration: 4 + Math.random() * 2,
      delay,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  />
);

// Probability ring visualization - lightweight SVG animation
const ProbabilityRing = () => (
  <motion.svg
    className="absolute -top-8 -right-8 w-24 h-24 opacity-30"
    viewBox="0 0 100 100"
    animate={{ rotate: 360 }}
    transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
  >
    <defs>
      <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.1" />
        <stop offset="50%" stopColor="#D4AF37" stopOpacity="0.4" />
        <stop offset="100%" stopColor="#D4AF37" stopOpacity="0.1" />
      </linearGradient>
    </defs>
    <circle cx="50" cy="50" r="45" fill="none" stroke="url(#ringGrad)" strokeWidth="1" />
    <circle cx="50" cy="50" r="35" fill="none" stroke="url(#ringGrad)" strokeWidth="0.5" />
    <circle cx="50" cy="50" r="25" fill="none" stroke="url(#ringGrad)" strokeWidth="0.3" />
  </motion.svg>
);

// Animated stat line - lightweight HUD element
const AnimatedStatLine = ({ label, value, delay }: { label: string; value: string; delay: number }) => (
  <motion.div
    className="flex justify-between items-center text-xs"
    initial={{ opacity: 0, x: -10 }}
    whileInView={{ opacity: 1, x: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.5, delay }}
  >
    <span className="text-cream/40">{label}</span>
    <motion.span
      className="text-gold font-mono"
      animate={{ opacity: [0.7, 1, 0.7] }}
      transition={{ duration: 2, repeat: Infinity, delay }}
    >
      {value}
    </motion.span>
  </motion.div>
);

// Enhanced Feature Card with animations
const FeatureCard = ({ icon: Icon, title, desc, delay, index }: { icon: any; title: string; desc: string; delay: number; index: number }) => {
  const cardVariants = {
    hidden: { opacity: 0, y: 40 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { ...easeOutTransition, delay: delay * 0.1 }
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      whileHover={{ y: -4, transition: { duration: 0.3 } }}
      className="group relative bg-charcoal-light border border-white/5 p-5 rounded-2xl overflow-hidden"
    >
      {/* Glow effect on hover */}
      <motion.div
        className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{ background: "radial-gradient(ellipse at center, rgba(212,175,55,0.15) 0%, transparent 70%)" }}
      />

      {/* Corner accent */}
      <div className="absolute top-0 right-0 w-16 h-16 overflow-hidden">
        <div className="absolute top-[-20px] right-[-20px] w-40 h-40 bg-gold/5 rotate-45 group-hover:rotate-45 transition-transform duration-500" />
      </div>

      <div className="relative z-10 space-y-3">
        <motion.div
          className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center text-gold group-hover:bg-gold group-hover:text-charcoal transition-all duration-500 shadow-gold"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, delay: delay * 0.2, repeat: Infinity }}
        >
          <Icon size={20} />
        </motion.div>

        <h3 className="text-base font-black text-white uppercase tracking-wider">{title}</h3>
        <p className="text-xs text-cream/50 leading-relaxed">{desc}</p>

        {/* Mini HUD stats - subtle */}
        <div className="pt-2 border-t border-white/5 space-y-1">
          {index === 0 && (
            <>
              <AnimatedStatLine label="EV Accuracy" value="94.2%" delay={0.1} />
              <AnimatedStatLine label="Simulations" value="10K+" delay={0.15} />
            </>
          )}
          {index === 1 && (
            <>
              <AnimatedStatLine label="Bluff Precision" value="87%" delay={0.1} />
              <AnimatedStatLine label="Patterns" value="2.4K" delay={0.15} />
            </>
          )}
          {index === 2 && (
            <>
              <AnimatedStatLine label="Theory Tags" value="156" delay={0.1} />
              <AnimatedStatLine label="References" value="20 Ch." delay={0.15} />
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// CTA Button with magnetic effect
const CTAButton = ({ href, primary, children, icon: Icon }: { href: string; primary?: boolean; children: React.ReactNode; icon?: any }) => {
  return (
    <motion.a
      href={href}
      className={`
        group relative overflow-hidden rounded-xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all
        ${primary
          ? "bg-gold hover:bg-gold-light text-charcoal-dark shadow-gold-strong hover:shadow-gold"
          : "bg-white/5 hover:bg-white/10 text-cream border border-white/10 hover:border-gold/30"
        }
        px-6 py-3
      `}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        initial={{ x: "-100%" }}
        whileHover={{ x: "100%" }}
        transition={{ duration: 0.6 }}
      />
      <span className="relative z-10 flex items-center gap-2">
        {children}
        {Icon && <Icon size={14} className="group-hover:translate-x-0.5 transition-transform" />}
      </span>
    </motion.a>
  );
};

// AI Analysis visualization - pulsing ring
const AIIndicator = () => (
  <div className="relative w-8 h-8">
    <motion.div
      className="absolute inset-0 rounded-full border border-gold/20"
      animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
      transition={{ duration: 2, repeat: Infinity }}
    />
    <motion.div
      className="absolute inset-2 rounded-full border border-gold/40"
      animate={{ scale: [1, 1.3], opacity: [0.3, 0] }}
      transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
    />
    <div className="absolute inset-3 rounded-full bg-gold" />
  </div>
);

export const HomeView: React.FC = () => {
  const [mounted, setMounted] = React.useState(false);
  const [user, setUser] = useState<any>(null);

  // Mouse parallax - lazy tracked
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    if (typeof window === 'undefined') return;
    const x = (e.clientX / window.innerWidth - 0.5) * 10;
    const y = (e.clientY / window.innerHeight - 0.5) * 10;
    setMousePos({ x, y });
  };

  useEffect(() => {
    setMounted(true);

    const fetchSession = async () => {
      try {
        const { data: session } = await authClient.getSession();
        setUser(session?.user || null);
      } catch (err) {
        console.error("[HomeView] Failed to fetch session:", err);
      }
    };

    fetchSession();
  }, []);

  // Memoize particles to prevent rerenders
  const particles = useMemo(() => (
    Array.from({ length: 8 }).map((_, i) => ({
      id: i,
      delay: i * 0.5,
      size: 4 + Math.random() * 8,
      left: `${10 + Math.random() * 80}%`,
      top: `${10 + Math.random() * 80}%`
    }))
  ), []);

  return (
    <AuthProvider>
      {/* Animated background layers */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-charcoal-dark" />

        {/* Radial glow - top center */}
        <motion.div
          className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full"
          style={{
            background: "radial-gradient(ellipse at center, rgba(212,175,55,0.08) 0%, transparent 60%)",
          }}
          animate={{ opacity: [0.5, 0.8, 0.5] }}
          transition={{ duration: 5, repeat: Infinity }}
        />

        {/* Moving grain - very subtle */}
        <motion.div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          }}
          animate={{ x: [0, 50, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />

        {/* Floating particles */}
        {particles.map((p) => (
          <FloatingParticle key={p.id} {...p} />
        ))}
      </div>

      <div
        className="max-w-5xl mx-auto w-full space-y-14 py-12"
        onMouseMove={handleMouseMove}
      >
        {/* Hero Section */}
        <motion.section
          className="text-center space-y-5 relative"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Probability ring decoration */}
          <div className="absolute -top-12 -right-12 w-32 h-32 pointer-events-none opacity-20">
            <ProbabilityRing />
          </div>

          {/* AI indicator badge */}
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center gap-3 bg-gold/5 border border-gold/20 px-4 py-2 rounded-full"
          >
            <AIIndicator />
            <span className="text-[10px] font-black uppercase tracking-widest text-gold">Advanced Decision Support System</span>
          </motion.div>

          {/* Heading with parallax effect */}
          <motion.h1
            variants={itemVariants}
            className="text-4xl md:text-5xl lg:text-6xl font-black text-white tracking-tighter leading-tight"
            style={{
              x: mousePos.x * -2,
              y: mousePos.y * -1
            }}
          >
            Master the <span className="text-gold relative">Theory
              {/* Shimmer effect */}
              <motion.span
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                initial={{ x: "-100%" }}
                animate={{ x: "100%" }}
                transition={{ duration: 3, repeat: Infinity, delay: 2 }}
                style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)" }}
              />
            </span>,<br />Dominate the <span className="text-cream">Game.</span>
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="max-w-xl mx-auto text-cream/60 text-sm leading-relaxed"
          >
            PokerSense AI combines real-time Monte Carlo simulations with David Sklansky's "The Theory of Poker" to provide mathematically optimal move recommendations.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row justify-center gap-4 pt-6"
          >
            <CTAButton href="/play" primary>
              Start Real-Time Analysis
              <ChevronRight size={14} />
            </CTAButton>

            {mounted && !user && (
              <CTAButton href="/auth/sign-up">
                Create Account
                <UserPlus size={14} />
              </CTAButton>
            )}

            <CTAButton href="/theory">
              Study the Theory
              <BookOpen size={14} />
            </CTAButton>
          </motion.div>
        </motion.section>

        {/* Principles Section */}
        <motion.section
          className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-10"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          {[
            { icon: Target, title: "Expected Value", desc: "Every move is analyzed through the lens of long-term profitability (EV). We don't just guess; we calculate." },
            { icon: Brain, title: "Behavioral Modeling", desc: "The system detects opponent patterns to predict bluffs and identify fundamental strategic mistakes." },
            { icon: GraduationCap, title: "Theory-Driven", desc: "Powered by the Fundamental Theorem of Poker. We exploit opponent mistakes to maximize your edge." }
          ].map((item, i) => (
            <FeatureCard key={i} {...item} index={i} delay={300 + i * 100} />
          ))}
        </motion.section>

        {/* Decorative divider */}
        <motion.div
          className="flex items-center justify-center gap-2 pt-8"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <div className="h-px w-16 bg-gradient-to-r from-transparent to-gold/30" />
          <Crosshair size={12} className="text-gold/30" />
          <div className="h-px w-16 bg-gradient-to-l from-transparent to-gold/30" />
        </motion.div>
      </div>
    </AuthProvider>
  );
};