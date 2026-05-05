# Graph Report - Poker_AI  (2026-05-05)

## Corpus Check
- 131 files · ~108,075 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 508 nodes · 942 edges · 87 communities (75 shown, 12 thin omitted)
- Extraction: 53% EXTRACTED · 47% INFERRED · 0% AMBIGUOUS · INFERRED: 444 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e1aacf0a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]

## God Nodes (most connected - your core abstractions)
1. `Card` - 47 edges
2. `StatsRepository` - 36 edges
3. `GameState` - 29 edges
4. `ProcessActionUseCase` - 26 edges
5. `get_data_path()` - 26 edges
6. `Player` - 24 edges
7. `StartGameUseCase` - 22 edges
8. `ShowdownUseCase` - 21 edges
9. `ActionRecord` - 21 edges
10. `ActionType` - 19 edges

## Surprising Connections (you probably didn't know these)
- `ShowdownUseCase` --uses--> `HandValue`  [INFERRED]
  apps/api/application/showdown.py → packages/domain/hand_evaluator.py
- `StartGameUseCase` --uses--> `Deck`  [INFERRED]
  apps/api/application/start_game.py → packages/domain/deck.py
- `test_start_game_use_case()` --calls--> `StartGameUseCase`  [INFERRED]
  tests/unit/test_use_cases.py → apps/api/application/start_game.py
- `WinProbRequest` --uses--> `Card`  [INFERRED]
  apps/api/interfaces/ai_controller.py → packages/domain/models.py
- `WinProbRequest` --uses--> `GameState`  [INFERRED]
  apps/api/interfaces/ai_controller.py → packages/domain/models.py

## Communities (87 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (36): BluffDetector, Real-time bluff detector using the trained XGBoost v3 model., FeatureMapper, map_to_live_state(), MoveRecommender, OpponentProfiler, Advanced recommendation engine that synthesizes mathematical probability     an, SmartAdvisor (+28 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (36): ProcessActionUseCase, ShowdownUseCase, StartGameUseCase, BaseModel, HandEvaluator, Action, ActionType, GameRound (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (34): engineer_features_v2(), generate_labels_v2(), train_model_v2(), analyze_by_street(), analyze_pr(), check_stats(), check_feature_alignment(), check_corr() (+26 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (6): calculate(), Deck, Card, TestHandEvaluator, test_card_creation(), TestWinProbability

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (13): askAi(), fetchStats(), handleAction(), handleShowdown(), initGame(), analyzeFull(), getAllStats(), getHeaders() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (11): IdentityVerifier, main(), Cross-File Identity Verification  Verifies that player identities are consiste, Recursively verify identity consistency across subdirectories., Generate a summary report of identity verification.                  Returns:, Main verification flow., Verifies player identity consistency across PHH files., Initialize the verifier. (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (10): DataQualityValidator, Check that action sequences are consistent and logically valid., Validate consistency across dataset strata.                  Checks:, Extract data source from hand_id., Run all validation checks.                  Returns:             Dictionary w, Generate validation report., Validates parsed poker data quality., Initialize validator with parsed data. (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.15
Nodes (11): main(), Stratified Sampling for Batch Parsing  Creates a stratified 1-5% sample of PHH, Create a stratified random sample.                  Samples `percentage` of fi, Generate a sample list file for batch processing.                  Args:, Main sampling workflow., Creates stratified samples of PHH files., Initialize the sampler., Extract dataset source from file path. (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.18
Nodes (5): Calculates features and returns bluff probability., int, PHHParser, PHH (Poker Hand History) Parser & Loader  Parses poker hand history files usin, Parses Poker Hand History files using pokerkit.

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (11): calculate_dryness(), Calculate a simple dryness score for the board.     1.0 = Very Dry, 0.0 = Very, get_hand_strength(), main(), Simulates a full game path via stateless API endpoints:     Start -> Pre-flop A, test_complete_game_path(), try_connect(), get_move_recommendation() (+3 more)

### Community 11 - "Community 11"
Cohesion: 0.2
Nodes (9): BatchParsingOrchestrator, main(), Batch Parsing Orchestrator  Orchestrates parsing of sampled PHH files with: -, Validate parsed data quality.                  Checks:         - All required, Generate parsing and validation report., Save parsed data and reports., Main orchestration workflow., Orchestrates batch parsing of PHH files. (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (4): AggressiveStatCollector, Aggressive Player Stat Collector Processes a large number of handhq files to ge, Entry point for the pipeline., run_profiling()

### Community 13 - "Community 13"
Cohesion: 0.28
Nodes (3): evaluate_5_cards(), evaluate_7_cards(), HandValue

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (4): BluffPredictor, Returns a dictionary with probability, detection, and confidence., Calculates v3 features from a raw game state dictionary.                  stat, Inference wrapper for the PokerSense Bluff Detection model.     Handles real-ti

### Community 15 - "Community 15"
Cohesion: 0.39
Nodes (3): FullDatasetParsingOrchestrator, main(), Full Dataset Parsing Orchestrator  Parses all PHH files under `poker-hand-hist

### Community 19 - "Community 19"
Cohesion: 0.47
Nodes (4): AggressiveParser, Aggressive Dataset Parser  Parses a large subset (1000 files) of handhq data t, Entry point for the pipeline., run_ingestion()

### Community 20 - "Community 20"
Cohesion: 0.33
Nodes (3): GUID, Platform-independent GUID type.     Uses PostgreSQL's UUID type, otherwise uses, TypeDecorator

## Knowledge Gaps
- **71 isolated node(s):** `Verify that required input files exist for each step.`, `Run the ML pipeline steps.     Steps can be: 'ingest', 'validate', 'surface', '`, `Cross-File Identity Verification  Verifies that player identities are consiste`, `Verifies player identity consistency across PHH files.`, `Initialize the verifier.` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_data_path()` connect `Community 2` to `Community 10`, `Community 12`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 10` to `Community 2`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `run_validation()` connect `Community 2` to `Community 7`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Card` (e.g. with `WinProbRequest` and `MoveRecRequest`) actually correct?**
  _`Card` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `str` (e.g. with `get_bluff_detector()` and `get_win_probability()`) actually correct?**
  _`str` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `StatsRepository` (e.g. with `WinProbRequest` and `MoveRecRequest`) actually correct?**
  _`StatsRepository` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `GameState` (e.g. with `ProcessActionUseCase` and `ShowdownUseCase`) actually correct?**
  _`GameState` has 27 INFERRED edges - model-reasoned connections that need verification._