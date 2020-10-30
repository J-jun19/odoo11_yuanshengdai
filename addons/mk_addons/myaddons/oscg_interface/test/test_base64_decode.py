# -*- coding: utf-8 -*-
from decimal import Decimal
import math

from odoo.tools import float_utils
from contextlib import contextmanager
import xlrd
import base64
import hashlib
import json


dic ={}

def get_base64_val(str_val):
    try:
        result_str=base64.b64decode(str_val)
    except:
        result_str=str_val
    return result_str

def get_json_base64(dic_json):
    result_dict={}
    for key in dic_json:
        if isinstance(dic_json[key],dict):#如果dic_json[key]依旧是字典类型
            #print("****key--：%s value--: %s"%(key,dic_json[key]))
            sub_dict=get_json_base64(dic_json[key])
            result_dict[key] = sub_dict
        elif isinstance(dic_json[key],list):
            value_list=[]
            for item_val in dic_json[key]:
                if isinstance(item_val,dict):
                    #构成数组的元素是dict那么递归调用
                    sub_dict=get_json_base64(item_val)
                    value_list.append(sub_dict)
                else:
                    #构成数组的元素是普通值
                    value_list.append(item_val)
            result_dict[key] = value_list
        else:
            result_dict[key] = get_base64_val(dic_json[key])
    return result_dict



if __name__ == "__main__":
    str_test="""
    {"status": "true", "FormStatus": "C", "jsonrpc": "2.0", "id": 15339, "tokens": ["aHR0cDovL3d3dy5vc2NnLmNuLCBJQUNfREIsIGFkbWluLCAxLCAxNTM0NzI5NjUw"], "params": {"sitesurvey": "N", "Comments": [{"Comment": "JCMkI0c8Pg==", "stage": "CM"}], "Score": [], "File": [{"Memo": "", "File_ID": 156871, "ExpirationDate": ""}, {"Memo": "", "File_ID": 156872, "ExpirationDate": ""}, {"Memo": "IUAjJCVeJiooPD4=", "File_ID": 156878, "ExpirationDate": "2018/08/23"}], "FlowList": [{"Timestamp": "2018/08/20 09:38:32", "Approver": "\u9ec3\u91d1\u679d", "Comments": "QXBwbHku", "Stage": "\u958b\u59cb"}, {"Timestamp": "2018/08/20 09:40:43", "Approver": "\u694a\u5a6d\u59e3", "Comments": "QXBwcm92ZS4=", "Stage": "QS_Engineer"}, {"Timestamp": "2018/08/20 09:40:57", "Approver": "\u738b\u7d00\u7d05", "Comments": "QXBwcm92ZS4=", "Stage": "QS_Engineer"}, {"Timestamp": "2018/08/20 09:44:39", "Approver": "\u675c\u4eac\u5065", "Comments": "QXBwcm92ZS4=", "Stage": "CM"}, {"Timestamp": "2018/08/20 09:44:53", "Approver": "\u738b\u5cfb\u5cf0", "Comments": "QXBwcm92ZS4=", "Stage": "BU_Leader"}, {"Timestamp": "2018/08/20 09:45:07", "Approver": "\u7687\u752b\u5ba3\u5f6c", "Comments": "QXBwcm92ZS4=", "Stage": "QM_Leader"}, {"Timestamp": "2018/08/20 11:16:15", "Approver": "\u5f35\u77e5\u97f3", "Comments": "Approve.", "Stage": "GM"}, {"Timestamp": "2018/08/20 11:16:15", "Approver": "", "Comments": "", "Stage": "\u7d50\u675f"}], "vendor_property": "Own Parts"}, "EFormNO": "NVC201808200002", "message": "", "stage": "F01_E", "method": "call", "inf_call_id": "282489"}
    """
    encode_json=json.loads(str_test)
    result=get_json_base64(encode_json)
    print result
    result_str=base64.b64decode("QXBwcm92ZS4=")
    print result_str

    result_str=base64.encodestring("!!!!!{}{|??><>")
    print result_str

    result_str=base64.decodestring(result_str)
    print result_str

    test_str="ISEhISF7fXt8Pz8 PD4="
    test_str=test_str.replace(" ","+")
    print test_str

