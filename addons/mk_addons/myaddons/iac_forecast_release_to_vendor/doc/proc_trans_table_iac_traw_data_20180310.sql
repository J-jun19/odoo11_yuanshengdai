-- FUNCTION: ep_temp_master.proc_trans_table_iac_tjob_status(character varying, integer, integer, integer, integer)

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status(character varying, integer, integer, integer, integer);
/*

執行 FUNCTION語句
SELECT
	*
FROM
	ep_temp_master.proc_trans_table_iac_traw_data (
		'MaterialMaster2018-03-10 11:25:06.082000000',
		1000,
		1000
	) AS (
		v_last_id int4,
		v_log_line_id int4,
		v_group_id int4,
		v_group_line_id int4,
		v_group_name VARCHAR,
		v_group_line_name VARCHAR,
		v_update_count int4,
		v_fail_count int4,
		v_miss_count int4
	)

	
	
--先找到 public.iac_tjob_status的 need_update_id 須更新的值, 再改參數 
SELECT ep_temp_master.proc_trans_table_iac_tjob_status_ref('test4',need_update_id,561,561,1000,0) ; 

*/

/*
--參考code
SELECT
	*
FROM
	ep_temp_master.sp_job_part_material_master_insert (
		'MaterialMaster2018-03-06 18:44:06.082000000',
		1000,
		1000
	) AS (
		v_last_id int4,
		v_log_line_id int4,
		v_group_id int4,
		v_group_line_id int4,
		v_group_name VARCHAR,
		v_group_line_name VARCHAR,
		v_update_count int4,
		v_fail_count int4,
		v_miss_count int4
	)
	*/

CREATE OR REPLACE FUNCTION "ep_temp_master"."proc_trans_table_iac_traw_data"
(v_sap_log_id varchar, v_limit int4, v_start_id int4)
  RETURNS SETOF "pg_catalog"."record" AS $BODY$        
                                                                                                                    
                                                                                                                                                                
declare                                                                                                                                                         
v_rc	record;                                                                                                                                                                                                                                                                                      
v_count	integer;                                                                                                                                             
                                                                                                                                                                
--异常捕?信息                                                                                                                                                  
v_table_name varchar;                                                                                                                                           
v_column_name varchar;                                                                                                                                          
v_message_text text;                                                                                                                                            
v_exception_detail text;                                                                                                                                                                                                                                                                                      
                                                                                                                                                                
v_update_count integer;
v_fail_count integer; 
v_miss_count integer;
v_order_line_id integer;

v_last_id    integer;
v_break_id integer;
v_group_name  varchar;
v_group_line_name varchar;
v_group_id   integer;
v_group_line_id integer;
v_log_id     integer;
v_log_line_id integer;                                                                                                                                 
begin                                                                                                                                                           


                                                                                                                                                                
v_update_count:=0;
v_fail_count:=0;
v_miss_count:=0;
v_last_id:=0;
v_group_name:='FORECAST';
v_group_line_name:='IAC_TRAW';
v_table_name:='iac_traw_data';
select id into v_group_id from public.iac_interface_temp_table_group t where t.name=v_group_name;
select id into v_group_line_id from "public".iac_interface_temp_table_group_line t where t.group_id=v_group_id and t.group_line_name=v_group_line_name;                                                                                                                   
select o_last_id,o_log_id,o_log_line_id into v_break_id,v_log_id,v_log_line_id from ep_temp_master.sp_func_get_log_info(v_sap_log_id,v_group_line_id);                                                                                                                        
                                                                                                                           

for v_rc in select * from ep_temp_master.iac_traw_data 
where vendor_code<>''and id > v_start_id order by id LIMIT v_limit 
	                                                                                                                            
