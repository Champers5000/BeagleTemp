$( document ).ready(function() {
  socket = io();
  socket.connect();

  socket.on('connect', function(){
    console.log("Connected");
  })

  socket.on('message', function(msg){
    console.log(msg);
  })

  var tableheader = null;
  socket.on('headerchange', function(data){
    data = data.substring(1, data.length-1)
    tableheader = data.split(',');
    for(i=0; i<tableheader.length; i++){
      if(tableheader[i].charAt(0) === ' '){
        tableheader[i] = tableheader[i].substring(1)
      }
      tableheader[i] = tableheader[i].substring(1,tableheader[i].length-1);
    }
    console.log(tableheader);
  })

  socket.on('tempreadings', function(data){
    console.log(data)
    const temparray = data.split(',');
    var tablehtml = '<tr><td id="row">Sensor</td><td id="row">Temp</td></tr>';

    if(tableheader.length == temparray.length-1){
      for(i=0; i<tableheader.length; i++){
        tablehtml += '<tr><td>'+tableheader[i]+'</td>'+'<td>'+ temparray[i]+'</td></tr>';
      }
      document.getElementById("temp").innerHTML = tablehtml
    }
  })

});



/*
const config = {
  type: "line",
  data: {
    labels: [],
    datasets: [{
      data: [], // Set initially to empty data
      label: "Temperature",
      borderColor: "#3e95cd",
      fill: false
    }]
  },
  options: {
    scales: {
      xAxes: [{
        type: "time",
        distribution: "linear"
      }],
      title: {
        display: false
      }
    }
  }
};

const ctx = document.querySelector("#line-chart").getContext("2d");
const temperatureChart = new Chart(ctx, config);

const csvToChartData = csv => {
  const lines = csv.trim().split("\n");
  lines.shift(); // remove titles (first line)
  return lines.map(line => {
    const [date, temperature] = line.split(",");
    return {
      x: date,
      y: temperature
    };
  });
};

const fetchCSV = () => fetch("temperature.csv")
  .then(data => data.text())
  .then(csv => {
    temperatureChart.data.datasets[0].data = csvToChartData(csv);
    temperatureChart.update();
    setTimeout(fetchCSV, 5000); // Repeat every 5 sec
  });

fetchCSV(); // First fetch!
*/
