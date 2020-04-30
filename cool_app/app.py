'''
Comments in this file will be verbose as it is intended as a learning tool

The cool-app is intended to demonstrate some cool features of microservices running in a typical Kubernetes cluster.

The following high-level features are implemented:

* Liveliness and readyness probes as suggested by Kubernetes - see https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
* Metrics collectors and API, using Redis as a backend
* Circuit-Breaker pattern to cater for cases where redis is not installed or otherwise unusable - see https://martinfowler.com/bliki/CircuitBreaker.html
'''

import socket
import traceback
import os
import sys
from datetime import datetime
import sqlite3
from flask import Flask, render_template, redirect, url_for, Response, request
import redis 
from cool_app.state.state_manager import *


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                       THREAD INITIALIZATION                          /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


app = Flask(__name__)
thread_pid = os.getpid()
conn = sqlite3.connect(os.getenv('STATE_DB_PATH', '/opt/state.db'))
if not test_state_db_ready(conn=conn, thread_pid=thread_pid):
    print('[pid={}] warning: state DB failed readyness'.format(thread_pid))
start_time = int(datetime.now().timestamp())
app_version = '0.0.1'
redis_client = None



'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                          HELPER FUNCTIONS                            /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


def get_redis_client():
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'cool-app-redis-master'), port=6379, db=0)
        except:
            traceback.print_exc(file=sys.stdout)
            redis_client = None
            print('[pid={}] warning: Failed to connect to redis'.format(thread_pid))
    return redis_client


def get_redis_error_count()->int:
    result = 99
    try:
        result = get_field_value(conn=conn, thread_pid=thread_pid, field_name='redis_bad_counter', default=result)
    except:
        traceback.print_exc(file=sys.stdout)
    return result


def reset_redis_error_count():
    try:
        result = update_thread_field(conn=conn, thread_pid=thread_pid, field_name='redis_bad_counter', value=0)
        print('[pid={}] info: redis error count set to {}'.format(thread_pid, result))
    except:
        traceback.print_exc(file=sys.stdout)
        print('[pid={}] warning: failed to reset redis error count'.format(thread_pid))


def log_redis_critical_error()->int:
    redis_circuit_breaker_counter = 99
    try:
        redis_circuit_breaker_counter = update_thread_field(conn=conn, thread_pid=thread_pid, field_name='redis_bad_counter', value=get_redis_error_count() + 1)
    except:
        traceback.print_exc(file=sys.stdout)
    return redis_circuit_breaker_counter


def record_hit(key: str, value: int):
    try:
        if get_redis_error_count() == 0:
            try:
                r = get_redis_client()
                with r.lock('host-{}-pid-{}'.format(get_hostname(), str(thread_pid)), blocking_timeout=5) as lock:
                    # code you want executed only after the lock has been acquired
                    r.incr(name=key, amount=value)
                    r.incr(name='total-record-hits', amount=1)
                    r.incr(name='host-{}-thread-{}-total-record-hits'.format(get_hostname(), str(thread_pid)), amount=1)
            except LockError:
                print('[pid={}] warning: failed to acquire redis lock. this metric will not be recorded: function=record_hit() key={}'.format(thread_pid, key))            
        else:
            print('[pid={}] info: record_hit(): redis is not ready'.format(thread_pid))
    except:      
        log_redis_critical_error()
        traceback.print_exc(file=sys.stdout)


def get_hostname():
    hostname = 'unknown2'
    try:
        hostname = socket.gethostname()
    except:
        traceback.print_exc(file=sys.stdout)
    return hostname


def livelyness()->bool:
    try:
        if get_field_value(conn=conn, thread_pid=thread_pid, field_name='alive', default=0) == 1:
            return True
    except:
        traceback.print_exc(file=sys.stdout)
    return False


def readiness()->bool:
    try:
        if get_field_value(conn=conn, thread_pid=thread_pid, field_name='ready', default=0) == 1:
            return True
    except:
        traceback.print_exc(file=sys.stdout)
    return False


def uptime()->int:
    return int(datetime.now().timestamp()) - start_time


def get_metric_by_key(name: str='welcome-resource')->int:
    print('[pid={}] get_metric_by_key(): called for name={}'.format(thread_pid, name))
    value = 0
    try:
        if get_redis_error_count() == 0:
            r = get_redis_client()
            value = r.get(name=name)
            if isinstance(value, str):
                value = int(value)
            elif isinstance(value, bytes):
                value = int(value.decode('utf-8'))
            else:
                print('[pid={}] get_metric_by_key(): Unable to convert value. Value type is "{}" and raw value: {}'.format(thread_pid, type(value), value))
                value = 0
    except:
        log_redis_critical_error()
        traceback.print_exc(file=sys.stdout)
        value = 0
    return value


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                     REQUEST HANDLERS SECTION                         /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


@app.route('/')
def welcome():
    record_hit(key='welcome-resource', value=1)
    return render_template('welcome.html', hostname=get_hostname(), app_version=app_version, uptime=uptime())


@app.route('/metrics/get-circuit-breakers')
def metrics_get_circuit_breakers():
    record_hit(key='metrics-get-circuit-breakers-resource', value=1)
    return {
        'Redis': {
            'Flag': get_redis_error_count(),
            'Counter': get_redis_error_count()
        }
    }


@app.route('/admin/reset-circuit-breaker')
def admin_reset_circuit_breaker(name: str='redis'):
    global get_redis_error_count()
    get_redis_error_count() = 0
    reset_redis_error_count()
    return redirect(url_for('metrics_get_circuit_breakers'))
    


@app.route('/metrics/get-counter')
def metrics_get_stats(name: str='welcome-resource'):
    record_hit(key='metrics-get-stats-resource', value=1)
    print('[pid={}] metrics_get_stats(): called for name={}'.format(thread_pid, name))
    return '{}'.format(get_metric_by_key(name=request.args.get('name', name)))


@app.route('/status')
def status():
    record_hit(key='status-resource', value=1)
    hostname = '{}'.format(get_hostname())
    return 'pid={}|   hostname={} |   app_version={}   |   uptime={}\n'.format(
        str(thread_pid).ljust(5),
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
        traceback.print_exc(file=sys.stdout)
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
    record_hit(key='probe-alive-resource', value=1)
    if livelyness() is False:
        return ('** Oops, I am dead?\n', 500)
    return '** ok\n'


@app.route('/probe/ready')
def k8s_ready():
    record_hit(key='probe-ready-resource', value=1)
    if readiness() is True:
        return '** ok\n'
    return ('** Starting up...\n', 500)

# EOF
