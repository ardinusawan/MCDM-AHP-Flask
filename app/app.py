from flask import Flask
from flask import jsonify
import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import utils as UTILS

app = Flask(__name__)

get_stats = 10 # minutes

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/container/list")
def container_list():
    UTILS.stats()
    # print(dir(list[0]))
    con_log = ''


    return (con_log)


#schedule to write stats to DB
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=UTILS.stats,
    trigger=IntervalTrigger(minutes=get_stats),#10 minute
    id='printing_job',
    name='Print date and time every five seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    # app.debug = True
    app.run()