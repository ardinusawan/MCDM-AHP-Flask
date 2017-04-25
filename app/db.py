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
    sql = "SELECT {column} FROM {table_name} {where_text} {where} {between} {sort}".format(column=kwargs["column"],
                                                                                    table_name=table_name,
                                                                                    where_text=where_text,
                                                                                    where=kwargs["where"],
                                                                                    between=between,
                                                                                    sort=sort)
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
