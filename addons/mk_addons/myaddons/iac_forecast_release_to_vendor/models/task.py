# -*- coding: utf-8 -*-
import logging
import pytz
import odoo
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import pdb
from functools import wraps
import  traceback
import threading
from odoo.odoo_env import odoo_env

_logger = logging.getLogger(__name__)
 
 
# 定时任务：自动將本周 iac_tconfirm_data 備份 temp table
class TaskBackupConfirmData(models.Model):
    """
        程式\思路：
                1. 直接 select * from iac_tconfirm.data into iac_tconfirm.data.temp
                2. 刪除所有 iac_tconfirm.data 資料
        """

    _name = 'task.backup.confirm.data'
    name = fields.Char(string="Name")

    @odoo_env
    @api.model
    def job_backup_confirm_data(self):

        _logger.debug(u'定时任务启动，開始將本周 iac_tconfirm_data 備份 temp table...')

        # print '*48: '
        # 1. 將本周 iac_tconfirm_version 備份 temp table
        self._cr.execute(" INSERT INTO iac_tconfirm_version_temp ( "
                         "   division_id,status,create_uid,vendor_id,material_id,write_uid, "
                         "   version,raw_id,write_date,fpversion,create_date,buyer_id ) "
                         " ( select division_id,status,create_uid,vendor_id,material_id,write_uid, "
                         "       version,raw_id,write_date,fpversion,create_date,buyer_id"
                         "      from iac_tconfirm_version ) ")
        # print '*32: '
        # 2. 將本周 iac_tconfirm_data 備份 temp table
        self._cr.execute(" INSERT INTO iac_tconfirm_data_temp( "
                         "   status, vendor_id, version, buyer_id, fpversion, "
                         "   plant_id, raw_id, description, division_id, "
                         "   custpn_info, flag, intransit_qty, leadtime, "
                         "   material_id, max_surplus_qty, mfgpn_info, "
                         "  remark, quota, round_value, stock, "
                         "  release_flag, open_po, mquota_flag, "
                         "  vendor_name, vendor_reg_id, "
                         "  alt_flag, alt_grp, "
                         "  create_by, create_date, create_uid, creation_date, "
                         "  write_date, write_uid, po, pr, "
                         "  b001, b002, b004, b005, b012, b017b, b902q, b902s, "
                         "  qty_m1, qty_m2, qty_m3, qty_m4, qty_m5, qty_m6, qty_m7, qty_m8, qty_m9, "
                         "  qty_w1, qty_w1_r, qty_w2, qty_w3, qty_w4, qty_w5, qty_w6, qty_w7, "
                         "  qty_w8, qty_w9, qty_w10, qty_w11, qty_w12, qty_w13 ) "
                         " ( select  status, vendor_id, version, buyer_id, fpversion, "
                         "      plant_id, raw_id, description, division_id, "
                         "      custpn_info, flag, intransit_qty, leadtime, "
                         "      material_id, max_surplus_qty, mfgpn_info, "
                         "      remark, quota, round_value, stock, "
                         "      release_flag, open_po, mquota_flag, "
                         "      vendor_name, vendor_reg_id, "
                         "      alt_flag, alt_grp, "
                         "      create_by, create_date, create_uid, creation_date, "
                         "      write_date, write_uid, po, pr, "
                         "      b001, b002, b004, b005, b012, b017b, b902q, b902s, "
                         "      qty_m1, qty_m2, qty_m3, qty_m4, qty_m5, qty_m6, qty_m7, qty_m8, qty_m9, "
                         "      qty_w1, qty_w1_r, qty_w2, qty_w3, qty_w4, qty_w5, qty_w6, qty_w7, "
                         "      qty_w8, qty_w9, qty_w10, qty_w11, qty_w12, qty_w13 from iac_tconfirm_data ) ")

        # 3.將本周 iac_tconfirm_version 刪除
        # print '*89: '
        self._cr.execute(" delete FROM iac_tconfirm_version ")

        # 4.將本周 iac_tconfirm_data 刪除
        # print '*93: '
        self._cr.execute(" delete FROM iac_tconfirm_data ")
        # 调用SAP接口更新数据  FP 的 table :  iac.tconfirm.data

# 定时任务：自动刪除歷史 RawDate、confirmDataTemp，只保留最近7天的資料 20180827 laura add
class TaskDeleteRawDate(models.Model):
    """
        程式\思路：
                自动刪除歷史 RawDate、confirmDataTemp，只保留最近7天的資料 20180827 laura add
        """
    _name = 'task.delete.raw.data'
    name = fields.Char(string="Name")

    @odoo_env
    @api.model
    def job_delete_raw_data(self):

        print '*97:   job_delete_raw_data '
        _logger.debug(u'定时任务启动，開始刪除 RawDate、confirmDataTemp歷史資料，只保留本周最近7天資料...')

        # 找出&刪除 歷史 RawDate、confirmDataTemp
        self._cr.execute("""select * from public.proc_delete_iac_traw_data()""")
        # self._cr.execute(
        #     "   delete FROM iac_tconfirm_data_temp where fpversion <= TO_CHAR(now()::timestamp + '-28 day' ,'YYYYMMDD')  " ) # 把舊的紀錄刪掉
        #
        # self._cr.execute(
        #     "   delete FROM iac_tRaw_data where  fpversion <= TO_CHAR(now()::timestamp + '-28 day' ,'YYYYMMDD')  ")  # 把舊的紀錄刪掉
