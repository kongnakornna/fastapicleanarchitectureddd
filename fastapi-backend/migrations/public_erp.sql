/*
 Navicat Premium Dump SQL

 Source Server         : postgres-Docker-5437
 Source Server Type    : PostgreSQL
 Source Server Version : 170011 (170011)
 Source Host           : localhost:5437
 Source Catalog        : ioterp
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170011 (170011)
 File Encoding         : 65001

 Date: 21/09/2026 22:12:22
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
-- Type structure for notification_type_enum
-- ----------------------------
DROP TYPE IF EXISTS "public"."notification_type_enum";
CREATE TYPE "public"."notification_type_enum" AS ENUM (
  'KNOWLEDGE_CREATED',
  'KNOWLEDGE_UPDATED',
  'KNOWLEDGE_DELETED',
  'SYSTEM_ALERT'
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
INSERT INTO "public"."alembic_version" VALUES ('a1b2c3d4e5f6');

-- ----------------------------
-- Table structure for erp_access_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_access_tokens";
CREATE TABLE "public"."erp_access_tokens" (
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
COMMENT ON COLUMN "public"."erp_access_tokens"."id" IS 'Unique identifier of the access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."refresh_id" IS 'Refresh token associated with this access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."erp_access_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."permission" IS 'Permission level associated with the access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."created_at" IS 'Timestamp when the access token was created';
COMMENT ON COLUMN "public"."erp_access_tokens"."expires_at" IS 'Expiration timestamp of the access token';
COMMENT ON COLUMN "public"."erp_access_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."erp_access_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of erp_access_tokens
-- ----------------------------
INSERT INTO "public"."erp_access_tokens" VALUES ('cc35ad7e-d018-4ba5-a8c3-8a1543d09e0b', '942fb32b-99b2-4d14-87ad-70b21759e7d8', 'cb575276f50d0c5ef135b791f48a9e731d1ecf54b5b2fcfc4b32ff1f163f6132', '9e7623491621540d9b301da098f5bd300a27d4ef99589089a901aa489773d5b8', 'USER', '2026-09-19 10:40:56.273987+00', '2026-09-19 10:55:56.273987+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('e5a0b049-feb1-41b6-a63c-2c3558c39c7b', 'f2e6a9a0-a33c-4f90-84b7-b8ea7e280118', '68a504a91deee1c1d03d241625de7ad7cc15adafda17591e963c12ff854d2c6a', '623d76f8a29712365bdd8742a3da7787c0753ca5585b87655106d473d515e02f', 'ADMIN', '2026-09-19 10:42:06.127162+00', '2026-09-19 10:57:06.127162+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('f13abb50-63a6-4194-955a-35c26a98783c', '67fa2957-4650-4e2f-aa1d-a9ebd401153b', '60572eb2b82973cfe1071f1994c1d8d322806a2e83839e024a808d5b1c028c43', NULL, 'ADMIN', '2026-09-20 03:16:54.114949+00', '2026-09-20 03:31:54.114949+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('249680af-b141-410d-8f7e-d5b5f2c965f8', '3a680b04-04cc-4bbe-9ebb-84e659b78952', '8b3d042bf847ebd3faa037a71879e21071f13a929764648f16b79711f1f200ee', NULL, 'ADMIN', '2026-09-20 03:16:58.159196+00', '2026-09-20 03:31:58.159196+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('8edeb2b7-8228-492e-a6fb-0a2b1358e457', 'ad1f20bf-14e1-4993-a271-c25084b6df13', '7e810dfbd95b20fb23bbe1596db4b4c555bde8f9eeb3a2334359b205f2bd7fd8', NULL, 'ADMIN', '2026-09-20 12:06:51.790621+00', '2026-09-20 12:21:51.790621+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('b26795bf-c192-4ad5-b0b7-ddb672c6c8b4', '55ad1881-f904-4745-8595-2e7757835628', 'dbf2e0b8494cb97c010e5132dc667602e9c13759080623ad7b791376fa13dd64', NULL, 'ADMIN', '2026-09-20 12:06:55.70572+00', '2026-09-20 12:21:55.70572+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('07ec16cd-ee50-412e-b66f-c1fd1f32c1fc', 'f6f10b5a-6f54-4b00-a865-a242a5a2d811', 'b932037d1a91a72d28c01eaa1e3a51caa1e12f5a87855fe2a019e069921fa16a', NULL, 'ADMIN', '2026-09-20 04:34:22.132496+00', '2026-09-20 04:49:22.132496+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('fe13642a-49b7-49e2-bca6-b8be6d254e98', '5d5ec304-be7b-4635-8f08-62951e5970d2', '07462621dfdad28850eddafe6c9c631d6de4839b6c97b9316fa682c4b028f686', NULL, 'ADMIN', '2026-09-20 04:34:40.006493+00', '2026-09-20 04:49:40.006493+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('fe1499b2-3eda-4fdb-96a4-e8889032da88', '8460f833-8f5a-4e6d-a0c0-edd2d6176e19', '40e90ce76e7c46a1d318fdb3837623babe7bc0a80b370e3a779842787fdb3fe0', NULL, 'ADMIN', '2026-09-20 04:34:51.412929+00', '2026-09-20 04:49:51.412929+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('8c6f6c91-85e1-43e0-9f2c-7c9e5c074f08', '9bf8e90b-239a-4d7e-879c-da57ff8baf24', '094cf1155902961e27f52ca13d94672b3717e27067104bd0b50cafdd79459c8d', NULL, 'ADMIN', '2026-09-20 04:37:11.858977+00', '2026-09-20 04:52:11.858977+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('4e9ee8a9-1fa6-4bf0-a950-c069c9d22773', 'e995fd97-1612-4c3e-9653-9629cb577bab', '7f0cf0c531346903b02e4521a66620d3f8c308fd9b829f0a396df7754fc78fff', NULL, 'ADMIN', '2026-09-20 04:44:44.422011+00', '2026-09-20 04:59:44.422011+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('07fc7291-58bc-48de-9733-dcd0121941f5', 'bd2c201c-ddfb-42cf-a19b-809a779116d0', '77b58a67c36f712c0e5d4f62c7be9347c691bdd4326cb62924c2114c89d3437f', NULL, 'ADMIN', '2026-09-20 05:02:27.967339+00', '2026-09-20 05:17:27.967339+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('13073941-8e7e-43d3-8276-4f3b17ef2955', '8c90f2e2-2b6d-4462-8d10-f5539d6d732e', '4946e2f94993a9ae4b517665331bdddb3bae8d25f4dd8af1891172ac11bdd772', NULL, 'ADMIN', '2026-09-20 12:07:03.531524+00', '2026-09-20 12:22:03.531524+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('e34c4f5f-2cbb-4ef6-a23f-1f2b75cf821f', '2e999b19-6eae-4b15-84bb-9578805485ac', 'e246fb61dc8c7a4c41043d76db92877ddf9e904413dfd9bcf283eb8fd8c77e9a', NULL, 'ADMIN', '2026-09-20 12:07:04.586201+00', '2026-09-20 12:22:04.586201+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('e4ebf29d-a929-4866-afd3-4e1891615eec', 'bbb7a2db-8190-4c69-be46-3f9d66a9967a', '6f310b3897144373e4578d30f64704d573a3e2d2e426cb0df3da6b1bf5a01f3e', NULL, 'ADMIN', '2026-09-20 12:07:06.063783+00', '2026-09-20 12:22:06.063783+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('9f783405-de4a-4dea-bf58-1a632b264800', '3af8d814-e838-4999-9738-f54d9c30de36', '864aea342642c531943e7cfe8801c9c62b88efd52c84f16e8a207008043bbf84', NULL, 'ADMIN', '2026-09-21 04:19:45.848112+00', '2026-09-21 04:34:45.848112+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('200b7b7b-9fc3-4c7e-8224-47ce89f0b8a3', '7ae53838-3c47-42d5-9df2-a3d19d85c98a', '02252b522ae5ba9ad4eadb39f10eb74a7cdcca3705c2ac2a9b61631467840f37', 'b996badbf85f26841a5d2b418d9f3a7bd051b78c3f2823dc747ee82041f0ab39', 'ADMIN', '2026-09-21 06:11:27.221943+00', '2026-09-21 06:26:27.221943+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('30af19ef-e067-4148-9a88-90f013afe198', '8404b67b-7c39-4e1f-a675-69430bf46883', '33621ca6e6c42f9c258403b36cf78907c45b001a0ae293adc77b2b06b5295b63', '870755d62adae3962e51916bb43ca8cebeffcfddfd03de48956da2d35cff4627', 'ADMIN', '2026-09-21 14:59:26.30405+00', '2026-09-21 15:14:26.30405+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('325d0894-6097-47c8-9499-ae41d89b618b', 'a586628c-de2f-4313-83c2-542ad875441d', '7c6b69697de384c6eda32e25cf6ad3858b04b7b3a8b9d9cffd7f0674f242d3cb', 'b70fc7dc05cb2a1edd7a89172f988a56af4266c0c6f2af542047a3a0cdb3548d', 'ADMIN', '2026-09-21 15:05:00.638853+00', '2026-09-21 15:20:00.638853+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('4179c82a-f168-4873-8fe3-a731b3a8ca5a', '5da71da1-279f-4411-8616-566adfc91dfd', '0a029b68c081123f3b9e0357d4e602201c835b9ffe5b8f1ec787e977f4c747df', '4841adb34d623b335443dbe9d671e61c3d74dae04c656b7e5827227d3c66f579', 'ADMIN', '2026-09-20 12:56:39.346261+00', '2026-09-20 13:11:39.346261+00', 'f', NULL);

-- ----------------------------
-- Table structure for erp_authentications
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_authentications";
CREATE TABLE "public"."erp_authentications" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "ip_address" varchar(45) COLLATE "pg_catalog"."default" NOT NULL,
  "device" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "user_agent" text COLLATE "pg_catalog"."default" NOT NULL,
  "accept_language" varchar(255) COLLATE "pg_catalog"."default",
  "accept_encoding" varchar(255) COLLATE "pg_catalog"."default",
  "origin" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "referrer" varchar(255) COLLATE "pg_catalog"."default",
  "location" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "last_update_at" timestamptz(6) NOT NULL DEFAULT now(),
  "blacklisted" bool NOT NULL,
  "provider_user_id" varchar(255) COLLATE "pg_catalog"."default",
  "provider" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'local'::character varying
)
;
COMMENT ON COLUMN "public"."erp_authentications"."id" IS 'Unique identifier of the authentication';
COMMENT ON COLUMN "public"."erp_authentications"."user_id" IS 'Identifier of the user who owns the authentication';
COMMENT ON COLUMN "public"."erp_authentications"."ip_address" IS 'IP address used when the authentication was created';
COMMENT ON COLUMN "public"."erp_authentications"."device" IS 'Human readable device name';
COMMENT ON COLUMN "public"."erp_authentications"."user_agent" IS 'User agent string of the client';
COMMENT ON COLUMN "public"."erp_authentications"."accept_language" IS 'Accept-Language header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."accept_encoding" IS 'Accept-Encoding header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."origin" IS 'Origin header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."referrer" IS 'Referrer header value of the client';
COMMENT ON COLUMN "public"."erp_authentications"."location" IS 'Approximate geographic location of the client';
COMMENT ON COLUMN "public"."erp_authentications"."created_at" IS 'Timestamp when the authentication was created';
COMMENT ON COLUMN "public"."erp_authentications"."last_update_at" IS 'Last time the authentication was updated';
COMMENT ON COLUMN "public"."erp_authentications"."blacklisted" IS 'Indicates whether the authentication is blacklisted';

-- ----------------------------
-- Records of erp_authentications
-- ----------------------------
INSERT INTO "public"."erp_authentications" VALUES ('ae8cae4a-6353-4b32-8af3-37cde47c3ffe', 'e4461d77-2832-47d9-81ca-8c3b401cde56', '127.0.0.1', '1d1f74f140894371b28a830764200e3b', 'postmanruntime/2.7.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-19 10:40:42.57074+00', '2026-09-19 10:40:56.273987+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('20ece580-9671-4805-abfd-3ed1c592527e', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '1d1f74f140894371b28a830764200e3b', 'postmanruntime/2.7.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-19 10:42:01.081133+00', '2026-09-19 10:42:06.127162+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('69c8c729-0147-4a9d-b8a4-f8c101362133', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'fd92422e4a914cfb96c1378a7be0546b', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:06:51.794351+00', '2026-09-20 12:06:51.794357+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('7b680c5c-862b-4fe8-927c-f67ace8fdbeb', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e43cec10dbb54589913b15b9f7f06403', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:06:55.709662+00', '2026-09-20 12:06:55.709669+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('841960cb-5ae5-4dfc-9925-d54253c3c7f6', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ea47becab8d840eeb6b2cef89861b4bb', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:07:03.534772+00', '2026-09-20 12:07:03.534778+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('ec06acf2-a98d-4acc-a6ab-3ae54b50ea13', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '1484632c220c45d2b8c8b30817dd27af', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-20 03:16:54.120331+00', '2026-09-20 03:16:54.120355+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('058631bc-a44b-42d9-b80e-0f7c0b5f3b59', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e34964145e0240389f74df1720b1e907', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-20 03:16:58.162684+00', '2026-09-20 03:16:58.162689+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('74299931-d9d2-41dd-97c4-d753ceaa5ade', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '41b0d6a533a14811949a9f72f7c45921', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:07:04.589759+00', '2026-09-20 12:07:04.589763+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('0aafb99a-9692-4be5-8e2f-8b13123f24ec', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '101266d4097e401481448edfdfb11ba7', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:07:06.068767+00', '2026-09-20 12:07:06.068773+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('af5cc3fe-1467-4a14-b805-c141a5336708', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '109d3e4e73e94cca8cef3a43f7279730', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', NULL, 'http://localhost:8000', 'http://localhost:8000/docs', NULL, '2026-09-21 13:15:56.991312+00', '2026-09-21 14:59:26.30405+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('d4d81f45-1933-449e-a209-83bba2b76046', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ef1424796132439281fffbd6cbf111a4', 'postmanruntime/2.7.0', NULL, NULL, '', NULL, NULL, '2026-09-21 12:42:10.060523+00', '2026-09-21 15:05:00.638853+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('60458107-c2c9-4636-9f1e-25eccc582984', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '1f43006ef2004dc983edf08221db632a', 'postmanruntime/2.7.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-20 03:11:59.957678+00', '2026-09-20 12:56:39.346261+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('93617966-e97b-4458-87ca-ad49d8787422', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '6408d273659e46549ecfbbd1f298b636', 'postmanruntime/2.7.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-21 03:57:55.095801+00', '2026-09-21 06:11:27.221943+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('61024cf3-ecef-41ca-b6b5-c61c970b35ad', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '3778318dafa74b4f891ddf4d9e342c51', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', NULL, 'http://localhost:8000', 'http://localhost:8000/docs', NULL, '2026-09-21 04:19:45.852126+00', '2026-09-21 04:19:45.85213+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('9a1e48ca-62da-47cb-a549-21ab54098816', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '0508e10450164669a3a3cca4adbbaa79', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:34:22.148914+00', '2026-09-20 04:34:22.148921+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('989e6a2b-5b4c-48d9-bfa5-c8892dae9ec6', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '497e5f83ac60425288a62e10851c7c8e', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:34:40.010784+00', '2026-09-20 04:34:40.010789+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('aad3cc4d-2d14-4a79-abfe-0e4f75fcaf30', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ce9a6c206ba74e1d95b4b2834c900c06', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:34:51.416936+00', '2026-09-20 04:34:51.416941+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('9d890261-0de3-41c7-9d08-cac81e610677', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'c8e36c09d3ee4131a6d29c87ac8d5471', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:37:11.863771+00', '2026-09-20 04:37:11.863777+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('d7d55c99-8e19-40e5-96d9-a7fce0b361dc', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'b852ca48d06a4cfb9f8912ad77d57c2a', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:44:44.426776+00', '2026-09-20 04:44:44.426782+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('cbde52c7-b85e-49fc-a15a-2fdb32211fc9', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '9c0b4cdcc1b449a1b2baea74e0182d26', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 05:02:27.971893+00', '2026-09-20 05:02:27.971898+00', 'f', NULL, 'local');

-- ----------------------------
-- Table structure for erp_hardware_keys
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_hardware_keys";
CREATE TABLE "public"."erp_hardware_keys" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "credential_id" text COLLATE "pg_catalog"."default" NOT NULL,
  "public_key" text COLLATE "pg_catalog"."default" NOT NULL,
  "algorithm" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'ES256'::character varying,
  "sign_count" int4 NOT NULL DEFAULT 0,
  "transports" jsonb,
  "aaguid" varchar(64) COLLATE "pg_catalog"."default",
  "name" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "last_used_at" timestamptz(6),
  "disabled" bool NOT NULL DEFAULT false
)
;

-- ----------------------------
-- Records of erp_hardware_keys
-- ----------------------------

-- ----------------------------
-- Table structure for erp_keys
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_keys";
CREATE TABLE "public"."erp_keys" (
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "prefix" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
  "last_four" varchar(4) COLLATE "pg_catalog"."default" NOT NULL,
  "hashed_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "expires_at" timestamptz(6),
  "last_used_at" timestamptz(6),
  "created_by" uuid NOT NULL,
  "updated_by" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_keys"."name" IS 'Human-readable name of the API key';
COMMENT ON COLUMN "public"."erp_keys"."description" IS 'Optional description of the API key';
COMMENT ON COLUMN "public"."erp_keys"."prefix" IS 'Public, non-secret identifier fragment of the key';
COMMENT ON COLUMN "public"."erp_keys"."last_four" IS 'Last four characters of the raw key, for masked display';
COMMENT ON COLUMN "public"."erp_keys"."hashed_key" IS 'HMAC-SHA256 hash of the raw key; the raw key is never stored';
COMMENT ON COLUMN "public"."erp_keys"."expires_at" IS 'Expiration timestamp of the key; null means it never expires';
COMMENT ON COLUMN "public"."erp_keys"."last_used_at" IS 'Timestamp of the last time the key was used to authenticate';
COMMENT ON COLUMN "public"."erp_keys"."created_by" IS 'Identifier of the user who created the key';
COMMENT ON COLUMN "public"."erp_keys"."updated_by" IS 'Identifier of the user who last updated the key';
COMMENT ON COLUMN "public"."erp_keys"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."erp_keys"."is_active" IS 'Indicates whether the record is active';
COMMENT ON COLUMN "public"."erp_keys"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."erp_keys"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of erp_keys
-- ----------------------------
INSERT INTO "public"."erp_keys" VALUES ('CI pipeline', 'Used by the CI pipeline to publish releases.', 'iap', 'xyFo', 'fd2e2fb52e8010f8cb2848a50ca4a289664c3b338243da23ad4eac97886d056a', '2026-10-21 15:00:32.559927+00', NULL, '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '16a113dd-c1e4-4e08-8576-b04a61656ddb', 't', '2026-09-21 15:00:32.570304+00', '2026-09-21 15:00:32.570319+00');
INSERT INTO "public"."erp_keys" VALUES ('CI pipeline renomeada', 'Na api', 'iap', 'rfbQ', '7e3f13677cdc9a5c971f44445fc445d84e5a68401c6d9997f7fe5f646d71a297', '2027-03-20 15:01:48.031147+00', NULL, '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '99237e05-c08e-46ae-8670-7078e8c90f49', 'f', '2026-09-21 15:01:48.038822+00', '2026-09-21 15:08:01.689148+00');
INSERT INTO "public"."erp_keys" VALUES ('CI pipeline renomeada', 'Na api', 'iap', 'z5vc', 'd549f278d3247ac71f8e22d80eeea5cee68cf9d7a279f5756d10bd95d6eb0532', '2027-03-20 15:08:19.033851+00', NULL, '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '5be5512d-6f21-451e-aa97-608f7d5d5609', 't', '2026-09-21 15:08:19.041839+00', '2026-09-21 15:08:40.671176+00');

-- ----------------------------
-- Table structure for erp_knowledges
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_knowledges";
CREATE TABLE "public"."erp_knowledges" (
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_by" uuid NOT NULL,
  "updated_by" uuid NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_knowledges"."name" IS 'Unique name of the knowledge record';
COMMENT ON COLUMN "public"."erp_knowledges"."description" IS 'Detailed description of the knowledge record';
COMMENT ON COLUMN "public"."erp_knowledges"."created_by" IS 'Identifier of the user who created the record';
COMMENT ON COLUMN "public"."erp_knowledges"."updated_by" IS 'Identifier of the user who last updated the record';
COMMENT ON COLUMN "public"."erp_knowledges"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."erp_knowledges"."is_active" IS 'Indicates whether the record is active';
COMMENT ON COLUMN "public"."erp_knowledges"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."erp_knowledges"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of erp_knowledges
-- ----------------------------
INSERT INTO "public"."erp_knowledges" VALUES ('Machine Learning Fundamentals', 'A collection of resources on machine learning fundamentals.', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '3e1c67cc-94ee-40b5-a725-8dc828106f75', 't', '2026-09-21 15:08:50.688998+00', '2026-09-21 15:08:50.689007+00');
INSERT INTO "public"."erp_knowledges" VALUES ('Machine Learning Fundamentals v2', 'Descricao atualizada.', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '100b5c8b-a777-45db-97c4-cae0140ee339', 't', '2026-09-21 15:09:21.112174+00', '2026-09-21 15:09:47.88845+00');

-- ----------------------------
-- Table structure for erp_notifications
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_notifications";
CREATE TABLE "public"."erp_notifications" (
  "user_id" uuid NOT NULL,
  "notification_type" "public"."notification_type_enum" NOT NULL,
  "title" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "body" text COLLATE "pg_catalog"."default" NOT NULL,
  "redirect_url" varchar(2048) COLLATE "pg_catalog"."default",
  "metadata" jsonb,
  "originated_from_broadcast" varchar(20) COLLATE "pg_catalog"."default",
  "is_read" bool NOT NULL DEFAULT false,
  "read_at" timestamptz(6),
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_notifications"."user_id" IS 'Identifier of the user who receives this notification';
COMMENT ON COLUMN "public"."erp_notifications"."notification_type" IS 'Event type that triggered this notification';
COMMENT ON COLUMN "public"."erp_notifications"."title" IS 'Short title of the notification';
COMMENT ON COLUMN "public"."erp_notifications"."body" IS 'Full body text of the notification';
COMMENT ON COLUMN "public"."erp_notifications"."redirect_url" IS 'Optional URL for deep linking from the notification';
COMMENT ON COLUMN "public"."erp_notifications"."metadata" IS 'Optional JSON payload with internal context data (resource_id, etc.)';
COMMENT ON COLUMN "public"."erp_notifications"."originated_from_broadcast" IS 'Role targeted by the fan-out broadcast that created this notification, if any';
COMMENT ON COLUMN "public"."erp_notifications"."is_read" IS 'Whether the user has read this notification';
COMMENT ON COLUMN "public"."erp_notifications"."read_at" IS 'Timestamp when the notification was marked as read';
COMMENT ON COLUMN "public"."erp_notifications"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."erp_notifications"."is_active" IS 'Indicates whether the record is active';
COMMENT ON COLUMN "public"."erp_notifications"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."erp_notifications"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of erp_notifications
-- ----------------------------
INSERT INTO "public"."erp_notifications" VALUES ('0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'KNOWLEDGE_CREATED', 'Knowledge base created', 'Knowledge base ''Machine Learning Fundamentals'' was created by System Admin (Admin).', NULL, NULL, 'manager', 'f', NULL, '951f36cf-8144-4c58-94c8-b84c3d7627ea', 't', '2026-09-21 15:08:50.681351+00', '2026-09-21 15:08:50.681351+00');
INSERT INTO "public"."erp_notifications" VALUES ('0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 'KNOWLEDGE_CREATED', 'Knowledge base created', 'Knowledge base ''Machine Learning Fundamentals IoT'' was created by System Admin (Admin).', NULL, NULL, 'manager', 'f', NULL, 'f7bfc2fa-9853-46d3-948c-2d3ce27b2e24', 't', '2026-09-21 15:09:21.108396+00', '2026-09-21 15:09:21.108396+00');

-- ----------------------------
-- Table structure for erp_oauth2_accounts
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_oauth2_accounts";
CREATE TABLE "public"."erp_oauth2_accounts" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "provider" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "provider_user_id" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(255) COLLATE "pg_catalog"."default",
  "access_token" text COLLATE "pg_catalog"."default",
  "refresh_token" text COLLATE "pg_catalog"."default",
  "expires_at" timestamptz(6),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;

-- ----------------------------
-- Records of erp_oauth2_accounts
-- ----------------------------

-- ----------------------------
-- Table structure for erp_refresh_tokens
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_refresh_tokens";
CREATE TABLE "public"."erp_refresh_tokens" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "authentication_id" uuid NOT NULL,
  "hashed_jti" text COLLATE "pg_catalog"."default" NOT NULL,
  "previous_hashed_jti" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6) NOT NULL,
  "revoked" bool NOT NULL,
  "revoked_at" timestamptz(6)
)
;
COMMENT ON COLUMN "public"."erp_refresh_tokens"."id" IS 'Unique identifier of the refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."authentication_id" IS 'Authentication associated with this refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."hashed_jti" IS 'Hashed JTI (JWT ID) value';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."previous_hashed_jti" IS 'Hashed JTI (JWT ID) value of the previous refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."created_at" IS 'Timestamp when the refresh token was created';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."updated_at" IS 'Timestamp when the record was last updated';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."expires_at" IS 'Expiration timestamp of the refresh token';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."revoked" IS 'Indicates whether the refresh token was revoked';
COMMENT ON COLUMN "public"."erp_refresh_tokens"."revoked_at" IS 'Timestamp when the refresh token was revoked';

-- ----------------------------
-- Records of erp_refresh_tokens
-- ----------------------------
INSERT INTO "public"."erp_refresh_tokens" VALUES ('942fb32b-99b2-4d14-87ad-70b21759e7d8', 'ae8cae4a-6353-4b32-8af3-37cde47c3ffe', 'cef0d1a9bf623ec0c2da67122ca077350fcf7bd12606840c536c8dcc973c627e', 'c6faab6fc726a2b3767d1f16086658cab8872c4dc2aeaec115e6c0ae4e9b4ad5', '2026-09-19 10:40:42.495751+00', '2026-09-19 10:40:56.273987+00', '2026-09-26 10:40:56.273987+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('f2e6a9a0-a33c-4f90-84b7-b8ea7e280118', '20ece580-9671-4805-abfd-3ed1c592527e', '045d26b70b9d79459bf8e6c4aac3c4d4cffcfb748c8ee04682af014c3ce22e9b', '1300868bdee126a77cb71724cbc0b7768b6290841517a589a0437a041c297bdc', '2026-09-19 10:42:01.07663+00', '2026-09-19 10:42:06.127162+00', '2026-09-26 10:42:06.127162+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('67fa2957-4650-4e2f-aa1d-a9ebd401153b', 'ec06acf2-a98d-4acc-a6ab-3ae54b50ea13', '1626d36e58804b65c1beccb64f87c8f70dde9969f2ae785356d80616300e33fa', NULL, '2026-09-20 03:16:54.114949+00', '2026-09-20 03:16:54.114949+00', '2026-09-27 03:16:54.114949+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('3a680b04-04cc-4bbe-9ebb-84e659b78952', '058631bc-a44b-42d9-b80e-0f7c0b5f3b59', 'a98cd1a3269cec3be0539263697707f33b3fc6a0001cafd317f40affbd92fac4', NULL, '2026-09-20 03:16:58.159196+00', '2026-09-20 03:16:58.159196+00', '2026-09-27 03:16:58.159196+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('ad1f20bf-14e1-4993-a271-c25084b6df13', '69c8c729-0147-4a9d-b8a4-f8c101362133', '1be8ee4af05904122c501f19d1b78b63c0d952f0f19d256c7d19b543b6ffe85c', NULL, '2026-09-20 12:06:51.790621+00', '2026-09-20 12:06:51.790621+00', '2026-09-27 12:06:51.790621+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('55ad1881-f904-4745-8595-2e7757835628', '7b680c5c-862b-4fe8-927c-f67ace8fdbeb', '050ffbb4a8efd3f93f36e86ef0598d4d8e922b50e8692b1d44ce1523d834dc5a', NULL, '2026-09-20 12:06:55.70572+00', '2026-09-20 12:06:55.70572+00', '2026-09-27 12:06:55.70572+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('8c90f2e2-2b6d-4462-8d10-f5539d6d732e', '841960cb-5ae5-4dfc-9925-d54253c3c7f6', '9cccd0277a3fb227bf80a99fa216774dd77173f5bf81a3cc232c7c510dbacb33', NULL, '2026-09-20 12:07:03.531524+00', '2026-09-20 12:07:03.531524+00', '2026-09-27 12:07:03.531524+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('2e999b19-6eae-4b15-84bb-9578805485ac', '74299931-d9d2-41dd-97c4-d753ceaa5ade', '10d77c07e2a1ebc9b29d1a7a614e5e5cd841de5340ebf051d6177debe99a159c', NULL, '2026-09-20 12:07:04.586201+00', '2026-09-20 12:07:04.586201+00', '2026-09-27 12:07:04.586201+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('f6f10b5a-6f54-4b00-a865-a242a5a2d811', '9a1e48ca-62da-47cb-a549-21ab54098816', '17894dde81b9a648bead0af53409f0634c1afc4bc463e1fe641211dd61d67d0b', NULL, '2026-09-20 04:34:22.132496+00', '2026-09-20 04:34:22.132496+00', '2026-09-27 04:34:22.132496+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('5d5ec304-be7b-4635-8f08-62951e5970d2', '989e6a2b-5b4c-48d9-bfa5-c8892dae9ec6', '5d2b2bcd9a09a6deaea98623686d059071721035f59d6de451c8c78a1db5b51a', NULL, '2026-09-20 04:34:40.006493+00', '2026-09-20 04:34:40.006493+00', '2026-09-27 04:34:40.006493+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('8460f833-8f5a-4e6d-a0c0-edd2d6176e19', 'aad3cc4d-2d14-4a79-abfe-0e4f75fcaf30', '7e9854a9849ff64cc19fdf3426bfa99c1958e058cb432e301729672b971ee742', NULL, '2026-09-20 04:34:51.412929+00', '2026-09-20 04:34:51.412929+00', '2026-09-27 04:34:51.412929+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('9bf8e90b-239a-4d7e-879c-da57ff8baf24', '9d890261-0de3-41c7-9d08-cac81e610677', '13e4b59cfee8479f210ade70a09def10d91c2159aaa2b56f15c2276b4a23c0d7', NULL, '2026-09-20 04:37:11.858977+00', '2026-09-20 04:37:11.858977+00', '2026-09-27 04:37:11.858977+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('e995fd97-1612-4c3e-9653-9629cb577bab', 'd7d55c99-8e19-40e5-96d9-a7fce0b361dc', 'eaac1108caebbcfe1cd40ea2235a9b6052159e17a9be5fd60aa83d29c8f43a1d', NULL, '2026-09-20 04:44:44.422011+00', '2026-09-20 04:44:44.422011+00', '2026-09-27 04:44:44.422011+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('bd2c201c-ddfb-42cf-a19b-809a779116d0', 'cbde52c7-b85e-49fc-a15a-2fdb32211fc9', 'c900f4f6d09fb0dbf4d5d0bf6e2d6bb75bfd3bdf2c042b264158f7edf211bc0e', NULL, '2026-09-20 05:02:27.967339+00', '2026-09-20 05:02:27.967339+00', '2026-09-27 05:02:27.967339+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('bbb7a2db-8190-4c69-be46-3f9d66a9967a', '0aafb99a-9692-4be5-8e2f-8b13123f24ec', 'c9b221513838161bf816d8e78cd94ac1334a5a47f4428282630124e2e273ed4c', NULL, '2026-09-20 12:07:06.063783+00', '2026-09-20 12:07:06.063783+00', '2026-09-27 12:07:06.063783+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('3af8d814-e838-4999-9738-f54d9c30de36', '61024cf3-ecef-41ca-b6b5-c61c970b35ad', 'bbe9a944bc4b5a3489a369d01e184171b15ffbf6e0c4d85eb8ddee5896db1c6c', NULL, '2026-09-21 04:19:45.848112+00', '2026-09-21 04:19:45.848112+00', '2026-09-28 04:19:45.848112+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('7ae53838-3c47-42d5-9df2-a3d19d85c98a', '93617966-e97b-4458-87ca-ad49d8787422', 'bc6d25460edb8007197d03323b2599e37eebbd6bdca46d2abeef08be353234fe', 'e2776367f6c58ab6c4085657713bdc4bca295556c42675131266ed8ccbede726', '2026-09-21 03:57:55.017354+00', '2026-09-21 06:11:27.221943+00', '2026-09-28 06:11:27.221943+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('8404b67b-7c39-4e1f-a675-69430bf46883', 'af5cc3fe-1467-4a14-b805-c141a5336708', '84252a6028e82ef70464f34e62fb76a627a6847921e2c8cbb3f3966b6269d385', '28e6e5813fb5fda757fcea7dfe9b42bbc29c6f4f6a7e4c99df7c959a1c706d42', '2026-09-21 13:15:56.934067+00', '2026-09-21 14:59:26.30405+00', '2026-09-28 14:59:26.30405+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('a586628c-de2f-4313-83c2-542ad875441d', 'd4d81f45-1933-449e-a209-83bba2b76046', 'a9460a5acd6a5e9b553ef847239ba5e849ebadf150125e05f097c883d49a3a09', '99b463cad88444438a1823342c1405411929fed61b14fddf8225c162aac24440', '2026-09-21 12:42:10.011002+00', '2026-09-21 15:05:00.638853+00', '2026-09-28 15:05:00.638853+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('5da71da1-279f-4411-8616-566adfc91dfd', '60458107-c2c9-4636-9f1e-25eccc582984', '2c7bd5a384212eac68dc7e23fdcd1793cb9da07f21830f91317d37f2d04d57af', '941f80647d7ff673f1355d13464f78e3584501f9c34acf1f3feee74f620b80d7', '2026-09-20 03:11:59.891576+00', '2026-09-20 12:56:39.346261+00', '2026-09-27 12:56:39.346261+00', 'f', NULL);

-- ----------------------------
-- Table structure for erp_token_revocations
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_token_revocations";
CREATE TABLE "public"."erp_token_revocations" (
  "jti" uuid NOT NULL,
  "user_id" uuid,
  "reason" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'manual'::character varying,
  "revoked_at" timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at" timestamptz(6)
)
;

-- ----------------------------
-- Records of erp_token_revocations
-- ----------------------------

-- ----------------------------
-- Table structure for erp_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."erp_users";
CREATE TABLE "public"."erp_users" (
  "first_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "last_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "preferred_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "gender" "public"."gender_enum",
  "birthdate" date,
  "email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "phone" varchar(18) COLLATE "pg_catalog"."default",
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "role" "public"."role_enum" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now()
)
;
COMMENT ON COLUMN "public"."erp_users"."first_name" IS 'First name of the user';
COMMENT ON COLUMN "public"."erp_users"."last_name" IS 'Last name of the user';
COMMENT ON COLUMN "public"."erp_users"."preferred_name" IS 'Preferred name of the user';
COMMENT ON COLUMN "public"."erp_users"."gender" IS 'Gender of the user';
COMMENT ON COLUMN "public"."erp_users"."birthdate" IS 'Birthdate of the user';
COMMENT ON COLUMN "public"."erp_users"."email" IS 'Email address of the user';
COMMENT ON COLUMN "public"."erp_users"."phone" IS 'Phone number of the user';
COMMENT ON COLUMN "public"."erp_users"."hashed_password" IS 'Hashed password of the user';
COMMENT ON COLUMN "public"."erp_users"."role" IS 'Role of the user';
COMMENT ON COLUMN "public"."erp_users"."id" IS 'Unique identifier of the record';
COMMENT ON COLUMN "public"."erp_users"."is_active" IS 'Indicates whether the record is active';
COMMENT ON COLUMN "public"."erp_users"."created_at" IS 'Timestamp when the record was created';
COMMENT ON COLUMN "public"."erp_users"."updated_at" IS 'Timestamp when the record was last updated';

-- ----------------------------
-- Records of erp_users
-- ----------------------------
INSERT INTO "public"."erp_users" VALUES ('John', 'Doe', 'Joe', 'MALE', '1995-01-01', 'johndoe@example.com', '+555472664275', '$argon2id$v=19$m=65536,t=3,p=4$pY4vzkacysRTP3HxJ+KIpg$FY9VHAxN1GFlFv6cB8Mx/xXg/js6ZkZ5zkAmmOXu55I', 'USER', 'e4461d77-2832-47d9-81ca-8c3b401cde56', 't', '2026-09-19 10:39:43.245882+00', '2026-09-19 10:39:43.245896+00');
INSERT INTO "public"."erp_users" VALUES ('System', 'Admin', 'Admin', 'OTHER', '1990-01-01', 'admin@example.com', NULL, '$argon2id$v=19$m=65536,t=3,p=4$pY4vzkacysRTP3HxJ+KIpg$FY9VHAxN1GFlFv6cB8Mx/xXg/js6ZkZ5zkAmmOXu55I', 'ADMIN', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', 't', '2026-09-19 08:57:37.641459+00', '2026-09-19 08:57:37.641459+00');
INSERT INTO "public"."erp_users" VALUES ('Demo', 'Demo', 'Demo', NULL, NULL, 'demo@example.com', '+566988522431', '$argon2id$v=19$m=65536,t=3,p=4$6NtcZ305D6WjsCDZE01ZOg$/6/IH9L4zv1XDWU3NXt8Lw6AAQ1ghXsTEi6XkRIAe5o', 'USER', '0d610b48-e83a-4e81-8a25-d43296bf4521', 't', '2026-09-21 14:10:34.900342+00', '2026-09-21 14:10:34.900353+00');
INSERT INTO "public"."erp_users" VALUES ('System', 'App', 'System', NULL, NULL, 'system@example.com', '+566988522431', '$argon2id$v=19$m=65536,t=3,p=4$fM6oE5Mojpu94NjdMLPq3w$a+/ThCIoss0w+PnZU9ZAKLMnZuBFdaTiRR6HT3dPMkE', 'USER', 'd767edfd-e087-4885-9486-ffdc708d859d', 't', '2026-09-21 14:13:57.66594+00', '2026-09-21 14:13:57.665957+00');
INSERT INTO "public"."erp_users" VALUES ('Asdemo', 'Aj asdemo', 'Asdemo', 'MALE', '1995-01-01', 'app@example.com', '+555472664275', '$argon2id$v=19$m=65536,t=3,p=4$tB7nBMxilA5+Np0rj+M0Sw$vlgOK6rjTacfdm1JMmnImYzwwKyRuhmjlgq74RR1gPI', 'USER', 'f5ce21c6-7743-4046-bddd-e111f1928ab5', 't', '2026-09-21 14:55:01.275258+00', '2026-09-21 14:55:01.275282+00');

-- ----------------------------
-- Function structure for set_updated_at
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_updated_at"();
CREATE FUNCTION "public"."set_updated_at"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Primary Key structure for table alembic_version
-- ----------------------------
ALTER TABLE "public"."alembic_version" ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");

-- ----------------------------
-- Indexes structure for table erp_access_tokens
-- ----------------------------
CREATE INDEX "ix_access_tokens_hashed_jti_revoked" ON "public"."erp_access_tokens" USING btree (
  "hashed_jti" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "revoked" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_access_tokens
-- ----------------------------
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_hashed_jti_key" UNIQUE ("hashed_jti");
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_previous_hashed_jti_key" UNIQUE ("previous_hashed_jti");
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "uq_access_tokens_refresh_id" UNIQUE ("refresh_id");

-- ----------------------------
-- Primary Key structure for table erp_access_tokens
-- ----------------------------
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_authentications
-- ----------------------------
CREATE INDEX "ix_authentications_user_id_user_agent_device" ON "public"."erp_authentications" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "user_agent" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "device" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_authentications
-- ----------------------------
ALTER TABLE "public"."erp_authentications" ADD CONSTRAINT "uq_authentications_user_id_user_agent_device" UNIQUE ("user_id", "user_agent", "device");

-- ----------------------------
-- Primary Key structure for table erp_authentications
-- ----------------------------
ALTER TABLE "public"."erp_authentications" ADD CONSTRAINT "erp_authentications_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_hardware_keys
-- ----------------------------
CREATE INDEX "ix_hardware_keys_user_id" ON "public"."erp_hardware_keys" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_hardware_keys
-- ----------------------------
ALTER TABLE "public"."erp_hardware_keys" ADD CONSTRAINT "uq_hardware_keys_credential_id" UNIQUE ("credential_id");

-- ----------------------------
-- Primary Key structure for table erp_hardware_keys
-- ----------------------------
ALTER TABLE "public"."erp_hardware_keys" ADD CONSTRAINT "erp_hardware_keys_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_keys
-- ----------------------------
CREATE INDEX "ix_keys_created_by" ON "public"."erp_keys" USING btree (
  "created_by" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_keys_prefix" ON "public"."erp_keys" USING btree (
  "prefix" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_keys_updated_by" ON "public"."erp_keys" USING btree (
  "updated_by" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_keys
-- ----------------------------
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "uq_keys_hashed_key" UNIQUE ("hashed_key");

-- ----------------------------
-- Primary Key structure for table erp_keys
-- ----------------------------
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "erp_keys_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_knowledges
-- ----------------------------
CREATE INDEX "ix_knowledges_created_by" ON "public"."erp_knowledges" USING btree (
  "created_by" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_knowledges_name_is_active" ON "public"."erp_knowledges" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_knowledges_updated_by" ON "public"."erp_knowledges" USING btree (
  "updated_by" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_knowledges
-- ----------------------------
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table erp_knowledges
-- ----------------------------
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_notifications
-- ----------------------------
CREATE INDEX "ix_notifications_user_id_is_active" ON "public"."erp_notifications" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_notifications_user_id_is_read" ON "public"."erp_notifications" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST,
  "is_read" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table erp_notifications
-- ----------------------------
ALTER TABLE "public"."erp_notifications" ADD CONSTRAINT "erp_notifications_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_oauth2_accounts
-- ----------------------------
CREATE INDEX "ix_oauth2_accounts_user_id" ON "public"."erp_oauth2_accounts" USING btree (
  "user_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_oauth2_accounts
-- ----------------------------
ALTER TABLE "public"."erp_oauth2_accounts" ADD CONSTRAINT "uq_oauth2_accounts_provider_user" UNIQUE ("provider", "provider_user_id");

-- ----------------------------
-- Primary Key structure for table erp_oauth2_accounts
-- ----------------------------
ALTER TABLE "public"."erp_oauth2_accounts" ADD CONSTRAINT "erp_oauth2_accounts_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_refresh_tokens
-- ----------------------------
CREATE INDEX "ix_refresh_tokens_hashed_jti_revoked" ON "public"."erp_refresh_tokens" USING btree (
  "hashed_jti" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "revoked" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "uq_refresh_tokens_authentication_id" UNIQUE ("authentication_id");
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "erp_refresh_tokens_hashed_jti_key" UNIQUE ("hashed_jti");

-- ----------------------------
-- Primary Key structure for table erp_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "erp_refresh_tokens_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table erp_token_revocations
-- ----------------------------
CREATE INDEX "ix_token_revocations_expires_at" ON "public"."erp_token_revocations" USING btree (
  "expires_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table erp_token_revocations
-- ----------------------------
ALTER TABLE "public"."erp_token_revocations" ADD CONSTRAINT "erp_token_revocations_pkey" PRIMARY KEY ("jti");

-- ----------------------------
-- Indexes structure for table erp_users
-- ----------------------------
CREATE INDEX "ix_users_email_is_active" ON "public"."erp_users" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST,
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table erp_users
-- ----------------------------
ALTER TABLE "public"."erp_users" ADD CONSTRAINT "erp_users_email_key" UNIQUE ("email");

-- ----------------------------
-- Primary Key structure for table erp_users
-- ----------------------------
ALTER TABLE "public"."erp_users" ADD CONSTRAINT "erp_users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table erp_access_tokens
-- ----------------------------
ALTER TABLE "public"."erp_access_tokens" ADD CONSTRAINT "erp_access_tokens_refresh_id_fkey" FOREIGN KEY ("refresh_id") REFERENCES "public"."erp_refresh_tokens" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_authentications
-- ----------------------------
ALTER TABLE "public"."erp_authentications" ADD CONSTRAINT "erp_authentications_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."erp_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_hardware_keys
-- ----------------------------
ALTER TABLE "public"."erp_hardware_keys" ADD CONSTRAINT "erp_hardware_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."erp_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_keys
-- ----------------------------
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "erp_keys_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;
ALTER TABLE "public"."erp_keys" ADD CONSTRAINT "erp_keys_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_knowledges
-- ----------------------------
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;
ALTER TABLE "public"."erp_knowledges" ADD CONSTRAINT "erp_knowledges_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."erp_users" ("id") ON DELETE RESTRICT ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_notifications
-- ----------------------------
ALTER TABLE "public"."erp_notifications" ADD CONSTRAINT "erp_notifications_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."erp_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_oauth2_accounts
-- ----------------------------
ALTER TABLE "public"."erp_oauth2_accounts" ADD CONSTRAINT "erp_oauth2_accounts_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."erp_users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table erp_refresh_tokens
-- ----------------------------
ALTER TABLE "public"."erp_refresh_tokens" ADD CONSTRAINT "erp_refresh_tokens_authentication_id_fkey" FOREIGN KEY ("authentication_id") REFERENCES "public"."erp_authentications" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
