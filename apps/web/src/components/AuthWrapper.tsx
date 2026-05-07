import React from 'react';
import { AuthProvider } from './AuthProvider';
import { Sidebar } from './Sidebar';
import { PageGuard } from './PageGuard';

interface AuthWrapperProps {
  children: React.ReactNode;
  currentPath?: string;
}

/**
 * Provides master layout structure and handles top-level auth context.
 * Consolidates Sidebar and PageGuard into a single island root.
 */
export const AuthWrapper: React.FC<AuthWrapperProps> = ({ children, currentPath = '' }) => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  React.useEffect(() => {
    const savedCollapsed = localStorage.getItem('sidebar_collapsed');
    if (savedCollapsed !== null) {
      const collapsed = savedCollapsed === 'true';
      setIsCollapsed(collapsed);
      if (collapsed) document.body.classList.add('sidebar-collapsed');
    }
  }, []);

  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    localStorage.setItem('sidebar_collapsed', String(newCollapsed));
    if (newCollapsed) {
      document.body.classList.add('sidebar-collapsed');
    } else {
      document.body.classList.remove('sidebar-collapsed');
    }
  };

  return (
    <div className="neon-auth-theme-wrapper">
      <AuthProvider>
        <div className="flex min-h-screen">
          <Sidebar 
            isCollapsed={isCollapsed} 
            onToggleCollapse={toggleCollapse} 
            currentPath={currentPath}
          />

          <main className={`flex-1 ${isCollapsed ? 'lg:ml-20' : 'lg:ml-72'} flex flex-col items-center py-12 px-6 overflow-y-auto transition-all duration-500`}>
            <div className="w-full max-w-7xl flex flex-col items-center justify-center relative z-10">
              <PageGuard currentPath={currentPath}>
                {children}
              </PageGuard>
            </div>

            <footer className="mt-20 pt-16 border-t border-white/5 w-full text-gold/20 text-[10px] font-black uppercase tracking-[0.4em] flex flex-col items-center gap-4">
              <div className="flex items-center gap-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-terminal"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
                <span>PokerSense OS v2.4 // THEORY DRIVEN</span>
                <span className="w-1.5 h-1.5 bg-gold/10 rounded-full"></span>
                <span>Strategic Support Active</span>
              </div>
              <div className="text-[8px] opacity-40 italic">"IF YOU MAKE THE BEST DECISIONS, THE MONEY WILL FOLLOW"</div>
            </footer>
          </main>
        </div>
      </AuthProvider>
      <style>{`
        .neon-auth-theme-wrapper {
          --neon-primary: #D4AF37;
          --neon-background: #0A0A0A;
          --neon-foreground: #F5F5F0;
          --neon-muted: #1A1A1A;
          --neon-border: rgba(212, 175, 55, 0.2);
          --neon-radius: 0px;
          --font-sans: var(--font-mono, 'JetBrains Mono', monospace);
        }
      `}</style>
    </div>
  );
};
