import React, { useState, useEffect } from 'react';
import { authClient, isAuthEnabled } from '../../lib/auth';
import { isAuthPath } from '../../lib/auth-utils';
import { Mail, Lock, LogIn, UserPlus, AlertCircle, ArrowRight, Settings } from 'lucide-react';

interface AuthUIProps {
  initialView?: 'login' | 'signup';
}

export const AuthUI: React.FC<AuthUIProps> = ({ initialView = 'login' }) => {
  const [view, setView] = useState<'login' | 'signup'>(initialView);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthEnabled) {
      setError("AUTHENTICATION SYSTEM OFFLINE: PUBLIC_NEON_AUTH_URL is not configured. Please check environment variables.");
    }
    
    const path = window.location.pathname;
    if (path.includes('signup') || path.includes('sign-up')) {
      setView('signup');
    } else {
      setView('login');
    }
  }, []);

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthEnabled) return;
    
    setLoading(true);
    setError(null);
    try {
      if (view === 'login') {
        const { error: signInError } = await authClient.signIn.email({
          email,
          password,
          rememberMe, // Enable persistent session
        });
        if (signInError) {
          setError(signInError.message || 'Login failed');
        } else {
          // Break potential redirect loops
          const searchParams = new URLSearchParams(window.location.search);
          const redirectTo = searchParams.get('redirectTo') || '/';
          
          if (isAuthPath(redirectTo)) {
            window.location.href = '/';
          } else {
            window.location.href = redirectTo;
          }
        }
      } else {
        const { error: signUpError } = await authClient.signUp.email({
          email,
          password,
        });
        if (signUpError) {
          setError(signUpError.message || 'Signup failed');
        } else {
          // Break potential redirect loops
          const searchParams = new URLSearchParams(window.location.search);
          const redirectTo = searchParams.get('redirectTo') || '/';
          
          if (isAuthPath(redirectTo)) {
            window.location.href = '/';
          } else {
            window.location.href = redirectTo;
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (!isAuthEnabled) return;
    
    setLoading(true);
    try {
      await authClient.signIn.social({
        provider: 'google',
        callbackURL: window.location.origin + '/',
      });
    } catch (err: any) {
      setError(err.message || 'Google login failed');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {!isAuthEnabled && (
        <div className="bg-amber-500/10 border border-amber-500/30 p-6 rounded-xl space-y-3 mb-6">
          <div className="flex items-center gap-3 text-amber-500">
            <Settings className="animate-spin-slow" size={20} />
            <span className="font-black uppercase tracking-widest text-xs">Configuration Required</span>
          </div>
          <p className="text-[10px] text-amber-200/60 leading-relaxed font-medium">
            The authentication service is currently detached. Ensure <code className="text-amber-500 font-bold">PUBLIC_NEON_AUTH_URL</code> is set in your environment variables to enable the Access Portal.
          </p>
        </div>
      )}

      {/* Social Login */}
      <button
        onClick={handleGoogleLogin}
        disabled={loading || !isAuthEnabled}
        className="w-full py-4 bg-gold/5 hover:bg-gold/10 border border-gold/20 rounded-xl font-black flex items-center justify-center gap-3 transition-all active:scale-[0.98] group relative overflow-hidden disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <svg className="w-5 h-5 relative z-10 transition-transform group-hover:scale-110" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#D4AF37"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#D4AF37" opacity="0.8"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#D4AF37" opacity="0.6"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#D4AF37" opacity="0.9"/>
        </svg>
        <span className="text-sm uppercase tracking-[0.2em] text-gold relative z-10">Authorize via Google</span>
      </button>

      <div className="flex items-center gap-4 py-2">
        <div className="flex-1 h-px bg-white/5"></div>
        <span className="text-[10px] text-cream/20 font-black uppercase tracking-[0.2em]">OR</span>
        <div className="flex-1 h-px bg-white/5"></div>
      </div>

      {/* Email Form */}
      <form onSubmit={handleEmailAuth} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-[10px] text-gold/60 font-black uppercase tracking-widest ml-1">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gold/40" size={18} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={!isAuthEnabled}
              className="w-full bg-charcoal/50 border border-gold/10 rounded-xl py-4 pl-12 pr-4 text-cream focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-all outline-none font-mono text-sm disabled:opacity-30"
              placeholder="operator@poker-sense.ai"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] text-gold/60 font-black uppercase tracking-widest ml-1">Access Key</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gold/40" size={18} />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={!isAuthEnabled}
              className="w-full bg-charcoal/50 border border-gold/10 rounded-xl py-4 pl-12 pr-4 text-cream focus:border-gold/50 focus:ring-1 focus:ring-gold/20 transition-all outline-none font-mono text-sm disabled:opacity-30"
              placeholder="••••••••••••"
            />
          </div>
        </div>

        {/* Tactical Persistence Toggle */}
        <div className="flex items-center gap-3 py-2 px-1">
          <button
            type="button"
            onClick={() => setRememberMe(!rememberMe)}
            disabled={!isAuthEnabled}
            className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${
              rememberMe ? 'bg-gold border-gold' : 'border-gold/20 hover:border-gold/40'
            } disabled:opacity-30`}
          >
            {rememberMe && <div className="w-2 h-2 bg-charcoal rounded-[1px]" />}
          </button>
          <span 
            className="text-[9px] font-black uppercase tracking-[0.1em] text-gold/60 cursor-pointer select-none disabled:opacity-30"
            onClick={() => isAuthEnabled && setRememberMe(!rememberMe)}
          >
            Maintain Tactical Persistence
          </span>
        </div>

        {error && (
          <div className={`border p-4 rounded-xl flex items-start gap-3 animate-shake ${
            !isAuthEnabled ? 'bg-amber-500/10 border-amber-500/20' : 'bg-red-500/10 border-red-500/20'
          }`}>
            <AlertCircle className={!isAuthEnabled ? 'text-amber-500' : 'text-red-500'} size={18} />
            <p className={`text-xs font-medium ${!isAuthEnabled ? 'text-amber-200/80' : 'text-red-500'}`}>{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !isAuthEnabled}
          className="w-full btn-tactical py-5 bg-gold text-charcoal-dark rounded-xl font-black uppercase tracking-[0.2em] shadow-gold-strong flex items-center justify-center gap-3 transition-all hover:scale-[1.01] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-charcoal-dark/20 border-t-charcoal-dark rounded-full animate-spin"></div>
          ) : (
            <>
              {view === 'login' ? <LogIn size={18} /> : <UserPlus size={18} />}
              {view === 'login' ? 'Initiate Session' : 'Register Operator'}
            </>
          )}
        </button>
      </form>

      {/* Toggle View */}
      <div className="text-center pt-4">
        <button
          onClick={() => {
            if (!isAuthEnabled) return;
            const nextView = view === 'login' ? 'signup' : 'login';
            const nextPath = nextView === 'login' ? 'sign-in' : 'sign-up';
            setView(nextView);
            window.history.pushState({}, '', `/auth/${nextPath}`);
          }}
          disabled={!isAuthEnabled}
          className="text-[10px] font-black uppercase tracking-[0.2em] text-gold/40 hover:text-gold transition-colors inline-flex items-center gap-2 group disabled:opacity-30"
        >
          {view === 'login' ? "Don't have an account?" : "Already registered?"}
          <span className="text-gold underline underline-offset-4 decoration-gold/20 group-hover:decoration-gold transition-all">
            {view === 'login' ? "Register Now" : "Sign In"}
          </span>
          <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};
