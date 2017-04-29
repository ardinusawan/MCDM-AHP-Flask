import atexit

import utils as utils
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask
from flask import jsonify
from flask import request
import db as database
import ahp as ahp
app = Flask(__name__)

get_stats = 10  # minutes


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/container/list")
def container_list():
    res = utils.stats()
    return jsonify({"status":"success", "data":res})

@app.route("/stats")
def stream_stats():
    data = dict()
    data["stream"] = True
    res = utils.stats(**data)
    return jsonify({"message":"success", "containers":res})

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
    app.debug = False
    app.run()
