import atexit

import utils as utils
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

get_stats = 10  # minutes


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/container/list")
def container_list():
    utils.stats()
    # print(dir(list[0]))
    con_log = ""
    utils.stats()
    return con_log


@app.route("/AHP/1", methods=['GET', 'POST'])
def computing_vector():
    if request.method == 'POST':
        data = request.get_json()
        # status = database.insert_comparison_matrix(data['parameter_data'], **data['comparison'])
        return jsonify(data)
    else:
        return jsonify({"Message": "Success"}, sort_keys=False, indent=2)


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
