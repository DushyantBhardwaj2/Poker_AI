import React, { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { 
  startGame, 
  processAction, 
  showdown, 
  analyzeFull,
  getAllStats, 
  type GameState, 
  type ActionType, 
  type Card,
  type ActionRecord,
  type FullAnalysisResponse
} from '../lib/api';
import { SetupView } from './SetupView';
import { CardInputView } from './CardInputView';
import { CommunityCardsInput } from './CommunityCardsInput';
import { ActionTracker } from './ActionTracker';
import { AIDashboard } from './AIDashboard';
import { ShowdownLogicView } from './ShowdownLogicView';

type GameView = 'setup' | 'cards' | 'tracker';

export default function PokerTable() {
  const [gameView, setGameView] = useState<GameView>('setup');
  const [theoryMode, setTheoryMode] = useState(true);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [actionHistory, setActionHistory] = useState<ActionRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [playerStats, setPlayerStats] = useState<Record<string, any>>({});
  
  // Setup State
  const [playerNames, setPlayerNames] = useState<string[]>(['You', 'Player 2', 'Player 3']);
  const [initialStack, setInitialStack] = useState(1000);
  const [bigBlind, setBigBlind] = useState(20);

  // Card Selection State
  const [selectedCards, setSelectedCards] = useState<Card[]>([]);
  const [pickingFor, setPickingFor] = useState<'hole' | 'community'>('hole');

  // AI State
  const [fullAnalysis, setFullAnalysis] = useState<FullAnalysisResponse | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  // Showdown State
  const [showdownResult, setShowdownResult] = useState<any>(null);
  const [pickingWinner, setPickingWinner] = useState(false);

  useEffect(() => {
    // Initial sync
    const savedMode = localStorage.getItem('poker_theory_mode');
    if (savedMode !== null) {
      setTheoryMode(savedMode === 'true');
    }

    // Listen for changes from Sidebar
    const handleTheoryChange = (e: any) => {
      setTheoryMode(e.detail.theoryMode);
    };
    window.addEventListener('poker_theory_mode_change', handleTheoryChange as EventListener);
    return () => window.removeEventListener('poker_theory_mode_change', handleTheoryChange as EventListener);
  }, []);

  const fetchStats = async () => {
    try {
      const stats = await getAllStats();
      setPlayerStats(stats);
    } catch (e) { 
      console.error("Failed to fetch stats:", e); 
    }
  };

  useEffect(() => { 
    fetchStats(); 
  }, []);

  // Reset AI when turn/round changes
  useEffect(() => {
    setFullAnalysis(null);
  }, [gameState?.current_player_index, gameState?.round]);

  // Auto-prompt community cards when round advances
  useEffect(() => {
    if (!gameState) return;
    
    const round = gameState.round;
    const cardsCount = gameState.community_cards.length;

    if (round === 'flop' && cardsCount < 3) {
      setPickingFor('community');
      setSelectedCards(gameState.community_cards);
      setGameView('cards');
    } else if (round === 'turn' && cardsCount < 4) {
      setPickingFor('community');
      setSelectedCards(gameState.community_cards);
      setGameView('cards');
    } else if (round === 'river' && cardsCount < 5) {
      setPickingFor('community');
      setSelectedCards(gameState.community_cards);
      setGameView('cards');
    }
  }, [gameState?.round]);

  // Auto-run AI on User's Turn
  useEffect(() => {
    if (gameState && gameState.current_player_index === 0 && !fullAnalysis && !aiLoading && gameView === 'tracker') {
      askAi();
    }
  }, [gameState?.current_player_index, gameState?.round, gameView, actionHistory]);

  const initGame = async (isNextHand = false) => {
    setLoading(true);
    setError(null);
    setShowdownResult(null);
    setActionHistory([]);
    try {
      let names = playerNames.map(n => n.trim() || 'Unknown');
      let stacks = Array.from({ length: names.length }, () => initialStack);
      let dIdx = 0;

      if (isNextHand && gameState) {
        names = gameState.players.map(p => p.name);
        stacks = gameState.players.map(p => p.stack);
        dIdx = (gameState.dealer_index + 1) % gameState.players.length;
      }

      const state = await startGame(names, stacks, bigBlind / 2, bigBlind, dIdx);
      setGameState(state);
      setPickingFor('hole');
      setSelectedCards([]);
      setGameView('cards');
    } catch (err: any) {
      setError(err.message || "Failed to start session. Verify API connectivity.");
    } finally {
      setLoading(false);
    }
  };

  const handleCardSelect = (card: Card) => {
    if (selectedCards.some(c => c.rank === card.rank && c.suit === card.suit)) {
      setSelectedCards(selectedCards.filter(c => !(c.rank === card.rank && c.suit === card.suit)));
      return;
    }

    if (pickingFor === 'hole' && selectedCards.length < 2) {
      setSelectedCards([...selectedCards, card]);
    } else if (pickingFor === 'community' && gameState) {
      const round = gameState.round;
      let maxAllowed = 0;
      
      if (round === 'flop') maxAllowed = 3;
      else if (round === 'turn') maxAllowed = 4;
      else if (round === 'river') maxAllowed = 5;

      if (selectedCards.length < maxAllowed) {
        setSelectedCards([...selectedCards, card]);
      }
    }
  };

  const confirmCards = () => {
    if (!gameState) return;
    const newState = { ...gameState };
    if (pickingFor === 'hole') {
      if (selectedCards.length !== 2) return;
      newState.players[0].hole_cards = selectedCards;
      setSelectedCards([]);
      setGameView('tracker');
    } else {
      const round = gameState.round;
      const count = selectedCards.length;
      
      if (round === 'flop' && count !== 3) return;
      if (round === 'turn' && count !== 4) return;
      if (round === 'river' && count !== 5) return;

      newState.community_cards = selectedCards;
      setGameView('tracker');
    }
    setGameState(newState);
  };

  const handleAction = async (type: ActionType, amount: number = 0) => {
    if (!gameState) return;
    setLoading(true);
    setError(null);
    try {
      // Track history locally for AI analysis
      const actingPlayer = gameState.players[gameState.current_player_index];
      const newAction: ActionRecord = {
        player_name: actingPlayer.name,
        action_type: type,
        amount: amount,
        street: gameState.round
      };

      const newState = await processAction(gameState, {
        player_index: gameState.current_player_index,
        action_type: type,
        amount
      });
      
      setGameState(newState);
      setActionHistory(prev => [...prev, newAction]);
      
      const activePlayers = newState.players.filter(p => !p.is_folded);
      if (newState.round === 'showdown') {
        if (activePlayers.length === 1) {
          // Everyone else folded, auto-resolve without picking winners
          handleShowdown([]);
        } else {
          setPickingWinner(true);
        }
      }
    } catch (err: any) {
      setError(err.message || "Action rejected. Check game rules.");
    } finally {
      setLoading(false);
    }
  };

  const handleRefillStack = (playerIndex: number, amount: number) => {
    if (!gameState) return;
    const newState = { ...gameState };
    newState.players[playerIndex].stack += amount;
    setGameState(newState);
  };

  const handleUpdatePlayerStatus = (playerIndex: number, status: PlayerStatus) => {
    if (!gameState) return;
    const newState = { ...gameState };
    const p = newState.players[playerIndex];
    
    // Toggle sitting out
    if (status === 'sitting-out') {
      p.status = p.status === 'sitting-out' ? 'active' : 'sitting-out';
    } else {
      p.status = status;
    }
    
    // If it was the current player's turn and they sat out, advance turn
    if (newState.current_player_index === playerIndex && p.status === 'sitting-out') {
       // Need to find next active player
       let nextIdx = (playerIndex + 1) % newState.players.length;
       let loops = 0;
       while (newState.players[nextIdx].status !== 'active' && loops < newState.players.length) {
         nextIdx = (nextIdx + 1) % newState.players.length;
         loops++;
       }
       newState.current_player_index = nextIdx;
    }

    setGameState(newState);
  };

  const handleRemovePlayer = (playerIndex: number) => {
    if (!gameState || gameState.players.length <= 2) {
      setError("Cannot have fewer than 2 players.");
      return;
    }
    const newState = { ...gameState };
    newState.players.splice(playerIndex, 1);
    
    // Adjust indices
    if (newState.current_player_index >= playerIndex) {
      newState.current_player_index = Math.max(0, newState.current_player_index - 1);
    }
    if (newState.dealer_index >= playerIndex) {
      newState.dealer_index = Math.max(0, newState.dealer_index - 1);
    }

    setGameState(newState);
  };

  const handleShowdown = async (playerHands: { playerIndex: number; cards: Card[] }[], blufferNames: string[] = []) => {
    if (!gameState) return;
    setLoading(true);
    try {
      const stateWithReveals = { ...gameState };
      playerHands.forEach(ph => {
        stateWithReveals.players[ph.playerIndex].hole_cards = ph.cards;
      });

      const res = await showdown(stateWithReveals, blufferNames); 
      
      const winnersMap = new Map<string, number>();
      if ((res as any).result && Array.isArray((res as any).result.pots_results)) {
        (res as any).result.pots_results.forEach((potRes: any) => {
          const winAmount = potRes.amount / potRes.winners.length;
          potRes.winners.forEach((w: string) => {
            winnersMap.set(w, (winnersMap.get(w) || 0) + winAmount);
          });
        });
      }

      const mappedWinners = Array.from(winnersMap.entries()).map(([name, amount]) => ({ name, amount }));

      const manualResult = {
        winners: mappedWinners,
        pots_results: (res as any).result.pots_results
      };
      
      setShowdownResult(manualResult);
      setGameState(res.new_state);
      setPickingWinner(false);
      setActionHistory([]); // Reset history for new hand
      await fetchStats(); 
    } catch (err: any) {
      setError("Failed to finalize hand: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const askAi = async () => {
    if (!gameState) return;
    const me = gameState.players[0];
    if (me.hole_cards.length !== 2) {
      setError("Hole cards missing. Input your cards to enable AI analysis.");
      return;
    }

    setAiLoading(true);
    try {
      // Find the last acting opponent to analyze for bluffing
      // If no history, analyze the second player (default)
      const opponentName = actionHistory.length > 0 
        ? actionHistory[actionHistory.length - 1].player_name 
        : (gameState.players.length > 1 ? gameState.players[1].name : "Unknown");

      const analysis = await analyzeFull(
        gameState,
        actionHistory,
        opponentName,
        me.hole_cards,
        1000 // simulations
      );
      
      setFullAnalysis(analysis);
    } catch (err: any) {
      setError("AI Engine Error: " + (err.message || "Processing failure"));
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="w-full animate-fade-in flex flex-col items-center">
      {error && (
        <div className="max-w-md w-full mb-8 glass-dark border border-red-500/20 text-red-400 p-5 rounded-2xl flex items-start gap-4 animate-slide-up relative z-50">
          <AlertCircle size={24} className="mt-0.5 shrink-0" />
          <div className="space-y-1">
            <h4 className="font-black text-[10px] uppercase tracking-widest text-red-500/80">System Alert</h4>
            <p className="text-sm font-medium leading-relaxed">{error}</p>
            <button 
              onClick={() => setError(null)} 
              className="mt-3 text-[10px] font-black uppercase tracking-widest bg-red-500/10 hover:bg-red-500/20 text-red-400 px-4 py-2 rounded-lg border border-red-500/20 transition-all active:scale-95"
            >
              Dismiss Alert
            </button>

          </div>
        </div>
      )}

      {pickingWinner && gameState ? (
        <div className="flex justify-center w-full">
          <ShowdownLogicView gameState={gameState} onFinalize={handleShowdown} />
        </div>
      ) : (
        <>
          {gameView === 'setup' && (
            <SetupView 
              playerNames={playerNames} setPlayerNames={setPlayerNames}
              initialStack={initialStack} setInitialStack={setInitialStack}
              bigBlind={bigBlind} setBigBlind={setBigBlind}
              loading={loading} onStart={initGame}
            />
          )}

          {gameView === 'cards' && (
            pickingFor === 'community' && gameState ? (
              <CommunityCardsInput 
                round={gameState.round}
                existingCards={gameState.community_cards}
                holeCards={gameState.players[0]?.hole_cards || []}
                onConfirm={(cards) => {
                  const newState = { ...gameState };
                  newState.community_cards = cards;
                  setGameState(newState);
                  setGameView('tracker');
                }}
              />
            ) : (
              <CardInputView 
                pickingFor={pickingFor} selectedCards={selectedCards}
                onCardSelect={handleCardSelect} onConfirm={confirmCards}
                onReset={() => setSelectedCards([])} round={gameState?.round}
                takenCards={gameState?.community_cards || []}
              />
            )
          )}

          {gameView === 'tracker' && gameState && (
            <div className="w-full flex flex-col lg:flex-row gap-10">
              <ActionTracker 
                gameState={gameState} onAction={handleAction}
                onRefillStack={handleRefillStack}
                onOpenCardInput={() => {
                  setPickingFor('community');
                  setSelectedCards(gameState.community_cards);
                  setGameView('cards');
                }}
                onUpdatePlayerStatus={handleUpdatePlayerStatus}
                onRemovePlayer={handleRemovePlayer}
              />
              <AIDashboard 
                fullAnalysis={fullAnalysis} loading={aiLoading} 
                onRunAnalysis={askAi}
                showdownResult={showdownResult} playerStats={playerStats}
                onNewHand={initGame} theoryMode={theoryMode}
                userName={playerNames[0]}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
