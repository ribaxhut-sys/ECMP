-- ECMP lab master-data seed (idempotent-ish)
-- Usage:
--   docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
--     exec -T postgres psql -U ecmp -d ecmp < deploy/seed-lab-master-data.sql
--
-- Then create AGENT/SUPERVISOR via API (or extend this script) and activate SLA is included below.

INSERT INTO branches (code, name, address, city, is_active)
VALUES ('JKT-01', 'Cabang Jakarta Pusat', 'Jl. Lab ECMP No. 1', 'Jakarta', true)
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name, address = EXCLUDED.address, city = EXCLUDED.city,
    is_active = true, updated_at = now();

INSERT INTO customers (external_customer_id, full_name, email, phone)
VALUES ('CUST-LAB-001', 'Pelanggan Lab Demo', 'pelanggan.lab@example.com', '081234567890')
ON CONFLICT (external_customer_id) DO UPDATE
SET full_name = EXCLUDED.full_name, email = EXCLUDED.email, phone = EXCLUDED.phone,
    updated_at = now();

-- Exactly one active SLA policy (partial unique index)
UPDATE sla_policies SET is_active = false, updated_at = now() WHERE is_active = true;

INSERT INTO sla_policies (
  name, description,
  assignment_target_minutes, appointment_target_minutes, resolution_target_minutes,
  escalation_target_minutes, overall_target_minutes, is_active
)
SELECT
  'Lab Default SLA',
  'Seeded lab policy for shared HTTPS environment',
  60, 1440, 2880, 480, 4320, true
WHERE NOT EXISTS (SELECT 1 FROM sla_policies WHERE name = 'Lab Default SLA');

UPDATE sla_policies
SET is_active = true, updated_at = now()
WHERE name = 'Lab Default SLA';

UPDATE sla_policies
SET is_active = false, updated_at = now()
WHERE name <> 'Lab Default SLA' AND is_active = true;

-- After creating users via API, ensure junction rows exist
-- (API create sets users.role_id but PermissionResolver reads user_roles):
--   INSERT INTO user_roles (user_id, role_id)
--   SELECT id, role_id FROM users u
--   WHERE username IN ('agent1','supervisor1')
--   ON CONFLICT (user_id, role_id) DO NOTHING;
-- Then restart backend (or invalidate permission cache) before assign/escalate.
