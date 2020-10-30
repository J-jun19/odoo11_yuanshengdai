/*注意所有字符主键的字段都要建立索引

蓝帝斯 2018/1/30 上午 10:50:13
document_erp_id = fields.Char(string="SAP ID",index=True)#purchase order code
类似这样

need_re_update,need_update_id
alter table	public.iac_traw_data ADD COLUMN need_re_update int4 ;
alter table	public.iac_traw_data ADD COLUMN need_update_id int4;

*/

/*執行 FUNCTION語句

確定本機有以下3 table& 2 function 
table:
iac_interface_temp_table_group
iac_interface_temp_table_group_line
iac_interface_temp_table_group_exe_log
  
function:
write_exception_log
proc_update_table_ref

執行 FUNCTION語句
SELECT ep_temp_master.proc_trans_table_iac_traw_data('test',123,456,1000,0) ;
 
 	
ALTER TABLE "ep_temp_master"."iac_traw_data" ALTER COLUMN round_value TYPE float 
USING to_number(round_value,  '9999999999999999.999999999999999999');

ALTER TABLE "ep_temp_master"."iac_tcolumn_title" ALTER COLUMN round_value TYPE float 
USING to_number(round_value,  '9999999999999999.999999999999999999');

-- ALTER TABLE "ep_temp_master"."iac_traw_data" ALTER COLUMN creation_date TYPE timestamp(6)

alter table "ep_temp_master"."iac_tcolumn_title" alter column creation_date type timestamp without time zone using to_timestamp(<columnname>) AT TIME ZONE 'UTC';

alter table "ep_temp_master"."iac_tcolumn_title" alter column creation_date type timestamp using creation_date::timestamp;

*/


