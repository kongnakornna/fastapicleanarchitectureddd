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

 Date: 20/07/2026 23:26:03
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
INSERT INTO "public"."alembic_version" VALUES ('a9a05a7f432d');

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
INSERT INTO "public"."app_access_tokens" VALUES ('488ad8ef-6ed1-47a5-96b4-435e598efa2a', 'e5cbf71f-230a-4199-975a-221e37af08ef', '17221291e77d1db1cbcf733cf1dab5c0925ad5739e400f82fa0bf38fdd5c22ee', NULL, 'ADMIN', '2026-07-20 21:13:01.543355+07', '2026-07-20 21:43:01.543083+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('3eccf97d-2975-49e1-9c02-971461644787', '653e8ab7-bfca-40d2-8aae-2ac6009b19d2', 'f46f8a85f9559f3b9383d3095d98243f621dde8ebd79d5a456dcacd4a627b779', NULL, 'USER', '2026-07-20 21:54:18.999439+07', '2026-07-20 22:24:18.999171+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('8634b7b6-0d55-4d05-bc2b-f521937fe307', 'f9b5e473-b9a1-461a-807b-d69af8828c3b', '22b6d26f7a01c0cf87ba2616b165137656ff7418bd1e65d1f7d971c74f6b28a2', NULL, 'USER', '2026-07-20 22:00:46.798325+07', '2026-07-20 22:30:46.798024+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('bd6b4c99-560d-409b-99d3-767c8bc4a8f7', '46357410-9515-49bd-85a4-73960862cabe', '76409096e380ce16dbc300a9bc707eddef9f4f2e7e1eb43d16d47437a7bccb9f', NULL, 'USER', '2026-07-20 22:03:20.959207+07', '2026-07-20 22:33:20.958936+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('b21c6f49-a483-4503-8538-41dde562896d', '10a97e3b-dfdd-45ae-a7d8-1d4154c29f9d', '78837e11fd8fcbd9a653d7f4ef581d56420d95ff8113a58845cb6f1b3bd17097', NULL, 'USER', '2026-07-20 22:03:51.615662+07', '2026-07-20 22:33:51.615372+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('fe138e45-cd39-42ec-934d-713be00043d4', '8c0d30d9-bea7-4d34-af6a-1b07e8d30b02', 'bd4264eace563193de4e3488d39d206abe7b794b51dda0db984da66a636068f9', NULL, 'USER', '2026-07-20 22:03:56.98473+07', '2026-07-20 22:33:56.984497+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('56c522a1-f181-4f7e-a25f-e2da0921237d', '02bc712f-2faa-489b-95a4-75cb9129eb7d', '7eb7f6755daf00a13bd3881567976a137622abe3f90df2bf5ec43ca4260a2d8a', NULL, 'USER', '2026-07-20 22:03:58.905485+07', '2026-07-20 22:33:58.905204+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('bc47350e-460d-481f-88ad-65af6ea09bd2', '9d60d244-77f3-4eea-9d70-d344572cdfbf', 'ae82edec8135028711de0a6419c126be58e37c5e9922f18c07f383465f9304d5', NULL, 'USER', '2026-07-20 22:08:59.502648+07', '2026-07-20 22:38:59.502387+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('46f294c3-a5be-4cdc-8e08-56e0110e0a54', '8e203b0a-1f7e-4dff-a0a8-79d6a4d4a176', '3267ad964a988608b318906b28d997753d9bea75f82be3c49c46fb7e42d87809', NULL, 'USER', '2026-07-20 22:21:45.352089+07', '2026-07-20 22:51:45.35149+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('48b10aff-6ec2-46a3-a9bd-dcdcc2f4e4e9', '0ec93b24-a216-4ae1-b4ac-8f9fc0021324', '654c3e554d51eefa7a3710af0f87dc7f402b83a1c00bc3c1d76c692de7bc9a51', NULL, 'USER', '2026-07-20 22:29:25.492649+07', '2026-07-20 22:59:25.492438+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('34511ee3-048d-42c8-b065-c002227e9bff', 'e2774645-9a6e-4396-99c1-77a7f3191d37', '3d8fa4c008cf9fadb46633a24ebb52860c620eb36cd29093df5312bda8b093ab', NULL, 'USER', '2026-07-20 22:35:40.579722+07', '2026-07-20 23:05:40.579331+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('71b37e98-c4c9-4c71-b156-6351d5f65280', '536daca0-7d49-4f51-82f5-3c0742acc8e6', '361e6be3af1a374c8b19ea595424b480b1294b6f51c3b76f3aaa550f84d766ea', NULL, 'USER', '2026-07-20 22:57:23.966818+07', '2026-07-20 23:27:23.966532+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('b7edc40d-87ce-42d0-b545-a82a98afadba', '2d19c7b2-8451-4489-b8f6-cbd591506eda', 'd9f829c9fc31b488c7eb87767f2a8adb66fc994a8a450392e365dfa9acb8540c', NULL, 'USER', '2026-07-20 23:01:40.646786+07', '2026-07-20 23:31:40.646271+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('5fd221fd-bcb9-4703-9190-8dfb0e1148df', 'ac5d3cea-b4ba-4094-9f0b-59a053468fcf', '3c94e1be780fdb303498d88ea9b47c076d3395c9f52bf9a3714640c7d81042e8', NULL, 'USER', '2026-07-20 23:01:59.719291+07', '2026-07-20 23:31:59.718731+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('fcaae557-ee9c-4272-886c-ca18ed2d71c5', '829881d8-abf5-4e5a-a69c-bc095b77a90d', 'ce3d531d4775cb36307360c85b6cde85dcf3e6f84f97f21ce3e8a05b7d335cf4', NULL, 'USER', '2026-07-20 23:02:41.890637+07', '2026-07-20 23:32:41.890319+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('99ee021e-87cc-484c-8b1e-4400c980b538', 'e746b84a-e134-4d26-8d3e-7034c472c67f', '226c5d0216efe1514bf04062eb5b8adad5dcc41c469bc3c26ea1109d44ff8245', NULL, 'USER', '2026-07-20 23:14:47.728294+07', '2026-07-20 23:44:47.728076+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('a8bee542-8639-49bb-b848-a415f6c8df98', '96421bf5-6269-478a-90f8-b037ee5e199d', '8226cc9885d660bfa205afd06f8445810ce6ce6af57e4f21c73d53f9a93cbc52', NULL, 'USER', '2026-07-20 23:14:48.707443+07', '2026-07-20 23:44:48.707228+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('fe05a368-3895-4e5c-8a25-75cc6b816c86', '3fee1dff-8fd5-46d0-8c20-67a18786a2ba', '48ef97deedaef9136775c8422de892765a46398b12df71509932c063409d5a2e', NULL, 'USER', '2026-07-20 23:14:49.619465+07', '2026-07-20 23:44:49.619244+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('4ffaf741-bfe2-45b0-91f5-95080d12b8e8', '7604db91-4bd4-4ac5-9742-9f641766eefc', 'a38751466f61dd71c321e058d3cca9a06ae4edec584e276115929c3004db1dc9', NULL, 'USER', '2026-07-20 23:14:50.550655+07', '2026-07-20 23:44:50.550434+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('ce5373dd-cfdf-4dec-8fc7-b662ef7adba2', 'f6dabdd6-7178-410a-beb2-bed9b5eb0857', 'ce95d36906e8cfa3d77207ad7bdb30935a07890e272540381891494fbeb7073a', NULL, 'USER', '2026-07-20 23:14:51.483111+07', '2026-07-20 23:44:51.48289+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('acfcb880-509e-4d66-9e65-4373ca37763c', '1d9c4d92-7dec-4853-ab26-9aadd3a8351c', 'ff2680d567fed5db20d1f3f6cef0a1fceb0a4c81111327a2401dbee3669bede6', NULL, 'USER', '2026-07-20 23:14:52.40841+07', '2026-07-20 23:44:52.408149+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('90f0e74f-43fd-49ef-808c-eed3c3588302', '46b755e6-37be-4662-bae0-20ddedfed8be', 'ccfdccb75896c5f964ff802ae08a490271201f64114830cffe972f663b0ea45e', NULL, 'USER', '2026-07-20 23:15:15.133304+07', '2026-07-20 23:45:15.133044+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('2b3fb041-6be6-471d-a7a9-e3f1219393bd', '995c9cbc-547a-453f-b08b-19b5c3921520', '805d0a77e424a46832caf787d1728f252aec5c0e4b7ef5d7ad1783192a5c66f3', NULL, 'USER', '2026-07-20 23:15:15.885522+07', '2026-07-20 23:45:15.885208+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('bd73238a-c22e-449e-8e44-59228c3f2326', '0dd73163-a6aa-4881-998c-5ff4fcea53d2', '95c117d9f728dbb4b98e9ba45374d9ea0991a717bbb4d15edc7c8bd5f82dcc11', NULL, 'USER', '2026-07-20 23:15:16.651525+07', '2026-07-20 23:45:16.65122+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('5df36f3e-a415-406a-a61f-72fcf74a1f85', '253b0333-a217-44c1-80cf-27b59c67afea', '1b4411c9c3cdf1f250a7314925d966fbd4457129b1548cd198e4cb5b8b3e46eb', NULL, 'USER', '2026-07-20 23:15:17.382762+07', '2026-07-20 23:45:17.382541+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('2f4bb142-c3e7-42c3-80c1-d50c896b55cd', 'e4be5366-9bd2-4bfe-916d-6b688c5e333e', 'f0d0ea3fdbb964d6e7d0b50cca7aca85ac805ca70c45d87ebcc4007dc528bf28', NULL, 'USER', '2026-07-20 23:15:18.1149+07', '2026-07-20 23:45:18.114676+07', 'f', NULL);
INSERT INTO "public"."app_access_tokens" VALUES ('88b662b9-0861-4144-837e-955eec71adb4', '2603074b-185a-4fb1-bc60-42cf3263c59c', 'edb39a09666981b845496b68578a5f28b56d154addaf6112b3350132ee5d1bbd', NULL, 'USER', '2026-07-20 23:16:53.525644+07', '2026-07-20 23:46:53.525364+07', 'f', NULL);

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
INSERT INTO "public"."app_refresh_tokens" VALUES ('e5cbf71f-230a-4199-975a-221e37af08ef', '900d22db-8559-4184-881f-28e347401a54', 'deeae4208294c31a0ac98854ff585c3bb1951e72c7e4103552b83bccd215e3cb', NULL, '2026-07-20 21:13:01.543351+07', '2026-07-20 21:13:01.543354+07', '2026-07-27 21:13:01.543072+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('653e8ab7-bfca-40d2-8aae-2ac6009b19d2', 'd4bd8cf4-3719-48b7-bce1-1512121b43c2', 'a0cbb644aeb9f0779a358479eceee8d7a9432abb800ffb04e5c8ba59486b756c', NULL, '2026-07-20 21:54:18.999434+07', '2026-07-20 21:54:18.999438+07', '2026-07-27 21:54:18.999162+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('f9b5e473-b9a1-461a-807b-d69af8828c3b', 'ed632b72-319f-4f3f-8119-ae5b3c12cf22', '86f5dc083109f6ec4ebebda98f29bf29ab285e6148e4a0c744cf152bd8b592f8', NULL, '2026-07-20 22:00:46.798322+07', '2026-07-20 22:00:46.798325+07', '2026-07-27 22:00:46.798011+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('46357410-9515-49bd-85a4-73960862cabe', '0a71cc8b-87ac-491a-8c3d-c8b1805da9ce', 'ee63ee373820c1ad87c517122002d9632830b8b5c09c16c4d496439726a0efb5', NULL, '2026-07-20 22:03:20.959203+07', '2026-07-20 22:03:20.959205+07', '2026-07-27 22:03:20.958925+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('10a97e3b-dfdd-45ae-a7d8-1d4154c29f9d', '53153f81-b493-41f3-a4ac-ddc00c28d441', '83ee58fedd9be83a63630640933b7860dd3033a7c3b192182a29f715efa38eb1', NULL, '2026-07-20 22:03:51.615659+07', '2026-07-20 22:03:51.615661+07', '2026-07-27 22:03:51.615363+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('8c0d30d9-bea7-4d34-af6a-1b07e8d30b02', '4a41ae4c-330a-41a2-b3eb-b0857bc836bd', 'bc3bfed937ec027b35be7cad01e856bb42caa2cea215b263a6821f08e8cfe3da', NULL, '2026-07-20 22:03:56.984726+07', '2026-07-20 22:03:56.984729+07', '2026-07-27 22:03:56.984487+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('02bc712f-2faa-489b-95a4-75cb9129eb7d', '31bad1f8-a025-4259-a710-e300fc45d9d9', 'e6ae7750c8888827df6d98754c98104d7cbb6de73d419be734a92dcc904fe222', NULL, '2026-07-20 22:03:58.905481+07', '2026-07-20 22:03:58.905484+07', '2026-07-27 22:03:58.905195+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('9d60d244-77f3-4eea-9d70-d344572cdfbf', '21cb5278-73db-49c9-8cf2-907ac0c73662', '84927af7f1105f9c1095d0f58f4c2093db53ac4aa2c94af5b666c28a5c3259e5', NULL, '2026-07-20 22:08:59.502644+07', '2026-07-20 22:08:59.502646+07', '2026-07-27 22:08:59.502376+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('8e203b0a-1f7e-4dff-a0a8-79d6a4d4a176', '97816549-48c9-4df5-93e2-114257afcc8b', '7c37e762336fa07b89c5d1248800fae5d7555cfeb518d3796beb4a33cddbf53a', NULL, '2026-07-20 22:21:45.352081+07', '2026-07-20 22:21:45.352087+07', '2026-07-27 22:21:45.351475+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('0ec93b24-a216-4ae1-b4ac-8f9fc0021324', '66227aef-a86e-4e34-9c0f-d4da5590bf7f', '97f08affec5f9e096f06221ee4c4520f753d16a24cc91064596b7c4eba6f6b5c', NULL, '2026-07-20 22:29:25.492646+07', '2026-07-20 22:29:25.492648+07', '2026-07-27 22:29:25.492426+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('e2774645-9a6e-4396-99c1-77a7f3191d37', 'ae9c8258-d96a-4ca6-a22a-e7280ad66b2b', 'c4b5c0490abada37b4100865f3992ba64380f2017f1e97b0254d710a2db40a96', NULL, '2026-07-20 22:35:40.579718+07', '2026-07-20 22:35:40.579721+07', '2026-07-27 22:35:40.579316+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('536daca0-7d49-4f51-82f5-3c0742acc8e6', '21df9ecd-9f7c-4030-9747-e4870201fe1e', '098986d8c0be9a3423ff7f0cf1f54e24dd68ce17372e7c4f042f6f2d662f1115', NULL, '2026-07-20 22:57:23.966814+07', '2026-07-20 22:57:23.966817+07', '2026-07-27 22:57:23.966521+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('2d19c7b2-8451-4489-b8f6-cbd591506eda', 'c27982e7-0163-4cb9-b1cc-c87274c3dbe7', '4de046da59135af58eccb89a8cbe3d4545db7d921181e3bc7c6a7cb0c452ce71', NULL, '2026-07-20 23:01:40.646779+07', '2026-07-20 23:01:40.646785+07', '2026-07-27 23:01:40.646257+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('ac5d3cea-b4ba-4094-9f0b-59a053468fcf', '2808bbff-74fd-4928-99bc-b5047e4e9abf', '935f7e546a3cb616d7739eb9b282ca917ddca1336b3d8e78ace17004bcfe0664', NULL, '2026-07-20 23:01:59.719285+07', '2026-07-20 23:01:59.71929+07', '2026-07-27 23:01:59.718713+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('829881d8-abf5-4e5a-a69c-bc095b77a90d', 'bb572137-3fdb-48c4-8dd6-4b63a9704246', 'c0377ebd12d278732116cde87f952153fb4bef979c2d2def999856410a154531', NULL, '2026-07-20 23:02:41.890632+07', '2026-07-20 23:02:41.890636+07', '2026-07-27 23:02:41.890309+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('e746b84a-e134-4d26-8d3e-7034c472c67f', '329c209b-aebe-4fb1-80b2-c351f80aa528', 'c38976fb5b844dbedd1433ee6cd1b79a7cdb4da3e55c946a28d52299d00c6f7c', NULL, '2026-07-20 23:14:47.728291+07', '2026-07-20 23:14:47.728293+07', '2026-07-27 23:14:47.728067+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('96421bf5-6269-478a-90f8-b037ee5e199d', 'bce7e4ac-2e3d-48b3-9077-d8111ccd043f', '3fce22ed3b59fd97db367df3855a6bfef896a8d25768bde93c673f4883da4269', NULL, '2026-07-20 23:14:48.707438+07', '2026-07-20 23:14:48.707441+07', '2026-07-27 23:14:48.707215+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('3fee1dff-8fd5-46d0-8c20-67a18786a2ba', '225035f7-3253-481f-9002-e3fb2843fee5', '357d373e98cefb8f9244c218fa63272de8452b88d17ae19ba2e21e7cccb8d064', NULL, '2026-07-20 23:14:49.619463+07', '2026-07-20 23:14:49.619465+07', '2026-07-27 23:14:49.619235+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('7604db91-4bd4-4ac5-9742-9f641766eefc', '572b052c-e218-4ad7-9345-f5af43ece88e', '63ad49d06493a31788c3f448b53e1c98efc48bfea5d970e469f3a4bc881ceb3c', NULL, '2026-07-20 23:14:50.550652+07', '2026-07-20 23:14:50.550655+07', '2026-07-27 23:14:50.550427+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('f6dabdd6-7178-410a-beb2-bed9b5eb0857', '169644f1-5e0e-4675-94a1-c1473eb2d9dd', '1aebd014b0de427a8d5fbe831e4f6c8694d10b3868f523bc52d97c37ad4d8b8f', NULL, '2026-07-20 23:14:51.483108+07', '2026-07-20 23:14:51.483111+07', '2026-07-27 23:14:51.482882+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('1d9c4d92-7dec-4853-ab26-9aadd3a8351c', 'dfd16535-626e-4863-96a1-ccfdca291525', '85ce0e86889265659fdbbbf02dcd948246c3af27ac837aea4119f454140f9333', NULL, '2026-07-20 23:14:52.408408+07', '2026-07-20 23:14:52.40841+07', '2026-07-27 23:14:52.408141+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('46b755e6-37be-4662-bae0-20ddedfed8be', '667b80c7-31fb-4241-9866-6e30ffa08811', 'af42469e38703109c64c3a822efe30845ae46b2ae0f97939be564f52f15e36a9', NULL, '2026-07-20 23:15:15.133301+07', '2026-07-20 23:15:15.133303+07', '2026-07-27 23:15:15.133035+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('995c9cbc-547a-453f-b08b-19b5c3921520', '1ee01ac5-bee7-413a-9f0f-9a1356b2892c', 'd2a1648156f20e9b98e4c65fcbfaf00e168eeb6d7886b75741a12f0e6b7ca8c4', NULL, '2026-07-20 23:15:15.885516+07', '2026-07-20 23:15:15.88552+07', '2026-07-27 23:15:15.885195+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('0dd73163-a6aa-4881-998c-5ff4fcea53d2', '7bed5dfd-f7b1-4db6-8d55-5ad115d8b54f', '295feaa3aa53b6486c07d3452f26271d09945abee69e666d4a198e39cee5304b', NULL, '2026-07-20 23:15:16.651522+07', '2026-07-20 23:15:16.651525+07', '2026-07-27 23:15:16.651166+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('253b0333-a217-44c1-80cf-27b59c67afea', '33cf828b-315d-463f-8f7c-166bbf6bf952', '3072b6eb0ffed822fa21293a3281102e0875602e59261294cd7fe75ed747ec47', NULL, '2026-07-20 23:15:17.38276+07', '2026-07-20 23:15:17.382762+07', '2026-07-27 23:15:17.382532+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('e4be5366-9bd2-4bfe-916d-6b688c5e333e', 'c78f2a0f-660c-4b05-8cc9-f611a8dad498', '50412d11d47c15b48739621b5f39b844b7e34d22eadea290f7471c0becd86e0a', NULL, '2026-07-20 23:15:18.114897+07', '2026-07-20 23:15:18.1149+07', '2026-07-27 23:15:18.114668+07', 'f', NULL);
INSERT INTO "public"."app_refresh_tokens" VALUES ('2603074b-185a-4fb1-bc60-42cf3263c59c', '2f81315f-20c0-4538-a333-1b2443c41147', 'b3d37e44fb013a8611bdec176944460c3139f6a5664579145cfaf94f06d9f2d5', NULL, '2026-07-20 23:16:53.525641+07', '2026-07-20 23:16:53.525643+07', '2026-07-27 23:16:53.525356+07', 'f', NULL);

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
  "origin" varchar(255) COLLATE "pg_catalog"."default",
  "referrer" varchar(255) COLLATE "pg_catalog"."default",
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
INSERT INTO "public"."app_sessions" VALUES ('900d22db-8559-4184-881f-28e347401a54', 'f856dc64-8900-4172-aca7-aa10dabaef70', '127.0.0.1', '82be8a147f08420abf875709eb143fd6', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 21:13:02.363464+07', '2026-07-20 21:13:02.363471+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('d4bd8cf4-3719-48b7-bce1-1512121b43c2', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', '02fcf7ec4fa94ff6bff1eac6bd7329d0', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 21:54:19.812344+07', '2026-07-20 21:54:19.812353+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('ed632b72-319f-4f3f-8119-ae5b3c12cf22', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', '42952c9942004c878e80563cddf46e51', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:00:47.57815+07', '2026-07-20 22:00:47.578155+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('0a71cc8b-87ac-491a-8c3d-c8b1805da9ce', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', 'd5dc56adc4ce4ad0982466b3d96f5244', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:03:21.716828+07', '2026-07-20 22:03:21.716837+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('53153f81-b493-41f3-a4ac-ddc00c28d441', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', 'aa03743e889f4f379396a8933c44cd8b', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:03:52.4007+07', '2026-07-20 22:03:52.400711+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('4a41ae4c-330a-41a2-b3eb-b0857bc836bd', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', 'b7cfdb38819643b99306706a2b0eead6', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:03:57.750224+07', '2026-07-20 22:03:57.750229+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('31bad1f8-a025-4259-a710-e300fc45d9d9', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', 'ced0c6dbac8e424d9f04df51f3dab383', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:03:59.972532+07', '2026-07-20 22:03:59.972539+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('21cb5278-73db-49c9-8cf2-907ac0c73662', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', '5ac494b46f7741ec8d29a9f4e663dc29', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:09:00.337998+07', '2026-07-20 22:09:00.338004+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('97816549-48c9-4df5-93e2-114257afcc8b', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', 'ea36055051a5415a977b742ae5b20ef6', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:21:46.467528+07', '2026-07-20 22:21:46.467535+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('66227aef-a86e-4e34-9c0f-d4da5590bf7f', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', '7b451034dcd848e5a3f96f527a5de6ac', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:29:26.291328+07', '2026-07-20 22:29:26.291333+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('ae9c8258-d96a-4ca6-a22a-e7280ad66b2b', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', '58842376272a4a058583751e97e72547', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 22:35:41.622649+07', '2026-07-20 22:35:41.622656+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('21df9ecd-9f7c-4030-9747-e4870201fe1e', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '83e5bc6571f64e15a37965cf87f9d9fd', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 22:57:24.70903+07', '2026-07-20 22:57:24.709037+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('c27982e7-0163-4cb9-b1cc-c87274c3dbe7', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '80fa5c10d6ad40ffbe789f7772c80fd8', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:01:41.738209+07', '2026-07-20 23:01:41.738217+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('2808bbff-74fd-4928-99bc-b5047e4e9abf', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '835b4ff4a5944ceb9bbe2aa70b6a1019', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:02:00.814948+07', '2026-07-20 23:02:00.814955+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('bb572137-3fdb-48c4-8dd6-4b63a9704246', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', '127.0.0.1', 'b7c4eb1eb0554f5bb6d50d2dcabc7f48', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/150.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-07-20 23:02:42.95018+07', '2026-07-20 23:02:42.950187+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('329c209b-aebe-4fb1-80b2-c351f80aa528', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '3b9329169b604d2e96109c490f2fa41d', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:14:48.422464+07', '2026-07-20 23:14:48.42247+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('bce7e4ac-2e3d-48b3-9077-d8111ccd043f', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '80aebf84ec9d4e7a9939364bfc7551e9', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:14:49.381368+07', '2026-07-20 23:14:49.381373+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('225035f7-3253-481f-9002-e3fb2843fee5', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', 'f0f3c0e5abd946a5b8646b1df5889a3d', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:14:50.295075+07', '2026-07-20 23:14:50.295079+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('572b052c-e218-4ad7-9345-f5af43ece88e', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', 'eb0ed935bdc542f7ab06f28b2b04f745', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:14:51.234188+07', '2026-07-20 23:14:51.234192+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('169644f1-5e0e-4675-94a1-c1473eb2d9dd', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '438fd825ca8c4107b73d98599909daea', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:14:52.159638+07', '2026-07-20 23:14:52.159643+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('dfd16535-626e-4863-96a1-ccfdca291525', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '3669157b8c5a48889fb9f783139a248d', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:14:53.087555+07', '2026-07-20 23:14:53.08756+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('667b80c7-31fb-4241-9866-6e30ffa08811', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '59d8c11b30774b12affb60e428c529ae', 'python-urllib/3.14', NULL, 'identity', NULL, NULL, NULL, '2026-07-20 23:15:15.819529+07', '2026-07-20 23:15:15.819538+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('1ee01ac5-bee7-413a-9f0f-9a1356b2892c', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '188a317f734a468fa3a12f53ca630b74', 'python-urllib/3.14', NULL, 'identity', NULL, NULL, NULL, '2026-07-20 23:15:16.591696+07', '2026-07-20 23:15:16.591701+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('7bed5dfd-f7b1-4db6-8d55-5ad115d8b54f', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '16927b85981b4d59ace10956b59b3385', 'python-urllib/3.14', NULL, 'identity', NULL, NULL, NULL, '2026-07-20 23:15:17.327984+07', '2026-07-20 23:15:17.327992+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('33cf828b-315d-463f-8f7c-166bbf6bf952', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', '751ccb9cc64a4bdd865fbb4e73f0a68a', 'python-urllib/3.14', NULL, 'identity', NULL, NULL, NULL, '2026-07-20 23:15:18.05728+07', '2026-07-20 23:15:18.057287+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('c78f2a0f-660c-4b05-8cc9-f611a8dad498', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', 'cc4acc801f624d97b630a66a40ccc2bb', 'python-urllib/3.14', NULL, 'identity', NULL, NULL, NULL, '2026-07-20 23:15:18.807058+07', '2026-07-20 23:15:18.807066+07', 'f');
INSERT INTO "public"."app_sessions" VALUES ('2f81315f-20c0-4538-a333-1b2443c41147', '1561f38c-9996-45bc-ac70-d408f4ed316b', '127.0.0.1', 'daec0244d9eb4673a50ff2ece26ea87e', 'curl/8.21.0', NULL, NULL, NULL, NULL, NULL, '2026-07-20 23:16:54.224872+07', '2026-07-20 23:16:54.224877+07', 'f');

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
INSERT INTO "public"."app_users" VALUES ('Kongnakorn', 'Jantakun', 'Na', 'MALE', '1995-01-01', 'kongnakorn@gmail.com', '+66955088091', '$argon2id$v=19$m=65536,t=3,p=4$q8ZAOrm/+Ol7y1Ej1Ks5Kw$6CIr/v7eQ1BGgdoG4FLBTVfXxlu4fAK2U/JRryFZ5jk', 'USER', '1684b3f5-1f44-42b7-b424-7baf85c23cfd', 't', '2026-07-20 21:53:24.882546+07', '2026-07-20 21:53:24.88256+07', 'ACTIVE', 'kongnakorn');
INSERT INTO "public"."app_users" VALUES ('John', 'Doe', 'Joe', 'MALE', '1995-01-01', 'johndoe2@gmail.com', '+66812345678', '$argon2id$v=19$m=65536,t=3,p=4$95PUbKM8K/6Hp2XRhN1avA$bXXWNAdYzgqgVWlBZGZKlb5y8InHbzxNiSp9cqA4QPc', 'USER', 'ebc95ba2-c4e0-4205-b86a-70622c0ca2ff', 't', '2026-07-20 21:57:15.732305+07', '2026-07-20 21:57:15.73231+07', 'ACTIVE', 'johndoe2');
INSERT INTO "public"."app_users" VALUES ('John', 'Doe', 'Joe', 'MALE', '1995-01-01', 'johndoe3@gmail.com', '+66812345679', '$argon2id$v=19$m=65536,t=3,p=4$X5wTNdPPc3nS/3GQRYoE/A$InQy94ZQFM2RLp+p/LEDQDqNF0LjRACt36IO6A0vvL0', 'USER', 'd7b7e898-72af-46a7-90b7-a60560ff85f6', 't', '2026-07-20 22:06:50.770578+07', '2026-07-20 22:06:50.770586+07', 'ACTIVE', 'johndoe3');
INSERT INTO "public"."app_users" VALUES ('Kongn', 'Nakorn', 'Kong', 'MALE', '1995-01-01', 'kongnakorn2@gmail.com', '+66812345679', '$argon2id$v=19$m=65536,t=3,p=4$ZIlNObD9jC7F6/xuFm4GLw$Ki9mZHHLqcqqWAdWn1gHQpRrs0MGT5dhXp5zap76BOs', 'USER', '1561f38c-9996-45bc-ac70-d408f4ed316b', 't', '2026-07-20 22:54:01.077791+07', '2026-07-20 22:54:01.077812+07', 'ACTIVE', 'kongnakorn2');

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
