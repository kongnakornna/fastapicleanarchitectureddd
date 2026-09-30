-- ═══════════════════════════════════════════════════════════════
-- V011__alter_auth_fk_bigint.sql
-- Convert auth_authentications.user_id UUID → BIGINT
-- Requires: erp_users.id is now BIGINT (V010)
-- NOTE: existing sessions become invalid — force re-login.
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- Drop FK constraint first
ALTER TABLE public.auth_authentications
    DROP CONSTRAINT IF EXISTS auth_authentications_user_id_fkey;

-- Drop the old column (sessions become orphaned → cleared)
ALTER TABLE public.auth_authentications
    DROP COLUMN IF EXISTS user_id;

-- Add new BIGINT column
ALTER TABLE public.auth_authentications
    ADD COLUMN user_id BIGINT NOT NULL DEFAULT 0;

-- Re-add FK
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema='public' AND table_name='erp_users') THEN
        ALTER TABLE public.auth_authentications
            ADD CONSTRAINT auth_authentications_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES public.erp_users (id)
            ON DELETE CASCADE;
    END IF;
END $$;

-- Recreate the unique constraint
ALTER TABLE public.auth_authentications
    DROP CONSTRAINT IF EXISTS uq_auth_user_agent_device;
ALTER TABLE public.auth_authentications
    ADD CONSTRAINT uq_auth_user_agent_device
        UNIQUE (user_id, user_agent, device);

DROP INDEX IF EXISTS public.ix_auth_user_agent_device;
CREATE INDEX ix_auth_user_agent_device
    ON public.auth_authentications (user_id, user_agent, device);

COMMIT;
