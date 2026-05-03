#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const rawResultsPath = path.join(__dirname, '../reports/raw-results.json');
const outputPath = path.join(__dirname, '../reports/analysis_report.json');

function severityFromTitle(title) {
  const t = title.toLowerCase();
  if (t.includes('error') || t.includes('crash') || t.includes('broken') || t.includes('js error')) return 'critical';
  if (t.includes('navigation') || t.includes('state') || t.includes('transition')) return 'medium';
  return 'low';
}

function categorizeTest(title, suiteName) {
  const s = (suiteName || '').toLowerCase();
  const t = (title || '').toLowerCase();
  if (s.includes('flow') || t.includes('navigation') || t.includes('navigate') || t.includes('link')) return 'flowIssues';
  if (s.includes('component') || t.includes('render') || t.includes('component') || t.includes('form')) return 'componentIssues';
  if (s.includes('responsive') || t.includes('viewport') || t.includes('overflow') || t.includes('mobile')) return 'responsiveIssues';
  if (s.includes('runtime') || t.includes('error') || t.includes('console') || t.includes('api')) return 'runtimeErrors';
  if (s.includes('state') || t.includes('state') || t.includes('transition')) return 'stateIssues';
  return 'componentIssues';
}

let rawData = { suites: [] };
if (fs.existsSync(rawResultsPath)) {
  try {
    rawData = JSON.parse(fs.readFileSync(rawResultsPath, 'utf-8'));
  } catch (e) {
    console.error('Could not parse raw results:', e.message);
  }
}

const report = {
  generatedAt: new Date().toISOString(),
  frontendUrl: 'http://localhost:4321',
  flowIssues: [],
  componentIssues: [],
  responsiveIssues: [],
  runtimeErrors: [],
  stateIssues: [],
  summary: {
    totalTests: 0,
    passed: 0,
    failed: 0,
    skipped: 0,
    criticalIssues: 0,
    mediumIssues: 0,
    lowIssues: 0,
    overallStatus: 'unknown',
  },
};

function processSuiteNode(node, suiteName) {
  // Process specs (leaf nodes containing test results)
  for (const spec of (node.specs || [])) {
    const title = spec.title || '';
    for (const test of (spec.tests || [])) {
      report.summary.totalTests++;
      const status = test.results?.[0]?.status ?? 'skipped';
      if (status === 'passed') report.summary.passed++;
      else if (status === 'skipped') report.summary.skipped++;
      else {
        report.summary.failed++;
        const category = categorizeTest(title, suiteName);
        const severity = severityFromTitle(title);
        if (severity === 'critical') report.summary.criticalIssues++;
        else if (severity === 'medium') report.summary.mediumIssues++;
        else report.summary.lowIssues++;

        const error = test.results?.[0]?.error?.message ?? 'Test failed';
        report[category].push({
          test: title,
          suite: suiteName,
          severity,
          error: error.substring(0, 300),
          status,
        });
      }
    }
  }
  // Recurse into nested suites
  for (const child of (node.suites || [])) {
    processSuiteNode(child, child.title || suiteName);
  }
}

for (const suite of (rawData.suites || [])) {
  processSuiteNode(suite, suite.title);
}

report.summary.overallStatus =
  report.summary.criticalIssues > 0 ? 'critical' :
  report.summary.mediumIssues > 0 ? 'warning' :
  report.summary.failed > 0 ? 'minor-issues' : 'healthy';

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
console.log('\n📊 Analysis Report Generated');
console.log(`   Total Tests: ${report.summary.totalTests}`);
console.log(`   ✅ Passed: ${report.summary.passed}`);
console.log(`   ❌ Failed: ${report.summary.failed}`);
console.log(`   Overall Status: ${report.summary.overallStatus.toUpperCase()}`);
console.log(`   Report: ${outputPath}\n`);
