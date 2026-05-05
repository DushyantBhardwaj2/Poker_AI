import React from 'react';
import { NeonAuthUIProvider } from "@neondatabase/auth/react";
import { authClient } from "../lib/auth";

interface AuthWrapperProps {
  children: React.ReactNode;
}

/**
 * Provides Neon Auth context to the application.
 * Matches the Black and Gold premium tactical theme.
 */
export const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  return (
    <NeonAuthUIProvider 
      authClient={authClient}
      theme={{
        colors: {
          primary: "#D4AF37", // Gold
          background: "#0A0A0A", // Deep Charcoal
          foreground: "#F5F5F0", // Cream
          muted: "#1A1A1A",
          border: "rgba(212, 175, 55, 0.2)",
        },
        fontFamily: "var(--font-mono, 'JetBrains Mono', monospace)",
        borderRadius: "0px", // Sharp, tactical edges
      }}
    >
      {children}
    </NeonAuthUIProvider>
  );
};
