/**
 * Utility to check if a path is an authentication-related route.
 * These routes should be accessible without authentication and 
 * should not trigger auth-related redirects.
 */
export const isAuthPath = (path: string): boolean => {
  if (!path) return false;
  
  // 1. Clean the path (remove query params and trailing slashes)
  const cleanPath = path.split('?')[0].split('#')[0].replace(/\/$/, '');
  
  // 2. Normalize path to always have a leading slash for consistent matching
  const normalizedPath = (cleanPath.startsWith('/') ? cleanPath : '/' + cleanPath).toLowerCase() || '/';
  
  // 3. Check for standard /auth prefix or common auth keywords
  // This is highly permissive to prevent loops
  const result = 
    normalizedPath === '/auth' || 
    normalizedPath.startsWith('/auth/') ||
    normalizedPath.includes('/login') || 
    normalizedPath.includes('/signup') || 
    normalizedPath.includes('/sign-in') || 
    normalizedPath.includes('/sign-up') ||
    normalizedPath.includes('/signin') ||
    normalizedPath.includes('/register') ||
    normalizedPath.includes('/callback');

  return result;
};

export const DEFAULT_AUTH_REDIRECT = '/auth/sign-in';
