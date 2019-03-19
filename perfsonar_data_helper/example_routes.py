import base64
import json
import logging
import os
from flask import Blueprint, url_for, \
        send_from_directory, request, render_template


examples = Blueprint("sample-client-routes", __name__)

static_base_path = os.path.join(
        os.path.dirname(__file__),
        "static")


@examples.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(static_base_path, path)


DEFAULT_PARAMS = {
    "source": "",
    "destination": "",
    "measurement": "",

    # latency params
    "wait": "",
    "timeout": "",
    "padding": "",
    "delay": "",
    "dscp": "",
    "bucket": "",

    # throughput params
    "duration": "",
    "interval": "",
    "tos": "",
    "protocol": "",
    "address_type": "",
    "tcp_window": "",
    "udp_buffer": "",
    "max_bandwidth": "",
}

LATENCY_PARAM_NAMES = [
    "source", "destination",
    "wait", "timeout", "padding", "delay", "dscp", "bucket"]
THROUGHPUT_PARAM_NAMES = [
    "source", "destination",
    "duration", "interval", "tos", "protocol", "address_type",
    "tcp_window", "udp_buffer", "max_bandwidth"]


@examples.route("/sample/run-test", methods=['GET', 'POST'])
def run_test():

    def _current_params():
        previous = request.values.get("previous", None)
        if previous:
            previous = json.loads(
                base64.b64decode(previous.encode("utf-8")).decode("utf-8"))
        else:
            previous = DEFAULT_PARAMS

        logging.error("%r" % request.values)
        return dict([
            (p, request.values.get(p, previous[p]))
            for p in DEFAULT_PARAMS.keys()
        ])

    def _encoded_current_params():
        return base64.b64encode(
            json.dumps(_current_params()).encode("utf-8")).decode("utf-8")

    def _measurement_params_string():
        request_params = _current_params()
        if request_params["measurement"] == "latency":
            param_names = LATENCY_PARAM_NAMES
        else:
            param_names = THROUGHPUT_PARAM_NAMES

        param_strings = []
        for n in param_names:
            if request_params[n]:
                param_strings.append('%s: "%s"' % (n, request_params[n]))
        return "{%s}" % ", ".join(param_strings)

    state = request.values.get("state", "configure")

    if state == "select source":
        return render_template(
            "select-mp.html.j2",
            submission_url=url_for("sample-client-routes.run_test"),
            hostname_varname="source",
            next_state="configure",
            previous_params_json=_encoded_current_params())
    elif state == "select destination":
        return render_template(
            "select-mp.html.j2",
            submission_url=url_for("sample-client-routes.run_test"),
            hostname_varname="destination",
            next_state="configure",
            previous_params_json=_encoded_current_params())
    elif state == "run":
        params = _current_params()
        if params["measurement"] == "latency":
            filename = "latency-histogram-http-long-polling.html.j2"
        elif params["measurement"] == "throughput":
            filename = "throughput-timeseries-http-long-polling.html.j2"
        else:
            assert False, \
                "unknown meaurement value: '%s'" % params["measurement"]
        return render_template(
            filename,
            measurement_params=_measurement_params_string())
    else:
        return render_template(
            "configure_test.html.j2",
            submission_url=url_for("sample-client-routes.run_test"),
            **_current_params())
    #
    # request.values.get()
    # get post vars:
    #     source or dest mp hostname to be updated\
    #     json payload with previous params
    # buttons:
    #     select source mp
    #     select dst mp
    #     run test (enabled only if source/dest)
    # form with:
    #     - source
    #     - dest
    #     - other vars
    # select mp, populate vars in template:
    #     - json of test vars
    #     - name of host var (source or dest)
    #     - return url???
    #     - render template
    #
