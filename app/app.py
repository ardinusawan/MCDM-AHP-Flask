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

get_stats = 10  # minutes


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/container/list")
def container_list():
    res = utils.stats()
    # if res["status"] != "error":
    #     return jsonify({"status":"success", "message":res})
    # else:
    #     return jsonify(res)

    return jsonify(res)
@app.route("/stats")
def stream_stats():
    data = dict()
    data["stream"] = True
    res = utils.stats(**data)
    # return jsonify({"message":"success", "containers":res})
    return render_template('index.html',**locals())
@app.route("/AHP/1", methods=['GET', 'POST'])
def computing_vector():
    if request.method == 'POST':
        data = request.get_json()
        status = database.insert_comparison_matrix(data['parameter_data'], **data['comparison'])
        return jsonify(data)
    else:
        return jsonify({"Message": "Success"}, sort_keys=False, indent=2)

@app.route("/AHP/result", methods=['GET'])
def ahp_result():
    return jsonify(ahp.score())

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
    app.debug = True
    app.run()
