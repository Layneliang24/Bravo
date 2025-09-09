// Coverage threshold verification - ANTI-CHEATING SETUP
// This file ensures coverage thresholds are properly enforced

const fs = require('fs')
const path = require('path')

// Global setup for coverage verification
global.beforeAll(() => {
  console.log('🔒 ANTI-CHEATING: Coverage threshold verification enabled')

  // Ensure coverage directory exists
  const coverageDir = path.join(__dirname, '../coverage')
  if (!fs.existsSync(coverageDir)) {
    fs.mkdirSync(coverageDir, { recursive: true })
  }
})

// After all tests, verify coverage was actually collected
global.afterAll(() => {
  const coverageFile = path.join(__dirname, '../coverage/coverage-final.json')

  if (process.env.CI && !fs.existsSync(coverageFile)) {
    console.error(
      '❌ ANTI-CHEATING: Coverage file not found - tests may not have run properly'
    )
    process.exit(1)
  }

  if (fs.existsSync(coverageFile)) {
    const coverage = JSON.parse(fs.readFileSync(coverageFile, 'utf8'))
    const fileCount = Object.keys(coverage).length

    if (fileCount === 0) {
      console.error(
        '❌ ANTI-CHEATING: No coverage data collected - suspicious test run'
      )
      process.exit(1)
    }

    console.log(`✅ ANTI-CHEATING: Coverage collected for ${fileCount} files`)
  }
})

// Custom matchers for coverage verification
expect.extend({
  toMeetCoverageThreshold(received, threshold) {
    const pass = received >= threshold

    if (pass) {
      return {
        message: () =>
          `Expected coverage ${received}% not to meet threshold ${threshold}%`,
        pass: true,
      }
    } else {
      return {
        message: () =>
          `Expected coverage ${received}% to meet threshold ${threshold}%`,
        pass: false,
      }
    }
  },
})

// Export verification functions
module.exports = {
  verifyCoverageIntegrity: () => {
    const coverageFile = path.join(__dirname, '../coverage/coverage-final.json')

    if (!fs.existsSync(coverageFile)) {
      throw new Error(
        'Coverage file not found - tests may not have executed properly'
      )
    }

    const coverage = JSON.parse(fs.readFileSync(coverageFile, 'utf8'))
    const summary = {
      files: Object.keys(coverage).length,
      totalLines: 0,
      coveredLines: 0,
    }

    Object.values(coverage).forEach(file => {
      if (file.s) {
        summary.totalLines += Object.keys(file.s).length
        summary.coveredLines += Object.values(file.s).filter(
          count => count > 0
        ).length
      }
    })

    const overallCoverage =
      summary.totalLines > 0
        ? (summary.coveredLines / summary.totalLines) * 100
        : 0

    console.log(
      `📊 Coverage Summary: ${overallCoverage.toFixed(2)}% (${
        summary.coveredLines
      }/${summary.totalLines} lines)`
    )

    return {
      ...summary,
      overallCoverage,
    }
  },
}
