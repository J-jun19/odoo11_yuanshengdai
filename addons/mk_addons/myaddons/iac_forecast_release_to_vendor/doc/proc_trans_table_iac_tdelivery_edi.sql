-- FUNCTION: ep_temp_master.proc_trans_table_iac_tdelivery_edi()

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_tdelivery_edi();
--- SELECT   ep_temp_master.proc_trans_table_iac_tdelivery_edi();

/*
執行 FUNCTION語句
SELECT ep_temp_master.proc_trans_table_iac_tdelivery_edi() ;


--1.先將 ep_temp_master.iac_tdelivery_edi 轉到 public
---1.1. update iac_tdelivery_edi=>先要捉到fcst_version+vendor_code+iac_pn，將己存在的data，valid 從1的改成0 and status改成從T的改成F
---1.2. 才是做insert 將 ep_temp_master.iac_tdelivery_edi 轉到 public
--2.將轉完成的 ep_temp_master.iac_tdelivery_edi 刪除
--3.將public.iac_tdelivery_edi 欄位id轉換

且 報表抓值 需捉valid = 1&status=T 的才會對 (才不會抓到重複送的)

*/

/*
SELECT * FROM "ep_temp_master"."iac_tdelivery_edi" where fcst_version='20180223115388';
SELECT * FROM "public"."iac_tdelivery_edi"  where fcst_version='20180223115388';

--SELECT ep_temp_master.proc_trans_table_iac_tdelivery_edi() ;
*/

CREATE OR REPLACE FUNCTION "ep_temp_master"."proc_trans_table_iac_tdelivery_edi"()
  RETURNS "pg_catalog"."int4" AS $BODY$

declare       
v_sap_log_id character varying;
v_group_id integer;
v_group_line_id integer;
v_limit integer;
v_offset integer;                                                                                                                                                 
v_rc	record;
v_rc2	record;                                                                                                                                                    
v_pre_period_id integer;                                                                                                                                        
v_start_datetime varchar;                                                                                                                                       
v_end_datetime varchar;                                                                                                                                         
v_count_1	integer;  
o_insert_count int4;
o_update_count int4;
o_fail_count int4;    

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
v_sap_log_id:=1;      
v_group_id:=1;  
v_group_line_id:=1;                                                                                                                                    
v_proc_line_count:=0;                                                                                                                                           
v_proc_line_fail_count:=0;                                                                                                                                      
v_start_time:=now();                                                                                                                                            
o_insert_count:=0;
o_update_count:=0;
o_fail_count:=0;     
							  
