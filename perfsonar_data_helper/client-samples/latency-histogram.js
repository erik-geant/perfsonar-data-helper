

MARGIN = ({top: 20, right: 20, bottom: 30, left: 40});
HEIGHT = 500;
WIDTH = 1000;
//num_bins = 40;
NUM_BINS = 10;
COLOR = "steelblue";



var formatCount = d3.format(",.0f");
var formatTime = d3.format(",.1f");

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

var svg = d3.select("body").append("svg")
    .attr("width", WIDTH + MARGIN.left + MARGIN.right)
    .attr("height", HEIGHT + MARGIN.top + MARGIN.bottom)
  .append("g")
    .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")")

var x;

function diagram(values) {

    var x_domain = d3.extent(values);
    x_domain_length = x_domain[1] - x_domain[0];
    x_domain[0] -= x_domain_length/2.0;
    x_domain[1] += x_domain_length/2.0;

    x = d3.scaleLinear()
        .domain(x_domain).nice()
//        .domain(d3.extent(values)).nice()
        .range([MARGIN.left, WIDTH - MARGIN.right]);

    var bins = d3.histogram()
        .domain(x.domain())
        .thresholds(x.ticks(NUM_BINS))
      (values);

    var colorScale = d3.scaleLinear()
        .domain(d3.extent(bins, d => d.length))
        .range([d3.rgb(COLOR).brighter(), d3.rgb(COLOR).darker()]);

    var y = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)]).nice()
        .range([HEIGHT - MARGIN.bottom, MARGIN.top]);

    var bar = svg.selectAll(".bar")
        .data(bins)
        .enter().append("g")
    .attr("class", "bar")
    .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", d => Math.max(x(d.x1) - x(d.x0) - 1, 0))
        .attr("height", d => y(0) - y(d.length))
        .attr("fill", d => colorScale(d.length));

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", -12)
        .attr("x", (x(bins[0].x1) - x(bins[0].x0)) / 2)
        .attr("text-anchor", "middle")
        .text(d => barText(d));

    svg
    .selectAll("rect")
    .data(bins)
    .enter().append("rect")
      .attr("x", d => x(d.x0) + 1)
      .attr("width", d => x(d.x1) - x(d.x0) - 1)
      .attr("y", d => y(d.length))
      .attr("height", d => y(0) - y(d.length))

    xAxis = g => g
        .attr("transform", `translate(0,${HEIGHT- MARGIN.bottom})`)
        .call(d3.axisBottom(x).tickSizeOuter(0));
//         .call(g => g.append("text")
//             .attr("x", WIDTH - MARGIN.right)
//             .attr("y", 30)
//             .attr("fill", "#000")
//             .attr("font-weight", "bold")
//             .attr("text-anchor", "end")
//             .text(values.x));

    svg.append("g")
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
    return svg.node();
}

function refresh(values) {

/*
    var x = d3.scaleLinear()
        .domain(d3.extent(values)).nice()
        .range([MARGIN.left, WIDTH - MARGIN.right]);
*/

    var bins = d3.histogram()
        .domain(x.domain())
        .thresholds(x.ticks(NUM_BINS))
      (values);

    var colorScale = d3.scaleLinear()
        .domain(d3.extent(bins, d => d.length))
        .range([d3.rgb(COLOR).brighter(), d3.rgb(COLOR).darker()]);

    var y = d3.scaleLinear()
        .domain([0, d3.max(bins, d => d.length)]).nice()
        .range([HEIGHT - MARGIN.bottom, MARGIN.top]);

    var bar = svg.selectAll(".bar").data(bins);

    // remove object with data
    bar.exit().remove();

    bar.transition()
        .duration(1000)
        .attr("transform", function(d) { return "translate(" + x(d.x0) + "," + y(d.length) + ")"; });

    bar.select("rect")
        .transition()
        .duration(1000)
        .attr("height", d => y(0) - y(d.length))
        .attr("fill", d => colorScale(d.length));

    bar.select("text")
        .transition()
        .duration(1000)
        .text(d => barText(d));
}

server_base_url = "http://" + document.domain + ":" + location.port + "/pscheduler/";

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