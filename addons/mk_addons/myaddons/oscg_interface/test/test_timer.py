# -*- coding: utf-8 -*-
import threading
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
def hello(name,call_back_func):

    #获取utc格式的当期时间
    cur_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "hello %s and time is %s \n" % (name,cur_time)
    my_callback()
    #global timer
    #timer = threading.Timer(2.0, hello, ["Hawk"])
    #timer.start()

def my_callback():
    global timer
    #timer.join()
    timer = threading.Timer(2.0, hello, ["Hawk",my_callback])
    timer.start()
    #print "function my_callback was called with  input"

if __name__ == "__main__":
    global timer
    timer = threading.Timer(2.0, hello, ["Hawk",my_callback])
    timer.start()
    #timer.join()