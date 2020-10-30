# -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
#
#    Copyright (C) 2017 MuK IT GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.muk_dms.models import muk_dms_base as base
from odoo.addons.muk_dms.models import muk_dms_data as data
from . import muk_dms_root as root
import traceback
import os
_logger = logging.getLogger(__name__)

class SysFileFile(base.DMSModel):
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def notify_change(self, change, values):
        super(SysFileFile, self).notify_change(change, values)
        if str(change) is str(base.PATH):
            self._update_file(data.MOVE, {'path': self.directory.get_path()})
        elif str(change) is str(base.ROOT):
            _logger.info("Migrating file from %s to %s" % (self.type, values))
            values = self.copy_data(None)[0]
            values['file'] =  self._get_file()
            self._delete_file()
            rec_file = self._create_file(values, self.directory, self.directory.get_root())
            self.file_ref = rec_file._name + ',' + str(rec_file.id)
    
    def _create_file(self, values, rec_dir, rec_root):
        result = super(SysFileFile, self)._create_file(values, rec_dir, rec_root)
        if result:
            return result
        elif rec_root.save_type == root.SAVE_SYSTEM:
            rec_data = self.env['muk_dms.system_data'].sudo().create({'filename': values['filename'],
                                                                      'entry_path': rec_root.entry_path,
                                                                      'path': rec_dir.get_path()})
            #生成存储在磁盘上的文件名
            file_name, file_extension = os.path.splitext(values["filename"])
            rec_data.sudo().write({'save_file_name':str(rec_data.id)+file_extension})
            #开始写入文件
            file_values={
                "file":values.get('file',False),
                "filename":values.get('filename',False),
                "file_extension":file_extension
            }
            rec_data.sudo().update(data.REPLACE,file_values)
            return rec_data
        return False

    def fix_file_ref(self):
        """
        只能被muk_dms.file 记录对象调用
        修复当前muk_dms.file 模型记录对象中file_ref对象记录的文件命名不规范的问题
        :return:
        """
        new_file_ref=self.file_ref.copy_to_fix()
        self.file_ref=new_file_ref._name + ',' + str(new_file_ref.id)
        return new_file_ref.id

    @api.model
    def job_fix_filename(self):
        """
        修改muk_dms_system_data 中的文件存储规则,文件名应该为 id +扩展名

        drop table ep_temp_master.lwt_checksum;
        create table ep_temp_master.lwt_checksum
        (id int4,
         checksum_flag BOOLEAN,
         ex_msg text
        );

        :return:
        """
        logging.info("job_fix_filename start")
        self.env.cr.execute("""
            SELECT
                err_file. ID,
                err_file.file_ref_id,
                err_file.file_base_name,
                dms_file.file_extension
            FROM
                ep_temp_master.lwt_err_file err_file,
                "public".muk_dms_file dms_file
            WHERE
                err_file. ID = dms_file. ID
            ORDER BY
                ID
        """)
        pg_result=self.env.cr.dictfetchall()
        for pg_line in pg_result:
            try:
                muk_file_rec=self.env["muk_dms.file"].browse(pg_line.get("id"))
                #修复文件关联,修复文件名
                new_file_ref_id=muk_file_rec.fix_file_ref()

                file_ref_rec=self.env["muk_dms.system_data"].browse(new_file_ref_id)
                #验证新复制的文件checksum是否正确
                checksum_result=file_ref_rec.test_checksum()
                self.env.cr.execute("""
                update ep_temp_master.lwt_err_file err_file
                set checksum_flag=%s,new_file_ref_id=%s
                where id=%s
                """,(checksum_result,new_file_ref_id,pg_line.get("id",False)))
                self.env.cr.commit()
            except:
                self.env.cr.rollback()
                traceback.print_exc()
                ex_msg=traceback.format_exc()
                self.env.cr.execute("""
                update ep_temp_master.lwt_err_file err_file
                set checksum_flag=False,
                ex_msg=%s
                where id=%s
                """,(ex_msg,pg_line.get("id",False)))
                self.env.cr.commit()

        #验证表中规定的checksum记录
        self.env.cr.execute("select id from  ep_temp_master.lwt_checksum")
        pg_result=self.env.cr.fetchall()
        for pg_line in pg_result:
            try:
                muk_file_rec=self.env["muk_dms.file"].browse(pg_line[0])
                checksum_result=muk_file_rec.file_ref.test_checksum()
                self.env.cr.execute("""
                update ep_temp_master.lwt_checksum
                set checksum_flag=%s
                where id=%s
                """,(checksum_result,pg_line[0]))
                self.env.cr.commit()
            except:
                self.env.cr.rollback()
                traceback.print_exc()
                ex_msg=traceback.format_exc()
                self.env.cr.execute("""
                update ep_temp_master.lwt_checksum
                set checksum_flag=False,ex_msg=%s
                where id=%s
                """,(ex_msg,pg_line[0]))
                self.env.cr.commit()

        logging.info("job_fix_filename end")
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------


    #没有使用的价值
    #def _append_values_write(self, values):
    #    values = super(SysFileFile, self)._append_values_write(values)
    #    if 'directory' in values:
    #        rec_dir = self.env['muk_dms.directory'].sudo().browse([values['directory']])
    #        self._update_file(data.MOVE, {'path': rec_dir.get_path()})
    #    return values