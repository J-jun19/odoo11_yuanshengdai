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

import os
import base64
import json
import urllib
import StringIO
import cStringIO
import mimetypes
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError
from string import maketrans

from . import muk_dms_base as base
from . import muk_dms_data as data
from . import muk_dms_root as root

_logger = logging.getLogger(__name__)

class File(base.DMSModel):
    _name = 'muk_dms.file'
    _description = "File"
    
    _inherit = ['muk_dms.access', 'mail.thread']
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    directory = fields.Many2one('muk_dms.directory', string="Directory", required=True)

    file_ref = fields.Reference(selection='_get_file_types', string="File Reference", readonly=True)
    
    filename = fields.Char(string='Filename', required=True)
    file = fields.Binary(string='File', store=False, required=True)
    
    file_extension = fields.Char(string='Extension', readonly=True)
    mime_type = fields.Char(string='Type', readonly=True)
    file_size = fields.Integer(string='Size', readonly=True)
    version = fields.Integer(string='Version', readonly=True, default=1)

    history_ids = fields.One2many('muk_dms.file.history', 'parent_id', String='History Version')
    
    name = fields.Char(compute='_compute_name', string="Name")
    
    type = fields.Char(compute='_compute_type', string="File Type")
    
    link_download = fields.Char(compute='_compute_link_download', string="Download Link")
    link_preview = fields.Char(compute='_compute_link_preview', string="Preview Link")
    link_checkout = fields.Char(compute='_compute_link_checkout', string="Checkout Link")
    link_update = fields.Char(compute='_compute_link_update', string="Update Link")
    
    path_text = fields.Char(compute='_compute_path_text', string="Path")
    path_object = fields.Char(compute='_compute_path_object', string="Path")
    
    is_locked_flag = fields.Boolean(compute='_compute_is_locked', string="Locked")
    is_editor = fields.Boolean(compute='_compute_is_editor', string="Editor")
    active = fields.Boolean(index=True, default=True)
    
    #----------------------------------------------------------
    # Local
    #----------------------------------------------------------
    
    file_types = [('muk_dms.data', _('Data'))]
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def get_path(self, include_self=True):
        path = include_self and str(self.filename) + "/" or ""
        if self.directory.check_existence():
            path = self.directory.get_path() + path
        return path

    @api.multi
    def name_get(self):
        return [(request.id, request.name) for request in self]
    
    def get_file_data(self):
        return self._get_file()
    
    def _get_file(self):
        return self.file_ref and self.file_ref.sudo().data() or None
    
    def _create_file(self, values, rec_dir, rec_root):
        if rec_root.save_type == root.SAVE_DATABASE:
            return self.env['muk_dms.database_data'].sudo().create({'file': values['file']})
        return False
    
    def _update_file(self, command, values):
        if self.file_ref and self.file_ref.id:
            self.file_ref.sudo().update(command, values)

    def _delete_file(self):
        if self.file_ref and self.file_ref.id:
            ref = self.file_ref
            self.file_ref = None
            ref.sudo().delete()
            ref.sudo().unlink()
        return True

    #----------------------------------------------------------
    # Selections
    #----------------------------------------------------------
    
    def _get_file_types(self):
        return self.file_types
    
    #----------------------------------------------------------
    # Locking
    #----------------------------------------------------------

    @api.multi
    def check_lock(self):
        lock = self.is_locked()
        if lock:
            return [lock.id, lock.locked_by_ref.id or "system"]
        else:
            return False
        
    @api.one
    def user_lock(self):
        lock = self.is_locked()
        if lock:
            raise AccessError(_("File is already locked."))
        return self.lock(self.env.user)
    
    @api.one
    def user_unlock(self):
        lock = self.is_locked()
        if lock:
            if lock and lock.locked_by_ref and lock.locked_by_ref.id == self.env.user.id:
                self.unlock()
            else:
                raise AccessError(_("No rights to unlock the file."))
    
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------

    @api.one
    @api.depends('filename')
    def _compute_name(self):
        self.name = self.filename and os.path.splitext(self.filename)[0] or ""
    
    @api.one
    @api.depends('file_ref')
    def _compute_type(self):
        self.type = self.file_ref and self.file_ref.get_type() or _("No Data")
    
    @api.one
    def _compute_link_download(self):
        self.link_download = "/dms/file/download/" + str(self.id)
    
    @api.one
    def _compute_link_preview(self):
        self.link_preview = "/dms/file/preview?id=" + str(self.id)
    
    
    @api.one
    def _compute_link_checkout(self):
        self.link_checkout = "/dms/file/checkout/" + str(self.id)
        
    @api.one
    def _compute_link_update(self):
        self.link_update = "/dms/file/update/" + str(self.id)
    
    @api.one
    @api.depends('filename', 'directory')
    def _compute_path_text(self):
        self.path_text = self.get_path(False)
    
    @api.one
    @api.depends('filename', 'directory')
    def _compute_path_object(self):
        path = []
        try:
            path.append({'id': int(self.id), 'name': self.filename or "New", 'model':self._name})
        except TypeError:
            # NewId can't be cast to integer
            path.append({'id':-1, 'name': self.filename or "New"})
        if self.directory.check_existence():
            for i, dir in enumerate(self.directory.get_parent_list()):
                try:
                    path.append({'id': int(dir.id), 'name': dir.name or "New", 'model':'muk_dms.directory'})
                except TypeError:
                    # NewId can't be cast to integer
                    path.append({'id': -1, 'name': dir.name or "New", 'model':'muk_dms.directory'})
        self.path_object = json.dumps(path[::-1])
    
    @api.one
    def _compute_is_locked(self):
        self.is_locked_flag = self.is_locked()
    
    @api.one
    def _compute_is_editor(self):
        self.is_editor = self.is_locked_by() == self.env.user
    
    def _append_field_values(self, index, result):
        result = super(File, self)._append_field_values(index, result)
        result[index]['file'] = "0 KB"
        return result
    
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------
    
    @api.one
    @api.constrains('directory', 'filename')
    def _check_name(self):
        _logger.debug("Checking if the given filename isn't already taken...")
        # 改成同一个目录下的文件名可以重名
        # if self.directory.check_existence():
        #     for rec in self.directory.files:
        #         if rec.filename == self.filename and rec != self:
        #             raise ValidationError(_("Files on the same level have to have a unique filename."))

    @api.one
    @api.constrains('directory')
    def _check_root(self):
        _logger.debug("Checking if a root exists...")
        if not self.directory.get_root().check_existence():
            raise ValidationError(_("The file structure needs to have a root node to create files."))
    
    def _validate_values(self, values):
        super(File, self)._validate_values(values)
           
    def _append_values_create(self, values):
        values = super(File, self)._append_values_create(values)
        rec_dir = self.env['muk_dms.directory'].sudo().browse([values['directory']])
        rec_root = rec_dir.get_root()
        
        if not rec_root.check_existence():
            raise ValidationError(_("The file structure needs to have a root node to create files."))
        
        if not 'file' in values:
            empty_file = StringIO.StringIO()
            empty_file.write(' ')
            values['file'] = base64.b64encode(empty_file.getvalue())
            empty_file.close()
        
        rec_file = self._create_file(values, rec_dir, rec_root)
        values['file_ref'] = rec_file._name + ',' + str(rec_file.id)

        values = self._set_filename_values(values, values['filename'])
        values = self._set_file_size(values, values['file'])
        return values

    def _onchange_values(self, values):
        super(File, self)._onchange_values(values)
        self.lock()
        
    def _append_values_write(self, values):
        values = super(File, self)._append_values_write(values)

        change_filename = False
        # 更新当前模型的文档，原文档并不删除
        #当前文件名和扩展名
        cur_file_name, cur_file_extension = os.path.splitext(self.filename)

        #没有指定文件名
        if 'filename' not in values:
            return values
        #没有指定文件内容信息
        if 'file' not in values:
            return  values
        new_file_name, new_file_extension = os.path.splitext( values['filename'])

        #新建一个 muk_dms_file 记录,新建的记录会复制当前记录的文件
        new_file_rec = self.copy_to(self.directory, None, self.filename)

        #记录文件变更历史记录,仍然在当前file_id 中更新新的文件名
        history = {
            'parent_id': new_file_rec.id,
            'file_id': self.id,
            'filename': self.filename,
            'version': self.version
        }
        self.env['muk_dms.file.history'].create(history)


        #更新关联模型 muk_dms_system_data 中的文件记录
        file_name, file_extension = os.path.splitext(values["filename"])
        file_vals={
            "filename":values['filename'],
            "file":values["file"],
            "file_extension":file_extension,
        }

        rec_dir = self.env['muk_dms.directory'].sudo().browse([values['directory']])
        rec_root = rec_dir.get_root()

        if not rec_root.check_existence():
            raise ValidationError(_("The file structure needs to have a root node to create files."))

        if not 'file' in values:
            empty_file = StringIO.StringIO()
            empty_file.write(' ')
            values['file'] = base64.b64encode(empty_file.getvalue())
            empty_file.close()

        rec_file = self._create_file(values, rec_dir, rec_root)
        values['file_ref'] = rec_file._name + ',' + str(rec_file.id)

        values = self._set_filename_values(values, values['filename'])
        values = self._set_file_size(values, values['file'])
        #self._update_file(data.REPLACE, file_vals)

        #返回参数给调用函数
        values['version'] = self.version + 1
        values["file_extension"]=file_extension
        return values

    
    def _follow_operation(self, values):
        super(File, self)._follow_operation(values)
        self.unlock()

    def _set_filename_values(self, values, filename):
        table = dict((ord(c), None) for c in "|\\?*<\":>+[]/'")
        filename = filename.translate(table).encode("utf-8")
        type, encoding = mimetypes.guess_type(urllib.pathname2url(filename))
        values['mime_type'] = type or 'application/octet-stream'
        file_name, file_extension = os.path.splitext(filename)
        values['file_extension'] = file_extension
        return values

    def _set_file_size(self, values, file):
        decode_file = base64.b64decode(file)
        values['file_size'] = len(decode_file)
        return values

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        i = 1
        filename = self.name + " " + str(i) + self.file_extension
        while len(self.directory.files.filtered(lambda r: r.filename == filename)) > 0:
            i = i + 1
            filename = self.name + " " + str(i) + self.file_extension
        return self.copy_to(self.directory, default, filename)
    
    def copy_to(self, newparent, default=None, filename=False):
        if not filename:
            filename = self.filename
        data = self.copy_data(default)[0]
        data['filename'] = filename
        data['file'] = self._get_file()
        data['directory'] = newparent.id
        new_id = self.with_context(lang=None).create(data)
        self.copy_translations(new_id)
        return new_id

    #----------------------------------------------------------
    # Delete
    #----------------------------------------------------------

    def prepare_unlink(self):
        _logger.debug("Unlinking reference file...")
        # 非物理删除，这里直接跳过
        #self._delete_file()
        pass

# 如果文件有更新，记录文件的历史版本。更新时将原文件copy一份作为历史文件
class FileLine(base.DMSModel):
    _name = 'muk_dms.file.history'
    _description = "File History"

    _inherit = ['muk_dms.access', 'mail.thread']

    parent_id = fields.Many2one('muk_dms.file', string="File", required=True)# 1.0版本的原始文件
    file_id = fields.Many2one('muk_dms.file', string="File", required=True)# 历史版本的文件
    filename = fields.Char(string='Filename', required=True)
    link_download = fields.Char(compute='_compute_link_download', string="Download Link")
    version = fields.Integer(string='Version', readonly=True, default=1)

    @api.one
    def _compute_link_download(self):
        config = self.env['ir.config_parameter'].search([('key', '=', 'web.server.url')], limit=1)
        self.link_download = config.value + "/dms/file/download/" + str(self.file_id.id)