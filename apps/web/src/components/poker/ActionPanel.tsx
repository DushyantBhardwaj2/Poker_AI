import React, { useState } from 'react';
import { usePokerStore } from '../../stores/usePokerStore';
import { PokerAPI } from '../../lib/api';

export default function ActionPanel() {
  const { players, activePlayerIndex, sessionId, updatePlayerAction, nextPlayer, setError } = usePokerStore();
  const [isRaising, setIsRaising] = useState(false);
  const [raiseAmount, setRaiseAmount] = useState<number | ''>('');

  const activePlayer = players[activePlayerIndex];
  
  // Calculate highest bet to determine if we can check or must call
  const maxBet = Math.max(...players.map(p => p.bet), 0);
  const toCall = maxBet - (activePlayer?.bet || 0);
  const canCheck = toCall === 0;

  if (!activePlayer) return null;

  const handleAction = async (action: 'fold' | 'check' | 'call' | 'raise' | 'all-in', amount: number = 0) => {
    try {
      // Opt UI
      updatePlayerAction(activePlayer.name, action, amount);
      nextPlayer();
      setIsRaising(false);
      setRaiseAmount('');
      
      // Real API
      if (sessionId) {
        await PokerAPI.recordAction(sessionId, activePlayer.name, action, amount);
      }
    } catch (err: any) {
      setError(err.message || 'Action failed');
    }
  };

  const ActionButton = ({ label, onClick, variant = 'default', shortcut }: any) => {
    const baseStyle = "relative flex flex-col items-center justify-center p-4 border font-mono tracking-widest transition-all group overflow-hidden";
    
    const variants = {
      default: "border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-500 hover:bg-gray-800",
      fold: "border-red-900/50 bg-red-950/30 text-red-400 hover:border-red-500/50 hover:bg-red-900/20",
      call: "border-emerald-900/50 bg-emerald-950/30 text-emerald-400 hover:border-emerald-500/50 hover:bg-emerald-900/20",
      raise: "border-amber-900/50 bg-amber-950/30 text-amber-400 hover:border-amber-500/50 hover:bg-amber-900/20",
    };

    return (
      <button onClick={onClick} className={`${baseStyle} ${variants[variant as keyof typeof variants]}`}>
        <span className="text-lg font-bold">{label}</span>
        {shortcut && <span className="absolute top-1 left-1 text-[10px] text-gray-600 border border-gray-700 px-1 rounded-sm">{shortcut}</span>}
      </button>
    );
  };

  return (
    <div className="h-full flex flex-col border border-gray-800 bg-gray-950">
      <div className="bg-gray-900 border-b border-gray-800 p-3 text-xs tracking-widest text-emerald-500 font-mono uppercase flex justify-between items-center">
        <span>Action Required</span>
        <span className="text-gray-400">{activePlayer.name}</span>
      </div>

      <div className="flex-1 p-4 flex flex-col gap-4 justify-center">
        
        {isRaising ? (
          <div className="flex flex-col h-full animate-in fade-in zoom-in duration-200">
            <div className="text-sm font-mono text-amber-400 mb-2">INPUT_AMOUNT</div>
            <div className="flex gap-2 mb-4">
              <span className="text-3xl text-gray-500 font-mono">$</span>
              <input 
                type="number"
                value={raiseAmount}
                onChange={(e) => setRaiseAmount(e.target.value ? Number(e.target.value) : '')}
                className="w-full bg-transparent border-b-2 border-amber-500/50 text-3xl font-mono text-gray-100 outline-none focus:border-amber-400 transition-colors"
                autoFocus
              />
            </div>
            
            <div className="grid grid-cols-3 gap-2 flex-1">
               {/* Quick add buttons could go here */}
               <button onClick={() => setRaiseAmount((Number(raiseAmount)||0) + potSize/2)} className="border border-gray-800 hover:bg-gray-800 text-xs font-mono text-gray-400">1/2 POT</button>
               <button onClick={() => setRaiseAmount((Number(raiseAmount)||0) + potSize)} className="border border-gray-800 hover:bg-gray-800 text-xs font-mono text-gray-400">FULL POT</button>
               <button onClick={() => setRaiseAmount(activePlayer.stack)} className="border border-red-900/50 hover:bg-red-900/20 text-xs font-mono text-red-400">MAX</button>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-4">
              <ActionButton label="CANCEL" onClick={() => setIsRaising(false)} />
              <ActionButton 
                label="CONFIRM" 
                variant="raise" 
                onClick={() => handleAction('raise', Number(raiseAmount))} 
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3 h-full">
            <ActionButton 
              label="FOLD" 
              variant="fold" 
              shortcut="F" 
              onClick={() => handleAction('fold')} 
            />
            
            {canCheck ? (
              <ActionButton 
                label="CHECK" 
                variant="call" 
                shortcut="C" 
                onClick={() => handleAction('check')} 
              />
            ) : (
              <ActionButton 
                label={`CALL $${toCall}`} 
                variant="call" 
                shortcut="C" 
                onClick={() => handleAction('call', toCall)} 
              />
            )}

            <ActionButton 
              label="RAISE" 
              variant="raise" 
              shortcut="R" 
              onClick={() => setIsRaising(true)} 
            />
            
            <ActionButton 
              label="ALL-IN" 
              variant="fold" // Using red style for danger
              shortcut="A" 
              onClick={() => handleAction('all-in', activePlayer.stack)} 
            />
          </div>
        )}

      </div>
    </div>
  );
}
