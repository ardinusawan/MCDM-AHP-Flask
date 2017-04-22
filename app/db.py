import MySQLdb
import datetime
import sys

db = MySQLdb.connect("localhost", "root", "Asddsaa1", "MCDM-AHP_dev")


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
        cursor.execute("TRUNCATE TABLE containers")
        print("Tabel containers sudah ada, skip..")

    stats = """
    CREATE TABLE IF NOT EXISTS stats (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
    else:
        print("Tabel stats sudah ada, skip..")

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
    else:
        print("Tabel comparison_matrix sudah ada, skip..")

    parameter = """
        CREATE TABLE IF NOT EXISTS parameter (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            timestamps DATETIME)
        """
    status = cursor.execute("SHOW TABLES LIKE 'parameter'")
    if status == 0:
        cursor.execute(parameter)
    else:
        print("Tabel parameter sudah ada, skip..")


def insert_containers(container_id, name, status, now):
    cursor = db.cursor()
    sql = "SELECT container_id FROM containers WHERE container_id = '%s'" % container_id
    msg = cursor.execute(sql)
    if msg == 0:
        sql = "INSERT INTO containers (container_id, name, status, timestamps) VALUES ('%s','%s','%s','%s')" % \
              (container_id, name, status, now)
    elif msg == 1:
        sql = "UPDATE containers SET name='%s', status='%s', timestamps='%s' WHERE container_id = '%s'" % \
              (name, status, now, container_id)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print(sys.exc_info())
        return False
    finally:
        return True


def insert_stats(container_id, container_name, cpu, memory, memory_percentage, last_time_access,
                 last_time_access_percentage, ts):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO stats (container_id,container_name,cpu,memory, memory_percentage, last_time_access,"
            "last_time_access_percentage,timestamps) values ('%s','%s','%f','%f','%f','%s','%f','%s')" % \
            (
                container_id, container_name, cpu, memory, memory_percentage, last_time_access,
                last_time_access_percentage,
                ts))
        db.commit()
    except:
        db.rollback()
        print(sys.exc_info())
        return False
    finally:
        return True


def insert_comparison_matrix(parameter_data, **kwargs):
    ts = datetime.datetime.now()
    cursor = db.cursor()
    status = False
    create_table()

    cursor.execute("TRUNCATE TABLE parameter")
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

    cursor.execute("TRUNCATE TABLE comparison_matrix")
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


def get_last_data(tableName, **kwargs):
    cursor = db.cursor()
    sql = "SELECT * FROM %s WHERE %s = '%s' ORDER BY timestamps DESC LIMIT 1;" % \
          (tableName, kwargs["column"], kwargs["value"])
    cursor.execute(sql)
    msg = cursor.fetchone()
    if msg == 0:
        msg = False
    return msg


def total_data(table_name):
    cursor = db.cursor()
    sql = "SELECT COUNT(*) FROM %s ;" % \
          table_name
    cursor.execute(sql)
    msg = cursor.fetchone()
    msg = msg[0]
    return msg
