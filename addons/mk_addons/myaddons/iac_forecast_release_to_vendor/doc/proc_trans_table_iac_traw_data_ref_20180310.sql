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
	
CREATE OR REPLACE FUNCTION "ep_temp_master"."proc_trans_table_iac_traw_data_ref"(v_sap_log_id varchar, v_limit int4, v_start_id int4)
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
v_miss        integer;                                                                                                                                                
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
 
--遍? 正式 vendor 表,?理??字段列表如下                                                                                                                        
                                                                                                                                                                  
for v_rc in 
select * from "public".iac_traw_data where id>v_start_id and sap_log_id=v_sap_log_id  order by id LIMIT v_limit                          

loop                                                                                                                                                              
			begin
				--perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'plant_id', 'pur_org_data' , 'plant_code', v_rc.id, v_rc.plant_ori);	
				v_miss:=0;
				select ep_temp_master.sp_update_table_ref('"public".iac_traw_data' , 'plant_id', '"public".pur_org_data' , 'plant_code', v_rc.id, v_rc.plant_ori) 
				  into v_miss;
				  if v_miss=1 THEN         
								 v_miss_count:=v_miss_count+1;
					 continue;
				  end if;   
				
				--perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'buyer_id', 'buyer_code' , 'buyer_erp_id', v_rc.id, v_rc.buyer_ori);	
				v_miss:=0;
				select ep_temp_master.sp_update_table_ref('"public".iac_traw_data' , 'buyer_id', '"public".buyer_code' , 'buyer_erp_id', v_rc.id, v_rc.buyer_ori) 
				  into v_miss;
				  if v_miss=1 THEN         
								 v_miss_count:=v_miss_count+1;
					 continue;
				  end if; 	
				
				--perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'division_id', 'division_code' , 'division_description', v_rc.id, v_rc.division_ori); 	
				v_miss:=0;
				select ep_temp_master.sp_update_table_ref('"public".iac_traw_data' , 'division_id', '"public".division_code' , 'division_description', v_rc.id, v_rc.division_ori) 
				  into v_miss;
				  if v_miss=1 THEN         
								 v_miss_count:=v_miss_count+1;
					 continue;
				  end if; 
				
				--perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'material_id', 'material_master' , 'part_unique_code', v_rc.id, v_rc.material_ori||v_rc.plant_ori);  	
				v_miss:=0;
				select ep_temp_master.sp_update_table_ref('"public".iac_traw_data' , 'material_id', '"public".material_master' , 'part_unique_code', v_rc.id, v_rc.material_ori||v_rc.plant_ori) 
				  into v_miss;
				  if v_miss=1 THEN         
								 v_miss_count:=v_miss_count+1;
					 continue;
				  end if; 

				--perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'vendor_id', 'iac_vendor' , 'vendor_code', v_rc.id, v_rc.vendor_ori);	
				v_miss:=0;
				select ep_temp_master.sp_update_table_ref('"public".iac_traw_data' , 'vendor_id', '"public".iac_vendor' , 'vendor_code', v_rc.id, v_rc.vendor_ori) 
				  into v_miss;
				  if v_miss=1 THEN         
								 v_miss_count:=v_miss_count+1;
					 continue;
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

ALTER FUNCTION "ep_temp_master"."proc_trans_table_iac_traw_data_ref"(v_sap_log_id varchar, v_limit int4, v_start_id int4) OWNER TO "odooiac"; 
