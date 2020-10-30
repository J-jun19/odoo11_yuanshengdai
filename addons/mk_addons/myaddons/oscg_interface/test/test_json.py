# -*- coding: utf-8 -*-
from odoo import models, fields, api
import urllib2
import json
import  requests
import xmlrpclib
from datetime import datetime,timedelta
from odoo.tools.safe_eval import safe_eval as eval
import time
def test_request():

    data = {
        'a': 123,
        'b': 456,
        'name':'lwt'
    }
    headers = {'Content-Type': 'application/json'}
    request = urllib2.Request(url='http://localhost:9000/report_viewer/say_hello', headers=headers, data=json.dumps(data))
    response = urllib2.urlopen(request)
    html=response.read()
    print '111'

def test_xml_prc():
    sock_common = xmlrpclib.ServerProxy ("http://localhost:9000/report_viewer/say_hello")
    report_paras={"filexml":"lwt"}

def test_encode_base64():
    json_str="""
    {"status": "true", "FormStatus": "C", "jsonrpc": "2.0", "method": "call", "tokens": ["aHR0cDovL3d3dy5vc2NnLmNuLCBJQUNfREIsIGFkbWluLCAxLCAxNTc5NDk0Njk0"], "params": {"FlowList": [{"Timestamp": "2020/02/03 08:11:17", "Approver": "\u5433\u9ad8\u8ce2", "Comments": "Approve.", "Stage": "BG_Leader"}, {"Timestamp": "2020/02/03 08:11:17", "Approver": "", "Comments": "", "Stage": "\u7d50\u675f"}]}, "EFormNO": "NVR202001310010", "message": "", "inf_call_id": "7098416", "id": "792", "stage": "F03_E"}
    """
    json_obj=json.loads(json_str)
if __name__ == "__main__":
    json_str='{"Approver":"莊世嘉","Comments":"退件.wedfwefwef!@#$%^&amp;*z(~+"}'
    obj_json=json.loads(json_str)
    print 123

    script_env={
        "sap_log_id":'11122233'
    }
    script_text="\"sap_log_id='%s'\"%(sap_log_id,)"
    print script_text
    eval_reulst=eval(script_text,script_env)
    print eval_reulst
    print script_text

    dt = datetime.now()
    dt.strftime('%Y-%m-%d %H:%M:%S %f')
    print dt.strftime('%Y-%m-%d')


    last_date=datetime.now()+timedelta(days=-31)
    print last_date.strftime("%Y-%m-%d %H:%M:%S")

    str_test=u'我是新疆人'
    print str_test.decode('utf-8')
    print str_test.encode('utf-8')
    #test_request()
    str_test="2018/08/22"
    str_test2=""
    expiration_date=time.strftime('%Y-%m-%d',time.strptime(str_test,'%Y/%m/%d'))
    print len(str_test2)
    if len(str_test2)>0:
        expiration_date=time.strftime('%Y-%m-%d',time.strptime(str_test2,'%Y/%m/%d'))
    print expiration_date