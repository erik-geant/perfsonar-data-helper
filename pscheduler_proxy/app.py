import logging
import sys
from pscheduler_proxy import app_factory


logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG)

app = app_factory.create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="9876")
