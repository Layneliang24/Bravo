#!/usr/bin/env node
// Coverage verification script - ANTI-CHEATING
// This script verifies that coverage thresholds are actually met

const fs = require('fs');
const path = require('path');

// Configuration
const COVERAGE_THRESHOLDS = {
  global: {
    branches: 90,
    functions: 90,
    lines: 90,
    statements: 90
  }
};

const COVERAGE_DIR = path.join(__dirname, '../coverage');
const COVERAGE_SUMMARY_FILE = path.join(COVERAGE_DIR, 'coverage-summary.json');

function verifyCoverage() {
  console.log('🔍 ANTI-CHEATING: Verifying coverage thresholds...');
  
  // Check if coverage directory exists
  if (!fs.existsSync(COVERAGE_DIR)) {
    console.error('❌ Coverage directory not found. Tests may not have run properly.');
    process.exit(1);
  }
  
  // Check if coverage summary exists
  if (!fs.existsSync(COVERAGE_SUMMARY_FILE)) {
    console.error('❌ Coverage summary file not found. Coverage may not have been collected.');
    process.exit(1);
  }
  
  // Read coverage summary
  let coverageSummary;
  try {
    const summaryContent = fs.readFileSync(COVERAGE_SUMMARY_FILE, 'utf8');
    coverageSummary = JSON.parse(summaryContent);
  } catch (error) {
    console.error('❌ Failed to parse coverage summary:', error.message);
    process.exit(1);
  }
  
  // Extract total coverage
  const totalCoverage = coverageSummary.total;
  if (!totalCoverage) {
    console.error('❌ No total coverage data found in summary.');
    process.exit(1);
  }
  
  console.log('📊 Coverage Summary:');
  console.log(`   Lines: ${totalCoverage.lines.pct}%`);
  console.log(`   Statements: ${totalCoverage.statements.pct}%`);
  console.log(`   Functions: ${totalCoverage.functions.pct}%`);
  console.log(`   Branches: ${totalCoverage.branches.pct}%`);
  
  // Check thresholds
  const failures = [];
  
  if (totalCoverage.lines.pct < COVERAGE_THRESHOLDS.global.lines) {
    failures.push(`Lines: ${totalCoverage.lines.pct}% < ${COVERAGE_THRESHOLDS.global.lines}%`);
  }
  
  if (totalCoverage.statements.pct < COVERAGE_THRESHOLDS.global.statements) {
    failures.push(`Statements: ${totalCoverage.statements.pct}% < ${COVERAGE_THRESHOLDS.global.statements}%`);
  }
  
  if (totalCoverage.functions.pct < COVERAGE_THRESHOLDS.global.functions) {
    failures.push(`Functions: ${totalCoverage.functions.pct}% < ${COVERAGE_THRESHOLDS.global.functions}%`);
  }
  
  if (totalCoverage.branches.pct < COVERAGE_THRESHOLDS.global.branches) {
    failures.push(`Branches: ${totalCoverage.branches.pct}% < ${COVERAGE_THRESHOLDS.global.branches}%`);
  }
  
  if (failures.length > 0) {
    console.error('❌ COVERAGE THRESHOLD FAILURES:');
    failures.forEach(failure => console.error(`   ${failure}`));
    console.error('');
    console.error('🚫 Build failed due to insufficient coverage.');
    console.error('💡 Increase test coverage or adjust thresholds in jest.config.coverage.js');
    process.exit(1);
  }
  
  // Additional integrity checks
  const fileCount = Object.keys(coverageSummary).length - 1; // -1 for 'total' key
  if (fileCount < 5) {
    console.warn(`⚠️  Warning: Only ${fileCount} files in coverage report. This seems low.`);
  }
  
  // Check for suspicious patterns
  const suspiciousFiles = [];
  Object.entries(coverageSummary).forEach(([file, data]) => {
    if (file === 'total') return;
    
    // Check for 100% coverage on all metrics (suspicious)
    if (data.lines.pct === 100 && data.statements.pct === 100 && 
        data.functions.pct === 100 && data.branches.pct === 100) {
      suspiciousFiles.push(file);
    }
  });
  
  if (suspiciousFiles.length > fileCount * 0.8) {
    console.warn('⚠️  Warning: High percentage of files with 100% coverage. Please verify test quality.');
  }
  
  console.log('✅ All coverage thresholds met!');
  console.log(`📁 Coverage collected for ${fileCount} files`);
  console.log('🔒 ANTI-CHEATING: Coverage verification passed');
  
  return true;
}

// Export for use in other scripts
module.exports = { verifyCoverage, COVERAGE_THRESHOLDS };

// Run if called directly
if (require.main === module) {
  verifyCoverage();
}