from flask import Flask, render_template, jsonify, request
import socket
import math
from os import getenv
import signal
import time
import logging
import sys

if len(getenv("APP_VERSION")) == 0:
    APP_VERSION = "v1.0.0"
else:
    APP_VERSION = getenv("APP_VERSION")

if len(getenv("HOSTNAME")) == 0:
    HOSTNAME = socket.gethostname()
else:
    HOSTNAME = getenv("HOSTNAME")

app = Flask(__name__, static_url_path="/static")
ready = True

# Create a custom logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
werkzeug_format = '%(remote_addr)s - [%(asctime)s] "%(request_method)s %(path)s %(protocol)s" %(status)s'
formatter = logging.Formatter(werkzeug_format, datefmt='%d/%b/%Y %H:%M:%S')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)


@app.route("/status", methods=["GET"])
def status():
    return (
        jsonify(
            Healthy=True,
            Host=HOSTNAME,
            AppVersion=APP_VERSION,
            StatusCode=200
        ),
        200,
        {"ContentType": "application/json"},
    )


def handle_sigterm(*args):
    global ready
    print("SIGTERM received: marking as not ready")
    ready = False
    time.sleep(90)
    print("Finished draining, exiting")


signal.signal(signal.SIGTERM, handle_sigterm)


@app.route("/sticky", methods=["GET"])
def sticky():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr

    log_data = {
        'remote_addr': client_ip,
        'asctime': time.strftime("%d/%b/%Y %H:%M:%S"),
        'request_method': request.method,
        'path': request.path,
        'protocol': request.environ.get('SERVER_PROTOCOL'),
        'status': 200,
    }

    logger.info(werkzeug_format % log_data)

    return (
        jsonify(
            Message="Sticky session test",
            Host=HOSTNAME,
            AppVersion=APP_VERSION,
            ClientIP=client_ip
        ),
        200,
        {"ContentType": "application/json"},
    )


@app.route('/stress', methods=['GET'])
def stress():
    stress_enabled = getenv('ENABLE_STRESS', 'false').lower() == 'true'
    if not stress_enabled:
        return jsonify({
            "Message": "The /stress endpoint is currently disabled.",
            "Hostname": HOSTNAME
        }), 200

    x = 0.0001
    for i in range(1000000):
        x += math.sqrt(x)

    return jsonify({
        "Message": "Calculation completed!",
        "Hostname": HOSTNAME
    }), 200


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html", hostname=HOSTNAME, app_version=APP_VERSION
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8882)
