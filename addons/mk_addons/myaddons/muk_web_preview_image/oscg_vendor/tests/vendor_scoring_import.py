# -*- coding: utf-8 -*-

import erppeek
import xlrd
import logging

"""
导入vendor scoring
"""

if __name__=="__main__":
    api = erppeek.Client('http://localhost:8069', 'IAC_DB', 'admin', 'admin')

    import_data = 1
    if import_data == 1:
        workbook = xlrd.open_workbook('d:\\temp\\vendor_scoring.xls')
        part_category_sheet = workbook.sheet_by_name('iac.part.category')
        score_iqc_mprma_sheet = workbook.sheet_by_name('iac.score.iqc.mprma')
        fail_cost_section_sheet = workbook.sheet_by_name('iac.fail.cost.section')
        score_exclude_sheet = workbook.sheet_by_name('iac.score.exclude')
        score_definition_sheet = workbook.sheet_by_name('iac.score.definition')
        score_range_sheet = workbook.sheet_by_name('iac.score.range')

        # 处理iac.part.category
        # 导入数据校验
        check_flag = True
        index = 1
        while index <= part_category_sheet.nrows - 1:
            if part_category_sheet.cell_value(index, 1):
                object_id = api.model('iac.part.class').get([('name', '=', part_category_sheet.cell_value(index, 1))])
                if not object_id:
                    api.model('iac.part.class').create({'name': part_category_sheet.cell_value(index, 1)})

            if part_category_sheet.cell_value(index, 2):
                for item in part_category_sheet.cell_value(index, 2).split('|'):
                    object_id = api.model('material.group').get([('material_group', '=', item)])
                    if not object_id:
                        check_flag = check_flag & False
                        logging.error(u'No.%s 数据异常，未找到material_group=%s' % (index, item))

            index += 1
        logging.warn(u'需创建 %s 个iac.part.category' % (index - 1))

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= part_category_sheet.nrows - 1:
                int_part_class_id = False
                int_material_group_ids = []
                material_group_ids = False

                if part_category_sheet.cell_value(index, 1):
                    object_id = api.model('iac.part.class').get(
                        [('name', '=', part_category_sheet.cell_value(index, 1))])
                    if object_id:
                        int_part_class_id = object_id.id

                if part_category_sheet.cell_value(index, 2):
                    for item in part_category_sheet.cell_value(index, 2).split('|'):
                        object_id = api.model('material.group').get([('material_group', '=', item)])
                        if object_id:
                            int_material_group_ids.append(object_id.id)
                    material_group_ids = erppeek.RecordList(api.model('material.group'), int_material_group_ids)

                part_category_vals = {
                    'name': part_category_sheet.cell_value(index, 0),
                    'part_class': int_part_class_id,
                    'material_group_ids': material_group_ids
                }
                api.model('iac.part.category').create(part_category_vals)

                index += 1

            logging.warn(u'成功创建 %s 个iac.part.category' % (index - 1))

        # 处理iac.score.iqc.mprma
        # 导入数据校验
        check_flag = True
        index = 1
        while index <= score_iqc_mprma_sheet.nrows - 1:
            if score_iqc_mprma_sheet.cell_value(index, 0):
                object_id = api.model('iac.part.category').get([('name', '=', score_iqc_mprma_sheet.cell_value(index, 0))])
                if not object_id:
                    check_flag = check_flag & False
                    logging.error(u'No.%s 数据异常，未找到part_category=%s' % (index, score_iqc_mprma_sheet.cell_value(index, 0)))

            index += 1
        logging.warn(u'需创建 %s 个iac.score.iqc.mprma' % (index - 1))

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= score_iqc_mprma_sheet.nrows - 1:
                int_part_category_id = False

                if score_iqc_mprma_sheet.cell_value(index, 0):
                    object_id = api.model('iac.part.category').get(
                        [('name', '=', score_iqc_mprma_sheet.cell_value(index, 0))])
                    if object_id:
                        int_part_category_id = object_id.id

                iqc_mprma_vals = {
                    'part_category_id': int_part_category_id,
                    'score_type': score_iqc_mprma_sheet.cell_value(index, 1),
                    'score': score_iqc_mprma_sheet.cell_value(index, 2),
                    'lower_limit': score_iqc_mprma_sheet.cell_value(index, 3),
                    'high_limit': score_iqc_mprma_sheet.cell_value(index, 4)
                }
                api.model('iac.score.iqc.mprma').create(iqc_mprma_vals)

                index += 1

            logging.warn(u'成功创建 %s 个iac.score.iqc.mprma' % (index - 1))

        # 处理iac.fail.cost.section
        # 导入数据校验
        check_flag = True

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= fail_cost_section_sheet.nrows - 1:
                fail_cost_section_vals = {
                    'fail_type': fail_cost_section_sheet.cell_value(index, 0),
                    'score': fail_cost_section_sheet.cell_value(index, 1),
                    'lower_limit': fail_cost_section_sheet.cell_value(index, 2),
                    'high_limit': fail_cost_section_sheet.cell_value(index, 3)
                }
                api.model('iac.fail.cost.section').create(fail_cost_section_vals)

                index += 1

            logging.warn(u'成功创建 %s 个iac.fail.cost.section' % (index - 1))

        # 处理iac.score.exclude
        # 导入数据校验
        check_flag = True
        index = 1
        while index <= score_exclude_sheet.nrows - 1:
            if score_exclude_sheet.cell_value(index, 0):
                object_id = api.model('iac.supplier.company').get(
                    [('company_no', '=', score_exclude_sheet.cell_value(index, 0))])
                if not object_id:
                    check_flag = check_flag & False
                    logging.error(u'No.%s 数据异常，未找到company_no=%s' % (index, score_exclude_sheet.cell_value(index, 0)))

            index += 1
        logging.warn(u'需创建 %s 个iac.score.exclude' % (index - 1))

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= score_exclude_sheet.nrows - 1:
                int_supplier_company_id = False

                if score_exclude_sheet.cell_value(index, 0):
                    object_id = api.model('iac.supplier.company').get(
                        [('company_no', '=', score_exclude_sheet.cell_value(index, 0))])
                    if object_id:
                        int_supplier_company_id = object_id.id

                api.model('iac.score.exclude').create({'supplier_company_id': int_supplier_company_id})

                index += 1

            logging.warn(u'成功创建 %s 个iac.score.exclude' % (index - 1))

        # 处理iac.score.definition
        # 导入数据校验
        check_flag = True
        index = 1
        while index <= score_definition_sheet.nrows - 1:
            if score_definition_sheet.cell_value(index, 6):
                object_id = api.model('iac.part.class').get(
                    [('name', '=', score_definition_sheet.cell_value(index, 6))])
                if not object_id:
                    check_flag = check_flag & False
                    logging.error(u'No.%s 数据异常，未找到part_class=%s' % (index, score_definition_sheet.cell_value(index, 6)))

            index += 1
        logging.warn(u'需创建 %s 个iac.score.definition' % (index - 1))

        # 执行导入数据
        if check_flag:
            index = 1
            while index <= score_definition_sheet.nrows - 1:
                int_part_class_id = False

                if score_definition_sheet.cell_value(index, 6):
                    object_id = api.model('iac.part.class').get(
                        [('name', '=', score_definition_sheet.cell_value(index, 6))])
                    if object_id:
                        int_part_class_id = object_id.id

                bool_active = False
                if score_definition_sheet.cell_value(index, 7).lower() == 'true':
                    bool_active = True
                score_definition_vals = {
                    'group_code': score_definition_sheet.cell_value(index, 0),
                    'sequence': score_definition_sheet.cell_value(index, 1),
                    'display_label': score_definition_sheet.cell_value(index, 2),
                    'description': score_definition_sheet.cell_value(index, 3),
                    'score_standard': score_definition_sheet.cell_value(index, 4),
                    'ratio': score_definition_sheet.cell_value(index, 5),
                    'part_class': int_part_class_id,
                    'active': bool_active,
                    'memo': score_definition_sheet.cell_value(index, 8)
                }
                api.model('iac.score.definition').create(score_definition_vals)

                index += 1

            logging.warn(u'成功创建 %s 个iac.score.definition' % (index - 1))

        # 处理iac.score.range
        # 导入数据校验
        index = 1
        while index <= score_range_sheet.nrows - 1:
            score_range_vals = {
                'log_type': score_range_sheet.cell_value(index, 0),
                'level_t': score_range_sheet.cell_value(index, 1),
                'range_from': score_range_sheet.cell_value(index, 2),
                'range_to': score_range_sheet.cell_value(index, 3),
                'score': score_range_sheet.cell_value(index, 4)
            }
            api.model('iac.score.range').create(score_range_vals)

            index += 1

        logging.warn(u'成功创建 %s 个iac.score.range' % (index - 1))