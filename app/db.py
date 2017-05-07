import MySQLdb
import datetime
import sys
import os

import configparser

def config(section):
    full_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(full_path)
    dir_path = dir_path + '/'

    settings = configparser.ConfigParser(allow_no_value=True)
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(dir_path + 'config.ini')

    data = dict()
    options = settings.options(section)
    for option in options:
        try:
            data[option] = settings.get(section, option)
            if data[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            data[option] = None
    return data


db = MySQLdb.connect(config("mysql")["host"],
                     config("mysql")["username"],
                     config("mysql")["password"],
                     config("mysql")["database"])

def close():
    db.close()

def column(table_name):
    cursor = db.cursor()
    cursor.execute("SHOW columns FROM {table_name}".format(table_name=table_name))
    field_names = [columns[0] for columns in cursor.fetchall()]
    return field_names

def truncate(table_name):
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE {}".format(table_name))

# create table if not exist
def create_table():
    cursor = db.cursor()

    containers = """
    CREATE TABLE IF NOT EXISTS containers (
        container_id VARCHAR(255) PRIMARY KEY, 
        name VARCHAR(255),
        status VARCHAR(255),
        timestamps DATETIME)
    """
    status = cursor.execute("SHOW TABLES LIKE 'containers'")
    if status == 0:
        cursor.execute(containers)
    else:
        truncate("containers")
        # print("Table containers is already, skip..")

    stats = """
    CREATE TABLE IF NOT EXISTS stats (
        id VARCHAR(255) NOT NULL PRIMARY KEY,
        container_id VARCHAR(255),
        container_name VARCHAR(255),
        cpu INT,
        memory FLOAT,
        memory_percentage FLOAT,
        last_time_access DATETIME,
        last_time_access_percentage FLOAT,
        timestamps DATETIME)
    """
    status = cursor.execute("SHOW TABLES LIKE 'stats'")
    if status == 0:
        cursor.execute(stats)

    result = """
            CREATE TABLE IF NOT EXISTS result (
                container_id_hours VARCHAR(255),
                container_id_days VARCHAR(255),
                container_id_weeks VARCHAR(255),
                score_hours FLOAT,
                score_days FLOAT,
                score_weeks FLOAT,
                hour_from DATETIME,
                day_from DATETIME,
                week_from DATETIME,
                timestamps DATETIME PRIMARY KEY)
            """
    status = cursor.execute("SHOW TABLES LIKE 'result'")
    if status == 0:
        cursor.execute(result)
    # else:
    #     print("Table result is already, skip..")


def total_data(table_name,**kwargs):
    cursor = db.cursor()
    where_text = "WHERE"
    if "where" not in kwargs:
        where_text = ""
        kwargs["where"] = ""
    sql = "SELECT COUNT(*) FROM {table_name} {where_text} {where} ;".format(table_name=table_name,
                                                                            where_text=where_text,
                                                                            where=kwargs["where"])
    cursor.execute(sql)
    msg = cursor.fetchone()
    msg = msg[0]
    return msg


def select(table_name,*args,**kwargs):
    cursor = db.cursor()
    msg = None
    where_text = "WHERE"
    between = ""
    sort = ""
    limit = "LIMIT 0, 18446744073709551615"
    if "config" in kwargs:
        return config(table_name)
    if "between" in kwargs:
        between = "AND {between} BETWEEN {from_date} AND {to_date}".format(between=kwargs["between"],
                                                                                from_date=args[0],
                                                                                to_date=args[1])
    if "column" not in kwargs:
        kwargs["column"] = "*"
    if "where" not in kwargs:
        where_text = ""
        kwargs["where"] = ""
    if "sort" in kwargs:
        sort = "ORDER BY {}" .format(kwargs["sort"])
    if "limit" in kwargs:
        limit = "LIMIT {limit}".format(limit=kwargs["limit"])
    sql = "SELECT {column} FROM {table_name} {where_text} {where} {between} {sort} {limit}".format(column=kwargs["column"],
                                                                                    table_name=table_name,
                                                                                    where_text=where_text,
                                                                                    where=kwargs["where"],
                                                                                    between=between,
                                                                                    sort=sort, limit=limit)
    try:
        cursor.execute(sql)
        msg = cursor.fetchall()
    except:
        db.rollback()
        print(table_name, sys.exc_info())
    return msg

def insert(table_name,**kwargs):
    cursor = db.cursor()
    status = False
    if "truncate" in kwargs:
        truncate(table_name)
    if "mode" not in kwargs:
        kwargs["mode"] = "INSERT"
    sql = "{mode} INTO {table_name} ({params}) VALUES ({values})".format(mode=kwargs["mode"],
                                                                         table_name=table_name,
                                                                         params=kwargs["params"],
                                                                         values=kwargs["value"])
    try:
        status = cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print(table_name,sys.exc_info())
        return status
    finally:
        return status