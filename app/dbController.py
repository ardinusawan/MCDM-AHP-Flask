import sqlite3
import datetime
from flask import g
import sys
from flask import Flask


DATABASE = './database.db'

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# create table if not exist
def create_table():
    cur = get_db().cursor()
    containers = """
    CREATE TABLE IF NOT EXISTS containers (
        container_id TEXT PRIMARY KEY, 
        name TEXT,
        status TEXT,
        timestamps DATETIME)
    """
    cur.execute(containers)
    print("Table %s is exist / created successfully" % "containers")

    stats = """
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        container_id TEXT,
        cpu REAL,
        memory REAL,
        memory_percentage REAL,
        last_time_access DATETIME,
        last_time_access_percentage REAL,
        timestamps  DATETIME,
        FOREIGN KEY(container_id) REFERENCES containers(container_id))
    """
    cur.execute(stats)
    print("Table %s is exist / created successfully" % "stats")

    cur.close()


def query_db(query, args=(), one=False):
    # with app.app_context():
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_containers(container_id, name, status):
    # with app.app_context():
    cur = get_db().cursor()
    con = get_db()
    now = datetime.datetime.now()
    # now = utc_to_local(now)
    try:
        status = cur.execute("REPLACE INTO containers (container_id, name, status, timestamps) values (?,?,?,?)",
                             (container_id, name, status, now))
        con.commit()
        cur.close()
    except:
        con.rollback()
        status = sys.exc_info()
    finally:
        return status


def insert_stats(container_id, cpu, memory, memory_percentage, last_time_access, last_time_access_percentage, ts):
    # with app.app_context():
    cur = get_db().cursor()
    con = get_db()
    try:
        status = cur.execute(
            "INSERT INTO stats (container_id, cpu, memory, memory_percentage, last_time_access, last_time_access_percentage, timestamps) values (?,?,?,?,?,?,?)",
            (container_id, cpu, memory, memory_percentage, last_time_access, last_time_access_percentage, ts))
        con.commit()
        cur.close()
    except:
        con.rollback()
        status = sys.exc_info()
    finally:
        return status

