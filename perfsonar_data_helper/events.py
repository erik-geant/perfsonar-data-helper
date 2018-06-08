import logging
from perfsonar_data_helper import socketio
from flask_socketio import emit


@socketio.on('message')
def handle_message(message):
    logging.debug("got socket 'message': %r" % message)
    emit('status', "response #1")
    emit('status', "response #2")


