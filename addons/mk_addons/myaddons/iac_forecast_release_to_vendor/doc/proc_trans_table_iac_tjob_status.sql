-- FUNCTION: ep_temp_master.proc_trans_table_iac_tjob_status(character varying, integer, integer, integer, integer)

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status(character varying, integer, integer, integer, integer);
/*

執行 FUNCTION語句

SELECT ep_temp_master.proc_trans_table_iac_tjob_status('test4',561,561,1000,0) ;

SELECT ep_temp_master.proc_trans_table_iac_tjob_status_ref('test4',561,561,1000,0) ; 

--先找到 public.iac_tjob_status的 need_update_id 須更新的值, 再改參數 
SELECT ep_temp_master.proc_trans_table_iac_tjob_status_ref('test4',need_update_id,561,561,1000,0) ; 

*/

CREATE OR REPLACE FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status(
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
for v_rc in select * from ep_temp_master.iac_tjob_status order by id LIMIT v_limit offset v_offset                                                                                                                                  
loop                                                                                                                                                            
			begin                                                                                                                                                
				 select count(*) into v_count_1 from "public".iac_tjob_status 
				  where fpversion=v_rc.fpversion ;  -- 同一天fpversion 只會有一筆資料                      
				 
				 --目標表中不存在相關紀錄,進行插入操作                                                                                                           
				 if v_count_1=0 THEN    
						INSERT INTO "public".iac_tjob_status (
							fpversion,
							status,
							startTime,
							endTime,
							sap_log_id,
							sap_temp_id								
						)
						VALUES(	
							v_rc.fpversion,
							v_rc.status,
							v_rc.startTime,
							v_rc.endTime,
							v_sap_log_id,
							v_rc. ID
						);
            o_insert_count:=o_insert_count+1;                                                                                                                         
				 end if;                                                                                                                                         
                                                                                                                                                                
				 --目標据存在,進行更新操作                                                                                                                     
				if v_count_1=1 THEN  
						UPDATE "public".iac_tjob_status
						SET fpversion = v_rc.fpversion,
							status = v_rc.status,
							startTime = v_rc.startTime,
							endTime = v_rc.endTime,
							sap_log_id = v_sap_log_id,
							sap_temp_id = v_rc. ID
						WHERE fpversion = v_rc.fpversion ;  -- 同一天fpversion 只會有一筆資料   
						 
            o_update_count:=o_update_count+1;                                                                                                                           
				end if;                                                                                                                                          
				v_proc_line_count:=v_proc_line_count+1;
                                                                                                      
			EXCEPTION                                                                                                                                            
			when OTHERS THEN                                                                                                                                     
           GET STACKED DIAGNOSTICS                                                                                                 
                                   v_message_text = MESSAGE_TEXT,                                                                                               
																	 v_exception_detail=PG_EXCEPTION_DETAIL;                                                     
          v_table_name:='iac_tjob_status';                                                                                                                              
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

ALTER FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status(character varying, integer, integer, integer, integer)
    OWNER TO openerp;

