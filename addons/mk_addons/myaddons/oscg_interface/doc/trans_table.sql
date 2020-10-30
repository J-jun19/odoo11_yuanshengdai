DROP TABLE IF EXISTS "ep_temp_master"."iac_asn";
CREATE TABLE "ep_temp_master"."iac_asn" (
"id" int4 ,
"airbill_no" varchar COLLATE "default",
"asn_date" date,
"asn_no" varchar COLLATE "default",
"asn_status" varchar COLLATE "default",
"buyer_code" varchar COLLATE "default",
"company_code" varchar COLLATE "default",
"create_date" timestamp(6),
"create_mode" varchar COLLATE "default",
"delivery_days" int4,
"eta_date" date,
"etd_date" date,
"from_source" varchar COLLATE "default",
"gross_weight" float8,
"has_attachment" varchar COLLATE "default",
"housebill_no" varchar COLLATE "default",
"net_weight" float8,
"packing_list_no" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"pull_signal_id" varchar COLLATE "default",
"sap_key" varchar COLLATE "default",
"ship_from" varchar COLLATE "default",
"ship_from_country" varchar COLLATE "default",
"ship_to" varchar COLLATE "default",
"shipping_days" int4,
"source_id" int4,
"standard_carrier" varchar COLLATE "default",
"state" varchar COLLATE "default",
"storage_location" varchar COLLATE "default",
"total_cartons" float8,
"transport_id" int4,
"transport_type" varchar COLLATE "default",
"type" varchar COLLATE "default",
"vendor_asn" varchar COLLATE "default",
"vendor_code_sap" varchar COLLATE "default",
"write_date" timestamp(6),
"sap_log_id" varchar COLLATE "default",
"buy_sell_asn_id" int4,
"customer_country" int4,
"customer_currency" int4,
"plant_id" int4,
"vendor_id" int4,
"vmi_asn_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"customer_country_name" varchar COLLATE "default",
"customer_currency_name" varchar COLLATE "default",
CONSTRAINT "iac_asn_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;


DROP TABLE IF EXISTS "ep_temp_master"."iac_asn_line";
CREATE TABLE "ep_temp_master"."iac_asn_line" (
"id" int4 DEFAULT nextval('"ep_temp_master".iac_asn_line_id_seq'::regclass) NOT NULL,
"amount" float8,
"asn_line_no" int4,
"asn_qty" numeric,
"buyer_erp_id" varchar,
"create_date" timestamp(6),
"gross_weight" float8,
"invoice_no" varchar,
"net_weight" float8,
"origin_country" int4,
"packing_note" varchar,
"plant_code" varchar,
"po_code" varchar,
"po_line_code" varchar,
"qty_per_carton" int4,
"rpc_note" text,
"sap_key" varchar,
"storage_location" varchar,
"vendor_asn" varchar,
"vendor_asn_item" varchar,
"vendor_code_sap" varchar,
"write_date" timestamp(6),
"sap_log_id" varchar,
"asn_id" int4,
"buy_sell_asn_id" int4,
"buy_sell_asn_line_id" int4,
"buyer_id" int4,
"part_id" int4,
"plant_id" int4,
"po_id" int4,
"po_line_id" int4,
"vendor_id" int4,
"vmi_asn_id" int4,
"vmi_asn_line_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"asn_no" varchar,
"part_no" varchar,
"part_desc" varchar,
"document_line_erp_id" varchar,
CONSTRAINT "iac_asn_line_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;



DROP TABLE IF EXISTS "ep_temp_master"."iac_purchase_order";
CREATE TABLE "ep_temp_master"."iac_purchase_order" (
"id" int4 ,
"buspartno" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"changed" bool,
"changed_terms" varchar COLLATE "default",
"changed_text" varchar COLLATE "default",
"company_code" varchar COLLATE "default",
"contact_fax" varchar COLLATE "default",
"contact_name" varchar COLLATE "default",
"contact_person" varchar COLLATE "default",
"contact_phone" varchar COLLATE "default",
"create_date" timestamp(6),
"created_by" varchar COLLATE "default",
"currency" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"document_erp_id" varchar COLLATE "default",
"dropship_flag" bool,
"dropship_no" varchar COLLATE "default",
"exchange_rate" varchar COLLATE "default",
"incoterm" varchar COLLATE "default",
"incoterm1" varchar COLLATE "default",
"incoterm2" varchar COLLATE "default",
"language_key" varchar COLLATE "default",
"manually_po_comment" text COLLATE "default",
"manually_po_comment2" text COLLATE "default",
"manually_po_reason" text COLLATE "default",
"manually_po_reason_type" varchar COLLATE "default",
"manually_po_type" text COLLATE "default",
"name" varchar COLLATE "default",
"note" text COLLATE "default",
"odoo_deletion_flag" bool,
"order_category" varchar COLLATE "default",
"order_date" date,
"order_release_status" varchar COLLATE "default",
"order_type" varchar COLLATE "default",
"our_reference" varchar COLLATE "default",
"payment_term" varchar COLLATE "default",
"pricecontrol" varchar COLLATE "default",
"purchase_org" varchar COLLATE "default",
"sap_key" varchar COLLATE "default",
"ship_addr" varchar COLLATE "default",
"ship_code" varchar COLLATE "default",
"state" varchar COLLATE "default",
"status" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"version_no" varchar COLLATE "default",
"warehouse" varchar COLLATE "default",
"write_date" timestamp(6),
"your_reference" varchar COLLATE "default",
"sap_log_id" varchar COLLATE "default",
"address_odoo_id" int4,
"attachment" int4,
"buyer_id" int4,
"change_id" int4,
"company_id" int4,
"currency_id" int4,
"history_order_id" int4,
"incoterm_id" int4,
"last_change_id" int4,
"payment_term_id" int4,
"plant_id" int4,
"price_his_id" int4,
"purchase_org_id" int4,
"vendor_id" int4,
"vendor_reg_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
CONSTRAINT "iac_purchase_order_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;



DROP TABLE IF EXISTS "ep_temp_master"."iac_purchase_order_line";
CREATE TABLE "ep_temp_master"."iac_purchase_order_line" (
"id" int4,
"address" varchar COLLATE "default",
"address_detail" varchar COLLATE "default",
"address_id" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"change_date" varchar COLLATE "default",
"create_date" timestamp(6),
"deletion_flag" varchar COLLATE "default",
"delivery_complete" varchar COLLATE "default",
"delivery_date" date,
"document_erp_id" varchar COLLATE "default",
"document_line_erp_id" varchar COLLATE "default",
"line_text" varchar COLLATE "default",
"manufacturer_part_no" varchar COLLATE "default",
"material_uom" varchar COLLATE "default",
"name" varchar COLLATE "default",
"net_order_price" varchar COLLATE "default",
"order_reason" text COLLATE "default",
"part_no" varchar COLLATE "default",
"part_no1" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"price" float8,
"price_date" date,
"price_unit" int4,
"purchase_req_item_no" varchar COLLATE "default",
"purchase_req_no" varchar COLLATE "default",
"quantity" float8,
"reject_flag" varchar COLLATE "default",
"rejection_indicator" bool,
"remain" int4,
"revision_level" varchar COLLATE "default",
"rfq_no" varchar COLLATE "default",
"rfq_start_date" date,
"rfq_status" varchar COLLATE "default",
"sap_key" varchar COLLATE "default",
"shipping" int4,
"short_text" varchar COLLATE "default",
"state" varchar COLLATE "default",
"state_msg" varchar COLLATE "default",
"storage_location" varchar COLLATE "default",
"tax_code" varchar COLLATE "default",
"tracking_number" varchar COLLATE "default",
"unit" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"vendor_delivery_date" date,
"vendor_exception_reason" text COLLATE "default",
"vendor_part_no" varchar COLLATE "default",
"vendor_to_be_supply" varchar COLLATE "default",
"write_date" timestamp(6),
"sap_log_id" varchar COLLATE "default",
"address_odoo_id" int4,
"buyer_id" int4,
"currency_id" int4,
"last_order_line_change_id" int4,
"order_id" int4,
"part_id" int4,
"plant_id" int4,
"price_his_id" int4,
"ref_line_id" int4,
"rfq_id" int4,
"vendor_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"currency_id" int4,
CONSTRAINT "iac_purchase_order_line_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;



DROP TABLE IF EXISTS "ep_temp_master"."iac_purchase_order_history";
CREATE TABLE "ep_temp_master"."iac_purchase_order_history" (
"id" int4,
"buspartno" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"changed" bool,
"changed_terms" varchar COLLATE "default",
"changed_text" varchar COLLATE "default",
"company_code" varchar COLLATE "default",
"contact_fax" varchar COLLATE "default",
"contact_name" varchar COLLATE "default",
"contact_person" varchar COLLATE "default",
"contact_phone" varchar COLLATE "default",
"create_date" timestamp(6),
"created_by" varchar COLLATE "default",
"currency" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"document_erp_id" varchar COLLATE "default",
"dropship_flag" bool,
"dropship_no" varchar COLLATE "default",
"exchange_rate" varchar COLLATE "default",
"incoterm" varchar COLLATE "default",
"incoterm1" varchar COLLATE "default",
"incoterm2" varchar COLLATE "default",
"language_key" varchar COLLATE "default",
"manually_po_comment" text COLLATE "default",
"manually_po_comment2" text COLLATE "default",
"manually_po_reason" text COLLATE "default",
"manually_po_reason_type" varchar COLLATE "default",
"manually_po_type" text COLLATE "default",
"name" varchar COLLATE "default",
"note" text COLLATE "default",
"odoo_deletion_flag" bool,
"order_category" varchar COLLATE "default",
"order_date" date,
"order_release_status" varchar COLLATE "default",
"order_type" varchar COLLATE "default",
"our_reference" varchar COLLATE "default",
"payment_term" varchar COLLATE "default",
"pricecontrol" varchar COLLATE "default",
"purchase_org" varchar COLLATE "default",
"sap_key" varchar COLLATE "default",
"ship_addr" varchar COLLATE "default",
"ship_code" varchar COLLATE "default",
"state" varchar COLLATE "default",
"status" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"version_no" varchar COLLATE "default",
"warehouse" varchar COLLATE "default",
"write_date" timestamp(6),
"your_reference" varchar COLLATE "default",
"sap_log_id" varchar COLLATE "default",
"address_odoo_id" int4,
"attachment" int4,
"buyer_id" int4,
"change_id" int4,
"company_id" int4,
"currency_id" int4,
"history_order_id" int4,
"incoterm_id" int4,
"last_change_id" int4,
"payment_term_id" int4,
"plant_id" int4,
"price_his_id" int4,
"purchase_org_id" int4,
"vendor_id" int4,
"vendor_reg_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"order_id" int4,
CONSTRAINT "iac_purchase_order_history_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;





DROP TABLE IF EXISTS "ep_temp_master"."iac_purchase_order_line_history";
CREATE TABLE "ep_temp_master"."iac_purchase_order_line_history" (
"id" int4 ,
"address" varchar COLLATE "default",
"address_detail" varchar COLLATE "default",
"address_id" varchar COLLATE "default",
"buyer_erp_id" varchar COLLATE "default",
"change_date" varchar COLLATE "default",
"create_date" timestamp(6),
"deletion_flag" varchar COLLATE "default",
"delivery_complete" varchar COLLATE "default",
"delivery_date" date,
"document_erp_id" varchar COLLATE "default",
"document_line_erp_id" varchar COLLATE "default",
"line_text" varchar COLLATE "default",
"manufacturer_part_no" varchar COLLATE "default",
"material_uom" varchar COLLATE "default",
"name" varchar COLLATE "default",
"net_order_price" varchar COLLATE "default",
"order_reason" text COLLATE "default",
"part_no" varchar COLLATE "default",
"part_no1" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"price" float8,
"price_date" date,
"price_unit" int4,
"purchase_req_item_no" varchar COLLATE "default",
"purchase_req_no" varchar COLLATE "default",
"quantity" float8,
"reject_flag" varchar COLLATE "default",
"rejection_indicator" bool,
"remain" int4,
"revision_level" varchar COLLATE "default",
"rfq_no" varchar COLLATE "default",
"rfq_start_date" date,
"rfq_status" varchar COLLATE "default",
"sap_key" varchar COLLATE "default",
"shipping" int4,
"short_text" varchar COLLATE "default",
"state" varchar COLLATE "default",
"state_msg" varchar COLLATE "default",
"storage_location" varchar COLLATE "default",
"tax_code" varchar COLLATE "default",
"tracking_number" varchar COLLATE "default",
"unit" varchar COLLATE "default",
"vendor_code" varchar COLLATE "default",
"vendor_delivery_date" date,
"vendor_exception_reason" text COLLATE "default",
"vendor_part_no" varchar COLLATE "default",
"vendor_to_be_supply" varchar COLLATE "default",
"write_date" timestamp(6),
"sap_log_id" varchar COLLATE "default",
"address_odoo_id" int4,
"buyer_id" int4,
"currency_id" int4,
"last_order_line_change_id" int4,
"order_id" int4,
"part_id" int4,
"plant_id" int4,
"price_his_id" int4,
"ref_line_id" int4,
"vendor_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"his_order_id" int4,
"currency_id" int4,
CONSTRAINT "iac_purchase_order_line_history_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;




DROP TABLE IF EXISTS "ep_temp_master"."iac_purchase_order_unconfirm_detail";
CREATE TABLE "ep_temp_master"."iac_purchase_order_unconfirm_detail" (
"id" int4,
"buyer_erp_id" varchar COLLATE "default",
"change_date" date,
"currency" varchar COLLATE "default",
"deletion_flag" varchar COLLATE "default",
"description" varchar COLLATE "default",
"diff" numeric,
"division_code" varchar COLLATE "default",
"document_line_no" varchar COLLATE "default",
"document_no" varchar COLLATE "default",
"flag" varchar COLLATE "default",
"last_update_date" date,
"orig_total_qty" numeric,
"part_no" varchar COLLATE "default",
"plant_id" varchar COLLATE "default",
"price" numeric,
"priceunit" numeric,
"sap_key" varchar COLLATE "default",
"source_code" varchar COLLATE "default",
"total_qty" numeric,
"vendor_erp_id" varchar COLLATE "default",
"vendor_name" varchar COLLATE "default",
"sap_log_id" varchar COLLATE "default",
"buyer_id" int4,
"currency_id" int4,
"division_id" int4,
"odoo_plant_id" int4,
"order_id" int4,
"order_line_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"part_id" int4,
CONSTRAINT "iac_purchase_order_unconfirm_detail_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;


DROP TABLE IF EXISTS "ep_temp_master"."iac_purchase_order_unconfirm_summary";
CREATE TABLE "ep_temp_master"."iac_purchase_order_unconfirm_summary" (
"id" int4 ,
"buyer_erp_id" varchar COLLATE "default",
"currency" varchar COLLATE "default",
"description" varchar COLLATE "default",
"division_code" varchar COLLATE "default",
"document_line_no" varchar COLLATE "default",
"document_no" varchar COLLATE "default",
"last_update_date" date,
"part_no" varchar COLLATE "default",
"plant_id" varchar COLLATE "default",
"price" numeric,
"price_unit" numeric,
"sap_key" varchar COLLATE "default",
"source_code" varchar COLLATE "default",
"unconqtyd" numeric,
"unconqtyr" numeric,
"vendor_erp_id" varchar COLLATE "default",
"vendor_name" varchar COLLATE "default",
"sap_log_id" varchar COLLATE "default",
"buyer_id" int4,
"currency_id" int4,
"division_id" int4,
"odoo_plant_id" int4,
"order_id" int4,
"order_line_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
CONSTRAINT "iac_purchase_order_unconfirm_summary_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;



DROP TABLE IF EXISTS "ep_temp_master"."iac_rfq";
CREATE TABLE "ep_temp_master"."iac_rfq" (
"id" int4 ,
"buyer_code_sap" varchar COLLATE "default",
"country_code" varchar COLLATE "default",
"create_date" timestamp(6),
"currency_name" varchar COLLATE "default",
"cw" varchar COLLATE "default",
"division_code" varchar COLLATE "default",
"incoterm" varchar COLLATE "default",
"incoterm2" varchar COLLATE "default",
"input_price" numeric,
"last_rfq_no" varchar COLLATE "default",
"line_text" varchar COLLATE "default",
"lt" int4,
"manufacturer_part_no" varchar COLLATE "default",
"moq" int4,
"mpq" int4,
"name" varchar COLLATE "default",
"note" text COLLATE "default",
"order_reason" varchar COLLATE "default",
"part_code" varchar COLLATE "default",
"payment_term" varchar COLLATE "default",
"plant_code" varchar COLLATE "default",
"price_control" varchar COLLATE "default",
"price_unit" float8,
"purchase_org" varchar COLLATE "default",
"reason_code_text" varchar COLLATE "default",
"release_flag" varchar COLLATE "default",
"rw" varchar COLLATE "default",
"sap_key" varchar COLLATE "default",
"state" varchar COLLATE "default",
"supplier_company_no" varchar COLLATE "default",
"tax" varchar COLLATE "default",
"text" text COLLATE "default",
"type" varchar COLLATE "default",
"unit_price" float8,
"uom" int4,
"valid_from" date,
"valid_to" date,
"vendor_code" varchar COLLATE "default",
"vendor_part_no" varchar COLLATE "default",
"write_date" timestamp(6),
"sap_log_id" varchar COLLATE "default",
"buyer_code" int4,
"company_id" int4,
"currency" int4,
"currency_id" int4,
"division_id" int4,
"group_id" int4,
"last_rfq_id" int4,
"no_down_reason_id" int4,
"part_id" int4,
"plant_id" int4,
"reason_code" int4,
"supplier_id" int4,
"user_id" int4,
"vendor_id" int4,
"miss_flag" int4 DEFAULT 0,
"trans_prod_flag" int4 DEFAULT 0,
"ex_flag" int4 DEFAULT 0,
"source_code" varchar COLLATE "default",
"new_type" varchar COLLATE "default",
CONSTRAINT "iac_rfq_pk_id" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;



CREATE SEQUENCE "ep_temp_master"."iac_purchase_order_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_purchase_order"."id";

ALTER TABLE ep_temp_master.iac_purchase_order ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_purchase_order_id_seq'::regclass);

CREATE SEQUENCE "ep_temp_master"."iac_purchase_order_line_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_purchase_order_line"."id";

ALTER TABLE ep_temp_master.iac_purchase_order_line ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_purchase_order_line_id_seq'::regclass);

CREATE SEQUENCE "ep_temp_master"."iac_purchase_order_history_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_purchase_order_history"."id";

ALTER TABLE ep_temp_master.iac_purchase_order_history ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_purchase_order_history_id_seq'::regclass);


CREATE SEQUENCE "ep_temp_master"."iac_purchase_order_line_history_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_purchase_order_line_history"."id";

ALTER TABLE ep_temp_master.iac_purchase_order_line_history ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_purchase_order_line_history_id_seq'::regclass);

CREATE SEQUENCE "ep_temp_master"."iac_purchase_order_unconfirm_summary_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_purchase_order_unconfirm_summary"."id";

ALTER TABLE ep_temp_master.iac_purchase_order_unconfirm_summary ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_purchase_order_unconfirm_summary_id_seq'::regclass);
CREATE SEQUENCE "ep_temp_master"."iac_purchase_order_unconfirm_detail_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_purchase_order_unconfirm_detail"."id";

ALTER TABLE ep_temp_master.iac_purchase_order_unconfirm_detail ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_purchase_order_unconfirm_detail_id_seq'::regclass);
CREATE SEQUENCE "ep_temp_master"."iac_asn_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_asn"."id";

ALTER TABLE ep_temp_master.iac_asn ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_asn_id_seq'::regclass);
CREATE SEQUENCE "ep_temp_master"."iac_asn_line_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_asn_line"."id";

ALTER TABLE ep_temp_master.iac_asn_line ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_asn_line_id_seq'::regclass);
CREATE SEQUENCE "ep_temp_master"."iac_rfq_id_seq" INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 OWNED BY "ep_temp_master"."iac_rfq"."id";

ALTER TABLE ep_temp_master.iac_rfq ALTER COLUMN id SET DEFAULT nextval('ep_temp_master.iac_rfq_id_seq'::regclass);




alter table	ep_temp_master.	iac_purchase_order	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_line	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_history	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_line_history	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_unconfirm_summary	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_unconfirm_detail	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_asn	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_asn_line	alter column	miss_flag	set default	0;
alter table	ep_temp_master.	iac_rfq	alter column	miss_flag	set default	0;

alter table	ep_temp_master.	iac_purchase_order	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_line	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_history	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_line_history	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_unconfirm_summary	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_unconfirm_detail	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_asn	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_asn_line	alter column	ex_flag	set default	0;
alter table	ep_temp_master.	iac_rfq	alter column	ex_flag	set default	0;


alter table	ep_temp_master.	iac_purchase_order	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_line	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_history	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_line_history	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_unconfirm_summary	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_purchase_order_unconfirm_detail	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_asn	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_asn_line	alter column	trans_prod_flag	set default	0;
alter table	ep_temp_master.	iac_rfq	alter column	trans_prod_flag	set default	0;
