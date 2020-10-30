# -*- coding: utf-8 -*-
from decimal import Decimal
import math

from odoo.tools import float_utils

import xlrd


#读取xls文件输出 res.groups 的菜单配置D:\GOdoo10_IAC\myaddons\iac_security\security
if __name__ == "__main__":
    workbook = xlrd.open_workbook('E:\\tools\\Odoo\\GOdoo10_IAC\\myaddons\\iac_security\\doc\\res.groups_org.xls')
    sheet = workbook.sheet_by_name('res.groups_org')

    #获取有效的行数
    nrows = sheet.nrows
    group_name=''

    #遍历所有行
    i_row=1
    dict_group_menu={}
    while i_row<=nrows-1:
        new_group_name=sheet.cell_value(i_row,0)
        #删除空格和换行符
        new_group_name=new_group_name.strip()
        new_group_name=new_group_name.replace("\n", "")
        if new_group_name!=False and new_group_name!='' and len(new_group_name)!=0:
            group_name=new_group_name
        menu_name_list=[]
        if group_name in dict_group_menu:
            menu_name_list=dict_group_menu.get(group_name)
        menu_name=''
        menu_name=sheet.cell_value(i_row,1)
        menu_name=menu_name.strip()
        menu_name=menu_name.replace("\n", "")
        if len(menu_name)!=0:
            menu_name_list.append(menu_name)
        dict_group_menu[group_name]=menu_name_list
        i_row+=1

    fo = open("E:\\tools\\Odoo\\GOdoo10_IAC\\myaddons\\iac_security\\doc\\res.groups.csv", "wb")
    fo.write('\"id\",\"menu_access/id\"\n')
    for group_name in dict_group_menu:
        menu_name_list=[]
        menu_name_list_str=''
        menu_name_list=dict_group_menu.get(group_name)
        menu_name_list_str=",".join( menu_name_list)
        fo.write('\"'+group_name+'\",')
        fo.write('\"'+menu_name_list_str+'\"\n')
    fo.close()
    print 'success'