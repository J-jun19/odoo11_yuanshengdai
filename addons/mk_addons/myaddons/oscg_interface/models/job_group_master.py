# -*- coding: utf-8 -*-
from odoo import models, fields, api,odoo_env
from apscheduler.schedulers.background import BackgroundScheduler
from odoo.modules.registry import RegistryManager
import datetime
import logging
import traceback
import odoo
import threading,time
from odoo import tools
from odoo.tools.safe_eval import safe_eval as eval
from .import interface_timer
from odoo.odoo_env import odoo_env
import json

_logger = logging.getLogger(__name__)

def is_empty_str(str_txt):
    if (str_txt is None or str_txt is False or len(str_txt)==0 or len(str_txt.strip())==0):
        return True
    return False

class IacJobGroupMaster(models.TransientModel):
    _name="iac.job.group.master"


    def _get_page_list(self, record_count, limit_count):
        page_list = []
        if record_count <= limit_count:
            page_list.append(0)
            return page_list

        #计算分页偏移量
        offset_count = 0
        while offset_count < record_count:
            page_list.append(offset_count)
            offset_count = offset_count + limit_count
        return page_list;

    def _get_start_id(self,group_line_id,sp_fun_name):
        """
        每个分组条目的存储过程独立记录已经处理的id值,通过这个id值来进行分页处理记录
        :param group_line_id:
        :param sp_fun_name:
        :return:
        """
        self.env.cr.execute("""
        SELECT
            COALESCE (MAX(last_id), 0) start_id
        FROM
            "public".sp_job_time_log
        WHERE
            group_line_id = %s
        AND sp_name = %s
        """,(group_line_id,sp_fun_name))
        pg_result=self.env.cr.fetchone()
        return pg_result[0]

    def _get_group_log_rec(self,sap_log_id, group_id,group_line_list):
        """
        根据sap_log_id 和 group_name 定位到组日志记录信息
        ,如果组日志记录不存在,那么创建相关记录
        在组日志记录存在的情况下,确保组条目记录也存在，不存在的情况下创建相关组条目记录

        返回值有2个,
        1   组日志记录
        2   以组条目id为索引,组条目日志记录为数值的字典对象
        :param group_name:
        :return:
        """


        #查询是否有未执行完毕的group
        #每个group_line 都有独立的sap_log_id,这里选取顺序号为第一个的group_line 的sap_log_id
        group_rec=self.env["iac.interface.temp.table.group"].browse(group_id)
        group_log_rec=self.env["iac.interface.temp.table.group.exe"].search([('state','=','processing'),('group_id','=',group_id),('sap_log_id','=',sap_log_id)],order='id desc',limit=1)
        if not group_log_rec.exists():
            group_log_vals={
                "group_code":group_rec.code,
                "group_name":group_rec.name,
                "group_id":group_id,
                "sap_log_id":sap_log_id,
                "start_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state":"processing",
                }
            group_log_rec=self.env["iac.interface.temp.table.group.exe"].create(group_log_vals)
            self.env.cr.commit()
        return group_log_rec

    def _get_sp_log_rec(self,group_exe_id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name):
        domain_sp_log=[('group_exe_id','=',group_exe_id)]
        domain_sp_log=[('group_line_id','=',group_line_id)]
        domain_sp_log+=[('sap_log_id','=',sap_log_id)]
        domain_sp_log+=[('sp_name','=',db_func_name)]
        sp_log_rec=self.env["sp.job.time.log"].search(domain_sp_log,limit=1)
        if not sp_log_rec:
           group_line_log_vals={
               "group_name":group_name,
               "group_line_name":group_line_name,
               "group_id":group_id,
               "group_line_id":group_line_id,
               "extractwmid":sap_log_id,
               "sap_log_id":sap_log_id,
               "group_exe_id":group_exe_id,
               "state":"processing",
               "sp_name":db_func_name
           }
           sp_log_rec=self.env["sp.job.time.log"].create(group_line_log_vals)
           self.env.cr.commit()
        return sp_log_rec

    def _confirm_sap_log_state(self,group_exe_id,sap_log_id):
        """
        判断sap 接口表中的关联记录是否应该改写状态
        :return:
        """
        #判断是否所有的存储过程条目都执行完成
        self.env.cr.execute("""
        select count(*) from public.sp_job_time_log
          where group_exe_id=%s and sap_log_id=%s and state <>'success'
        """,(group_exe_id,sap_log_id))
        pg_result=self.env.cr.fetchone()
        #没有状态不为success的条目，表示条目关联的存储过程全部执行完毕
        if pg_result[0]==0:
            self.env.cr.execute("update ep_temp_master.extractlog                        " \
                                " set extractstatus='STEP2DONE' where extractwmid=%s ",
                                (sap_log_id,))
            self.env.cr.commit()

    def proc_tans_group_line_base(self, **kwargs):
        """
        处理一个组条目的函数调用操作,
        同时写入组条目的日志和多次数据函数的操作日志

        :param cr:
        :param group_id:
        :param group_name:
        :param group_line_id:
        :param group_line_name:
        :param sap_log_id:
        :param table_name:
        :param db_func_name:
        :return:
        """
        #设定默认记录分页记录数量
        dict_vals={
            "name":"wang"
        }
        db_func_name=kwargs.get("kwargs").get("db_func_name")
        sap_log_id=kwargs.get("kwargs").get("sap_log_id")
        group_id=kwargs.get("kwargs").get("group_id")
        group_line_id=kwargs.get("kwargs").get("group_line_id")
        group_name=kwargs.get("kwargs").get("group_name")
        group_line_name=kwargs.get("kwargs").get("group_line_name")
        process_table_name=kwargs.get("kwargs").get("process_table_name")
        start_id=kwargs.get("kwargs").get("start_id")
        select_count_sql=kwargs.get("kwargs").get("select_count_sql"," ")
        limit_count=kwargs.get("kwargs").get("limit_count",1000)
        sp_log_id=kwargs.get("kwargs").get("sp_log_id",False)

        #分页数组，存储sql 语句中的offset 参数
        page_list = []

        self.env.cr.execute("""select * from public.iac_interface_temp_table_group_line where id=%s and
                            db_func_name_2=%s""",(group_line_id,db_func_name))
        if self.env.cr.fetchall():
            select_count = "select count(*) from %s where id>%s and sap_log_id='%s' %s" % (process_table_name,start_id,sap_log_id,select_count_sql)
        else:
            select_count = "select count(*) from %s where id>%s %s" % (
            process_table_name, start_id, select_count_sql)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()

        record_count = record_count_result[0][0]
        if record_count==0:
            log_msg="group line name is ( %s ) ,db_func_name is ( %s ),sap_log_id is ( %s )" \
                          ", wait process record count is ( %s ),no record found ,will quit"% \
                    (group_line_name,db_func_name,sap_log_id,record_count)
            _logger.debug(log_msg)
            group_line_log_rec=None
            start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #查找当前执行的存储过程对应的日志记录信息
            if sp_log_id==False:
                err_msg="sp_log_id must be sent"
                _logger.error(err_msg)
                raise Exception(err_msg)
            sp_log_rec=self.env["sp.job.time.log"].browse(sp_log_id)
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            group_line_log_vals={
                "start_time":end_time,
                "end_time":end_time,
                "start_id":start_id,
                "last_id":start_id,
                "log_memo":log_msg,
                "state":"success"
                }
            sp_log_rec.write(group_line_log_vals)
            self.env.cr.commit()
            #判断当前条目的所有存储过程是否都执行完成,如果执行完成则变更接口表日志状态
            self._confirm_sap_log_state(sp_log_rec.group_exe_id.id,sap_log_id)
            return


        #更新sap接口日志表的状态为 PROCESS
        self.env.cr.execute("update ep_temp_master.extractlog                        " \
                   " set extractstatus='ODOO_PROCESS' where extractwmid=%s ",
                   (sap_log_id,))
        self.env.cr.commit()
        #获取目标表的总记录数量
        page_list = self._get_page_list(record_count, limit_count)

        _logger.debug("group line name is ( %s ) ,db_func_name is ( %s ),sap_log_id is ( %s )"\
                      " will start, wait process record count is ( %s )"
                      %(group_line_name,db_func_name,sap_log_id,record_count))

        #group_id=kwargs.get("group_id")
        #group_line_id=kwargs.get("group_line_id")
        #便利分页数组调用数据库中的存储过程完成任务
        miss_count_sum = 0
        update_count_sum = 0
        fail_count_sum = 0
        finish_rate=0
        group_line_log_rec=None
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #查找当前执行的存储过程对应的日志记录信息
        if sp_log_id==False:
            err_msg="sp_log_id must be sent"
            _logger.error(err_msg)
            raise Exception(err_msg)
        sp_log_rec=self.env["sp.job.time.log"].browse(sp_log_id)

        #记录执行sp之前的时间
        vals = {
            'start_time':datetime.datetime.now(),
            "start_id":start_id,
            "last_id":start_id,
            'paramater_str':str(sap_log_id)+','+str(limit_count)+','+str(start_id),
        }
        sp_log_rec.write(vals)
        self.env.cr.commit()

        for offset_count in page_list:
            offset_count=0
            sql_text="select * from " + db_func_name + "(%s,%s,%s)" % (sap_log_id,  limit_count, start_id)
            _logger.debug(sql_text)

            sql_fun_text="SELECT                                " \
                         "	*                                  " \
                         "FROM                                  " \
                         "	%s('%s' ,%s ,%s) AS (  " \
                         "		v_last_id int4,                " \
                         "		v_log_line_id int4,            " \
                         "		v_group_id int4,               " \
                         "		v_group_line_id int4,          " \
                         "		v_group_name VARCHAR,          " \
                         "		v_group_line_name VARCHAR,     " \
                         "		v_update_count int4,           " \
                         "		v_fail_count int4,             " \
                         "		v_miss_count int4              " \
                         "	)                                  "% (db_func_name,sap_log_id,limit_count,start_id)

            #存储执行的sql语句
            self.env.cr.execute("INSERT INTO public.iac_job_func_call_log ( " \
                                                    "	group_id,                                 " \
                                                    "	group_line_id,                            " \
                                                    "	group_name,                               " \
                                                    "	group_line_name,                          " \
                                                    "	fun_call_text,                            " \
                                                    "	sap_log_id                                " \
                                                    ")                                            " \
                                                    "VALUES                                       " \
                                                    "	(%s ,%s ,%s ,%s ,%s ,%s);           ",
                                (group_id,group_line_id,group_name,group_line_name,sql_fun_text,sap_log_id))
            self.env.cr.commit()


            #正式执行sql语句
            self.env.cr.execute("select * from " + db_func_name + "(%s,%s,%s) as "\
            " (v_last_id  int4,v_log_line_id int4,v_group_id int4,v_group_line_id int4,v_group_name varchar,v_group_line_name varchar,v_update_count int4,v_fail_count int4,v_miss_count int4)",
                       (sap_log_id, limit_count, start_id))
            fun_result=self.env.cr.fetchall()


            if len(fun_result)==0:
                err_msg="func name is %s has no return"%(db_func_name,)
                _logger.error(err_msg)
                raise err_msg

            for  v_last_id,v_log_line_id,v_group_id,v_group_line_id,v_group_name,v_group_line_name,v_update_count,v_fail_count,v_miss_count in fun_result:
                miss_count_sum += v_miss_count
                update_count_sum += v_update_count
                fail_count_sum +=  v_fail_count
                finish_rate=format(float(update_count_sum)/float(record_count),'.0%')
                _logger.debug("executing db func %s ,updated records:%s,missed records:%s,fail records:%s" % (
                    db_func_name,v_update_count, v_miss_count, v_fail_count))
                start_id=v_last_id
                vals={
                    "last_id":v_last_id,
                    "update_record_counts":update_count_sum,
                    "fail_record_counts":fail_count_sum,
                    "miss_record_counts":miss_count_sum
                }
                sp_log_rec.write(vals)
                self.env.cr.commit()
                _logger.debug("execute db func %s completed,all record count is: %s ,updated records:%s,finish rate is %s ,missed records:%s,failed records:%s" % (
                    db_func_name,record_count, update_count_sum,finish_rate, miss_count_sum, fail_count_sum))

        #所有操作都完成的情况下,分页调用存储过程执行完成的情况下,需要更新完成的时间点和组条目状态
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        group_line_log_vals={
            "end_time":end_time,
            "state":"success"
            }
        sp_log_rec.write(group_line_log_vals)
        self.env.cr.commit()
        #判断是否所有的存储过程条目都执行完成
        self._confirm_sap_log_state(sp_log_rec.group_exe_id.id,sap_log_id)


    @odoo_env
    def proc_trans_group_base(self, group_name,specific_group_line=0,dict_group_line=None):
        """
        执行一个组操作,从组中获取构成组的条目信息
        然后依次执行条目的3个存储过程,也就是对一个条目需要执行3次存储过程调用,
        存储过程1   默认的表信息从条目的 src_table 中获取
        存储过程2   默认的表信息从条目的 dst_table 中获取
        存储过程3   默认的表信息从条目的 dst_table 中获取
        可以通过参数设定,决定是否要执行存储过程1 或者存储过程2 或者存储过程3
            例如:不执行第一个存储过程,那么这样设定"step_1":0
        可以通过参数设定,决定特定存储过程对应的处理表
            例如：存储过程1 使用的处理表是 public.iac_asn  ,那么设定参数 "process_table":"public.iac_asn"
        可以设定对应表的起始id值,只有大于这个id的数据才会被处理
            例如:步骤1的存储过程起始值为2000,那么这样设定 "start_id_1":2000
        可以设定对应表的sql参数,用于删选表中的记录
            例如:第一步的存储过程需要筛选 del_flag=0,那么这样设定 "select_count_sql_1":"cancel_flag=0"
            可以支持动态参数绑定 "and sap_log_id='%s'"%(sap_log_id,) 能够生成 sap_log_id='11122233'

        specific_group_line 是否只执行 dict_group_line 中的的项目,默认为0不执行
            当为1时，只执行dict_group_line指定的项目
        可以针对每个group_line配置调度信息,决定group_line 执行第1步或者第二步骤,
        或者第一步或者第二步的开始id
        dict_group_line={
            "group_line_name_1":{
                "step_1":0,
                "step_2":1,
                "step_3":1,
                "process_table_1":"public.iac_asn",
                "select_count_sql_1":"cancel_flag=0",
                "select_count_sql_2":"",
                "select_count_sql_3":"",
                "start_id_1":2000,
                "start_id_2":1000,
                "start_id_3":0,
                "limit_count_1":10000,
                "limit_count_2":10000,
                "limit_count_3":10000,
            }
        }
        传入组名参数,进行组数据传输处理
        :param group_name:
        :return:
        """
        #判断SAP系统是否完成数据导入完成

        #获取组合租条目的执行日志记录对象
        #group_log_rec,map_group_line_log_rec=self._get_group_line_log(sap_log_id,group_name)

        #查询组判定组的数据是否全部导入完成
        self.env.cr.execute("SELECT                                                      " \
                            "	sap_log_id,                                              " \
                            "	group_id,                                                " \
                            "	group_line_id,                                           " \
                            "	group_name,                                              " \
                            "	group_line_name,                                         " \
                            "	src_table_name,                                          " \
                            "	dst_table_name,                                          " \
                            "	db_func_name_1,                                          " \
                            "	db_func_name_2,                                          " \
                            "	db_func_name_3,                                           " \
                            "	process_state                                           " \
                            "FROM                                                        " \
                            "	ep_temp_master.sp_job_query_group_line (%s) AS (   " \
                            "		sap_log_id VARCHAR,                                  " \
                            "		group_id int4,                                       " \
                            "		group_line_id int4,                                  " \
                            "		group_name VARCHAR,                                  " \
                            "		group_line_name VARCHAR,                             " \
                            "		src_table_name VARCHAR,                              " \
                            "		dst_table_name VARCHAR,                              " \
                            "		db_func_name_1 VARCHAR,                              " \
                            "		db_func_name_2 VARCHAR,                              " \
                            "		db_func_name_3 VARCHAR,                               " \
                            "		process_state VARCHAR                               " \
                            "	)                                                        ",(group_name,))
        group_line_list = self.env.cr.fetchall()

        if len(group_line_list)==0:
            _logger.debug("group name is %s not found,job will quit" % (group_name))
            return;
        run_group_line_list=[]
        for sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state in group_line_list:
            if sap_log_id!=False and sap_log_id!=None:
                run_group_line_list.append((sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state))


        if len(run_group_line_list)==0:
                _logger.debug("group name is %s not found,job will quit" % (group_name))
                return;

        group_log_rec=self._get_group_log_rec(group_line_list[0][0],group_line_list[0][1],group_line_list)

        #执行db_func_name_1上面的函数
        for sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state in group_line_list:
            step_exe=0
            if is_empty_str(sap_log_id):
                _logger.debug("group line : %s has not get param sap_log_id,will skip "%(group_line_name,))
                continue

            if is_empty_str(db_func_name_1):
                _logger.debug("group line : %s has not set db_func_name_1,will skip "%(group_line_name,))
                continue

            #设定了需要指定项目的参数,没有传递 dict_group_line 则不进行任何操作
            if specific_group_line==1 and specific_group_line==None:
                _logger.debug("when json param specific_group_line is set to 1,param specific_group_line is needed")
                continue
            #只执行指定项目,dict_group_line中设定的项目才能执行
            if specific_group_line==1 and dict_group_line!=None and group_line_name not in dict_group_line:
                _logger.debug("group line : %s is not in dict_group_line,will skip"%(group_line_name,))
                continue
            start_id=0
            kwargs={
                "sap_log_id":sap_log_id,
                "group_id":group_id,
                "group_line_id":group_line_id,
                "group_name":group_name,
                "group_line_name":group_line_name,
                "src_table_name":src_table_name,
                "dst_table_name":dst_table_name,
                "db_func_name":db_func_name_1,
                "process_table_name":src_table_name,
                "start_id":start_id,
                }

            if specific_group_line==1 and dict_group_line!=None:
                group_line_vals=dict_group_line.get(group_line_name)
                start_id=group_line_vals.get("start_id_1",0)
                #没有指定start_id的情况下,通过存储过程执行日志获取最大的start_id
                if start_id==0:
                    start_id=self._get_start_id(group_line_id,db_func_name_1)
                step_exe=group_line_vals.get("step_1",0)
                limit_count=group_line_vals.get("limit_count_1",1000)
                process_table=group_line_vals.get("process_table_1",src_table_name)
                kwargs["start_id"]=start_id
                kwargs["process_table"]=process_table
                kwargs["limit_count"]=limit_count

                if step_exe==0:
                    _logger.debug("group line : %s set step_1=%s,will skip"%(group_line_name,start_id))
                    continue
                #获取存储过程执行日志记录,日过不存在就新建
                sp_log_rec=self._get_sp_log_rec(group_log_rec.id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name_1)
                kwargs["sp_log_id"]=sp_log_rec.id
                root_vals={
                    "kwargs":kwargs
                }
                select_count_sql=group_line_vals.get("select_count_sql_1",False)
                if select_count_sql!=False:
                    script_env={}
                    script_env.update(kwargs)
                    eval_reulst=False
                    try:
                        eval_reulst=eval(select_count_sql,script_env)
                        kwargs["select_count_sql"]=eval_reulst
                    except:
                        _logger.error("calculate select_count_sql_1 param error")
                        traceback.print_exc()

                self.proc_tans_group_line_base(**root_vals)
            else:
                start_id=self._get_start_id(group_line_id,db_func_name_1)
                kwargs["start_id"]=start_id
                sp_log_rec=self._get_sp_log_rec(group_log_rec.id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name_1)
                kwargs["sp_log_id"]=sp_log_rec.id
                #不需要执行项目执行的情况下,直接执行当前条目
                root_vals={
                    "kwargs":kwargs
                }
                self.proc_tans_group_line_base(**root_vals)



        #执行db_func_name_2上面的函数
        for sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state in group_line_list:
            #函数2位空的情况,不进行调用,直接跳过,数据迁移程序存在这种现象,
            #每个表独立更新关联字段,写入正式库只使用一个group_line中的db_fun_name_2
            if is_empty_str(sap_log_id):
                _logger.debug("group line : %s has not get param sap_log_id,will skip "%(group_line_name,))
                continue
            if is_empty_str(db_func_name_2):
                _logger.debug("group line : %s has not set db_func_name_2,will skip ",(group_line_name,))
                continue

            step_exe=0

            #设定了需要指定项目的参数,没有传递 dict_group_line 则不进行任何操作
            if specific_group_line==1 and specific_group_line==None:
                _logger.debug("when json param specific_group_line is set to 1,param specific_group_line is needed")
                continue
                #只执行指定项目,dict_group_line中设定的项目才能执行
            if specific_group_line==1 and dict_group_line!=None and group_line_name not in dict_group_line:
                _logger.debug("group line : %s is not in dict_group_line,will skip",(group_line_name,))
                continue
            start_id=0
            kwargs={
                "sap_log_id":sap_log_id,
                "group_id":group_id,
                "group_line_id":group_line_id,
                "group_name":group_name,
                "group_line_name":group_line_name,
                "src_table_name":src_table_name,
                "dst_table_name":dst_table_name,
                "db_func_name":db_func_name_2,
                "process_table_name":dst_table_name,
                "start_id":start_id,
                }
            if specific_group_line==1 and dict_group_line!=None:
                group_line_vals=dict_group_line.get(group_line_name)
                #start_id=group_line_vals.get("start_id_2",0)
                step_exe=group_line_vals.get("step_2",0)
                limit_count=group_line_vals.get("limit_count_2",1000)
                process_table=group_line_vals.get("process_table_2",dst_table_name)
                # if start_id==0:
                #     start_id=self._get_start_id(group_line_id,db_func_name_2)
