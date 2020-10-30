# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
from odoo import SUPERUSER_ID
from odoo.odoo_env import odoo_env
import  traceback
import threading
import traceback, logging, types,json
_logger = logging.getLogger(__name__)


class IacVendorRegister(models.Model):
    """
    Vendor基本资料
    """
    _inherit = "iac.vendor.register"

    @odoo_env
    @api.model
    def job_fill_attachment(self):
        """
        补充文档附件
        :return:
        """
        self.env.cr.execute("""select id from iac_vendor_register where state='done' or state='block'""")
        pg_result=self.env.cr.fetchall()
        for vendor_id in pg_result:
            vendor_rec=self.env["iac.vendor.register"].browse(vendor_id)
            vendor_rec.fill_blank_attachment()

    @api.one
    def fill_blank_attachment(self):
        """
        只能由vendor_register对象调用,在复制完attachment之后,根据iac_attachment_config中的定义
        的信息补充空的附件栏位
        :param object_id:
        :return:
        """
        #查询得到缺少的附件栏位信息
        self.env.cr.execute("""
            SELECT
                iac.\"type\" \"attachment_type_id\",
                iat.\"name\",
                iat.description,
                iac.model_obj attachment_cate,
                iac.is_required,
                iac.is_displayed,
                iac.\"sequence\"
            FROM
                iac_attachment_config iac,
                iac_attachment_type iat
            WHERE
                iac.\"type\" = iat. ID
            AND iac.model_obj = 'vendor'
            AND NOT EXISTS (
                SELECT
                    1
                FROM
                    iac_vendor_register_attachment ivra
                WHERE
                    ivra.vendor_reg_id = %s
                AND ivra.\"type\" = iac.\"type\"
            )
            ORDER BY
                iac.model_obj,
                iac.\"sequence\"
        """,(self.id,))

        pg_result=self.env.cr.fetchall()
        #遍历全部缺少的栏位进行补充操作
        for attachment_type_id,attachment_type_name,attachment_type_desc,attachment_type_cate,\
            is_required,is_displayed,sequence in pg_result:
            attachment_vals = {
                'vendor_reg_id': self.id,
                'type': attachment_type_id,
                'group': 'basic',
            }
            attachment_rec=self.env["iac.vendor.register.attachment"].create(attachment_vals)