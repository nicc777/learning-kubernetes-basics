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
from flask import Flask, render_template, redirect, url_for, Response
import redis 


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                       THREAD INITIALIZATION                          /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


app = Flask(__name__)
start_time = int(datetime.now().timestamp())
with open('/tmp/alive', 'w') as f:
    f.write('1')
app_version = '0.0.1'
redis_circuit_breaker_flag = 0 
redis_client = None
thread_pid = os.getpid()


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
    result = -1
    global redis_circuit_breaker_flag
    try:
        result = os.path.getsize('redis_error')
        print('[pid={}] info: get_redis_error_count(): result={}'.format(thread_pid, result))
    except:
        try:
            with open('redis_error', 'a') as f:
                f.print('\n')
        except:
            print('[pid={}] warning: failed to initialize redis_error file. If this message repeats often, kill the POD'.format(thread_pid))
            redis_circuit_breaker_flag = 1
        traceback.print_exc(file=sys.stdout)
        result = 0
        print('[pid={}] warning: can not determine redis file size - returning 0'.format(thread_pid))
    return result


def reset_redis_error_file():
    try:
        os.unlink('redis_error')
    except:
        traceback.print_exc(file=sys.stdout)
        print('[pid={}] warning: failed to reset redis_error file'.format(thread_pid))


def log_redis_critical_error()->int:
    redis_circuit_breaker_counter = get_redis_error_count()
    global redis_circuit_breaker_flag
    try:
        with open('redis_error', 'a') as f:
            f.print('*\n')
        redis_circuit_breaker_counter = get_redis_error_count()
    except:
        traceback.print_exc(file=sys.stdout)
        if redis_circuit_breaker_counter >= 10:
            print('[pid={}] warning: DISABLING REDIS [function: log_redis_critical_error()]'.format(thread_pid))
            redis_circuit_breaker_flag = 1
    return redis_circuit_breaker_counter


def record_hit(key: str, value: int):
    global redis_circuit_breaker_flag
    try:
        if redis_circuit_breaker_flag == 0:
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
            if get_redis_error_count() < 10:
                redis_circuit_breaker_flag = 0
                print('[pid={}] info: record_hit(): Hits will be recorded again from the next attempt'.format(thread_pid))
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
        with open('/tmp/alive', 'r') as f:
            lines = f.readlines()
        if len(lines) > 0:
            if int(lines[0]) != 1:
                return False
    except:
        traceback.print_exc(file=sys.stdout)
    return True


def readiness()->bool:
    return True


def uptime()->int:
    return int(datetime.now().timestamp()) - start_time


def get_metric_by_key(name: str='welcome-resource')->int:
    value = 0
    try:
        if redis_circuit_breaker_flag == 0:
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
            'Flag': redis_circuit_breaker_flag,
            'Counter': get_redis_error_count()
        }
    }


@app.route('/admin/reset-circuit-breaker')
def admin_reset_circuit_breaker(name: str='redis'):
    global redis_circuit_breaker_flag
    redis_circuit_breaker_flag = 0
    reset_redis_error_file()
    return redirect(url_for('metrics_get_circuit_breakers'))
    


@app.route('/metrics/get-counter')
def metrics_get_stats(name: str='welcome-resource'):
    record_hit(key='metrics-get-counter-resource', value=1)
    return '{}'.format(get_metric_by_key(name=name))


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
        return ('** Oops, I died\n', 500)
    return '** ok\n'


@app.route('/probe/ready')
def k8s_ready():
    record_hit(key='probe-ready-resource', value=1)
    if readiness() is True:
        return '** ok\n'
    return ('** Starting up...\n', 500)

# EOF
