# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval as eval
import urllib2
import json
import time
import datetime
import traceback
import sys
import types

class JSONFieldBuilderException(Exception):
    """
    FieldBuilder的异常处理基础类
    """
    def __init__(self,field_builder):
        self.field_builder=field_builder
        self.exception_log=[]

    def generate_exception_info(self):
        pass

    def get_exception_log(self):
        return self.exception_log
        pass

class JSONScriptFieldBuilderException(JSONFieldBuilderException):
    """
    FieldBuilder的异常处理基础类
    """
    def __init__(self,field_builder,eval_script,system_ex_msg):
        super(JSONScriptFieldBuilderException,self).__init__(field_builder)
        self.generate_exception_info(eval_script,system_ex_msg)

    def generate_exception_info(self,eval_script,system_ex_msg):
        exception_str="A exception is raised when eval script field value , " \
                      "interface is ( %s ) ," \
                      "field builder id is:( %s ) ,builder_var_context is( \"%s\" ), " \
                      "eval script text is( \"%s\" ), " \
                      "JSON field path is %s/%s," \
                      "System exception  is ( %s );" \
                      %(self.field_builder.builder_line.interface_id.id,
                        self.field_builder.builder_line.id,
                        self.field_builder.builder_line.builder_id.builder_var_context,
                        eval_script,
                        self.field_builder.builder_line.json_field_path,
                        self.field_builder.builder_line.json_field_name,
                        system_ex_msg
        )
        self.exception_log.append(exception_str)

class JSONFieldBuilderFactoryException(Exception):
    """
    JSONFieldBuilderFactory的异常处理的基础类
    生成工厂类在产生FieldBuilder过程中产生的异常信息
    """
    def __init__(self,builder_line):
        self.builder_line=builder_line
        self.exception_log=[]
        self.generate_exception_info()

    def generate_exception_info(self):
        pass

    def get_exception_log(self):
        return self.exception_log
        pass

class JSONFieldBuilderFactoryTypeException(JSONFieldBuilderFactoryException):
    """
    JSONFieldBuilderFactory的异常处理的类在遇到未知类型无法创建FieldBuilder 时候引发
    生成工厂类在产生FieldBuilder过程中产生的异常信息
    """
    def __init__(self,builder_line):
        super(JSONFieldBuilderFactoryTypeException,self).__init__(builder_line)


    def generate_exception_info(self):
        exception_str="A exception is raised when create field builder , " \
                      "interface is ( %s ) ," \
                      "field builder id is:( %s ) , " \
                      "unknown field type group :json_field_type is( \"%s\") ," \
                      " source_field_type is( \"%s\") ," \
                      "JSON field path is %s//%s" \
                      %(self.builder_line.interface_id.id,
                        self.builder_line.id,
                        self.builder_line.json_field_type,
                        self.builder_line.source_field_type,
                        self.builder_line.json_field_path,
                        self.builder_line.json_field_name,
        )
        self.exception_log.append(exception_str)
        pass


class JSONBuilderDirectorException(Exception):
    """
    JSONBuilderDirector的异常处理的基础类
    生成工厂类在产生FieldBuilder过程中产生的异常信息
    """
    def __init__(self,field_list_builder):
        self.field_list_builder=field_list_builder
        self.exception_log=[]
        self.generate_exception_info()

    def generate_exception_info(self):
        pass

    def get_exception_log(self):
        return self.exception_log
        pass


class JSONBuilderDirectorBizObjectParseException(Exception):
    """
    JSONBuilderDirector的解析业务对象参数产生的异常
    """
    def __init__(self,field_list_builder):
        self.exception_log=[]
        super(JSONBuilderDirectorBizObjectParseException,self).__init__(field_list_builder)

    def generate_exception_info(self):
        exception_str="A fatal exception is raised when parse biz object params , " \
                      "biz object str is ( %s ) ," \
                      %(self.field_list_builder.context["biz_obj_str"],)
        self.exception_log.append(exception_str)
        pass

    def get_exception_log(self):
        return self.exception_log
        pass


