"use strict";

{% comment%}
    include from template:
        "django-for-runners/for_runners/templates/for_runners/chartjs.html"

    Chart-JS Reference:
        "http://www.chartjs.org/docs/latest/"
{% endcomment %}

var ctx = document.getElementById("chart").getContext('2d');

var labels = [{% for label in labels %}"{{ label }}",{% endfor %}]



var dataset_elevations = {
    label: 'elevations (meters)',
    pointRadius: 0,
    borderColor: "rgb(255, 99, 132, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    fill: true,
    data: [{% for elevation in elevations %}{{ elevation|stringformat:".1f" }},{% endfor %}],
    yAxisID: 'y-axis-1',
}

var dataset_heart_rates = {
    label: 'heart rates (bpm)',
    pointRadius: 0,
    borderColor: "rgb(255, 159, 64, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    fill: true,
    data: [{% for hr in heart_rates %}{{ hr }},{% endfor %}],
    yAxisID: 'y-axis-2',
}

var dataset_cadence_values = {
    label: 'cadence values (spm)',
    pointRadius: 0,
    borderColor: "rgb(255, 205, 86, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    fill: false,
    data: [{% for cad in cadence_values %}{{ cad }},{% endfor %}],
    yAxisID: 'y-axis-3'
}

var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [
            dataset_elevations,
            dataset_heart_rates,
            dataset_cadence_values
        ],
    },
    options: {
        responsive: true,

        tooltips: {
            position: "average",
            mode: 'index',
            intersect: false,
        },

//        tooltips: {
//            mode: 'index',
//            intersect: true,
//        },
        hover: {
            mode: 'index',
            intersect: true,
        },
        stacked: false,
        title: {
            display: true,
            text: '{{ instance }} {{ instance.human_length }} {{ instance.human_duration }} {{ instance.human_pace }}'
        },
        scales: {
            yAxes: [
            {
                type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                display: true,
                position: 'left',
                id: 'y-axis-1',
            }, {
                type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                display: true,
                position: 'right',
                id: 'y-axis-2',

                // grid line settings
                gridLines: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
            }, {
                type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                display: false,
                position: 'right',
                id: 'y-axis-3',

                // grid line settings
                gridLines: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
            }
            ],
        },
//        elements: {
//            line: {
//                tension: 0, // disables bezier curves
//            }
//        },
        animation: {
            duration: 0, // general animation time
        },
    }
});