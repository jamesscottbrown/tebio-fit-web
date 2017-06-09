
function summariseModelTable() {

    var sections = d3.select('#models')
        .selectAll("div")
        .append("ul")
        .data(global_data.models)
        .enter()
        .append("li");

        sections.append('a')
        .attr('href', function (d) {
            return window.location.href.split("?")[0].replace("comparison.html", "index.html") + "?experiment=" + getUrlVars()["experiment"] + "&model=" + d.model_name;
        })
        .text(function (d) {
            return d.model_name;
        })

    d3.select('#models').append("img")
        .attr('src', path + "compare.png");


    var numModels = global_data.models.length;
    if (numModels == 1){
        d3.select(".lead").text("This page is intended to compare models, but only one was provided:")
    } else {
        d3.select(".lead").text("This page compares " + numModels.toString() + " models:")

    }

    // plot graph
    var dataURL = path + "ModelDistribution.txt";
    d3.text(dataURL, function (error, rawData) {
        if (error) throw error;

        var dsv = d3.dsv(" ", "text/plain");
        parsedData = dsv.parseRows(rawData);


        var //width = 480,
            size = 230,
            padding = 20,
            xPadding = 50,
            bar_thickness = 20,
            full_height = (bar_thickness + padding) * parsedData.length,
            height = bar_thickness * parsedData.length;

        var x = d3.scale.linear()
            .range([0, width - xPadding])
            .domain([0, 1]);

        var y = d3.scale.linear()
            .range([0, height - bar_thickness])
            .domain([0, parsedData[0].length]);

        var color = d3.scale.category10()
            .domain([0, parsedData[0].length]);

        var svg = d3.select('#modelLikelihood').append('svg')
            .attr("width", width)
            .attr("height", full_height);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .ticks(10);


        // reformat data, so that each bar can work out its position as well as length

        var data = [];
        data.push([]);

        for (var i = 0; i < parsedData.length; i++) {
            data[i] = [];
            for (var j = 0; j < parsedData[i].length; j++) {
                if (parsedData[i][j] == "") {
                    continue;
                }
                tmp = [];
                tmp["val"] = Number(parsedData[i][j]);

                if (j == 0) {
                    tmp["cumSum"] = 0;
                } else {
                    tmp["cumSum"] = data[i][j - 1].cumSum + Number(parsedData[i][j - 1]);
                }

                tmp["row"] = i;
                tmp["model_name"] = global_data.models[j].model_name;
                tmp["epsilon"] = global_data.epsilon_schedule[i];
                data[i][j] = tmp;
            }
        }


        var row = svg.selectAll(".row")
            .data(data)

            .enter().append("g")
            .attr("class", "g")

            .attr('transform', function (d, i) {
                return "translate(0," + y(i) + ")";
            });


        var bars = row.selectAll("rect")
            .data(function (d, i) {
                return d;
            })
            .enter()
            .append('rect')
            .attr('x', function (d, i) {
                return x(d.cumSum);
            })
            .attr('width', function (d, i) {
                return x(d.val);
            })
            .attr('height', 20)
            .style('fill', function (d, i) {
                return color(i);
            });

        bars.append("svg:title")
            .text(function (d) {
                return d.model_name + ": " + d.val;
            });

        bars.on("click", function (d) {
                return window.location.href = window.location.href.split("?")[0].replace("comparison.html", "index.html") + "?experiment=" + getUrlVars()["experiment"] + "&model=" + d.model_name + "&epsilon=" + d.epsilon;
            }
        );

        row.selectAll("text")
            .data(function (d, i) {
                return d;
            })
            .enter()
            .append("text")
            .text(function (d, i) {
                return d.epsilon;
            })
            .attr("y", bar_thickness / 2)
            .attr("x", (width + 5 - xPadding));

        svg.append("g")
            .attr("transform", "rotate(90) translate (" +  (height / 2) + "," +  - (width + 30 - xPadding) + ")" )
            .append("text").text("Epsilon")
            .classed("axis-title", true);



        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + (height + 20) + ")")
            .call(xAxis);

        svg.append("g")
            .attr("transform", "translate (" +  (width / 2 - 60 ) + "," +  (height + 60) + ")" )
            .append("text").text("Model Probability")
            .classed("axis-title", true);


    })
}