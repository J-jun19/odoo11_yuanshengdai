# -*- coding: utf-8 -*-
import threading
import datetime
import types
from odoo.tools.safe_eval import safe_eval as eval
def fun_test1(name,sex,age):
    print name
    print sex
    print age

def test_args(first, second, third, fourth, fifth):
    print 'First argument: ', first
    print 'Second argument: ', second
    print 'Third argument: ', third
    print 'Fourth argument: ', fourth
    print 'Fifth argument: ', fifth

# Use *args
args = [1, 2, 3, 4, 5]
test_args(*args)
# results:
# First argument:  1
# Second argument:  2
# Third argument:  3
# Fourth argument:  4
# Fifth argument:  5

# Use **kwargs
kwargs = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'fifth': 51
}

if __name__ == "__main__":
    cur_date_time= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_date_time=(datetime.datetime.now()+datetime.timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
    print cur_date_time
    print new_date_time
    test_args(**kwargs)

    exe_code='cust={' \
             '\'name\':\'lwt\'}'
    eval_context={}
    eval(exe_code, eval_context, mode="exec", nocopy=True)
    b=eval(u'3e-05')
    test_str=u'3e-05'
    if test_str.index('e')>0:
        c=eval(test_str)
        s_c="%f"%(c,)
        print s_c

    if 'cust' in eval_context:
        print 'success'

    tables= ['"iac_asn"']
    where_clause= ['("iac_asn"."plant_id" in (%s))']
    where_params=['\'27\'']
    print tuple(where_params)
    sql_params=tuple(where_params)
    where_str=where_clause[0]%sql_params
    print where_str
    print sql_params

    where_params=['27']
    for param_vals in where_params:
        if (type(param_vals) is types.StringType ):
            param_vals='\''+param_vals+'\''
            print param_vals

    for param_vals in where_params:
        print param_vals