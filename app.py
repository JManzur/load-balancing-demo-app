from flask import Flask, render_template, jsonify
import socket

app = Flask(__name__, static_url_path='/static')

hostname=(socket.gethostname())
        
@app.route('/status', methods=['GET'])
def status():
	return jsonify(
		Healthy = True,
		Host = hostname,
		StatusCode = 200
	), 200, {'ContentType':'application/json'}

@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        hostname=hostname,
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8882)