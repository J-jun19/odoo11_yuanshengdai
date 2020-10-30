# -*- coding: utf-8 -*-
from odoo import models, fields, api
from apscheduler.schedulers.background import BackgroundScheduler
from odoo.modules.registry import RegistryManager
import datetime
import logging
import traceback
import odoo
import threading
import json
from odoo import odoo_env
from odoo.odoo_env import odoo_env
from odoo.exceptions import UserError, ValidationError
from odoo.models import SUPERUSER_ID
from odoo import tools

from apscheduler.events import (
    SchedulerEvent, JobEvent, JobSubmissionEvent, EVENT_SCHEDULER_START, EVENT_SCHEDULER_SHUTDOWN,
    EVENT_JOBSTORE_ADDED, EVENT_JOBSTORE_REMOVED, EVENT_ALL, EVENT_JOB_MODIFIED, EVENT_JOB_REMOVED,
    EVENT_JOB_ADDED, EVENT_EXECUTOR_ADDED, EVENT_EXECUTOR_REMOVED, EVENT_ALL_JOBS_REMOVED,
    EVENT_JOB_SUBMITTED, EVENT_JOB_MAX_INSTANCES, EVENT_SCHEDULER_RESUMED, EVENT_SCHEDULER_PAUSED,
    EVENT_JOB_EXECUTED,EVENT_JOB_ERROR)


_logger = logging.getLogger(__name__)

