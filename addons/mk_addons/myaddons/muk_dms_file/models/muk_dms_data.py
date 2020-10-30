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
import errno
import shutil
import base64
import hashlib
import logging

from contextlib import contextmanager

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError, MissingError

from odoo.addons.muk_dms.models import muk_dms_data as data
from docutils.parsers.rst.directives import path
import traceback
_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Static Functions
#----------------------------------------------------------

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

class SysFileDataModel(models.Model):
    _name = 'muk_dms.system_data'
    _description = 'System File Data Model'
    
    _inherit = 'muk_dms.data'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    filename = fields.Char(string="Filename")
    entry_path = fields.Char(string="Entry Path")
    path = fields.Char(string="Path")
    
    checksum = fields.Char(string="Checksum", readonly=True)
    save_file_name = fields.Char(string="Save File Name")
    #----------------------------------------------------------
    # Abstract Implementation
    #----------------------------------------------------------
    
    def get_type(self):
        return "File"
    
    def data(self):
        try:
            file_path = self.__build_path()
            file_content=self.__read_file(file_path)
            return file_content
        except:
            traceback.print_exc()
            raise
    
    def update(self, command, values):
        if str(command) is str(data.RENAME) and 'save_file_name' in values:
            file_save_name,file_save_path_name=self.__build_file_path_name(values.get("file_extension",False))
            self.filename = values['filename']
            self.save_file_name=file_save_name
            file = base64.decodestring(values['file'])
            self.checksum = self.__compute_checksum(file)
            self.__write_file(file_save_path_name, file)
        elif str(command) is str(data.REPLACE) and 'file' in values:
            file_save_name,file_save_path_name=self.__build_file_path_name(values.get("file_extension",False))
            self.filename = values['filename']
            self.save_file_name=file_save_name
            file = base64.decodestring(values['file'])
            self.checksum = self.__compute_checksum(file)
            self.__write_file(file_save_path_name, file)

            #file = base64.decodestring(values['file'])
            #file_path = self.__build_path()
            #self.__ensure_dir(file_path)
            #self.checksum = self.__compute_checksum(file)
            #check_sum_1=self.__compute_checksum(file)
            #check_sum_2=self.__compute_checksum(values['file'])
            #self.__write_file(file_path, file)
        elif str(command) is str(data.MOVE):
            new_entry_path = None
            new_path = None
            if 'entry_path' in values:
                new_entry_path = values['entry_path']
            if 'path' in values:
                new_path = values['path']
            old_file_path = self.__build_path()
            new_file_path = self.__build_path(entry_path=new_entry_path, path=new_path)
            if old_file_path==new_file_path:
                return
            self.__ensure_dir(new_file_path)
            self.__move_file(old_file_path, new_file_path)
            self.__remove_empty_directories(old_file_path)
            if new_entry_path:
                self.entry_path = new_entry_path
            if new_path:
                self.path = new_path
    
    def delete(self):
        file_path = self.__build_path()
        self.__delete_file(file_path)
        self.__remove_empty_directories(file_path)
    
    #----------------------------------------------------------
    # File Helper
    #----------------------------------------------------------

    def __build_file_path_name(self,file_extension=False):
        """
        只能由muk_dms_system_data 模型记录调用
        通过当前记录的内容构建 文件路径
        :return:
        """
        #return os.path.join(entry_path or self.entry_path, path or self.path,
        #                    filename or self.filename).replace("\\", "/")
        file_save_name=""
        if file_extension!=False:
            file_save_name="%s%s"%(self.id,file_extension)
        else:
            file_save_name=str(self.id)
        file_path_name=  os.path.join(self.entry_path,self.path,file_save_name).replace("\\", "/")
        return file_save_name,file_path_name


    def __build_path(self, entry_path=None, path=None, filename=None):
        #return os.path.join(entry_path or self.entry_path, path or self.path,
        #                    filename or self.filename).replace("\\", "/")
        os_file_path=  os.path.join(entry_path or self.entry_path, path or self.path,
                                                 filename or self.save_file_name or self.filename).replace("\\", "/")
        return os_file_path

    def __ensure_dir(self, file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
                    _logger.error("Failed to create the necessary directories: " + str(exc))
                    raise AccessError(_("The System failed to create the necessary directories."))
    
    def __compute_checksum(self, file):
        return hashlib.sha1(file).hexdigest()
    
    def __check_file(self, file, checksum):
        return hashlib.sha1(file).hexdigest() == checksum
    
    def __delete_file(self, file_path):
        try:
            os.remove(file_path)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                _logger.error("Failed to delete the file: " + str(exc))
                raise AccessError(_("The System failed to delete the file."))
            
    def __remove_empty_directories(self, file_path):
        try:
            os.removedirs(os.path.dirname(file_path))
        except OSError as exc:
            if exc.errno != errno.ENOTEMPTY:
                _logger.error("Failed to remove empty directories: " + str(exc))
                raise AccessError(_("The System failed to delete a directory."))
            
    def __move_file(self, old_file_path, new_file_path):
        try:
            shutil.move(old_file_path, new_file_path)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                _logger.error("Failed to move the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                _logger.error("Failed to move the file: " + str(exc))
                raise AccessError(_("The System failed to rename the file."))
    
    def __read_file(self, file_path):
        with opened_w_error(file_path, "rb") as (file_handler, exc):
            if exc:
                _logger.error("Failed to read the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                #file = file_handler.read()
                #encode_file = base64.b64encode(file)
                #print 'file hash:'+str(hashlib.sha1(file).hexdigest())
                #print self.checksum
                #return encode_file
                file = file_handler.read()
                encode_file = base64.b64encode(file)
                if self.__check_file(file, self.checksum):
                    return encode_file
                else:
                    _logger.error("Failed to read the file: The file has been altered outside of the system.")
                    raise ValidationError(_("The file is corrupted."))
            
    def __write_file(self, file_path, file):
        with opened_w_error(file_path, "wb") as (file_handler, exc):
            if exc:
                ex_alert_msg="The System failed to write the file %s .System error info is: %s"\
                             %(file_path,exc.strerror)
                _logger.error(ex_alert_msg)
                raise AccessError(_(ex_alert_msg))
            else:
                file_handler.write(file)
            

    def __read_file_nocheck(self, file_path):
        with opened_w_error(file_path, "rb") as (file_handler, exc):
            if exc:
                _logger.error("Failed to read the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                #file = file_handler.read()
                #encode_file = base64.b64encode(file)
                #print 'file hash:'+str(hashlib.sha1(file).hexdigest())
                #print self.checksum
                #return encode_file
                file = file_handler.read()
                encode_file = base64.b64encode(file)
                return file

    def recompute_checksum(self):
        """
        重新计算当前文件对象的checksum,并且返回
        :return:
        """
        file_path = self.__build_path()
        file_content=self.__read_file_nocheck(file_path)
        new_checksum=self.__compute_checksum(file_content)
        return new_checksum

    def test_checksum(self):
        """
        验证记录中的checksum 是否和从文件中获取的相同
        :return:
        """
        new_checksum=self.recompute_checksum()
        if new_checksum==self.checksum:
            return True
        else:
            return False

    def copy_to_fix(self):
        """
        处理文件命名不符合规则的情况，文件存储应该符合 id+ 文件扩展名的规则
        :param newparent:
        :param default:
        :param filename:
        :return:
        """
        #获取文件扩展名
        cur_file_name, cur_file_extension = os.path.splitext(self.save_file_name)
        file_ref_vals=self.copy_data()[0]
        file_ref_rec=self.env["muk_dms.system_data"].create(file_ref_vals)
        old_path_name=self.__build_path()
        #获取新的文件名称存储名称和存储路径
        new_file_name,new_path_name=file_ref_rec.__build_file_path_name(cur_file_extension)
        #判断对应的文件存储路径是否被占用
        if (not os.path.exists(new_path_name)):#如果文件存储路径没有占用的情况下,复制原文件然后更新记录
            shutil.copyfile(old_path_name,new_path_name)
            file_ref_rec.save_file_name=new_file_name
            return file_ref_rec
        else:
            #文件存储路径被占用那么进行递归调用直到存在未被占用的路径为止
            result_rec=self.copy_to_fix()
            return result_rec