# -*- coding: utf-8 -*-
import pytz
import time
import odoo
from datetime import datetime,timedelta
from odoo import models, fields, api,odoo_env
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import pdb
from functools import wraps
from odoo.odoo_env import odoo_env
import  traceback
import threading
import traceback, logging, types,json
from contextlib import contextmanager
from odoo.exceptions import ValidationError, AccessError, MissingError
import base64

_logger = logging.getLogger(__name__)


@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError, err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()

class mukDmsSysData(models.Model):
    _inherit="muk_dms.system_data"

    @odoo_env
    @api.model
    def job_recompute_checksum(self):
        """
        重新计算存储在文件服务器中的文件校验码，如果不一致就更新最新的校验码
        :return:
        """
        logging.info("job_recompute_checksum start,thread name is %s" %(threading.currentThread().getName()))
        file_id_list=self.env["muk_dms.system_data"].search([])
        #file_id_list=self.search([])
        for file_rec in file_id_list:
            try:
                checksum=file_rec.recompute_checksum()
                if checksum!=file_rec.checksum:
                    logging.info("file id is %s,file_name is %s,file checksum is %s ,database checksum is %s"%
                                 (file_rec.id,file_rec.save_file_name,checksum,file_rec.checksum))
                    file_rec.checksum=checksum
            except:
                logging.error("compute file checksum error;file id is %s,file_name is %s,database checksum is %s"%
                                (file_rec.id,file_rec.save_file_name,file_rec.checksum))
                traceback.print_exc()

        logging.info("job_recompute_checksum end,thread name is %s" %(threading.currentThread().getName()))