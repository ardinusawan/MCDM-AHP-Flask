from flask import Flask
from flask import jsonify
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import utils as UTILS

app = Flask(__name__)

get_stats = 0.6 # minutes

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
    trigger=IntervalTrigger(minutes=get_stats),
    id='get_docker_stats',
    name='Get Docker Stats every ten minutes',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    # app.debug = True
    app.run()