-- Lab Mode A: ensure HQ schedule destination PUSAT-CRO exists under PUSAT.
-- Required for "Terima & jadwalkan" (destinationUnitId must resolve to an
-- active organization unit). Safe to re-run (ON CONFLICT).
--
-- Usage:
--   docker compose --env-file .env exec -T postgres \
--     psql -U ecmp -d ecmp -f - < deploy/seed-lab-pusat-cro.sql

INSERT INTO branches (id, code, name, is_active, parent_branch_id, created_at, updated_at)
SELECT gen_random_uuid(), 'PUSAT', 'Pusat', true, NULL, now(), now()
WHERE NOT EXISTS (
  SELECT 1 FROM branches WHERE UPPER(code) = 'PUSAT' AND deleted_at IS NULL
);

INSERT INTO branches (id, code, name, is_active, parent_branch_id, created_at, updated_at)
SELECT gen_random_uuid(), 'PUSAT-CRO', 'CRO Pusat', true, b.id, now(), now()
FROM branches b
WHERE UPPER(b.code) = 'PUSAT' AND b.deleted_at IS NULL
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name,
    is_active = true,
    deleted_at = NULL,
    parent_branch_id = COALESCE(branches.parent_branch_id, EXCLUDED.parent_branch_id),
    updated_at = now();
