# -*- coding: utf-8 -*-
from odoo import models, fields, api
from apscheduler.schedulers.background import BackgroundScheduler
from odoo.modules.registry import RegistryManager
import datetime
import logging
import traceback
import odoo
import threading

_logger = logging.getLogger(__name__)
"""
对调用的任务进行包装,初始化odoo的env环境
"""
def odoo_env(func,**kwargs):
    def __decorator(self,**kwargs):    #add parameter receive the user information
        db_name = self.env.registry.db_name
        db = odoo.sql_db.db_connect(db_name)
        threading.current_thread().dbname = db_name
        cr = db.cursor()
        with api.Environment.manage():
            try:
                env=api.Environment(cr, self.env.uid, {})
                self.env=env
                func(self,**kwargs)

            except:
                traceback.print_exc()
        cr.commit()
        cr.close()

    return __decorator

class IacTransGroupPoUnconfirm(models.TransientModel):
    _name="iac.trans.group.po.unconfirm"


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

    def _get_group_line_log(self,sap_log_id,group_name):
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
        exe_log_rec=self.env["iac.interface.temp.table.group.exe"].search([('sap_log_id','=',sap_log_id)],limit=1)
        map_group_line_log_rec={}
        if not exe_log_rec.exists():
            group_rec=self.env["iac.interface.temp.table.group"].search([('name','=','TRANS_PO')],limit=1)
            if not group_rec.exists():
                _logger.debug('no record found in group config ')
                return;
            group_exe_vals={
                "group_code":group_rec.code,
                "group_name":group_rec.name,
                "group_id":group_rec.id,
                "start_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state":"processing",
                "sap_log_id":sap_log_id,
                }
            exe_log_rec=self.env["iac.interface.temp.table.group.exe"].create(group_exe_vals)

            group_line_list=self.env["iac.interface.temp.table.group.line"].search([('group_id','=',group_rec.id)])
            for group_line in group_line_list:
                group_line_exe_vals={
                    "group_code":group_rec.code,
                    "group_name":group_rec.name,
                    "group_id":group_rec.id,
                    "group_line_id":group_line.id,
                    "group_line_code":group_line.code,
                    "group_line_name":group_line.name,
                    "start_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "group_exe_id":exe_log_rec.id,
                    "state":"processing"
                }
                group_line_exe_rec=self.env["iac.interface.temp.table.group.exe.line"].create(group_line_exe_vals)
                map_group_line_log_rec[group_line.id]=group_line_exe_rec
            self.env.cr.commit()
        else:
            for group_line_log_rec in exe_log_rec.exe_line_ids:
                map_group_line_log_rec[group_line_log_rec.group_line_id.id]=group_line_log_rec
        return exe_log_rec,map_group_line_log_rec


    def proc_update_ref(self,sap_log_id):
        """
        更新中间表关联字段
        :return:
        """

        #设定默认记录分页记录数量
        limit_count = 1000
        #分页数组，存储sql 语句中的offset 参数
        page_list = []

        select_count="select coalesce(max(t2.record_count),0) from (                                                              " \
                     "select count(*) record_count from ep_temp_master.iac_purchase_order_unconfirm_summary t where t.sap_log_id='%s'                 " \
                     "union                                                                                                       " \
                     "select count(*) record_count from ep_temp_master.iac_purchase_order_unconfirm_detail t where t.sap_log_id='%s') t2 "\
                     %(sap_log_id,sap_log_id,)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()

        record_count = record_count_result[0][0]
        if record_count==0:
            _logger.debug('no record found in iac_purchase_order_unconfirm_summary ')
            return

        #获取组合租条目的执行日志记录对象
        group_log_rec,map_group_line_log_rec=self._get_group_line_log(sap_log_id,"TRANS_PO_UNCONFIRM")

        #获取目标表的总记录数量
        page_list = self._get_page_list(record_count, limit_count)
        update_count_sum=0
        fail_count_sum=0
        miss_count_sum=0
        for offset_count in page_list:
            sql_text="select * from ep_temp_master.sp_po_unconfirm_group_update_ref('%s',%s,%s)  " \
                     "as (last_id int4,group_id int4,group_line_id int4 ,group_name varchar,group_line_name varchar,update_count int4,fail_count int4,miss_count int4)"\
                     % (sap_log_id, limit_count, offset_count)
            _logger.debug(sql_text)

            self.env.cr.execute("select * from ep_temp_master.sp_po_unconfirm_group_update_ref(%s,%s,%s)  " \
                                "as (last_id int4,group_id int4,group_line_id int4 ,group_name varchar,group_line_name varchar,update_count int4,fail_count int4,miss_count int4)",
                       (sap_log_id, limit_count, offset_count))
            for last_id,group_id,group_line_id,group_name,group_line_name, update_count, fail_count,miss_count in self.env.cr.fetchall():
                miss_count_sum = miss_count_sum + miss_count
                update_count_sum = update_count_sum + update_count
                fail_count_sum = fail_count_sum + fail_count
                _logger.debug("executing db func %s ,update records:%s,fail records:%s,miss records:%s," % (
                    "sp_po_unconfirm_group_update_ref", update_count, fail_count,miss_count))
                log_line_rec=map_group_line_log_rec.get(group_line_id)
                if log_line_rec !=None:
                    log_line_vals={
                        "last_id":last_id,
                        "update_record_counts":update_count+log_line_rec.update_record_counts,
                        "fail_record_counts":fail_count+log_line_rec.fail_record_counts,
                        "miss_record_counts":miss_count+log_line_rec.miss_record_counts,
                        "sap_log_id":sap_log_id,
                    }
                    log_line_rec.write(log_line_vals)
            self.env.cr.commit()

        #所有数据更新完毕,更新日志状态
        group_log_vals={
            "end_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "update_record_counts":update_count_sum,
            "fail_record_counts":fail_count_sum,
            "miss_record_counts":miss_count_sum,
            "state":"success",
        }
        if fail_count_sum>0:
            group_log_vals["state"]="fail"
        else:
            group_log_vals["state"]="success"
        group_log_rec.write(group_log_vals)

        #更新明细日志情况
        for group_line_id in map_group_line_log_rec:
            log_line_rec=map_group_line_log_rec.get(group_line_id)
            group_line_log_vals={
                "end_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state":"success",
                }
            if log_line_rec.fail_record_counts>0:
                group_line_log_vals["state"]="fail"
            log_line_rec.write(group_line_log_vals)
        self.env.cr.commit()

    def proc_update_ref_miss(self,sap_log_id):
        """
        更新中间表关联字段，针对更新关联未成功的情况
        :return:
        """
        #设定默认记录分页记录数量
        limit_count = 1000
        #分页数组，存储sql 语句中的offset 参数
        page_list = []

        select_count="select coalesce(max(t2.record_count),0) from (                                                              " \
                     "select count(*) record_count from ep_temp_master.iac_purchase_order_unconfirm_summary t where t.sap_log_id='%s'                 " \
                     "union                                                                                                       " \
                     "select count(*) record_count from ep_temp_master.iac_purchase_order_unconfirm_detail t where t.sap_log_id='%s') t2 " \
                     %(sap_log_id,sap_log_id,)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()

        record_count = record_count_result[0][0]
        if record_count==0:
            _logger.debug('no record found in ep_temp_master.iac_purchase_order ')
            return

        #获取组合租条目的执行日志记录对象
        group_log_rec,map_group_line_log_rec=self._get_group_line_log(sap_log_id,"TRANS_PO_UNCONFIRM")

        #获取目标表的总记录数量
        page_list = self._get_page_list(record_count, limit_count)
        update_count_sum=0
        fail_count_sum=0
        miss_count_sum=0
        for offset_count in page_list:
            sql_text="select * from ep_temp_master.sp_po_unconfirm_group_update_ref_miss('%s',%s,%s)  " \
                     "as (last_id int4,group_id int4,group_line_id int4 ,group_name varchar,group_line_name varchar,update_count int4,fail_count int4,miss_count int4)" \
                     % (sap_log_id, limit_count, offset_count)
            _logger.debug(sql_text)

            self.env.cr.execute("select * from ep_temp_master.sp_po_unconfirm_group_update_ref_miss(%s,%s,%s)  " \
                                "as (last_id int4,group_id int4,group_line_id int4 ,group_name varchar,group_line_name varchar,update_count int4,fail_count int4,miss_count int4)",
                                (sap_log_id, limit_count, offset_count))
            for last_id,group_id,group_line_id,group_name,group_line_name, update_count, fail_count,miss_count in self.env.cr.fetchall():
                miss_count_sum = miss_count_sum + miss_count
                update_count_sum = update_count_sum + update_count
                fail_count_sum = fail_count_sum + fail_count
                _logger.debug("executing db func %s ,update records:%s,fail records:%s,miss records:%s," % (
                    "sp_po_unconfirm_group_update_ref_miss", update_count, fail_count,miss_count))
                log_line_rec=map_group_line_log_rec.get(group_line_id)
                if log_line_rec !=None:
                    log_line_vals={
                        "last_id":last_id,
                        "update_record_counts":update_count+log_line_rec.update_record_counts,
                        "fail_record_counts":fail_count+log_line_rec.fail_record_counts,
                        "miss_record_counts":miss_count+log_line_rec.miss_record_counts,
                        "sap_log_id":sap_log_id,
                        }
                    log_line_rec.write(log_line_vals)
            self.env.cr.commit()

        #所有数据更新完毕,更新日志状态
        group_log_vals={
            "end_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "state":"success",
            }
        if fail_count_sum>0:
            group_log_vals["state"]="fail"
        else:
            group_log_vals["state"]="success"
        group_log_rec.write(group_log_vals)

        #更新明细日志情况
        for group_line_id in map_group_line_log_rec:
            log_line_rec=map_group_line_log_rec.get(group_line_id)
            group_line_log_vals={
                "end_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state":"success",
                }
            if log_line_rec.fail_record_counts>0:
                group_line_log_vals["state"]="fail"
            log_line_rec.write(group_line_log_vals)
        self.env.cr.commit()
        pass

    def proc_trans_prod(self,sap_log_id):
        """
        把数据从中间表写入到正式表,只针对关联正确的数据
        :return:
        """
        #设定默认记录分页记录数量
        limit_count = 1000
        #分页数组，存储sql 语句中的offset 参数
        page_list = []

        select_count="select coalesce(max(t2.record_count),0) from (                                                              " \
                     "select count(*) record_count from ep_temp_master.iac_purchase_order_unconfirm_summary t where t.sap_log_id='%s'                 " \
                     "union                                                                                                       " \
                     "select count(*) record_count from ep_temp_master.iac_purchase_order_unconfirm_detail t where t.sap_log_id='%s') t2 " \
                     %(sap_log_id,sap_log_id,)
        self.env.cr.execute(select_count)
        record_count_result = self.env.cr.fetchall()

        record_count = record_count_result[0][0]
        if record_count==0:
            _logger.debug('no record found in ep_temp_master.iac_purchase_order ')
            return

        #获取组合租条目的执行日志记录对象
        group_log_rec,map_group_line_log_rec=self._get_group_line_log(sap_log_id,"TRANS_PO_UNCONFIRM")

        #获取目标表的总记录数量
        page_list = self._get_page_list(record_count, limit_count)
        update_count_sum=0
        fail_count_sum=0
        miss_count_sum=0
        for offset_count in page_list:
            sql_text="select * from ep_temp_master.sp_po_unconfirm_group_trans_prod('%s',%s,%s)  " \
                     "as (last_id int4,group_id int4,group_line_id int4 ,group_name varchar,group_line_name varchar,update_count int4,fail_count int4,miss_count int4)" \
                     % (sap_log_id, limit_count, offset_count)
            _logger.debug(sql_text)

            self.env.cr.execute("select * from ep_temp_master.sp_po_unconfirm_group_trans_prod(%s,%s,%s)  " \
                                "as (last_id int4,group_id int4,group_line_id int4 ,group_name varchar,group_line_name varchar,update_count int4,fail_count int4,miss_count int4)",
                                (sap_log_id, limit_count, offset_count))
            for last_id,group_id,group_line_id,group_name,group_line_name, update_count, fail_count,miss_count in self.env.cr.fetchall():
                miss_count_sum = miss_count_sum + miss_count
                update_count_sum = update_count_sum + update_count
                fail_count_sum = fail_count_sum + fail_count
                _logger.debug("executing db func %s ,update records:%s,fail records:%s,miss records:%s," % (
                    "sp_po_unconfirm_group_trans_prod", update_count, fail_count,miss_count))
                log_line_rec=map_group_line_log_rec.get(group_line_id)
                if log_line_rec !=None:
                    log_line_vals={
                        "last_id":last_id,
                        "update_record_counts":update_count+log_line_rec.update_record_counts,
                        "fail_record_counts":fail_count+log_line_rec.fail_record_counts,
                        "miss_record_counts":miss_count+log_line_rec.miss_record_counts,
                        "sap_log_id":sap_log_id,
                        }
                    log_line_rec.write(log_line_vals)
            self.env.cr.commit()

        #所有数据更新完毕,更新日志状态
        group_log_vals={
            "end_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "state":"success",
            }
        if fail_count_sum>0:
            group_log_vals["state"]="fail"
        else:
            group_log_vals["state"]="success"
        group_log_rec.write(group_log_vals)

        #更新明细日志情况
        for group_line_id in map_group_line_log_rec:
            log_line_rec=map_group_line_log_rec.get(group_line_id)
            group_line_log_vals={
                "end_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state":"success",
                }
            if log_line_rec.fail_record_counts>0:
                group_line_log_vals["state"]="fail"
            log_line_rec.write(group_line_log_vals)
        self.env.cr.commit()

