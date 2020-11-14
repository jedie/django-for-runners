"use strict";

{% comment%}
    include from template:
        "django-for-runners/for_runners/templates/for_runners/chartjs.html"

    Chart-JS Reference:
        "http://www.chartjs.org/docs/latest/"
{% endcomment %}

var ctx = document.getElementById("chart").getContext('2d');

var labels = [{% for track in track_data %}"{{ track.0 }}-{{ track.1 }}km",{% endfor %}]


var dataset_track_count = {
    label: 'count',
//    type: 'bar', // FIXME: Should be a "bar"
    type: 'line',
    borderColor: "rgb(255, 99, 132, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    data: [{% for track in track_data %}{{ track.2 }},{% endfor %}],
    yAxisID: 'y-axis-1',
}
var dataset_fastes_pace = {
    label: 'fastes pace',
    type: 'line',
    fill: '+2',
    borderDash: [5, 15],
    spanGaps: true,
    borderColor: "rgb(255, 159, 64, 0.8)",
    backgroundColor: "rgba(255, 159, 64, 0.2)",
    data: [{% for track in track_data %}{{ track.3 }},{% endfor %}],
    yAxisID: 'y-axis-2',
}
var dataset_avg_pace = {
    label: 'avg. pace',
    type: 'line',
    fill: false,
    spanGaps: true,
    borderColor: "rgb(255, 159, 64, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    data: [{% for track in track_data %}{{ track.4 }},{% endfor %}],
    yAxisID: 'y-axis-2',
}
var dataset_slowest_pace = {
    label: 'slowest pace',
    type: 'line',
    fill: false,
    borderDash: [15, 5],
    spanGaps: true,
    borderColor: "rgb(255, 159, 64, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    data: [{% for track in track_data %}{{ track.5 }},{% endfor %}],
    yAxisID: 'y-axis-2',
}

var myChart = new Chart(ctx, {
    data: {
        labels: labels,
        datasets: [
            dataset_track_count,
            dataset_fastes_pace,
            dataset_avg_pace,
            dataset_slowest_pace,
        ],
    },
    options: {
        responsive: true,
        tooltips: {
            position: "average",
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'index',
            intersect: true,
        },
        title: {
            display: true,
            text: '{{ track_count }} Tracks, {{ min_length_km }}km - {{ max_length_km }}km, Avg.: {{ avg_length_km }}km'
        },
        scales: {
            xAxes: [{}],
            yAxes: [
            {
                id: 'y-axis-1',
                type: 'linear',
                labelString: "Count",
                position: 'left',
                display: true,
                ticks: {
                    suggestedMin: 0,
                }
            }, {
                id: 'y-axis-2',
                type: 'linear',
                labelString: "Pace",
                position: 'right',
                display: true,
                ticks: {
                    callback: function(value, index, values) {
                        return value + " Min/km";
                    }
                },
                // grid line settings
                gridLines: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
            }],
        },
    }
});