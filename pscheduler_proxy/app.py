from flask import Flask, jsonify
import owamp

app = Flask(__name__)


@app.route("/owamp/<string:source>/<string:destination>")
def owamp_raw(source, destination):
    return jsonify(owamp.get_raw(source=source, destination=destination))


if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app.run(host="0.0.0.0", port="9876")
