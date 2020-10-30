-- FUNCTION: ep_temp_master.proc_trans_table_iac_tjob_status_ref(character varying, integer, integer, integer, integer)

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status_ref(character varying, integer, integer, integer, integer);
/*

執行 FUNCTION語句

SELECT ep_temp_master.proc_trans_table_iac_tjob_status('test4',561,561,1000,0) ;

SELECT ep_temp_master.proc_trans_table_iac_tjob_status_ref('test4',561,561,1000,0) ; 

--先找到 public.iac_tjob_status的 need_update_id 須更新的值, 再改參數 
SELECT ep_temp_master.proc_trans_table_iac_tjob_status_ref('test4',need_update_id,561,561,1000,0) ; 

*/
CREATE OR REPLACE FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status_ref(
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
                                                                                                                           
                                                                                                                                          
begin                                                                                                                                      
  return ;                                                                                                                                                       
                                                                                                                                                                  
                                                                                                                                                                  
end;                                                                                                                                                              

$BODY$;

ALTER FUNCTION ep_temp_master.proc_trans_table_iac_tjob_status_ref(character varying, integer, integer, integer, integer)
    OWNER TO openerp;

