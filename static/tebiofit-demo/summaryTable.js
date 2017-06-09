function summaryTable() {

    var dataURL = "data/" + experiment + "/rates.txt";

    d3.text(dataURL, function (error, rawData) {
        if (error) throw error;

        var dsv = d3.dsv(" ", "text/plain");

        rawData = rawData.replace('[', '', 'g').replace(']', '', 'g').replace('  ', ' ', 'g');

        var parsedData = dsv.parseRows(rawData);

        var table = d3.select('#summaryTable').append("table");
        table.classed('table', true).classed('table-bordered', true); // apply bootstrap table themeing


        var tHead = table.append("thead");
        var tBody = table.append("tbody");

        var columns = [{"table_column": 1, "display_name": "Epsilon"},
            {"table_column": 2, "display_name": "Simulations" },
            {"table_column": 3, "display_name": "Acceptance Rate"},
            {"table_column": 4, "display_name": "Simulation Time/s" }];

        tHead.append("tr")
            .selectAll("th")
            .data(columns)
            .enter()
            .append("th")
            .text(function (column) {
                return column.display_name;
            });


        var rows = tBody.selectAll("tr")
            .data(parsedData)
            .enter()
            .append("tr");

        var cells = rows.selectAll("td")
            .data(function (row) {
                // callback must return data in format:
                // {name: "p5", type: "uniform", min: 0, max: 30}

                return columns.map(function (column) {
                    return {column: column.display_name, value: row[column.table_column]};
                });

            })
            .enter()
            .append("td")
            .html(function (d) {
                return d.value;
            });

    });

}