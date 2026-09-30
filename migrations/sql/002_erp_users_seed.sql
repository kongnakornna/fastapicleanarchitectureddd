-- ============================================================================
-- ERP-IOT · Seed data for erp_users
-- Run AFTER 001_erp_users_full.sql
-- NOTE: replace the fake argon2 hashes below with real ones from
--       `python -c "from app.core.security import hash_password; \
--        print(hash_password('Admin@1234'))"`
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Admin / superuser  (password: Admin@1234)
-- ----------------------------------------------------------------------------
INSERT INTO erp_users (
    first_name, last_name, preferred_name, full_name, nickname,
    username, email, phone, mobile_number, line_id, id_card,
    gender, birthdate,
    hashed_password, temporary_password,
    role, status, online_status, active_status,
    network_id, network_type_id, type_id, system_id, location_id,
    is_verified, is_superuser, login_failed_count, last_sign_in_at,
    public_notification, sms_notification, email_notification, line_notification,
    public_status, information_agreement_status, is_active
) VALUES (
    'System', 'Admin', 'Sys', 'System Admin', 'sys',
    'admin', 'admin@example.com', '+555100000001', '+555100000001', 'line_admin', '0000000000001',
    'MALE', '1985-03-15',
    '$argon2id$v=19$m=65536,t=3,p=4$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH',
    NULL,
    'ADMIN', 'ACTIVE', 'OFFLINE', 1,
    1, 0, 0, '1', '1',
    TRUE, TRUE, 0, NOW(),
    1, 1, 1, 1,
    0, 1, TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. Regular user  (password: User@1234)
-- ----------------------------------------------------------------------------
INSERT INTO erp_users (
    first_name, last_name, preferred_name, full_name, nickname,
    username, email, phone, mobile_number, line_id, id_card,
    gender, birthdate,
    hashed_password, temporary_password,
    role, status, online_status, active_status,
    network_id, network_type_id, type_id, system_id, location_id,
    is_verified, is_superuser, login_failed_count, last_sign_in_at,
    public_notification, sms_notification, email_notification, line_notification,
    public_status, information_agreement_status, is_active
) VALUES (
    'John', 'Doe', 'Johnny', 'John Doe', 'JD',
    'johndoe', 'johndoe@example.com', '+555472664275', '+555472664275', 'line_john', '0000000000002',
    'MALE', '1990-07-22',
    '$argon2id$v=19$m=65536,t=3,p=4$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH',
    NULL,
    'USER', 'ACTIVE', 'OFFLINE', 1,
    1, 0, 0, '1', '1',
    TRUE, FALSE, 0, NOW() - INTERVAL '2 hours',
    1, 0, 1, 0,
    1, 1, TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. Regular user (female)  (password: User@1234)
-- ----------------------------------------------------------------------------
INSERT INTO erp_users (
    first_name, last_name, preferred_name, full_name, nickname,
    username, email, phone, mobile_number, line_id, id_card,
    gender, birthdate,
    hashed_password, temporary_password,
    role, status, online_status, active_status,
    network_id, network_type_id, type_id, system_id, location_id,
    is_verified, is_superuser, login_failed_count, last_sign_in_at,
    public_notification, sms_notification, email_notification, line_notification,
    public_status, information_agreement_status, is_active
) VALUES (
    'Jane', 'Smith', 'Janie', 'Jane Smith', 'JS',
    'janesmith', 'jane.smith@example.com', '+555100000003', '+555100000003', NULL, NULL,
    'FEMALE', '1992-11-08',
    '$argon2id$v=19$m=65536,t=3,p=4$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH',
    NULL,
    'USER', 'ACTIVE', 'ONLINE', 1,
    1, 0, 0, '1', '1',
    TRUE, FALSE, 0, NOW() - INTERVAL '10 minutes',
    1, 1, 1, 1,
    1, 1, TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. Guest user  (password: Guest@1234)
-- ----------------------------------------------------------------------------
INSERT INTO erp_users (
    first_name, last_name, preferred_name, full_name, nickname,
    username, email, phone, mobile_number, line_id, id_card,
    gender, birthdate,
    hashed_password, temporary_password,
    role, status, online_status, active_status,
    network_id, network_type_id, type_id, system_id, location_id,
    is_verified, is_superuser, login_failed_count, last_sign_in_at,
    public_notification, sms_notification, email_notification, line_notification,
    public_status, information_agreement_status, is_active
) VALUES (
    'Guest', 'User', NULL, 'Guest User', NULL,
    'guest', 'guest@example.com', NULL, NULL, NULL, NULL,
    'OTHER', NULL,
    '$argon2id$v=19$m=65536,t=3,p=4$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH',
    NULL,
    'GUEST', 'ACTIVE', 'OFFLINE', 1,
    1, 0, 0, '1', '1',
    FALSE, FALSE, 0, NULL,
    0, 0, 0, 0,
    0, 0, TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. Suspended user
-- ----------------------------------------------------------------------------
INSERT INTO erp_users (
    first_name, last_name, preferred_name, full_name, nickname,
    username, email, phone, mobile_number, line_id, id_card,
    gender, birthdate,
    hashed_password, temporary_password,
    role, status, online_status, active_status,
    network_id, network_type_id, type_id, system_id, location_id,
    is_verified, is_superuser, login_failed_count, last_sign_in_at,
    public_notification, sms_notification, email_notification, line_notification,
    public_status, information_agreement_status, is_active,
    deleted_at
) VALUES (
    'Suspended', 'User', NULL, 'Suspended User', NULL,
    'suspended', 'suspended@example.com', NULL, NULL, NULL, NULL,
    'MALE', '1988-05-30',
    '$argon2id$v=19$m=65536,t=3,p=4$REPLACE_WITH_REAL_HASH$REPLACE_WITH_REAL_HASH',
    NULL,
    'USER', 'SUSPENDED', 'OFFLINE', 0,
    1, 0, 0, '1', '1',
    TRUE, FALSE, 5, NOW() - INTERVAL '30 days',
    0, 0, 0, 0,
    0, 0, FALSE,
    (NOW() - INTERVAL '30 days')::date
)
ON CONFLICT (email) DO NOTHING;

COMMIT;

-- ----------------------------------------------------------------------------
-- Verification (plain SQL, works everywhere)
-- ----------------------------------------------------------------------------
SELECT
    id,
    username,
    email,
    first_name || ' ' || last_name AS name,
    role,
    status,
    is_active,
    is_verified,
    created_at
FROM erp_users
ORDER BY id;