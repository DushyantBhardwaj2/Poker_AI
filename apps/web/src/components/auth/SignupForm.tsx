import React, { useState, useEffect } from 'react';
import { authClient, isAuthEnabled } from '../../lib/auth';
import { isAuthPath } from '../../lib/auth-utils';
import { Mail, Lock, UserPlus, AlertCircle, ArrowLeft, Settings, User, ShieldCheck } from 'lucide-react';

export const SignupForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [experience, setExperience] = useState('Intermediate');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthEnabled) {
      setError("AUTHENTICATION SYSTEM OFFLINE: PUBLIC_NEON_AUTH_URL is not configured.");
    }
  }, []);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthEnabled) return;
    
    setLoading(true);
    setError(null);
    try {
      const { error: signUpError } = await authClient.signUp.email({
        email,
        password,
        name,
        // Passing additional fields if supported by the schema
        // metadata: { experience } 
      });
      
      if (signUpError) {
        setError(signUpError.message || 'Signup failed');
      } else {
        const searchParams = new URLSearchParams(window.location.search);
        const redirectTo = searchParams.get('redirectTo') || '/';
        window.location.href = isAuthPath(redirectTo) ? '/' : redirectTo;
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {!isAuthEnabled && (
        <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl mb-6">
          <p className="text-[10px] text-amber-500 font-black uppercase tracking-widest">Configuration Required</p>
        </div>
      )}

      <form onSubmit={handleSignup} className="space-y-4">
        {/* Name Field */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-gold/60 font-black uppercase tracking-widest ml-1">Operator Name</label>
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-gold/40" size={18} />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full bg-charcoal/50 border border-gold/10 rounded-xl py-4 pl-12 pr-4 text-cream outline-none font-mono text-sm focus:border-gold/30 transition-all"
              placeholder="e.g. John Doe"
            />
          </div>
        </div>

        {/* Email Field */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-gold/60 font-black uppercase tracking-widest ml-1">Secure Email</label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gold/40" size={18} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-charcoal/50 border border-gold/10 rounded-xl py-4 pl-12 pr-4 text-cream outline-none font-mono text-sm focus:border-gold/30 transition-all"
              placeholder="operator@poker-sense.ai"
            />
          </div>
        </div>

        {/* Password Field */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-gold/60 font-black uppercase tracking-widest ml-1">Master Access Key</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gold/40" size={18} />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full bg-charcoal/50 border border-gold/10 rounded-xl py-4 pl-12 pr-4 text-cream outline-none font-mono text-sm focus:border-gold/30 transition-all"
              placeholder="Min. 8 characters"
            />
          </div>
        </div>

        {/* Poker Experience Level */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-gold/60 font-black uppercase tracking-widest ml-1">Strategic Experience</label>
          <div className="grid grid-cols-3 gap-2">
            {['Novice', 'Intermediate', 'Pro'].map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setExperience(level)}
                className={`py-3 rounded-xl border text-[10px] font-black uppercase tracking-widest transition-all ${
                  experience === level 
                    ? 'bg-gold/10 border-gold text-gold shadow-[0_0_15px_rgba(212,175,55,0.1)]' 
                    : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        <div className="py-2 flex items-center gap-2 text-[9px] text-gold/40 font-black uppercase tracking-widest px-1">
          <ShieldCheck size={12} />
          <span>Biometric & MFA can be enabled post-registration</span>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex items-start gap-3">
            <AlertCircle className="text-red-500" size={18} />
            <p className="text-xs text-red-500">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-5 bg-gold text-charcoal-dark rounded-xl font-black uppercase tracking-[0.2em] shadow-gold-strong flex items-center justify-center gap-3 transition-all hover:scale-[1.01] active:scale-[0.98] disabled:opacity-50"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-charcoal-dark/20 border-t-charcoal-dark rounded-full animate-spin"></div>
          ) : (
            <>
              <UserPlus size={18} />
              Provision Identity
            </>
          )}
        </button>
      </form>

      <div className="text-center pt-4">
        <a
          href="/auth/sign-in"
          className="text-[10px] font-black uppercase tracking-[0.2em] text-gold/40 hover:text-gold transition-colors inline-flex items-center gap-2 group"
        >
          <ArrowLeft size={12} className="group-hover:-translate-x-1 transition-transform" />
          Already registered?
          <span className="text-gold underline underline-offset-4 decoration-gold/20 group-hover:decoration-gold">
            Return to Login
          </span>
        </a>
      </div>
    </div>
  );
};
