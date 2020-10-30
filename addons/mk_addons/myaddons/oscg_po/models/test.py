# -*- coding: utf-8 -*-
from rule_parser import RuleParser

def _taken_account_number_1(account_number):
    if account_number and len(account_number) >= 16:
        account_number1 = account_number[0:16]
    else:
        account_number1 = account_number
    print(account_number1)

def _taken_account_number_2(account_number):
    if account_number and len(account_number) >= 16:
        account_number2 = account_number[16:]
    else:
        account_number2 = ''
    print(account_number2)

if __name__=="__main__":
    print("main")
    test = 5
    if test == 1:
        line = '["and", [">", "{order_amount}", 1000], [">", {material_maxprice}, 20]]'
        regular = {
            'expression': line
        }
        print regular['expression']
        regular['expression'] = regular['expression'].replace('{order_amount}', '9999')
        regular['expression'] = regular['expression'].replace('{material_maxprice}', '10')
        regular['expression'] = regular['expression'].replace('{change_incoterm}', '')
        regular['expression'] = regular['expression'].replace('{change_paymentterm}', '')
        regular['expression'] = regular['expression'].replace('{price_factor}', '')
        regular['expression'] = regular['expression'].replace('{quantity_factor}', '')
        regular['expression'] = regular['expression'].replace('{change_delivery}', '')
        regular['expression'] = regular['expression'].replace('{item_factor}', '')
        print regular['expression']
        rule = RuleParser(regular['expression'])
        if rule.evaluate():
            print "yes"
        else:
            print "no"
    elif test == 2:
        line = '["and", [">", "{order_amount}", 1000], ["in", "{material_maxprice}", "10,20,30"]]'
        line = line.replace('{order_amount}', '9999')
        line = line.replace('{material_maxprice}', '10')
        print line
        rule = RuleParser(line)
        if rule.evaluate():
            print "yes"
        else:
            print "no"
    elif test == 3:
        line = '["in", "jb51.net", "(haotu.net,ijb51.net)"]'
        print line
        rule = RuleParser(line)
        if rule.evaluate():
            print "yes"
        else:
            print "no"
    elif test == 4:
        line = '["in", "{material_maxprice}", "jim,jack"]'
        line = line.replace('{order_amount}', '9999')
        line = line.replace('{material_maxprice}', 'jim')
        print line
        rule = RuleParser(line)
        if rule.evaluate():
            print "yes"
        else:
            print "no"
    elif test == 5:
        account_number = '123456789321456a9874569856'
        print account_number
        if account_number and len(account_number) >= 16:
            account_number1 = account_number[0:16]
        else:
            account_number1 = account_number

        print account_number1
        print '----------'

        if account_number and len(account_number) >= 16:
            account_number1 = account_number[16:]
        else:
            account_number1 = account_number

        print account_number1