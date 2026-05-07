import React from 'react';
import { NeonAuthUIProvider } from "@neondatabase/auth/react";
import { authClient } from "../lib/auth";

interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * Low-level Auth Provider that only handles Neon Auth context.
 * Use this to wrap page-level islands that need auth state.
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  return (
    <NeonAuthUIProvider 
      authClient={authClient}
      defaultTheme="dark"
    >
      {children}
    </NeonAuthUIProvider>
  );
};
