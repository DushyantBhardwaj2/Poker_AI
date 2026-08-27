import { createAuthClient } from "@neondatabase/auth";

function getSafeAuthUrl(): string {
  let raw = (import.meta.env.PUBLIC_NEON_AUTH_URL || import.meta.env.VITE_NEON_AUTH_URL || '').trim();
  if (!raw) return 'https://placeholder-auth.neon.tech';

  // Guard against accidentally setting DATABASE_URL into PUBLIC_NEON_AUTH_URL
  if (raw.startsWith('postgresql://') || raw.startsWith('postgres://')) {
    if (typeof window !== 'undefined') {
      console.error(
        "❌ PokerSense Auth Error: PUBLIC_NEON_AUTH_URL is configured with a PostgreSQL connection string (postgresql://...) instead of your Neon Auth URL (https://<auth-subdomain>.neon.tech). Please update this in your Vercel Environment Variables."
      );
    }
    return 'https://placeholder-auth.neon.tech';
  }

  if (!raw.startsWith('http://') && !raw.startsWith('https://')) {
    raw = `https://${raw}`;
  }

  try {
    const parsed = new URL(raw);
    // Disallow single-word invalid hostnames like 'postgresql' or 'postgres'
    if (parsed.hostname === 'postgresql' || parsed.hostname === 'postgres' || !parsed.hostname.includes('.')) {
      if (parsed.hostname !== 'localhost') {
        return 'https://placeholder-auth.neon.tech';
      }
    }
    return parsed.origin;
  } catch {
    return 'https://placeholder-auth.neon.tech';
  }
}

const authUrl = getSafeAuthUrl();

export const isAuthEnabled = Boolean(
  (import.meta.env.PUBLIC_NEON_AUTH_URL || import.meta.env.VITE_NEON_AUTH_URL) &&
  authUrl !== 'https://placeholder-auth.neon.tech'
);

if (!isAuthEnabled) {
  if (typeof window !== 'undefined') {
    console.warn("⚠️ PokerSense Auth Warning: PUBLIC_NEON_AUTH_URL is not defined or invalid.");
    console.warn("Authentication features will be non-functional until configured in the environment.");
  }
}

// Better-Auth based client
export const authClient = createAuthClient(authUrl);

/**
 * Helper to get the current session token for API calls
 */
export async function getSessionToken(): Promise<string | null> {
  if (!isAuthEnabled) return null;
  try {
    const { data: session } = await authClient.getSession();
    return session?.session?.token || null;
  } catch (err) {
    return null;
  }
}

/**
 * Reactive hook-like function for components to subscribe to auth state
 * In Astro/React, we can use this in a useEffect or a custom hook
 */
export function subscribeToAuth(_callback: (session: any) => void) {
  // BetterAuth doesn't have a direct "onAuthStateChanged" in the basic client,
  // but we can poll or use a proxy. For now, we'll rely on manual checks
  // or the NeonAuthUIProvider's internal state.
}
