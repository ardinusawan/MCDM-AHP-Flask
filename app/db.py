import MySQLdb
import datetime
import sys

db = MySQLdb.connect("localhost", "root", "Asddsaa1", "MCDM-AHP")

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
    # else:
        # print("Table stats is already, skip..")

    comparison_matrix = """
    CREATE TABLE IF NOT EXISTS comparison_matrix (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        comparison VARCHAR(255),
        value FLOAT,
        timestamps DATETIME)
    """
    status = cursor.execute("SHOW TABLES LIKE 'comparison_matrix'")
    if status == 0:
        cursor.execute(comparison_matrix)
    # else:
        # print("Table comparison_matrix is already, skip..")

    parameter = """
        CREATE TABLE IF NOT EXISTS parameter (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            timestamps DATETIME)
        """
    status = cursor.execute("SHOW TABLES LIKE 'parameter'")
    if status == 0:
        cursor.execute(parameter)
    # else:
    #     print("Table parameter is already, skip..")

    result = """
            CREATE TABLE IF NOT EXISTS result (
                container_id VARCHAR(255),
                score FLOAT,
                timestamps DATETIME PRIMARY KEY)
            """
    status = cursor.execute("SHOW TABLES LIKE 'result'")
    if status == 0:
        cursor.execute(result)
    # else:
    #     print("Table result is already, skip..")


# def insert_containers(container_id, name, status, now):
#     cursor = db.cursor()
#     sql = "SELECT container_id FROM containers WHERE container_id = '%s'" % container_id
#     msg = cursor.execute(sql)
#     if msg == 0:
#         sql = "INSERT INTO containers (container_id, name, status, timestamps) VALUES ('%s','%s','%s','%s')" % \
#               (container_id, name, status, now)
#     elif msg == 1:
#         sql = "UPDATE containers SET name='%s', status='%s', timestamps='%s' WHERE container_id = '%s'" % \
#               (name, status, now, container_id)
#     try:
#         cursor.execute(sql)
#         db.commit()
#     except:
#         db.rollback()
#         print(sys.exc_info())
#         return False
#     finally:
#         return True


# def insert_stats(container_id, container_name, cpu, memory, memory_percentage, last_time_access,
#                  last_time_access_percentage, ts):
#     cursor = db.cursor()
#     try:
#         cursor.execute(
#             "INSERT INTO stats (container_id,container_name,cpu,memory, memory_percentage, last_time_access,"
#             "last_time_access_percentage,timestamps) values ('%s','%s','%f','%f','%f','%s','%f','%s')" % \
#             (
#                 container_id, container_name, cpu, memory, memory_percentage, last_time_access,
#                 last_time_access_percentage,
#                 ts))
#         db.commit()
#     except:
#         db.rollback()
#         print(sys.exc_info())
#         return False
#     finally:
#         return True


def insert_comparison_matrix(parameter_data, **kwargs):
    ts = datetime.datetime.now()
    cursor = db.cursor()
    status = False
    create_table()

    truncate("parameter")
    for i in range(len(parameter_data)):
        try:
            cursor.execute(
                "INSERT INTO parameter (name ,timestamps) values ('%s','%s')" % \
                (parameter_data[i], ts))
            db.commit()
        except:
            db.rollback()
            print(sys.exc_info())
            status = False
            break
        finally:
            status = True

    truncate("comparison_matrix")
    for key, value in kwargs.items():
        print(key, value)
        try:
            cursor.execute(
                "INSERT INTO comparison_matrix (comparison, value ,timestamps) values ('%s','%f','%s')" % \
                (key, value, ts))
            db.commit()
        except:
            db.rollback()
            print(sys.exc_info())
            status = False
            break
        finally:
            status = True
    return status


def last_data(tableName, **kwargs):
    cursor = db.cursor()
    sql = "SELECT * FROM %s WHERE %s = '%s' ORDER BY timestamps DESC LIMIT 1;" % \
          (tableName, kwargs["column"], kwargs["value"])
    cursor.execute(sql)
    msg = cursor.fetchone()
    if msg == 0:
        msg = False
    return msg


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

# def all_data(table_name,**kwargs):
#     cursor = db.cursor()
#     sql = "SELECT * FROM {table_name}" .format(table_name=table_name)
#     if "select" in kwargs:
#         sql = "SELECT {column} FROM {table}".format(column=kwargs["select"]["data"],table=table_name)
#     if "sort" in kwargs:
#         temp = " ORDER BY {}" .format(kwargs["sort"]['column'],kwargs["sort"]['order'])
#         sql = sql + temp
#
#     cursor.execute(sql)
#     msg = cursor.fetchall()
#     return msg

# def find_data(table_name, *args, **kwargs):
#     cursor = db.cursor()
#     args = ','.join(map(str, list(args)))
#     where = ""
#     msg = ""
#     i = 0
#     for key,value in kwargs.items():
#         where += key + " = " + str(value)
#         if i < len(kwargs.keys()) - 1:
#             where += " AND "
#         i += 1
#     sql = "SELECT * FROM {table_name} WHERE {where}".format(table_name=table_name, where=where)
#     if args:
#         sql = "SELECT {select} FROM {table_name} WHERE {where}".format(select=args,table_name=table_name, where=where)
#     try:
#         cursor.execute(sql)
#         msg = cursor.fetchall()
#     except:
#         db.rollback()
#         print(table_name, sys.exc_info())
#     return msg

def select(table_name,*args,**kwargs):
    cursor = db.cursor()
    msg = None
    where_text = "WHERE"
    between = ""
    if "between" not in kwargs:
        between_text = ""
        kwargs["between"] = ""
    elif "between" in kwargs:
        between = "AND {between} BETWEEN {from_date} AND {to_date}".format(between=kwargs["between"],
                                                                                from_date=args[0],
                                                                                to_date=args[1])
    if "column" not in kwargs:
        kwargs["column"] = "*"
    if "where" not in kwargs:
        where_text = ""
        kwargs["where"] = ""
    sql = "SELECT {column} FROM {table_name} {where_text} {where} {between}".format(column=kwargs["column"],
                                                                                    table_name=table_name,
                                                                                    where_text=where_text,
                                                                                    where=kwargs["where"],
                                                                                    between=between)
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
