# -*- coding: utf-8 -*-
from decimal import Decimal
import math

from odoo.tools import float_utils

def trans_float_to_currency(float_val=0,float_digit=2):
    """
    1.123456 转换后变成 11234.56
    :param float_val:传入一个浮点数
    :param float_digit: 需要转换的目标浮点位数
    :return: 转换后的浮点数,与转换前的相比10的倍数
    """
    float_trans=float_val
    float_count=0
    while (True):
        float_trans=float_trans*10
        float_count=float_count+1
        float_digets=float_trans-float_trans
        if (round(float_digets,8)>=0.00000001):
            continue
        else:
            break

    #当一个数的整数部分等于这个数的时候，转换完成得到一个整数
    float_trans=math.pow(10,float_count-2)*float_val
    return float_trans,float_count-2

if __name__ == "__main__":
    a = Decimal('1.0231212121')
    round_a = round(a,3) # Decimal('1.023')

    result,float_digit=trans_float_to_currency(0.123456,2)
    print result
    print float_digit



    float_test=35.001
    float_digets=float_test-math.trunc(float_test)
    if (round(float_digets,8)>=0.00000001):
        print '有小数'
    else:
        print '没有小数'


    #获取当前货币的小数位
    digits_count=0

    input_price=2.1
    price_unit=0
    #获取允许范围之外的小数部分
    digits_part=input_price*1000*math.pow(10,digits_count)-math.trunc(input_price*1000*math.pow(10,digits_count))
    if (digits_part>0):
        #1000的不满足,尝试10000
        digits_part=input_price*10000*math.pow(10,digits_count)-math.trunc(input_price*10000*math.pow(10,digits_count))
        if digits_part>0:
            #抛出异常,小数位太多
            print '发生异常,小数位太多'
            pass
        else:
            price_unit=10000
    else:
        price_unit=1000
        #根据price_unit 进行价格转换
    rfq_price=input_price*price_unit
    print rfq_price
    print price_unit

    finish_rate=0.0
    finish_count=1000
    record_count=25651
    finish_rate=9000/25651
    print format(float(finish_count)/float(record_count),'.0%')
    part_lst=[' 1000 ','2000 ',' 3000']
    new_list=[]
    a=""
    a.strip()
    for item in part_lst:
        new_list.append(item.strip())
    print new_list
    test_id_list=[1,3,4,5]
    test_id_list_str=[str(x) for x in test_id_list]
    print ([str(x) for x in test_id_list])

    str_tuple='('+  ','.join(test_id_list_str) + ')'

    print str_tuple

