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

 Date: 21/09/2026 23:56:51
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
INSERT INTO "public"."erp_access_tokens" VALUES ('325d0894-6097-47c8-9499-ae41d89b618b', 'a586628c-de2f-4313-83c2-542ad875441d', 'ad833deca09b3847cc8d7e0640902428d74d81253142c17308287cac0386a548', '649ccd42bb1f39932dc33519e74137cc3d1577e30ab5f14dbc9e02873bca489c', 'ADMIN', '2026-09-21 16:54:04.845451+00', '2026-09-21 17:09:04.845451+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('30af19ef-e067-4148-9a88-90f013afe198', '8404b67b-7c39-4e1f-a675-69430bf46883', '19f91bc0890656d1c4c8d8637bd47e6052c9b13d5a0fb534e388adb7e87a6cb8', '068b44edc13cd874721a47cd6b0136e9d0cd54717f0f0eca9f5e6ae3fa27b070', 'ADMIN', '2026-09-21 16:54:57.629084+00', '2026-09-21 17:09:57.629084+00', 'f', NULL);
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
INSERT INTO "public"."erp_access_tokens" VALUES ('31922602-4836-44f3-9918-78d2af13a811', '7b981bef-c513-418d-b463-0574133456c1', 'c8eba84e7fd23e1f0f75eab65f531732a1d3f02d9e98fc67892137036e70738d', NULL, 'ADMIN', '2026-09-21 15:57:07.09206+00', '2026-09-21 16:12:07.09206+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('a5c6a4f2-61e5-4598-9558-61757c59fdd7', '52bf0019-9159-4c38-bffc-ed0e4364d601', 'df8815402544576aacc1564afac28400cfbd64ffc97225831e91c508ac2390f1', NULL, 'ADMIN', '2026-09-21 15:57:11.291517+00', '2026-09-21 16:12:11.291517+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('4179c82a-f168-4873-8fe3-a731b3a8ca5a', '5da71da1-279f-4411-8616-566adfc91dfd', '0a029b68c081123f3b9e0357d4e602201c835b9ffe5b8f1ec787e977f4c747df', '4841adb34d623b335443dbe9d671e61c3d74dae04c656b7e5827227d3c66f579', 'ADMIN', '2026-09-20 12:56:39.346261+00', '2026-09-20 13:11:39.346261+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('227f5658-c0e8-481a-907b-59f420095025', 'a2689ef3-9f38-46a4-b9d1-9b7d5df420be', '947cfce6f92fa4afaf31b3f8114895bab53bd8d2bf5d44c69e8a52459b0e222d', NULL, 'ADMIN', '2026-09-21 16:10:07.568387+00', '2026-09-21 16:25:07.568387+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('65849cc9-5bc4-450b-a89b-46166a909759', '75bbe805-e6c9-4f12-a000-517684fbfdf7', '7c4c0dbb0872cd2beb5162f2ce78a44f075a8e40b3d84b37084807a0b711dfda', NULL, 'ADMIN', '2026-09-21 16:10:09.263175+00', '2026-09-21 16:25:09.263175+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('bd2539c6-c8cf-40b5-a3b0-7beffc24b826', 'c71c2acc-1b3c-4552-8d7c-337119538ebd', '20c4564184dd66e057c55ee5e47e4e2b2f8409f85423f915118361effe5be4e2', NULL, 'ADMIN', '2026-09-21 16:10:10.623122+00', '2026-09-21 16:25:10.623122+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('40040aa6-2282-4922-8bb8-fda4a4df2cb5', 'eddd3e8f-034d-434b-9e0b-01c304b46146', 'ec71dabef39b2f8d5da95f5853ad259880aeb11ca74bfbd8b38a1e14055631e8', NULL, 'ADMIN', '2026-09-21 16:10:25.315708+00', '2026-09-21 16:25:25.315708+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('63018c90-e1f9-40a8-9ad3-f5bd610893ef', 'de401b4b-6bda-4b55-8a66-c3afa90dec6a', '17ed919e4f266b542697f545d82b18d78fa076df9ab6914e5bd1eb4f14c84193', NULL, 'ADMIN', '2026-09-21 16:10:28.97788+00', '2026-09-21 16:25:28.97788+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('b096d03c-9240-4aa5-9b83-f45796e30ec4', '2f84d91b-1876-48ce-ad34-adf1ef3c74ad', '7d55a5383b5753780e4d762e4e963ff8c55bbedfca61a351ecce8b366255b617', NULL, 'ADMIN', '2026-09-21 16:10:31.801953+00', '2026-09-21 16:25:31.801953+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('7d48f822-2063-480c-9480-16dc8a5d1401', '4a36ead8-1134-47ae-9f8a-aaf648bdb353', 'f340ae4eeb9ca09dbdf3bc3ba99cf6b22a826ce83e9b4a348befe7d8ce54803a', NULL, 'ADMIN', '2026-09-21 16:10:41.14507+00', '2026-09-21 16:25:41.14507+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('af71321b-dd70-4856-b432-901123096e24', '271c9a8e-1117-4374-a39f-309144df6db6', 'd18810ac88873698ddcd41ac01268763a99862354c64772b3038ff3205f376e4', NULL, 'ADMIN', '2026-09-21 16:10:53.634095+00', '2026-09-21 16:25:53.634095+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('7b5c53af-0871-4373-a65a-34c537592f25', '8d7573c6-2a7a-4402-ad8b-4b09c50d6fb7', 'b4b7b2bc4878186def06e28a6f8bce2c52799c41085be7d864fc64119a3e544e', NULL, 'ADMIN', '2026-09-21 16:10:54.843685+00', '2026-09-21 16:25:54.843685+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('40e21207-bf01-4172-a436-15746c89d725', 'cae7fbf9-ea71-4de9-8a02-617c157d4538', '9318fd9a1d72373baad4f5a6beb6977e4a7cbd511491cc3c82a9df7282eda169', NULL, 'ADMIN', '2026-09-21 16:10:55.967251+00', '2026-09-21 16:25:55.967251+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('db9f6871-aea8-4285-a032-d56ccc471f05', '11efe786-cbfa-4c09-a0c9-371ef49aa84b', 'b4a3bac40bcfb3987875d257c6f2671f45c9f32b6ab28f753f2afbeaf82aa241', NULL, 'ADMIN', '2026-09-21 16:10:56.635795+00', '2026-09-21 16:25:56.635795+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('e339ca97-910e-4f11-9be9-91fc9cc1b0d8', '22d0a278-424a-4dd6-8da7-a89d687fb35e', 'f9947056f43a0577cdbc9e0eec680247ccdbd5098d4504c0402390197a130777', NULL, 'ADMIN', '2026-09-21 16:10:56.809822+00', '2026-09-21 16:25:56.809822+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('36311a89-3b6f-41e7-bc27-5ebd557b4343', '36f42fea-e403-499b-85c0-b526605cebb8', '31db0be01f5674c8ce755c40ddfa798b00c3f33ae9e90023c39bfc9a076a3798', NULL, 'ADMIN', '2026-09-21 16:10:56.972842+00', '2026-09-21 16:25:56.972842+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('a2ff6176-c1a6-47f8-9e8d-edb2cca930c3', 'afa6ef49-f88f-4c73-b8fe-49b2dceaab6c', '2ac0517d0b0c6cb70de4c8d098f9616ad85617873c62326b15e1c1491ef833de', NULL, 'ADMIN', '2026-09-21 16:10:57.157737+00', '2026-09-21 16:25:57.157737+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('c47bfad9-f141-4cc7-9ab7-a2c207361c4d', '02e7f0ca-0317-402d-82c4-d0ff3ace341f', '70069d777999969d156b2492ea5e826a4a0401bf4446a2cb6ae3a8a571cb855f', NULL, 'ADMIN', '2026-09-21 16:10:57.296296+00', '2026-09-21 16:25:57.296296+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('47b84650-d9f2-4db4-b4ac-84e10161bf79', '6573a96d-01e5-46d4-9f1d-46e878e6ed5d', '7e0f86a5cf6e0da09d69f57e767a0ead253ab9cd8c55e432f202834904490b0c', NULL, 'ADMIN', '2026-09-21 16:10:57.452659+00', '2026-09-21 16:25:57.452659+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('4f5b64c8-40c6-4b3a-9b02-8f63fb0d84e4', 'e5882857-4e8c-4ee7-b124-2bdc0075f909', '332684c8671f9674abc8519fecb29f6dacb2e6da986af090bf6bc32a48e573b2', NULL, 'ADMIN', '2026-09-21 16:10:57.607892+00', '2026-09-21 16:25:57.607892+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('169895e1-883f-4455-b01e-cafd3ed776cb', 'd25930d3-02ac-4e89-8dff-4c2f791f3e55', '16bf94a6d34cade8e874ea18a1fa99d0e9494116f1d7b0dcab8f62139c25e155', NULL, 'ADMIN', '2026-09-21 16:12:18.270698+00', '2026-09-21 16:27:18.270698+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('3598d28a-68e1-4d38-886b-a090b396fb5f', 'a9d50a4a-fd9f-44d0-b274-e3253cc64efb', '24a0ddd4195bd01405a08ec29efce4f958b6ee391ce882ffa77876ffaf3fb06c', NULL, 'ADMIN', '2026-09-21 16:12:44.496509+00', '2026-09-21 16:27:44.496509+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('e870f798-c659-4d57-80cd-afbfe15c33b4', '16afd733-7cff-4f61-8b6a-d56770c407c4', '263cac3cdbf888eff3aac01263b3a3eec2e02d7bcf60079051d83886f4302442', NULL, 'ADMIN', '2026-09-21 16:16:08.685586+00', '2026-09-21 16:31:08.685586+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('5be987de-cb7b-4739-87ca-56e7302a1064', 'aca5d875-a6ac-4c39-b579-59162109eba0', '7eff10d331a694d09947e8fb6a7f406c722bf8b9d55a41f1b29d5748077593f8', NULL, 'ADMIN', '2026-09-21 16:18:46.003051+00', '2026-09-21 16:33:46.003051+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('2ca89e19-aa65-4e50-9d56-34c1a5d257a8', '632e8c80-b37a-442a-bc59-2534d4c48af2', 'd2e52516d7b6bfffce216c71936a9a378f8de77a471a5adce4a0c837515b6f6c', NULL, 'ADMIN', '2026-09-21 16:19:04.073271+00', '2026-09-21 16:34:04.073271+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('40d91811-16df-4dbc-a7b8-484464d96b24', '192906a9-df66-4780-9735-cafb4d6f1593', '5baa5aae50f5fae5b88aefa0f74315b0fecb269d495f7611c63969b3455eedbd', NULL, 'ADMIN', '2026-09-21 16:19:15.23421+00', '2026-09-21 16:34:15.23421+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('e0ea6553-6116-4ede-bd45-3e373a9c3c39', '4e0b4af6-48d4-4194-8d53-ea182714e3ad', '257e22c48d02172ebd9bdb3ea221e036e6414acc1bc2b482544ede65828d684e', NULL, 'ADMIN', '2026-09-21 16:20:31.681423+00', '2026-09-21 16:35:31.681423+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('2c0f6727-4160-48e1-ae97-a7efb783fda7', 'b8cd944b-155e-4f13-bdbd-f5f57e359940', '676be97a1121dd53e56f8122801106b35aa4c80cf2b9f8bdb6d405965fb8b618', NULL, 'ADMIN', '2026-09-21 16:21:29.182571+00', '2026-09-21 16:36:29.182571+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('5cfd40ca-4f3e-4782-b59b-011a73715956', '44f9f2af-95f7-420e-aa92-f27246feaf6d', '6f67ce28ed821c5fafe287c30d6daba7df8c79e6250cf92eeccaa4128f3d927d', NULL, 'ADMIN', '2026-09-21 16:23:29.286404+00', '2026-09-21 16:38:29.286404+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('113ae5bd-c1c7-4abd-8df6-63e1cd82f7ae', '8c1e22ad-bbaa-4092-8ba0-47eeb5a01fe7', '4fe9e13ec08094512e9895be1f0ee069e167693453e9b5f75d1d9bef117c5bcf', NULL, 'ADMIN', '2026-09-21 16:23:32.297859+00', '2026-09-21 16:38:32.297859+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('eaaa7f50-19f1-429d-a4c5-0316a3e027c1', '7ae8ed72-2990-4030-a60d-7c28fdb6b98e', 'd68a2fad5c7e483f1ebe7d4eb94f991924dc4b38440aec2873ef8ecd3a897c8e', NULL, 'ADMIN', '2026-09-21 16:23:33.186287+00', '2026-09-21 16:38:33.186287+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('f8091221-2b0c-484c-b351-a6cad3086a97', 'fa018d9b-6d3c-428b-86d5-14673e2bcdce', '55ec776a20330b7427012d2bc45370a77eb5b6df96475ce93056449f1ec3e252', NULL, 'ADMIN', '2026-09-21 16:23:57.125991+00', '2026-09-21 16:38:57.125991+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('8dfa06f4-0c83-49d4-822c-1cde2fbf86e9', '83fceafe-b12a-417b-a8c2-9db2b773be54', '610d0f98ede6b2300a6db23edf3e4e882c8d76622356bef760041ccff9a35ef9', NULL, 'ADMIN', '2026-09-21 16:24:53.026935+00', '2026-09-21 16:39:53.026935+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('c02787dc-c574-4356-8a8b-467816908868', 'b8c579fb-0be7-4d84-aed4-f89b9ad99ec7', '922ae4c5f222bb10d24db8ccbb1057dd75d84b40eb1d157949dc5e56d979b031', NULL, 'ADMIN', '2026-09-21 16:25:25.850396+00', '2026-09-21 16:40:25.850396+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('022fef32-d58a-44d4-a1ff-ddc4ad5b0e52', '729c3c23-c573-47d0-a04a-185491e3a2cc', '255e345683fcfa11b145cebac0f5de08bf7da6517460f4e732bdf617396f41ce', NULL, 'ADMIN', '2026-09-21 16:26:43.063285+00', '2026-09-21 16:41:43.063285+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('34df3192-00e1-4277-96de-a3ff9969d34b', '31abf7e2-2d8e-45ff-800e-d5175057e5b7', '42584f22a75f66d86a01547e9ea9062cb76d52971d1839f3ede642153dac697c', NULL, 'ADMIN', '2026-09-21 16:35:18.500186+00', '2026-09-21 16:50:18.500186+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('b1d83f4b-51c1-4acd-9a39-bd32f6d90493', '22f8c99e-cc01-49dd-9238-93a52b57379e', '1286f0d736203f481c91ab81c57eebef8b48f7ae9b4c4238c49be7a371a12297', NULL, 'ADMIN', '2026-09-21 16:35:21.80298+00', '2026-09-21 16:50:21.80298+00', 'f', NULL);
INSERT INTO "public"."erp_access_tokens" VALUES ('ccd4e20d-bca6-4530-808a-987f2484d08b', 'b87301d5-c525-4c01-a487-ae719b6a6a8b', 'd2bf16dc70d0bb761696d790c9fc453adce6c3956a03c9eb934be351fb306952', NULL, 'ADMIN', '2026-09-21 16:36:41.329911+00', '2026-09-21 16:51:41.329911+00', 'f', NULL);

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
INSERT INTO "public"."erp_authentications" VALUES ('2c7dd851-b08f-4684-a4a6-54ed71fe09ed', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'f1d10b9b19174f3fa5bc1c998ada4f49', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 15:57:11.295437+00', '2026-09-21 15:57:11.295441+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('69c8c729-0147-4a9d-b8a4-f8c101362133', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'fd92422e4a914cfb96c1378a7be0546b', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:06:51.794351+00', '2026-09-20 12:06:51.794357+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('7b680c5c-862b-4fe8-927c-f67ace8fdbeb', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e43cec10dbb54589913b15b9f7f06403', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:06:55.709662+00', '2026-09-20 12:06:55.709669+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('841960cb-5ae5-4dfc-9925-d54253c3c7f6', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ea47becab8d840eeb6b2cef89861b4bb', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:07:03.534772+00', '2026-09-20 12:07:03.534778+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('ec06acf2-a98d-4acc-a6ab-3ae54b50ea13', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '1484632c220c45d2b8c8b30817dd27af', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-20 03:16:54.120331+00', '2026-09-20 03:16:54.120355+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('058631bc-a44b-42d9-b80e-0f7c0b5f3b59', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e34964145e0240389f74df1720b1e907', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-20 03:16:58.162684+00', '2026-09-20 03:16:58.162689+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('74299931-d9d2-41dd-97c4-d753ceaa5ade', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '41b0d6a533a14811949a9f72f7c45921', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:07:04.589759+00', '2026-09-20 12:07:04.589763+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('0aafb99a-9692-4be5-8e2f-8b13123f24ec', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '101266d4097e401481448edfdfb11ba7', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 12:07:06.068767+00', '2026-09-20 12:07:06.068773+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('032d0587-eb88-4450-93fd-ca7f319fd523', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'cba4ed2115404138a5be923803536824', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:09.266602+00', '2026-09-21 16:10:09.266607+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('c62b76de-9d4b-46aa-8ae9-e6e7bfd5053c', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '470e48ad599843eb987e5171e72eac2a', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:10.626638+00', '2026-09-21 16:10:10.626641+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('60458107-c2c9-4636-9f1e-25eccc582984', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '1f43006ef2004dc983edf08221db632a', 'postmanruntime/2.7.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-20 03:11:59.957678+00', '2026-09-20 12:56:39.346261+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('7d9fd874-f96c-4d47-8a5e-3c8057699c43', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '0546f9a4ab3c4d8e80e4469a78ffd7cb', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:25.322019+00', '2026-09-21 16:10:25.322024+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('93617966-e97b-4458-87ca-ad49d8787422', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '6408d273659e46549ecfbbd1f298b636', 'postmanruntime/2.7.0', NULL, 'gzip, deflate, br', '', NULL, NULL, '2026-09-21 03:57:55.095801+00', '2026-09-21 06:11:27.221943+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('61024cf3-ecef-41ca-b6b5-c61c970b35ad', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '3778318dafa74b4f891ddf4d9e342c51', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', NULL, 'http://localhost:8000', 'http://localhost:8000/docs', NULL, '2026-09-21 04:19:45.852126+00', '2026-09-21 04:19:45.85213+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('9a1e48ca-62da-47cb-a549-21ab54098816', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '0508e10450164669a3a3cca4adbbaa79', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:34:22.148914+00', '2026-09-20 04:34:22.148921+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('989e6a2b-5b4c-48d9-bfa5-c8892dae9ec6', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '497e5f83ac60425288a62e10851c7c8e', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:34:40.010784+00', '2026-09-20 04:34:40.010789+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('aad3cc4d-2d14-4a79-abfe-0e4f75fcaf30', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ce9a6c206ba74e1d95b4b2834c900c06', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:34:51.416936+00', '2026-09-20 04:34:51.416941+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('9d890261-0de3-41c7-9d08-cac81e610677', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'c8e36c09d3ee4131a6d29c87ac8d5471', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:37:11.863771+00', '2026-09-20 04:37:11.863777+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('d7d55c99-8e19-40e5-96d9-a7fce0b361dc', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'b852ca48d06a4cfb9f8912ad77d57c2a', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 04:44:44.426776+00', '2026-09-20 04:44:44.426782+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('cbde52c7-b85e-49fc-a15a-2fdb32211fc9', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '9c0b4cdcc1b449a1b2baea74e0182d26', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'http://127.0.0.1:8000', 'http://127.0.0.1:8000/docs', NULL, '2026-09-20 05:02:27.971893+00', '2026-09-20 05:02:27.971898+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('959faee0-c76c-417e-8143-35972eaddb28', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'c0ad8533891243f18d9a3954b6729065', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 15:57:07.149648+00', '2026-09-21 15:57:07.149653+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('e08f062b-f407-4deb-be32-042c8a411ce1', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '6a1f8f0f2f4d4da3a1cd7d03839aa3f7', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:07.573103+00', '2026-09-21 16:10:07.57311+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('f50774a6-9939-4d2e-9e75-ca7f601200e9', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '39c16469778c41c9b5956b9d8df1f11e', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:28.981943+00', '2026-09-21 16:10:28.981949+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('38f239e1-b2bc-4575-932e-70b1c28d65f8', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e9f787147a6d476c9ac81b98ced07c04', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:31.804825+00', '2026-09-21 16:10:31.804828+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('79b06f36-c91f-4eea-8b81-781441ef924e', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '7e8cab02908248cd8a2ddfd2e51753d4', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:41.149501+00', '2026-09-21 16:10:41.149508+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('e1280d35-6556-48a8-995e-55d35ad8803c', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '7e730a40f2214756ad63b7f844f4480b', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:53.6377+00', '2026-09-21 16:10:53.637705+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('00c9ac4b-2e5d-4a84-a335-6b3a266d92f9', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '218096aa9e674e90b90965048e8e89f4', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:54.846776+00', '2026-09-21 16:10:54.84678+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('b06cceb8-5acd-4947-a826-c871ceedd0fd', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '72803ee65453458e923b04cdf140413e', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:55.969787+00', '2026-09-21 16:10:55.969791+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('a3939fde-cc75-4e67-a090-6e86e3164d78', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '790e8f5b3eaa4ae2b8901c556b81bb45', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:56.639964+00', '2026-09-21 16:10:56.63997+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('d3fcd006-5b12-4ffe-bf4e-ba70ff98ccaa', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '737b8cfd56d44af5af65597cde63575a', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:56.813231+00', '2026-09-21 16:10:56.813236+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('f0d301c4-f491-4c75-bf26-fd481c4a4769', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ff87d312d9c5402cadf060adfc1df8c4', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:56.977177+00', '2026-09-21 16:10:56.977183+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('9d0d6dd6-4abc-4698-b6f8-e035089b9348', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '8f6f2de1c22d420c9dc4b4f52112e9c6', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:57.161981+00', '2026-09-21 16:10:57.161985+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('0e830b02-1cf6-451e-8cfa-d8cd04010f3b', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'c98032d7db6c4b8ebfa79125788eb709', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:57.299812+00', '2026-09-21 16:10:57.299816+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('dfd1423a-de89-4709-938d-611a051e09b7', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'b811aa8d35ff49f8be6421a50119091f', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:57.455613+00', '2026-09-21 16:10:57.455616+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('2685a105-3f0a-4c0b-9450-e1ad8317cda7', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '01920e5c83f346ab8be96b5c5e93d644', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:10:57.610822+00', '2026-09-21 16:10:57.610825+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('8ac5b623-00e9-4e93-92b6-4bcfe37e59bf', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '6d92c68773df487190d2b4a208f484fa', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:12:18.29212+00', '2026-09-21 16:12:18.292126+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('d47ebae1-0ff1-4798-9b77-c871b900e04b', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '42a094206569458399263ed6a8f121dd', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:12:44.50198+00', '2026-09-21 16:12:44.501984+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('76020d23-1b6c-4c8a-8987-530fd08e3ad7', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'f7d9574dfc54480086640aed37bba037', 'python-httpx/0.28.1', NULL, 'gzip, deflate', '', NULL, NULL, '2026-09-21 16:16:08.697437+00', '2026-09-21 16:16:08.697441+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('a8446ece-17e9-498a-b8ed-30b5f5441b74', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e4110cee36594f328d8faa8287cb0a57', 'python-httpx/0.28.1', NULL, 'gzip, deflate', '', NULL, NULL, '2026-09-21 16:18:46.016122+00', '2026-09-21 16:18:46.016128+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('0deadb31-d6cc-48d1-8bed-fe65ca17873e', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'a37cfe6c97134723a6bd4a84b0dc5b19', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:19:04.087757+00', '2026-09-21 16:19:04.087762+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('0946c6ff-a3a2-4d0a-a967-971fb3ddec0a', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'f0be84c598ec46febd3c7b61ea6e5dd0', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:19:15.239007+00', '2026-09-21 16:19:15.239012+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('2f6afdd1-ad85-407b-b37e-2c9c5c19a01f', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'c77a6e9744654cb6a44dc8df0f125a3b', 'curl/8.21.0', NULL, NULL, '', NULL, NULL, '2026-09-21 16:20:31.684717+00', '2026-09-21 16:20:31.684722+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('60e90faa-238e-4426-987d-e32ab03ca12b', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '8495ab2a6acb4aa4bc4302298273c2ad', 'python-httpx/0.28.1', NULL, 'gzip, deflate', '', NULL, NULL, '2026-09-21 16:21:29.193207+00', '2026-09-21 16:21:29.193225+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('ea3898ed-c76b-435b-affe-c0089fb72f16', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'a1f78ba71a44434f92200cc7f51c847a', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:23:29.289872+00', '2026-09-21 16:23:29.289876+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('6edf502b-0ed5-415f-acaf-926ed17f0223', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '52450041bf7a4340bebdd31189f4a6e7', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:23:32.301032+00', '2026-09-21 16:23:32.301037+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('3452fa50-caf1-4430-af4b-cd4bdd9fff4a', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '85edf3df9494469d9dba37dc8e7ee37d', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:23:33.190072+00', '2026-09-21 16:23:33.190076+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('537c6fab-1b7b-4dd0-b94d-d630629789cf', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '514ad9a0c4b347ccb71dd3dda2717a59', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:23:57.130595+00', '2026-09-21 16:23:57.130598+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('053a3f91-c1fd-475d-830c-712a9df9235a', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'e00ba9da5ac1440e9657a277384fda1a', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:24:53.031514+00', '2026-09-21 16:24:53.031525+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('bfb47865-fc40-4c5a-8152-6e52102106dd', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '6f1bfba3b3cc458a8df655bbb9e93ebc', 'curl/8.21.0', NULL, NULL, '', NULL, NULL, '2026-09-21 16:25:25.852694+00', '2026-09-21 16:25:25.852696+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('e4a5646d-3024-44cc-9a6f-1942ebaf973c', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '83e2101427e741b4a999ce04446e0f9e', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:26:43.068261+00', '2026-09-21 16:26:43.068267+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('9d55865e-dfa9-4de8-b397-9644f4d6dca3', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ad8a9cad0b4f46cd803919638c553a4e', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:35:18.518803+00', '2026-09-21 16:35:18.518812+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('d4d81f45-1933-449e-a209-83bba2b76046', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', 'ef1424796132439281fffbd6cbf111a4', 'postmanruntime/2.7.0', NULL, NULL, '', NULL, NULL, '2026-09-21 12:42:10.060523+00', '2026-09-21 16:54:04.845451+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('8b5d3a8a-784b-45e8-8924-5939c658ee3f', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '87d9fb109b8645508b86e61042fe7edf', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:35:21.806439+00', '2026-09-21 16:35:21.806444+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('88af5abb-d1f7-452a-8407-f7965686dfe1', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '6a088ddcb10b4b71a0628b601dbca9fd', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', 'gzip, deflate, br, zstd', 'null', NULL, NULL, '2026-09-21 16:36:41.333705+00', '2026-09-21 16:36:41.33371+00', 'f', NULL, 'local');
INSERT INTO "public"."erp_authentications" VALUES ('af5cc3fe-1467-4a14-b805-c141a5336708', '0998e0d8-24d9-4ffc-b0f9-4d24345b9c70', '127.0.0.1', '109d3e4e73e94cca8cef3a43f7279730', 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/153.0.0.0 safari/537.36', 'en-us,en;q=0.9,th;q=0.8', NULL, 'http://localhost:8000', 'http://localhost:8000/docs', NULL, '2026-09-21 13:15:56.991312+00', '2026-09-21 16:54:57.629084+00', 'f', NULL, 'local');

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
INSERT INTO "public"."erp_refresh_tokens" VALUES ('5da71da1-279f-4411-8616-566adfc91dfd', '60458107-c2c9-4636-9f1e-25eccc582984', '2c7bd5a384212eac68dc7e23fdcd1793cb9da07f21830f91317d37f2d04d57af', '941f80647d7ff673f1355d13464f78e3584501f9c34acf1f3feee74f620b80d7', '2026-09-20 03:11:59.891576+00', '2026-09-20 12:56:39.346261+00', '2026-09-27 12:56:39.346261+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('7b981bef-c513-418d-b463-0574133456c1', '959faee0-c76c-417e-8143-35972eaddb28', 'cc7471ba5aa4faab883eedffb172235be3816eab1793c9b4255ef8eda21aae7c', NULL, '2026-09-21 15:57:07.09206+00', '2026-09-21 15:57:07.09206+00', '2026-09-28 15:57:07.09206+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('52bf0019-9159-4c38-bffc-ed0e4364d601', '2c7dd851-b08f-4684-a4a6-54ed71fe09ed', 'cf32373958897d28df155da04ff09b58f89c0b7878b2c48544595198e2f0a152', NULL, '2026-09-21 15:57:11.291517+00', '2026-09-21 15:57:11.291517+00', '2026-09-28 15:57:11.291517+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('a2689ef3-9f38-46a4-b9d1-9b7d5df420be', 'e08f062b-f407-4deb-be32-042c8a411ce1', '3c2e403701bd042ea015064b3ad6d94076a673e06bcb7194c85c8d0df8ceb137', NULL, '2026-09-21 16:10:07.568387+00', '2026-09-21 16:10:07.568387+00', '2026-09-28 16:10:07.568387+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('75bbe805-e6c9-4f12-a000-517684fbfdf7', '032d0587-eb88-4450-93fd-ca7f319fd523', 'd98ed86bc03530dfa3b61be258fd837becf65121e3682831753c56fcbe0046d5', NULL, '2026-09-21 16:10:09.263175+00', '2026-09-21 16:10:09.263175+00', '2026-09-28 16:10:09.263175+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('c71c2acc-1b3c-4552-8d7c-337119538ebd', 'c62b76de-9d4b-46aa-8ae9-e6e7bfd5053c', '8089adef6dbcaca6e3097e882ca5a571ecc835ca9dd3646aed9e10b762acfb12', NULL, '2026-09-21 16:10:10.623122+00', '2026-09-21 16:10:10.623122+00', '2026-09-28 16:10:10.623122+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('eddd3e8f-034d-434b-9e0b-01c304b46146', '7d9fd874-f96c-4d47-8a5e-3c8057699c43', '2a5a16d1817b2b94df972b3ed40575d0ad38a99767a3b93c158a9565ba69c4a3', NULL, '2026-09-21 16:10:25.315708+00', '2026-09-21 16:10:25.315708+00', '2026-09-28 16:10:25.315708+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('de401b4b-6bda-4b55-8a66-c3afa90dec6a', 'f50774a6-9939-4d2e-9e75-ca7f601200e9', 'd07ba2a2d16b7fb2634f8f31551a66580f8c85a470f7a0880811eeaa12e752d3', NULL, '2026-09-21 16:10:28.97788+00', '2026-09-21 16:10:28.97788+00', '2026-09-28 16:10:28.97788+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('2f84d91b-1876-48ce-ad34-adf1ef3c74ad', '38f239e1-b2bc-4575-932e-70b1c28d65f8', 'c4ed24dcd3e5577e2fa741fa417b991cec89f31938e3e31afb31664b395fa348', NULL, '2026-09-21 16:10:31.801953+00', '2026-09-21 16:10:31.801953+00', '2026-09-28 16:10:31.801953+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('4a36ead8-1134-47ae-9f8a-aaf648bdb353', '79b06f36-c91f-4eea-8b81-781441ef924e', '09e06164de24bd526555d8ed4c6dc9c1f8ad5ea41f4cf7f8f46d42009514bbfd', NULL, '2026-09-21 16:10:41.14507+00', '2026-09-21 16:10:41.14507+00', '2026-09-28 16:10:41.14507+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('271c9a8e-1117-4374-a39f-309144df6db6', 'e1280d35-6556-48a8-995e-55d35ad8803c', '3fda42ae06493e6fb0fb77d7df582094187c1ab13376777de75fdfca7153d683', NULL, '2026-09-21 16:10:53.634095+00', '2026-09-21 16:10:53.634095+00', '2026-09-28 16:10:53.634095+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('8d7573c6-2a7a-4402-ad8b-4b09c50d6fb7', '00c9ac4b-2e5d-4a84-a335-6b3a266d92f9', 'e5f537ccc5cb9014c1d255518a3b758f080b7bccd025581fa8ba3b841422517b', NULL, '2026-09-21 16:10:54.843685+00', '2026-09-21 16:10:54.843685+00', '2026-09-28 16:10:54.843685+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('cae7fbf9-ea71-4de9-8a02-617c157d4538', 'b06cceb8-5acd-4947-a826-c871ceedd0fd', '4faa6a6481e11167917c90600ff12d9ab1857aee2d5aee0614049db530ad135a', NULL, '2026-09-21 16:10:55.967251+00', '2026-09-21 16:10:55.967251+00', '2026-09-28 16:10:55.967251+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('11efe786-cbfa-4c09-a0c9-371ef49aa84b', 'a3939fde-cc75-4e67-a090-6e86e3164d78', '73cd0cd0d3c48db26188aa11f2f05b45c0a13ee780b8fb9da33cf1300e89d565', NULL, '2026-09-21 16:10:56.635795+00', '2026-09-21 16:10:56.635795+00', '2026-09-28 16:10:56.635795+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('22d0a278-424a-4dd6-8da7-a89d687fb35e', 'd3fcd006-5b12-4ffe-bf4e-ba70ff98ccaa', 'f90e96482a4bb672dda4d778aaa1755a6c0390f38c697fb07211caec9af693ca', NULL, '2026-09-21 16:10:56.809822+00', '2026-09-21 16:10:56.809822+00', '2026-09-28 16:10:56.809822+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('36f42fea-e403-499b-85c0-b526605cebb8', 'f0d301c4-f491-4c75-bf26-fd481c4a4769', '579751bfb4fd44b360275135d6a7191eca49a0caea432dba008178984a2d1ceb', NULL, '2026-09-21 16:10:56.972842+00', '2026-09-21 16:10:56.972842+00', '2026-09-28 16:10:56.972842+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('afa6ef49-f88f-4c73-b8fe-49b2dceaab6c', '9d0d6dd6-4abc-4698-b6f8-e035089b9348', 'e8de1def7634598b96a00083caa7f51056b2bfdc3d407003e84b6f26a623b1c7', NULL, '2026-09-21 16:10:57.157737+00', '2026-09-21 16:10:57.157737+00', '2026-09-28 16:10:57.157737+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('02e7f0ca-0317-402d-82c4-d0ff3ace341f', '0e830b02-1cf6-451e-8cfa-d8cd04010f3b', '7449a36acfaa1af7fcbc7d371087f258c2a769defe575d79b90c02c5e934c9f4', NULL, '2026-09-21 16:10:57.296296+00', '2026-09-21 16:10:57.296296+00', '2026-09-28 16:10:57.296296+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('6573a96d-01e5-46d4-9f1d-46e878e6ed5d', 'dfd1423a-de89-4709-938d-611a051e09b7', 'b93ed42cdde1cdd4ca7eab685d6f4f2375b5e5636c3c127096a9fa0e25c1e3d9', NULL, '2026-09-21 16:10:57.452659+00', '2026-09-21 16:10:57.452659+00', '2026-09-28 16:10:57.452659+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('e5882857-4e8c-4ee7-b124-2bdc0075f909', '2685a105-3f0a-4c0b-9450-e1ad8317cda7', '5ba88dbfbcfd526bda7b47ff79240b8030a19230149a5c1c913f5e50b7bfa390', NULL, '2026-09-21 16:10:57.607892+00', '2026-09-21 16:10:57.607892+00', '2026-09-28 16:10:57.607892+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('d25930d3-02ac-4e89-8dff-4c2f791f3e55', '8ac5b623-00e9-4e93-92b6-4bcfe37e59bf', '21452156c416873661bc44c9b40db54e7dc36771508b391ea6ed865484771239', NULL, '2026-09-21 16:12:18.270698+00', '2026-09-21 16:12:18.270698+00', '2026-09-28 16:12:18.270698+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('a9d50a4a-fd9f-44d0-b274-e3253cc64efb', 'd47ebae1-0ff1-4798-9b77-c871b900e04b', '721818d35632e8e5439f601fc4ef1ba57cfb10e54ff613e3d808b60ba8420b92', NULL, '2026-09-21 16:12:44.496509+00', '2026-09-21 16:12:44.496509+00', '2026-09-28 16:12:44.496509+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('16afd733-7cff-4f61-8b6a-d56770c407c4', '76020d23-1b6c-4c8a-8987-530fd08e3ad7', '95521cc46d2f6f415536590c0084fd17784441785bb55b0e8c0d77af56a38315', NULL, '2026-09-21 16:16:08.685586+00', '2026-09-21 16:16:08.685586+00', '2026-09-28 16:16:08.685586+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('aca5d875-a6ac-4c39-b579-59162109eba0', 'a8446ece-17e9-498a-b8ed-30b5f5441b74', '30ed760a7b81ed46b31da1d306b670d8669bdfbc52f7ea3ee2c4785d743b77de', NULL, '2026-09-21 16:18:46.003051+00', '2026-09-21 16:18:46.003051+00', '2026-09-28 16:18:46.003051+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('632e8c80-b37a-442a-bc59-2534d4c48af2', '0deadb31-d6cc-48d1-8bed-fe65ca17873e', 'a0b217394c8ac202764b0c524682419205744688995cacd10a16be22bfb1af77', NULL, '2026-09-21 16:19:04.073271+00', '2026-09-21 16:19:04.073271+00', '2026-09-28 16:19:04.073271+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('192906a9-df66-4780-9735-cafb4d6f1593', '0946c6ff-a3a2-4d0a-a967-971fb3ddec0a', 'a9672e31fc0b1761782c236a764cf48fd15a433a22c70f03090084d933302239', NULL, '2026-09-21 16:19:15.23421+00', '2026-09-21 16:19:15.23421+00', '2026-09-28 16:19:15.23421+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('4e0b4af6-48d4-4194-8d53-ea182714e3ad', '2f6afdd1-ad85-407b-b37e-2c9c5c19a01f', 'b78c35479ab411f6d346d8c9c810b2c41191e931e1fc81b8d275503277f65fae', NULL, '2026-09-21 16:20:31.681423+00', '2026-09-21 16:20:31.681423+00', '2026-09-28 16:20:31.681423+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('b8cd944b-155e-4f13-bdbd-f5f57e359940', '60e90faa-238e-4426-987d-e32ab03ca12b', '2aa04c0d89651ac96e92a2046f4ddca2cb98531c5eec1e3d494af556638ff214', NULL, '2026-09-21 16:21:29.182571+00', '2026-09-21 16:21:29.182571+00', '2026-09-28 16:21:29.182571+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('44f9f2af-95f7-420e-aa92-f27246feaf6d', 'ea3898ed-c76b-435b-affe-c0089fb72f16', 'eaacfcf8e1d87e2f8bfcdf75dd2eba1b4b32d239803eb8ea6f7b316b87c10929', NULL, '2026-09-21 16:23:29.286404+00', '2026-09-21 16:23:29.286404+00', '2026-09-28 16:23:29.286404+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('8c1e22ad-bbaa-4092-8ba0-47eeb5a01fe7', '6edf502b-0ed5-415f-acaf-926ed17f0223', '6a35cd034fdaf71f91f833d285638d353c0b7c74098da89986d62d5aae2a74eb', NULL, '2026-09-21 16:23:32.297859+00', '2026-09-21 16:23:32.297859+00', '2026-09-28 16:23:32.297859+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('7ae8ed72-2990-4030-a60d-7c28fdb6b98e', '3452fa50-caf1-4430-af4b-cd4bdd9fff4a', '1f670033afcf4f1308bf5b89fd98ba2fa4e332f77b99bc54be218214dae25bfc', NULL, '2026-09-21 16:23:33.186287+00', '2026-09-21 16:23:33.186287+00', '2026-09-28 16:23:33.186287+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('fa018d9b-6d3c-428b-86d5-14673e2bcdce', '537c6fab-1b7b-4dd0-b94d-d630629789cf', '178199a9a04d32d15d418d8abea339e128496fb9a66b2a5e96e344e4db936fdc', NULL, '2026-09-21 16:23:57.125991+00', '2026-09-21 16:23:57.125991+00', '2026-09-28 16:23:57.125991+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('83fceafe-b12a-417b-a8c2-9db2b773be54', '053a3f91-c1fd-475d-830c-712a9df9235a', 'f045ef5e200563c70963c418c480fd520575ccfe61deabeca14e8cdb6fa87898', NULL, '2026-09-21 16:24:53.026935+00', '2026-09-21 16:24:53.026935+00', '2026-09-28 16:24:53.026935+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('b8c579fb-0be7-4d84-aed4-f89b9ad99ec7', 'bfb47865-fc40-4c5a-8152-6e52102106dd', '45d08c7435899c88b0c62bbe703b013bafb59d8a64e91c567e1a05f9c171c266', NULL, '2026-09-21 16:25:25.850396+00', '2026-09-21 16:25:25.850396+00', '2026-09-28 16:25:25.850396+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('729c3c23-c573-47d0-a04a-185491e3a2cc', 'e4a5646d-3024-44cc-9a6f-1942ebaf973c', '6d3746e1755c7ed428c2ced6c7d76a5dbe2a94e7f71da0acbda30a155a732b96', NULL, '2026-09-21 16:26:43.063285+00', '2026-09-21 16:26:43.063285+00', '2026-09-28 16:26:43.063285+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('31abf7e2-2d8e-45ff-800e-d5175057e5b7', '9d55865e-dfa9-4de8-b397-9644f4d6dca3', 'dae32b564eb87e5d7da6b7101801bd909353f5782c906a6a0a42cfee3ff081d5', NULL, '2026-09-21 16:35:18.500186+00', '2026-09-21 16:35:18.500186+00', '2026-09-28 16:35:18.500186+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('22f8c99e-cc01-49dd-9238-93a52b57379e', '8b5d3a8a-784b-45e8-8924-5939c658ee3f', '31c785eef32466fd987cd01c05daf7deaae85f15b91be21f2131033c700188d5', NULL, '2026-09-21 16:35:21.80298+00', '2026-09-21 16:35:21.80298+00', '2026-09-28 16:35:21.80298+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('b87301d5-c525-4c01-a487-ae719b6a6a8b', '88af5abb-d1f7-452a-8407-f7965686dfe1', 'dd4d80d17d77cb607169373979925d28437f874be700dcee5c900c9adda46226', NULL, '2026-09-21 16:36:41.329911+00', '2026-09-21 16:36:41.329911+00', '2026-09-28 16:36:41.329911+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('a586628c-de2f-4313-83c2-542ad875441d', 'd4d81f45-1933-449e-a209-83bba2b76046', '1e76fed94ba6052b56fd7998365084fcedb3fcb2feecd66892e6811c32abbe2a', 'bbc0a4a2a24cd13a6a384b6a4c9ef72e5d3afd2fc38733566b113f3d76cc57b4', '2026-09-21 12:42:10.011002+00', '2026-09-21 16:54:04.845451+00', '2026-09-28 16:54:04.845451+00', 'f', NULL);
INSERT INTO "public"."erp_refresh_tokens" VALUES ('8404b67b-7c39-4e1f-a675-69430bf46883', 'af5cc3fe-1467-4a14-b805-c141a5336708', '75edd83ad8ecd814d7cea20e1f76fab803d2d857833d29fbab52ccffc72bcb13', 'c3c4989531eb758d0bc88a750a06be5ded8c809a7bbbb86a7969d26d67feee11', '2026-09-21 13:15:56.934067+00', '2026-09-21 16:54:57.629084+00', '2026-09-28 16:54:57.629084+00', 'f', NULL);

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
