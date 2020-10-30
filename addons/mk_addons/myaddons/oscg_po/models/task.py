# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)

# 定时任务
class TaskPurchaseOrder(models.Model):
    _auto = False
    _name = 'task.purchase.order'

    @api.model
    def _cron_vendor_auto_confirm(self):
        self.vendor_auto_confirm()

    @api.model
    def vendor_auto_confirm(self):
        _logger.debug(u'定时任务启动，Vendor Auto Confirm PO...')

        # 调用SAP接口查询EDI855资料
        biz_object = {
            "id": 855,
            "biz_object_id": 855
        }
        rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
            "iac.interface.rpc"].invoke_web_call_with_log(
            "ODOO_PO_005", biz_object)
        if rpc_result:
            order_codes = []
            sap_date = rpc_json_data['rpc_callback_data']
            if sap_date['Document'] and sap_date['Document']['ITEM']:
                item_list = rpc_json_data['Document']['ITEM']
                for item in item_list:
                    if item['PO_NO'] not in order_codes:
                        order_codes.append(item['PO_NO'])
                    order_lines = self.env['iac.purchase.order.line'].search([('order_code', '=', item['PO_NO']), ('name', '=', item['PO_LINE_NO'])], limit=1)
                    order_lines[0].write({'vendor_confirmed': 'confirmed'})

                for order_code in order_codes:
                    # 调用SAP接口更新PO vendor confirmed状态
                    biz_object = {
                        "id": 855,
                        "biz_object_id": 855,
                        "PO_NO": order_code,
                        "EDI_TYPE": "I855",
                        "EP_STATUS": "EP2"
                    }
                    rpc_result, rpc_json_data, log_line_id, exception_log = self.env[
                        "iac.interface.rpc"].invoke_web_call_with_log(
                        "ODOO_PO_006", biz_object)
                    if rpc_result:
                        _logger.debug('EDI vendor confirmed successfully!')