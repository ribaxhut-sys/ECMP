/**
 * Bundle-size budget reporter (Sprint-10 RC1, P1 — warning mode).
 *
 * Compares production dist/ JS assets against budgets. Exits 1 when over budget
 * so CI can surface a warning via continue-on-error without blocking merge.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { gzipSync } from 'node:zlib'
import { join } from 'node:path'

const DIST = join(process.cwd(), 'dist', 'assets')

/** Soft budgets (bytes). Headroom above 2026-07-22 measured baseline. */
const BUDGET = {
  entryJsRaw: 280_000, // index-*.js ~245 KB
  entryJsGzip: 100_000, // ~80 KB gzip
  totalJsRaw: 320_000,
  totalJsGzip: 120_000,
}

function listJsAssets() {
  return readdirSync(DIST)
    .filter((name) => name.endsWith('.js'))
    .map((name) => {
      const path = join(DIST, name)
      const raw = readFileSync(path)
      return {
        name,
        raw: statSync(path).size,
        gzip: gzipSync(raw).length,
      }
    })
}

const assets = listJsAssets()
const entry = assets.find((a) => a.name.startsWith('index-'))
if (!entry) {
  console.error('Bundle budget: no index-*.js found under dist/assets — run build first.')
  process.exit(1)
}

const totalRaw = assets.reduce((sum, a) => sum + a.raw, 0)
const totalGzip = assets.reduce((sum, a) => sum + a.gzip, 0)

const checks = [
  ['entry JS raw', entry.raw, BUDGET.entryJsRaw],
  ['entry JS gzip', entry.gzip, BUDGET.entryJsGzip],
  ['total JS raw', totalRaw, BUDGET.totalJsRaw],
  ['total JS gzip', totalGzip, BUDGET.totalJsGzip],
]

console.log('Bundle size report')
console.log(`  entry: ${entry.name}  raw=${entry.raw}  gzip=${entry.gzip}`)
for (const a of assets) {
  console.log(`  ${a.name}  raw=${a.raw}  gzip=${a.gzip}`)
}

let over = false
for (const [label, actual, limit] of checks) {
  const status = actual <= limit ? 'OK' : 'OVER'
  if (status === 'OVER') over = true
  const line = `  [${status}] ${label}: ${actual} / budget ${limit}`
  console.log(line)
  if (status === 'OVER' && process.env.GITHUB_ACTIONS === 'true') {
    console.log(`::warning title=Bundle budget::${label} ${actual} exceeds budget ${limit}`)
  }
}

if (over) {
  console.error('Bundle budget exceeded (warning-mode gate; CI continue-on-error).')
  process.exit(1)
}

console.log('Bundle budget: all checks within soft limits.')
process.exit(0)
