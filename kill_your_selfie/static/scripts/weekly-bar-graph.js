
function createSimpleBarGraph(canvas, name, data) {
// Creates a bar graph on the canvas expecting data in the form of 
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
        backgroundColor: '#FF0000',
        borderWidth: 5,
        borderRadius: 10,
        borderSkipped: false
      }
    ]
  };
  const config = {
    type: 'bar',
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

lastWeekData=document.getElementById("bargraph-weekly").getAttribute("data-chart")
lastWeekData=JSON.parse(lastWeekData);

createSimpleBarGraph(document.getElementById('bargraph-weekly'), 'Occurences In The Last 7 Days', lastWeekData);
