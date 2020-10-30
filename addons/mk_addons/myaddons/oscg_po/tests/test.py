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
    test_list=[1,2,3,5]
    if 1 in test_list:
        print '1 in list'
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

{
    "Message": {
        "Status": "Y"
    },
    "Document": {
        "HEADER": [
            {
                "VMI_CODE": "B",
                "PLANT_ID": "CP21",
                "ITEM": [
                    {

                        {
                            "PO_ITEM": "00010",
                            "PS_ITEM": "1",
                            "PART_NO": "6035A0119301",
                            "VENDOR_ERP_ID": "0000381593",
                            "PO_NO": "4501154870",
                            "PULL_QTY": "20.0",
                            "MEINS": "EA"
                        },
                        {
                            "PO_ITEM": "00010",
                            "PS_ITEM": "2",
                            "PART_NO": "6012A0503701",
                            "VENDOR_ERP_ID": "0000381593",
                            "PO_NO": "4501154871",
                            "PULL_QTY": "20.0",
                            "MEINS": "EA"
                        }

                    }
                ],
                "PULL_SIGNAL_ID": "B38007717120601",
                "ITEM_COUNTS": "002",
                "OWNER": "IAC"
            }
        ]
    }
}

[
    {
        "VMI_CODE": "B",
        "PLANT_ID": "CP21",
        "ITEM": [
            {

                {
                    "PO_ITEM": "00010",
                    "PS_ITEM": "1",
                    "PART_NO": "6035A0119301",
                    "VENDOR_ERP_ID": "0000381593",
                    "PO_NO": "4501154870",
                    "PULL_QTY": "20.0",
                    "MEINS": "EA"
                },
                {
                    "PO_ITEM": "00010",
                    "PS_ITEM": "2",
                    "PART_NO": "6012A0503701",
                    "VENDOR_ERP_ID": "0000381593",
                    "PO_NO": "4501154871",
                    "PULL_QTY": "20.0",
                    "MEINS": "EA"
                }

            }
        ],
        "PULL_SIGNAL_ID": "B38007717120601",
        "ITEM_COUNTS": "002",
        "OWNER": "IAC"
    },
]