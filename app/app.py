import atexit

import utils as utils
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, render_template, redirect
from flask import jsonify
from flask import request
import db as database
import ahp as ahp
import os
import time
import requests
from flask_cors import CORS, cross_origin



tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
application = Flask(__name__, template_folder=tmpl_dir)
CORS(application)
get_stats = database.interval()

@application.route("/")
def hello():
    return "Hello World!"

def check(url):
    return requests.head(url)

@application.route("/moodle/<moodle_id>")
def moodle(moodle_id):
    moodle = 'moodle' + moodle_id
    utils.start_docker(moodle)
    if moodle_id == "10":
        moodle_id = str(10010)
    else:
        moodle_id = str(1000) + moodle_id

    url = "http://10.151.34.236:" + moodle_id
    while (requests.head(url).status_code!=200):
        time.sleep(1)

    return redirect(url, code=302)

@application.route("/compute")
def container_list():
    res = utils.stats()
    return jsonify(res)

@application.route("/stats-now")
def stream_stats():
    data = dict()
    data["stream"] = True
    res = utils.stats(**data)
    # return jsonify({"message":"success", "containers":res})
    return render_template('index.html',**locals())


@application.route("/result", methods=['GET', 'POST'])
def result_log():
    table_name = "result"
    if request.method == 'GET':
        res = utils.log(table_name)
        return jsonify(res)
    if request.method == 'POST':
        limit = True
        res = utils.log(table_name, limit, request.form["from"], request.form["to"])
        return jsonify(res)

@application.route("/stats", methods=['GET', 'POST'])
def stats():
    table_name = "stats"
    if request.method == 'GET':
        res = utils.log(table_name)
        return jsonify(res)
    if request.method == 'POST':
        limit = True
        res = utils.log(table_name, limit, request.form["from"], request.form["to"])
        return jsonify(res)

@application.route("/server-stats", methods=['GET', 'POST'])
def server_stats():
    table_name = "server_stats"
    if request.method == 'GET':
        res = utils.log(table_name)
        return jsonify(res)
    if request.method == 'POST':
        limit = True
        res = utils.log(table_name, limit, request.form["from"], request.form["to"])
        return jsonify(res)


@application.route("/database/create")
def create_database():
    database.create_table()
    return jsonify({"message":"success"})

@application.errorhandler(500)
def internal_error(exception):
    application.logger.error(exception)
    return render_template('500.html'), 500


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
    application.debug = False
    application.run(host='0.0.0.0')