--遍歷iac_tdelivery_edi 表,數据轉移到odoo正式表中                                                                                                                        
for v_rc in select * from ep_temp_master.iac_tdelivery_edi where finish is null                                                                                                                           
loop                                                                                                                                                            
	begin        	

		 select count(*) into v_count_1 from "public".iac_tdelivery_edi 
		  where fcst_version=rtrim(v_rc.fcst_version) 
		    and iac_pn=rtrim(v_rc.iac_pn)
			  and plant=rtrim(v_rc.plant) 
			  and vendor_code=rtrim(v_rc.vendor_code)
			  and shipping_date = v_rc.shipping_date  ;  
			
		--目標表中存在相關紀錄,進行；
		---  1.1. update iac_tdelivery_edi=>先要捉到 fcst_version+vendor_code+iac_pn，
		---   將己存在的data，valid 從1的改成0 and status從T的改成F
		if v_count_1>=1 THEN   	
			UPDATE "public".iac_tdelivery_edi 
			   SET "valid" = 0 , status='F'
			 where fcst_version=rtrim(v_rc.fcst_version) 
		     and iac_pn=rtrim(v_rc.iac_pn)
			   and plant=rtrim(v_rc.plant) 
			   and vendor_code=rtrim(v_rc.vendor_code) 
				 and shipping_date = v_rc.shipping_date ; 
		end if;    
		
		---1.2. 才是做insert 將 ep_temp_master.iac_tdelivery_edi 轉到 public

			if v_rc."valid"=1 THEN
				v_rc.status:='T';
			ELSE 
				v_rc.status:='F'; 
			END IF; 
			--1.先將 ep_temp_master.iac_tdelivery_edi 轉到 public
			INSERT INTO "public".iac_tdelivery_edi (
				shipping_date,
				qty,
				cdt,
				key_part,
				fcst_version,
				iac_pn,
				plant,
				vendor_code,
				iac_pn_vendor,
				"valid",
				status,
				buyer_code		
			)
			VALUES(							
				v_rc.shipping_date,
				v_rc.qty,
				v_rc.cdt,
				v_rc.key_part,
				v_rc.fcst_version,
				rtrim(v_rc.iac_pn),
				rtrim(v_rc.plant),
				rtrim(v_rc.vendor_code),
				rtrim(v_rc.iac_pn)||replace(rtrim(v_rc.vendor_code),'0000',''),
				v_rc.valid,
				v_rc.status,
				substr(v_rc.fcst_version,1,3)		
			);
		o_insert_count:=o_insert_count+1;    
		
			--2.將轉完成的 ep_temp_master.iac_tdelivery_edi 的 finish 改 'd' : 代表已轉進public 
			UPDATE "ep_temp_master".iac_tdelivery_edi set finish = 'D' where id = v_rc. ID  ;                                                                                                 
			
			EXCEPTION                                                                                                                                            
			when OTHERS THEN                                                                                                                                     
           GET STACKED DIAGNOSTICS                                                                                                 
                                   v_message_text = MESSAGE_TEXT,                                                                                               
																	 v_exception_detail=PG_EXCEPTION_DETAIL;                                                     
          v_table_name:='iac_tdelivery_edi';                                                                                                                              
					v_exception_detail:='A error occurs when insert table 0 ( '||v_table_name||' ),source id is ( '||v_rc.id||' )';                                
					v_src_id=v_rc.id;                                                                                                                            
					perform ep_temp_master.write_exception_log(v_sap_log_id,v_group_id,v_group_line_id,v_table_name,v_column_name,v_message_text,v_exception_detail,v_src_id);  
          v_proc_line_fail_count=v_proc_line_fail_count+1;   
          o_fail_count:=o_fail_count+1;   
		   
    end;                                                                                                                                                      
end loop;   


--遍歷 正式表iac_tdelivery_edi 表,欄位id轉換                                                                                                                      
for v_rc2 in select * from "public".iac_tdelivery_edi where plant_id is null or vendor_id is null or material_id is null                                                                                                                         
loop                                                                                                                                                            
	begin 
			--3.將public.iac_tdelivery_edi 欄位id轉換
			perform ep_temp_master.proc_update_table_ref('iac_tdelivery_edi' , 'plant_id', 'pur_org_data' , 'plant_code', v_rc2.id, v_rc2.plant);
			perform ep_temp_master.proc_update_table_ref('iac_tdelivery_edi' , 'material_id', 'material_master' , 'part_unique_code', v_rc2.id, v_rc2.iac_pn||v_rc2.plant);  
			perform ep_temp_master.proc_update_table_ref('iac_tdelivery_edi' , 'vendor_id', 'iac_vendor' , 'vendor_code', v_rc2.id, v_rc2.vendor_code);
			perform ep_temp_master.proc_update_table_ref('iac_tdelivery_edi' , 'buyer_id', 'buyer_code' , 'buyer_erp_id', v_rc2.id, v_rc2.buyer_code);
					

			EXCEPTION                                                                                                                                            
			when OTHERS THEN                                                                                                                                     
           GET STACKED DIAGNOSTICS                                                                                                 
                                   v_message_text = MESSAGE_TEXT,                                                                                               
																	 v_exception_detail=PG_EXCEPTION_DETAIL;                                                     
          v_table_name:='iac_tdelivery_edi';                                                                                                                              
					v_exception_detail:='A error occurs when insert table 1 ( '||v_table_name||' ),source id is ( '||v_rc2.id||' )';                                
					v_src_id=v_rc2.id;                                                                                                                            
					perform ep_temp_master.write_exception_log(v_sap_log_id,v_group_id,v_group_line_id,v_table_name,v_column_name,v_message_text,v_exception_detail,v_src_id);  
          v_proc_line_fail_count=v_proc_line_fail_count+1;   
          o_fail_count:=o_fail_count+1;   
		  
    end;                                                                                                                                                      
end loop; 
		
return 1;                                                                                                                                                   
                                                                                                                                                                
end;                                                                                                                                                            

$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100
;

ALTER FUNCTION "ep_temp_master"."proc_trans_table_iac_tdelivery_edi"() OWNER TO "openerp";