import { createAuthClient } from "@neondatabase/neon-js/auth";

// VITE_NEON_AUTH_URL should be set in .env
const authUrl = import.meta.env.PUBLIC_NEON_AUTH_URL || import.meta.env.VITE_NEON_AUTH_URL;

if (!authUrl) {
  console.warn("Neon Auth URL is not defined. Authentication will be disabled.");
}

export const authClient = createAuthClient(authUrl);

/**
 * Helper to get the current session token for API calls
 */
export async function getSessionToken(): Promise<string | null> {
  const { data: session } = await authClient.getSession();
  return session?.session?.token || null;
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
