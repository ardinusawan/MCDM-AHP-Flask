import atexit

import utils as utils
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, render_template
from flask import jsonify
from flask import request
import db as database
import ahp as ahp
import os


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

get_stats = database.interval()

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/container/list")
def container_list():
    res = utils.stats()
    return jsonify(res)

@app.route("/stats-now")
def stream_stats():
    data = dict()
    data["stream"] = True
    res = utils.stats(**data)
    # return jsonify({"message":"success", "containers":res})
    return render_template('index.html',**locals())

@app.route("/stats-log", methods=['GET', 'POST'])
def stats_log():
    table_name = "stats"
    if request.method == 'GET':
        res = utils.log(table_name)
        return jsonify(res)
    if request.method == 'POST':
        limit = True
        res = utils.log(table_name, limit, request.form["from"], request.form["to"])
        return jsonify(res)

@app.route("/result-log", methods=['GET', 'POST'])
def result_log():
    table_name = "result"
    if request.method == 'GET':
        res = utils.log(table_name)
        return jsonify(res)
    if request.method == 'POST':
        limit = True
        res = utils.log(table_name, limit, request.form["from"], request.form["to"])
        return jsonify(res)

# schedule to write stats to DB
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=utils.stats,
    trigger=IntervalTrigger(minutes=get_stats),
    id='get_docker_stats',
    name='Get Docker Stats every %s minutes' % get_stats,
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.debug = False
    app.run(host='0.0.0.0')
