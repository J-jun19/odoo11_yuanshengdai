-- ----------------------------
-- Table structure for goods_receipts
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."goods_receipts";
CREATE TABLE "ep_temp_master"."goods_receipts" (
"id" int4 ,
"company_code" varchar COLLATE "default",
"create_date" timestamp(6),
"part_no" varchar COLLATE "default",
"asn_no" varchar COLLATE "default",
"write_uid" int4,
"document_erp_id" varchar COLLATE "default",
"gr_document_line_no" varchar COLLATE "default",
"qty_received" numeric,
"create_uid" int4,
"sap_control_no" varchar COLLATE "default",
"gr_document_year" int4,
"gr_document_date" date,
"gr_document_no" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"gr_document_time" timestamp(6),
"write_date" timestamp(6),
"movement_type" varchar COLLATE "default",
"po_line_no" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"asn_line_no" int4,
"qty_total" numeric,
"part_id" int4,
"vendor_id" int4,
"plant_id" int4,
"po_id" int4,
"po_line_id" int4,
"asn_id" int4,
"asn_line_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."goods_receipts" IS 'Goods Receipts';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."company_code" IS 'Company Code';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."asn_no" IS 'ASN NO';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."document_erp_id" IS 'SAP ID';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."gr_document_line_no" IS 'GR Line No';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."qty_received" IS 'Received Quantity';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."sap_control_no" IS 'SAP NO';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."gr_document_year" IS 'GR Year';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."gr_document_date" IS 'GR Date';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."gr_document_no" IS 'GR No';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."buyer_erp_id" IS 'Buyer Code';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."gr_document_time" IS 'GR Time';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."movement_type" IS 'Move Type';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."po_line_no" IS 'Po Line No';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."asn_line_no" IS 'ASN Line NO';
COMMENT ON COLUMN "ep_temp_master"."goods_receipts"."qty_total" IS 'Total Quantity';


-- ----------------------------
-- Table structure for source_list
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."source_list";
CREATE TABLE "ep_temp_master"."source_list" (
"id" int4 DEFAULT nextval('"ep_temp_master".source_list_id_seq'::regclass) NOT NULL,
"isfix_flag" varchar COLLATE "default",
"create_date" timestamp(6),
"write_date" timestamp(6),
"part_no" varchar COLLATE "default",
"special_stock_indicator" varchar COLLATE "default",
"mrp_indicator" varchar COLLATE "default",
"creation_date" varchar COLLATE "default",
"issue_plant" varchar COLLATE "default",
"agree_item" int4,
"purchase_org" varchar COLLATE "default",
"po_category" varchar COLLATE "default",
"unit_of_measure" varchar COLLATE "default",
"block_flag" varchar COLLATE "default",
"created_by" varchar COLLATE "default",
"fixed_outline" varchar COLLATE "default",
"create_uid" int4,
"record_category" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"record_number" int4,
"procured_plant" varchar COLLATE "default",
"logical_system" varchar COLLATE "default",
"write_uid" int4,
"plant_code" varchar COLLATE "default",
"manufacturer_part_no" varchar COLLATE "default",
"agree_number" varchar COLLATE "default",
"valid_from" date,
"valid_to" date,
CONSTRAINT "source_list_pkey" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;
COMMENT ON TABLE "ep_temp_master"."source_list" IS 'source.list';
COMMENT ON COLUMN "ep_temp_master"."source_list"."isfix_flag" IS 'Is Fix Flag';
COMMENT ON COLUMN "ep_temp_master"."source_list"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."source_list"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."source_list"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."source_list"."special_stock_indicator" IS 'Special Stock Indicator';
COMMENT ON COLUMN "ep_temp_master"."source_list"."mrp_indicator" IS 'MRP Indicator';
COMMENT ON COLUMN "ep_temp_master"."source_list"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."source_list"."issue_plant" IS 'Issue Plant';
COMMENT ON COLUMN "ep_temp_master"."source_list"."agree_item" IS 'Agree Item';
COMMENT ON COLUMN "ep_temp_master"."source_list"."purchase_org" IS 'Purchase Org';
COMMENT ON COLUMN "ep_temp_master"."source_list"."po_category" IS 'PO Category';
COMMENT ON COLUMN "ep_temp_master"."source_list"."valid_from" IS 'Valid From';
COMMENT ON COLUMN "ep_temp_master"."source_list"."unit_of_measure" IS 'Unit Of Measure';
COMMENT ON COLUMN "ep_temp_master"."source_list"."block_flag" IS 'Block Flag';
COMMENT ON COLUMN "ep_temp_master"."source_list"."created_by" IS 'Created By';
COMMENT ON COLUMN "ep_temp_master"."source_list"."fixed_outline" IS 'Fixed Outline';
COMMENT ON COLUMN "ep_temp_master"."source_list"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."source_list"."record_category" IS 'Record Category';
COMMENT ON COLUMN "ep_temp_master"."source_list"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."source_list"."record_number" IS 'Record Number';
COMMENT ON COLUMN "ep_temp_master"."source_list"."procured_plant" IS 'Procured Plant';
COMMENT ON COLUMN "ep_temp_master"."source_list"."logical_system" IS 'Logical System';
COMMENT ON COLUMN "ep_temp_master"."source_list"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."source_list"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."source_list"."valid_to" IS 'Valid To';
COMMENT ON COLUMN "ep_temp_master"."source_list"."manufacturer_part_no" IS 'Manufacturer Part NO';
COMMENT ON COLUMN "ep_temp_master"."source_list"."agree_number" IS 'Agree Number';


-- ----------------------------
-- Table structure for inforecord_history
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."inforecord_history";
CREATE TABLE "ep_temp_master"."inforecord_history" (
"id" int4 ,
"create_date" timestamp(6),
"part_no" varchar COLLATE "default",
"price_unit" float8,
"creation_date" date,
"currency" varchar COLLATE "default",
"price_control" varchar COLLATE "default",
"purchase_org" varchar COLLATE "default",
"cw" varchar COLLATE "default",
"create_uid" int4,
"valid_from" date,
"application" varchar COLLATE "default",
"ltime" float8,
"price" float8,
"moq" float8,
"vendor_code" varchar COLLATE "default",
"rw" varchar COLLATE "default",
"write_date" timestamp(6),
"mpq" float8,
"write_uid" int4,
"taxcode" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"valid_to" date,
"condition_record" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."inforecord_history" IS 'inforecord.history';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."part_no" IS 'Part NO';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."price_unit" IS 'PriceUnit';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."currency" IS 'Currency';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."price_control" IS 'PriceControl';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."purchase_org" IS 'Purchase Org';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."cw" IS 'CW';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."valid_from" IS 'Valid From';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."application" IS 'Application';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."ltime" IS 'Ltime';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."price" IS 'Price';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."moq" IS 'MOQ';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."rw" IS 'RW';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."mpq" IS 'MPQ';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."taxcode" IS 'Taxcode';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."valid_to" IS 'Valid To';
COMMENT ON COLUMN "ep_temp_master"."inforecord_history"."condition_record" IS 'ConditionRecord';


-- ----------------------------
-- Table structure for plm_actual_vendor
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."plm_actual_vendor";
CREATE TABLE "ep_temp_master"."plm_actual_vendor" (
"id" int4 ,
"create_uid" int4,
"name" varchar COLLATE "default",
"write_uid" int4,
"write_date" timestamp(6),
"create_date" timestamp(6),
"fullname" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."plm_actual_vendor" IS 'plm.actual.vendor';
COMMENT ON COLUMN "ep_temp_master"."plm_actual_vendor"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."plm_actual_vendor"."name" IS 'name';
COMMENT ON COLUMN "ep_temp_master"."plm_actual_vendor"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."plm_actual_vendor"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."plm_actual_vendor"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."plm_actual_vendor"."fullname" IS 'Full Name';


-- ----------------------------
-- Table structure for plm_subclass
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."plm_subclass";
CREATE TABLE "ep_temp_master"."plm_subclass" (
"id" int4 ,
"create_uid" int4,
"class_code" varchar COLLATE "default",
"cht_name" varchar COLLATE "default",
"material_code" varchar COLLATE "default",
"material_group" varchar COLLATE "default",
"created_by" varchar COLLATE "default",
"subclass" varchar COLLATE "default",
"full_name" varchar COLLATE "default",
"created_date" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6),
"write_uid" int4,
"plm_id" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."plm_subclass" IS 'plm.subclass';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."class_code" IS 'Class Code';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."cht_name" IS 'CHT Name';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."material_code" IS 'MaterialCode';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."material_group" IS 'Material Group';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."created_by" IS 'Created By';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."subclass" IS 'SubClass';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."full_name" IS 'Full Name';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."created_date" IS 'Created Date';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."plm_subclass"."plm_id" IS 'PLM ID';


-- ----------------------------
-- Table structure for company
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."company";
CREATE TABLE "ep_temp_master"."company" (
"id" int4 ,
"city" varchar COLLATE "default",
"address_id" varchar COLLATE "default",
"company_code" varchar COLLATE "default",
"create_uid" int4,
"write_uid" int4,
"company_code1" varchar COLLATE "default",
"company_name" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6)
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."company" IS 'company';
COMMENT ON COLUMN "ep_temp_master"."company"."city" IS 'City';
COMMENT ON COLUMN "ep_temp_master"."company"."address_id" IS 'Address ID';
COMMENT ON COLUMN "ep_temp_master"."company"."company_code" IS 'Company Code';
COMMENT ON COLUMN "ep_temp_master"."company"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."company"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."company"."company_code1" IS 'Company Code1';
COMMENT ON COLUMN "ep_temp_master"."company"."company_name" IS 'Company Name';
COMMENT ON COLUMN "ep_temp_master"."company"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."company"."create_date" IS 'Created on';



-- ----------------------------
-- Table structure for pur_org_data
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."pur_org_data";
CREATE TABLE "ep_temp_master"."pur_org_data" (
"id" int4 ,
"create_uid" int4,
"address_id" varchar COLLATE "default",
"plant_name_en" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"plant_name_cn" varchar COLLATE "default",
"write_uid" int4,
"create_date" timestamp(6),
"write_date" timestamp(6),
"plant_code1" varchar COLLATE "default",
"purchase_org" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."pur_org_data" IS 'pur.org.data';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."address_id" IS 'Address ID';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."plant_name_en" IS 'Plant Name En';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."plant_name_cn" IS 'Plant Name Cn';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."plant_code1" IS 'Plant Code1';
COMMENT ON COLUMN "ep_temp_master"."pur_org_data"."purchase_org" IS 'Purchase Org';



-- ----------------------------
-- Table structure for material_group
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_group";
CREATE TABLE "ep_temp_master"."material_group" (
"id" int4 ,
"create_uid" int4,
"create_date" timestamp(6),
"description" varchar COLLATE "default",
"material_group" varchar COLLATE "default",
"write_uid" int4,
"write_date" timestamp(6)
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."material_group" IS 'material.group';
COMMENT ON COLUMN "ep_temp_master"."material_group"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."material_group"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."material_group"."description" IS 'Description';
COMMENT ON COLUMN "ep_temp_master"."material_group"."material_group" IS 'Material Group';
COMMENT ON COLUMN "ep_temp_master"."material_group"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."material_group"."write_date" IS 'Last Updated on';



-- ----------------------------
-- Table structure for buyer_code
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."buyer_code";
CREATE TABLE "ep_temp_master"."buyer_code" (
"id" int4 ,
"create_uid" int4,
"buyer_name" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"write_uid" int4,
"buyer_ad_account" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6)
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."buyer_code" IS 'buyer.code';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."buyer_name" IS 'Buyer Name';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."buyer_erp_id" IS 'buyer SAP ID';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."buyer_ad_account" IS 'Buyer Login Account';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."buyer_code"."create_date" IS 'Created on';



-- ----------------------------
-- Table structure for ship_instruct
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."ship_instruct";
CREATE TABLE "ep_temp_master"."ship_instruct" (
"id" int4 ,
"create_uid" int4,
"ship_description" varchar COLLATE "default",
"write_uid" int4,
"ship_id" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6),
"language_key" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."ship_instruct" IS 'ship.instruct';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."ship_description" IS 'Ship Description';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."ship_id" IS 'Ship ID';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."ship_instruct"."language_key" IS 'Language Key';


-- ----------------------------
-- Table structure for payment_term
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."payment_term";
CREATE TABLE "ep_temp_master"."payment_term" (
"id" int4 ,
"create_uid" int4,
"payment_term" varchar COLLATE "default",
"payment_description" varchar COLLATE "default",
"write_uid" int4,
"write_date" timestamp(6),
"create_date" timestamp(6),
"language_key" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."payment_term" IS 'payment.term';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."payment_term" IS 'Payment Term';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."payment_description" IS 'Payment Description';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."payment_term"."language_key" IS 'Language Key';



-- ----------------------------
-- Table structure for vendor_group
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."vendor_group";
CREATE TABLE "ep_temp_master"."vendor_group" (
"id" int4 ,
"create_uid" int4,
"account_group_name" varchar COLLATE "default",
"write_uid" int4,
"write_date" timestamp(6),
"create_date" timestamp(6),
"vendor_account_group" varchar COLLATE "default",
"language_key" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."vendor_group" IS 'vendor.group';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."account_group_name" IS 'Account Group Name';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."vendor_account_group" IS 'Vendor Account Group';
COMMENT ON COLUMN "ep_temp_master"."vendor_group"."language_key" IS 'Language Key';



-- ----------------------------
-- Table structure for division_code
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."division_code";
CREATE TABLE "ep_temp_master"."division_code" (
"id" int4 ,
"create_uid" int4,
"write_date" timestamp(6),
"division" varchar COLLATE "default",
"write_uid" int4,
"division_description" varchar COLLATE "default",
"create_date" timestamp(6),
"language_key" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."division_code" IS 'division.code';
COMMENT ON COLUMN "ep_temp_master"."division_code"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."division_code"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."division_code"."division" IS 'Division';
COMMENT ON COLUMN "ep_temp_master"."division_code"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."division_code"."division_description" IS 'Division Description';
COMMENT ON COLUMN "ep_temp_master"."division_code"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."division_code"."language_key" IS 'Language Key';


-- ----------------------------
-- Table structure for payment_info
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."payment_info";
CREATE TABLE "ep_temp_master"."payment_info" (
"id" int4 ,
"create_uid" int4,
"b" varchar COLLATE "default",
"write_uid" int4,
"assignment" varchar COLLATE "default",
"m" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"vendor_name" varchar COLLATE "default",
"currency" varchar COLLATE "default",
"amount" float8,
"write_date" timestamp(6),
"text" varchar COLLATE "default",
"create_date" timestamp(6),
"document" varchar COLLATE "default",
"referenece" varchar COLLATE "default",
"company_code" varchar COLLATE "default",
"document_year" varchar COLLATE "default",
"document_line" varchar COLLATE "default",
"post_date" date,
"clear_date" date
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."payment_info" IS 'payment.info';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."b" IS 'B';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."assignment" IS 'Assignment';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."m" IS 'M';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."vendor_code" IS 'Vendor_Code';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."vendor_name" IS 'Vendor_Name';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."currency" IS 'Currency';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."amount" IS 'Amount';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."text" IS 'Text';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."document" IS 'Document';
COMMENT ON COLUMN "ep_temp_master"."payment_info"."referenece" IS 'Referenece';



-- ----------------------------
-- Table structure for material_description
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_description";
CREATE TABLE "ep_temp_master"."material_description" (
"id" int4 ,
"part_description" varchar COLLATE "default",
"create_uid" int4,
"part_no" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"write_uid" int4,
"part_description1" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6),
"language_key" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."material_description" IS 'material.description';
COMMENT ON COLUMN "ep_temp_master"."material_description"."part_description" IS 'Part Description';
COMMENT ON COLUMN "ep_temp_master"."material_description"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."material_description"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."material_description"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."material_description"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."material_description"."part_description1" IS 'Part Description1';
COMMENT ON COLUMN "ep_temp_master"."material_description"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."material_description"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."material_description"."language_key" IS 'Language Key';



-- ----------------------------
-- Table structure for material_master
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_master";
CREATE TABLE "ep_temp_master"."material_master" (
"id" int4 ,
"division" varchar COLLATE "default",
"create_uid" int4,
"part_no" varchar COLLATE "default",
"material_group" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"material_category" varchar COLLATE "default",
"write_uid" int4,
"create_date" timestamp(6),
"part_type" varchar COLLATE "default",
"write_date" timestamp(6),
"change_date" date,
"order_uom" varchar COLLATE "default",
"creation_date" date,
"unit" varchar COLLATE "default",
"part_unique_code" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."material_master" IS 'material.master';
COMMENT ON COLUMN "ep_temp_master"."material_master"."division" IS 'Division';
COMMENT ON COLUMN "ep_temp_master"."material_master"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."material_master"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."material_master"."material_group" IS 'Material Group';
COMMENT ON COLUMN "ep_temp_master"."material_master"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."material_master"."material_category" IS 'Material Category';
COMMENT ON COLUMN "ep_temp_master"."material_master"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."material_master"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."material_master"."part_type" IS 'Part Type';
COMMENT ON COLUMN "ep_temp_master"."material_master"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."material_master"."change_date" IS 'Change Date';
COMMENT ON COLUMN "ep_temp_master"."material_master"."order_uom" IS 'Order Uom';
COMMENT ON COLUMN "ep_temp_master"."material_master"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."material_master"."unit" IS 'Unit';



-- ----------------------------
-- Table structure for material_plant
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_plant";
CREATE TABLE "ep_temp_master"."material_plant" (
"id" int4 ,
"create_date" timestamp(6),
"quota_arrangement_usage" varchar COLLATE "default",
"part_no" varchar COLLATE "default",
"write_uid" int4,
"critical_part_flag" varchar COLLATE "default",
"commodity_code" varchar COLLATE "default",
"record_point" float8,
"issue_storage_location" varchar COLLATE "default",
"planner_erp_id" varchar COLLATE "default",
"ltime" float8,
"rounding_value" float8,
"abc_indicator" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"create_uid" int4,
"gr_days" int4,
"procurement_type" varchar COLLATE "default",
"part_status" varchar COLLATE "default",
"write_date" timestamp(6),
"auto_po_allowed" varchar COLLATE "default",
"safety_stock" float8,
"deletion_flag" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"maximum_stock_level" float8,
"special_procurement_type" varchar COLLATE "default",
"post_to_insp_stock" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."material_plant" IS 'material.plant';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."quota_arrangement_usage" IS 'Quota Arrangement Usage';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."critical_part_flag" IS 'Critical Part Flag';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."commodity_code" IS 'Commodity Code';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."record_point" IS 'Record Point';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."issue_storage_location" IS 'Issue Storage Location';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."planner_erp_id" IS 'Planner Erp Id';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."ltime" IS 'Ltime';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."rounding_value" IS 'Rounding Value';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."abc_indicator" IS 'Abc Indicator';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."buyer_erp_id" IS 'Buyer Code';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."gr_days" IS 'Gr Days';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."procurement_type" IS 'Procurement Type';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."part_status" IS 'Part Status';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."auto_po_allowed" IS 'Auto Po Allowed';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."safety_stock" IS 'Safety Stock';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."maximum_stock_level" IS 'Maximum Stock Level';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."special_procurement_type" IS 'Special Procurement Type';
COMMENT ON COLUMN "ep_temp_master"."material_plant"."post_to_insp_stock" IS 'Post To Insp Stock';



-- ----------------------------
-- Table structure for material_map
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_map";
CREATE TABLE "ep_temp_master"."material_map" (
"id" int4 ,
"create_uid" int4,
"part_no" varchar COLLATE "default",
"price" float8,
"plant_code" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6),
"write_uid" int4,
"price_unit" int4
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."material_map" IS 'material.map';
COMMENT ON COLUMN "ep_temp_master"."material_map"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."material_map"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."material_map"."price" IS 'Price';
COMMENT ON COLUMN "ep_temp_master"."material_map"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."material_map"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."material_map"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."material_map"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."material_map"."price_unit" IS 'Price Unit';


-- ----------------------------
-- Table structure for material_custmaster
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_custmaster";
CREATE TABLE "ep_temp_master"."material_custmaster" (
"id" int4 ,
"create_uid" int4,
"part_status_by_site" varchar COLLATE "default",
"last_buy_flag" varchar COLLATE "default",
"material_group_cn" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"sourcer" varchar COLLATE "default",
"part_no" varchar COLLATE "default",
"buy_sell_flag" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6),
"write_uid" int4,
"gr_location" varchar COLLATE "default",
"rma_flag" varchar COLLATE "default"
)
WITH (OIDS=FALSE)
;


-- ----------------------------
-- Table structure for material_division
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."material_division";
CREATE TABLE "ep_temp_master"."material_division" (
"id" int4 ,
"division" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"create_uid" int4,
"part_no" varchar COLLATE "default",
"changed_by" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"created_by" varchar COLLATE "default",
"creation_date" date,
"write_date" timestamp(6),
"change_date" date,
"create_date" timestamp(6),
"write_uid" int4
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."material_division" IS 'material.division';
COMMENT ON COLUMN "ep_temp_master"."material_division"."division" IS 'Division';
COMMENT ON COLUMN "ep_temp_master"."material_division"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."material_division"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."material_division"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."material_division"."changed_by" IS 'Changed By';
COMMENT ON COLUMN "ep_temp_master"."material_division"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."material_division"."created_by" IS 'Created By';
COMMENT ON COLUMN "ep_temp_master"."material_division"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."material_division"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."material_division"."change_date" IS 'Change Date';
COMMENT ON COLUMN "ep_temp_master"."material_division"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."material_division"."write_uid" IS 'Last Updated by';



-- ----------------------------
-- Table structure for po_header
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."po_header";
CREATE TABLE "ep_temp_master"."po_header" (
"id" int4 ,
"address_id" varchar COLLATE "default",
"company_code" varchar COLLATE "default",
"create_date" timestamp(6),
"payment_term" varchar COLLATE "default",
"write_uid" int4,
"document_erp_id" varchar COLLATE "default",
"exchange_rate" varchar COLLATE "default",
"purchase_org" varchar COLLATE "default",
"manually_po_comment2" varchar COLLATE "default",
"document_date" date,
"create_uid" int4,
"incoterm1" varchar COLLATE "default",
"order_type" varchar COLLATE "default",
"created_by" varchar COLLATE "default",
"contact_phone" varchar COLLATE "default",
"language_key" varchar COLLATE "default",
"status" varchar COLLATE "default",
"incoterm" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"write_date" timestamp(6),
"your_reference" varchar COLLATE "default",
"our_reference" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"currency" varchar COLLATE "default",
"manually_po_comment" varchar COLLATE "default",
"manually_po_reason" varchar COLLATE "default",
"manually_po_reason_type" varchar COLLATE "default",
"contact_person" varchar COLLATE "default",
"document_release_status" varchar COLLATE "default",
"document_category" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."po_header" IS 'po.header';
COMMENT ON COLUMN "ep_temp_master"."po_header"."address_id" IS 'Address Id';
COMMENT ON COLUMN "ep_temp_master"."po_header"."company_code" IS 'Company Code';
COMMENT ON COLUMN "ep_temp_master"."po_header"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."po_header"."payment_term" IS 'Payment Term';
COMMENT ON COLUMN "ep_temp_master"."po_header"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."po_header"."document_erp_id" IS 'Document Erp Id';
COMMENT ON COLUMN "ep_temp_master"."po_header"."exchange_rate" IS 'Exchange Rate';
COMMENT ON COLUMN "ep_temp_master"."po_header"."purchase_org" IS 'Purchase Org';
COMMENT ON COLUMN "ep_temp_master"."po_header"."manually_po_comment2" IS 'Manually Po Comment2';
COMMENT ON COLUMN "ep_temp_master"."po_header"."document_date" IS 'Document Date';
COMMENT ON COLUMN "ep_temp_master"."po_header"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."po_header"."incoterm1" IS 'Incoterm1';
COMMENT ON COLUMN "ep_temp_master"."po_header"."order_type" IS 'Order Type';
COMMENT ON COLUMN "ep_temp_master"."po_header"."created_by" IS 'Created By';
COMMENT ON COLUMN "ep_temp_master"."po_header"."contact_phone" IS 'Contact Phone';
COMMENT ON COLUMN "ep_temp_master"."po_header"."language_key" IS 'Language Key';
COMMENT ON COLUMN "ep_temp_master"."po_header"."status" IS 'Status';
COMMENT ON COLUMN "ep_temp_master"."po_header"."incoterm" IS 'Incoterm';
COMMENT ON COLUMN "ep_temp_master"."po_header"."buyer_erp_id" IS 'Buyer Erp Id';
COMMENT ON COLUMN "ep_temp_master"."po_header"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."po_header"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."po_header"."your_reference" IS 'Your Reference';
COMMENT ON COLUMN "ep_temp_master"."po_header"."our_reference" IS 'Our Reference';
COMMENT ON COLUMN "ep_temp_master"."po_header"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."po_header"."currency" IS 'Currency';
COMMENT ON COLUMN "ep_temp_master"."po_header"."manually_po_comment" IS 'Manually Po Comment';
COMMENT ON COLUMN "ep_temp_master"."po_header"."manually_po_reason" IS 'Manually Po Reason';
COMMENT ON COLUMN "ep_temp_master"."po_header"."manually_po_reason_type" IS 'Manually Po Reason Type';
COMMENT ON COLUMN "ep_temp_master"."po_header"."contact_person" IS 'Contact Person';
COMMENT ON COLUMN "ep_temp_master"."po_header"."document_release_status" IS 'Document Release Status';
COMMENT ON COLUMN "ep_temp_master"."po_header"."document_category" IS 'Document Category';



-- ----------------------------
-- Table structure for po_partner
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."po_partner";
CREATE TABLE "ep_temp_master"."po_partner" (
"id" int4 ,
"create_uid" int4,
"document_line_erp_id" varchar COLLATE "default",
"partner_function" varchar COLLATE "default",
"reference_vendor_code" varchar COLLATE "default",
"creation_date" date,
"document_erp_id" varchar COLLATE "default",
"write_date" timestamp(6),
"create_date" timestamp(6),
"purchase_org" varchar COLLATE "default",
"write_uid" int4
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."po_partner" IS 'po.partner';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."document_line_erp_id" IS 'Document Line Erp Id';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."partner_function" IS 'Partner Function';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."reference_vendor_code" IS 'Reference Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."document_erp_id" IS 'Document Erp Id';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."purchase_org" IS 'Purchase Org';
COMMENT ON COLUMN "ep_temp_master"."po_partner"."write_uid" IS 'Last Updated by';



-- ----------------------------
-- Table structure for po_detail
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."po_detail";
CREATE TABLE "ep_temp_master"."po_detail" (
"id" int4 ,
"address_id" varchar COLLATE "default",
"create_date" timestamp(6),
"part_no" varchar COLLATE "default",
"price_unit" float8,
"document_line_erp_id" varchar COLLATE "default",
"write_uid" int4,
"document_erp_id" varchar COLLATE "default",
"delivery_complete" varchar COLLATE "default",
"price_determine_date" date,
"unit" varchar COLLATE "default",
"create_uid" int4,
"tax_code" varchar COLLATE "default",
"price" float8,
"vendor_part_no" varchar COLLATE "default",
"vendor_to_be_supply" varchar COLLATE "default",
"storage_location" varchar COLLATE "default",
"revision_level" varchar COLLATE "default",
"rfq_status" varchar COLLATE "default",
"part_no1" varchar COLLATE "default",
"write_date" timestamp(6),
"purchase_req_item_no" varchar COLLATE "default",
"short_text" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"rfq_no" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"purchase_req_no" varchar COLLATE "default",
"reject_flag" varchar COLLATE "default",
"tracking_number" varchar COLLATE "default",
"manufacturer_part_no" varchar COLLATE "default",
"change_date" varchar COLLATE "default",
"quantity" float8,
"delivery_date" date
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."po_detail" IS 'po.detail';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."address_id" IS 'Address Id';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."price_unit" IS 'Price Unit';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."document_line_erp_id" IS 'Document Line Erp Id';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."document_erp_id" IS 'Document Erp Id';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."delivery_complete" IS 'Delivery Complete';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."price_determine_date" IS 'Price Determine Date';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."unit" IS 'Unit';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."tax_code" IS 'Tax Code';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."price" IS 'Price';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."vendor_part_no" IS 'Vendor Part No';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."vendor_to_be_supply" IS 'Vendor To Be Supply';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."storage_location" IS 'Storage Location';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."revision_level" IS 'Revision Level';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."rfq_status" IS 'Rfq Status';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."part_no1" IS 'Part No1';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."purchase_req_item_no" IS 'Purchase Req Item No';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."short_text" IS 'Short Text';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."rfq_no" IS 'Rfq No';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."purchase_req_no" IS 'Purchase Req No';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."reject_flag" IS 'Reject Flag';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."tracking_number" IS 'Tracking Number';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."manufacturer_part_no" IS 'Manufacturer Part No';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."change_date" IS 'Change Date';
COMMENT ON COLUMN "ep_temp_master"."po_detail"."quantity" IS 'Quantity';



-- ----------------------------
-- Table structure for vendor_plant
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."vendor_plant";
CREATE TABLE "ep_temp_master"."vendor_plant" (
"id" int4 ,
"create_uid" int4,
"confirmation_control_key" varchar COLLATE "default",
"incoterm1" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"ers" varchar COLLATE "default",
"payment_term" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"creation_date" date,
"currency" varchar COLLATE "default",
"sales_telephone" varchar COLLATE "default",
"incoterm" varchar COLLATE "default",
"write_date" timestamp(6),
"purchase_block" varchar COLLATE "default",
"purchase_org" varchar COLLATE "default",
"write_uid" int4,
"sales_person" varchar COLLATE "default",
"create_date" timestamp(6)
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."vendor_plant" IS 'vendor.plant';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."confirmation_control_key" IS 'Confirmation Control Key';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."incoterm1" IS 'Incoterm1';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."buyer_erp_id" IS 'Buyer Erp Id';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."ers" IS 'Ers';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."payment_term" IS 'Payment Term';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."currency" IS 'Currency';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."sales_telephone" IS 'Sales_Telephone';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."incoterm" IS 'Incoterm';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."purchase_block" IS 'Purchase Block';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."purchase_org" IS 'Purchase Org';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."sales_person" IS 'Sales Person';
COMMENT ON COLUMN "ep_temp_master"."vendor_plant"."create_date" IS 'Created on';


-- ----------------------------
-- Table structure for vendor_bank
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."vendor_bank";
CREATE TABLE "ep_temp_master"."vendor_bank" (
"id" int4 ,
"special_bank_detail" varchar COLLATE "default",
"address_id" varchar COLLATE "default",
"create_date" timestamp(6),
"creation_date" varchar COLLATE "default",
"bank_group" varchar COLLATE "default",
"create_uid" int4,
"partner_bank_type" varchar COLLATE "default",
"lanuage_key" varchar COLLATE "default",
"create_by" varchar COLLATE "default",
"post_account" varchar COLLATE "default",
"branch" varchar COLLATE "default",
"bank_control_key" varchar COLLATE "default",
"swift_code" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"bank_city" varchar COLLATE "default",
"post_current_bank_number" varchar COLLATE "default",
"write_date" timestamp(6),
"write_uid" int4,
"bank_region" varchar COLLATE "default",
"account_hold_number" varchar COLLATE "default",
"name" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"bank_country_code" varchar COLLATE "default",
"account_number" varchar COLLATE "default",
"bank_key" varchar COLLATE "default",
"bank_number" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."vendor_bank" IS 'vendor.bank';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."special_bank_detail" IS 'Special Bank Detail';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."address_id" IS 'Address Id';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_group" IS 'Bank Group';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."partner_bank_type" IS 'Partner Bank Type';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."lanuage_key" IS 'Lanuage Key';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."create_by" IS 'Create By';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."post_account" IS 'Post Account';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."branch" IS 'Branch';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_control_key" IS 'Bank Control Key';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."swift_code" IS 'Swift Code';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_city" IS 'Bank City';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."post_current_bank_number" IS 'Post Current Bank Number';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_region" IS 'Bank Region';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."account_hold_number" IS 'Account Hold Number';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."name" IS 'Name';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_country_code" IS 'Bank Country Code';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."account_number" IS 'Account Number';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_key" IS 'Bank Key';
COMMENT ON COLUMN "ep_temp_master"."vendor_bank"."bank_number" IS 'Bank Number';




-- ----------------------------
-- Table structure for vendor_certified
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."vendor_certified";
CREATE TABLE "ep_temp_master"."vendor_certified" (
"id" int4 ,
"create_uid" int4,
"write_date" timestamp(6),
"score_thisyear" float8,
"vendor_code" varchar COLLATE "default",
"write_uid" int4,
"score_previous" float8,
"class_previous" varchar COLLATE "default",
"create_date" timestamp(6),
"supplier_type" varchar COLLATE "default",
"class_thisyear" varchar COLLATE "default",
"vendor_email" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."vendor_certified" IS 'vendor.certified';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."score_thisyear" IS 'Score This Year';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."score_previous" IS 'Score Previous';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."class_previous" IS 'Class Previous';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."supplier_type" IS 'Supplier Type';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."class_thisyear" IS 'Class This Year';
COMMENT ON COLUMN "ep_temp_master"."vendor_certified"."vendor_email" IS 'Vendor Email';

-- ----------------------------
-- Table structure for address
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."address";
CREATE TABLE "ep_temp_master"."address" (
"id" int4 ,
"address_id" varchar COLLATE "default",
"create_date" timestamp(6),
"write_uid" int4,
"street" varchar COLLATE "default",
"country_code" varchar COLLATE "default",
"po_box" varchar COLLATE "default",
"city2" varchar COLLATE "default",
"city1" varchar COLLATE "default",
"create_uid" int4,
"nam1" varchar COLLATE "default",
"nam2" varchar COLLATE "default",
"language_key" varchar COLLATE "default",
"fax" varchar COLLATE "default",
"house_num1" varchar COLLATE "default",
"street2" varchar COLLATE "default",
"street3" varchar COLLATE "default",
"street4" varchar COLLATE "default",
"name4" varchar COLLATE "default",
"name3" varchar COLLATE "default",
"write_date" timestamp(6),
"post_code1" varchar COLLATE "default",
"post_code2" varchar COLLATE "default",
"region" varchar COLLATE "default",
"telphone" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."address" IS 'address';
COMMENT ON COLUMN "ep_temp_master"."address"."address_id" IS 'ADDRESS ID';
COMMENT ON COLUMN "ep_temp_master"."address"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."address"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."address"."street" IS 'STREET';
COMMENT ON COLUMN "ep_temp_master"."address"."country_code" IS 'COUNTRY CODE';
COMMENT ON COLUMN "ep_temp_master"."address"."po_box" IS 'PO_BOX';
COMMENT ON COLUMN "ep_temp_master"."address"."city2" IS 'CITY2';
COMMENT ON COLUMN "ep_temp_master"."address"."city1" IS 'CITY1';
COMMENT ON COLUMN "ep_temp_master"."address"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."address"."nam1" IS 'NAM1';
COMMENT ON COLUMN "ep_temp_master"."address"."nam2" IS 'NAM2';
COMMENT ON COLUMN "ep_temp_master"."address"."language_key" IS 'LANGUAGE KEY';
COMMENT ON COLUMN "ep_temp_master"."address"."fax" IS 'FAX';
COMMENT ON COLUMN "ep_temp_master"."address"."house_num1" IS 'HOUSE NUM1';
COMMENT ON COLUMN "ep_temp_master"."address"."street2" IS 'STREET2';
COMMENT ON COLUMN "ep_temp_master"."address"."street3" IS 'STREET3';
COMMENT ON COLUMN "ep_temp_master"."address"."street4" IS 'STREET4';
COMMENT ON COLUMN "ep_temp_master"."address"."name4" IS 'NAME4';
COMMENT ON COLUMN "ep_temp_master"."address"."name3" IS 'NAME3';
COMMENT ON COLUMN "ep_temp_master"."address"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."address"."post_code1" IS 'POST CODE1';
COMMENT ON COLUMN "ep_temp_master"."address"."post_code2" IS 'POST CODE2';
COMMENT ON COLUMN "ep_temp_master"."address"."region" IS 'REGION';
COMMENT ON COLUMN "ep_temp_master"."address"."telphone" IS 'TELPHONE';



-- ----------------------------
-- Table structure for vs_webflow_iqc_data
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."vs_webflow_iqc_data";
CREATE TABLE "ep_temp_master"."vs_webflow_iqc_data" (
"id" int4 ,
"create_date" timestamp(6),
"part_no" varchar COLLATE "default",
"lurking_cost" float8,
"creation_date" date,
"cdt" varchar COLLATE "default",
"mo_cnf_qty" float8,
"supplier_company_id" varchar COLLATE "default",
"create_uid" int4,
"rma_ma" float8,
"return_qty" float8,
"hardness_cost" float8,
"vendor_code" varchar COLLATE "default",
"rma_mi" float8,
"flag" varchar COLLATE "default",
"gr_qty" float8,
"write_date" timestamp(6),
"write_uid" int4,
"qual_qty" float8,
"material_group" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"tc_qty" float8,
"gr_mi" float8,
"gr_ma" float8
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."vs_webflow_iqc_data" IS 'vs.webflow.iqc.data';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."lurking_cost" IS 'Lurking Cost';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."creation_date" IS 'Creation Date';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."cdt" IS 'Cdt';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."mo_cnf_qty" IS 'Mo Cnf Qty';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."supplier_company_id" IS 'Supplier Company Id';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."rma_ma" IS 'Rma Ma';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."return_qty" IS 'Return Qty';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."hardness_cost" IS 'Hardness Cost';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."rma_mi" IS 'Rma Mi';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."flag" IS 'Flag';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."gr_qty" IS 'Gr Qty';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."qual_qty" IS 'Qual Qty';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."material_group" IS 'Material Group';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."tc_qty" IS 'Tc Qty';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."gr_mi" IS 'Gr Mi';
COMMENT ON COLUMN "ep_temp_master"."vs_webflow_iqc_data"."gr_ma" IS 'Gr Ma';


-- ----------------------------
-- Table structure for asn_maxqty
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."asn_maxqty";
CREATE TABLE "ep_temp_master"."asn_maxqty" (
"id" int4 ,
"division" varchar COLLATE "default",
"plant" varchar COLLATE "default",
"vendorcode" varchar COLLATE "default",
"create_uid" int4,
"createdate" date,
"material" varchar COLLATE "default",
"deliverytype" varchar COLLATE "default",
"version" varchar COLLATE "default",
"maxqty" float8,
"write_date" timestamp(6),
"create_date" timestamp(6),
"write_uid" int4,
"engineid" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."asn_maxqty" IS 'asn.maxqty';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."division" IS 'Division';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."plant" IS 'Plant';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."vendorcode" IS 'Vendorcode';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."createdate" IS 'Createdate';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."material" IS 'Material';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."deliverytype" IS 'Deliverytype';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."version" IS 'Version';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."maxqty" IS 'Maxqty';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."asn_maxqty"."engineid" IS 'Engineid';



-- ----------------------------
-- Table structure for asn_jitrule
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."asn_jitrule";
CREATE TABLE "ep_temp_master"."asn_jitrule" (
"id" int4 ,
"rule_type" varchar COLLATE "default",
"create_uid" int4,
"buyer_erp_id" varchar COLLATE "default",
"part_no" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"write_uid" int4,
"write_date" timestamp(6),
"create_date" timestamp(6),
"pulling_type" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."asn_jitrule" IS 'asn.jitrule';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."rule_type" IS 'Rule Type';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."buyer_erp_id" IS 'Buyer Erp Id';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."part_no" IS 'Part No';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."asn_jitrule"."pulling_type" IS 'Pulling Type';



-- ----------------------------
-- Table structure for incoterm
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."incoterm";
CREATE TABLE "ep_temp_master"."incoterm" (
"id" int4 ,
"create_uid" int4,
"write_date" timestamp(6),
"incoterm" varchar COLLATE "default",
"write_uid" int4,
"incoterm_description" varchar COLLATE "default",
"create_date" timestamp(6),
"language_key" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."incoterm" IS 'incoterm';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."incoterm" IS 'Incoterm';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."incoterm_description" IS 'Incoterm Description';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."incoterm"."language_key" IS 'Language Key';



-- ----------------------------
-- Table structure for vendor
-- ----------------------------
DROP TABLE IF EXISTS "ep_temp_master"."vendor";
CREATE TABLE "ep_temp_master"."vendor" (
"id" int4 ,
"address_id" varchar COLLATE "default",
"create_date" timestamp(6),
"address_pobox" varchar COLLATE "default",
"write_uid" int4,
"po_box_city" varchar COLLATE "default",
"po_box" varchar COLLATE "default",
"vat_number" varchar COLLATE "default",
"address_country" varchar COLLATE "default",
"create_uid" int4,
"address_street" varchar COLLATE "default",
"address_postalcode" varchar COLLATE "default",
"address_region" varchar COLLATE "default",
"address_district" varchar COLLATE "default",
"language_key" varchar COLLATE "default",
"company_telephone2" varchar COLLATE "default",
"name2_en" varchar COLLATE "default",
"short_name" varchar COLLATE "default",
"company_telephone1" varchar COLLATE "default",
"title" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"company_fax" varchar COLLATE "default",
"name2_cn" varchar COLLATE "default",
"write_date" timestamp(6),
"purchase_block" varchar COLLATE "default",
"vendor_account_group" varchar COLLATE "default",
"address_city" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"name1_cn" varchar COLLATE "default",
"vendor_url" varchar COLLATE "default",
"payment_block" varchar COLLATE "default",
"name1_en" varchar COLLATE "default",
"deletion_block" varchar COLLATE "default"
)
WITH (OIDS=FALSE)

;
COMMENT ON TABLE "ep_temp_master"."vendor" IS 'vendor';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_id" IS 'Address Id';
COMMENT ON COLUMN "ep_temp_master"."vendor"."create_date" IS 'Created on';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_pobox" IS 'Address Pobox';
COMMENT ON COLUMN "ep_temp_master"."vendor"."write_uid" IS 'Last Updated by';
COMMENT ON COLUMN "ep_temp_master"."vendor"."po_box_city" IS 'Po Box City';
COMMENT ON COLUMN "ep_temp_master"."vendor"."po_box" IS 'Po Box';
COMMENT ON COLUMN "ep_temp_master"."vendor"."vat_number" IS 'Vat Number';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_country" IS 'Address Country';
COMMENT ON COLUMN "ep_temp_master"."vendor"."create_uid" IS 'Created by';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_street" IS 'Address Street';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_postalcode" IS 'Address Postalcode';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_region" IS 'Address Region';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_district" IS 'Address District';
COMMENT ON COLUMN "ep_temp_master"."vendor"."language_key" IS 'Language Key';
COMMENT ON COLUMN "ep_temp_master"."vendor"."company_telephone2" IS 'Company Telephone2';
COMMENT ON COLUMN "ep_temp_master"."vendor"."name2_en" IS 'Name2 En';
COMMENT ON COLUMN "ep_temp_master"."vendor"."short_name" IS 'Short Name';
COMMENT ON COLUMN "ep_temp_master"."vendor"."company_telephone1" IS 'Company Telephone1';
COMMENT ON COLUMN "ep_temp_master"."vendor"."title" IS 'Title';
COMMENT ON COLUMN "ep_temp_master"."vendor"."vendor_code" IS 'Vendor Code';
COMMENT ON COLUMN "ep_temp_master"."vendor"."company_fax" IS 'Company Fax';
COMMENT ON COLUMN "ep_temp_master"."vendor"."name2_cn" IS 'Name2 Cn';
COMMENT ON COLUMN "ep_temp_master"."vendor"."write_date" IS 'Last Updated on';
COMMENT ON COLUMN "ep_temp_master"."vendor"."purchase_block" IS 'Purchase Block';
COMMENT ON COLUMN "ep_temp_master"."vendor"."vendor_account_group" IS 'Vendor Account Group';
COMMENT ON COLUMN "ep_temp_master"."vendor"."address_city" IS 'Address City';
COMMENT ON COLUMN "ep_temp_master"."vendor"."deletion_flag" IS 'Deletion Flag';
COMMENT ON COLUMN "ep_temp_master"."vendor"."plant_code" IS 'Plant Code';
COMMENT ON COLUMN "ep_temp_master"."vendor"."name1_cn" IS 'Name1 Cn';
COMMENT ON COLUMN "ep_temp_master"."vendor"."vendor_url" IS 'Vendor Url';
COMMENT ON COLUMN "ep_temp_master"."vendor"."payment_block" IS 'Payment Block';
COMMENT ON COLUMN "ep_temp_master"."vendor"."name1_en" IS 'Name1 En';
COMMENT ON COLUMN "ep_temp_master"."vendor"."deletion_block" IS 'Deletion Block';


DROP TABLE IF EXISTS "ep_temp_master"."storage_location";
CREATE TABLE "ep_temp_master"."storage_location" (
"id" int4 ,
"create_uid" int4,
"storage_location" varchar COLLATE "default",
"description" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"write_uid" int4,
"write_date" timestamp(6),
"create_date" timestamp(6)
)
WITH (OIDS=FALSE)
;


COMMENT ON TABLE "ep_temp_master"."storage_location" IS 'storage.location';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."create_uid" IS 'Created by';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."storage_location" IS 'Storage Location';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."description" IS 'Description';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."plant_code" IS 'Plant Code';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."write_uid" IS 'Last Updated by';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."write_date" IS 'Last Updated on';

COMMENT ON COLUMN "ep_temp_master"."storage_location"."create_date" IS 'Created on';

DROP TABLE IF EXISTS "ep_temp_master"."extractgroup";
CREATE TABLE "ep_temp_master"."extractgroup" (
"extractgroup" varchar(255) COLLATE "default",
"extractname" varchar(255) COLLATE "default"
)
WITH (OIDS=FALSE)
;

DROP TABLE IF EXISTS "ep_temp_master"."extractlog";
create table "ep_temp_master"."extractlog"
(
"extractwmid"	varchar(255),
"extractname"	varchar(255),
"sourcetable"	varchar(255),
"desttable"	varchar(255),
"extractdate"	timestamp        ,
"extractcount"	integer     ,
"extractstatus"	varchar(255),
"extractenddate"	timestamp
);



-- ----------------------------
-- Create sequence
-- ----------------------------
DROP SEQUENCE IF EXISTS "ep_temp_master"."goods_receipts_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."source_list_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."inforecord_history_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."plm_actual_vendor_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."plm_subclass_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."company_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."pur_org_data_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_group_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."buyer_code_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."ship_instruct_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."payment_term_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."vendor_group_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."incoterm_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."division_code_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."payment_info_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_description_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_master_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_plant_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_map_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_custmaster_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."material_division_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."po_header_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."po_partner_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."po_detail_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."storage_location_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."vendor_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."vendor_plant_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."vendor_bank_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."vendor_certified_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."address_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."vs_webflow_iqc_data_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."asn_maxqty_id_seq";

DROP SEQUENCE IF EXISTS "ep_temp_master"."asn_jitrule_id_seq";

CREATE SEQUENCE "ep_temp_master"."goods_receipts_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."goods_receipts"."id";
CREATE SEQUENCE "ep_temp_master"."source_list_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."source_list"."id";
CREATE SEQUENCE "ep_temp_master"."inforecord_history_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."inforecord_history"."id";
CREATE SEQUENCE "ep_temp_master"."plm_actual_vendor_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."plm_actual_vendor"."id";
CREATE SEQUENCE "ep_temp_master"."plm_subclass_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."plm_subclass"."id";
CREATE SEQUENCE "ep_temp_master"."company_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."company"."id";
CREATE SEQUENCE "ep_temp_master"."pur_org_data_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."pur_org_data"."id";
CREATE SEQUENCE "ep_temp_master"."material_group_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_group"."id";
CREATE SEQUENCE "ep_temp_master"."buyer_code_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."buyer_code"."id";
CREATE SEQUENCE "ep_temp_master"."ship_instruct_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."ship_instruct"."id";
CREATE SEQUENCE "ep_temp_master"."payment_term_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."payment_term"."id";
CREATE SEQUENCE "ep_temp_master"."vendor_group_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."vendor_group"."id";
CREATE SEQUENCE "ep_temp_master"."incoterm_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."incoterm"."id";
CREATE SEQUENCE "ep_temp_master"."division_code_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."division_code"."id";
CREATE SEQUENCE "ep_temp_master"."payment_info_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."payment_info"."id";
CREATE SEQUENCE "ep_temp_master"."material_description_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_description"."id";
CREATE SEQUENCE "ep_temp_master"."material_master_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_master"."id";
CREATE SEQUENCE "ep_temp_master"."material_plant_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_plant"."id";
CREATE SEQUENCE "ep_temp_master"."material_map_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_map"."id";
CREATE SEQUENCE "ep_temp_master"."material_custmaster_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_custmaster"."id";
CREATE SEQUENCE "ep_temp_master"."material_division_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."material_division"."id";
CREATE SEQUENCE "ep_temp_master"."po_header_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."po_header"."id";
CREATE SEQUENCE "ep_temp_master"."po_partner_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."po_partner"."id";
CREATE SEQUENCE "ep_temp_master"."po_detail_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."po_detail"."id";
CREATE SEQUENCE "ep_temp_master"."storage_location_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."storage_location"."id";
CREATE SEQUENCE "ep_temp_master"."vendor_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."vendor"."id";
CREATE SEQUENCE "ep_temp_master"."vendor_plant_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."vendor_plant"."id";
CREATE SEQUENCE "ep_temp_master"."vendor_bank_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."vendor_bank"."id";
CREATE SEQUENCE "ep_temp_master"."vendor_certified_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."vendor_certified"."id";
CREATE SEQUENCE "ep_temp_master"."address_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."address"."id";
CREATE SEQUENCE "ep_temp_master"."vs_webflow_iqc_data_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."vs_webflow_iqc_data"."id";
CREATE SEQUENCE "ep_temp_master"."asn_maxqty_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."asn_maxqty"."id";
CREATE SEQUENCE "ep_temp_master"."asn_jitrule_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "ep_temp_master"."asn_jitrule"."id";


DROP SEQUENCE IF EXISTS "public"."odoo_asn_005_id_seq";
CREATE SEQUENCE "public"."odoo_asn_005_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 ;

DROP SEQUENCE IF EXISTS "public"."odoo_po_005_id_seq";
CREATE SEQUENCE "public"."odoo_po_005_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 ;

DROP SEQUENCE IF EXISTS "public"."odoo_po_006_id_seq";
CREATE SEQUENCE "public"."odoo_po_006_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 ;
-- ----------------------------
-- create pkey
-- ----------------------------
alter table ep_temp_master.goods_receipts add CONSTRAINT  "goods_receipts_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.source_list add CONSTRAINT  "source_list_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.inforecord_history add CONSTRAINT  "inforecord_history_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.plm_actual_vendor add CONSTRAINT  "plm_actual_vendor_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.plm_subclass add CONSTRAINT  "plm_subclass_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.company add CONSTRAINT  "company_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.pur_org_data add CONSTRAINT  "pur_org_data_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_group add CONSTRAINT  "material_group_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.buyer_code add CONSTRAINT  "buyer_code_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.ship_instruct add CONSTRAINT  "ship_instruct_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.payment_term add CONSTRAINT  "payment_term_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.vendor_group add CONSTRAINT  "vendor_group_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.incoterm add CONSTRAINT  "incoterm_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.division_code add CONSTRAINT  "division_code_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.payment_info add CONSTRAINT  "payment_info_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_description add CONSTRAINT  "material_description_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_master add CONSTRAINT  "material_master_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_plant add CONSTRAINT  "material_plant_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_map add CONSTRAINT  "material_map_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_custmaster add CONSTRAINT  "material_custmaster_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.material_division add CONSTRAINT  "material_division_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.po_header add CONSTRAINT  "po_header_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.po_partner add CONSTRAINT  "po_partner_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.po_detail add CONSTRAINT  "po_detail_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.storage_location add CONSTRAINT  "storage_location_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.vendor add CONSTRAINT  "vendor_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.vendor_plant add CONSTRAINT  "vendor_plant_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.vendor_bank add CONSTRAINT  "vendor_bank_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.vendor_certified add CONSTRAINT  "vendor_certified_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.address add CONSTRAINT  "address_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.vs_webflow_iqc_data add CONSTRAINT  "vs_webflow_iqc_data_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.asn_maxqty add CONSTRAINT  "asn_maxqty_pkey" PRIMARY KEY ("id");

alter table ep_temp_master.asn_jitrule add CONSTRAINT  "asn_jitrule_pkey" PRIMARY KEY ("id");


-- ----------------------------
-- add pkey default
-- ----------------------------
ALTER TABLE ep_temp_master.goods_receipts ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.goods_receipts_id_seq'::regclass);

ALTER TABLE ep_temp_master.source_list ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.source_list_id_seq'::regclass);

ALTER TABLE ep_temp_master.inforecord_history ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.inforecord_history_id_seq'::regclass);

ALTER TABLE ep_temp_master.plm_actual_vendor ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.plm_actual_vendor_id_seq'::regclass);

ALTER TABLE ep_temp_master.plm_subclass ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.plm_subclass_id_seq'::regclass);

ALTER TABLE ep_temp_master.company ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.company_id_seq'::regclass);

ALTER TABLE ep_temp_master.pur_org_data ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.pur_org_data_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_group ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_group_id_seq'::regclass);

ALTER TABLE ep_temp_master.buyer_code ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.buyer_code_id_seq'::regclass);

ALTER TABLE ep_temp_master.ship_instruct ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.ship_instruct_id_seq'::regclass);

ALTER TABLE ep_temp_master.payment_term ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.payment_term_id_seq'::regclass);

ALTER TABLE ep_temp_master.vendor_group ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.vendor_group_id_seq'::regclass);

ALTER TABLE ep_temp_master.incoterm ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.incoterm_id_seq'::regclass);

ALTER TABLE ep_temp_master.division_code ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.division_code_id_seq'::regclass);

ALTER TABLE ep_temp_master.payment_info ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.payment_info_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_description ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_description_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_master ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_master_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_plant ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_plant_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_map ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_map_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_custmaster ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_custmaster_id_seq'::regclass);

ALTER TABLE ep_temp_master.material_division ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.material_division_id_seq'::regclass);

ALTER TABLE ep_temp_master.po_header ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.po_header_id_seq'::regclass);

ALTER TABLE ep_temp_master.po_partner ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.po_partner_id_seq'::regclass);

ALTER TABLE ep_temp_master.po_detail ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.po_detail_id_seq'::regclass);

ALTER TABLE ep_temp_master.storage_location ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.storage_location_id_seq'::regclass);

ALTER TABLE ep_temp_master.vendor ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.vendor_id_seq'::regclass);

ALTER TABLE ep_temp_master.vendor_plant ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.vendor_plant_id_seq'::regclass);

ALTER TABLE ep_temp_master.vendor_bank ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.vendor_bank_id_seq'::regclass);

ALTER TABLE ep_temp_master.vendor_certified ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.vendor_certified_id_seq'::regclass);

ALTER TABLE ep_temp_master.address ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.address_id_seq'::regclass);

ALTER TABLE ep_temp_master.vs_webflow_iqc_data ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.vs_webflow_iqc_data_id_seq'::regclass);

ALTER TABLE ep_temp_master.asn_maxqty ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.asn_maxqty_id_seq'::regclass);

ALTER TABLE ep_temp_master.asn_jitrule ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.asn_jitrule_id_seq'::regclass);

DROP SEQUENCE
IF EXISTS "ep_temp_master"."need_update_id_seq";

CREATE SEQUENCE "ep_temp_master"."need_update_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 ;

--------------------
---建立错误数据中间表
--------------------
DROP TABLE IF EXISTS "ep_temp_master"."goods_receipts_error";
DROP TABLE IF EXISTS "ep_temp_master"."source_list_error";
DROP TABLE IF EXISTS "ep_temp_master"."inforecord_history_error";
DROP TABLE IF EXISTS "ep_temp_master"."plm_actual_vendor_error";
DROP TABLE IF EXISTS "ep_temp_master"."plm_subclass_error";
DROP TABLE IF EXISTS "ep_temp_master"."company_error";
DROP TABLE IF EXISTS "ep_temp_master"."pur_org_data_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_group_error";
DROP TABLE IF EXISTS "ep_temp_master"."buyer_code_error";
DROP TABLE IF EXISTS "ep_temp_master"."ship_instruct_error";
DROP TABLE IF EXISTS "ep_temp_master"."payment_term_error";
DROP TABLE IF EXISTS "ep_temp_master"."vendor_group_error";
DROP TABLE IF EXISTS "ep_temp_master"."incoterm_error";
DROP TABLE IF EXISTS "ep_temp_master"."division_code_error";
DROP TABLE IF EXISTS "ep_temp_master"."country_error";
DROP TABLE IF EXISTS "ep_temp_master"."currency_error";
DROP TABLE IF EXISTS "ep_temp_master"."payment_info_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_description_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_master_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_plant_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_map_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_custmaster_error";
DROP TABLE IF EXISTS "ep_temp_master"."material_division_error";
DROP TABLE IF EXISTS "ep_temp_master"."po_header_error";
DROP TABLE IF EXISTS "ep_temp_master"."po_partner_error";
DROP TABLE IF EXISTS "ep_temp_master"."po_detail_error";
DROP TABLE IF EXISTS "ep_temp_master"."storage_location_error";
DROP TABLE IF EXISTS "ep_temp_master"."vendor_error";
DROP TABLE IF EXISTS "ep_temp_master"."vendor_plant_error";
DROP TABLE IF EXISTS "ep_temp_master"."vendor_bank_error";
DROP TABLE IF EXISTS "ep_temp_master"."vendor_certified_error";
DROP TABLE IF EXISTS "ep_temp_master"."address_error";
DROP TABLE IF EXISTS "ep_temp_master"."vs_webflow_iqc_data_error";
DROP TABLE IF EXISTS "ep_temp_master"."asn_maxqty_error";
DROP TABLE IF EXISTS "ep_temp_master"."asn_jitrule_error";
CREATE TABLE "ep_temp_master"."goods_receipts_error" as select * from "ep_temp_master"."goods_receipts" where 1=2;
CREATE TABLE "ep_temp_master"."source_list_error" as select * from "ep_temp_master"."source_list" where 1=2;
CREATE TABLE "ep_temp_master"."inforecord_history_error" as select * from "ep_temp_master"."inforecord_history" where 1=2;
CREATE TABLE "ep_temp_master"."plm_actual_vendor_error" as select * from "ep_temp_master"."plm_actual_vendor" where 1=2;
CREATE TABLE "ep_temp_master"."plm_subclass_error" as select * from "ep_temp_master"."plm_subclass" where 1=2;
CREATE TABLE "ep_temp_master"."company_error" as select * from "ep_temp_master"."company" where 1=2;
CREATE TABLE "ep_temp_master"."pur_org_data_error" as select * from "ep_temp_master"."pur_org_data" where 1=2;
CREATE TABLE "ep_temp_master"."material_group_error" as select * from "ep_temp_master"."material_group" where 1=2;
CREATE TABLE "ep_temp_master"."buyer_code_error" as select * from "ep_temp_master"."buyer_code" where 1=2;
CREATE TABLE "ep_temp_master"."ship_instruct_error" as select * from "ep_temp_master"."ship_instruct" where 1=2;
CREATE TABLE "ep_temp_master"."payment_term_error" as select * from "ep_temp_master"."payment_term" where 1=2;
CREATE TABLE "ep_temp_master"."vendor_group_error" as select * from "ep_temp_master"."vendor_group" where 1=2;
CREATE TABLE "ep_temp_master"."incoterm_error" as select * from "ep_temp_master"."incoterm" where 1=2;
CREATE TABLE "ep_temp_master"."division_code_error" as select * from "ep_temp_master"."division_code" where 1=2;
CREATE TABLE "ep_temp_master"."payment_info_error" as select * from "ep_temp_master"."payment_info" where 1=2;
CREATE TABLE "ep_temp_master"."material_description_error" as select * from "ep_temp_master"."material_description" where 1=2;
CREATE TABLE "ep_temp_master"."material_master_error" as select * from "ep_temp_master"."material_master" where 1=2;
CREATE TABLE "ep_temp_master"."material_plant_error" as select * from "ep_temp_master"."material_plant" where 1=2;
CREATE TABLE "ep_temp_master"."material_map_error" as select * from "ep_temp_master"."material_map" where 1=2;
CREATE TABLE "ep_temp_master"."material_custmaster_error" as select * from "ep_temp_master"."material_custmaster" where 1=2;
CREATE TABLE "ep_temp_master"."material_division_error" as select * from "ep_temp_master"."material_division" where 1=2;
CREATE TABLE "ep_temp_master"."po_header_error" as select * from "ep_temp_master"."po_header" where 1=2;
CREATE TABLE "ep_temp_master"."po_partner_error" as select * from "ep_temp_master"."po_partner" where 1=2;
CREATE TABLE "ep_temp_master"."po_detail_error" as select * from "ep_temp_master"."po_detail" where 1=2;
CREATE TABLE "ep_temp_master"."storage_location_error" as select * from "ep_temp_master"."storage_location" where 1=2;
CREATE TABLE "ep_temp_master"."vendor_error" as select * from "ep_temp_master"."vendor" where 1=2;
CREATE TABLE "ep_temp_master"."vendor_plant_error" as select * from "ep_temp_master"."vendor_plant" where 1=2;
CREATE TABLE "ep_temp_master"."vendor_bank_error" as select * from "ep_temp_master"."vendor_bank" where 1=2;
CREATE TABLE "ep_temp_master"."vendor_certified_error" as select * from "ep_temp_master"."vendor_certified" where 1=2;
CREATE TABLE "ep_temp_master"."address_error" as select * from "ep_temp_master"."address" where 1=2;
CREATE TABLE "ep_temp_master"."vs_webflow_iqc_data_error" as select * from "ep_temp_master"."vs_webflow_iqc_data" where 1=2;
CREATE TABLE "ep_temp_master"."asn_maxqty_error" as select * from "ep_temp_master"."asn_maxqty" where 1=2;
CREATE TABLE "ep_temp_master"."asn_jitrule_error" as select * from "ep_temp_master"."asn_jitrule" where 1=2;

alter table ep_temp_master.goods_receipts_error add CONSTRAINT  "goods_receipts_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.source_list_error add CONSTRAINT  "source_list_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.inforecord_history_error add CONSTRAINT  "inforecord_history_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.plm_actual_vendor_error add CONSTRAINT  "plm_actual_vendor_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.plm_subclass_error add CONSTRAINT  "plm_subclass_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.company_error add CONSTRAINT  "company_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.pur_org_data_error add CONSTRAINT  "pur_org_data_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_group_error add CONSTRAINT  "material_group_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.buyer_code_error add CONSTRAINT  "buyer_code_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.ship_instruct_error add CONSTRAINT  "ship_instruct_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.payment_term_error add CONSTRAINT  "payment_term_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.vendor_group_error add CONSTRAINT  "vendor_group_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.incoterm_error add CONSTRAINT  "incoterm_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.division_code_error add CONSTRAINT  "division_code_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.payment_info_error add CONSTRAINT  "payment_info_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_description_error add CONSTRAINT  "material_description_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_master_error add CONSTRAINT  "material_master_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_plant_error add CONSTRAINT  "material_plant_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_map_error add CONSTRAINT  "material_map_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_custmaster_error add CONSTRAINT  "material_custmaster_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.material_division_error add CONSTRAINT  "material_division_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.po_header_error add CONSTRAINT  "po_header_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.po_partner_error add CONSTRAINT  "po_partner_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.po_detail_error add CONSTRAINT  "po_detail_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.storage_location_error add CONSTRAINT  "storage_location_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.vendor_error add CONSTRAINT  "vendor_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.vendor_plant_error add CONSTRAINT  "vendor_plant_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.vendor_bank_error add CONSTRAINT  "vendor_bank_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.vendor_certified_error add CONSTRAINT  "vendor_certified_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.address_error add CONSTRAINT  "address_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.vs_webflow_iqc_data_error add CONSTRAINT  "vs_webflow_iqc_data_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.asn_maxqty_error add CONSTRAINT  "asn_maxqty_error_pkey" PRIMARY KEY ("id");
alter table ep_temp_master.asn_jitrule_error add CONSTRAINT  "asn_jitrule_error_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Insert config data
-- ----------------------------
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('ASN','ASNMaxQTY');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('ASNJIT','ASNJITRule');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('GR','GoodsReceipts');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('INFO','SourceList');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('INFO','InforecordHistory');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER_PLM','PLMActualVendor');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER_PLM','PLMSubClass');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','Company');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','PurOrgData');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','MaterialGroup');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','BuyerCode');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','ShipInstruct');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','PaymentTerm');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','VendorGroup');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','IncoTerm');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','DivisionCode');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('MASTER','PaymentInfo');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PART','MaterialDescription');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PART','MaterialMaster');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PART','MaterialPlant');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PART','MaterialMAP');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PART','MaterialCustMaster');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PART','MaterialDivision');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PO','POHeader');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PO','POPartner');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PO','PODetail');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('PO','StorageLocation');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('VENDOR','Vendor');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('VENDOR','VendorPlant');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('VENDOR','VendorBank');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('VENDOR','VendorCertified');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('VENDOR','Address');
insert into ep_temp_master.extractgroup(extractgroup,extractname) values('IQCDATA','VS_WEBFLOW_IQC_DATA');

insert into ExtractGroup
VALUES
('TRANS_PO','iac_purchase_order'),
('TRANS_PO','iac_purchase_order_line'),
('TRANS_PO','iac_purchase_order_history'),
('TRANS_PO','iac_purchase_order_line_history'),
('TRANS_PO_UNCONFIRM','iac_purchase_order_unconfirm_summary'),
('TRANS_PO_UNCONFIRM','iac_purchase_order_unconfirm_detail'),
('TRANS_ASN','iac_asn'),
('TRANS_ASN','iac_asn_line'),
('TRANS_RFQ','iac_rfq');

DROP TABLE IF EXISTS "ep_temp_master"."restful_log";
create table "ep_temp_master"."restful_log"
(
  id                varchar,
  int_no            varchar,
  external_key      varchar,
  input_value       text,
  output_value      text,
  status           varchar,
  message           varchar,
  creation_date     varchar,
  last_update_date  varchar,
  seqno             int4
);

-- ----------------------------
-- add sap log table
-- ----------------------------

CREATE SEQUENCE "ep_temp_master"."restful_log_seqno_seq"
 INCREMENT 1
 MINVALUE 1
 MAXVALUE 9223372036854775807
 START 183
 CACHE 1
 OWNED BY "ep_temp_master"."restful_log"."seqno";


ALTER TABLE ep_temp_master.restful_log ALTER COLUMN seqno SET DEFAULT nextval('ep_temp_master.restful_log_seqno_seq'::regclass);


-- ----------------------------
-- add fun_def table
-- ----------------------------
CREATE TABLE "ep_temp_master"."lwt_fun_def" (
"fun_name" varchar COLLATE "default",
"fun_def" text COLLATE "default"
)
WITH (OIDS=FALSE)
;



alter table	public.	goods_receipts	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	source_list	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	inforecord_history	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	plm_actual_vendor	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	plm_subclass	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	company	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	pur_org_data	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_group	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	buyer_code	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	ship_instruct	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	payment_term	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	vendor_group	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	incoterm	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	division_code	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	payment_info	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_description	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_master	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_plant	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_map	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_custmaster	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	material_division	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	iac_purchase_order	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	iac_purchase_order_partner	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	iac_purchase_order_line	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	storage_location	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	vendor	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	vendor_plant	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	vendor_bank	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	vendor_certified	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	address	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	vs_webflow_iqc_data	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	asn_maxqty	ALTER COLUMN need_re_update SET DEFAULT 0;
alter table	public.	asn_jitrule	ALTER COLUMN need_re_update SET DEFAULT 0;

update	public.	goods_receipts	set need_re_update =0 where need_re_update is null;
update	public.	source_list	set need_re_update =0 where need_re_update is null;
update	public.	inforecord_history	set need_re_update =0 where need_re_update is null;
update	public.	plm_actual_vendor	set need_re_update =0 where need_re_update is null;
update	public.	plm_subclass	set need_re_update =0 where need_re_update is null;
update	public.	company	set need_re_update =0 where need_re_update is null;
update	public.	pur_org_data	set need_re_update =0 where need_re_update is null;
update	public.	material_group	set need_re_update =0 where need_re_update is null;
update	public.	buyer_code	set need_re_update =0 where need_re_update is null;
update	public.	ship_instruct	set need_re_update =0 where need_re_update is null;
update	public.	payment_term	set need_re_update =0 where need_re_update is null;
update	public.	vendor_group	set need_re_update =0 where need_re_update is null;
update	public.	incoterm	set need_re_update =0 where need_re_update is null;
update	public.	division_code	set need_re_update =0 where need_re_update is null;
update	public.	payment_info	set need_re_update =0 where need_re_update is null;
update	public.	material_description	set need_re_update =0 where need_re_update is null;
update	public.	material_master	set need_re_update =0 where need_re_update is null;
update	public.	material_plant	set need_re_update =0 where need_re_update is null;
update	public.	material_map	set need_re_update =0 where need_re_update is null;
update	public.	material_custmaster	set need_re_update =0 where need_re_update is null;
update	public.	material_division	set need_re_update =0 where need_re_update is null;
update	public.	iac_purchase_order	set need_re_update =0 where need_re_update is null;
update	public.	iac_purchase_order_partner	set need_re_update =0 where need_re_update is null;
update	public.	iac_purchase_order_line	set need_re_update =0 where need_re_update is null;
update	public.	storage_location	set need_re_update =0 where need_re_update is null;
update	public.	vendor	set need_re_update =0 where need_re_update is null;
update	public.	vendor_plant	set need_re_update =0 where need_re_update is null;
update	public.	vendor_bank	set need_re_update =0 where need_re_update is null;
update	public.	vendor_certified	set need_re_update =0 where need_re_update is null;
update	public.	address	set need_re_update =0 where need_re_update is null;
update	public.	vs_webflow_iqc_data	set need_re_update =0 where need_re_update is null;
update	public.	asn_maxqty	set need_re_update =0 where need_re_update is null;
update	public.	asn_jitrule	set need_re_update =0 where need_re_update is null;


--------------------------------
--测试日志表
--------------------------------
DROP TABLE
IF EXISTS "ep_temp_master"."lwt_log";

CREATE TABLE "ep_temp_master"."lwt_log" (
	"id" int4,
	"create_uid" int4,
	"log_text" TEXT COLLATE "default",
	"write_date" TIMESTAMP (6),
	"create_date" TIMESTAMP (6)
) WITH (OIDS = FALSE);

DROP SEQUENCE
IF EXISTS "ep_temp_master"."lwt_log_id_seq";

CREATE SEQUENCE "ep_temp_master"."lwt_log_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."lwt_log"."id";

ALTER TABLE ep_temp_master.lwt_log ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.lwt_log_id_seq'::regclass);



DROP TABLE IF EXISTS "public"."iac_job_func_call_log";
CREATE TABLE "public"."iac_job_func_call_log" (
"id" int4 ,
"group_id" int4,
"group_line_id" int4,
"group_name" varchar,
"group_line_name" varchar,
"fun_call_text" text,
"sap_log_id" varchar
)
WITH (OIDS=FALSE)
;

CREATE SEQUENCE "public"."iac_job_func_call_log_id_seq" INCREMENT 1 MINVALUE 1  MAXVALUE 9223372036854775807 START 1  CACHE 1  OWNED BY "public"."iac_job_func_call_log"."id";

alter table public.iac_job_func_call_log add CONSTRAINT  "iac_job_func_call_log_pkey" PRIMARY KEY ("id");

ALTER TABLE public.iac_job_func_call_log ALTER COLUMN id SET DEFAULT nextval('public.iac_job_func_call_log_id_seq'::regclass);

CREATE INDEX "iac_purchase_order_document_erp_id_index" ON "ep_temp_master"."iac_purchase_order" USING btree (document_erp_id);
CREATE INDEX "iac_purchase_order_history_document_erp_id_index" ON "ep_temp_master"."iac_purchase_order_history" USING btree (document_erp_id);

CREATE INDEX "iac_purchase_order_line_document_erp_id_index" ON "ep_temp_master"."iac_purchase_order_line" USING btree (document_erp_id);
CREATE INDEX "iac_purchase_order_line_history_document_erp_id_index" ON "ep_temp_master"."iac_purchase_order_line_history" USING btree (document_erp_id);


CREATE INDEX "iac_purchase_order_line_document_line_erp_id_index" ON "ep_temp_master"."iac_purchase_order_line" USING btree (document_line_erp_id);
CREATE INDEX "iac_purchase_order_line_history_document_line_erp_id_index" ON "ep_temp_master"."iac_purchase_order_line_history" USING btree (document_line_erp_id);

CREATE INDEX "iac_asn_line_asn_no_index" ON "ep_temp_master"."iac_asn_line" USING btree (asn_no);

CREATE INDEX "iac_asn_asn_no_index" ON "ep_temp_master"."iac_asn" USING btree (asn_no);

alter table "public".iac_asn_line add miss_flag integer;