# perfSONAR data helper API

## Overview

This module implements a Flask-based webservice which
provides some wrappers for various queries of data from
the perfSONAR network.

The webservice is communicates with clients over HTTP.
Responses to valid requests are returned as JSON messages.
The server will therefore return an error unless
`application/json` is in the `Accept` request header field.

HTTP communication and JSON grammar details are
beyond the scope of this document.
Please refer to [RFC 2616](https://tools.ietf.org/html/rfc2616)
and www.json.org for more details.


## configuration

A configuration file can be provided when launching the web service.
The runtime-accessible path of this file should be
stored in the environment variable `SETTINGS FILENAME`.

The configuration file is python.  The following is an example:

```python
SLS_BOOTSTRAP_URL = "http://ps-west.es.net:8096/lookup/activehosts.json"
SLS_CACHE_FILENAME = "/tmp/sls-cache.json"
STARTUP_REFRESH_SLS_CACHE = True
PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS = 5
```

The following values are valid in the configuration file.

- `SLS_BOOTSTRAP_URL`: url of the server that returns a list of
 active SLS server.

- `SLS_CACHE_FILENAME`: local path of a file used for caching
 lookup service data

- `STARTUP_REFRESH_SLS_CACHE`: refresh the sls cache when starting
 the server before accepting connections

- `PSCHEDULER_TASK_POLLING_INTERVAL_SECONDS`: number of seconds to wait
 between each request when polling for pscheduler task status


## running this module

This module has been tested in the following execution environments:

- As an embedded Flask application.
For example, the application could be launched as follows:

```bash
$ export FLASK_APP=app.py
$ export SETTINGS_FILENAME=settings.cfg
$ flask run
```

- As an Apache/`mod_wsgi` service.
  - Details of Apache and `mod_wsgi`
configuration are beyond the scope of this document.


## protocol specification

The following resources can be requested from the webservice.

### synchronous resources

* `/latency/<source address>/<destination address>`

  This resource sends a request to the `pscheduler` instance running
  on the source system to schedule and perform a latency
  test.

  The response will be a JSON message formatted list
  of the latency measurements for each packet use in the test,
  and will be formatted as follows:

  ```json
    {
      "$schema": "http://json-schema.org/draft-06/schema#",
      "type": "array",
      "minimum": 0.0,
      "items": {"type": "number"},
    }
  ```

* `/throughput/<source address>/<destination address>`

  This resource sends a request to the `pscheduler` instance running
  on the source system to schedule and perform a throughput
  test.

  The response will be a JSON message formatted list
  of the throughput measurement results and will be
  formatted as follows:

  ```json
    {
      "$schema": "http://json-schema.org/draft-06/schema#",
      "type": "array",
      "minItems": 1,
      "items": {
          "type": "object",
          "properties": {
              "start": {"type": "number", "minimum": 0.0},
              "end": {"type": "number", "minimum": 0.0},
              "bytes": {"type": "integer", "minimum": 0},
          },
          "required": ["start", "end", "bytes"]
      }
    }
  ```

* `/mplist/refresh`

  This resource refreshes the cached SLS data.the server top The response will be a JSON message (key / value pairs) formatted

* `/mplist/<tool name>`

  This resource returns a list of url's of measurement points
  running pscheduler and also supporting the requested tool
  (e.g. `owping`).

  The response will be a JSON message formatted
  according to the following JSON schema:

  ```json
    {
      "$schema": "http://json-schema.org/draft-06/schema#",
      "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "hostname": {"type": "string"},
            "name": {"type": "string"},
            "communities": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["hostname", "name", "communities"]
    }
  ```

### asynchronous resources

The following resources may be used to asynchronously launch a
measurement and periodically retrieve the status and eventually
the result.  The running job is maintained using session data
stored in a cookie returned with the response to the
`/pscheduler/measurement` resource.  Clients must therefore support
storing and sending cookies in order to use these resources.
In order to use these resources the client must support
storing and sending cookies.

* `/pscheduler/measurement`

  Use this resource to launch a new measurement.  The client
  must send a post request with payload formatted according
  to the following JSON schema:

