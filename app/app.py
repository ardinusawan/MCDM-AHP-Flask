from flask import Flask
import docker
from flask import jsonify
import logging
import datetime
import pytz
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import dbController as DB

delay = 60 #minute
get_stats = 10 # minutes

local_tz = pytz.timezone('Asia/Jakarta')

app = Flask(__name__)
client = docker.from_env()

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

#LTA: last time access
def get_LTA_Data(con):
    conName = con.name
    timepercentage = 0.0
    date_last_access = datetime.datetime.min

    # Check if the container is running
    if (con.status != 'running'):
        raise ValueError('"%s" container is not running' % conName)

    now = datetime.datetime.now()
    date_crawler = now - datetime.timedelta(minutes=delay)
    date_crawler = int(date_crawler.strftime('%s'))
    con_log = con.logs(stream=False, timestamps=1, since=date_crawler)
    # con_log_all = con.logs(stream=False, timestamps=1)
    if b'200' in con_log:
        last_hit_start = int(str(con_log).rfind('[')) + 1
        last_hit_end = int(str(con_log).rfind(']'))

        date_last_access = str(con_log)[last_hit_start:last_hit_end]
        date_last_access = datetime.datetime.strptime(date_last_access, '%d/%b/%Y:%H:%M:%S %z')
        date_last_access = utc_to_local(date_last_access)
        date_now = datetime.datetime.utcnow()
        date_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
        date_now = utc_to_local(date_now)
        difference_date = date_now - date_last_access
        difference_date = difference_date.total_seconds()
        day = 86400 # seconds

        timepercentage = difference_date/day * 100
    else:
        con_log = "No Data"

    if timepercentage is not 0:
        return timepercentage, date_last_access
    else:
        return con_log

def get_Memory_Data(con):
    conName = con.name
    memorypercentage = 0.0

    # Check if the container is running
    if (con.status != 'running'):
        raise ValueError('"%s" container is not running' % conName)

    # Get Memory Usage in percentage
    constat = con.stats(stream=False)
    usage = constat['memory_stats']['usage']
    limit = constat['memory_stats']['limit']
    usage_mb = usage/(1024*1024)
    limit_mb = limit/(1024*1024)
    memorypercentage = usage_mb/limit_mb * 100
    return memorypercentage, usage_mb

def get_CPU_Percentage(con):
    conName = con.name
    cpupercentage = 0.0

    # Check if the container is running
    if (con.status != 'running'):
        raise ValueError('"%s" container is not running' % conName)

    # Get CPU Usage in percentage
    constat = con.stats(stream=False)
    prestats = constat['precpu_stats']
    cpustats = constat['cpu_stats']

    # cpuDelta = res.cpu_stats.cpu_usage.total_usage -  res.precpu_stats.cpu_usage.total_usage;
    # systemDelta = res.cpu_stats.system_cpu_usage - res.precpu_stats.system_cpu_usage;
    # var RESULT_CPU_USAGE = cpuDelta / systemDelta * 100;
    # CPUStats.CPUUsage.PercpuUsage


    prestats_totalusage = prestats['cpu_usage']['total_usage']
    stats_totalusage = cpustats['cpu_usage']['total_usage']
    numOfCPUCore = len(cpustats['cpu_usage']['percpu_usage'])
    logging.debug('prestats_totalusage: %s, stats_totalusage: %s, NoOfCore: %s' % (
    prestats_totalusage, stats_totalusage, numOfCPUCore))

    prestats_syscpu = prestats['system_cpu_usage']
    stats_syscpu = cpustats['system_cpu_usage']
    logging.debug('prestats_syscpu: %s, stats_syscpu: %s' % (prestats_syscpu, stats_syscpu))

    cpuDelta = stats_totalusage - prestats_totalusage
    systemDelta = stats_syscpu - prestats_syscpu

    if cpuDelta > 0 and systemDelta > 0:
        cpupercentage = (cpuDelta / systemDelta) * numOfCPUCore

    formattedcpupert = '{:.1%}'.format(cpupercentage)
    logging.debug('cpuDelta: %s, systemDelta: %s, cpu: %s' % (cpuDelta, systemDelta, cpupercentage))

    logging.info('"%s" Container CPU: %s ' % (conName, formattedcpupert))

    return (cpupercentage * 100)



def stats():
    DB.create_table()
    list = client.containers.list()
    if not list:
        return False

    now = datetime.datetime.now()
    for c in list:
        if "moodle" in c.name:
            print("Container Name:",c.name)
            con = client.containers.get(c.short_id)
            cpu_percentage = get_CPU_Percentage(con)
            memory_percentage, memory_mb = get_Memory_Data(con)
            LTA_percentage, LTA_datetime = get_LTA_Data(con)
            # print(cpu_percentage)
            # print(memory_percentage, memory_mb)
            # print(LTA_percentage, LTA_datetime)

            data_container = {"container_id":con.short_id, "name":con.name, "status":con.status}
            data_stats = {"container_id":con.short_id, "cpu":cpu_percentage,"memory":memory_mb, "memory_percentage":memory_percentage, "last_time_access":LTA_datetime, "last_time_access_percentage":LTA_percentage, "ts":now}

            status = DB.insert_containers(**data_container)
            print(status)
            status1 = DB.insert_stats(**data_stats)
            print(status1)
            # print(data_container,data_stats)
    return True

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/container/list")
def container_list():
    stats()
    # print(dir(list[0]))
    con_log = ''


    return (con_log)


#schedule to write stats to DB
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=stats,
    trigger=IntervalTrigger(minutes=get_stats),#10 minute
    id='printing_job',
    name='Print date and time every five seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    # app.debug = True
    app.run()