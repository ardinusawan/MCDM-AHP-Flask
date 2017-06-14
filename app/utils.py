import docker
import logging

import psutil
import pytz
import datetime
from flask import Flask
import ahp as ahp
import db as database
import re

app = Flask(__name__)

delay = 60  # minute

local_tz = pytz.timezone('Asia/Jakarta')

client = docker.from_env()


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)  # .normalize might be unnecessary


# LTA: last time access
def get_LTA_Data(con):
    conName = con.name
    timepercentage = 0.0
    date_last_access = datetime.datetime.min

    # Check if the container is running
    if (con.status != 'running'):
        raise ValueError('"%s" container is not running' % conName)

    now = datetime.datetime.now()
    # date_crawler = now - datetime.timedelta(minutes=delay)
    # date_crawler = int(date_crawler.strftime('%s'))
    # con_log = con.logs(stream=False, timestamps=1, since=date_crawler)
    con_log_all = con.logs(stream=False, timestamps=1)
    if b'200' in con_log_all:
        last_hit_start = int(str(con_log_all).rfind('[')) + 1
        last_hit_end = int(str(con_log_all).rfind(']'))

        date_last_access = str(con_log_all)[last_hit_start:last_hit_end]
        date_last_access = datetime.datetime.strptime(date_last_access, '%d/%b/%Y:%H:%M:%S %z')
        date_last_access = utc_to_local(date_last_access)
        date_now = datetime.datetime.utcnow()
        date_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
        date_now = utc_to_local(date_now)
        difference_date = date_now - date_last_access
        difference_date = difference_date.total_seconds()
        day = 86400  # seconds

        timepercentage = difference_date / day * 100
    else:
        con_log = "No Data"

    if timepercentage is not 0:
        return timepercentage, date_last_access.replace(tzinfo=None)
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
    usage_mb = usage / (1024 * 1024)
    limit_mb = limit / (1024 * 1024)
    memorypercentage = usage_mb / limit_mb * 100
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

def get_server_data(now):
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    cpu = sum(cpu)/len(cpu)
    memory = psutil.virtual_memory().used / (1024^2) #MegaByte
    data = dict()
    data["params"] = "CPU, Memory, timestamps"
    data["value"] = "{CPU}, {Memory}, '{ts}'".format(CPU=cpu,Memory=memory,ts=now)
    database.insert("server_stats", **data)


