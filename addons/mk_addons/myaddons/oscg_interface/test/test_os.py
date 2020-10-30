# -*- coding: utf-8 -*-
import threading
import datetime
import os
import psutil
from apscheduler.schedulers.background import BackgroundScheduler
import socket

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

if __name__ == "__main__":
    #os.system("calc.exe")
    ip_str=get_host_ip()
    print ip_str
    str_ip=get_host_ip()
    result="Exception raise at machine %s;"%(str_ip,)
    print result

    #//fileObject = open('	//odoo-files//webflow_error.txt', 'w')
    fileObject = open('d://lwt//webflow_error.txt', 'w')
    fileObject.write(result)
    fileObject.close()
    #a=psutil.Popen(["calc.exe"])
    #a=psutil.Popen(['/usr/bin/python','-c','print('hello')'],stdout=PIPE)
    #print a.name
    #print a.pid
    #a.wait()

