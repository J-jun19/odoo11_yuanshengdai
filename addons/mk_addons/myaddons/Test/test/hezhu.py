# -*- coding: utf-8 -*-
from decimal import Decimal
import math
# import erppeek
import psycopg2
from odoo.tools import float_utils
import os,shutil
import xlrd
from xml.dom.minidom import Document

import xml.etree.ElementTree as ET
import re



# 将excel的资料存到数据库中
def save_to_database(excel_name):
    conn = psycopg2.connect(database="IAC_DB", user="odooiac", password="erp**123", host="127.0.0.1", port="5432")
    # print "Opened database successfully"
    cur = conn.cursor()

    workbook = xlrd.open_workbook('C:\\hezhu\\upload\\'+excel_name)
    sheet = workbook.sheet_by_name('Sheet1')

    rows_five = sheet.row_values(4)  # 第五行内容
    list_five = []
    for item in range(sheet.ncols):
        if sheet.row_values(4)[item]:
            list_five.append(rows_five[item])

    rows_ten = sheet.row_values(9)  # 第十行内容
    list_ten = []
    for item in range(sheet.ncols):
        list_ten.append(rows_ten[item])

    rows_eleven = sheet.row_values(10)  # 第十一行内容
    list_eleven = []
    for item in range(sheet.ncols):
        if sheet.row_values(10)[item]:
            list_eleven.append(rows_eleven[item])
    # 清单编号
    list_number = list_five[3].encode('utf-8')
    # 进出口标记
    ieflag = list_number[8:9]
    # 预录入统一编号
    seqno1 = list_five[1].encode('utf-8')
    # 料件、成品标志
    if list_eleven[1].encode('utf-8') == '料件':
        mtpckEndprdMarkcd = 'I'
    elif list_eleven[1].encode('utf-8') == '成品':
        mtpckEndprdMarkcd = 'E'

    # 录入日期
    PDate = list_ten[31]
    for item in range(len(sheet.col_values(1))):
        if sheet.col_values(1)[item].encode('utf-8') == '表体':
            begin = item + 2
            continue
        if sheet.col_values(1)[item].encode('utf-8') == '报关单草稿':
            end = item - 1
            break
    # print sheet.col_values(1)[begin],sheet.col_values(1)[end]
    cur.execute("INSERT INTO INV_HEAD (bondinvtno,tradeco,tradename,dcrtimes,trademode,seqno1,invttype,"
                "ieflag,putrecno,applycompanycode,applycompanyname,dclEtpsSccd,tradeCountry,copCode,copName,"
                "inputCreditCode,mtpckEndprdMarkcd,trafMode,invtIochkptStucd,listType,dclcusFlag,dclcusTypecd,"
                "entryType,PDate,export_flag) \
              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (list_number, '3601660018', '南昌英华达智能制造有限公司','1','5015', seqno1, '0', ieflag, 'H401918A0009',
                 '3601660018', '南昌英华达智能制造有限公司', '91360106MA38027Q2U', '142', '3601660018', '南昌英华达智能制造有限公司',
                 '91360106MA38027Q2U', mtpckEndprdMarkcd, '9', '0', 'A', '1', '1', '1', PDate,'F'));
    for item in range(begin, end + 1):
        # print item
        list_auto = []
        for j in range(sheet.ncols):
            list_auto.append(sheet.row_values(item)[j])
        # print list_auto
        # 商品编码
        codeTs = list_auto[10]
        # 商品名称
        gName = list_auto[13].encode('utf-8')
        # 规格型号
        gModel = list_auto[16].encode('utf-8')
        # 申报数量
        gQty = list_auto[51]
        # 申报计量单位
        gUnit_dic = {'台': '001', '个': '007', '卷': '018', '片': '020', '米': '030', '千克': '035', '克': '036'}
        # print list_auto[19].encode('utf-8')
        if list_auto[19].encode('utf-8') != '':
            if gUnit_dic[list_auto[19].encode('utf-8')]:
                gUnit = gUnit_dic[list_auto[19].encode('utf-8')]
            else:
                gUnit = ''
        else:
            gUnit = ''
        # 法定数量
        qty1 = list_auto[44]
        # 法定计量单位
        if list_auto[23].encode('utf-8') != '':
            if gUnit_dic[list_auto[23].encode('utf-8')]:
                unit1 = gUnit_dic[list_auto[23].encode('utf-8')]
            else:
                unit1 = ''
        else:
            unit1 = ''
        # 第二法定数量
        if list_auto[47] == '':
            qty2 = 0
        else:
            qty2 = list_auto[47]
        # 法定第二计量单位
        # print list_auto[27]
        if list_auto[27].encode('utf-8') != '':
            if gUnit_dic[list_auto[27].encode('utf-8')]:
                unit2 = gUnit_dic[list_auto[27].encode('utf-8')]
            else:
                unit2 = ''
        else:
            unit2 = ''
        # 申报单价
        declPrice = list_auto[35]
        # 申报总价
        declTotal = list_auto[38]
        # 币制
        if list_auto[41].encode('utf-8') == '美元':
            tradeCurr = '502'
        # 商品料号
        copGNo = list_auto[7].encode('utf-8')
        cur.execute("insert into inv_list(codeTs,gName,gModel,gQty,gUnit,qty1,unit1,qty2,unit2,declPrice,declTotal,"
                    "tradeCurr,useTo,originCountry,dutyMode,copGNo,bondInvtNo) "
                    "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (codeTs, gName, gModel, gQty, gUnit, qty1, unit1, qty2, unit2, declPrice, declTotal, tradeCurr,
                     '05', '142', '3', copGNo, list_number));
    conn.commit()
    conn.close()

