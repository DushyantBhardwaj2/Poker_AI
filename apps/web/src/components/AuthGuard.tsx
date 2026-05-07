import React, { useEffect, useState } from 'react';
import { authClient } from "../lib/auth";
import { isAuthPath, DEFAULT_AUTH_REDIRECT } from '../lib/auth-utils';

interface AuthGuardProps {
  children: React.ReactNode;
  fallbackPath?: string;
  currentPath?: string;
}

/**
 * Higher-order component to protect routes that require authentication.
 * Redirects to the login page if the user is not authenticated.
 */
export const AuthGuard: React.FC<AuthGuardProps> = ({ 
  children, 
  fallbackPath = '/auth/sign-in',
  currentPath = ''
}) => {
  const [mounted, setMounted] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRedirecting, setIsRedirecting] = useState(false);
  
  useEffect(() => {
    setMounted(true);
    
    const checkAuth = async () => {
      try {
        const { data: session } = await authClient.getSession();
        setUser(session?.user || null);
      } catch (err) {
        console.error("[AuthGuard] Session check failed:", err);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  const isAuthenticated = !!user;
  const isDefinitivelyLoggedOut = mounted && !isLoading && !isAuthenticated;
useEffect(() => {
  if (isDefinitivelyLoggedOut && !isRedirecting) {
    // Use window.location.pathname as a source of truth for current browser state
    const browserPath = typeof window !== 'undefined' ? window.location.pathname : '';
    const pathToCheck = browserPath || currentPath;

    const isA = isAuthPath(pathToCheck);

    // ABSOLUTE LOOP PREVENTION: Never redirect if we are already on an auth path
    if (isA) return;

    const target = fallbackPath.includes('login') ? '/auth/sign-in' : fallbackPath;

    // Secondary check: Don't redirect if we're already at the target
    const normalizedCurrent = (browserPath.split('?')[0].replace(/\/$/, '') || '/').toLowerCase();
    const normalizedTarget = (target.split('?')[0].replace(/\/$/, '') || '/').toLowerCase();

    if (normalizedCurrent === normalizedTarget || normalizedCurrent.startsWith('/auth')) {
      return;
    }

    setIsRedirecting(true);
    window.location.replace(target);
  }
}, [isDefinitivelyLoggedOut, fallbackPath, isRedirecting, currentPath]);


  if (!mounted) {
    return <div className="min-h-[50vh] flex items-center justify-center animate-pulse"><div className="w-12 h-12 rounded-full bg-gold/5" /></div>;
  }

  if (isLoading || isRedirecting || !isAuthenticated) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-6">
        <div className="w-16 h-16 border-4 border-gold/10 border-t-gold rounded-full animate-spin"></div>
        <div className="text-center">
          <p className="text-gold font-black uppercase tracking-[0.3em] text-xs">Authenticating Session</p>
          <p className="text-gold/40 text-[10px] uppercase tracking-widest mt-2">Strategic Clearance Required</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
