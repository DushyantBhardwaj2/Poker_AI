import React, { useEffect, useState } from 'react';
import { Home, Play, BookOpen, GraduationCap, Settings, Menu, X, ChevronLeft, ChevronRight, LogIn, Target, LogOut, User, TrendingUp } from 'lucide-react';
import { authClient, isAuthEnabled } from "../lib/auth";

import { isAuthPath } from '../lib/auth-utils';

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  currentPath?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  isCollapsed = false, 
  onToggleCollapse,
  currentPath = ''
}) => {
  const [mounted, setMounted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [activePath, setActivePath] = useState(currentPath);
  const [theoryMode, setTheoryMode] = useState(true);
  
  // PASSIVE AUTH: Fetch session manually to avoid hook-based redirects
  const [user, setUser] = useState<any>(null);

  const fetchSession = async () => {
    if (!mounted || !isAuthEnabled) {
      if (!isAuthEnabled && mounted) {
        setUser({ id: 'guest', email: 'guest@poker-sense.ai' });
      }
      return;
    }
    
    try {
      const { data: session } = await authClient.getSession();
      setUser(session?.user || null);
    } catch (err) {
      // Passive fail
    }
  };

  const handleLogout = async () => {
    await authClient.signOut();
    setUser(null);
    window.location.href = '/auth/sign-in';
  };

  useEffect(() => {
    setMounted(true);
    
    // Sync if window available
    if (typeof window !== 'undefined') {
      setActivePath(window.location.pathname);
    }

    // Sync theoryMode with localStorage
    const savedMode = localStorage.getItem('poker_theory_mode');
    if (savedMode !== null) {
      setTheoryMode(savedMode === 'true');
    }

    // Listen for path changes (Astro View Transitions)
    const handlePageChange = () => {
      setActivePath(window.location.pathname);
    };

    document.addEventListener('astro:after-swap', handlePageChange);
    return () => document.removeEventListener('astro:after-swap', handlePageChange);
  }, []);

  useEffect(() => {
    if (mounted) {
      fetchSession();
    }
  }, [mounted, activePath]);

  // Update activePath when currentPath prop changes
  useEffect(() => {
    if (currentPath) {
      setActivePath(currentPath);
    }
  }, [currentPath]);

  const toggleTheoryMode = () => {
    const newMode = !theoryMode;
    setTheoryMode(newMode);
    localStorage.setItem('poker_theory_mode', String(newMode));
    // Dispatch custom event so other components (like PokerTable) can react
    window.dispatchEvent(new CustomEvent('poker_theory_mode_change', { detail: { theoryMode: newMode } }));
  };

  const navItems = [
    { id: 'home', label: 'Home', icon: Home, href: '/' },
    { id: 'play', label: 'Play Game', icon: Play, href: '/play' },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp, href: '/analytics' },
    { id: 'learn', label: 'Learn Poker', icon: GraduationCap, href: '/theory' },
    { id: 'guide', label: 'Guide & Rules', icon: BookOpen, href: '/guide' },
    { id: 'settings', label: 'Settings', icon: Settings, href: '/settings' },
  ];

  const authNavItem = { id: 'auth', label: 'Sign In', icon: LogIn, href: '/auth/sign-in' };
  const signupNavItem = { id: 'signup', label: 'Create Account', icon: Target, href: '/auth/sign-up' };

  const isActive = (href: string) => {
    if (href === '/' && activePath === '/') return true;
    if (href !== '/' && activePath.startsWith(href)) return true;
    return false;
  };

  return (
    <>
      {/* Mobile Toggle */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-6 right-6 z-[60] bg-gold p-3 rounded-full text-charcoal shadow-gold active:scale-90 transition-transform"
        aria-label="Toggle Menu"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar Container */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 bg-charcoal-dark/95 border-r border-white/5 transform transition-all duration-500 ease-in-out
        ${isOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0'}
        ${isCollapsed ? 'lg:w-20' : 'lg:w-64'}
      `}>
        {/* Collapse Toggle Desktop */}
        <button 
          onClick={onToggleCollapse}
          className="hidden lg:flex absolute -right-4 top-10 w-8 h-8 bg-charcoal border border-gold/20 rounded-full items-center justify-center text-gold shadow-gold hover:bg-gold/10 transition-all z-[60]"
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>

        <div className={`flex flex-col h-full ${isCollapsed ? 'p-4' : 'p-6'} transition-all duration-500 overflow-hidden`}>
          <div className={`flex items-center gap-3 ${isCollapsed ? 'mb-8 justify-center' : 'mb-10'}`}>
            <a href="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 bg-gold/90 rounded-lg flex items-center justify-center shadow-gold-subtle transition-transform group-hover:scale-105 shrink-0">
                <span className="text-charcoal font-black text-lg">P</span>
              </div>
              {!isCollapsed && (
                <div className="animate-fade-in whitespace-nowrap">
                  <h1 className="text-lg font-bold text-cream/80 tracking-wide">PokerSense</h1>
                </div>
              )}
            </a>
          </div>

          <nav className="flex-1 space-y-1.5">
            {navItems.map((item) => {
              const active = isActive(item.href);
              return (
                <a
                  key={item.id}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={`
                    w-full flex items-center gap-4 rounded-xl transition-all duration-300 group
                    ${isCollapsed ? 'justify-center p-3' : 'px-5 py-3.5'}
                    ${active
                      ? 'bg-gold/5 text-gold border border-gold/10'
                      : 'text-cream/50 hover:text-cream/80 hover:bg-white/5 border border-transparent'
                    }
                  `}
                  title={isCollapsed ? item.label : ''}
                >
                  <item.icon size={18} className={`${active ? 'text-gold' : 'text-cream/40 group-hover:text-gold'} shrink-0`} />
                  {!isCollapsed && (
                    <span className="font-bold tracking-widest text-xs uppercase animate-fade-in whitespace-nowrap">{item.label}</span>
                  )}
                </a>
              );
            })}

            {mounted && !user && (
                <div className="pt-4 space-y-1.5">
                  <a
                    href={authNavItem.href}
                    onClick={() => setIsOpen(false)}
                    className={`
                      w-full flex items-center gap-4 rounded-xl transition-all duration-300 group
                      ${isCollapsed ? 'justify-center p-3' : 'px-5 py-3.5'}
                      ${isActive(authNavItem.href) ? 'bg-gold/10 text-gold' : 'text-cream/50 hover:text-cream hover:bg-white/5'}
                      border border-transparent
                    `}
                    title={isCollapsed ? authNavItem.label : ''}
                  >
                    <authNavItem.icon size={18} className="group-hover:text-gold shrink-0" />
                    {!isCollapsed && (
                      <span className="font-bold tracking-widest text-xs uppercase animate-fade-in whitespace-nowrap">{authNavItem.label}</span>
                    )}
                  </a>
                  <a
                    href={signupNavItem.href}
                    onClick={() => setIsOpen(false)}
                    className={`
                      w-full flex items-center gap-4 rounded-xl transition-all duration-300 group
                      ${isCollapsed ? 'justify-center p-3' : 'px-5 py-3.5'}
                      ${isActive(signupNavItem.href) ? 'bg-gold/20 text-gold shadow-gold' : 'bg-gold/5 text-gold/70 hover:bg-gold/10 hover:text-gold'}
                      border border-gold/10
                    `}
                    title={isCollapsed ? signupNavItem.label : ''}
                  >
                    <signupNavItem.icon size={18} className="shrink-0" />
                    {!isCollapsed && (
                      <span className="font-bold tracking-widest text-xs uppercase animate-fade-in whitespace-nowrap">{signupNavItem.label}</span>
                    )}
                  </a>
                </div>
            )}
          </nav>

          <div className="mt-4 mb-8 flex justify-center">
            {mounted && user && (
                <div className={`flex flex-col gap-2 ${isCollapsed ? 'items-center' : 'w-full'}`}>
                  <div className={`flex items-center gap-4 ${isCollapsed ? '' : 'w-full px-6 py-4 bg-white/5 rounded-xl border border-white/10'}`}>
                    <div className="w-8 h-8 rounded-full bg-gold/10 border border-gold/20 flex items-center justify-center text-gold shrink-0">
                      <User size={16} />
                    </div>
                    {!isCollapsed && (
                      <div className="flex flex-col animate-fade-in flex-1 overflow-hidden">
                        <span className="text-[10px] font-black text-gold uppercase tracking-tighter truncate">
                          {user?.email?.split('@')[0] || 'Authenticated'}
                        </span>
                        <span className="text-[8px] text-cream/40 uppercase tracking-widest">System Access</span>
                      </div>
                    )}
                  </div>
                  
                  <button 
                    onClick={handleLogout}
                    className={`
                      flex items-center gap-4 rounded-xl transition-all duration-300 group
                      ${isCollapsed ? 'justify-center p-4' : 'px-6 py-3'}
                      text-red-500/60 hover:text-red-500 hover:bg-red-500/5 border border-transparent
                    `}
                    title={isCollapsed ? 'Logout' : ''}
                  >
                    <LogOut size={18} className="shrink-0" />
                    {!isCollapsed && (
                      <span className="font-bold tracking-widest text-[10px] uppercase animate-fade-in">Sign Out</span>
                    )}
                  </button>
                </div>
            )}
          </div>

          {!isCollapsed && (
            <div className="mt-auto pt-8 border-t border-gold/5 animate-fade-in">
              <div className={`rounded-2xl p-6 border transition-all duration-500 ${theoryMode ? 'bg-gold/5 border-gold/20' : 'bg-white/2 border-white/5'}`}>
                <div className="flex items-center justify-between mb-4">
                  <h4 className={`text-[10px] font-black uppercase tracking-[0.2em] ${theoryMode ? 'text-gold' : 'text-cream/20'}`}>Learning Mode</h4>
                  <button 
                    onClick={toggleTheoryMode}
                    className={`w-10 h-5 rounded-full relative transition-colors duration-300 ${theoryMode ? 'bg-gold' : 'bg-white/10'}`}
                  >
                    <div className={`absolute top-1 w-3 h-3 rounded-full bg-charcoal transition-all duration-300 ${theoryMode ? 'left-6' : 'left-1'}`} />
                  </button>
                </div>
                <p className={`text-[9px] leading-relaxed transition-colors duration-300 ${theoryMode ? 'text-cream/40' : 'text-cream/10'}`}>
                  {theoryMode 
                    ? 'Theory-assisted insights enabled. Every decision explained through "The Theory of Poker" lens.' 
                    : 'Standard simulation mode. Theoretical reasoning hidden.'}
                </p>
                {theoryMode && (
                  <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mt-4">
                    <div className="w-3/4 h-full bg-gold shadow-gold animate-pulse-gold"></div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {isCollapsed && (
            <div className="mt-auto pt-8 border-t border-gold/5 flex justify-center">
              <button 
                onClick={toggleTheoryMode}
                className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${theoryMode ? 'bg-gold text-charcoal shadow-gold' : 'bg-white/5 text-white/20'}`}
                title="Toggle Theory Mode"
              >
                <GraduationCap size={18} />
              </button>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
