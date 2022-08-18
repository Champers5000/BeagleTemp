$(document).ready(function () {
  socket = io();
  socket.connect();

  socket.on('connect', function () {
    console.log("Connected");
  });

  socket.on('message', function (msg) {
    console.log(msg);
  });

  var tableheader = null;
  socket.on('headerchange', function (data) {
    data = data.substring(1, data.length - 1);
    tableheader = data.split(',');
    for (i = 0; i < tableheader.length; i++) {
      if (tableheader[i].charAt(0) === ' ') {
        tableheader[i] = tableheader[i].substring(1);
      }
      tableheader[i] = tableheader[i].substring(1, tableheader[i].length - 1);
    }
    //console.log(tableheader);
  });

  socket.on('tempreadings', function (data) {
    //console.log(data);
    const temparray = data.split(',');
    var tablehtml = '<tr><td id="row">Sensor</td><td id="row">Temp</td></tr>';

    if (tableheader.length == temparray.length - 1) {
      for (i = 0; i < tableheader.length; i++) {
        tablehtml += '<tr><td>' + tableheader[i] + '</td>' + '<td>' + temparray[i] + '</td></tr>';
      }
      document.getElementById("temp").innerHTML = tablehtml;
    }
  });

  socket.on('logstate', function (data) {
    console.log(data);
    if (data = "True") {
      document.getElementById('togglebutton').innerText = "Stop Logging";
    } else {
      document.getElementById('togglebutton').innerText = "Start Logging";
    }
  });

  $('#togglebutton').on('click', function () {
    socket.emit('toggle');
  });
});