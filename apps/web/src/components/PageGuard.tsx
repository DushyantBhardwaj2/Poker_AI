import React from 'react';
import { AuthGuard } from './AuthGuard';
import { isAuthPath } from '../lib/auth-utils';

interface PageGuardProps {
  children: React.ReactNode;
  currentPath?: string;
}

/**
 * Conditionally applies AuthGuard based on the current path.
 * Public paths (like /auth/*) are allowed without authentication.
 */
export const PageGuard: React.FC<PageGuardProps> = ({ children, currentPath = '' }) => {
  // Initialize from window if possible to avoid one-frame mismatch
  const [mounted, setMounted] = React.useState(false);
  const [clientPath, setClientPath] = React.useState(currentPath);

  React.useEffect(() => {
    setMounted(true);
    // Sync if window available
    if (typeof window !== 'undefined') {
      setClientPath(window.location.pathname);
    }

    const handlePathChange = () => {
      setClientPath(window.location.pathname);
    };
    
    document.addEventListener('astro:after-swap', handlePathChange);
    window.addEventListener('popstate', handlePathChange);
    
    return () => {
      document.removeEventListener('astro:after-swap', handlePathChange);
      window.removeEventListener('popstate', handlePathChange);
    };
  }, []);

  // Sync state if prop changes (important for transition:persist)
  React.useEffect(() => {
    if (currentPath && currentPath !== clientPath) {
      setClientPath(currentPath);
    }
  }, [currentPath]);

  // Use the most up-to-date path available. 
  // Prefer currentPath (from prop) as it's updated immediately by Astro, 
  // whereas clientPath (state) might be stale for one frame during transitions.
  const activePath = currentPath || (mounted ? clientPath : (typeof window !== 'undefined' ? window.location.pathname : '')) || '/';
  
  const isAuth = isAuthPath(activePath);

  // LOOP PROTECTION: Check for self-referencing redirectTo in query params
  React.useEffect(() => {
    if (typeof window !== 'undefined' && isAuthPath(window.location.pathname)) {
      const searchParams = new URLSearchParams(window.location.search);
      const redirectTo = searchParams.get('redirectTo');
      
      // If we are on an auth page and it's trying to redirect back to an auth page,
      // break the loop by redirecting to home.
      if (redirectTo && isAuthPath(redirectTo)) {
        console.warn(`[PageGuard] Infinite loop detected: redirectTo="${redirectTo}" on auth path. Redirecting to home.`);
        window.location.replace('/');
      }
    }
  }, [mounted]);

  // Diagnostic logging removed to prevent dev-mode spam

  // During SSR or on auth paths, just render children without the guard
  if (!mounted || isAuth) {
    return <>{children}</>;
  }

  return <AuthGuard currentPath={activePath}>{children}</AuthGuard>;
};