-- ----------------------------
-- Table structure for iac_traw_data
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."iac_traw_data";
CREATE TABLE "ep_temp_master"."iac_traw_data" (
"id" int4 ,
"plant" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"vendor_name" varchar COLLATE "default",
"buyer_code" varchar COLLATE "default",
"division" varchar COLLATE "default",
"material" varchar COLLATE "default",
"description" varchar COLLATE "default",
"fpversion" varchar COLLATE "default",
"flag" varchar COLLATE "default",
"custpn_info" varchar COLLATE "default",
"intransit_qty" float8,
"leadtime" int4,
"max_surplus_qty" varchar COLLATE "default",
"mfgpn_info" varchar COLLATE "default",
"mquota_flag" varchar COLLATE "default",
"open_po" float8,
"quota" float8,
"remark" varchar COLLATE "default",
"round_value" float8,
"stock" float8,
"alt_flag" varchar COLLATE "default",
"alt_grp" varchar COLLATE "default",
"po" varchar COLLATE "default",
"pr" varchar COLLATE "default",
"qty_m1" float8,
"qty_m2" float8,
"qty_m3" float8,
"qty_m4" float8,
"qty_m5" float8,
"qty_m6" float8,
"qty_m7" float8,
"qty_m8" float8,
"qty_m9" float8,
"qty_w1" float8,
"qty_w1_r" float8,
"qty_w2" float8,
"qty_w3" float8,
"qty_w4" float8,
"qty_w5" float8,
"qty_w6" float8,
"qty_w7" float8,
"qty_w8" float8,
"qty_w9" float8,
"qty_w10" float8,
"qty_w11" float8,
"qty_w12" float8,
"qty_w13" float8,
"b001" float8,
"b002" float8,
"b004" float8,
"b005" float8,
"b012" float8,
"b017b" float8,
"b902q" float8,
"b902s" float8,
"creation_date" timestamp(6),
"create_uid" int4,
"write_uid" int4,
"create_date" timestamp(6),
"write_date" timestamp(6)
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."iac_traw_data" IS 'iac.traw.data';

COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."alt_flag" IS 'ALT_FLAG';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."alt_grp" IS 'ALT_GRP';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b001" IS 'B001';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b002" IS 'B002';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b004" IS 'B004';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b005" IS 'B005';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b012" IS 'B012';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b017b" IS 'B017B';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b902q" IS 'B902Q';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."b902s" IS 'B902S';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."buyer_code" IS 'BUYER_CODE';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."creation_date" IS 'CREATION_DATE';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."custpn_info" IS 'CUSTPN_INFO';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."description" IS 'DESCRIPTION';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."division" IS 'DIVISION';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."flag" IS 'FLAG';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."fpversion" IS 'FPVERSION';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."intransit_qty" IS 'INTRANSIT_QTY';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."leadtime" IS 'LEADTIME';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."material" IS 'MATERIAL';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."max_surplus_qty" IS 'MAX_SURPLUS_QTY';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."mfgpn_info" IS 'MFGPN_INFO';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."mquota_flag" IS 'MQUOTA_FLAG';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."open_po" IS 'OPEN_PO';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."plant" IS 'PLANT';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."po" IS 'PO';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."pr" IS 'PR';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m1" IS 'QTY_M1';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m2" IS 'QTY_M2';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m3" IS 'QTY_M3';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m4" IS 'QTY_M4';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m5" IS 'QTY_M5';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m6" IS 'QTY_M6';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m7" IS 'QTY_M7';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m8" IS 'QTY_M8';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_m9" IS 'QTY_M9';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w1" IS 'QTY_W1';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w1_r" IS 'QTY_W1_R';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w10" IS 'QTY_W10';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w11" IS 'QTY_W11';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w12" IS 'QTY_W12';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w13" IS 'QTY_W13';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w2" IS 'QTY_W2';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w3" IS 'QTY_W3';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w4" IS 'QTY_W4';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w5" IS 'QTY_W5';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w6" IS 'QTY_W6';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w7" IS 'QTY_W7';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w8" IS 'QTY_W8';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."qty_w9" IS 'QTY_W9';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."quota" IS 'QUOTA';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."remark" IS 'REMARK';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."round_value" IS 'ROUND_VALUE';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."stock" IS 'STOCK';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."vendor_code" IS 'VENDOR_CODE';
COMMENT ON COLUMN "ep_temp_master"."iac_traw_data"."vendor_name" IS 'VENDOR_NAME';
  
-- ----------------------------
-- Create sequence
-- ----------------------------

DROP SEQUENCE IF EXISTS "ep_temp_master"."iac_traw_data_id_seq";

CREATE SEQUENCE "ep_temp_master"."iac_traw_data_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."iac_traw_data"."id";

--select * from "ep_temp_master"."iac_traw_data_id_seq" ;

-- ----------------------------
-- create pkey
-- ----------------------------

alter table ep_temp_master.iac_traw_data add CONSTRAINT  "iac_traw_data_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add pkey default
-- ----------------------------

ALTER TABLE ep_temp_master.iac_traw_data ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_traw_data_id_seq'::regclass);


--------------------
--- 增加欄位  need_re_update,need_update_id
-------------------- 
  
alter table	public.iac_traw_data ADD COLUMN need_re_update int4 ;
alter table	public.iac_traw_data ADD COLUMN need_update_id int4;
 
------///////////////////////------------

--------------------
---建立错误数据中间表
--------------------

DROP TABLE IF EXISTS "ep_temp_master"."iac_traw_data_error";

CREATE TABLE "ep_temp_master"."iac_traw_data_error" as select * from "ep_temp_master"."iac_traw_data" where 1=2;

alter table ep_temp_master.iac_traw_data_error add CONSTRAINT  "iac_traw_data_error_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add fun_def table
-- ----------------------------

alter table	public.iac_traw_data	ALTER COLUMN need_re_update SET DEFAULT 0;

update	public.iac_traw_data	set need_re_update =0 where need_re_update is null;


-- ----------------------------
-- add fun_def table
-- ----------------------------
alter table	public.iac_traw_data ADD COLUMN miss_flag int4 ;

