# -*- coding: utf-8 -*-
from odoo import models, fields, api,odoo_env
from apscheduler.schedulers.background import BackgroundScheduler
from odoo.modules.registry import RegistryManager
import datetime
import logging
import traceback
import odoo
import threading,time
from odoo.odoo_env import odoo_env
_logger = logging.getLogger(__name__)



class IacJobTransGroupMaster(models.TransientModel):
    _name="iac.job.trans.group.master"


    def _get_page_list(self, record_count, limit_count):
        page_list = []
        if record_count <= limit_count:
            page_list.append(0)
            return page_list

        #计算分页偏移量
        offset_count = 0
        while offset_count <= record_count:
            page_list.append(offset_count)
            offset_count = offset_count + limit_count
        return page_list;

    def _get_group_log(self,group_id):
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
        group_rec=self.env["iac.interface.temp.table.group"].browse(group_id)
        group_log_rec=self.env["iac.interface.temp.table.group.exe"].search([('state','=','processing'),('group_id','=','group_id')],order='id desc',limit=1)
        if not group_log_rec.exists():
            group_log_vals={
                "group_code":group_rec.code,
                "group_name":group_rec.name,
                "group_id":group_id,
                "start_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state":"processing",
                }
            group_log_rec=self.env["iac.interface.temp.table.group.exe"].create(group_log_vals)

        group_line_list=self.env["iac.interface.temp.table.group.line"].search([('group_id','=',group_id)])
        for group_line_rec in group_line_list:
            #判定明细条目是否已经存在
            group_line_log_rec=self.env["iac.interface.temp.table.group.exe.line"].search([('group_id','=',group_id),('group_line_id','=',group_line_rec.id),('state','=','processing')],order='id desc',limit=1)
            if not group_line_log_rec.exists():
                group_line_log_vals={
                    "group_code":group_rec.code,
                    "group_name":group_rec.name,
                    "group_id":group_rec.id,
                    "group_line_id":group_line_rec.id,

                    "group_line_name":group_line_rec.group_line_name,
                    "start_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "group_exe_id":group_log_rec.id,
                    "state":"processing"
                }
                group_line_log_rec=self.env["iac.interface.temp.table.group.exe.line"].create(group_line_log_vals)


        self.env.cr.commit()
        return group_log_rec



    def proc_tans_group_line_base(self, **kwargs):
        """
        处理一个组条目的函数调用操作,
        同时写入组条目的日志和多次数据函数的操作日志
        首先要从目标表中获取
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
        db_func_name=kwargs.get("kwargs").get("db_func_name")
        sap_log_id=kwargs.get("kwargs").get("sap_log_id")
        group_id=kwargs.get("kwargs").get("group_id")
        group_line_id=kwargs.get("kwargs").get("group_line_id")
        group_name=kwargs.get("kwargs").get("group_name")
        group_line_name=kwargs.get("kwargs").get("group_line_name")
        src_table_name=kwargs.get("kwargs").get("src_table_name")
        start_id=kwargs.get("kwargs").get("start_id")
        limit_count = 1000
        #分页数组，存储sql 语句中的offset 参数
        page_list = []



        select_count = "select count(*) from %s where sap_log_id='%s' and id >%s" % (src_table_name,sap_log_id,start_id)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()

        record_count = record_count_result[0][0]
        src_table_name=kwargs.get("kwargs").get("src_table_name")
        if src_table_name=="ep_temp_master.material_description":
            pass

        #更新sap接口日志表的状态为 PROCESS


        self.env.cr.execute("update ep_temp_master.extractlog                        " \
                   " set extractstatus='ODOO_PROCESS' where extractwmid=%s ",
                   (sap_log_id,))
        self.env.cr.commit()
        #获取目标表的总记录数量
        page_list = self._get_page_list(record_count, limit_count)

        _logger.debug("group line name is ( %s ) ,db_func_name is ( %s ),sap_log_id is ( %s ) will start"%(group_line_name,db_func_name,sap_log_id))

        #group_id=kwargs.get("group_id")
        #group_line_id=kwargs.get("group_line_id")
        #便利分页数组调用数据库中的存储过程完成任务
        miss_count_sum = 0
        update_count_sum = 0
        fail_count_sum = 0
        group_line_log_rec=None
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
                _logger.debug("func name is %s has no return"%(db_func_name,))
                continue
            for  v_last_id,v_log_line_id,v_group_id,v_group_line_id,v_group_name,v_group_line_name,v_update_count,v_fail_count,v_miss_count in fun_result:
                miss_count_sum += v_miss_count
                update_count_sum += v_update_count
                fail_count_sum +=  v_fail_count
                _logger.debug("executing db func %s ,updated records:%s,missed records:%s,fail records:%s" % (
                    db_func_name, v_update_count, v_miss_count, v_fail_count))
                start_id=v_last_id
                if v_log_line_id!=False:
                    group_line_log_rec=self.env["iac.interface.temp.table.group.exe.line"].browse(v_log_line_id)
                    group_line_log_vals={
                        "last_id":v_last_id,
                        "seq_id":v_last_id,
                        "update_record_counts":update_count_sum,
                        "fail_record_counts":fail_count_sum,
                        "miss_record_counts":miss_count_sum,
                    }
                    group_line_log_rec.write(group_line_log_vals)
                    self.env.cr.commit()
                    _logger.debug("execute db func %s completed,updated records:%s,missed records:%s,failed records:%s" % (
                        db_func_name, update_count_sum, miss_count_sum, fail_count_sum))

        #所有操作都完成的情况下,需要更新完成的时间点和组条目状态
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        group_line_log_vals={
            "last_id":0,
            "end_time":end_time,
            "state":"success"
            }
        group_line_log_rec.write(group_line_log_vals)

        self.env.cr.execute("update ep_temp_master.extractlog                        " \
                            " set extractstatus='STEP2DONE' where extractwmid=%s ",
                            (sap_log_id,))
        self.env.cr.commit()


    @odoo_env
    def proc_trans_group_base(self, group_name,step_1=0,step_2=0,start_id_step_1=0,start_id_step_2=0):
        """
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

        group_log_rec=self._get_group_log(group_line_list[0][1])

        #开始多线程更新数据执行每个group_line的更新操作，实际上是执行db_func_name_1上面的函数
        thread_list=[]
        for sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state in group_line_list:
            kwargs={
                "sap_log_id":sap_log_id,
                "group_id":group_id,
                "group_line_id":group_line_id,
                "group_name":group_name,
                "group_line_name":group_line_name,
                "src_table_name":src_table_name,
                "dst_table_name":dst_table_name,
                "db_func_name":db_func_name_1,
                "start_id":start_id_step_1,
            }
            root_vals={
                "kwargs":kwargs
            }
            if step_1==0:
                continue
            self.proc_tans_group_line_base(**root_vals)



        #开始多线程更新数据执行每个group_line的更新操作，实际上是执行db_func_name_2上面的函数
        thread_list=[]
        for sap_log_id, group_id, group_line_id,group_name, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2,db_func_name_3,process_state in group_line_list:
            #函数2位空的情况,不进行调用,直接跳过,数据迁移程序存在这种现象,
            #每个表独立更新关联字段,写入正式库只使用一个group_line中的db_fun_name_2
            if db_func_name_2==False or db_func_name_2==None:
                continue
            kwargs={
                "sap_log_id":sap_log_id,
                "group_id":group_id,
                "group_line_id":group_line_id,
                "group_name":group_name,
                "group_line_name":group_line_name,
                "src_table_name":src_table_name,
                "dst_table_name":dst_table_name,
                "db_func_name":db_func_name_2,
                "start_id":start_id_step_2,
                }
            root_vals={
                "kwargs":kwargs
            }

            if step_2==0:
                continue
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


        select_count = "select count(*) from %s where miss_flag=1" % (dst_table_name,)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()


        record_count = record_count_result[0][0]
        if record_count==0:
            return
        limit_count=1000
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


