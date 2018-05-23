import logging
import sys
from perfsonar_data_helper import app_factory


logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG)

app = app_factory.create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="9876")
