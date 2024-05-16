from flask import Flask, render_template, jsonify
import socket
from os import getenv

if len(getenv('APP_VERSION')) == 0:
    APP_VERSION = "V1.0"
else:
    APP_VERSION = getenv('APP_VERSION')

if len(getenv('HOSTNAME')) == 0:
    HOSTNAME = socket.gethostname()
else:
    HOSTNAME = getenv('HOSTNAME')

app = Flask(__name__, static_url_path='/static')
        
@app.route('/status', methods=['GET'])
def status():
	return jsonify(
		Healthy = True,
		Host = HOSTNAME,
        AppVersion = APP_VERSION,
		StatusCode = 200
	), 200, {'ContentType':'application/json'}

@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        hostname = HOSTNAME,
        app_version = APP_VERSION
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8882)
