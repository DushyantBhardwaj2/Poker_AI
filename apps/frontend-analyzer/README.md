# PokerSense Frontend Analyzer

Playwright-based automated frontend analysis tool for PokerSense AI.

## Setup

```bash
npm install
npm run install-browsers
```

## Usage

1. Start the frontend: `cd ../web && npm run dev`
2. Run analysis: `npm run analyze`
3. View report: `cat reports/analysis_report.json`

## Test Suites

| File | What it tests |
|------|--------------|
| `ui-flow.spec.ts` | Navigation, dead links, page transitions |
| `components.spec.ts` | Component rendering and presence |
| `responsive.spec.ts` | Viewports: 320px, 768px, 1024px, 1440px |
| `runtime.spec.ts` | Console errors, failed API calls |
| `state.spec.ts` | Setup → Cards → Game state transitions |

## Report Structure

```json
{
  "flowIssues": [],
  "componentIssues": [],
  "responsiveIssues": [],
  "runtimeErrors": [],
  "stateIssues": [],
  "summary": { "overallStatus": "healthy" }
}
```
