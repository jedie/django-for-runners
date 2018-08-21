{% load i18n %}"use strict";

{% comment%}
    include from template:
        "django-for-runners/for_runners/templates/admin/for_runners/gpxmodel/dygraphs.html"

    dygraphs Homepage:
        "http://dygraphs.com"
{% endcomment %}

var time2coordinates={
    {% for timestamp, coordinates in time2coordinates.items %}{{ timestamp|stringformat:"i" }}:[{{ coordinates.0|stringformat:".5f" }},{{ coordinates.1|stringformat:".5f" }}],{% endfor %}
}

var leaflet_marker = L.marker([0,0]).addTo(map);

function graph2map(event, timestamp, pts, row) {
//    console.log("graph2map", timestamp);
    var coordinates=time2coordinates[timestamp];
//    console.log("coordinates", coordinates);

    var newLatLng = new L.LatLng(coordinates[0], coordinates[1]);
    leaflet_marker.setLatLng(newLatLng);
}

var g = new Dygraph(
    document.getElementById("dygraph_gpx_track"),
    [
        {% for column in columns %}[{{ column }}],{% endfor %}
    ],
    {
        // http://dygraphs.com/options.html
        // title: "{{ instance }} {{ instance.human_length }} {{ instance.human_duration }} {{ instance.human_pace }}",
        title: false,
        labels: [{% for label in labels %}"{{ label }}",{% endfor %}],
        legend: 'always',
        animatedZooms: true,

        // http://dygraphs.com/tests/callback.html
        highlightCallback: graph2map,
    }
);

var annotations=[
{% for point in km_points %}
    {
          series: "{{ elevation_label }}",
          x: {{ point.x }},
          shortText: "{{ point.distance_km }}",
          text: "{{ point.distance_km }}km ({{ point.distance_m|stringformat:".1f" }}m)",
    },
{% endfor %}
]

g.ready(function() {
    g.setAnnotations(annotations);
});
