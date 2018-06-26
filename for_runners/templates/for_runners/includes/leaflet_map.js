{% comment%}
    include from template:
        "django-for-runners/for_runners/templates/for_runners/leaflet_map.html"

    Note:
        The route on OpenStreetMap does not look more detailed, with more than 5 decimal places ;)

    Leaflet-JS Reference:
        "https://leafletjs.com/reference-1.3.0.html#map"
{% endcomment %}

var map = L.map('map');

L.control.scale().addTo(map);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    minZoom: 5,
    maxZoom: 19,
}).addTo(map);

var icon_size=[15,15];
var icon_start = L.divIcon({className: "leaflet-marker-start", html: "S", iconSize: icon_size});
var icon_finish = L.divIcon({className: "leaflet-marker-finish", html: "F", iconSize: icon_size});

L.marker(
    [{{ start_latitude|stringformat:".5f" }}, {{ start_longitude|stringformat:".5f" }}], {icon: icon_start}
).addTo(map).bindPopup(
    "<strong>start at {{ short_start_address }}</strong><br>{{ start_time }}"
).openPopup();

L.marker(
    [{{ finish_latitude|stringformat:".5f" }}, {{ finish_longitude|stringformat:".5f" }}], {icon: icon_finish}
).addTo(map).bindPopup(
    "<strong>finish at {{ short_finish_address }}</strong><br>{{ finish_time }}"
).openPopup();



{% for gpx_point, distance_m, distance_km in km_gpx_points %}{# iterate over GPXTrackPoint instances #}
L.marker(
    [{{ gpx_point.latitude|stringformat:".5f" }}, {{ gpx_point.longitude|stringformat:".5f" }}],
    {title:"{{ distance_km }}km", icon: L.divIcon({className: "leaflet-marker-kilometers", html: "{{ distance_km }}", iconSize: icon_size})}
).addTo(map).bindPopup(
    "<strong>{{ distance_km }}km</strong> ({{ distance_m|stringformat:".1f" }}m)<br>{{ gpx_point.time }}"
);
{% endfor %}

var path = L.polyline(
    [
        {% for latitude,longitude in coordinates %}[{{ latitude|stringformat:".5f" }},{{ longitude|stringformat:".5f" }}],{% endfor %}
    ],
    {color: 'red'}
).addTo(map);

map.fitBounds(path.getBounds());