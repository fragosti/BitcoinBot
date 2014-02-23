var jsonData = [
{
  "low": 1.2,
  "high":4,
  "last": 3.50,
  "avg" : 3.5,
  "date" : 22
 
},
{
  "low": 1.2,
  "high":4,
  "last": 3.80,
  "avg" : 3.5,
  "date" : 23
 
},
{
  "low": 1.2,
  "high":4,
  "last": 4.0,
  "avg" : 3.5,
  "date" : 24
 
},
{
  "low": 1.2,
  "high":4,
  "last": 4.9,
  "avg" : 3.5,
  "date" : 25
 
}

];

$('document').ready(function(){
  var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;
parseDate("1-1-1993")
console.log(parseDate("2011-01-01T12:14:35"))

var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
.domain([0, d3.max(jsonData, function(d) { return d["last"]; })])
    .range([height, 1]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");
                         

var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.last); });


var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    
    
  console.log(jsonData)
  x.domain(d3.extent(jsonData, function(d) { return d.date; }));
  y.domain(d3.extent(jsonData, function(d) { return d.last; }));

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Price ($)");

  svg.append("path")
      .datum(jsonData)
      .attr("class", "line")
      .attr("d", line);


});
