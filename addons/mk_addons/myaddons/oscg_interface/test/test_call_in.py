# -*- coding: utf-8 -*-

from odoo import models, fields, api
import urllib2
import json
import  requests
#hello.py
def sayHello():
    str="hello"
    print(str);

def test_log_in():
    pass

def test_call_method():
    json_para={

    }
    json_data={
        "status":"true",
        "FormStatus":"C",
        "jsonrpc":"2.0",
        "id":13,
        "tokens":[
            "aHR0cDovL3d3dy5vc2NnLmNuLCBJQUNfREIsIGFkbWluLCAxLCAxNTIxODY5MTIy"
        ],
        "params":{
            "FlowList":[
                {
                    "Timestamp":"2018/03/24 13:54:21",
                    "Approver":"陳艷",
                    "Comments":"申請.",
                    "Stage":"開始"
                },
                {
                    "Timestamp":"2018/03/24 13:58:46",
                    "Approver":"許淑惠",
                    "Comments":"送件.",
                    "Stage":"AS_Manager"
                },
                {
                    "Timestamp":"2018/03/24 13:59:00",
                    "Approver":"林瑜文",
                    "Comments":"送件.",
                    "Stage":"CM_Manager"
                },
                {
                    "Timestamp":"2018/03/24 13:59:10",
                    "Approver":"曾煜霖",
                    "Comments":"送件.",
                    "Stage":"*MM_Manager"
                },
                {
                    "Timestamp":"2018/03/24 13:59:10",
                    "Approver":"",
                    "Comments":"",
                    "Stage":"結束"
                }
            ]
        },
        "EFormNO":"POC201803240019",
        "message":"",
        "stage":"F07_E_2",
        "method":"call",
        "inf_call_id":"96"
    }

    data={"jsonrpc":"2.0","method":"call","inf_call_id":"527","stage":"F07_E_2","id":10,"params":{"FlowList":[{"Stage":"開始","Timestamp":"2018/06/25 15:40:02","Approver":"吳美先","Comments":"申請."},{"Stage":"AS_Manager","Timestamp":"2018/06/26 19:36:15","Approver":"許淑惠","Comments":"送件."},{"Stage":"CM_Manager","Timestamp":"2018/06/26 21:34:28","Approver":"林瑜文","Comments":"送件.mail : 2018/6/22 (週五) 下午 01:26 &lt;申請不列入cost up查核 (Venus_381320_6019A1203701)&gt;"},{"Stage":"MM_Manager","Timestamp":"2018/06/28 08:56:25","Approver":"曾煜霖","Comments":"Approve."},{"Stage":"結束","Timestamp":"2018/06/28 08:56:25","Approver":"","Comments":""}]},"FormStatus":"C","EFormNO":"POC201806250054","status":"true","message":""}
    json_para["data"]=data
    json_str=json.dumps(json_para)
    #print json_str
    payload = {'data': json_str}
    url_base="http://localhost:8069/webflow/IAC_DB/web.call.in.webflow.f06/call/call_in_func/admin"
    r = requests.post(url_base, params=payload)
    #print r.url
    print r.content


if __name__ == "__main__":
    test_call_method()
