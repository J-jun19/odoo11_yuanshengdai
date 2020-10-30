# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo
import threading
import logging
import traceback
from odoo import SUPERUSER_ID
_logger = logging.getLogger(__name__)

class IacVendorChangeBasic(models.Model):
    """
    Vendor基本资料
    """
    _inherit = "iac.vendor.change.basic"

    @api.one
    def fill_blank_attachment(self):
        """
        只能由vendor对象调用,在复制完attachment之后,根据iac_attachment_config中的定义
        的信息补充空的附件栏位
        :param object_id:
        :return:
        """
        #查询得到缺少的附件栏位信息
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
            AND iac.model_obj = 'vendor_bank'
            AND NOT EXISTS (
                SELECT
                    1
                FROM
                    iac_vendor_change_attachment iva
                WHERE
                    iva.change_id = %s
                AND iva.\"type\" = iac.\"type\"
            )
            ORDER BY
                iac.model_obj,
                iac.\"sequence\"
        """,(self.id,))

        pg_result=self.env.cr.fetchall()
        #遍历全部缺少的栏位进行补充操作,缺少必须的文件会提示错误信息
        for attachment_type_id,attachment_type_name,attachment_type_desc,attachment_type_cate,\
            is_required,is_displayed,sequence in pg_result:
            attachment_vals = {
                'change_id': self.id,
                'vendor_id': self.vendor_reg_id.vendor_id.id,
                'type': attachment_type_id,
                'group': 'bank',
            }
            attachment_rec=self.env["iac.vendor.change.attachment"].create(attachment_vals)

        pg_result=self.env.cr.fetchall()
        #遍历全部缺少的栏位进行补充操作
        for attachment_type_id,attachment_type_name,attachment_type_desc,attachment_type_cate,\
            is_required,is_displayed,sequence in pg_result:
            attachment_vals = {
                'change_id': self.id,
                'type': attachment_type_id,
                'group': 'bank',
            }
            attachment_rec=self.env["iac.vendor.attachment"].create(attachment_vals)