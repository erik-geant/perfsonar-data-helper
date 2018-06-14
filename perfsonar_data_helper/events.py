# import logging
# from perfsonar_data_helper import socketio
# from perfsonar_data_helper import latency
# from perfsonar_data_helper import throughput
# from perfsonar_data_helper.pscheduler import client as pscheduler_client
# from flask_socketio import emit
# from flask import current_app, session
#
#
# import eventlet
#
# @socketio.on('message')
# def handle_message(message):
#     logging.debug("got socket 'message': %r" % message)
#     emit('status', "response #1")
#     emit('status', "response #2")
#
# import datetime, time
#
#
# def _formatted_time():
#     return datetime \
#         .datetime \
#         .utcfromtimestamp(time.time()) \
#         .strftime('%Y-%m-%dT%H:%M:%SZ')
#
#
# def _ws_message(message):
#     return {
#         "message": message,
#         "time": _formatted_time()
#     }
#
#
# @socketio.on('measurement')
# def schedule_measurement(message):
#     if not {"type", "source", "destination"}.issubset(set(message.keys())):
#         emit("error", _ws_message("bad message format"))
#         return
#
#     if message["type"] not in {"latency", "throughput"}:
#         emit("error", _ws_message("bad measurement type"))
#         return
#
#     if message["type"] == "latency":
#         test_data = latency.make_test_data(
#             message["source"],
#             message["destination"])
#     else:
#         emit("error", _ws_message("to do: " + message["type"]))
#         return
#
#     import json
#     logging.debug("creating task, test data: " + json.dumps(test_data))
#
#     task_url = pscheduler_client.create_task(
#         message["source"],
#         test_data)
#
#     session["task_url"] = task_url
#     session["type"] = message["type"]
#
#     emit("status", _ws_message("scheduled"))
#
#
# @socketio.on("get-status")
# def check_task_status():
#     if not {"task_url", "type"}.issubset(set(session.keys())):
#         emit("error", _ws_message("session not initialized"))
#         return
#
#     assert session["type"] in {"latency", "throughput"}  # sanity
#
#     logging.debug("calling get_task_status, task_url: %r" % session["task_url"])
#     state, result = pscheduler_client.get_task_status(session["task_url"])
#     logging.debug("task state: %r" % state)
#
#     emit("status", _ws_message(state))
#
#     if result is None:
#         return
#
#     if session["type"] == "latency":
#         data = latency.format_result(result)
#     else:
#         assert False  # sanity (should have already been checked)
#
#     logging.debug("task complete")
#
#     emit("complete", {
#         "data": data,
#         "type": session["type"],
#         "time": _formatted_time()
#     })
#
#
