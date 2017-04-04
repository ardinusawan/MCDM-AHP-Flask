from flask import Flask
import docker
from flask import jsonify
import logging
import datetime
import pytz

local_tz = pytz.timezone('Asia/Jakarta')

app = Flask(__name__)
client = docker.from_env()

delay =60 #minute

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

def get_Time_Percentage(con):
    conName = con.name
    timepercentage = 0.0

    # Check if the container is running
    if (con.status != 'running'):
        raise ValueError('"%s" container is not running' % conName)

    now = datetime.datetime.now()
    difference = now - datetime.timedelta(minutes=delay)
    difference = int(difference.strftime('%s'))
    con_log = con.logs(stream=False, timestamps=1, since=difference)
    if b'200' in con_log:
        last_hit_start = int(str(con_log).rfind('[')) + 1
        last_hit_end = int(str(con_log).rfind(']'))

        date_last_access = str(con_log)[last_hit_start:last_hit_end]
        date_last_access = datetime.datetime.strptime(date_last_access, '%d/%b/%Y:%H:%M:%S %z')
        date_last_access = utc_to_local(date_last_access)
        print(date_last_access)
    else:
        con_log = "No access data"
    return con_log
    # # Get Memory Usage in percentage
    # constat = con.stats(stream=False)
    # usage = constat['memory_stats']['usage']
    # limit = constat['memory_stats']['limit']
    # usage_mb = usage / (1024 * 1024)
    # limit_mb = limit / (1024 * 1024)
    # memorypercentage = usage_mb / limit_mb * 100
    # return memorypercentage

def get_Memory_Percentage(con):
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
    return memorypercentage

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
    # print(cpustats)

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

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/container/list")
def container_list():
    list = client.containers.list()
    # print(dir(list[0]))
    for c in list:
        if "moodle" in c.name:
            print("Container Name:",c.name)
            con = client.containers.get(c.short_id)

    con_perc = get_CPU_Percentage(con)
    mem_perc = get_Memory_Percentage(con)
    con_stats = con.stats(stream=False)
    con_log = get_Time_Percentage(con)


    return (con_log)

if __name__ == "__main__":
    # app.debug = True
    app.run()