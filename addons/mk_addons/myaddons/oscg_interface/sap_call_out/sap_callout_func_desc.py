# <<<<<<< HEAD
# # -*- coding: utf-8 -*-
# from odoo import models, fields, api
# """
# ODOO_ASN_001
# ODOO_ASN_002
# ODOO_ASN_003
# ODOO_ASN_004
# ODOO_ASN_005
# ODOO_ASN_006
# ODOO_ASN_007
# ODOO_ASN_008
#
# """
#
# """
# ODOO_ASN_005 接口
# 调用模型 iac.interface.rpc 的 invoke_web_call_with_log 方法
# 入口参数有2个
# 1   接口代码 interface_code='ODOO_ASN_005'
# 2   接口json 参数
#  biz_object={
#             "id":1,
#             "biz_object_id":1
#         }
# id 和 biz_object_id 相等为一个序列
# """
#
#
# def odoo_vendor_001_callback(self,context=None):
#     """
#     业务说明,新建SAP Normal廠商資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "vendor_code":"0000458888",
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#             "Document": {
#                 "VENDOR": "0000458888"
#             }
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
# def odoo_vendor_002_callback(self,context=None):
#     """
#     业务说明,新建SAP現貨商,模具廠商,BVI等資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "vendor_code":"0000458888",
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#             "Document": {
#                 "VENDOR": "0000458888"
#             }
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
# def odoo_vendor_003_callback(self,context=None):
#     """
#     业务说明,修改SAP廠商基本資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
# def odoo_vendor_004_callback(self,context=None):
#     """
#     业务说明,SAP 廠商Block or Unblock
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
# def odoo_vendor_005_callback(self,context=None):
#     """
#     业务说明,SAP  廠商Delete or UnDelete
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
#
# def odoo_vendor_006_callback(self,context=None):
#     """
#     业务说明,更新SAP中廠商等級資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#             "Document": {
#                 "VENDOR": "0000458888"
#             }
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
# =======
# # -*- coding: utf-8 -*-
# from odoo import models, fields, api
# """
# ODOO_ASN_001
# ODOO_ASN_002
# ODOO_ASN_003
# ODOO_ASN_004
# ODOO_ASN_005
# ODOO_ASN_006
# ODOO_ASN_007
# ODOO_ASN_008
#
# """
#
# """
# ODOO_ASN_005 接口
# 调用模型 iac.interface.rpc 的 invoke_web_call_with_log 方法
# 入口参数有2个
# 1   接口代码 interface_code='ODOO_ASN_005'
# 2   接口json 参数
#  biz_object={
#             "id":1,
#             "biz_object_id":1
#         }
# id 和 biz_object_id 相等为一个序列
# """
#
#
# def odoo_vendor_001_callback(self,context=None):
#     """
#     业务说明,新建SAP Normal廠商資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "vendor_code":"0000458888",
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#             "Document": {
#                 "VENDOR": "0000458888"
#             }
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
# def odoo_vendor_002_callback(self,context=None):
#     """
#     业务说明,新建SAP現貨商,模具廠商,BVI等資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "vendor_code":"0000458888",
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#             "Document": {
#                 "VENDOR": "0000458888"
#             }
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
# def odoo_vendor_003_callback(self,context=None):
#     """
#     业务说明,修改SAP廠商基本資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
# def odoo_vendor_004_callback(self,context=None):
#     """
#     业务说明,SAP 廠商Block or Unblock
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
# def odoo_vendor_005_callback(self,context=None):
#     """
#     业务说明,SAP  廠商Delete or UnDelete
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
#     """
#
#
#
# def odoo_vendor_006_callback(self,context=None):
#     """
#     业务说明,更新SAP中廠商等級資料
#     实现方法模型  iac.vendor
#     context 参数实例如下:
#     id 是vendor_id
#     {
#         "id": 1083,
#         "rpc_callback_data": {
#             "Message": {
#                 "Status": "Y",
#                 "Message": "SUCCESS"
#             },
#             "Document": {
#                 "VENDOR": "0000458888"
#             }
#         }
#     }
#
#     返回参数有2个
#     1   布尔类型,表示业务处理成功或者失败
#     2   异常信息列表
#     :param context:
#     :return:
# >>>>>>> f6498de7849a2141be64504780ef85df2f63ec10
#     """