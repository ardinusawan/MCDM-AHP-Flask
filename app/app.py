from flask import Flask
import docker
from flask import jsonify

app = Flask(__name__)
client = docker.from_env()

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/container/list")
def container_list():
    list = client.containers.list()
    return jsonify("this is list of container")

if __name__ == "__main__":
    # app.debug = True
    app.run()