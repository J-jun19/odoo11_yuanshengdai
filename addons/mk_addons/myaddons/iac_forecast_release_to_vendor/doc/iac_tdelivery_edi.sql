/*注意所有字符主键的字段都要建立索引

蓝帝斯 2018/1/30 上午 10:50:13
document_erp_id = fields.Char(string="SAP ID",index=True)#purchase order code
类似这样

need_re_update,need_update_id
alter table	ep_temp_master.iac_tdelivery_edi ADD COLUMN need_re_update int4 ;
alter table	ep_temp_master.iac_tdelivery_edi ADD COLUMN need_update_id int4;

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
SELECT ep_temp_master.proc_trans_table_iac_tdelivery_edi() ;
 
 	
ALTER TABLE "ep_temp_master"."iac_tdelivery_edi" ALTER COLUMN round_value TYPE float 
USING to_number(round_value,  '9999999999999999.999999999999999999');

ALTER TABLE "ep_temp_master"."iac_tcolumn_title" ALTER COLUMN round_value TYPE float 
USING to_number(round_value,  '9999999999999999.999999999999999999');

-- ALTER TABLE "ep_temp_master"."iac_tdelivery_edi" ALTER COLUMN creation_date TYPE timestamp(6)

alter table "ep_temp_master"."iac_tcolumn_title" alter column creation_date type timestamp without time zone using to_timestamp(<columnname>) AT TIME ZONE 'UTC';

alter table "ep_temp_master"."iac_tcolumn_title" alter column creation_date type timestamp using creation_date::timestamp;

*/

/*
--SELECT  ep_temp_master.proc_trans_table_iac_tdelivery_edi();
--select fcst_version,* from "ep_temp_master".iac_tdelivery_edi_error;
SELECT * from "ep_temp_master".extractlog where extractdate >='2018-02-22' order by extractdate desc;
SELECT * from "public".iac_interface_temp_table_group_exe_log where start_time>='2018-02-23' ;
select iac_pn,fcst_version,* from "public".iac_tdelivery_edi where fcst_version= '20180223115355';
select iac_pn,fcst_version,* from "ep_temp_master".iac_tdelivery_edi where fcst_version ='20180223115355';
*/

-- ----------------------------
-- Table structure for iac_tdelivery_edi
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."iac_tdelivery_edi";
CREATE TABLE "ep_temp_master"."iac_tdelivery_edi" (
"id" int4 ,
"buyer_remark" varchar,
"status" varchar,
"write_date" timestamp(6),
"create_uid" int4,
"write_uid" int4,
"plant_id" int4,
"vendor_id" int4,
"shipping_date" date,
"material_id" int4,
"qty" float8,
"cdt" timestamp(6),
"iac_pn_vendor" varchar,
"reply_id" int4,
"uploader" int4,
"create_date" timestamp(6),
"buyer_id" int4,
"key_part" varchar,
"fcst_version" varchar,
"iac_pn" varchar,
"plant" varchar,
"vendor_code" varchar,
"valid" int4
)
WITH (OIDS=FALSE)
;

COMMENT ON TABLE "ep_temp_master"."iac_tdelivery_edi" IS 'iac.tdelivery.edi';

 

COMMENT ON TABLE "ep_temp_master"."iac_tdelivery_edi" IS 'iac.tdelivery.edi';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."buyer_remark" IS 'buyer remark';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."status" IS 'Status';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."write_date" IS 'Last Updated on';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."create_uid" IS 'Created by';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."write_uid" IS 'Last Updated by';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."plant_id" IS 'Plant';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."vendor_id" IS '廠商代碼';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."shipping_date" IS 'shipping date';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."material_id" IS '料號';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."qty" IS 'QTY';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."cdt" IS 'cdt';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."iac_pn_vendor" IS 'iac_pn vendor';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."reply_id" IS 'Reply id';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."uploader" IS 'uploader';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."create_date" IS 'Created on';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."buyer_id" IS 'IACP採購';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."key_part" IS 'key part';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."fcst_version" IS 'fcst_version';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."iac_pn" IS 'iac_pn';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."plant" IS 'plant';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."vendor_code" IS 'vendor_code';

COMMENT ON COLUMN "ep_temp_master"."iac_tdelivery_edi"."valid" IS 'valid';
 
  
-- ----------------------------
-- Create sequence
-- ----------------------------

DROP SEQUENCE IF EXISTS "ep_temp_master"."iac_tdelivery_edi_id_seq";

CREATE SEQUENCE "ep_temp_master"."iac_tdelivery_edi_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."iac_tdelivery_edi"."id";

--select * from "ep_temp_master"."iac_tdelivery_edi_id_seq" ;

-- ----------------------------
-- create pkey
-- ----------------------------

alter table ep_temp_master.iac_tdelivery_edi add CONSTRAINT  "iac_tdelivery_edi_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- add pkey default
-- ----------------------------

ALTER TABLE ep_temp_master.iac_tdelivery_edi ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_tdelivery_edi_id_seq'::regclass);

ALTER TABLE "ep_temp_master"."iac_tdelivery_edi" OWNER TO "openerp";

------///////////////////////------------

--------------------
---建立错误数据中间表
--------------------

DROP TABLE IF EXISTS "ep_temp_master"."iac_tdelivery_edi_error";

CREATE TABLE "ep_temp_master"."iac_tdelivery_edi_error" as select * from "ep_temp_master"."iac_tdelivery_edi" where 1=2;

alter table ep_temp_master.iac_tdelivery_edi_error add CONSTRAINT  "iac_tdelivery_edi_error_pkey" PRIMARY KEY ("id");
 
--------------------
--- 增加欄位  need_re_update,need_update_id
-------------------- 
  
alter table	public.iac_tdelivery_edi ADD COLUMN need_re_update int4 ;
alter table	public.iac_tdelivery_edi ADD COLUMN need_update_id int4;

-- ----------------------------
-- add fun_def table
-- ----------------------------

alter table	public.iac_tdelivery_edi	ALTER COLUMN need_re_update SET DEFAULT 0;

update	public.iac_tdelivery_edi	set need_re_update =0 where need_re_update is null;

--------------------
--- 增加欄位 finish : 判斷是否已轉public
-------------------- 
alter table	ep_temp_master.iac_tdelivery_edi ADD COLUMN finish varchar ;