def stats(**kwargs):

    if "stream" in kwargs.keys():
        stream = []
    elif not "stream" in kwargs.keys():
        database.create_table()

    now = datetime.datetime.now()
    get_server_data(now)

    list = client.containers.list()
    if not list:
        return "No container up"

    containers = 0

    for c in list:
        if "moodle" in c.name and c.status == 'running':
            containers += 1
            # print("Container Name:",c.name)
            con = client.containers.get(c.short_id)
            cpu_percentage = get_CPU_Percentage(con)
            memory_percentage, memory_mb = get_Memory_Data(con)
            LTA_percentage, LTA_datetime = get_LTA_Data(con)
            if "stream" in kwargs.keys():
                stream.append({"container_id":c.short_id,"container_name":c.name, "cpu":cpu_percentage,
                               "memory":memory_mb, "memory_percentage":memory_percentage,
                               "last_time_access":LTA_datetime,"last_time_access_percentage":LTA_percentage})
            else:
                if app.debug:
                    kwargs["mode"] = "REPLACE"
                kwargs["params"] = "container_id, name, status, timestamps"
                kwargs["value"] = "'{short_id}', '{name}', '{status}', '{timestamps}'".format(short_id=con.short_id, name=con.name,
                                                                                              status=con.status, timestamps=now)
                status = database.insert("containers",**kwargs)
                if status:
                    # kwargs.clear()
                    if app.debug:
                        kwargs["mode"] = "REPLACE"
                    id = con.short_id + now.strftime("%s")
                    kwargs[
                        "params"] = "id, container_id, container_name, cpu, memory, memory_percentage, last_time_access, last_time_access_percentage, timestamps"
                    kwargs[
                        "value"] = "'{id}', '{container_id}', '{container_name}', '{cpu}', '{memory}', '{memory_percentage}', '{last_time_access}', '{last_time_access_percentage}', '{timestamps}'".format(
                        id=id,container_id=con.short_id, container_name=con.name, cpu=cpu_percentage, memory=memory_mb,
                        memory_percentage=memory_percentage, last_time_access=LTA_datetime,
                        last_time_access_percentage=LTA_percentage, timestamps=now)
                    database.insert("stats",**kwargs)
    if "stream" in kwargs.keys():
        return stream

    # if containers == database.total_data("containers") and ahp.score()["status"] != "error":
    if ahp.score()["status"] != "error":
        kwargs.clear()
        kwargs["params"] = "container_id_hours, container_id_days, container_id_weeks, score_hours, score_days, score_weeks, hour_from, day_from, week_from, timestamps"
        hour = timedelta(now,"hour")
        day = timedelta(now,"day")
        week = timedelta(now,"week")
        score_hour = ahp.score(**hour)
        score_day = ahp.score(**day)
        score_week = ahp.score(**week)
        kwargs["value"] = "'{max_hour}', '{max_day}', '{max_week}', '{score_hour}', '{score_days}', '{score_weeks}', '{hour_from}', '{day_from}', '{week_from}', '{timestamps}'".format(max_hour=score_hour["max"],
                                                                                                                                                                                        max_day=score_day["max"], max_week=score_week["max"],
                                                                                                                                                                                        score_hour=score_hour["result"][score_hour["max"]], score_days=score_day["result"][score_day["max"]], score_weeks=score_week["result"][score_week["max"]],
                                                                                                                                                                                        hour_from=hour["hour_from"], day_from=day["day_from"], week_from=week["week_from"], timestamps=score_hour["ts"])

        if app.debug:
            kwargs["mode"] = "REPLACE"
        database.insert("result", **kwargs)
        print("Get result on " + now.strftime("%Y-%m-%d %H:%M"))
        c_stop_hour= client.containers.get(score_hour["max"])
        c_stop_day = client.containers.get(score_day["max"])
        c_stop_week = client.containers.get(score_week["max"])

        mysql_stop_hour = client.containers.get("mariadb" + c_stop_hour.name.strip()[-1])
        mysql_stop_day = client.containers.get("mariadb" + c_stop_day.name.strip()[-1])
        mysql_stop_week = client.containers.get("mariadb" + c_stop_week.name.strip()[-1])

        cpu = psutil.cpu_percent(interval=1, percpu=True)
        cpu = sum(cpu) / len(cpu)
        memory = psutil.virtual_memory().used / (1024 ^ 2)
        memory_total = psutil.virtual_memory().total / (1024 ^ 2)

        # limit = False
        # if((memory/memory_total)*100 > 60):
        #     limit = True
        limit = True

        temp = dict()
        temp["config"] = True
        todo = database.select("prefered", **temp)
        if limit:
            if todo["do"].lower() != "running":
                if todo["do"].lower() == "pause":
                    if todo["by"] == "hour":
                        c_stop_hour.pause()
                        mysql_stop_hour.pause()
                        score_hour["message"] = "container {name} has been paused".format(name=c_stop_hour.name)
                    elif todo["by"] == "day":
                        c_stop_day.pause()
                        mysql_stop_day.pause()
                        score_day["message"] = "container {name} has been paused".format(name=c_stop_day.name)
                    elif todo["by"] == "week":
                        c_stop_week.pause()
                        mysql_stop_week.pause()
                        score_week["message"] = "container {name} has been paused".format(name=c_stop_week.name)
                elif todo["do"].lower() == "stop":
                    if todo["by"] == "hour":
                        c_stop_hour.stop()
                        mysql_stop_hour.stop()
                        score_hour["message"] = "container {name} has been stoped".format(name=c_stop_hour.name)
                    elif todo["by"] == "day":
                        c_stop_day.stop()
                        mysql_stop_day.stop()
                        score_day["message"] = "container {name} has been stoped".format(name=c_stop_day.name)
                    elif todo["by"] == "week":
                        c_stop_week.stop()
                        mysql_stop_week.stop()
                        score_week["message"] = "container {name} has been stoped".format(name=c_stop_week.name)
            # database.close()
        return {"hour":score_hour, "day":score_day, "week":score_week}
    else:
        return {"status":"error","error":ahp.score()["message"]}


def ahp_score(**kwargs):
    data = database.select("result", **kwargs)
    # if data:
    #     database.close()
    return data

def timedelta(now,time):
    data = dict()
    temp = dict()
    temp["config"] = True
    td = database.select("timedelta", **temp)
    td = {k: int(v) for k, v in td.items()}
    if time == "hour":
        data["hour"] = True
        data["hour_from"] = now - datetime.timedelta(hours=td["hour"])
        data["hour_to"] = now
    elif time == "day":
        data["day"] = True
        data["day_from"] = now - datetime.timedelta(days=td["day"])
        data["day_to"] = now

    elif time == "week":
        data["week"] = True
        data["week_from"] = now - datetime.timedelta(weeks=td["week"])
        data["week_to"] = now

    return data


def log(table_name, limit=False, *args):
    data = dict()
    data["sort"] = "timestamps DESC"
    if limit:
        data["limit"] = args[0] + ", " + args[1]
        logs = database.select(table_name, **data)
    else:
        logs = database.select(table_name, **data)
    column = database.column(table_name)
    # print(column)
    # print(logs)
    res = list()
    for key,val in enumerate(logs):
        temp = dict(zip(column,logs[key]))
        res.append(temp)
    return res

def unpause_docker(id_or_name):
    con = client.containers.get(id_or_name)
    number = re.search(r'\d+', con.name).group()
    maridb = client.containers.get("mariadb" + number)
    if con.status == 'paused':
        con.unpause()
        maridb.unpause()
def start_docker(id_or_name):
    con = client.containers.get(id_or_name)
    number = re.search(r'\d+', con.name).group()
    maridb = client.containers.get("mariadb" + number)
    if con.status == 'exited':
        con.start()
        maridb.start()