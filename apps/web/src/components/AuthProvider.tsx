import React from 'react';
import { NeonAuthUIProvider } from "@neondatabase/auth/react";
import { authClient, isAuthEnabled } from "../lib/auth";

interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * Low-level Auth Provider that only handles Neon Auth context.
 * Use this to wrap page-level islands that need auth state.
 *
 * When PUBLIC_NEON_AUTH_URL is unset, lib/auth.ts hands the client a
 * placeholder hostname so construction does not throw. The provider does not
 * know that and retries get-session against a domain that will never resolve,
 * which on a fresh clone was 150+ failed requests per page load. Skipping the
 * provider entirely is the fix: nothing below it reads auth state without
 * checking isAuthEnabled first, and AuthGuard already treats the unconfigured
 * case as a guest session.
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  if (!isAuthEnabled) {
    return <>{children}</>;
  }

  return (
    <NeonAuthUIProvider
      authClient={authClient}
      defaultTheme="dark"
    >
      {children}
    </NeonAuthUIProvider>
  );
};
