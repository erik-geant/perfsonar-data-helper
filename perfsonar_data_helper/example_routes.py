import base64
import json
import os
from flask import Blueprint, current_app, url_for, \
        send_from_directory, request, render_template


examples = Blueprint("sample-client-routes", __name__)

static_base_path = os.path.join(
        os.path.dirname(__file__),
        "static")


@examples.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(static_base_path, path)

@examples.route("/sample2/run-test", methods=['GET', 'POST'])
def run_test():

    def _current_params():
        previous = request.values.get("previous", None)
        if previous:
            previous = json.loads(
                base64.b64decode(previous.encode("utf-8")).decode("utf-8"))
        else:
            previous = {
                "source": "",
                "destination": "",
                "measurement": ""
            }
        return {
            "source": request.values.get(
                "source",
                previous["source"]),
            "destination": request.values.get(
                "destination",
                previous["destination"]),
            "measurement": request.values.get(
                "measurement",
                previous["measurement"]
            )
        }

    def _encoded_current_params():
        return base64.b64encode(
            json.dumps(_current_params()).encode("utf-8")).decode("utf-8")


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
            return render_template(
                "latency-histogram-http-long-polling.html.j2",
                **params)
        elif params["measurement"] == "throughput":
            return render_template(
                "throughput-timeseries-http-long-polling.html.j2",
                **params)
        assert False, "unknown meaurement value: '%s'" % params["measurement"]
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

