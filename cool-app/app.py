import socket
import traceback
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, Response


app = Flask(__name__)
start_time = int(datetime.now().timestamp())
with open('/tmp/alive', 'w') as f:
    f.write('1')
app_version = '0.0.1'


def get_hostname():
    hostname = 'unknown2'
    try:
        hostname = socket.gethostname()
    except:
        traceback.print_exc()
    return hostname


def livelyness()->bool:
    try:
        with open('/tmp/alive', 'r') as f:
            lines = f.readlines()
        if len(lines) > 0:
            if int(lines[0]) != 1:
                return False
    except:
        traceback.print_exc()
    return True


def readiness()->bool:
    return True


def uptime()->int:
    return int(datetime.now().timestamp()) - start_time


@app.route('/')
def welcome():
    return render_template('welcome.html', hostname=get_hostname(), app_version=app_version, uptime=uptime())


@app.route('/status')
def status():
    hostname = '{}'.format(get_hostname())
    return 'pid={}|   hostname={} |   app_version={}   |   uptime={}\n'.format(
        str(os.getpid()).ljust(5),
        hostname.ljust(40),
        app_version,
        uptime()
    )


@app.route('/die')
def die():
    try:
        with open('/tmp/alive', 'w') as f:
            f.write('0')
    except:
        traceback.print_exc()
    return redirect(url_for('welcome'))


@app.route('/starve')
def starve():
    def generate():
        l = list()
        counter = 0
        for i in range(0, 1024*1024*1024):
            counter += 1
            l.append('{}: ********************************'.format(i))
            if counter > 100000:
                yield 'Generated {} items\n'.format(i)
                counter = 0
    return Response(generate(), mimetype='text/plain')


@app.route('/probe/alive')
def k8s_alive():
    if livelyness() is False:
        return ('** Oops, I died\n', 500)
    return '** ok\n'


@app.route('/probe/ready')
def k8s_ready():
    if readiness() is True:
        return '** ok\n'
    return ('** Starting up...\n', 500)

# EOF
