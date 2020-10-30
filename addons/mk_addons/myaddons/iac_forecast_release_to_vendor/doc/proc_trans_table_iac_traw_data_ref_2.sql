-- FUNCTION: ep_temp_master.proc_trans_table_iac_traw_data_ref_2(character varying, integer, integer, integer, integer, integer)

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_traw_data_ref_2(character varying, integer, integer, integer, integer, integer);
/*

執行 FUNCTION語句

SELECT ep_temp_master.proc_trans_table_iac_traw_data('test4',561,561,1000,0) ;

SELECT ep_temp_master.proc_trans_table_iac_traw_data_ref('test4',561,561,1000,0) ; 

--先找到 public.iac_traw_data的 need_update_id 須更新的值, 再改參數 
SELECT ep_temp_master.proc_trans_table_iac_traw_data_ref('test4',need_update_id,561,561,1000,0) ; 

*/
CREATE OR REPLACE FUNCTION ep_temp_master.proc_trans_table_iac_traw_data_ref_2(
	v_sap_log_id character varying,
	v_need_update_id integer,
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
                                                                                                                                                                  
--异常捕?信息                                                                                                                                                    
v_table_name varchar;                                                                                                                                             
v_column_name varchar;                                                                                                                                            
v_message_text text;                                                                                                                                              
v_exception_detail text;                                                                                                                                          
v_src_id int4;                                                                                                                                                    
                                                                                                                                                                  
--???理日志相?                                                                                                                                                
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
--遍? 正式 vendor 表,?理??字段列表如下                                                                                                                        
                                                                                                                                                                  
for v_rc in select * from "public".iac_traw_data where need_update_id=v_need_update_id order by id LIMIT v_limit offset v_offset                                                                                            
loop                                                                                                                                                              
			begin			  
					perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'division_id', 'division_code' , 'division_description', v_rc.id, v_rc.division_ori); 
					perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'plant_id', 'pur_org_data' , 'plant_code', v_rc.id, v_rc.plant_ori);
					perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'buyer_id', 'buyer_code' , 'buyer_erp_id', v_rc.id, v_rc.buyer_ori);
					perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'material_id', 'material_master' , 'part_unique_code', v_rc.id, v_rc.material_ori||v_rc.plant_ori);  
					perform ep_temp_master.proc_update_table_ref('iac_traw_data' , 'vendor_id', 'iac_vendor' , 'vendor_code', v_rc.id, v_rc.vendor_ori);

				  v_proc_line_count:=v_proc_line_count+1;      
          o_update_count:=o_update_count+1;                                                                                                    
			EXCEPTION                                                                                                                                              
			when OTHERS THEN                                                                                                                                       
           GET STACKED DIAGNOSTICS                                                                                                 
                                   v_message_text = MESSAGE_TEXT,                                                                                                 
																	 v_exception_detail=PG_EXCEPTION_DETAIL;                                                       
          v_table_name:='iac_traw_data';                                                                                                                                 
					v_exception_detail:='A error occurs when insert table 2 ( '||v_table_name||' ),source id is ( '||v_rc.id||' )';                                  
					v_src_id=v_rc.id;                                                                                                                              
					perform ep_temp_master.write_exception_log(v_sap_log_id,v_group_id,v_group_line_id,v_table_name,v_column_name,v_message_text,v_exception_detail,v_src_id);    
          v_proc_line_fail_count=v_proc_line_fail_count+1;
          o_fail_count:=o_fail_count+1;                                                                                                        
      end;                                                                                                                                                        
end loop;                                                                                                                                                         
                                                                                                                                                      
  return ;                                                                                                                                                       
                                                                                                                                                                  
                                                                                                                                                                  
end;                                                                                                                                                              

$BODY$;

ALTER FUNCTION ep_temp_master.proc_trans_table_iac_traw_data_ref_2(character varying, integer, integer, integer, integer, integer)
    OWNER TO openerp;

