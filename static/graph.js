const linecolors = ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850", "#ce1c8b", "#11463c"];
const currenturl = window.location.href;

//parse how many days to show from the url
let daysShown = 1;
if (currenturl.includes("days=")) {
    let i = currenturl.indexOf("days=");
    daysShown = parseInt(currenturl.charAt(i + 5));
}
//set dropdown html
let dropdownHTML = "";
//special case for 1 day not being plural
if (daysShown == 1) {
    dropdownHTML = "<option value=1>day</option>";
} else {
    dropdownHTML = "<option selected value=1>day</option>";
}
//do the rest of the days
for (let i = 2; i <= 10; i++) {
    dropdownHTML += "<option ";
    if (daysShown == i) {
        dropdownHTML += "selected ";
    }
    dropdownHTML += "value=" + i + ">" + i + " days</option>";
}

$(document).ready(function () {
    document.getElementById("chartdata").innerHTML = dropdownHTML;
    //draw the chart
    drawChart();

    async function drawChart() {
        const datapoints = await getData();
        //using the array, generate a list of datasets
        const plotdataset = new Array(datapoints.length - 1);
        for (let i = 0; i < plotdataset.length; i++) {
            plotdataset[i] = {
                label: datapoints[i + 1][0],
                data: datapoints[i + 1].slice(1),
                borderColor: linecolors[i],
                pointRadius: 1,
                pointHoverRadius: 1,
                fill: false
            };
        }

        //create the actual chart
        new Chart(document.getElementById("line-chart"), {
            type: 'line',
            data: {
                labels: datapoints[0].slice(1),
                datasets: plotdataset
            },
            options: {
                responsive: true,

                title: {
                    display: true,
                    text: 'Temperature Graph'
                },
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            displayFormats: {
                                hour: 'M-D, k:mm'
                            }
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Time'
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Temperature °C'
                        }
                    }]
                }
            }
        });
    }

    async function getData() {
        const url = "../temperaturelog.csv";
        const response = await fetch(url);
        const tabledata = await response.text();
        const table = tabledata.split('\n');
        table.pop();

        const firstline = table[0].split(',');
        var outputarray = new Array(firstline.length - 2);

        for (let i = 0; i < outputarray.length; i++) {
            outputarray[i] = new Array();
        }

        //search for latest dates
        let shownDates = new Set()
        for (let i = table.length - 1; i >= 0; i--) {
            shownDates.add(table[i].split(',')[0]);
            if (shownDates.size >= daysShown) {
                break;
            }
        }

        //turn data from columns into arrays
        lastdate = ""
        for (let i = 0; i < table.length; i++) {
            const thisline = table[i].split(',');
            if (shownDates.has(thisline[0]) || i == 0) {
                for (let j = 0; j < outputarray.length; j++) {
                    //special case for combining date and time
                    if (j == 0) {
                        outputarray[0].push(thisline[0] + " " + thisline[1]);
                        /*
                        if (lastdate === thisline[0]) {
                            outputarray[0].push(thisline[1]);
                        } else {
                            outputarray[0].push(thisline[0] + " " + thisline[1]);
                        }*/
                    } else {
                        if (thisline[j + 1].length > 0) {
                            outputarray[j].push(thisline[j + 1]);
                        } else {
                            outputarray[j].push(null);
                        }
                    }
                }
                lastdate = thisline[0];
            }
        }

        return outputarray;
    }
});
