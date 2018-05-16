from flask import Flask

app = Flask(__name__)

@app.route("/owamp/<string:source>/<string:destination>")
def owamp(source, destination):
    return "source: %s, destination: %s" % (source, destination)

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app.run(host="0.0.0.0", port="9876")
