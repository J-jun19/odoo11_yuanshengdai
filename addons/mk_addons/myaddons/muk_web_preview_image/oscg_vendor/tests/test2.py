# -*- coding: utf-8 -*-

import psycopg2
import os

"""
直接连接postgresql数据库
"""

if __name__=="__main__":
    test_flag = 2
    if test_flag == 1:
        conn = psycopg2.connect(host="localhost", port=65432, user="openerp", password="openerp",
                                database="iac_test_db")
        cur = conn.cursor()
        sql = "select part_id,part_no from goods_receipts where part_id is null limit 1000"
        cur.execute(sql)
        for gr in cur.fetchall():
            sql = "select part_no,id from material_master mm where part_no = %s", gr['part_no']
            cur.execute(sql)
            material = cur.fetchone()
            if material and material['id']:
                sql = "update goods_receipts set part_id = %s where part_no = %s", material['id'], gr['part_no']
        conn.commit()
        conn.close()
    elif test_flag == 2:
        for root, dirs, files in os.walk('d:/temp/3'):
            print(files)

