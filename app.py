from flask import Flask, render_template
from healthcheck import HealthCheck
import urllib.request
import socket

app = Flask(__name__, static_url_path='/static')
health = HealthCheck(app, "/status")

hostname=(socket.gethostname())

def demo_available():
	code = urllib.request.urlopen("http://127.0.0.1:5000").getcode()
	print(code)
	if code == 200:
		return True, "OK"
	else:
		return False, "ERROR"
        
health.add_check(demo_available)

@app.route('/')
def index():
    return render_template(
        'index.html',
        hostname=hostname,
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0")