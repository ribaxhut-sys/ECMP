-- Cleanup only — calon TIDAK di-insert; admin mendaftarkan.
BEGIN;
DELETE FROM user_roles WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@lab.ecmp.local'
);
DELETE FROM refresh_tokens WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@lab.ecmp.local'
);
DELETE FROM password_reset_tokens WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@lab.ecmp.local'
);
DELETE FROM users WHERE email LIKE '%@lab.ecmp.local';
COMMIT;
