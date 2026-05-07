import React, { useState, useEffect } from 'react';
import { Play, BookOpen, GraduationCap, ChevronRight, Award, Target, Brain, UserPlus } from 'lucide-react';
import { authClient } from '../lib/auth';
import { AuthProvider } from './AuthProvider';

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
      <div className="max-w-6xl w-full space-y-16 animate-fade-in py-12">
        {/* Hero Section */}
        <section className="text-center space-y-8">
          <div className="inline-flex items-center gap-3 bg-gold/5 border border-gold/20 px-4 py-2 rounded-full animate-slide-up">
            <Award size={16} className="text-gold" />
            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-gold">Advanced Decision Support System</span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-black text-white tracking-tighter leading-none animate-slide-up stagger-1">
            Master the <span className="text-gold">Theory</span>,<br />Dominate the <span className="text-cream">Game.</span>
          </h1>
          
          <p className="max-w-2xl mx-auto text-cream/50 text-lg leading-relaxed animate-slide-up stagger-2">
            PokerSense AI combines real-time Monte Carlo simulations with David Sklansky's "The Theory of Poker" to provide mathematically optimal move recommendations.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-6 pt-8 animate-slide-up stagger-3">
            <a 
              href="/play"
              className="group relative bg-gold hover:bg-gold-light text-charcoal-dark px-10 py-5 rounded-2xl font-black text-sm uppercase tracking-widest transition-all shadow-gold-strong flex items-center justify-center gap-4"
            >
              Start Real-Time Analysis
              <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </a>
            
            {mounted && !user && (
                <a 
                  href="/auth/sign-up"
                  className="group bg-white/5 hover:bg-white/10 text-cream px-10 py-5 rounded-2xl font-black text-sm uppercase tracking-widest transition-all border border-white/10 flex items-center justify-center gap-4"
                >
                  Create Account
                  <UserPlus size={18} className="group-hover:scale-110 transition-transform text-gold" />
                </a>
            )}

            <a 
              href="/theory"
              className="bg-white/5 hover:bg-white/10 text-cream px-10 py-5 rounded-2xl font-black text-sm uppercase tracking-widest transition-all border border-white/10 flex items-center justify-center gap-4"
            >
              Study the Theory
              <BookOpen size={18} />
            </a>
          </div>
        </section>


        {/* Principles Section */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-12">
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
            <div key={i} className={`bg-charcoal p-10 rounded-3xl border border-white/5 space-y-6 hover:border-gold/30 transition-all group animate-slide-up stagger-${i+1}`}>
              <div className="w-12 h-12 bg-gold/10 rounded-2xl flex items-center justify-center text-gold group-hover:bg-gold group-hover:text-charcoal transition-all shadow-gold">
                <item.icon size={24} />
              </div>
              <h3 className="text-2xl font-black text-white uppercase tracking-wider">{item.title}</h3>
              <p className="text-cream/40 leading-relaxed text-sm">{item.desc}</p>
            </div>
          ))}
        </section>
      </div>
    </AuthProvider>
  );
};
