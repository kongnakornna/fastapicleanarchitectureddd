/*
 Navicat Premium Dump SQL

 Source Server         : postgres-localhost
 Source Server Type    : PostgreSQL
 Source Server Version : 180003 (180003)
 Source Host           : localhost:5432
 Source Catalog        : fastapi
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 180003 (180003)
 File Encoding         : 65001

 Date: 20/07/2026 21:11:44
*/


-- ----------------------------
-- Type structure for gender_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."gender_enum";
CREATE TYPE "public"."gender_enum" AS ENUM (
  'MALE',
  'FEMALE',
  'NON_BINARY',
  'OTHER'
);

-- ----------------------------
-- Type structure for role_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."role_enum";
CREATE TYPE "public"."role_enum" AS ENUM (
  'ADMIN',
  'MANAGER',
  'USER'
);

-- ----------------------------
-- Type structure for user_status_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."user_status_enum";
CREATE TYPE "public"."user_status_enum" AS ENUM (
  'ACTIVE',
  'INACTIVE',
  'SUSPENDED'
);

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."alembic_version";
CREATE TABLE "public"."alembic_version" (
  "version_num" varchar(32) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO "public"."alembic_version" VALUES ('25845428d7a7');

-- ----------------------------
-- Table structure for app_access_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_access_tokens";
CREATE TABLE "public"."app_access_tokens" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "refresh_id" uuid NOT NULL,
  "hashed_jti" text COLLATE "pg_catalog"."default" NOT NULL,
  "previous_hashed_jti" text COLLATE "pg_catalog"."default",
  "permission" "public"."role_enum" NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool NOT NULL,
  "revoked_at" timestamptz(6)
)
;
COMMENT ON COLUMN "public"."app_access_tokens"."id" IS 'Unique identifier of the access token';
COMMENT ON COLUMN "public"."app_access_tokens"."refresh_id" IS 'Refresh token associated with this access token';
COMMENT ON COLUMN "public"."app_access_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."app_access_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous access token';
COMMENT ON COLUMN "public"."app_access_tokens"."permission" IS 'Permission level associated with the access token';
COMMENT ON COLUMN "public"."app_access_tokens"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_access_tokens"."expires_at" IS 'Expiration timestamp of the access token';
COMMENT ON COLUMN "public"."app_access_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."app_access_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of app_access_tokens
-- ----------------------------
INSERT INTO "public"."app_access_tokens" VALUES ('7711dc18-0ae2-4a47-890c-5bdcbbdb9c3c', '82a2343c-0d22-45f7-8151-2e28f9ff6174', 'a2e0b70f2e757f36f9c238cd4e05508fdb0350e93625ae36c0c6eba6cde5660d', NULL, 'ADMIN', '2026-07-20 20:46:02.553752+07', '2026-07-20 21:16:02.55342+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('c86d0f1a-223e-47f9-8462-2eb672a38047', 'f3e208c3-42c7-49fe-a475-ace203d5a9a4', 'fac4f153c5f4c48923307797ae194a2a58bbeaa4d9c50d4f44bd85df498ef642', NULL, 'ADMIN', '2026-07-20 20:46:38.744588+07', '2026-07-20 21:16:38.744297+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('9ca775df-5145-409b-ae90-d60d0458dfe6', '99a9a4cb-5814-4876-8d66-670fe16e7ab7', 'ce144b07bb924a0faf37535e7c2c96bdda62857c4b96a701e071fde492da0530', NULL, 'ADMIN', '2026-07-20 20:47:09.536374+07', '2026-07-20 21:17:09.535895+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('1f962539-1892-4bb5-8096-8683f4fc957b', 'cf3b03c1-b8de-406c-863a-e07a68bcf28d', '23afe22bd25b6b1f1023bf1e46cbf4a669f634e1bfc8881f28b86cd1227f72c9', NULL, 'ADMIN', '2026-07-20 20:49:00.770572+07', '2026-07-20 21:19:00.770319+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('68907837-d6ff-4738-bf2d-5340823943b0', 'c8e2d79b-fd88-4ada-9c73-aff5764d7e47', 'd623f3fd469284bfafcdf1afdafb7e089db762e6f7a967d204388b50ad7603b3', NULL, 'ADMIN', '2026-07-20 20:55:06.336675+07', '2026-07-20 21:25:06.336358+07', 'f', NULL);

-- ----------------------------
-- Table structure for app_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_permissions";
CREATE TABLE "public"."app_permissions" (
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "resource" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "action" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_permissions"."name" IS 'Name of the permission';
COMMENT ON COLUMN "public"."app_permissions"."description" IS 'Description of the permission';
COMMENT ON COLUMN "public"."app_permissions"."resource" IS 'Resource that the permission applies to (e.g. ''user'', ''session'')';
COMMENT ON COLUMN "public"."app_permissions"."action" IS 'Action allowed on the resource (e.g. ''create'', ''read'', ''update'', ''delete'')';
COMMENT ON COLUMN "public"."app_permissions"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_permissions"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_permissions"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for app_refresh_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_refresh_tokens";
CREATE TABLE "public"."app_refresh_tokens" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "session_id" uuid NOT NULL,
  "hashed_jti" text COLLATE "pg_catalog"."default" NOT NULL,
  "previous_hashed_jti" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool NOT NULL,
  "revoked_at" timestamptz(6)
)
;
COMMENT ON COLUMN "public"."app_refresh_tokens"."id" IS 'Unique identifier of the refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."session_id" IS 'Session associated with this refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."app_refresh_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."created_at" IS 'Timestamp when the refresh token was created';
COMMENT ON COLUMN "public"."app_refresh_tokens"."updated_at" IS 'Timestamp when the record was last updated';
COMMENT ON COLUMN "public"."app_refresh_tokens"."expires_at" IS 'Expiration timestamp of the refresh token';
COMMENT ON COLUMN "public"."app_refresh_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."app_refresh_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of app_refresh_tokens
-- ----------------------------
INSERT INTO "public"."app_refresh_tokens" VALUES ('82a2343c-0d22-45f7-8151-2e28f9ff6174', '3488ef26-c652-4342-b4cc-60ac9013e7f6', '28b91dba0ba31b99b3e19157c6b8be7c5a39f80f6a4b62182a6d7d021540f587', NULL, '2026-07-20 20:46:02.553745+07', '2026-07-20 20:46:02.553749+07', '2026-07-27 20:46:02.553409+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('f3e208c3-42c7-49fe-a475-ace203d5a9a4', '17ce7088-483e-408d-a4d7-d5c3a1faaac6', '104123b7f389598fa3b75a74d17eec5cbd8403c2a2bd6c40dfad947abe48a5e2', NULL, '2026-07-20 20:46:38.744584+07', '2026-07-20 20:46:38.744587+07', '2026-07-27 20:46:38.744285+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('99a9a4cb-5814-4876-8d66-670fe16e7ab7', 'dac9bdf6-731d-4dd7-82b6-bffaad76c2b2', '526d97e9ab23afe9fc71bc96dca634e8c7e1ed2829bf040fa6896afb8cc50f4b', NULL, '2026-07-20 20:47:09.536369+07', '2026-07-20 20:47:09.536373+07', '2026-07-27 20:47:09.535882+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('cf3b03c1-b8de-406c-863a-e07a68bcf28d', '6a35e260-b387-4b46-aaed-914879085f0f', 'cca00a0f3e558d8f245a701bf54df8f005ab4b9364037c6e14b4c9c3f1b8ca25', NULL, '2026-07-20 20:49:00.77057+07', '2026-07-20 20:49:00.770571+07', '2026-07-27 20:49:00.770308+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('c8e2d79b-fd88-4ada-9c73-aff5764d7e47', 'bbc843a0-ef41-4b73-bbab-d6b5d2ecbcf5', '626179dcb2f682c49998fa5f2f789b67793a58220e96dad639ae2f5f69176b26', NULL, '2026-07-20 20:55:06.336671+07', '2026-07-20 20:55:06.336674+07', '2026-07-27 20:55:06.336347+07', 'f', NULL);

-- ----------------------------
-- Table structure for app_role_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_role_permissions";
CREATE TABLE "public"."app_role_permissions" (
  "role_id" uuid NOT NULL,
  "permission_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_role_permissions"."role_id" IS 'Identifier of the role';
COMMENT ON COLUMN "public"."app_role_permissions"."permission_id" IS 'Identifier of the permission';
COMMENT ON COLUMN "public"."app_role_permissions"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_role_permissions"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_role_permissions"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_role_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for app_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_roles";
CREATE TABLE "public"."app_roles" (
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_roles"."name" IS 'Name of the role';
COMMENT ON COLUMN "public"."app_roles"."description" IS 'Description of the role';
COMMENT ON COLUMN "public"."app_roles"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_roles"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_roles"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_roles
-- ----------------------------
INSERT INTO "public"."app_roles" VALUES ('admin', 'Administrator role with full access', '05a40adf-0844-4b18-92f1-7bc0d1d37e10', 't', '2026-07-20 14:58:04.211164+07', '2026-07-20 14:58:04.211164+07');
INSERT INTO "public"."app_roles" VALUES ('manager', 'Manager role with elevated access', 'eb6bf59a-cbb7-43cb-bbec-0ec5a94aab52', 't', '2026-07-20 14:58:04.211164+07', '2026-07-20 14:58:04.211164+07');
INSERT INTO "public"."app_roles" VALUES ('user', 'Regular user role with basic access', '08ff9b8a-52dd-4264-88fe-9dd64552e751', 't', '2026-07-20 14:58:04.211164+07', '2026-07-20 14:58:04.211164+07');

-- ----------------------------
-- Table structure for app_sessions
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_sessions";
CREATE TABLE "public"."app_sessions" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "ip_address" varchar(45) COLLATE "pg_catalog"."default" NOT NULL,
  "device" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "user_agent" text COLLATE "pg_catalog"."default" NOT NULL,
  "accept_language" varchar(255) COLLATE "pg_catalog"."default",
  "accept-encoding" varchar(255) COLLATE "pg_catalog"."default",
  "origin" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "referrer" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "location" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "last_update_at" timestamptz(6) NOT NULL DEFAULT now(),
  "blacklisted" bool NOT NULL
)
;
COMMENT ON COLUMN "public"."app_sessions"."id" IS 'Unique identifier of the session';
COMMENT ON COLUMN "public"."app_sessions"."user_id" IS 'Identifier of the user who owns the session';
COMMENT ON COLUMN "public"."app_sessions"."ip_address" IS 'IP address used when the session was created';
COMMENT ON COLUMN "public"."app_sessions"."device" IS 'Human readable device name';
COMMENT ON COLUMN "public"."app_sessions"."user_agent" IS 'User agent string of the client';
COMMENT ON COLUMN "public"."app_sessions"."accept_language" IS 'Accept-Language header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."accept-encoding" IS 'Accept-Encoding header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."origin" IS 'Origin header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."referrer" IS 'Referrer header value of the client';
COMMENT ON COLUMN "public"."app_sessions"."location" IS 'Approximate geographic location of the client';
COMMENT ON COLUMN "public"."app_sessions"."created_at" IS 'Timestamp when the session was created';
COMMENT ON COLUMN "public"."app_sessions"."last_update_at" IS 'Last time the session was updated';
COMMENT ON COLUMN "public"."app_sessions"."blacklisted" IS 'Indicates whether the session is blacklisted';

-- ----------------------------
-- Records of app_sessions
-- ----------------------------
INSERT INTO "public"."app_sessions" VALUES ('3488ef26-c652-4342-b4cc-60ac9013e7f6', 'f856dc64-8900-4172-aca7-aa10dabaef70', '127.0.0.1', '764d44e8d66f4c098eb29b5dedc69740', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 20:46:03.807516+07', '2026-07-20 20:46:03.807523+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('17ce7088-483e-408d-a4d7-d5c3a1faaac6', 'f856dc64-8900-4172-aca7-aa10dabaef70', '127.0.0.1', 'ab89c901130345f69e2a63fd94735a6d', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 20:46:39.53617+07', '2026-07-20 20:46:39.536178+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('dac9bdf6-731d-4dd7-82b6-bffaad76c2b2', 'f856dc64-8900-4172-aca7-aa10dabaef70', '127.0.0.1', '6de3d619655f4b2da97d5e9f369ce954', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 20:47:10.324206+07', '2026-07-20 20:47:10.324212+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('6a35e260-b387-4b46-aaed-914879085f0f', 'f856dc64-8900-4172-aca7-aa10dabaef70', '127.0.0.1', '6ff585bc303d4ab896b19556a10ec5a1', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 20:49:01.59252+07', '2026-07-20 20:49:01.592526+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('bbc843a0-ef41-4b73-bbab-d6b5d2ecbcf5', 'f856dc64-8900-4172-aca7-aa10dabaef70', '127.0.0.1', '794521a62473467a8ceea49556d8e881', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 20:55:07.157925+07', '2026-07-20 20:55:07.157931+07', 'f');

-- ----------------------------
-- Table structure for app_user_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_user_roles";
CREATE TABLE "public"."app_user_roles" (
  "user_id" uuid NOT NULL,
  "role_id" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."app_user_roles"."user_id" IS 'Identifier of the user';
COMMENT ON COLUMN "public"."app_user_roles"."role_id" IS 'Identifier of the role';
COMMENT ON COLUMN "public"."app_user_roles"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_user_roles"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_user_roles"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of app_user_roles
-- ----------------------------

-- ----------------------------
-- Table structure for app_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."app_users";
CREATE TABLE "public"."app_users" (
  "first_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "last_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "preferred_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "gender" "public"."gender_enum" NOT NULL,
  "birthdate" date NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "phone" varchar(18) COLLATE "pg_catalog"."default",
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "role" "public"."role_enum" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "status" "public"."user_status_enum" NOT NULL DEFAULT 'ACTIVE'::user_status_enum,
  "username" varchar(100) COLLATE "pg_catalog"."default" NOT NULL
)
;
COMMENT ON COLUMN "public"."app_users"."first_name" IS 'First name of the user';
COMMENT ON COLUMN "public"."app_users"."last_name" IS 'Last name of the user';
COMMENT ON COLUMN "public"."app_users"."preferred_name" IS 'Preferred name of the user';
COMMENT ON COLUMN "public"."app_users"."gender" IS 'Gender of the user';
COMMENT ON COLUMN "public"."app_users"."birthdate" IS 'Birthdate of the user';
COMMENT ON COLUMN "public"."app_users"."email" IS 'Email address of the user';
COMMENT ON COLUMN "public"."app_users"."phone" IS 'Phone number of the user';
COMMENT ON COLUMN "public"."app_users"."hashed_password" IS 'Hashed password of the user';
COMMENT ON COLUMN "public"."app_users"."role" IS 'Role of the user';
COMMENT ON COLUMN "public"."app_users"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."app_users"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."app_users"."updated_at" IS 'Timestamp when the record was last updated';
COMMENT ON COLUMN "public"."app_users"."status" IS 'Status of the user (active, inactive, suspended)';
COMMENT ON COLUMN "public"."app_users"."username" IS 'Unique username of the user';

-- ----------------------------
-- Records of app_users
-- ----------------------------
INSERT INTO "public"."app_users" VALUES ('System', 'Administrator', 'Admin', 'OTHER', '1999-12-31', 'admin@localhost.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$qHgbBMhkDHnxyzrEICp8dA$FBSs2Qs7iRAjYwFRximNYkkcwcrGcIwkmUY/1A4TfKE', 'ADMIN', 'a47149f5-2511-4241-8f6e-f35a3eef8b79', 't', '2026-07-20 14:02:42.618696+07', '2026-07-20 14:02:42.618696+07', 'ACTIVE', 'admin');
INSERT INTO "public"."app_users" VALUES ('Demo App', 'Admin App', 'Admin', 'MALE', '1990-01-01', 'demoadmin@localhost.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$Oyn9azZlb/GUqXkY576dww$BjmorZ3swcpiM8GRNUqle6LCLB7hJvimjeun1QXRd5k', 'ADMIN', 'f856dc64-8900-4172-aca7-aa10dabaef70', 't', '2026-07-20 19:03:05.1961+07', '2026-07-20 19:03:05.1961+07', 'ACTIVE', 'demoadmin');
INSERT INTO "public"."app_users" VALUES ('John Data3', 'Doe', 'Joe', 'MALE', '1995-01-01', 'johndoe@localhost.com', '+66812345678', '$argon2id$v=19$m=65536,t=3,p=4$9BU5VboExqskjIVAeU59JQ$9ewF/S4CnCRnqkZQjjiocSJPTDFXZAdhPGgaED9b6qw', 'USER', 'bd984b2a-0a5f-4336-803e-5c91ce06376d', 't', '2026-07-20 20:43:57.679935+07', '2026-07-20 20:43:57.679941+07', 'ACTIVE', 'johndoe');

-- ----------------------------
-- Primary Key structure for table alembic_version
-- ----------------------------
ALTER TABLE "public"."alembic_version" ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");

-- ----------------------------
-- Indexes structure for table app_access_tokens
-- ----------------------------
CREATE INDEX "ix_hashed_jti" ON "public"."app_access_tokens" USING btree (
  "hashed_jti" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table app_access_tokens
-- ----------------------------
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_hashed_jti_key" UNIQUE ("hashed_jti");
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_previous_hashed_jti_key" UNIQUE ("previous_hashed_jti");
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "uq_access_tokens_refresh_id" UNIQUE ("refresh_id");

-- ----------------------------
-- Primary Key structure for table app_access_tokens
-- ----------------------------
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_permissions
-- ----------------------------
ALTER TABLE "public"."app_permissions" ADD CONSTRAINT "app_permissions_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table app_permissions
-- ----------------------------
ALTER TABLE "public"."app_permissions" ADD CONSTRAINT "app_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."app_refresh_tokens" ADD CONSTRAINT "uq_refresh_tokens_session_id" UNIQUE ("session_id");

-- ----------------------------
-- Primary Key structure for table app_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."app_refresh_tokens" ADD CONSTRAINT "app_refresh_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_role_permissions
-- ----------------------------
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "uq_role_permissions" UNIQUE ("role_id", "permission_id");

-- ----------------------------
-- Primary Key structure for table app_role_permissions
-- ----------------------------
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "app_role_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_roles
-- ----------------------------
ALTER TABLE "public"."app_roles" ADD CONSTRAINT "app_roles_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table app_roles
-- ----------------------------
ALTER TABLE "public"."app_roles" ADD CONSTRAINT "app_roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table app_sessions
-- ----------------------------
CREATE INDEX "ix_sessions_user_id_user_agent_device" ON "public"."app_sessions" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "user_agent" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "device" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table app_sessions
-- ----------------------------
ALTER TABLE "public"."app_sessions" ADD CONSTRAINT "uq_sessions_user_id_user_agent_device" UNIQUE ("user_id", "user_agent", "device");

-- ----------------------------
-- Primary Key structure for table app_sessions
-- ----------------------------
ALTER TABLE "public"."app_sessions" ADD CONSTRAINT "app_sessions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_user_roles
-- ----------------------------
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "uq_user_roles" UNIQUE ("user_id", "role_id");

-- ----------------------------
-- Primary Key structure for table app_user_roles
-- ----------------------------
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "app_user_roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table app_users
-- ----------------------------
ALTER TABLE "public"."app_users" ADD CONSTRAINT "uq_users_email_status" UNIQUE ("email", "status");
ALTER TABLE "public"."app_users" ADD CONSTRAINT "uq_users_username_status" UNIQUE ("username", "status");

-- ----------------------------
-- Primary Key structure for table app_users
-- ----------------------------
ALTER TABLE "public"."app_users" ADD CONSTRAINT "app_users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table app_access_tokens
-- ----------------------------
ALTER TABLE "public"."app_access_tokens" ADD CONSTRAINT "app_access_tokens_refresh_id_fkey" FOREIGN KEY ("refresh_id") REFERENCES "public"."app_refresh_tokens" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."app_refresh_tokens" ADD CONSTRAINT "app_refresh_tokens_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."app_sessions" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_role_permissions
-- ----------------------------
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "app_role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."app_permissions" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."app_role_permissions" ADD CONSTRAINT "app_role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."app_roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_sessions
-- ----------------------------
ALTER TABLE "public"."app_sessions" ADD CONSTRAINT "app_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."app_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table app_user_roles
-- ----------------------------
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "app_user_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."app_roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."app_user_roles" ADD CONSTRAINT "app_user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."app_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
