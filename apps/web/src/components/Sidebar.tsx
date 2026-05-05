import React, { useEffect, useState } from 'react';
import { Home, Play, BookOpen, GraduationCap, Settings, Menu, X, ChevronLeft, ChevronRight, LogIn } from 'lucide-react';
import { SignedIn, SignedOut, UserButton } from "@neondatabase/auth/react";

export const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activePath, setActivePath] = useState('/');
  const [theoryMode, setTheoryMode] = useState(true);

  useEffect(() => {
    // Set initial path
    setActivePath(window.location.pathname);

    // Sync theoryMode with localStorage
    const savedMode = localStorage.getItem('poker_theory_mode');
    if (savedMode !== null) {
      setTheoryMode(savedMode === 'true');
    }

    const savedCollapsed = localStorage.getItem('sidebar_collapsed');
    if (savedCollapsed !== null) {
      const collapsed = savedCollapsed === 'true';
      setIsCollapsed(collapsed);
      if (collapsed) document.body.classList.add('sidebar-collapsed');
    }

    // Listen for path changes (Astro View Transitions)
    const handlePageChange = () => {
      setActivePath(window.location.pathname);
    };

    document.addEventListener('astro:after-swap', handlePageChange);
    return () => document.removeEventListener('astro:after-swap', handlePageChange);
  }, []);

  const toggleTheoryMode = () => {
    const newMode = !theoryMode;
    setTheoryMode(newMode);
    localStorage.setItem('poker_theory_mode', String(newMode));
    // Dispatch custom event so other components (like PokerTable) can react
    window.dispatchEvent(new CustomEvent('poker_theory_mode_change', { detail: { theoryMode: newMode } }));
  };

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

  const navItems = [
    { id: 'home', label: 'Home', icon: Home, href: '/' },
    { id: 'play', label: 'Play Game', icon: Play, href: '/play' },
    { id: 'learn', label: 'Learn Poker', icon: GraduationCap, href: '/theory' },
    { id: 'guide', label: 'Guide & Rules', icon: BookOpen, href: '/guide' },
    { id: 'settings', label: 'Settings', icon: Settings, href: '/settings' },
  ];

  const authNavItem = { id: 'auth', label: 'Sign In', icon: LogIn, href: '/auth/sign-in' };

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
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Sidebar Container */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 bg-charcoal border-r border-gold/10 transform transition-all duration-500 ease-in-out
        ${isOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0'}
        ${isCollapsed ? 'lg:w-20' : 'lg:w-72'}
      `}>
        {/* Collapse Toggle Desktop */}
        <button 
          onClick={toggleCollapse}
          className="hidden lg:flex absolute -right-4 top-10 w-8 h-8 bg-charcoal border border-gold/20 rounded-full items-center justify-center text-gold shadow-gold hover:bg-gold/10 transition-all z-[60]"
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>

        <div className={`flex flex-col h-full ${isCollapsed ? 'p-4' : 'p-8'} transition-all duration-500 overflow-hidden`}>
          <div className={`flex items-center gap-4 ${isCollapsed ? 'mb-10 justify-center' : 'mb-12'}`}>
            <a href="/" className="flex items-center gap-4 group">
              <div className="w-10 h-10 bg-gold rounded-xl flex items-center justify-center shadow-gold transition-transform group-hover:scale-105 shrink-0">
                <span className="text-charcoal font-black text-xl">P</span>
              </div>
              {!isCollapsed && (
                <div className="animate-fade-in whitespace-nowrap">
                  <h1 className="text-xl font-black tracking-widest text-gold uppercase">PokerSense</h1>
                  <p className="text-[10px] text-gold/40 tracking-[0.2em] font-bold">OS v2.4 // THEORY DRIVEN</p>
                </div>
              )}
            </a>
          </div>

          <nav className="flex-1 space-y-2">
            {navItems.map((item) => {
              const active = isActive(item.href);
              return (
                <a
                  key={item.id}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={`
                    w-full flex items-center gap-4 rounded-xl transition-all duration-300 group
                    ${isCollapsed ? 'justify-center p-4' : 'px-6 py-4'}
                    ${active 
                      ? 'bg-gold/10 text-gold border border-gold/20 shadow-gold' 
                      : 'text-cream/40 hover:text-cream hover:bg-white/5 border border-transparent'
                    }
                  `}
                  title={isCollapsed ? item.label : ''}
                >
                  <item.icon size={20} className={`${active ? 'text-gold' : 'group-hover:text-gold'} shrink-0`} />
                  {!isCollapsed && (
                    <span className="font-bold tracking-widest text-xs uppercase animate-fade-in whitespace-nowrap">{item.label}</span>
                  )}
                </a>
              );
            })}

            <SignedOut>
              <a
                href={authNavItem.href}
                onClick={() => setIsOpen(false)}
                className={`
                  w-full flex items-center gap-4 rounded-xl transition-all duration-300 group
                  ${isCollapsed ? 'justify-center p-4' : 'px-6 py-4'}
                  text-cream/40 hover:text-cream hover:bg-white/5 border border-transparent
                `}
                title={isCollapsed ? authNavItem.label : ''}
              >
                <authNavItem.icon size={20} className="group-hover:text-gold shrink-0" />
                {!isCollapsed && (
                  <span className="font-bold tracking-widest text-xs uppercase animate-fade-in whitespace-nowrap">{authNavItem.label}</span>
                )}
              </a>
            </SignedOut>
          </nav>

          <div className="mt-4 mb-8 flex justify-center">
            <SignedIn>
              <div className={`flex items-center gap-4 ${isCollapsed ? '' : 'w-full px-6 py-4 bg-white/5 rounded-xl border border-white/10'}`}>
                <UserButton />
                {!isCollapsed && (
                  <div className="flex flex-col animate-fade-in">
                    <span className="text-[10px] font-black text-gold uppercase tracking-tighter">Authenticated</span>
                    <span className="text-[8px] text-cream/40 uppercase tracking-widest">Premium Access</span>
                  </div>
                )}
              </div>
            </SignedIn>
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
