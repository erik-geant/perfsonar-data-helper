// cf. https://bl.ocks.org/mbostock/3884955
//     https://bl.ocks.org/mbostock/0533f44f2cfabecc5e3a


function diagram(values) {
    var svg = d3.select("svg");
    MARGIN = ({top: 20, right: 20, bottom: 30, left: 40});
    WIDTH = svg.attr("width") - MARGIN.left - MARGIN.right;
    HEIGHT = svg.attr("height") - MARGIN.top - MARGIN.bottom;

    var x = d3.scaleLinear().range([0, WIDTH - MARGIN.left - MARGIN.right]);
    var y = d3.scaleLinear().range([HEIGHT - MARGIN.top - MARGIN.bottom, 0]);

    g = svg.append("g")
        .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")")

    var line = d3.line()
    //    .curve(d3.curveBasis)
        .x(function(d) { return x(d.time); })
        .y(function(d) { return y(d.gb); });

    x.domain(d3.extent(values, d => d.time));

    y.domain([
        d3.min(values, d => d.gb),
        d3.max(values, d => d.gb)
    ]);


    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + HEIGHT + ")")
        .call(d3.axisBottom(x));

//g.append("g")
//  .attr("class", "axis axis--x")
//  .attr("transform", "translate(0," + HEIGHT + ")")
//  .call(d3.axisBottom(x));
//  .append("text")
//  .attr("x", 10)
//  .attr("dx", "0.71em")
//  .attr("fill", "#000")
//    .text("seconds");

    g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y))
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .attr("fill", "#000")
      .text("Gb");

    g.append("path")
        .datum(values)
        .attr("class", "line")
    //    .attr("d", line(values));
        .attr("d", line);
}



function draw_diagram(d) {
    const dd = d.map(x => ({
        time: x.end,
        gb: (x.bytes * 8.0)/(1024.0 * 1024.0 * (x.end - x.start))
    }));
    diagram(dd);
}

function reload_diagram(d) {
    draw_diagram(d);
}

data = '[{"bytes":675769528,"end":6.000079870223999,"start":0},{"bytes":677642240,"end":12.002346992492676,"start":6.000079870223999},{"bytes":665845760,"end":18.000200033187866,"start":12.002346992492676},{"bytes":693370880,"end":24.000130891799927,"start":18.000200033187866},{"bytes":627834880,"end":30.000110864639282,"start":24.000130891799927}]';
measurements = JSON.parse(data);

console.log(measurements);

draw_diagram(measurements);


