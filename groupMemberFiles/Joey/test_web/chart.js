var width=500;
var height=125;
var margin = {'bottom':25, 'left':40, 'right':5}

var chartData = [0,0,0,0]
let actions = ['stay','hit','double','split']

var x = d3.scaleLinear()
    .domain([0, 100])
    .range([0, width-margin.left-margin.right])

var y = d3.scaleBand()
    .domain(actions)
    .range([0, Math.floor((height-margin.bottom)/4) * chartData.length])

const svg = d3.select('svg')

const xAxis = d3.axisBottom(x).ticks(11);

const yAxis = d3.axisLeft(y).ticks(4)

svg.attr("width", width)
    .attr("height", height)
    .attr("font-family", "sans-serif")
    .attr("font-size", "10")
    .attr("text-anchor", "end");

const bar = svg.selectAll("g")
    .data(chartData)
    .join("g")
    .attr("transform", (d, i) => `translate(${margin.left},${y(actions[i])})`);

bar.append("rect")
    .attr("fill", "steelblue")
    .attr("width", x)
    .attr("height", y.bandwidth() - 1);

bar.append("text")
    .attr("fill", "white")
    .attr('class','probText')
    .attr("x", d => x(d) - 3)
    .attr("y", y.bandwidth() / 2)
    .attr("dy", "0.35em")
    .text(d => d);

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", `translate(${margin.left},${height-margin.bottom})`)
    .call(xAxis)
    .style("text-anchor", "end");

svg.append("g")
    .attr("class", "x axis")
    .attr("transform", `translate(${margin.left},0)`)
    .call(yAxis)
    .style("text-anchor", "end");