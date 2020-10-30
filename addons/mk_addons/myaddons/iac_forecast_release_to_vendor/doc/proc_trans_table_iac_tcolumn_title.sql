-- FUNCTION: ep_temp_master.proc_trans_table_iac_tcolumn_title(character varying, integer, integer, integer, integer)

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_tcolumn_title(character varying, integer, integer, integer, integer);
/*

執行 FUNCTION語句

SELECT ep_temp_master.proc_trans_table_iac_tcolumn_title('t0209',1,1,1000,0) ;

SELECT ep_temp_master.proc_trans_table_iac_tcolumn_title_ref('t0209',1,1,1000,0) ; 

--先找到 public.iac_tcolumn_title的 need_update_id 須更新的值, 再改參數 
SELECT ep_temp_master.proc_trans_table_iac_tcolumn_title_ref('test4',need_update_id,561,561,1000,0) ; 

*/

CREATE OR REPLACE FUNCTION ep_temp_master.proc_trans_table_iac_tcolumn_title(
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
for v_rc in select * from ep_temp_master.iac_tcolumn_title order by id LIMIT v_limit offset v_offset                                                                                                                                  
loop                                                                                                                                                            
			begin                                                                                                                                                
				 select count(*) into v_count_1 from "public".iac_tcolumn_title 
				  where fpversion=v_rc.fpversion ;  -- 同一天fpversion 只會有一筆資料                      
				 
				 --目標表中不存在相關紀錄,進行插入操作                                                                                                           
				 if v_count_1=0 THEN    
						INSERT INTO "public".iac_tcolumn_title (
							fpversion,
							qty_w2,
							division,
							qty_w5,
							creation_date,
							b017b,
							intransit_qty,
							buyer_code,
							open_po,
							qty_w3,
							alt_grp,
							pr,
							qty_m3,
							qty_m1,
							qty_m6,
							qty_m7,
							qty_m4,
							qty_m8,
							qty_m9,
							b012,
							alt_flag,
							po,
							stock,
							qty_m2,
							plant,
							mquota_flag,
							description,
							remark,
							round_value,
							material,
							vendor_code,
							quota,
							flag,
							qty_w7,
							mfgpn_info,
							qty_w1_r,
							qty_w12,
							qty_w13,
							qty_w10,
							qty_w11,
							b002,
							custpn_info,
							qty_w6,
							b001,
							qty_w1,
							b004,
							b005,
							b902s,
							b902q,
							qty_w8,
							qty_w4,
							qty_w9,
							qty_m5,
							vendor_name,
							leadtime,
							max_surplus_qty,
							sap_temp_id,
							sap_log_id 					
						)
						VALUES(	
							v_rc.fpversion,
							v_rc.qty_w2,
							v_rc.division,
							v_rc.qty_w5,
							v_rc.creation_date,
							v_rc.b017b,
							v_rc.intransit_qty,
							v_rc.buyer_code,
							v_rc.open_po,
							v_rc.qty_w3,
							v_rc.alt_grp,
							v_rc.pr,
							v_rc.qty_m3,
							v_rc.qty_m1,
							v_rc.qty_m6,
							v_rc.qty_m7,
							v_rc.qty_m4,
							v_rc.qty_m8,
							v_rc.qty_m9,
							v_rc.b012,
							v_rc.alt_flag,
							v_rc.po,
							v_rc.stock,
							v_rc.qty_m2,
							v_rc.plant,
							v_rc.mquota_flag,
							v_rc.description,
							v_rc.remark,
							v_rc.round_value,
							v_rc.material,
							v_rc.vendor_code,
							v_rc.quota,
							v_rc.flag,
							v_rc.qty_w7,
							v_rc.mfgpn_info,
							v_rc.qty_w1_r,
							v_rc.qty_w12,
							v_rc.qty_w13,
							v_rc.qty_w10,
							v_rc.qty_w11,
							v_rc.b002,
							v_rc.custpn_info,
							v_rc.qty_w6,
							v_rc.b001,
							v_rc.qty_w1,
							v_rc.b004,
							v_rc.b005,
							v_rc.b902s,
							v_rc.b902q,
							v_rc.qty_w8,
							v_rc.qty_w4,
							v_rc.qty_w9,
							v_rc.qty_m5,
							v_rc.vendor_name,
							v_rc.leadtime,
							v_rc.max_surplus_qty,
							v_rc. ID,
							v_sap_log_id
						);
            o_insert_count:=o_insert_count+1;                                                                                                                         
				 end if;                                                                                                                                         
                                                                                                                                                                
				 --目標据存在,進行更新操作                                                                                                                     
				if v_count_1=1 THEN  
						UPDATE "public".iac_tcolumn_title
						SET fpversion = v_rc.fpversion,
							qty_w2 = v_rc.qty_w2,
							division = v_rc.division,
							qty_w5 = v_rc.qty_w5,
							creation_date = v_rc.creation_date,
							b017b = v_rc.b017b,
							intransit_qty = v_rc.intransit_qty,
							buyer_code = v_rc.buyer_code,
							open_po = v_rc.open_po,
							qty_w3 = v_rc.qty_w3,
							alt_grp = v_rc.alt_grp,
							pr = v_rc.pr,
							qty_m3 = v_rc.qty_m3,
							qty_m1 = v_rc.qty_m1,
							qty_m6 = v_rc.qty_m6,
							qty_m7 = v_rc.qty_m7,
							qty_m4 = v_rc.qty_m4,
							qty_m8 = v_rc.qty_m8,
							qty_m9 = v_rc.qty_m9,
							b012 = v_rc.b012,
							alt_flag = v_rc.alt_flag,
							po = v_rc.po,
							stock = v_rc.stock,
							qty_m2 = v_rc.qty_m2,
							plant = v_rc.plant,
							mquota_flag = v_rc.mquota_flag,
							description = v_rc.description,
							remark = v_rc.remark,
							round_value = v_rc.round_value,
							material = v_rc.material,
							vendor_code = v_rc.vendor_code,
							quota = v_rc.quota,
							flag = v_rc.flag,
							qty_w7 = v_rc.qty_w7,
							mfgpn_info = v_rc.mfgpn_info,
							qty_w1_r = v_rc.qty_w1_r,
							qty_w12 = v_rc.qty_w12,
							qty_w13 = v_rc.qty_w13,
							qty_w10 = v_rc.qty_w10,
							qty_w11 = v_rc.qty_w11,
							b002 = v_rc.b002,
							custpn_info = v_rc.custpn_info,
							qty_w6 = v_rc.qty_w6,
							b001 = v_rc.b001,
							qty_w1 = v_rc.qty_w1,
							b004 = v_rc.b004,
							b005 = v_rc.b005,
							b902s = v_rc.b902s,
							b902q = v_rc.b902q,
							qty_w8 = v_rc.qty_w8,
							qty_w4 = v_rc.qty_w4,
							qty_w9 = v_rc.qty_w9,
							qty_m5 = v_rc.qty_m5,
							vendor_name = v_rc.vendor_name,
							leadtime = v_rc.leadtime,
							max_surplus_qty = v_rc.max_surplus_qty,
							sap_temp_id = v_rc. ID,
							sap_log_id = v_sap_log_id
						WHERE fpversion = v_rc.fpversion ;  -- 同一天fpversion 只會有一筆資料   
						 
            o_update_count:=o_update_count+1;                                                                                                                           
				end if;                                                                                                                                          
				v_proc_line_count:=v_proc_line_count+1;
                                                                                                      
			EXCEPTION                                                                                                                                            
			when OTHERS THEN                                                                                                                                     
           GET STACKED DIAGNOSTICS                                                                                                 
                                   v_message_text = MESSAGE_TEXT,                                                                                               
																	 v_exception_detail=PG_EXCEPTION_DETAIL;                                                     
          v_table_name:='iac_tcolumn_title';                                                                                                                              
					v_exception_detail:='A error occurs when insert table ( '||v_table_name||' ),source id is ( '||v_rc.id||' )';                                
					v_src_id=v_rc.id;                                                                                                                            
					perform ep_temp_master.write_exception_log(v_sap_log_id,v_group_id,v_group_line_id,v_table_name,v_column_name,v_message_text,v_exception_detail,v_src_id);  
          v_proc_line_fail_count=v_proc_line_fail_count+1;   
          o_fail_count:=o_fail_count+1;                                                                                                   
      end;                                                                                                                                                      
end loop;                                                                                                                                                       
return;                                                                                                                                                   
                                                                                                                                                                
end;                                                                                                                                                            

$BODY$;

ALTER FUNCTION ep_temp_master.proc_trans_table_iac_tcolumn_title(character varying, integer, integer, integer, integer)
    OWNER TO openerp;

