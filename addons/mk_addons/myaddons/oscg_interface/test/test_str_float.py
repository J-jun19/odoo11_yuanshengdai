# -*- coding: utf-8 -*-
import threading
import datetime
import math
import traceback

def is_float_valid(str_val):
    """
    返回2个值
    对出现科学计数法的字符串转换为标准字符串
    1   处理是否成功
    2   转换成的数值
    :param str_val:
    :return:
    """
    try:
        float_val=float(str_val)
        #获取允许范围之外的小数部分
        input_price=float_val

        #扩大10 的6次方倍
        try_price=input_price*math.pow(10,6)

        #减去整数部分获得小数部分
        digits_part=abs(round(try_price-round(try_price),2))
        price_unit=0
        #如果小数部分大于0.0001 那么表示超过6位，反之小于6位
        if (digits_part>0.0001):
            #1000的不满足,尝试10000
            return False,"%f"%(float_val,)
        else:
            return  True,"%f"%(float_val,)
    except:
        traceback.print_exc()
        pass
    return False,0

def calcu_po_price(vals):
    if "input_price" not in vals:
        return
    digits_count=vals.get("digits_count",0)


    #获取允许范围之外的小数部分
    input_price=vals["input_price"]
    return_vals={
        "input_price":input_price
    }
    rfq_po_test=input_price*math.pow(10,digits_count)

    #计算得到小数部分
    digits_part_test=float("%.1f"%(rfq_po_test))-int("%.1d"%(rfq_po_test))

    price_unit=0
    #浮点位数问题导致，做特殊处理,小数部分等于1,表明小数部分
    if  (digits_part_test==1.0):
        price_unit=1000
        return_vals["price_unit"]=price_unit
        return_vals["rfq_price"]=round(price_unit*input_price,digits_count)
        return return_vals


    if (digits_part_test>=0.01):
        #1000的不满足,尝试10000
        rfq_price_test=input_price*10000*math.pow(10,digits_count)
        full_price=float("%.2f"%(rfq_price_test))
        int_part_price=float("%.0d"%(rfq_price_test))
        digits_part=float("%.2f"%(rfq_price_test))-int("%.0d"%(rfq_price_test))

        price_unit=10000
        return_vals["price_unit"]=price_unit
        #存在小数的情况下,精度不允许的情况下进行截断处理
        if digits_part>=0.01 and digits_count==0:
            return_vals["rfq_price"]=int("%.0d"%(input_price*10000))
        else:
            return_vals["rfq_price"]=round(input_price*10000,digits_count)
    else:
        price_unit=1000
        return_vals["price_unit"]=price_unit
        return_vals["rfq_price"]=round(price_unit*input_price,digits_count)


    return return_vals

def calcu_rfq_price(vals):
    if "input_price" not in vals:
        return
    digits_count=vals.get("digits_count",0)


    #获取允许范围之外的小数部分
    input_price=vals["input_price"]
    return_vals={
        "input_price":input_price
    }
    rfq_price_test=input_price*1000*math.pow(10,digits_count)

    digits_part_test=float("%.2f"%(rfq_price_test))-int("%.0d"%(rfq_price_test))

    price_unit=0
    #浮点位数问题导致，做特殊处理,小数部分等于1,表明1000的price_unit够用
    if  (digits_part_test==1.0):
        price_unit=1000
        return_vals["price_unit"]=price_unit
        return_vals["rfq_price"]=round(price_unit*input_price,digits_count)
        return return_vals


    if (digits_part_test>=0.01):
        #1000的不满足,尝试10000
        rfq_price_test=input_price*10000*math.pow(10,digits_count)
        full_price=float("%.2f"%(rfq_price_test))
        int_part_price=float("%.0d"%(rfq_price_test))
        digits_part=float("%.2f"%(rfq_price_test))-int("%.0d"%(rfq_price_test))

        price_unit=10000
        return_vals["price_unit"]=price_unit
        #存在小数的情况下,精度不允许的情况下进行截断处理
        if digits_part>=0.01 and digits_count==0:
            return_vals["rfq_price"]=int("%.0d"%(input_price*10000))
        else:
            return_vals["rfq_price"]=round(input_price*10000,digits_count)
    else:
        price_unit=1000
        return_vals["price_unit"]=price_unit
        return_vals["rfq_price"]=round(price_unit*input_price,digits_count)


    return return_vals

def is_empty_str(str_txt):
    if (str_txt is None or str_txt is False or len(str_txt)==0 or len(str_txt.strip())==0):
        return True
    return False

if __name__ == "__main__":

    vals={
        "input_price":0.005258,
        "digits_count":2
    }
    return_vals=calcu_rfq_price(vals)
    print return_vals

    str1 =None
    str2 = False
    str3 = ''
    str4='  '
    str5=u''
    str6=u' '
    str7='111 '
    print is_empty_str(str1)
    print is_empty_str(str2)
    print is_empty_str(str3)
    print is_empty_str(str4)
    print is_empty_str(str5)
    print is_empty_str(str6)
    print is_empty_str(str7)

