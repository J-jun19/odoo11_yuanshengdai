/*在中間表ep_temp_master  
建立  暫存 table - iac_tjob_status */

-- ----------------------------
-- Table structure for "ep_temp_master"."iac_tjob_status"
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."iac_tjob_status";
CREATE TABLE "ep_temp_master"."iac_tjob_status" (
"id" int4,
"status" varchar,
"create_uid" int4,
"write_date" timestamp(6),
"write_uid" int4,
"starttime" date,
"fpversion" varchar,
"create_date" timestamp(6),
"endtime" date
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."iac_tjob_status" IS 'tjob status';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."status" IS 'status';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."starttime" IS 'Start Time';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."fpversion" IS 'fpversion';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."iac_tjob_status"."endtime" IS 'End Time';
 
-- ----------------------------
-- Create sequence
-- ----------------------------

DROP SEQUENCE IF EXISTS "ep_temp_master"."iac_tjob_status_id_seq";

CREATE SEQUENCE "ep_temp_master"."iac_tjob_status_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."iac_tjob_status"."id";


-- ----------------------------
-- create pkey
-- ----------------------------

alter table ep_temp_master.iac_tjob_status add CONSTRAINT  "iac_tjob_status_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add pkey default
-- ----------------------------

ALTER TABLE ep_temp_master.iac_tjob_status ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_tjob_status_id_seq'::regclass);


 
--------------------
--- 增加欄位  need_re_update,need_update_id
-------------------- 
  
alter table	public.iac_tjob_status ADD COLUMN need_re_update int4 ;
alter table	public.iac_tjob_status ADD COLUMN need_update_id int4;
alter table	public.iac_tjob_status ADD COLUMN sap_temp_id int4;
alter table	public.iac_tjob_status ADD COLUMN sap_log_id varchar;
 
------///////////////////////------------

--------------------
---建立錯誤樹續据中間表
--------------------

DROP TABLE IF EXISTS "ep_temp_master"."iac_tjob_status_error";

CREATE TABLE "ep_temp_master"."iac_tjob_status_error" as select * from "ep_temp_master"."iac_tjob_status" where 1=2;

alter table ep_temp_master.iac_tjob_status_error add CONSTRAINT  "iac_tjob_status_error_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add fun_def table
-- ----------------------------

alter table	public.iac_tjob_status	ALTER COLUMN need_re_update SET DEFAULT 0;

update	public.iac_tjob_status	set need_re_update =0 where need_re_update is null;

----------$$$$$$$$$$$$$$------------
----改欄位名稱

ALTER TABLE "ep_temp_master".iac_tjob_status RENAME COLUMN "endTime" TO endtime;
ALTER TABLE "ep_temp_master".iac_tjob_status RENAME COLUMN "startTime" TO starttime;