#ref ID的SP固定从第一条开始跑
                start_id = 0
                kwargs["start_id"]=start_id
                kwargs["process_table"]=process_table
                kwargs["limit_count"]=limit_count

                if step_exe==0:
                    _logger.debug("group line : %s set step_2=%s,will skip"%(group_line_name,start_id))
                    continue

                sp_log_rec=self._get_sp_log_rec(group_log_rec.id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name_2)
                kwargs["sp_log_id"]=sp_log_rec.id
                root_vals={
                    "kwargs":kwargs
                }

                select_count_sql=group_line_vals.get("select_count_sql_2",False)
                if select_count_sql!=False:
                    script_env={}
                    script_env.update(kwargs)
                    eval_reulst=False
                    try:
                        eval_reulst=eval(select_count_sql,script_env)
                        kwargs["select_count_sql"]=eval_reulst
                    except:
                        _logger.error("calculate select_count_sql_2 param error")
                        traceback.print_exc()
                self.proc_tans_group_line_base(**root_vals)
            else:
                #ref 的存过程start_id 从0开始
                start_id=0
                #start_id=self._get_start_id(group_line_id,db_func_name_2)
                kwargs["start_id"]=start_id
                sp_log_rec=self._get_sp_log_rec(group_log_rec.id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name_2)
                kwargs["sp_log_id"]=sp_log_rec.id
                #不指定 specific_group_line 参数的情况下,直接执行
                root_vals={
                    "kwargs":kwargs
                }
                self.proc_tans_group_line_base(**root_vals)


        #执行db_func_name_3上面的函数
        for sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state in group_line_list:
            #函数2位空的情况,不进行调用,直接跳过,数据迁移程序存在这种现象,
            #每个表独立更新关联字段,写入正式库只使用一个group_line中的db_fun_name_2
            if is_empty_str(sap_log_id):
                _logger.debug("group line : %s has not get param sap_log_id,will skip "%(group_line_name,))
                continue
            if is_empty_str(db_func_name_3):
                _logger.debug("group line : %s has not set db_func_name_2,will skip ",(group_line_name,))
                continue

            step_exe=0

            #设定了需要指定项目的参数,没有传递 dict_group_line 则不进行任何操作
            if specific_group_line==1 and specific_group_line==None:
                _logger.debug("when json param specific_group_line is set to 1,param specific_group_line is needed")
                continue
                #只执行指定项目,dict_group_line中设定的项目才能执行
            if specific_group_line==1 and dict_group_line!=None and group_line_name not in dict_group_line:
                _logger.debug("group line : %s is not in dict_group_line,will skip",(group_line_name,))
                continue
            start_id=0
            kwargs={
                "sap_log_id":sap_log_id,
                "group_id":group_id,
                "group_line_id":group_line_id,
                "group_name":group_name,
                "group_line_name":group_line_name,
                "src_table_name":src_table_name,
                "dst_table_name":dst_table_name,
                "db_func_name":db_func_name_3,
                "process_table_name":dst_table_name,
                "start_id":start_id,
                }
            if specific_group_line==1 and dict_group_line!=None:
                group_line_vals=dict_group_line.get(group_line_name)
                # start_id=group_line_vals.get("start_id_3",0)
                step_exe=group_line_vals.get("step_3",0)
                process_table=group_line_vals.get("process_table_3",dst_table_name)
                limit_count=group_line_vals.get("limit_count_3",1000)
                # if start_id==0:
                #     start_id=self._get_start_id(group_line_id,db_func_name_3)
                # ref ID的SP固定从第一条开始跑
                start_id = 0
                kwargs["start_id"]=start_id
                kwargs["process_table"]=process_table
                kwargs["limit_count"]=limit_count

                if step_exe==0:
                    _logger.debug("group line : %s set step_3=%s,will skip"%(group_line_name,start_id))
                    continue

                sp_log_rec=self._get_sp_log_rec(group_log_rec.id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name_2)
                kwargs["sp_log_id"]=sp_log_rec.id
                root_vals={
                    "kwargs":kwargs
                }

                select_count_sql=group_line_vals.get("select_count_sql_3",False)
                if select_count_sql!=False:
                    script_env={}
                    script_env.update(kwargs)
                    eval_reulst=False
                    try:
                        eval_reulst=eval(select_count_sql,script_env)
                        kwargs["select_count_sql"]=eval_reulst
                    except:
                        _logger.error("calculate select_count_sql_3 param error")
                        traceback.print_exc()

                self.proc_tans_group_line_base(**root_vals)
            else:
                #start_id 从0 开始
                #start_id=self._get_start_id(group_line_id,db_func_name_3)
                start_id=0
                kwargs["start_id"]=start_id
                sp_log_rec=self._get_sp_log_rec(group_log_rec.id,group_name,group_line_name,group_id,group_line_id,sap_log_id,db_func_name_3)
                kwargs["sp_log_id"]=sp_log_rec.id
                #不指定 specific_group_line 参数的情况下,直接执行
                root_vals={
                    "kwargs":kwargs
                }
                self.proc_tans_group_line_base(**root_vals)


        #当前组处理完毕,写入组操作日志
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        group_log_vals={
            "end_time":end_time,
            "state":"success"
        }
        group_log_rec.write(group_log_vals)
        self.env.cr.commit()
        _logger.debug("group name is %s completed,group executed id is: %s" % (group_name, group_log_rec.id))


    @odoo_env
    def proc_group_line_list_update_miss(self, group_name):
        """
        处理所有
        :param group_name:
        :return:
        """
        group_line_list=self.env["iac.interface.temp.table.group.line"].search([('update_miss_flag','=','Y')])

        for group_line in group_line_list:
            if group_line.db_func_name_3==False:
                continue
            kwargs={
                "sap_log_id":group_line.group_linesap_log_id,
                "group_id":group_line.group_id.id,
                "group_line_id":group_line.group_line_id.id,
                "group_name":group_line.group_name,
                "group_line_name":group_line.group_line_name,
                "src_table_name":group_line.src_table_name,
                "dst_table_name":group_line.dst_table_name,
                "db_func_name":group_line.db_func_name_3,
                }
            root_vals={
                "kwargs":kwargs
            }

            self.proc_group_line_update_miss(**root_vals)
        _logger.debug("proc_group_line_list_update_miss execute completed")


    def proc_group_line_update_miss(self,  **kwargs):
        db_func_name=kwargs.get("kwargs").get("db_func_name")
        sap_log_id=kwargs.get("kwargs").get("sap_log_id")
        group_id=kwargs.get("kwargs").get("group_id")
        group_line_id=kwargs.get("kwargs").get("group_line_id")
        group_name=kwargs.get("kwargs").get("group_name")
        group_line_name=kwargs.get("kwargs").get("group_line_name")
        dst_table_name=kwargs.get("kwargs").get("dst_table_name")
        limit_count=1000

        select_count = "select count(*) from %s where miss_flag=1" % (dst_table_name,)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()


        record_count = record_count_result[0][0]
        if record_count==0:
            return

        page_list = self._get_page_list(record_count, limit_count)
        #设置表中的neeed_update_id 数值
        select_update_id="select nextval('need_update_id_seq')"
        self.env.cr.execute(select_update_id)
        result = self.env.cr.fetchall()
        need_update_id=result[0][0]

        start_id=0
        for offset_count in page_list:
            offset_count=0
            #输出日志
            sql_fun_text="select * from  ep_temp_master.sp_func_set_update_flag('%s',%s,%s) as (last_id int4)" %(dst_table_name,  limit_count, start_id)
            _logger.debug(sql_fun_text)


            #调用存储过程打need_update_id 标记
            self.env.cr.execute("select * from  "+db_func_name+"(%s,%s,%s) as (last_id int4)",
                (dst_table_name,  limit_count, start_id))

            result=self.env.cr.fetchall()
            start_id=result[0][0]
            self.env.cr.commit()

            #存储执行的sql语句
            self.env.cr.execute("INSERT INTO public.iac_job_func_call_log ( " \
                                "	group_id,                                 " \
                                "	group_line_id,                            " \
                                "	group_name,                               " \
                                "	group_line_name,                          " \
                                "	fun_call_text,                            " \
                                "	sap_log_id                                " \
                                ")                                            " \
                                "VALUES                                       " \
                                "	(%s ,%s ,%s ,%s ,%s ,%s);           ",
                                (group_id,group_line_id,group_name,group_line_name,sql_fun_text,sap_log_id))
            self.env.cr.commit()

        #调用存储过程处理miss_flag=1的数据,目前已经打上了need_update_id标记
        start_id=0
        for offset_count in page_list:
            offset_count=0
            #输出日志
            sql_fun_text="select * from  %s('%s',%s,%s) as (last_id int4)" \
                         " (v_last_id  int4,v_log_line_id int4,v_group_id int4,v_group_line_id int4,v_group_name varchar,v_group_line_name varchar,v_update_count int4,v_fail_count int4,v_miss_count int4)" %(db_func_name, need_update_id, limit_count, start_id)
            _logger.debug(sql_fun_text)


            #调用存储过程打need_update_id 标记
            self.env.cr.execute("select * from " + db_func_name + "(%s,%s,%s) as " \
                                " (v_last_id  int4,v_log_line_id int4,v_group_id int4,v_group_line_id int4,v_group_name varchar,v_group_line_name varchar,v_update_count int4,v_fail_count int4,v_miss_count int4)",
                                (need_update_id, limit_count, start_id))

            fun_result=self.env.cr.fetchall()
            self.env.cr.commit()
            if len(fun_result)==0:
                _logger.debug("func name is %s has no return"%(db_func_name,))
                continue

            for  v_last_id,v_log_line_id,v_group_id,v_group_line_id,v_group_name,v_group_line_name,v_update_count,v_fail_count,v_miss_count in fun_result:
                start_id = v_last_id

            #存储执行的sql语句
            self.env.cr.execute("INSERT INTO public.iac_job_func_call_log ( " \
                                "	group_id,                                 " \
                                "	group_line_id,                            " \
                                "	group_name,                               " \
                                "	group_line_name,                          " \
                                "	fun_call_text,                            " \
                                "	sap_log_id                                " \
                                ")                                            " \
                                "VALUES                                       " \
                                "	(%s ,%s ,%s ,%s ,%s ,%s);           ",
                                (group_id,group_line_id,group_name,group_line_name,sql_fun_text,sap_log_id))
            self.env.cr.commit()

        #miss_record_counts
        select_count = "select count(*) from %s where miss_flag=1" % (dst_table_name,)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()
        record_count = record_count_result[0][0]
        _logger.debug("group_line_name is ( %s ),group_line_id is ( %s ) execute completed,miss record count is %s" %(group_line_name,group_line_id,record_count))
        group_line=self.env["iac.interface.temp.table.group.line"].browse(group_line_id)
        group_line.write({"miss_record_counts":record_count})
        self.env.cr.commit()


    @api.model
    def process_timer_job(self, scheduler, timer_rec):
        job_para_map = {}
        job_para_map["replace_existing"]=True
        job_para_map["id"] = str(timer_rec.id)
        job_para_map["name"] = timer_rec.name
        model_name = timer_rec.model
        method_name = timer_rec.function
        if model_name==False or method_name==False:
            return
        model_obj = self.env[model_name]
        job_para_map["func"] = getattr(model_obj, method_name)
        job_para_map["trigger"] = timer_rec.trigger_type

        try:
            #cron_args_list=['year','month','day','week','day_of_week','hour','minute','second','start_date']
            #解析job的传入参数,传递给 schedular
            job_args_text=timer_rec.args
            if job_args_text!=False:
                job_args=json.loads(job_args_text)
                job_para_map["kwargs"]=job_args

            if timer_rec.trigger_type == 'interval':
                job_para_map[timer_rec.interval_type] = timer_rec.interval_number
                scheduler.add_job(**job_para_map)
                return
            if timer_rec.trigger_type == 'date':
                job_para_map["run_date"] = timer_rec.run_date
                scheduler.add_job(**job_para_map)
                return
            if timer_rec.trigger_type=='cron':
                try:
                    cron_args_list=['year','month','day','week','day_of_week','hour','minute','second','start_date']
                    cron_text=timer_rec.cron_text
                    cron_json=json.loads(cron_text)
                    for json_key in cron_json:
                        if json_key in cron_args_list:
                            job_para_map[json_key]=cron_json.get(json_key)
                    scheduler.add_job(**job_para_map)
                except:
                    err_msg="Job cron_args is not valid,Job id is %s,Job name is %s;exception info is: %s" %(timer_rec.id,timer_rec.name,traceback.format_exc(),)
                    _logger.error(err_msg)
                return
        except:
            err_msg="Job args is not valid,Job id is %s,Job name is %s;exception info is: %s" %(timer_rec.id,timer_rec.name,traceback.format_exc(),)
            _logger.error(err_msg)



    @api.model
    def _setup_complete(self):
        """
        当前模型加载完毕根据数据库中的配置设置定时任务
        :return:
        """
        super(IacJobGroupMaster, self)._setup_complete()
        conf_obj=tools.config
        scheduler=interface_timer.scheduler
        #scheduler 加载odoo环境
        scheduler.env=self.env
        start_timer_job=int(conf_obj.get("start_timer_job",0))
        _logger.debug("iac.job.group.master _setup_complete has invoked")
        _logger.debug("Server Config Param start_timer_job is %s",start_timer_job )
        if start_timer_job==1:
            #将所有job注入scheduler
            try:

                timer_rs=self.env["iac.interface.timer"].sudo().search([('job_active','=',True)])
                for timer_rec in timer_rs:
                    self.process_timer_job(scheduler,timer_rec)
                    _logger.debug("job %s has added to job scheduler" %(timer_rec.name,))
                _logger.debug("Scheduler state is %s" %(scheduler.state,))
                if scheduler.state!=1:
                    scheduler.start()
                    _logger.debug("Scheduler start has invoked in iac.job.group.master  _setup_complete" )
                _logger.debug("Scheduler has in _setup_complete Line num is 733")
            except:
                _logger.debug("Scheduler has in _setup_complete Line num is 735  sssss")
                _logger.error(traceback.format_exc())
                traceback.print_exc()