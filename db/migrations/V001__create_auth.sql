-- ═══════════════════════════════════════════════════════════════
-- V001__create_auth.sql | Module: authentication | Prefix: auth_
-- Schema: public
-- FK: auth_authentications.user_id → erp_users.id BIGINT (11+ digit)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."auth_access_tokens";
DROP TABLE IF EXISTS "public"."auth_refresh_tokens";
DROP TABLE IF EXISTS "public"."auth_authentications";

CREATE TABLE "public"."auth_authentications" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id"            bigint NOT NULL,
  "ip_address"         varchar(45) NOT NULL,
  "device"             varchar(255) NOT NULL,
  "user_agent"         text NOT NULL,
  "accept_language"    varchar(255) NULL,
  "accept_encoding"    varchar(255) NULL,
  "origin"             varchar(255) NOT NULL DEFAULT '',
  "referrer"           varchar(255) NULL,
  "location"           varchar(255) NULL,
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "last_update_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "blacklisted"        bool NOT NULL DEFAULT false,
  CONSTRAINT "auth_authentications_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_auth_user_agent_device"
      UNIQUE ("user_id", "user_agent", "device")
);
CREATE INDEX "ix_auth_user_agent_device"
    ON "public"."auth_authentications" USING btree ("user_id", "user_agent", "device");

CREATE TABLE "public"."auth_refresh_tokens" (
  "id"                     uuid NOT NULL DEFAULT gen_random_uuid(),
  "authentication_id"      uuid NOT NULL,
  "hashed_jti"             text NOT NULL UNIQUE,
  "previous_hashed_jti"    text NULL,
  "created_at"             timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"             timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at"             timestamptz(6) NOT NULL,
  "revoked"                bool NOT NULL DEFAULT false,
  "revoked_at"             timestamptz(6) NULL,
  CONSTRAINT "auth_refresh_tokens_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_auth_refresh_authentication" UNIQUE ("authentication_id"),
  CONSTRAINT "fk_auth_refresh_authentication"
      FOREIGN KEY ("authentication_id")
      REFERENCES "public"."auth_authentications" ("id") ON DELETE CASCADE
);
CREATE INDEX "ix_auth_refresh_hashed_revoked"
    ON "public"."auth_refresh_tokens" USING btree ("hashed_jti", "revoked");

CREATE TABLE "public"."auth_access_tokens" (
  "id"                     uuid NOT NULL DEFAULT gen_random_uuid(),
  "refresh_id"             uuid NOT NULL,
  "hashed_jti"             text NOT NULL UNIQUE,
  "previous_hashed_jti"    text NULL UNIQUE,
  "permission"             varchar(20) NOT NULL DEFAULT 'user',
  "created_at"             timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at"             timestamptz(6) NOT NULL,
  "revoked"                bool NOT NULL DEFAULT false,
  "revoked_at"             timestamptz(6) NULL,
  CONSTRAINT "auth_access_tokens_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_auth_access_refresh" UNIQUE ("refresh_id"),
  CONSTRAINT "fk_auth_access_refresh"
      FOREIGN KEY ("refresh_id")
      REFERENCES "public"."auth_refresh_tokens" ("id") ON DELETE CASCADE
);
CREATE INDEX "ix_auth_access_hashed_revoked"
    ON "public"."auth_access_tokens" USING btree ("hashed_jti", "revoked");

-- Triggers
CREATE OR REPLACE FUNCTION public.set_updated_at_auth()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auth_updated ON "public"."auth_authentications";
CREATE TRIGGER trg_auth_updated BEFORE UPDATE ON "public"."auth_authentications"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_auth();

-- RLS
ALTER TABLE "public"."auth_authentications" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_auth_tenant ON "public"."auth_authentications";
CREATE POLICY p_auth_tenant ON "public"."auth_authentications"
    USING (true);

COMMIT;
