# -*- coding: utf-8 -*-

from odoo import models, fields, api
import urllib2
import json
import  requests
#hello.py

def call_with_request():
    json_data={"Input": {"Header": {"PASSWORD": "81d4d5174a34abfce8541c8d9ed8d345", "ODOO_KEY": "57", "INT_NO": "ODOO_FP_001"}, "Document": {"ITEM": [{"B2B_CONTROL": "Y", "OPTIME": "2018/02/02 15:40:02", "BU": "ALL", "ETA_TRANS": "30", "PLANT_CODE": "CP21", "OPERATOR": "Administrator", "CLASS": "ALL", "SAFETY_LT": "0", "FREQUENCY": "3", "TRANS_LT": "20", "FREQUENCY_PR": "7", "BUYER": "101", "VENDER": "0000380099", "TYPE": "ALL", "PULLING_TYPE": "SOI"}]}}, "inf_call_id": 1454}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url="http://10.2.254.182:5110/rest/IACEP.Odoo",data=json.dumps(json_data),headers=headers)
    print r.content

def call_with_url2():
    json_data={"Input": {"Header": {"PASSWORD": "81d4d5174a34abfce8541c8d9ed8d345", "ODOO_KEY": "57", "INT_NO": "ODOO_FP_001"}, "Document": {"ITEM": [{"B2B_CONTROL": "Y", "OPTIME": "2018/02/02 15:40:02", "BU": "ALL", "ETA_TRANS": "30", "PLANT_CODE": "CP21", "OPERATOR": "Administrator", "CLASS": "ALL", "SAFETY_LT": "0", "FREQUENCY": "3", "TRANS_LT": "20", "FREQUENCY_PR": "7", "BUYER": "101", "VENDER": "0000380099", "TYPE": "ALL", "PULLING_TYPE": "SOI"}]}}, "inf_call_id": 1454}
    json_data_str=json.dumps(json_data)
    headers = {'Content-Type': 'application/json'}
    request = urllib2.Request(url="http://10.2.254.182:5110/rest/IACEP.Odoo", data=json_data_str, headers=headers)
    response = urllib2.urlopen(request)
    json_obj_data = json.loads(response.read())
    print json_obj_data

if __name__ == "__main__":
    print 'request get json'
    call_with_request()

    print 'url2 get json'
    call_with_url2()