class IacInterfaceTimer(models.Model):
    _name = "iac.interface.timer"

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    job_active = fields.Boolean(default=True)
    trigger_type = fields.Selection([('date', 'Trigger Once On Specific time'),
                                     ('interval', 'Trigger At The Interval Time'),
                                     ('cron', 'Trigger Use cron args'),
                                    ],
                                    string='Trigger Type', default='interval')
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([('seconds', 'Seconds'),
                                      ('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days'),
                                     ],
                                     string='Interval Unit', default='hours')
    numbercall = fields.Integer(string='Number of Calls', default=1,
                                help='How many times the method is called,\na negative number indicates no limit.')
    doall = fields.Boolean(string='Repeat Missed',
                           help="Specify if missed occurrences should be executed when the server restarts.")
    nextcall = fields.Datetime(string='Next Execution Date', default=fields.Datetime.now,
                               help="Next planned execution date for this job.")
    model = fields.Char(string='Object',
                        help="Model name on which the method to be called is located, e.g. 'res.partner'.")
    function = fields.Char(string='Method', help="Name of the method to be called when this job is processed.")
    args = fields.Text(string='Arguments', help="Arguments to be passed to the method, e.g. (uid,).")
    run_date = fields.Datetime(string='Run Date', default=fields.Datetime.now,
                               help="When trigger_type is date,specific the first run time of job .")
    priority = fields.Integer(default=5,
                              help='The priority of the job, as an integer: 0 means higher priority, 10 means lower priority.')
    cron_text=fields.Text(string='Cron Args')
    job_exe_ids=fields.One2many('iac.interface.timer.line','job_id',string='Job Executed History')



    @api.multi
    def write(self,vals):
        result=super(IacInterfaceTimer,self).write(vals)
        self._validate_reocord()
        return result

    @api.model
    def create(self,vals):
        result=super(IacInterfaceTimer,self).create(vals)
        result._validate_reocord()
        return result

    def _validate_reocord(self):
        """
        校验当前记录信息是否合法
        """
        try:
            if self.args!=False:
                kwargs=json.loads(self.args)
        except:
            traceback.print_exc()
            raise UserError(u"解析参数 Arguments 发生异常,不是合法的JSON字串;%s"%(traceback.format_exc()))

        if self.trigger_type=='cron':
            if self.cron_text==False:
                raise UserError("Cron Args can be null when trigger type is cron")
            try:
                if self.cron_text!=False:
                    cron_args=json.loads(self.cron_text)
            except:
                traceback.print_exc()
                raise UserError(u"解析参数Cron Args 发生异常,不是合法的JSON字串;%s"%(traceback.format_exc()))


    @api.multi
    def button_reload_job(self):
        """
        从数据库中重新加载job 的设定信息
        """
        conf_obj=tools.config
        start_timer_job=int(conf_obj.get("start_timer_job",0))
        if start_timer_job==0:
            raise UserError("start_timer_job is 0 in conf file,Reload Job is not allowed")
        if self.job_active==False:
            try:
                scheduler.remove_job(str(self.id))
            except:
                logging.error(traceback.format_exc())
                traceback.print_exc()
        else:
            if start_timer_job==1:
                self.env["iac.job.group.master"].process_timer_job(scheduler,self)
                if scheduler.state !=1:
                    scheduler.start()


    @api.multi
    def method_direct_trigger(self):
        model_name = self.model
        method_name = self.function
        model_obj = self.env[model_name]
        #scheduler=BackgroundScheduler()
        run_date_time=datetime.datetime.now()+datetime.timedelta(seconds=5)
        kwargs=None
        try:
            if self.args!=False:
                kwargs=json.loads(self.args)
        except:
            traceback.print_exc()
            raise UserError(u"解析参数发生异常,不是合法的JSON字串;%s"%(traceback.format_exc()))
        job_para_map = {
            "replace_existing":True,
            "id":str(self.id),
            "name":self.name+'_run_once',
            "func":getattr(model_obj, method_name),
            "trigger":"date",
            "run_date":run_date_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if kwargs!=None:
            job_para_map["kwargs"]=kwargs
        scheduler.add_job(**job_para_map)
        if scheduler.state !=1:
            scheduler.start()



        #model_name = self.model
        #method_name = self.function
        #model_obj = self.env[model_name]
        #scheduler=BackgroundScheduler()
        #start_date=datetime.datetime.now()+datetime.timedelta(seconds=5)
        #job_para_map = {
        #    "replace_existing":True,
        #    "id":str(self.id)+'_run_once',
        #    "name":self.name+'_run_once',
        #    "func":getattr(model_obj, method_name),
        #    "trigger":"cron",
        #    "start_date":start_date.strftime("%Y-%m-%d %H:%M:%S"),
        #    }
#
        #if self.trigger_type=='cron':
        #    cron_args_list=['year','month','day','week','day_of_week','hour','minute','second','start_date']
        #    cron_text=self.cron_text
        #    try:
        #        cron_json=json.loads(cron_text)
        #        for json_key in cron_json:
        #            if json_key in cron_args_list:
        #                job_para_map[json_key]=cron_json.get(json_key)
        #        scheduler.add_job(**job_para_map)
        #        scheduler.start()
        #    except:
        #        traceback.print_exc()


class IacInterfaceTimerLine(models.Model):
    _name = "iac.interface.timer.line"
    _order="executed_time desc"
    job_id = fields.Many2one('iac.interface.timer', string='Job Timer')
    job_name=fields.Char(string='Job Name')
    state = fields.Selection([('job_start', 'Job Start'),
                              ('job_success', 'Job Success'),
                              ('job_fail', 'Job Fail'),
                             ],
                                  string='Run Result', default='fail')
    executed_time = fields.Datetime(string='Job Execute Time')
    job_err_msg=fields.Text(string='Job Exception Msg')

class IacInterfaceTimerJob(models.Model):
    _inherit = "iac.interface.timer"
    """
    asn
    asnjit
    gr
    info
    iqcdata
    master
    master_plm
    part
    po
    vendor
    """




    def proc_trans_group_asn(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'ASN')
        except:
            traceback.print_exc()
        cr.close()


    def proc_trans_group_asnjit(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'ASNJIT')
        except:
            traceback.print_exc()
        cr.close()

    def proc_trans_group_gr(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'GR')
        except:
            traceback.print_exc()
        cr.close()


    def proc_trans_group_info(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'INFO')
        except:
            traceback.print_exc()
        cr.close()

    def proc_trans_group_iqcdata(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'IQCDATA')
        except:
            traceback.print_exc()
        cr.close()


    def proc_trans_group_master(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'MASTER')
        except:
            traceback.print_exc()
        cr.close()


    def proc_trans_group_master_plm(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'MASTER_PLM')
        except:
            traceback.print_exc()
        cr.close()


    def proc_trans_group_part(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'PART')
        except:
            traceback.print_exc()
        cr.close()

    def proc_trans_group_po(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'PO')
        except:
            traceback.print_exc()
        cr.close()


    def get_local_cr(self):
        db_name = self.env.registry.db_name
        registry = RegistryManager.get(db_name)
        cr = registry.cursor()
        return cr

    def proc_trans_group_vendor(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'VENDOR')
        except:
            traceback.print_exc()
        cr.close()


    def proc_trans_group_forecast(self):
        cr=self.get_local_cr()
        try:
            self.proc_trans_group_base(cr,'FORECAST')
        except:
            traceback.print_exc()
        cr.close()


    def proc_get_page_list(self, record_count, limit_count):
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

    def proc_tans_group_line_base(self, cr, group_id, group_name, group_line_id, group_line_name, sap_log_id,
                                  table_name, db_func_name):
        """
        处理一个组条目的数据导入操作,
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
        limit_count = 1000
        #分页数组，存储sql 语句中的offset 参数
        page_list = []

        select_count = "select count(*) from %s" % (table_name,)
        cr.execute(select_count)
        record_count_result = cr.fetchall()

        record_count = record_count_result[0][0]

        #更新sap接口日志表的状态为 PROCESS
        cr.execute("update ep_temp_master.extractlog                        " \
                   " set extractstatus='ODOO_PROCESS' where extractwmid=%s ",
                   (sap_log_id,))

        #获取目标表的总记录数量
        page_list = self.proc_get_page_list(record_count, limit_count)

        #便利分页数组调用数据库中的存储过程完成任务
        insert_count_sum = 0
        update_count_sum = 0
        fail_count_sum = 0
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for offset_count in page_list:
            sql_text="select * from " + db_func_name + "(%s,%s,%s,%s,%s)" % (sap_log_id, group_id, group_line_id, limit_count, offset_count)
            _logger.debug(sql_text)
            cr.execute("select * from " + db_func_name + "(%s,%s,%s,%s,%s)",
                       (sap_log_id, group_id, group_line_id, limit_count, offset_count))
            for insert_count, update_count, fail_count in cr.fetchall():
                insert_count_sum = insert_count_sum + insert_count
                update_count_sum = update_count_sum + update_count
                fail_count_sum = fail_count_sum + fail_count
                _logger.debug("executing db func %s ,insert records:%s,update records:%s,fail records:%s" % (
                db_func_name, insert_count, update_count, fail_count))
            cr.commit()
        _logger.debug("execute db func %s completed,inserted records:%s,updated records:%s,failed records:%s" % (
        db_func_name, insert_count_sum, update_count_sum, fail_count_sum))
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #操作完成写入组条目日志
        cr.execute("INSERT INTO \"public\".iac_interface_temp_table_group_exe_line (  " \
                   "	group_id,                                                    " \
                   "	group_line_id,                                               " \
                   "	group_name,                                                  " \
                   "	group_line_name,                                             " \
                   "	sap_log_id,                                                  " \
                   "	start_time,                                                  " \
                   "	end_time,                                                    " \
                   "	insert_record_counts,                                        " \
                   "	update_record_counts,                                        " \
                   "	fail_record_counts,                                    " \
                   "	store_proc_name                                    " \
                   ")                                                               " \
                   "VALUES                                                          " \
                   "	(                                                            " \
                   "		%s,                                              " \
                   "		%s,                                         " \
                   "		%s,                                            " \
                   "		%s,                                       " \
                   "		%s,                                            " \
                   "		to_timestamp(%s,'yyyy-MM-dd hh24:mi:ss'),                                            " \
                   "		to_timestamp(%s,'yyyy-MM-dd hh24:mi:ss'),                                              " \
                   "		%s,                                          " \
                   "		%s,                                          " \
                   "		%s,                                             " \
                   "		%s                                             " \
                   "	);                                                           ",
                   (group_id, group_line_id, group_name, group_line_name, sap_log_id, start_time,
                    end_time, insert_count_sum, update_count_sum, fail_count_sum, db_func_name))
        cr.commit()


    def proc_trans_group_base(self, cr,group_name):
        """
        传入组名参数,进行组数据传输处理
        :param group_name:
        :return:
        """
        #判断SAP系统是否完成数据导入
        cr.execute(
            "select o_group_id group_id,o_group_state group_state from ep_temp_master.proc_query_group_state(%s)",
            (group_name,))

        #遍历数据集，实际上只返回一条记录
        for group_id, group_state in cr.fetchall():
            if group_id == 0 or group_state == 0:
                return
                #排除异常后,处理数据导入，遍历组条目信息
            start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cr.execute("SELECT                                                " \
                       "	extractwmid sap_log_id,                            " \
                       "	line. ID group_line_id,                            " \
                       "	extractname group_line_name,                       " \
                       "	src_table_name,                                    " \
                       "	dst_table_name,                                    " \
                       "	line.db_func_name_1,                               " \
                       "	line.db_func_name_2                                " \
                       "FROM                                                  " \
                       "	ep_temp_master.extractlog el,                      " \
                       "	public.iac_interface_temp_table_group_line line    " \
                       "WHERE                                                 " \
                       "	( el.extractstatus = 'STEP1DONE' OR  el.extractstatus = 'ODOO_PROCESS' )                    " \
                       "AND line.group_id = %s                                " \
                       "AND el.extractname = line.group_line_name             " \
                       "AND el.extractname IN (                               " \
                       "	SELECT                                             " \
                       "		eg.extractname                                 " \
                       "	FROM                                               " \
                       "		ep_temp_master.extractgroup eg                 " \
                       "	WHERE                                              " \
                       "		eg.extractgroup = %s )                      "
                , (group_id, group_name,))
            group_line_list = cr.fetchall()
            thread_list=[]
            for sap_log_id, group_line_id, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2 in group_line_list:
                self.proc_tans_group_line_base(cr, group_id, group_name, group_line_id, group_line_name, sap_log_id,
                                               src_table_name, db_func_name_1)


            for thread in thread_list:
                thread.join()

            for sap_log_id, group_line_id, group_line_name, src_table_name, dst_table_name, db_func_name_1, db_func_name_2 in group_line_list:
                self.proc_tans_group_line_base(cr, group_id, group_name, group_line_id, group_line_name, sap_log_id,
                                               src_table_name, db_func_name_2)



                #当前组处理完毕,写入组操作日志
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            #写入组操作日志
            cr.execute("select ep_temp_master.write_group_proc_log(%s,%s,%s,%s)",
                       (group_name, group_id, start_time, end_time))
            group_exe_id_result = cr.fetchone()
            cr.commit()

        _logger.debug("group name is %s completed,group executed id is: %s" % (group_name, group_exe_id_result[0]))


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
        if timer_rec.trigger_type == 'interval':
            job_para_map[timer_rec.interval_type] = timer_rec.interval_number
        if timer_rec.trigger_type == 'date':
            job_para_map["run_date"] = timer_rec.run_date
        scheduler.add_job(**job_para_map)

    def re_update_table_list_ref(self):
        """
        重新更新表关联
        1 从group_line中获取全部的数据表
        2 遍历数据表判断数据表种的need_re_update值是否大于0,大于0就进行re_update
        """
        cr = self.get_local_cr()
        try:
            cr.execute("SELECT                                                " \
                       "	line.group_id,                                     " \
                       "  gp.\"name\" group_name,                               " \
                       "	line.ID group_line_id,                             " \
                       "	line.group_line_name,                              " \
                       "	line.dst_table_name,                               " \
                       "	line.db_func_name_3                                " \
                       " FROM                                                  " \
                       "	\"public\".iac_interface_temp_table_group_line line, " \
                       "  \"public\".iac_interface_temp_table_group gp          " \
                       "where line.group_id=gp.id                               "\
                       "ORDER BY                                              " \
                       "	line.group_id,                                     " \
                       "	line.ID                                            ")
            group_line_list=[]
            group_line_list=cr.fetchall()
            for group_id, group_name, group_line_id, group_line_name, dst_table_name, db_fun_name_3 in group_line_list:
                self.re_update_table_ref(cr, group_id, group_name, group_line_id, group_line_name, dst_table_name,
                                         db_fun_name_3)
        except:
            traceback.print_exc()
        cr.close()

    def re_update_table_ref(self, cr, group_id, group_name, group_line_id, group_line_name, table_name, db_fun_name):
        """
        处理一张表的更新关联字段
        :param cr:
        :param group_id:
        :param group_name:
        :param group_line_id:
        :param group_line_name:
        :param table_name:
        :param db_fun_name_3:
        :return:
        """


        #设定默认记录分页记录数量
        limit_count = 1000
        #分页数组，存储sql 语句中的offset 参数
        page_list = []

        #获取唯一序列id 作为 need_update_id
        need_update_id=0
        cr.execute("select nextval('ep_temp_master.need_update_id_seq')")
        result=cr.fetchall()
        need_update_id=result[0][0]

        #获取need_re_update>0的所有记录数量
        select_count = "select count(*) from %s where need_re_update>0" % (table_name,)
        cr.execute(select_count)
        record_count_result = cr.fetchall()
        record_count = record_count_result[0][0]

        #遍历所有need_re_update的数据,为这些记录设置 need_update_id 值
        if record_count==0:
            _logger.debug("table name is ( %s ) no record need to be update ref ,re update job will quit." % (table_name,))
            return


        #获取目标表的总记录数量
        page_list = self.proc_get_page_list(record_count, limit_count)

        #为数据表更新need_update_id值
        #每次调用的参数都是limit_count=1000
        for offset_count in page_list:
            cr.execute("select * from ep_temp_master.proc_locate_table_update_ref_record_1(%s,%s,%s,%s)",
                       (table_name,need_update_id, limit_count, offset_count))
            cr.commit()
            _logger.debug("ep_temp_master.proc_locate_table_update_ref_record_1 update table ( %s ); set need_reupdate_id is ( %s ); " \
                          "limit value is ( %s );offset value is ( %s ) " %(table_name,need_update_id,limit_count,offset_count)
            )

        #为数据表更新need_re_update值为0
        #每次调用的参数都是limit_count=1000
        for offset_count in page_list:
            cr.execute("select * from ep_temp_master.proc_locate_table_update_ref_record_2(%s,%s,%s,%s)",
                       (table_name,need_update_id, limit_count, offset_count))
            cr.commit()
            _logger.debug(
                "ep_temp_master.proc_locate_table_update_ref_record_2 update table ( %s ); set need_reupdate_id is ( %s ); " \
                "limit value is ( %s );offset value is ( %s ) " % (table_name, need_update_id, limit_count, offset_count)
            )

        #便利分页数组调用数据库中的存储过程完成任务
        insert_count_sum = 0
        update_count_sum = 0
        fail_count_sum = 0
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #每次调用的参数都是limit_count=1000
        for offset_count in page_list:
            cr.execute("select * from " + db_fun_name + "(%s,%s,%s,%s,%s,%s)",
                       ('',need_update_id, group_id, group_line_id, limit_count, offset_count))
            for insert_count, update_count, fail_count in cr.fetchall():
                insert_count_sum = insert_count_sum + insert_count
                update_count_sum = update_count_sum + update_count
                fail_count_sum = fail_count_sum + fail_count
                _logger.debug("update table ( %s ) ref by executing db func %s ,insert records:%s,update records:%s,fail records:%s" % (
                table_name,db_fun_name, insert_count, update_count, fail_count))
            cr.commit()
        _logger.debug("update table ( %s ) ref by execute db func %s completed,inserted records:%s,updated records:%s,failed records:%s" % (
        table_name,db_fun_name, insert_count_sum, update_count_sum, fail_count_sum))
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #操作完成写入组条目日志
        cr.execute("INSERT INTO \"public\".iac_interface_temp_table_group_exe_line (  " \
                   "	group_id,                                                    " \
                   "	group_line_id,                                               " \
                   "	group_name,                                                  " \
                   "	group_line_name,                                             " \
                   "	start_time,                                                  " \
                   "	end_time,                                                    " \
                   "	insert_record_counts,                                        " \
                   "	update_record_counts,                                        " \
                   "	fail_record_counts,                                    " \
                   "	store_proc_name                                    " \
                   ")                                                               " \
                   "VALUES                                                          " \
                   "	(                                                            " \
                   "		%s,                                              " \
                   "		%s,                                         " \
                   "		%s,                                            " \
                   "		%s,                                       " \
                   "		to_timestamp(%s,'yyyy-MM-dd hh24:mi:ss'),                                            " \
                   "		to_timestamp(%s,'yyyy-MM-dd hh24:mi:ss'),                                              " \
                   "		%s,                                          " \
                   "		%s,                                          " \
                   "		%s,                                             " \
                   "		%s                                             " \
                   "	)                                                           ",
                   (group_id, group_line_id, group_name, group_line_name, start_time, end_time, insert_count_sum,
                    update_count_sum, fail_count_sum, db_fun_name))
        cr.commit()

    @odoo_env
    def proc_test_env_job(self):
        #file_rec=self.env["muk_dms.file"].browse(121)
        #new_fiel_rec=file_rec.copy()
        #mail_task_vals={
        #    "object_id":2947,
        #    "template_id":"oscg_vendor.vendor_register_supplier_email"
        #}
        #self.env["iac.mail.task"].add_mail_task(**mail_task_vals)
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print "proc_test_env_job has invoked"
        #raise Exception("This test Exception")
        #rfq_line_list=self.env["iac.rfq"].search([])
        #for rfq_line in rfq_line_list:
        #    print rfq_line.id


    @odoo_env
    def proc_test_send_mail_job(self):
        """
        测试发送邮件
        :return:
        """
        mail_task_vals={
            "object_id":126,
            "template_id":"oscg_rfq.iac_rfq_quote_as_email"
        }
        self.env["iac.mail.task"].add_mail_task(**mail_task_vals)

    @odoo_env
    def proc_test_env_with_param_job(self,sap_log_id):
        rfq_line_list=self.env["iac.rfq"].search([])
        for rfq_line in rfq_line_list:
            print rfq_line.id


    @api.model
    def _setup_complete(self):
        """
        当前模型加载完毕根据数据库中的配置设置定时任务
        :return:
        """
        super(IacInterfaceTimerJob, self)._setup_complete()

        #将所有job注入scheduler
        # try:
        #     scheduler = BackgroundScheduler()
        #     timer_rs=self.search([('job_active','=',True)])
        #     for timer_rec in timer_rs:
        #         self.process_timer_job(scheduler,timer_rec)
        #     scheduler.start()
        # except:
        #     traceback.print_exc()

        #mail_template_rs=self.env["mail.template"]
        #mail_vals={"subject":"this is a test mail",
        #           "body_html":"<p>this is a mail body",
        #           "email_from":"lwtrante@126.com",
        #           "email_to":"wantao.li@oscg.biz",
        #           "model":"vendor"
        #           }
        ##mail_rec=mail_template_rs.create(mail_vals)
        #mail_rec=self.env["mail.template"].browse(36)
        #mail_rec.send_mail(24864,force_send=True)
        #_logger.debug("send email has no error")
        #self.proc_trans_group_base('INFO')
        #self.re_update_table_list_ref()


scheduler = BackgroundScheduler()

def my_listener(event):
    """
    EVENT_SCHEDULER_START
    EVENT_SCHEDULER_SHUTDOWN
    EVENT_JOBSTORE_ADDED
    EVENT_JOBSTORE_REMOVED
    EVENT_ALL
    EVENT_JOB_MODIFIED
    EVENT_JOB_REMOVED
    EVENT_JOB_ADDED
    EVENT_EXECUTOR_ADDED
    EVENT_EXECUTOR_REMOVED
    EVENT_ALL_JOBS_REMOVED
    EVENT_JOB_SUBMITTED
    EVENT_JOB_MAX_INSTANCES
    EVENT_SCHEDULER_RESUMED
    EVENT_SCHEDULER_PAUSED
    :param event:
    :return:
    """
    if event.code==EVENT_SCHEDULER_START:
        _logger.debug("EVENT_SCHEDULER_START")
    elif event.code==EVENT_SCHEDULER_SHUTDOWN:
        _logger.debug("EVENT_SCHEDULER_SHUTDOWN")
    elif event.code==EVENT_JOB_MODIFIED:
        _logger.debug("EVENT_JOB_MODIFIED")
    elif event.code==EVENT_JOB_REMOVED:
        _logger.debug("EVENT_JOB_REMOVED")
    elif event.code==EVENT_JOB_ADDED:
        _logger.debug("EVENT_JOB_ADDED")
    elif event.code==EVENT_EXECUTOR_ADDED:
        _logger.debug("EVENT_EXECUTOR_ADDED")
    elif event.code==EVENT_EXECUTOR_REMOVED:
        _logger.debug("EVENT_EXECUTOR_REMOVED")
    elif event.code==EVENT_JOB_ERROR:
        #这个分支才考虑exception exception
        _logger.debug("EVENT_JOB_ERROR")
        job_exe_vals={
            "job_id":int(event.job_id),
            "state":"job_fail",
            "executed_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "job_err_msg":event.exception
        }
        save_job_executed_data(job_exe_vals)
    elif event.code==EVENT_JOB_SUBMITTED:
        #print 'EVENT_JOB_SUBMITTED'
        _logger.debug("EVENT_JOB_SUBMITTED")
        job_exe_vals={
            "job_id":int(event.job_id),
            "state":"job_start",
            "executed_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_job_executed_data(job_exe_vals)
    elif event.code==EVENT_JOB_EXECUTED:
        _logger.debug("EVENT_JOB_EXECUTED")
        job_exe_vals={
            "job_id":int(event.job_id),
            "state":"job_success",
            "executed_time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_job_executed_data(job_exe_vals)


    elif event.code==EVENT_JOBSTORE_ADDED:
        #print 'EVENT_JOBSTORE_ADDED'
        _logger.debug("EVENT_JOBSTORE_ADDED")
    else:
        _logger.debug("UNFOUND JOB EVENT %s" %(event.code,))

def save_job_executed_data(vals):
    db_name = scheduler.env.registry.db_name
    db = odoo.sql_db.db_connect(db_name)
    threading.current_thread().dbname = db_name
    cr = db.cursor()
    with api.Environment.manage():
        try:
            env=api.Environment(cr, SUPERUSER_ID, {})
            job_exe_vals={}
            job_exe_vals.update(vals)
            job_rec=env["iac.interface.timer"].browse(vals.get("job_id"))
            if not job_rec.exists():
                _logger.error("can not found record wtih job_id %s "%(vals.get("job_id"),))
            else:
                job_exe_vals["job_name"]=job_rec.name
                job_exe_rec=env["iac.interface.timer.line"].create(job_exe_vals)
        except:
            traceback.print_exc()
    cr.commit()
    cr.close()

scheduler.add_listener(my_listener)
