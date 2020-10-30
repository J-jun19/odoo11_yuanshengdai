# -*- coding: utf-8 -*-
# coding=utf-8
"""
Demonstrates how to use the background scheduler to schedule a job that executes on 3 second
intervals.
"""
import datetime
import time
import os
import threading
from apscheduler.schedulers.background import BackgroundScheduler


def odoo_env(func,**kwargs):
    def __decorator(self,**kwargs):    #add parameter receive the user information
        print 'odoo env before thread'
        func(self,**kwargs)
        print 'odoo env after thread'
    return __decorator


def tick_thread():
    print('This is Thread Tick! The time is: %s' % datetime.datetime.now())

def tick():
    print('Tick! The time is: %s' % datetime.now())

def tick_2(text_info):
    print('Tick! The time is: %s' % text_info)



class TimerJobGroup(object):
    @odoo_env
    def tick_thread(self,):
        print('This is self Thread Tick! The time is: %s' % datetime.datetime.now())


    def tick_3(self,text_info):

        mail_send_thread = threading.Thread(target=self.tick_thread, args=())
        mail_send_thread.start()
        mail_send_thread.join()
        print('Tick! The time is: %s' % text_info)


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    #scheduler.add_job(tick, 'interval', seconds=3)#间隔3秒钟执行一次

    job_args={
        'text_info':'lwt is a goodboy'
    }
    #scheduler.add_job(tick_2, 'interval', seconds=3,args=['lwt is a goodboy'])#间隔3秒钟执行一次
    #scheduler.add_job(func=tick_2, trigger='interval', seconds=3,kwargs=job_args)#间隔3秒钟执行一次
    #scheduler.start()    #这里的调度任务是独立的一个线程



    #测试调用对象的成员函数
    job_obj=TimerJobGroup()


    scheduler=BackgroundScheduler()
    run_date_time=datetime.datetime.now()+datetime.timedelta(seconds=5)
    job_para_map = {
        "replace_existing":True,
        "id":str(113)+'_run_once',
        "name":'TimerJobGroup_run_once',
        "func":getattr(job_obj, "tick_3"),
        "trigger":"date",
        "run_date":run_date_time,
        "kwargs":job_args,


        }

    scheduler.add_job(**job_para_map)
    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)    #其他任务是独立的线程执行
            print('sleep!')
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
        print('Exit The Job!')