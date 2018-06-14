"""
testing startup
"""

if __name__ == "__main__":
    import logging
    import sys
    import perfsonar_data_helper

    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG)

    app = perfsonar_data_helper.create_app()
    app.run(host="0.0.0.0", port="9876")
