-- FUNCTION: ep_temp_master.proc_trans_table_iac_tdelivery_edi()

-- DROP FUNCTION ep_temp_master.proc_trans_table_iac_tdelivery_edi();
--- SELECT   ep_temp_master.proc_trans_table_iac_tdelivery_edi();

/*
���� FUNCTION�y�y
SELECT ep_temp_master.proc_trans_table_iac_tdelivery_edi() ;


--1.���N ep_temp_master.iac_tdelivery_edi ��� public
---1.1. update iac_tdelivery_edi=>���n����fcst_version+vendor_code+iac_pn�A�N�v�s�b��data�Avalid �q1���令0 and status�令�qT���令F
---1.2. �~�O��insert �N ep_temp_master.iac_tdelivery_edi ��� public
--2.�N�৹���� ep_temp_master.iac_tdelivery_edi �R��
--3.�Npublic.iac_tdelivery_edi ���id�ഫ

�B ������ �ݮ�valid = 1&status=T ���~�|�� (�~���|��쭫�ưe��)

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

--�ݱ`����H��                                                                                                                                                  
v_table_name varchar;                                                                                                                                           
v_column_name varchar;                                                                                                                                          
v_message_text text;                                                                                                                                            
v_exception_detail text;                                                                                                                                        
v_src_id int4;                                                                                                                                                  
                                                                                                                                                                
--�O���B�z��Ӭ���                                                                                                                                              
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
							  
--�M��iac_tdelivery_edi ��,���u�ಾ��odoo������                                                                                                                        
for v_rc in select * from ep_temp_master.iac_tdelivery_edi where finish is null                                                                                                                           
loop                                                                                                                                                            
	begin        	

		 select count(*) into v_count_1 from "public".iac_tdelivery_edi 
		  where fcst_version=rtrim(v_rc.fcst_version) 
		    and iac_pn=rtrim(v_rc.iac_pn)
			  and plant=rtrim(v_rc.plant) 
			  and vendor_code=rtrim(v_rc.vendor_code)
			  and shipping_date = v_rc.shipping_date  ;  
			
		--�ؼЪ��s�b��������,�i��F
		---  1.1. update iac_tdelivery_edi=>���n���� fcst_version+vendor_code+iac_pn�A
		---   �N�v�s�b��data�Avalid �q1���令0 and status�qT���令F
		if v_count_1>=1 THEN   	
			UPDATE "public".iac_tdelivery_edi 
			   SET "valid" = 0 , status='F'
			 where fcst_version=rtrim(v_rc.fcst_version) 
		     and iac_pn=rtrim(v_rc.iac_pn)
			   and plant=rtrim(v_rc.plant) 
			   and vendor_code=rtrim(v_rc.vendor_code) 
				 and shipping_date = v_rc.shipping_date ; 
		end if;    
		
		---1.2. �~�O��insert �N ep_temp_master.iac_tdelivery_edi ��� public

			if v_rc."valid"=1 THEN
				v_rc.status:='T';
			ELSE 
				v_rc.status:='F'; 
			END IF; 
			--1.���N ep_temp_master.iac_tdelivery_edi ��� public
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
		
			--2.�N�৹���� ep_temp_master.iac_tdelivery_edi �� finish �� 'd' : �N��w��ipublic 
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


--�M�� ������iac_tdelivery_edi ��,���id�ഫ                                                                                                                      
for v_rc2 in select * from "public".iac_tdelivery_edi where plant_id is null or vendor_id is null or material_id is null                                                                                                                         
loop                                                                                                                                                            
	begin 
			--3.�Npublic.iac_tdelivery_edi ���id�ഫ
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