# 获取head表的资料
def get_head_data():
    conn = psycopg2.connect(database="IAC_DB", user="odooiac", password="erp**123", host="127.0.0.1", port="5432")
    # print "Opened database successfully"
    cur = conn.cursor()
    cur.execute("select * from inv_head where export_flag ='F' ");
    head_data = cur.fetchall()
    return head_data

#获取head对应的list表的资料
def get_list_by_head(data):
    conn = psycopg2.connect(database="IAC_DB", user="odooiac", password="erp**123", host="127.0.0.1", port="5432")
    # print "Opened database successfully"
    cur = conn.cursor()
    cur.execute("select * from inv_list where bondinvtno =%s ",(data,));
    list_data = cur.fetchall()
    return list_data


# 生成XML文件
def buildNewsXmlFile(data):
    # 创建dom文档
    doc = Document()
    # 创建根节点
    inv101 = doc.createElement("INV101")
    # 根节点插入dom树
    doc.appendChild(inv101)

    for i in range(len(data)):
        # print data
        inv_header = doc.createElement("INV_HEAD")
        # 插入父节点
        inv101.appendChild(inv_header)
        head_list = ['bondInvtNo','iEPort','tradeCo','tradeName','dcrTimes','tradeMode','seqNo1','listStat','cafNo','invtType','IEFlag',
                     'putrecNo','prjNo','vrfdedMarkcd','bizopEtpsSccd','shippingUnitcompCode','shippingUnitcompName',
                     'rvsngdEtpsSccd','applycompanycode','applycompanyname','dclEtpsSccd','tradeCountry','copCode',
                     'copName','inputCreditCode','mtpckEndprdMarkcd','trafMode','invtIochkptStucd','listType','dclcusFlag',
                     'dclcusTypecd','entryType','entryNo','corrEntryDclEtpsno','corrEntryDclEtpsNm','corrEntryDclEtpsSccd',
                     'rltEntryNo','rltEntryDclEtpsno','rltEntryDclEtpsNm','rltEntryDclEtpsSccd','rltInvtNo','rltEntryRcvgdEtpsno',
                     'rltEntryRcvgdEtpsNm','rltEntryRvsngdEtpsSccd','rltPutrecNo','rltEntryBizopEtpsno','rltEntryBizopEtpsNm',
                     'rltEntryBizopEtpsSccd','noteS','pDate','dDate']
        for item in range(len(head_list)):
            Element = doc.createElement(head_list[item])
            inv_header.appendChild(Element)
            if data[i][item+1]:
                # 创建文本节点
                Element_value = doc.createTextNode(str(data[i][item+1]))
            else:
                Element_value = doc.createTextNode('')
            # 将文本节点插入Element节点下
            Element.appendChild(Element_value)
        # 根据清单编号获取list中的资料
        list_data = get_list_by_head(data[i][1])
        for j in range(len(list_data)):
            inv_list = doc.createElement("INV_LIST")
            inv101.appendChild(inv_list)
            list_list = ['bondInvtNo','codeTs','gName','gModel','gQty','gUnit','qty1','unit1','qty2','unit2','declPrice',
                         'declTotal','tradeCurr','exgVersion','useTo','originCountry','dutyMode','copGNo']
            for item in range(len(list_list)):
                Element = doc.createElement(list_list[item])
                inv_list.appendChild(Element)
                # print list_data[j][item+1]
                if list_data[j][item + 1]:
                    Element_value = doc.createTextNode(str(list_data[j][item + 1]))
                    # print Element_value
                else:
                    Element_value = doc.createTextNode('')
                Element.appendChild(Element_value)

    filename = "C:\\hezhu\\xml\\INV101.xml"
    f = open(filename, "w")
    doc.writexml(f,encoding='utf-8')

    # f.write(doc.toprettyxml(encoding = 'UTF-8',indent='\t',newl = '\n', addindent = '\t'))
    f.close()


#读取xls文件输出 res.groups 的菜单配置
if __name__ == "__main__":
    rootdir = 'C:\\hezhu\\upload'
    list = os.listdir(rootdir)
    for i in range(len(list)):
        save_to_database(list[i])
        shutil.move("C:\\hezhu\\upload\\"+list[i], "c:\\hezhu\\backup")
    data = get_head_data()
    buildNewsXmlFile(data)
    conn = psycopg2.connect(database="IAC_DB", user="odooiac", password="erp**123", host="127.0.0.1", port="5432")
    # print "Opened database successfully"
    cur = conn.cursor()
    cur.execute("update inv_head set export_flag = 'T' where export_flag ='F' ");
    conn.commit()
    conn.close()
    print 'success'