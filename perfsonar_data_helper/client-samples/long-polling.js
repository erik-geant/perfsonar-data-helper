// note that draw_diagram & reload_diagram are defined in
// latency-histogram.js or throughput-???.js

var draw_diagram_handler = draw_diagram;
var statusIntervalId = null;
var measurementIntervalId = null;
var session_params = null;
var server_base_url = "http://" + document.domain + ":" + location.port + "/pscheduler/";




function handle_response(response) {
    if (response.type == "status") {
        $('#status').text(response.message + " [" + response.time + "]");
        console.log("status [" + response.time + "]: " + response.message);

        if (["pending", "on-deck", "running", "scheduled"].indexOf(response.message) < 0) {
            // some sort of error ... restart another measurement
            if (measurementIntervalId != null) {
                clearTimeout(measurementIntervalId);
            }
            measurementIntervalId = setTimeout(
                function() { launch_long_polling_measurement(null) }, 0);
            return;
        }

        // js bug?
        // callback is called after the timeout once
        // for each call to setTimeout ...?
        // ... at least in chrome, thus the clearTimeout behavior
        if (statusIntervalId != null) {
            clearTimeout(statusIntervalId);
        }
        statusIntervalId = setTimeout(get_status, 5000);
    }
    else if (response.type == "complete") {
        $('#status').text("received [" + response.time + "]");
        console.log("complete [" + response.time + "]: " + JSON.stringify(response.data));
        draw_diagram_handler(response.data);
        draw_diagram_handler = reload_diagram;

        // js bug? ... etc.
        if (measurementIntervalId != null) {
            clearTimeout(measurementIntervalId);
        }
        measurementIntervalId = setTimeout(
            function() { launch_long_polling_measurement(null) }, 0);
    }
}

function launch_long_polling_measurement(params) {
    // cf. https://bl.ocks.org/Fil/4748d004e6d17a6f044856d6454f75f6
    if (params != null) {
        session_params = params;
    }

    d3.json(server_base_url + "measurement", {
            method: "POST",
            body: JSON.stringify(session_params),
            headers: { "Content-type": "application/json; charset=UTF-8" },

            // cookies aren't used by default, this enables them
            // use "include" for cross-origin requests
            credentials: "same-origin"
        })
        .then(handle_response);
}

function get_status() {
    d3.json(server_base_url + "status", {
            // cookies aren't used by default, this enables them
            // use "include" for cross-origin requests
            credentials: "same-origin"
        })
        .then(handle_response);
}
