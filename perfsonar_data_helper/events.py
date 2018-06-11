import logging
from perfsonar_data_helper import socketio
from perfsonar_data_helper import latency
from perfsonar_data_helper import throughput
from flask_socketio import emit
from flask import current_app

@socketio.on('message')
def handle_message(message):
    logging.debug("got socket 'message': %r" % message)
    emit('status', "response #1")
    emit('status', "response #2")

import eventlet
import datetime, time

def _formatted_time():
    return datetime \
        .datetime \
        .utcfromtimestamp(time.time()) \
        .strftime('%Y-%m-%dT%H:%M:%SZ')

from flask import request

@socketio.on('measurement')
def handle_message(message):


    logging.debug("request.sid: %r" % request.sid)

    def _emit_status(status_message):
        logging.debug("socket status message: %r" % status_message)
        emit("status", {
            "status": status_message,
            "time": _formatted_time()
        })
        # socketio.sleep(0)
        eventlet.sleep(0)

    if message["type"] == "latency":
        result = {
            "successful": True,
            "data": latency.get_delays(
                source=message["source"],
                destination=message["destination"],
                polling_interval=current_app.config["PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS"],
                status_handler=_emit_status)
        }
    elif message["type"] == "throughput":
        result = {
            "successful": True,
            "data": throughput.get_throughput(
                source=message["source"],
                destination=message["destination"],
                polling_interval=current_app.config["PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS"],
                status_handler=_emit_status)
        }
    else:
        logging.debug("error: unrecognized measurement type")
        result = {"success": False}
        return

    logging.debug("task successful, return result: %r" % result)
    result["time"] = _formatted_time()
    emit("complete", result)
