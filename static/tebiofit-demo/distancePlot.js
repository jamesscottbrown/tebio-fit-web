function plotErrors(paddedWidth){

    var numGenerations = global_data.epsilon_schedule.length;
    var numModels = global_data.models.length;
    var numParticles = global_data.particles;


    // Build graphic
    console.log("in plotErrors, width is " + width)
    var height = 500,
        padding = 75,
        //paddedWidth = width + padding
        width  = paddedWidth - padding;

    // x-axis ranges from 1 to numParticles
    var x = d3.scale.linear()
        .range([padding / 2, width - padding / 2])
        .domain([0, numParticles ]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(6);


    // y axis ranges from 0 to max epsilon
    var y = d3.scale.linear()
        .range([height - padding / 2, padding / 2])
        .domain([0, global_data.epsilon_schedule[0]]);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(6);

    // same color scale as in bar chart. TODO: share the scale object
    var color = d3.scale.category10();

    // create SVG
    d3.select("#errors").select('svg').remove();
    var svg = d3.select("#errors").append('svg')
        .attr("width", paddedWidth)
        .attr("height", height + padding)
        .append("g")
        .attr("transform", "translate(" + padding + "," + padding / 2 + ")");


    // add y-axis and label
    svg.append("g")
        .attr("class", "y distanceplot-axis")
        .attr("transform", "translate(" + padding / 2 + ",0)").call(yAxis);

    svg.append("text")
        .attr("transform", "rotate(-90,0,0) translate(-" + (height + padding) / 2 + ", 0)") // TODO: fiddle with this
        .text("Distance")
        .classed("axis-title", true);;


    // add x-axis and label
    svg.append("g")
        .attr("class", "x distanceplot-axis")
        .attr("transform", "translate(0," + (height - padding / 2) + ")").call(xAxis);

    svg.append("text")
        .attr("transform", "translate(" + (width/2) + "," + (height)  +  ")") // TODO: fiddle with this
        .text("Particle Rank")
        .classed("axis-title", true);





    for (var generation = 1; generation <= numGenerations; generation++){
        processLine(generation);

        // plot reference line
        var reflineY = y(global_data.epsilon_schedule[generation-1]);
        svg.append("line")
            .attr("x1", x(0))
            .attr("y1", reflineY)
            .attr("x2", x(numParticles))
            .attr("y2", reflineY)
            .attr("stroke", "steelblue")
            .attr("stroke-width", "1px")
            .attr("stroke-dasharray", "5,5")

    }

    function processLine(generation){

        var dataURL = path + "distance_Population" + generation.toString() + ".txt";

        d3.text(dataURL, function (error, rawData) {
            if (error) throw error;

            var dsv = d3.dsv(" ", "text/plain");
            var parsedData = dsv.parseRows(rawData);

            // filter to get particles for this model only
            for (var modelNum = 0; modelNum < numModels; modelNum++) {
                var thisModelData = parsedData.filter(function (d) {
                    return d[3] == modelNum;
                });


                // reformat data
                var filteredData = [];
                for (var i=0; i < thisModelData.length; i++){
                    var error = thisModelData[i][2];
                    error = error.replace('[', '').replace(']', '');

                    var tmp = [];
                    tmp.y = parseFloat(error);
                    tmp.modelNum = modelNum;
                    tmp.epsilon = global_data.epsilon_schedule[generation-1];

                    filteredData[i] = tmp;
                }

                filteredData.sort(function(a,b){ return a.y - b.y; });

                // plot
                plotLine(filteredData);
            }
        });

    }

    function plotLine(filteredData){

        var group = svg.append("g")
            .attr("class", "refline")
            .attr("stroke", color(filteredData[0].modelNum+1) )
            .attr("fill", color(filteredData[0].modelNum+1) );

        var points = group.selectAll("path")
            .data(filteredData)
            .enter()
            .append("path")
            .attr("d", d3.svg.symbol().type('circle') )
            .attr("transform", function(d, i){ console.log(color(d.modelNum)); return "translate (" + x(i) + ", " + y(d.y) + ")";}  )
            .classed("epsilon" + filteredData[0].epsilon, "true" )
            .classed("epsilon-points", "true" );

            points.on("mouseover",
                function(d){
                    svg.selectAll(".epsilon-points")
                        .classed("unselected", function(d2){ return d.epsilon != d2.epsilon; })
                    ;
                })
                .on("mouseout",
                function(d){
                    svg.selectAll(".epsilon-points").classed("unselected", false);
                });


        group.selectAll("path").append("title")
            .text(function (d) {
                return "epsilon =" + d.epsilon + ", error = " + d.y;
            });



        var line = d3.svg.line()
            // assign the X function to plot our line as we wish
            .x(function(d,i) {
                return x(i);
            })
            .y(function(d) {
                return y(d.y);
            });

        svg.append("svg:path").attr("d", line(filteredData))
            .attr("fill", "none")
            .attr("stroke", color(filteredData[0].modelNum+1))
            .attr("stroke-width", "1px")
            .attr("fill", "none")
            .classed("epsilon-line", "true" );

    }



}
