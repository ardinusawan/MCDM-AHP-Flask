import MySQLdb
import datetime
import sys

db = MySQLdb.connect("localhost","root","Asddsaa1","MCDM-AHP_dev" )

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
    # else:
        # print("Tabel containers sudah ada, skip..")

    cursor = db.cursor()
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
        timestamps DATETIME,
        FOREIGN KEY(container_id) REFERENCES containers(container_id) ON DELETE NO ACTION ON UPDATE NO ACTION)
    """
    status = cursor.execute("SHOW TABLES LIKE 'stats'")
    if status == 0:
        cursor.execute(stats)
    # else:
        # print("Tabel stats sudah ada, skip..")

def insert_containers(container_id, name, status):
    cursor = db.cursor()
    now = datetime.datetime.now()
    sql = "SELECT container_id FROM containers WHERE container_id = '%s'" % (container_id)
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


def insert_stats(container_id, container_name, cpu, memory, memory_percentage, last_time_access, last_time_access_percentage, ts):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO stats (container_id,container_name,cpu,memory, memory_percentage, last_time_access,last_time_access_percentage,timestamps) values ('%s','%s','%f','%f','%f','%s','%f','%s')" % \
            (container_id,container_name,cpu,memory, memory_percentage, last_time_access,last_time_access_percentage,ts))
        db.commit()
    except:
        db.rollback()
        print(sys.exc_info())
        return False
    finally:
        return True

