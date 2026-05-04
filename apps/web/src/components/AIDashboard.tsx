import React from 'react';
import { AdvisorHUD } from './AdvisorHUD';
import { PlayerStats } from './PlayerStats';
import { PostHandAnalysis } from './PostHandAnalysis';
import type { FullAnalysisResponse } from '../types/poker';

interface AIDashboardProps {
  fullAnalysis: FullAnalysisResponse | null;
  loading: boolean;
  onRunAnalysis: () => void;
  showdownResult: any;
  playerStats: Record<string, any>;
  onNewHand: (isNextHand?: boolean) => void;
  theoryMode?: boolean;
}

export function AIDashboard({
  fullAnalysis,
  loading,
  onRunAnalysis,
  showdownResult,
  playerStats,
  onNewHand,
  theoryMode,
  userName = 'You'
}: AIDashboardProps & { userName?: string }) {
  
  return (
    <div className="flex-1 max-w-sm flex flex-col gap-6">
      {showdownResult ? (
        <PostHandAnalysis 
          showdownResult={showdownResult}
          onNewHand={() => onNewHand(true)}
          userName={userName}
        />
      ) : (
        <>
          {/* Unified AI Tactical HUD */}
          <AdvisorHUD 
            analysis={fullAnalysis}
            loading={loading}
            onRefresh={onRunAnalysis}
          />

          {/* Legacy Player Behavior Panel (Fallback/Extra) */}
          {Object.keys(playerStats).length > 0 && (
            <PlayerStats 
              stats={playerStats}
            />
          )}
        </>
      )}
    </div>
  );
}
