# -*- coding: utf-8 -*-
from odoo import models, fields, api

def vendor_register_callback(self,context=None):
    """
    F01_B
    回调函数说明
    供应商注册第一步审核完成
    模型为 iac.vendor.regster
    context={"approve_status": True,"data":{"id":1376,"vendor_property":"Own Parts",}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """

def vendor_be_normal_callback(self,context=None):
    """
    F02_B
    回调函数说明
    供应商提供银行资料后审核通过变更为正常状态
    模型为 iac.vendor
    context={"approve_status": True,"data":{"id":1376,}}

    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """

def vendor_copy_callback(self,context=None):
    """
    F03_B
    回调函数说明
    供应商复制审核完成
    模型为iac.vendor.copy
    context={"approve_status": True,"data":{"id":1376,}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """


def vendor_change_basic_callback(self,context=None):
    """
    F04_B_1
    回调函数说明
    供应商修改基本资料审核完成
    模型为iac.vendor.change.basic
    context={"approve_status": True,"data":{"id":1376,}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """


def vendor_block_unblock_callback(self,context=None):
    """
    F04_B_2
    回调函数说明
    供应商状态变更审核完成
    模型为 iac.vendor.block
    context={"approve_status": True,"data":{"id":1376,}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """


def vendor_change_payment_incoterm_callback(self,context=None):
    """
    F04_B_3
    回调函数说明
    采购员修改支付信息审核完成
    模型为 iac.vendor.change.terms
    context={"approve_status": True,"data":{"id":1376,}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """


def vendor_spot_register_callback(self,context=None):
    """
    F05_B
    回调函数说明
    现货商注册审核完成
    模型为 iac.spot.vendor
    context={"approve_status": True,"data":{"id":1376,}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """


def rfq_group_new_callback(self,context=None):
    """
    F06_B
    回调函数说明
    rfq一个分组审核完成
    模型为 iac.rfq.group
    context={"approve_status": True,"data":{"id":1376,}}


    返回值有2个,第一个为布尔型,表示是否操作成功,第二个是异常信息列表为list类型
    :param context:
    :return:
    """