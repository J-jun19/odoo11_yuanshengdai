
--1 在目标数据库中建立 ep_temp_master 模式

--2 在 ep_temp_master 中执行IAC_master.sql 脚本,这个操作会建立 表 序列 主键 和相应的配置数据

--3 在源数据库中 ep_temp_master 模式中执行存储过程获取最新的函数脚本
select proc_trans_get_fun_def();

--4 导出lwt_fun_def 表中的数据到csv文件中,注意选择包含列标题
--当前目录中lwt_fun_def.csv就是全部存储过程列表
select * from lwt_fun_def;

--5 在目标数据库中 ep_temp_master 模式中,执行下面脚本 建立 函数
-------------------------------------
-------------------------------------

--执行存储过程创建目标数据库的存储过程
CREATE OR REPLACE FUNCTION "ep_temp_master"."proc_init_create_fun_from_rec"()
  RETURNS "pg_catalog"."int4" AS $BODY$

declare
v_rc	record;
v_pre_period_id integer;
v_start_datetime varchar;
v_end_datetime varchar;
v_count_1	integer;
v_count_2 integer;
begin
--遍历 address 表,数据转移到odoo正式表中
for v_rc in select * from lwt_fun_def
loop
  execute v_rc.fun_def;
end loop;

  return 1;
end;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE COST 100
;
ALTER FUNCTION "ep_temp_master"."proc_init_create_fun_from_rec"() OWNER TO "openerp";

-------------------------------------
-------------------------------------

--6 在目标数据库中 ep_temp_master 模式中导入 步骤4 中导出的 csv文件
倒入之前 先删除数据
delete from lwt_fun_def;

--7 在目标数据库中 ep_temp_master 模式中,执行存储过程，执行这个存储过程会建立 中间表接口所需的函数
select proc_init_create_fun_from_rec();

f04 f02 接口都不要穿财务人员


获取模块的菜单
SELECT
  p.id ,
	T . NAME menu_id_name,
  p.name menu_name,
  p."sequence",
  p.parent_id,
  p.parent_left,
  p.parent_right
FROM
	ir_model_data T,ir_ui_menu p
WHERE
	T .model = 'ir.ui.menu'
AND T ."module" = 'oscg_rfq'
and t.res_id=p.id
order by p.parent_id ,p.parent_left,p.parent_right
;

测试账户
test_user_buyer
test_user_vendor
test_user_ep_user
test_user_asn_rule
test_user_warehouse
test_user_asn_ctrl
test_user_ep_admin
test_user_cm
test_user_as

https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
		trigger_type 为 cron
        year (int|str) – 4-digit year
        month (int|str) – month (1-12)
        day (int|str) – day of the (1-31)
        week (int|str) – ISO week (1-53)
        day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour (int|str) – hour (0-23)
        minute (int|str) – minute (0-59)
        second (int|str) – second (0-59)
        start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)


		设置cron_text为如下格式,列入秒数为5的时候启动:
		{
			"second":5
		}

http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f01/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f02/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f03/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f04.b.1/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f04.b.2/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f04.b.3/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f05/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f06/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f07.e.1/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f07.e.2/call/call.in.func/admin
http://iacp-erp-pc.iacp.iac:8069/webflow/IAC.DB/web.call.in.webflow.f08/call/call.in.func/admin