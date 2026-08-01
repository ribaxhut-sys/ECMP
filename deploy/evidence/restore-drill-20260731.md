# Restore drill — 2026-07-31 (non-destructive)

## Method
1. Source dump: `ecmp_20260731T085345Z.sql.gz`
2. Created temporary DB `ecmp_restore_drill` (owner `ecmp`)
3. Restored via `gunzip -c | psql -d ecmp_restore_drill`
4. Verified row counts, then **dropped** temp DB
5. Live DB `ecmp` untouched

## Result
- **PASS** — restore completed with `ON_ERROR_STOP`
- Spot checks: users / complaints / branches / customers present (see session log)
- Live app health after drill: verified separately

## Notes
Full cutover restore onto live `ecmp` was intentionally skipped to avoid downtime.