loop                                                                                                                                                            
			begin        
				select count(*) into v_count from "public".iac_traw_data 
				  where plant_ori=rtrim(v_rc.plant) and material_ori=rtrim(v_rc.material)
				    and vendor_ori=rtrim(v_rc.vendor_code) and buyer_ori=rtrim(v_rc.buyer_code) 
					and fpversion=v_rc.fpversion ;                       
                                                       
				 --目?表中不存在相???,?行插入操作                                                                                                           
				 if v_count=0 THEN
						INSERT INTO "public".iac_traw_data (
							alt_flag,
							alt_grp,
							b001,
							b002,
							b004,
							b005,
							b012,
							b017b,
							b902q,
							b902s,
							buyer_ori,
							creation_date,
							custpn_info,
							description,
							division_ori,
							flag,
							fpversion,
							intransit_qty,
							leadtime,
							material_ori,
							max_surplus_qty,
							mfgpn_info,
							mquota_flag,
							open_po,
							plant_ori,
							po,
							pr,
							qty_m1,
							qty_m2,
							qty_m3,
							qty_m4,
							qty_m5,
							qty_m6,
							qty_m7,
							qty_m8,
							qty_m9,
							qty_w1,
							qty_w1_r,
							qty_w10,
							qty_w11,
							qty_w12,
							qty_w13,
							qty_w2,
							qty_w3,
							qty_w4,
							qty_w5,
							qty_w6,
							qty_w7,
							qty_w8,
							qty_w9,
							quota,
							remark,
							round_value,
							stock,
							vendor_ori,
							vendor_name,
							sap_log_id,
							sap_temp_id							
						)
						VALUES(							
							v_rc.alt_flag,
							v_rc.alt_grp,
							v_rc.b001,
							v_rc.b002,
							v_rc.b004,
							v_rc.b005,
							v_rc.b012,
							v_rc.b017b,
							v_rc.b902q,
							v_rc.b902s,
							rtrim(v_rc.buyer_code),
							v_rc.creation_date,
							v_rc.custpn_info,
							v_rc.description,
							rtrim(v_rc.division),
							v_rc.flag,
							v_rc.fpversion,
							v_rc.intransit_qty,
							v_rc.leadtime,
							rtrim(v_rc.material),
							v_rc.max_surplus_qty,
							v_rc.mfgpn_info,
							v_rc.mquota_flag,
							v_rc.open_po,
							rtrim(v_rc.plant),
							v_rc.po,
							v_rc.pr,
							v_rc.qty_m1,
							v_rc.qty_m2,
							v_rc.qty_m3,
							v_rc.qty_m4,
							v_rc.qty_m5,
							v_rc.qty_m6,
							v_rc.qty_m7,
							v_rc.qty_m8,
							v_rc.qty_m9,
							v_rc.qty_w1,
							v_rc.qty_w1_r,
							v_rc.qty_w10,
							v_rc.qty_w11,
							v_rc.qty_w12,
							v_rc.qty_w13,
							v_rc.qty_w2,
							v_rc.qty_w3,
							v_rc.qty_w4,
							v_rc.qty_w5,
							v_rc.qty_w6,
							v_rc.qty_w7,
							v_rc.qty_w8,
							v_rc.qty_w9,
							v_rc.quota,
							v_rc.remark,
							v_rc.round_value,
							v_rc.stock,
							rtrim(v_rc.vendor_code),
							v_rc.vendor_name,
							v_sap_log_id,
							v_rc. ID
						);                            
                                                                                                                      
				 end if;                                                                                                                                         
                                                                                                                                                                
				 --目??据存在,?行更新操作                                                                                                                     
				if v_count=1 THEN
					UPDATE "public".iac_traw_data
						SET alt_flag = v_rc.alt_flag,
							alt_grp = v_rc.alt_grp,
							b001 = v_rc.b001,
							b002 = v_rc.b002,
							b004 = v_rc.b004,
							b005 = v_rc.b005,
							b012 = v_rc.b012,
							b017b = v_rc.b017b,
							b902q = v_rc.b902q,
							b902s = v_rc.b902s,
							buyer_ori = rtrim(v_rc.buyer_code),
							creation_date = v_rc.creation_date,
							custpn_info = v_rc.custpn_info,
							description = v_rc.description,
							division_ori = rtrim(v_rc.division),
							flag = v_rc.flag,
							fpversion = v_rc.fpversion,
							intransit_qty = v_rc.intransit_qty,
							leadtime = v_rc.leadtime,
							material_ori = rtrim(v_rc.material),
							max_surplus_qty = v_rc.max_surplus_qty,
							mfgpn_info = v_rc.mfgpn_info,
							mquota_flag = v_rc.mquota_flag,
							open_po = v_rc.open_po,
							plant_ori = rtrim(v_rc.plant),
							po = v_rc.po,
							pr = v_rc.pr,
							qty_m1 = v_rc.qty_m1,
							qty_m2 = v_rc.qty_m2,
							qty_m3 = v_rc.qty_m3,
							qty_m4 = v_rc.qty_m4,
							qty_m5 = v_rc.qty_m5,
							qty_m6 = v_rc.qty_m6,
							qty_m7 = v_rc.qty_m7,
							qty_m8 = v_rc.qty_m8,
							qty_m9 = v_rc.qty_m9,
							qty_w1 = v_rc.qty_w1,
							qty_w1_r = v_rc.qty_w1_r,
							qty_w10 = v_rc.qty_w10,
							qty_w11 = v_rc.qty_w11,
							qty_w12 = v_rc.qty_w12,
							qty_w13 = v_rc.qty_w13,
							qty_w2 = v_rc.qty_w2,
							qty_w3 = v_rc.qty_w3,
							qty_w4 = v_rc.qty_w4,
							qty_w5 = v_rc.qty_w5,
							qty_w6 = v_rc.qty_w6,
							qty_w7 = v_rc.qty_w7,
							qty_w8 = v_rc.qty_w8,
							qty_w9 = v_rc.qty_w9,
							quota = v_rc.quota,
							remark = v_rc.remark,
							round_value = v_rc.round_value,
							stock = v_rc.stock,
							vendor_ori = rtrim(v_rc.vendor_code),
							vendor_name = v_rc.vendor_name,
							sap_log_id = v_sap_log_id,
							sap_temp_id = v_rc. ID
						WHERE plant_ori=rtrim(v_rc.plant) and material_ori=rtrim(v_rc.material)
						  and vendor_ori=rtrim(v_rc.vendor_code) and buyer_ori=rtrim(v_rc.buyer_code) 
						  and fpversion=v_rc.fpversion ;    
                                                                                                                   
				end if;                  
				v_last_id:=v_rc.id;
				v_update_count:=v_update_count+1;                                                                                                     
			EXCEPTION                                                                                                                                            
			when OTHERS THEN                                                                                                                                     
           GET STACKED DIAGNOSTICS                                                                                          
                                   v_message_text = MESSAGE_TEXT,                                                                                               
								   v_exception_detail=PG_EXCEPTION_DETAIL;                                                     
                                                                                                                        
					v_exception_detail:='A error occurs when insert table ( '||v_table_name||' ),source id is ( '||v_rc.id||' )';                                                                                                                                                      
          perform ep_temp_master.sp_func_write_ex_log(v_sap_log_id,v_log_id,v_log_line_id,v_group_id,v_group_line_id,v_group_name,v_group_line_name,v_table_name,v_column_name,v_message_text,v_exception_detail,v_rc.id);  
          v_fail_count:=v_fail_count+1;                                                                                                      
      end;                                                                                                                                                      
end loop;                                                                                                                                                                                                                                                                                                           
return query select v_last_id,v_log_line_id,v_group_id,v_group_line_id,v_group_name,v_group_line_name,v_update_count,v_fail_count,v_miss_count;
return ;                                                                                                                                                  
                                                                                                                                                                
end;                                                                                                                                                            
$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100
 ROWS 1000
;

ALTER FUNCTION "ep_temp_master"."proc_trans_table_iac_traw_data"(v_sap_log_id varchar, v_limit int4, v_start_id int4) OWNER TO "odooiac";