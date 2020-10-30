# -*- coding: utf-8 -*-

from odoo import models,api
from odoo.odoo_env import odoo_env


class MailAlertBindPartCategory(models.Model):

    _name = 'mail.alert.bind.part.categroy'

    @odoo_env
    @api.model
    def job_mail_alert_bind_part_categroy(self):
        self._cr.execute("""select mg.material_group,mg.description from material_group mg
                    where not exists (select 1 from part_category_material_groups pcmg where 
                    pcmg.material_group_id = mg.id) and mg.material_group like 'R%' order by 
                    mg.material_group""")

        result = self._cr.fetchall()
        # remove_list = [(u'R-BASEBAN', u'BASEBAND'),(u'R-CONSIGN', u'Consign'),(u'R-FW', u'Firmware'),
        #                (u'R-NCI', u'NCI'),(u'R-TP05RD', u'TP05 RD material'),(u'R-VALVE', u'VALVE'),
        #                (u'R-WIRED', u'WIRED LAN')]
        # remove_list_re = remove_list[:]
        # search_storage = self.env['abolished.part.categroy.storage'].search([('material_group','!=',False)])
        self._cr.execute("""select apcs.material_group,apcs.description from abolished_part_categroy_storage apcs""")
        search_storage = self._cr.fetchall()
        for storage_obj in search_storage:
            if storage_obj in result:
                result.remove(storage_obj)

        # for item in search_storage:
        #     if item in result:
        #         vals = {}
        #         vals['material_group'] = item[0]
        #         vals['description'] = item[1]
        #         search_re = self.env['abolished.part.categroy.storage'].search([('material_group','=',item[0])])
        #         if not search_re:
        #             self.env['abolished.part.categroy.storage'].create(vals)
        #         result.remove(item)
        # self.env.cr.commit()
        print result

        if result:
            # 返回结果如果为空在MySQL中是null，而在Python中则是None
            result_list = []
            for row in result:
                row_list = list(row)
                result_list.append(row_list)

            print result_list
            email = 'Lai.Jocelyn@iac.com.tw' + ';' + 'Lin.Yun@iac.com.tw' + ';' + 'Zhang.Pei-Wu@iac.com.tw' + ';' + \
                    'Tsaur.Shiow-Chyn@iac.com.tw' + ';' + 'Jen.Cooper@iac.com.tw' + ';' + 'Lin.Chu-Wan@iac.com.tw' + ';' + \
                    'Shao.Jane@iac.com.tw' + ';' + 'Wang.Ningg@iac.com.tw' + ';' + 'Huang.CH@iac.com.tw' + ';' + \
                    'Chiou.Vincent@iac.com.tw' + ';' + 'jiang.shier@iac.com.tw'

            self.env['iac.email.pool'].button_to_mail('iac-ep_support@iac.com.tw', email, '', "以下material group沒有綁定part category, 請抓緊維護",
                                                            ['material_group', 'description'], result_list, 'MATERIAL_GROUP_BIND_PART_CATEGORY')
        else:
            return True