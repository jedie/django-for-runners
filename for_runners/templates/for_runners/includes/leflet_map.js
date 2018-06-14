{% comment%}
    include from template:
        "django-for-runners/for_runners/templates/for_runners/leaflet_map.html"

    Note:
        The route on OpenStreetMap does not look more detailed, with more than 5 decimal places ;)

    Leaflet-JS Reference:
        "https://leafletjs.com/reference-1.3.0.html#map"
{% endcomment %}

var map = L.map('map');

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
    maxZoom: 18,
}).addTo(map);

var marker = L.marker([{{ start_latitude|stringformat:".5f" }}, {{ start_longitude|stringformat:".5f" }}]).addTo(map);
marker.bindPopup("<strong>start at {{ short_start_address }}</strong><br>{{ start_time }}").openPopup();

marker = L.marker([{{ finish_latitude|stringformat:".5f" }}, {{ finish_longitude|stringformat:".5f" }}]).addTo(map);
marker.bindPopup("<strong>finish at {{ short_finish_address }}</strong><br>{{ finish_time }}").openPopup();

var path = L.polyline(
    [
        {% for latitude,longitude in coordinates %}[{{ latitude|stringformat:".5f" }},{{ longitude|stringformat:".5f" }}],{% endfor %}
    ],
    {color: 'red'}
).addTo(map);

map.fitBounds(path.getBounds());