class JSONFieldListBuilder(object):
    """
    字段列表构建基础类
    """
    def __init__(self,builder_lines,context):
        self.builder_lines=builder_lines
        self.context=context
        self.json_bag={}
        self.exception_log=[]

    def execute_action(self):
        pass

    def travel_field_list(self):
        try:
            self.execute_action()
        except JSONFieldBuilderException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            self.exception_log.append(ex_string)
            traceback.print_exc()

        except JSONFieldBuilderFactoryException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            traceback.print_exc()
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            self.exception_log.append(ex_string)
            print ex.get_exception_log()
        except:
            #处理未捕获的异常信息
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            self.exception_log.append(ex_string)
            traceback.print_exc()

class JSONObjectFieldListBuilder(JSONFieldListBuilder):
    """
    传入的数据集只有一条记录,这种情况下使用这个建造类
    返回字典类型JSON对象
    """
    def __init__(self,builder_lines,context):
        super(JSONObjectFieldListBuilder,self).__init__(builder_lines,context)


    def execute_action(self):
        for builder_line in self.builder_lines:
            field_builder=JSONFieldBuilderFactory.create_field_builder(builder_line,self.context)
            field_builder.calc_field_val()
            #收集field_builder发生的异常信息
            self.exception_log=self.exception_log+field_builder.exception_log
            self.json_bag[field_builder.field_name]=field_builder.json_val_obj
            pass

class JSONArrayFieldListBuilder(JSONFieldListBuilder):
    """
    当传入的记录集包含多条记录的情况下
    JSON容器为数组类型[]
    """
    def __init__(self,builder_lines,context):
        super(JSONArrayFieldListBuilder,self).__init__(builder_lines,context)

    def execute_action(self):
        field_builder_list=[]
        #重新定义json_bag类型
        self.json_bag=[]
        #首先获取全部的field_builder
        for builder_line in self.builder_lines:
            field_builder=JSONFieldBuilderFactory.create_field_builder(builder_line,self.context)
            field_builder_list.append(field_builder)


        #遍历数据集，组织json_bag数据
        rs=self.context["rs"]
        for rec in rs:
            item_val={}
            #遍历field_fuilder
            for field_builder in field_builder_list:
                field_builder.context.update({"rs":rec})
                field_builder.calc_field_val()
                #收集field_builder发生的异常信息
                self.exception_log=self.exception_log+field_builder.exception_log
                item_val[field_builder.field_name]=field_builder.json_val_obj

            #填充完成一条记录的时候,填充到json_bag中
            self.json_bag.append(item_val)




class JSONFieldBuilder(object):
    def __init__(self,builder_line,context):
        self.builder_line=builder_line
        self.field_name=builder_line.json_field_name
        self.context=context
        self.json_val_obj={}
        self.exception_log=[]

    def execute_action(self):
        pass

    def calc_field_val(self):
        try:
            self.execute_action()
        except JSONFieldBuilderException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            traceback.print_exc()
            print ex.get_exception_log()
        except JSONFieldBuilderFactoryException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            traceback.print_exc()
            print ex.get_exception_log()
        except:

            #处理未捕获的异常信息
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            self.exception_log.append(ex_string)
            traceback.print_exc()

    def trans_type_data(self,eval_val):
        """
        对数据类型进行转换，符合json的格式
        """
        result=""
        if ((type(eval_val) is types.FloatType ) or
                (type(eval_val) is types.IntType)):
            result=str(eval_val)
            return result

        elif (type(eval_val) is types.BooleanType):
            #处理获取字段为空值的情况
            if eval_val==False:
                result=""
                return result
            else:
                result="true"
                return result
        else:
            return eval_val


