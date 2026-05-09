import React, { useState, useEffect } from 'react';
import { Play, BookOpen, GraduationCap, ChevronRight, Award, Target, Brain, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';
import { authClient } from '../lib/auth';
import { AuthProvider } from './AuthProvider';

// Staggered animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
      delayChildren: 0.3,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 25 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" }
  },
};

export const HomeView: React.FC = () => {
  const [mounted, setMounted] = React.useState(false);
  const [user, setUser] = useState<any>(null);

  React.useEffect(() => {
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

  return (
    <AuthProvider>
      <div className="max-w-7xl w-full space-y-16 py-16">
        {/* Hero Section with Dramatic Staggered Reveal */}
        <motion.section
          className="text-center space-y-6"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center gap-3 bg-gold/5 border border-gold/20 px-4 py-2 rounded-full"
          >
            <Award size={16} className="text-gold" />
            <span className="text-[10px] font-black uppercase tracking-widest text-gold">Advanced Decision Support System</span>
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="text-5xl md:text-7xl font-black text-white tracking-tighter leading-none"
          >
            Master the <span className="text-gold">Theory</span>,<br />Dominate the <span className="text-cream">Game.</span>
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="max-w-2xl mx-auto text-cream/50 text-base leading-relaxed"
          >
            PokerSense AI combines real-time Monte Carlo simulations with David Sklansky's "The Theory of Poker" to provide mathematically optimal move recommendations.
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row justify-center gap-6 pt-8"
          >
            <a
              href="/play"
              className="group relative bg-gold hover:bg-gold-light text-charcoal-dark px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-gold-strong flex items-center justify-center gap-4 hover:scale-105 active:scale-95"
            >
              Start Real-Time Analysis
              <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </a>

            {mounted && !user && (
                <a
                  href="/auth/sign-up"
                  className="group bg-white/5 hover:bg-white/10 text-cream px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all border border-white/10 flex items-center justify-center gap-4 hover:scale-105 active:scale-95"
                >
                  Create Account
                  <UserPlus size={18} className="group-hover:scale-110 transition-transform text-gold" />
                </a>
            )}

            <a
              href="/theory"
              className="group bg-white/5 hover:bg-white/10 text-cream px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all border border-white/10 flex items-center justify-center gap-4 hover:scale-105 active:scale-95"
            >
              Study the Theory
              <BookOpen size={18} />
            </a>
          </motion.div>
        </motion.section>


        {/* Principles Section with Staggered Cards */}
        <motion.section
          className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-16"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {[
            {
              icon: Target,
              title: "Expected Value",
              desc: "Every move is analyzed through the lens of long-term profitability (EV). We don't just guess; we calculate."
            },
            {
              icon: Brain,
              title: "Behavioral Modeling",
              desc: "The system detects opponent patterns to predict bluffs and identify fundamental strategic mistakes."
            },
            {
              icon: GraduationCap,
              title: "Theory-Driven",
              desc: "Powered by the Fundamental Theorem of Poker. We exploit opponent mistakes to maximize your edge."
            }
          ].map((item, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              className="bg-charcoal p-8 rounded-3xl border border-white/5 space-y-6 hover:border-gold/30 transition-all group hover:-translate-y-1"
            >
              <div className="w-10 h-10 bg-gold/10 rounded-2xl flex items-center justify-center text-gold group-hover:bg-gold group-hover:text-charcoal transition-all shadow-gold">
                <item.icon size={24} />
              </div>
              <h3 className="text-xl font-black text-white uppercase tracking-wider">{item.title}</h3>
              <p className="text-cream/40 leading-relaxed text-xs">{item.desc}</p>
            </motion.div>
          ))}
        </motion.section>
      </div>
    </AuthProvider>
  );
};