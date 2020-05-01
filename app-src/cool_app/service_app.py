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
import connexion


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                       THREAD INITIALIZATION                          /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


SPECIFICATION_DIR = os.getenv('SPECIFICATION_DIR', '/usr/src/app')
print('Reading OpenAPI from file "{}"'.format(os.getenv('SPECIFICATION_DIR', '/opt/cool-app.yaml')))
start_time = int(datetime.now().timestamp())
app_version = '0.0.1'


def run_service():
    app.run(port=8080)


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                          HELPER FUNCTIONS                            /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


def get_hostname():
    hostname = 'unknown2'
    try:
        hostname = socket.gethostname()
    except:
        traceback.print_exc(file=sys.stdout)
    return hostname


def uptime()->int:
    return int(datetime.now().timestamp()) - start_time


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                     REQUEST HANDLERS SECTION                         /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


def welcome(message):
    return {'message': message}


options = {"swagger_ui": False}
if int(os.getenv('SWAGGER_UI', '1')) > 0:
    options = {"swagger_ui": True}    
app = connexion.FlaskApp(__name__, specification_dir=SPECIFICATION_DIR)
app.add_api('cool-app.yaml', strict_validation=True)
application = app.app # expose global WSGI application object

# EOF
