
function createSimpleLineGraph(canvas, name, data) {
    // Creates a line graph on the canvas expecting data in the form of
    // {(label, value), (label, value), (label, value)}

      let labels=[]
      let values=[]

      for (let i = 0; i < data.length; i++) {
        labels.push(data[i][0])
        values.push(data[i][1])
      }
      const chart_data = {
        labels: labels,
        datasets: [
          {
            label: name,
            data: values,
            borderColor: '#FEFEFE',        //TODO: figure out colors
            fill: false,
            cubicInterpolationMode:'monotone',
            tension: 0.4
          }
        ]
      };
      
      const config = {
        type: 'line',
        data: chart_data,
        options: {
          responsive: true,
          plugins: {
            legend: {
                position: 'none',
            },
            title: {
                display: false
            }
          }
        }
      };
      new Chart(canvas, config)
    }


    lastMonthData=JSON.parse(document.getElementById("linegraph-monthly").getAttribute("data-chart"));
    lastYearData=JSON.parse(document.getElementById("linegraph-yearly").getAttribute("data-chart"));

    createSimpleLineGraph(document.getElementById('linegraph-monthly'), 'Occurrences This Day', lastMonthData);
    createSimpleLineGraph(document.getElementById('linegraph-yearly'), 'Occurrences This Month', lastYearData);
