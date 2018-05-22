from flask import Flask, jsonify
from flask_cors import CORS

from pscheduler_proxy import app_factory
from pscheduler_proxy import latency
from pscheduler_proxy import sls

app = app_factory.create_app()


@app.route("/latency/<string:source>/<string:destination>")
def latency(source, destination):
#    return jsonify(latency.get_raw(source=source, destination=destination))
    return jsonify(latency.get_delays(source=source, destination=destination))
#    return jsonify(latency.get_delays_debug(source=source, destination=destination))


@app.route("/mplist/<string:tool>")
def mplist(tool):
    if tool == "refresh":
        sls.update_cached_mps(
            app.config["SLS_BOOTSTRAP_URL"],
            app.config["SLS_CACHE_FILENAME"])
        result = {"result": True}
    else:
        result = sls.load_mps(tool, app.config["SLS_CACHE_FILENAME"])
        result = list(result)

    return jsonify(result)


if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app.run(host="0.0.0.0", port="9876")
