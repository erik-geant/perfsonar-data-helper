
MARGIN = ({top: 20, right: 20, bottom: 30, left: 40});
NUM_BINS = 10;
COLOR = "steelblue";


var svg = d3.select("svg");

WIDTH = svg.attr("width") - MARGIN.left - MARGIN.right;
HEIGHT = svg.attr("height") - MARGIN.top - MARGIN.bottom;

svg.append("g")
    .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")")

var formatCount = d3.format(",.0f");
var formatTime = d3.format(",.1f");

var x;
var x_axis;

function barText(bar) {
/*
    return "["
        + formatTime(bar.x0)
        + ", "
        + formatTime(bar.x1)
        + "]";
*/
    return bar.length ? formatCount(bar.length) : "";
}


function get_x_axis_extent(values) {
    var x_domain = d3.extent(values);
    x_domain_length = x_domain[1] - x_domain[0];
    x_domain[0] -= x_domain_length/2.0;
    x_domain[1] += x_domain_length/2.0;
    return x_domain;
}

function get_color_scale(bins) {
    return d3.scaleLinear()
        .domain(d3.extent(bins, d => d.length))
        .range([d3.rgb(COLOR).brighter(), d3.rgb(COLOR).darker()]);
}

function size_bars(bins, x, transition) {
    var bars = svg.selectAll(".bar");
    // caller should have already created
    // rect & text subelements for these bars

    var colorScale = get_color_scale(bins);
    var y = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)]).nice()
        .range([HEIGHT - MARGIN.bottom, MARGIN.top]);

    if (transition) {
        bars.select("rect")
            .transition()
            .duration(1000)
            .attr("x", 1)
            .attr("width", d => Math.max(x(d.x1) - x(d.x0) - 1, 0))
            .attr("height", d => y(0) - y(d.length))
            .attr("fill", d => colorScale(d.length));
    } else {
        bars.select("rect")
            .attr("x", 1)
            .attr("width", d => Math.max(x(d.x1) - x(d.x0) - 1, 0))
            .attr("height", d => y(0) - y(d.length))
            .attr("fill", d => colorScale(d.length));
    }

    bars.select("text")
        .attr("dy", ".75em")
        .attr("y", -12)
        .attr("x", (x(bins[0].x1) - x(bins[0].x0)) / 2)
        .attr("text-anchor", "middle")
        .text(d => barText(d));

    if (transition) {
        bars.transition()
            .duration(1000)
            .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });
    } else {
        bars.attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });
    }
}

function diagram(values) {

    x = d3.scaleLinear()
        .domain(get_x_axis_extent(values)).nice()
        .range([MARGIN.left, WIDTH - MARGIN.right]);

    xAxis = d3.axisBottom(x);

    var bins = d3.histogram()
        .domain(x.domain())
        .thresholds(x.ticks(NUM_BINS))
      (values);

    var bar = svg.selectAll(".bar")
        .data(bins)
        .enter().append("g")
            .attr("class", "bar");

    bar.append("rect")
    bar.append("text")

    size_bars(bins, x, false);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${HEIGHT- MARGIN.bottom})`)
        .call(xAxis);

/*
    yAxis = g => g
        .attr("transform", `translate(${MARGIN.left},0)`)
        .call(d3.axisLeft(y))
        .call(g => g.select(".domain").remove())
        .call(g => g.select(".tick:last-of-type text").clone()
            .attr("x", 4)
            .attr("text-anchor", "start")
            .attr("font-weight", "bold")
            .text(values.y));

    svg.append("g")
        .call(yAxis);
*/
}

function refresh(values) {

    x.domain(get_x_axis_extent(values)).nice();

    var bins = d3.histogram()
        .domain(x.domain())
        .thresholds(x.ticks(NUM_BINS))
      (values);

    var bar = svg.selectAll(".bar").data(bins);
    bar.exit().remove(); // remove unneeded bars

    bar.enter().append("g")
        .attr("class", "bar");

    bar.enter().append("rect")
    bar.append("text")

    size_bars(bins, x, true);

    svg.select(".x")
        .transition()
        .call(xAxis);
}

function reload_diagram(d) {
    const dd = d.map(x => x*1000.0);
    refresh(dd);
}

function draw_diagram(d) {
    const dd = d.map(x => x*1000.0);
    dd.y = "packets";
    dd.x = "latency (ms)";
    diagram(dd);
}