class JSONScriptFieldBuilder(JSONFieldBuilder):
    def __init__(self,builder_line,context):
        super(JSONScriptFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        try:
            self.json_val_obj=self.trans_type_data(eval(self.builder_line.builder_id.builder_var_context,self.context))
        except:
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            traceback.print_exc()
            raise JSONScriptFieldBuilderException(self,self.builder_line.builder_id.builder_var_context,ex_info)

class JSONObjectFieldBuilder(JSONFieldBuilder):
    """
    对象类型字段,这里指的是通过odoo模型获取数据
    只获取一条记录
    """
    def __init__(self,builder_line,context):
        super(JSONObjectFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        odoo_model_name=self.builder_line.builder_id.odoo_model_name
        search_context=[]
        try:
            search_context=eval(self.builder_line.builder_id.builder_var_context,self.context)
        except:
            raise JSONScriptFieldBuilderException(self,self.builder_line.builder_id.builder_var_context)
        odoo_env=self.context["env"]
        result_rs=odoo_env[odoo_model_name].search(search_context)

        #获取下级builder_lines
        builder_lines=odoo_env["iac.interface.json.builder.line"].search([('parent_field_id','=',self.builder_line.id)])
        child_context={}
        child_context.update(self.context)
        child_context["rs"]=result_rs
        field_list=JSONObjectFieldListBuilder(builder_lines,child_context)
        field_list.travel_field_list()
        self.json_val_obj=field_list.json_bag

        #收集field_list_builder发生的异常信息
        self.exception_log=self.exception_log+field_list.exception_log


class JSONArrayFieldBuilder(JSONFieldBuilder):
    """
    数组类型字段,这里指的是通过odoo模型获取数据
    获取的数据是一个数据集
    """
    def __init__(self,builder_line,context):
        super(JSONArrayFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        odoo_model_name=self.builder_line.builder_id.odoo_model_name
        search_context=eval(self.builder_line.builder_id.builder_var_context,self.context)
        odoo_env=self.context["env"]
        result_rs=odoo_env[odoo_model_name].search(search_context)

        #获取下级builder_lines
        builder_lines=odoo_env["iac.interface.json.builder.line"].search([('parent_field_id','=',self.builder_line.id)])
        child_context={}
        child_context.update(self.context)
        child_context["rs"]=result_rs
        field_list=JSONArrayFieldListBuilder(builder_lines,child_context)
        field_list.travel_field_list()
        self.json_val_obj=field_list.json_bag

        #收集field_list_builder发生的异常信息
        self.exception_log=self.exception_log+field_list.exception_log


class JSONOdooRelationOne2ManyFieldBuilder(JSONFieldBuilder):
    """
    odoo的模型关联类型字段,这里指的是通过odoo模型中的one2many
    当前对象会依赖一个JSONArrayFieldListBuilder来获取json_val_obj
    """
    def __init__(self,builder_line,context):
        super(JSONOdooRelationOne2ManyFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        eval_script="rs.%s"%(self.builder_line.source_field_name,)
        child_rs={}
        try:
            child_rs=eval(eval_script,self.context)
        except:
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            raise JSONScriptFieldBuilderException(self,eval_script,ex_string)


        child_context={}
        child_context.update(self.context)
        child_context["rs"]=child_rs

        odoo_env=self.context["env"]
        #获取下级builder_lines
        builder_lines=odoo_env["iac.interface.json.builder.line"].search([('parent_field_id','=',self.builder_line.id)])

        field_list=JSONArrayFieldListBuilder(builder_lines,child_context)
        field_list.travel_field_list()
        self.json_val_obj=field_list.json_bag

        #收集field_list_builder发生的异常信息
        self.exception_log=self.exception_log+field_list.exception_log


class JSONOdooRelationMany2OneFieldBuilder(JSONFieldBuilder):
    """
    odoo的模型关联类型字段,这里指的是通过odoo模型中的many2one
    当前对象会依赖一个JSONArrayFieldListBuilder来获取json_val_obj
    """
    def __init__(self,builder_line,context):
        super(JSONOdooRelationMany2OneFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        eval_script="rs.%s"%(self.builder_line.source_field_name,)
        child_rs={}
        try:
            child_rs=eval(eval_script,self.context)
        except:
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            raise JSONScriptFieldBuilderException(self,eval_script,ex_string)


        child_context={}
        child_context.update(self.context)
        child_context["rs"]=child_rs

        odoo_env=self.context["env"]
        #获取下级builder_lines
        builder_lines=odoo_env["iac.interface.json.builder.line"].search([('parent_field_id','=',self.builder_line.id)])

        field_list=JSONObjectFieldListBuilder(builder_lines,child_context)
        field_list.travel_field_list()
        self.json_val_obj=field_list.json_bag

        #收集field_list_builder发生的异常信息
        self.exception_log=self.exception_log+field_list.exception_log

class JSONOdooSimpleFieldBuilder(JSONFieldBuilder):
    """
    odoo的模型关联类型字段,这里指的是通过odoo模型中的各种简单类型
    例如:integer char many2one
    这种情况下从数据集中结合source_field_name获取字段的值
    """
    def __init__(self,builder_line,context):
        super(JSONOdooSimpleFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):

        eval_script="rs.%s"%(self.builder_line.source_field_name,)
        eval_val=""
        try:
            eval_val=eval(eval_script,self.context)
        except:
        #处理未捕获的异常信息
            traceback.print_exc()
            raise JSONScriptFieldBuilderException(self,eval_script,traceback.format_exc())
        if type(eval_val) is types.BooleanType:
            pass
        if ((type(eval_val) is types.FloatType ) or
            (type(eval_val) is types.IntType)):
            self.json_val_obj=str(eval_val)
        elif (type(eval_val) is types.BooleanType):
            #处理获取字段为空值的情况
            if eval_val==False:
                eval_script="rs.%s==False"%(self.builder_line.source_field_name,)
                eval_val=eval(eval_script,self.context)
                if (eval_val==True):
                    self.json_val_obj=""
            else:
                self.json_val_obj=eval_val
        else:
            self.json_val_obj=eval_val

class JSONOdooDatetimeFieldBuilder(JSONFieldBuilder):
    """
    odoo的模型关联类型字段,这里指的是通过odoo模型中的Datetime
    日期类型需要做自定义格式化
    这种情况下从数据集中结合source_field_name获取字段的值
    获取到字符串之后再做自定义格式化
    """
    def __init__(self,builder_line,context):
        super(JSONOdooDatetimeFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        eval_script="rs.%s"%(self.builder_line.source_field_name,)
        eval_val=eval(eval_script,self.context)
        #time_str=time.strftime('%Y/%m/%d %H:%M:%S',time.strptime(eval_val,'%Y-%m-%d %H:%M:%S'))
        #self.json_val_obj=time_str
        if eval_val==False:
            self.json_val_obj=""
            return

        time_str=""
        if "config" in self.context:
            config=self.context.get("config")
            if "default_datetime_format" in config:
                default_date_format=config.get("default_datetime_format")
                time_str=time.strftime(default_date_format,time.strptime(eval_val,'%Y-%m-%d %H:%M:%S'))
            else:
                time_str=time.strftime('%Y/%m/%d %H:%M:%S',time.strptime(eval_val,'%Y-%m-%d %H:%M:%S'))
        else:
            time_str=time.strftime('%Y/%m/%d %H:%M:%S',time.strptime(eval_val,'%Y-%m-%d %H:%M:%S'))
        self.json_val_obj=time_str


class JSONOdooDateFieldBuilder(JSONFieldBuilder):
    """
    odoo的模型关联类型字段,这里指的是通过odoo模型中的Date
    日期类型需要做自定义格式化
    这种情况下从数据集中结合source_field_name获取字段的值
    获取到字符串之后再做自定义格式化
    """
    def __init__(self,builder_line,context):
        super(JSONOdooDateFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):
        eval_script="rs.%s"%(self.builder_line.source_field_name,)
        eval_val=eval(eval_script,self.context)

        if eval_val==False:
            self.json_val_obj=""
            return

        time_str=""
        if "config" in self.context:
            config=self.context.get("config")
            if "default_date_format" in config:
                default_date_format=config.get("default_date_format")
                time_str=time.strftime(default_date_format,time.strptime(eval_val,'%Y-%m-%d'))
            else:
                time_str=time.strftime('%Y/%m/%d',time.strptime(eval_val,'%Y-%m-%d'))
        else:
            time_str=time.strftime('%Y/%m/%d',time.strptime(eval_val,'%Y-%m-%d'))
        self.json_val_obj=time_str


class JSONOdooNameListFieldBuilder(JSONFieldBuilder):
    """
    odoo的模型关联类型字段,这里指的是通过odoo模型中的many2many关联
    通过关联获取关联数据集的name属性列表,获取到这个列表
    """
    def __init__(self,builder_line,context):
        super(JSONOdooNameListFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):

        eval_script="rs.%s"%(self.builder_line.source_field_name,)
        relation_rs=eval(eval_script,self.context)

        #遍历关联数据集
        name_list=[]
        for rec in relation_rs:
            name_list.append(rec.name)
        self.json_val_obj=name_list





class JSONDictionaryFieldBuilder(JSONFieldBuilder):
    """
    字典类型字段,作为容器字段,本身不能获取数据,作为 JSONObjectFiledBuilder 或者 JSONArrayFiledBuilder
    的容器存在
    """
    def __init__(self,builder_line,context):
        super(JSONDictionaryFieldBuilder,self).__init__(builder_line,context)

    def execute_action(self):

        odoo_env=self.context["env"]

        #获取模型环境,如果存在的情况下
        if (self.builder_line.builder_id.id!=False):
            odoo_model_name=self.builder_line.builder_id.odoo_model_name
            #builder_var_context=self.builder_line.builder_id.builder_var_context
            search_context=eval(self.builder_line.builder_id.builder_var_context,self.context)
            odoo_env=self.context["env"]
            result_rs=odoo_env[odoo_model_name].search(search_context)
            self.context["rs"]=result_rs

        #获取下级builder_lines
        builder_lines=odoo_env["iac.interface.json.builder.line"].search([('parent_field_id','=',self.builder_line.id)])

        for builder_line in builder_lines:
            field_builder=JSONFieldBuilderFactory.create_field_builder(builder_line,self.context)
            field_builder.calc_field_val()
            self.json_val_obj[field_builder.field_name]=field_builder.json_val_obj
            #收集field_list_builder发生的异常信息
            self.exception_log=self.exception_log+field_builder.exception_log

class JSONFieldBuilderFactory:
    @staticmethod
    def create_field_builder(builder_line,context=None):
        if (builder_line.json_field_type=='eval script'):
            field_builder=JSONScriptFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='object'):
            field_builder=JSONObjectFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='array'):
            field_builder=JSONArrayFieldBuilder(builder_line,context)
            return field_builder



        elif (builder_line.json_field_type=='simple type') and \
                (builder_line.source_field_type=='datetime') :
            field_builder=JSONOdooDatetimeFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='simple type') and \
                (builder_line.source_field_type=='date') :
            field_builder=JSONOdooDateFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='simple type') and \
                (builder_line.json_field_type<>'date') and \
                (builder_line.json_field_type<>'datetime'):
            field_builder=JSONOdooSimpleFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='relation travel') and \
                ((builder_line.source_field_type=='one2many')   ) :
            field_builder=JSONOdooRelationOne2ManyFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='relation travel') and \
                ((builder_line.source_field_type=='many2one')  ) :
            field_builder=JSONOdooRelationMany2OneFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='name list') and \
                (builder_line.source_field_type=='many2many') :
            field_builder=JSONOdooNameListFieldBuilder(builder_line,context)
            return field_builder

        elif (builder_line.json_field_type=='dict') :
            field_builder=JSONDictionaryFieldBuilder(builder_line,context)
            return field_builder
        else:
            raise JSONFieldBuilderFactoryTypeException(builder_line)
            #print("Error No Field Builder Found")

