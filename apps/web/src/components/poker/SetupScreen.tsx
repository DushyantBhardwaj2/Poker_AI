import React, { useState } from 'react';
import { Users, Plus, Play, Trash2 } from 'lucide-react';
import { usePokerStore } from '../../stores/usePokerStore';
import { PokerAPI } from '../../lib/api';

export default function SetupScreen({ onComplete }: { onComplete: () => void }) {
  const [players, setLocalPlayers] = useState([{ id: '1', name: '', stack: 1000 }]);
  const [isStarting, setIsStarting] = useState(false);
  const { setSession, setPlayers, setError } = usePokerStore();

  const addPlayerRow = () => {
    setLocalPlayers([...players, { id: crypto.randomUUID(), name: '', stack: 1000 }]);
  };

  const removePlayerRow = (id: string) => {
    setLocalPlayers(players.filter(p => p.id !== id));
  };

  const updatePlayer = (id: string, field: 'name' | 'stack', value: string | number) => {
    setLocalPlayers(players.map(p => p.id === id ? { ...p, [field]: value } : p));
  };

  const handleStart = async () => {
    try {
      setIsStarting(true);
      setError(null);
      
      const validPlayers = players.filter(p => p.name.trim() !== '');
      if (validPlayers.length < 2) {
        throw new Error('Minimum 2 players required');
      }

      const sessionRes = await PokerAPI.startSession();
      const sessionId = sessionRes.session_id || crypto.randomUUID(); // Fallback if mock
      setSession(sessionId);

      // 2. Add Players
      for (const p of validPlayers) {
        await PokerAPI.addPlayer(sessionId, p.name, p.stack);
      }

      // 3. Update Store
      setPlayers(validPlayers.map(p => ({
        id: p.id,
        name: p.name,
        stack: p.stack,
        bet: 0,
        status: 'active',
      })));

      onComplete();
    } catch (err: any) {
      setError(err.message || 'Failed to start session');
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950 text-gray-100 font-mono p-4">
      <div className="w-full max-w-2xl border border-gray-800 bg-gray-900/50 backdrop-blur-sm p-8 rounded-none shadow-[0_0_15px_rgba(0,255,128,0.1)]">
        <div className="flex items-center gap-3 mb-8 border-b border-gray-800 pb-4">
          <Users className="w-8 h-8 text-emerald-400" />
          <h1 className="text-2xl font-bold tracking-widest text-emerald-400 uppercase">System Init :: PokerSense</h1>
        </div>

        <div className="space-y-4 mb-8">
          <div className="grid grid-cols-12 gap-4 text-xs tracking-wider text-gray-500 uppercase mb-2 px-2">
            <div className="col-span-7">Operator / Name</div>
            <div className="col-span-4">Initial Stack</div>
            <div className="col-span-1"></div>
          </div>
          
          {players.map((player, index) => (
            <div key={player.id} className="grid grid-cols-12 gap-4 items-center bg-gray-900 border border-gray-800 p-2 focus-within:border-emerald-500/50 transition-colors">
              <div className="col-span-7">
                <input 
                  type="text" 
                  value={player.name}
                  onChange={(e) => updatePlayer(player.id, 'name', e.target.value)}
                  placeholder={`Player ${index + 1}`}
                  className="w-full bg-transparent border-none outline-none text-emerald-100 placeholder-gray-700 px-2 font-mono"
                  autoFocus={index === players.length - 1}
                />
              </div>
              <div className="col-span-4 flex items-center gap-2">
                <span className="text-emerald-500">$</span>
                <input 
                  type="number" 
                  value={player.stack}
                  onChange={(e) => updatePlayer(player.id, 'stack', Number(e.target.value))}
                  className="w-full bg-transparent border-none outline-none text-emerald-100 font-mono"
                />
              </div>
              <div className="col-span-1 flex justify-center">
                <button 
                  onClick={() => removePlayerRow(player.id)}
                  className="text-gray-600 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-800">
          <button 
            onClick={addPlayerRow}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-emerald-400 transition-colors"
          >
            <Plus className="w-4 h-4" /> ADD_OPERATOR
          </button>

          <button 
            onClick={handleStart}
            disabled={isStarting}
            className="group relative flex items-center gap-3 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold px-8 py-3 rounded-none tracking-widest transition-all disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-current" />
            {isStarting ? 'INITIALIZING...' : 'START_SESSION'}
            <div className="absolute inset-0 border border-emerald-400 scale-105 opacity-0 group-hover:opacity-100 transition-all pointer-events-none"></div>
          </button>
        </div>
      </div>
    </div>
  );
}
