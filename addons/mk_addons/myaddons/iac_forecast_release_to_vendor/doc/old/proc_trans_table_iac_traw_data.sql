-- FUNCTION: ep_temp_master.proc_trans_table_iac_traw_data(character varying, integer, integer, integer, integer)

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_traw_data(character varying, integer, integer, integer, integer);
/*

執行 FUNCTION語句

SELECT ep_temp_master.proc_trans_table_iac_traw_data('t0209',561,561,5000,0) ;

SELECT ep_temp_master.proc_trans_table_iac_traw_data_ref('t0209',561,561,5000,0) ;


--先找到 public.iac_traw_data的 need_update_id 須更新的值, 再改參數 
SELECT ep_temp_master.proc_trans_table_iac_traw_data_ref('test4',need_update_id,561,561,1000,0) ; 

*/
/*
SELECT  DISTINCT vendor_id,vendor_ori,sap_log_id
FROM "public"."iac_traw_data" 
where fpversion like '20180212%'
order by vendor_id desc;

SELECT count(*) --DISTINCT fpversion--* 
FROM "ep_temp_master"."iac_traw_data";

*/
/* modify : 
20180202 laura vendor_code=null,不導入。
			   去除表尾空白plant,vendor_code,buyer_code,division,material
			   
*/



CREATE OR REPLACE FUNCTION ep_temp_master.proc_trans_table_iac_traw_data(
	v_sap_log_id character varying,
	v_group_id integer,
	v_group_line_id integer,
	v_limit integer,
	v_offset integer,
	OUT o_insert_count integer,
	OUT o_update_count integer,
	OUT o_fail_count integer)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE 
    ROWS 0
AS $BODY$

declare                                                                                                                                                         
v_rc	record;                                                                                                                                                  
v_pre_period_id integer;                                                                                                                                        
v_start_datetime varchar;                                                                                                                                       
v_end_datetime varchar;                                                                                                                                         
v_count_1	integer;                                                                                                                                             
                                                                                                                                                                
--异常捕獲信息                                                                                                                                                  
v_table_name varchar;                                                                                                                                           
v_column_name varchar;                                                                                                                                          
v_message_text text;                                                                                                                                            
v_exception_detail text;                                                                                                                                        
v_src_id int4;                                                                                                                                                  
                                                                                                                                                                
--記錄處理日志相關                                                                                                                                              
v_proc_line_count int4;                                                                                                                                         
v_proc_line_fail_count int4;                                                                                                                                    
v_start_time TIMESTAMP;                                                                                                                                         
v_end_time TIMESTAMP;                                                                                                                                           
begin                                                                                                                                                           
v_proc_line_count:=0;                                                                                                                                           
v_proc_line_fail_count:=0;                                                                                                                                      
v_start_time:=now();                                                                                                                                            
o_insert_count:=0;
o_update_count:=0;
o_fail_count:=0;                
                                              
 
									  
--遍歷address 表,數据轉移到odoo正式表中                                                                                                                        
for v_rc in select * from ep_temp_master.iac_traw_data where vendor_code<>''order by id LIMIT v_limit offset v_offset                                                                                                                                  
loop                                                                                                                                                            
			begin        				
	  
				 select count(*) into v_count_1 from "public".iac_traw_data 
				  where plant_ori=rtrim(v_rc.plant) and material_ori=rtrim(v_rc.material)
				    and vendor_ori=rtrim(v_rc.vendor_code) and buyer_ori=rtrim(v_rc.buyer_code) 
					and fpversion=v_rc.fpversion ;                       
				 
				 --目標表中不存在相關紀錄,進行插入操作                                                                                                           
				 if v_count_1=0 THEN    
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
            o_insert_count:=o_insert_count+1;                                                                                                                         
				 end if;                                                                                                                                         
                                                                                                                                                                
				 --目標据存在,進行更新操作                                                                                                                     
				if v_count_1=1 THEN  
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
            o_update_count:=o_update_count+1;                                                                                                                           
				end if;                                                                                                                                          
				v_proc_line_count:=v_proc_line_count+1;

                                                                                                      
			EXCEPTION                                                                                                                                            
			when OTHERS THEN                                                                                                                                     
           GET STACKED DIAGNOSTICS                                                                                                 
                                   v_message_text = MESSAGE_TEXT,                                                                                               
																	 v_exception_detail=PG_EXCEPTION_DETAIL;                                                     
          v_table_name:='iac_traw_data';                                                                                                                              
					v_exception_detail:='A error occurs when insert table 0 ( '||v_table_name||' ),source id is ( '||v_rc.id||' )';                                
					v_src_id=v_rc.id;                                                                                                                            
					perform ep_temp_master.write_exception_log(v_sap_log_id,v_group_id,v_group_line_id,v_table_name,v_column_name,v_message_text,v_exception_detail,v_src_id);  
          v_proc_line_fail_count=v_proc_line_fail_count+1;   
          o_fail_count:=o_fail_count+1;                                                                                                   
      end;                                                                                                                                                      
end loop;                                                                                                                                                       
return;                                                                                                                                                   
                                                                                                                                                                
end;                                                                                                                                                            

$BODY$;

ALTER FUNCTION ep_temp_master.proc_trans_table_iac_traw_data(character varying, integer, integer, integer, integer)
    OWNER TO openerp;