class JSONBuilderDirector:
    def __init__(self,context,field_list_builder):
        self.field_list_builder=field_list_builder
        self.exception_log=[]
        self.context={}
        self.context=context

    def execute_action(self):
        try:
            #计算得到参数字符串对应json对象,并且副給下级对象
            #eval_script=self.field_list_builder.context.get("biz_object_str")
            #eval_val=eval(eval_script,self.field_list_builder.context)
            self.field_list_builder.context["params"]=self.context["params"]

            #赋予导演对象的环境变量给下一级对象
            self.field_list_builder.context["config"]=self.context
            #self.context["params"]=eval_val
        except:
            raise JSONBuilderDirectorBizObjectParseException(self.field_list_builder)

        self.field_list_builder.travel_field_list()
        json_obj_data=self.field_list_builder.json_bag

        #获取field_list_builder的异常信息
        self.exception_log=self.exception_log+self.field_list_builder.exception_log
        return json_obj_data

    def build_json_obj(self):
        json_obj_data={}
        try:
            json_obj_data=self.execute_action()
        except JSONFieldBuilderException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            traceback.print_exc()
        except JSONFieldBuilderFactoryException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            traceback.print_exc()
        except JSONBuilderDirectorBizObjectParseException,ex:
            self.exception_log=self.exception_log+ex.get_exception_log()
            traceback.print_exc()
        except:
            #处理未捕获的异常信息
            ex_info=sys.exc_info()
            ex_string="%s : %s"%(ex_info[0],ex_info[1])
            self.exception_log.append(ex_string)
            traceback.print_exc()

        return json_obj_data