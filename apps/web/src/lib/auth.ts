import { createAuthClient } from "@neondatabase/auth";

// PUBLIC_NEON_AUTH_URL should be set in .env or provider environment variables
const authUrl = import.meta.env.PUBLIC_NEON_AUTH_URL || import.meta.env.VITE_NEON_AUTH_URL || "";

export const isAuthEnabled = Boolean(authUrl && authUrl.startsWith('http'));

if (!isAuthEnabled) {
  if (typeof window !== 'undefined') {
    console.warn("⚠️ PokerSense Auth Warning: PUBLIC_NEON_AUTH_URL is not defined or invalid.");
    console.warn("Authentication features will be non-functional until configured in the environment.");
  }
}

// Better-Auth based client
export const authClient = createAuthClient(authUrl || "https://placeholder-auth.neon.tech");

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
export function subscribeToAuth(callback: (session: any) => void) {
  // BetterAuth doesn't have a direct "onAuthStateChanged" in the basic client,
  // but we can poll or use a proxy. For now, we'll rely on manual checks
  // or the NeonAuthUIProvider's internal state.
}
