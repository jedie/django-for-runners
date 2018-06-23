"use strict";

{% comment%}
    include from template:
        "django-for-runners/for_runners/templates/for_runners/chartjs.html"

    Chart-JS Reference:
        "http://www.chartjs.org/docs/latest/"
{% endcomment %}

var ctx = document.getElementById("chart").getContext('2d');

var labels = [{% for track in track_data %}"{{ track.0 }}-{{ track.1 }}km",{% endfor %}]


var dataset_elevations = {
    label: 'count',
    borderColor: "rgb(255, 99, 132, 0.8)",
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    borderWidth: 1,
    data: [{% for track in track_data %}{{ track.2 }},{% endfor %}],
}

var myChart = new Chart(ctx, {
    type: "bar",
    data: {
        labels: labels,
        datasets: [
            dataset_elevations,
        ],
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: '{{ track_count }} Tracks, {{ min_length_km }}km - {{ max_length_km }}km, Avg.: {{ avg_length_km }}km'
        },
    }
});