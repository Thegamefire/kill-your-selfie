
const labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
occ_last_week = fetch("/barweek")//.then((response) => response.json())
console.log(occ_last_week)
const data = {
  labels: labels,
  datasets: [
    {
      label: 'Small Radius',
      data: [0, 4, 50, 70, -80, 6],
      borderColor: '#FEFEFE',
      backgroundColor: '#FF0000',
      borderWidth: 5,
      borderRadius: 10,
      borderSkipped: false
    }
  ]
};

const config = {
    type: 'bar',
    data: data,
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

new Chart(document.getElementById('bargraph-weekly'), config);