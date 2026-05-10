import React, { useState, useCallback } from 'react';
import { usePokerStore } from '../../stores/usePokerStore';
import { PokerAPI } from '../../lib/api';

export default function ActionPanel() {
  const { players, current_player_index, sessionId, pot, updatePlayerAction, nextPlayer, setError, setPlayers } = usePokerStore();
  const [isRaising, setIsRaising] = useState(false);
  const [raiseAmount, setRaiseAmount] = useState<number | ''>('');
  const [actionInProgress, setActionInProgress] = useState(false);

  const activePlayer = players[current_player_index];

  // Calculate highest bet to determine if we can check or must call
  const maxBet = Math.max(...players.map(p => p.bet || 0), 0);
  const toCall = maxBet - (activePlayer?.bet || 0);
  const canCheck = toCall === 0;

  if (!activePlayer) return null;

  const handleAction = useCallback(async (action: 'fold' | 'check' | 'call' | 'raise' | 'all-in', amount: number = 0) => {
    if (actionInProgress) return;
    setActionInProgress(true);

    try {
      const previousPlayers = JSON.parse(JSON.stringify(players));
      const previousIndex = current_player_index;

      updatePlayerAction(activePlayer.name, action, amount);
      nextPlayer();
      setIsRaising(false);
      setRaiseAmount('');

      if (sessionId) {
        await PokerAPI.recordAction(sessionId, activePlayer.name, action, amount);
      }
    } catch (err: any) {
      setPlayers(previousPlayers);
      setError(err.message || 'Action failed - state restored, please retry');
    } finally {
      setActionInProgress(false);
    }
  }, [actionInProgress, sessionId, players, current_player_index, activePlayer]);

  const ActionButton = ({ label, onClick, variant = 'default' }: any) => {
    const baseStyle = "flex-1 flex flex-col items-center justify-center p-3 border font-mono tracking-widest transition-all group relative";
    const disabledStyle = actionInProgress ? "opacity-40 cursor-not-allowed" : "hover:brightness-110";

    const variants = {
      default: "border-gray-700/50 bg-gray-900/80 text-gray-400 hover:border-gray-500 hover:text-gray-200",
      fold: "border-red-900/30 bg-red-950/40 text-red-400/80 hover:border-red-500/50 hover:text-red-400 hover:bg-red-900/20",
      call: "border-emerald-900/30 bg-emerald-950/40 text-emerald-400/80 hover:border-emerald-500/50 hover:text-emerald-400 hover:bg-emerald-900/20",
      raise: "border-amber-900/30 bg-amber-950/40 text-amber-400/80 hover:border-amber-500/50 hover:text-amber-400 hover:bg-amber-900/20",
    };

    return (
      <button
        onClick={onClick}
        disabled={actionInProgress}
        className={`${baseStyle} ${variants[variant as keyof typeof variants]} ${disabledStyle} rounded-xl`}
      >
        <span className="text-sm font-bold">{label}</span>
      </button>
    );
  };

  return (
    <div className="h-full flex flex-col border border-gray-800/60 bg-charcoal-dark rounded-xl overflow-hidden">
      <div className="bg-charcoal-light/60 border-b border-gray-800/40 px-4 py-2 text-xs tracking-widest text-gold font-bold uppercase flex justify-between items-center">
        <span>Action Required</span>
        <span className="text-cream/60">{activePlayer.name}</span>
      </div>

      <div className="flex-1 p-3 flex flex-col gap-3 justify-center">

        {isRaising ? (
          <div className="flex flex-col h-full animate-in fade-in zoom-in duration-200">
            <div className="text-xs font-mono text-amber-400 mb-2">INPUT_AMOUNT</div>
            <div className="flex gap-2 mb-3">
              <span className="text-2xl text-gray-500 font-mono">$</span>
              <input
                type="number"
                value={raiseAmount}
                onChange={(e) => setRaiseAmount(e.target.value ? Number(e.target.value) : '')}
                className="w-full bg-transparent border-b-2 border-amber-500/50 text-2xl font-mono text-white outline-none focus:border-amber-400 transition-colors"
                autoFocus
              />
            </div>

            <div className="grid grid-cols-3 gap-2 mb-3">
               <button onClick={() => setRaiseAmount((Number(raiseAmount)||0) + pot/2)} className="border border-gray-700/50 hover:bg-gray-800/50 text-xs font-mono text-gray-400 rounded-lg py-2">1/2 POT</button>
               <button onClick={() => setRaiseAmount((Number(raiseAmount)||0) + pot)} className="border border-gray-700/50 hover:bg-gray-800/50 text-xs font-mono text-gray-400 rounded-lg py-2">FULL POT</button>
               <button onClick={() => setRaiseAmount(activePlayer.stack)} className="border border-red-900/30 hover:bg-red-900/20 text-xs font-mono text-red-400 rounded-lg py-2">MAX</button>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-auto">
              <ActionButton label="CANCEL" onClick={() => setIsRaising(false)} variant="default" />
              <ActionButton
                label="CONFIRM"
                variant="raise"
                onClick={() => handleAction('raise', Number(raiseAmount))}
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2 h-full">
            <ActionButton
              label="FOLD"
              variant="fold"
              onClick={() => handleAction('fold')}
            />

            {canCheck ? (
              <ActionButton
                label="CHECK"
                variant="call"
                onClick={() => handleAction('check')}
              />
            ) : (
              <ActionButton
                label={`CALL $${toCall}`}
                variant="call"
                onClick={() => handleAction('call', toCall)}
              />
            )}

            <ActionButton
              label="RAISE"
              variant="raise"
              onClick={() => setIsRaising(true)}
            />

            <ActionButton
              label="ALL-IN"
              variant="fold"
              onClick={() => handleAction('all-in', activePlayer.stack)}
            />
          </div>
        )}

      </div>
    </div>
  );
}
