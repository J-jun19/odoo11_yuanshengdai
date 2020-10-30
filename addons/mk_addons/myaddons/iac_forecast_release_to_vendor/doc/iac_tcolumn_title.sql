/*在中間表ep_temp_master  
建立  暫存 table - iac_tcolumn_title */

/*
ALTER TABLE "ep_temp_master"."iac_tcolumn_title" ALTER COLUMN round_value TYPE float 
USING to_number(round_value,  '9999999999999999.999999999999999999');

-- ALTER TABLE "ep_temp_master"."iac_traw_data" ALTER COLUMN creation_date TYPE timestamp(6)

alter table "ep_temp_master"."iac_tcolumn_title" alter column creation_date type timestamp without time zone using to_timestamp(<columnname>) AT TIME ZONE 'UTC';

alter table "ep_temp_master"."iac_tcolumn_title" alter column creation_date type timestamp using creation_date::timestamp;


 

*/

-- ----------------------------
-- Table structure for "ep_temp_master"."iac_tcolumn_title"
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."iac_tcolumn_title";
CREATE TABLE "ep_temp_master"."iac_tcolumn_title" (
"id" int4 ,
"qty_w2" varchar,
"create_date" timestamp(6),
"division" varchar,
"qty_w5" varchar,
"creation_date" varchar,
"b017b" varchar,
"intransit_qty" varchar,
"buyer_code" varchar,
"open_po" varchar,
"qty_w3" varchar,
"alt_grp" varchar,
"pr" varchar,
"qty_m3" varchar,
"qty_m1" varchar,
"qty_m6" varchar,
"qty_m7" varchar,
"qty_m4" varchar,
"qty_m8" varchar,
"qty_m9" varchar,
"b012" varchar,
"alt_flag" varchar,
"po" varchar,
"stock" varchar,
"qty_m2" varchar,
"plant" varchar,
"mquota_flag" varchar,
"description" varchar,
"create_uid" int4,
"remark" varchar,
"round_value" varchar,
"material" varchar,
"vendor_code" varchar,
"quota" varchar,
"flag" varchar,
"qty_w7" varchar,
"write_date" timestamp(6),
"mfgpn_info" varchar,
"qty_w1_r" varchar,
"write_uid" int4,
"qty_w12" varchar,
"qty_w13" varchar,
"qty_w10" varchar,
"qty_w11" varchar,
"b002" varchar,
"custpn_info" varchar,
"qty_w6" varchar,
"b001" varchar,
"qty_w1" varchar,
"b004" varchar,
"b005" varchar,
"b902s" varchar,
"b902q" varchar,
"qty_w8" varchar,
"qty_w4" varchar,
"qty_w9" varchar,
"fpversion" varchar,
"qty_m5" varchar,
"vendor_name" varchar,
"leadtime" varchar,
"max_surplus_qty" varchar
)
WITH (OIDS=FALSE)
;
 
COMMENT ON TABLE "ep_temp_master"."iac_tcolumn_title" IS 'column title';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w2" IS 'qty_w2';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."division" IS 'division';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w5" IS 'qty_w5';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."creation_date" IS 'creation_date';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b017b" IS 'b017b';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."intransit_qty" IS 'intransit_qty';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."buyer_code" IS 'buyer_code';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."open_po" IS 'open_po';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w3" IS 'qty_w3';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."alt_grp" IS 'alt_grp';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."pr" IS 'pr';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m3" IS 'qty_m3';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m1" IS 'qty_m1';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m6" IS 'qty_m6';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m7" IS 'qty_m7';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m4" IS 'qty_m4';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m8" IS 'qty_m8';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m9" IS 'qty_m9';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b012" IS 'b012';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."alt_flag" IS 'alt_flag';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."po" IS 'po';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."stock" IS 'stock';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m2" IS 'qty_m2';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."plant" IS 'plant';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."mquota_flag" IS 'mquota_flag';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."description" IS 'description';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."remark" IS 'remark';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."round_value" IS 'round_value';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."material" IS 'material';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."vendor_code" IS 'vendor_code';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."quota" IS 'quota';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."flag" IS 'flag';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w7" IS 'qty_w7';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."mfgpn_info" IS 'mfgpn_info';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w1_r" IS 'qty_w1_r';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w12" IS 'qty_w12';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w13" IS 'qty_w13';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w10" IS 'qty_w10';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w11" IS 'qty_w11';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b002" IS 'b002';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."custpn_info" IS 'custpn_info';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w6" IS 'qty_w6';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b001" IS 'b001';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w1" IS 'qty_w1';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b004" IS 'b004';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b005" IS 'b005';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b902s" IS 'b902s';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."b902q" IS 'b902q';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w8" IS 'qty_w8';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w4" IS 'qty_w4';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_w9" IS 'qty_w9';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."fpversion" IS 'fpversion';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."qty_m5" IS 'qty_m5';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."vendor_name" IS 'vendor_name';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."leadtime" IS 'leadtime';
COMMENT ON COLUMN "ep_temp_master"."iac_tcolumn_title"."max_surplus_qty" IS 'max_surplus_qty';

-- ----------------------------
-- Create sequence
-- ----------------------------

DROP SEQUENCE IF EXISTS "ep_temp_master"."iac_tcolumn_title_id_seq";

CREATE SEQUENCE "ep_temp_master"."iac_tcolumn_title_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."iac_tcolumn_title"."id";

 
-- ----------------------------
-- create pkey
-- ----------------------------

alter table ep_temp_master.iac_tcolumn_title add CONSTRAINT  "iac_tcolumn_title_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add pkey default
-- ----------------------------

ALTER TABLE ep_temp_master.iac_tcolumn_title ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_tcolumn_title_id_seq'::regclass);


 
 
--------------------
--- 增加欄位  need_re_update,need_update_id
-------------------- 
  
alter table	public.iac_tcolumn_title ADD COLUMN need_re_update int4 ;
alter table	public.iac_tcolumn_title ADD COLUMN need_update_id int4;

------///////////////////////------------

--------------------
---建立錯誤樹續据中間表
--------------------

DROP TABLE IF EXISTS "ep_temp_master"."iac_tcolumn_title_error";

CREATE TABLE "ep_temp_master"."iac_tcolumn_title_error" as select * from "ep_temp_master"."iac_tcolumn_title" where 1=2;

alter table ep_temp_master.iac_tcolumn_title_error add CONSTRAINT  "iac_tcolumn_title_error_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add fun_def table
-- ----------------------------

alter table	public.iac_tcolumn_title	ALTER COLUMN need_re_update SET DEFAULT 0;

update	public.iac_tcolumn_title	set need_re_update =0 where need_re_update is null;

-- ----------------------------
-- add fun_def table
-- ----------------------------
alter table	public.iac_tcolumn_title ADD COLUMN miss_flag int4 ;


