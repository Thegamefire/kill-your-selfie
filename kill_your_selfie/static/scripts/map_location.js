// Initialize the map
const map = L.map('map').setView([51.05, 3.73], 10);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Marker variable (to add or move the marker dynamically)
let marker;

// Input elements for latitude and longitude
const latInput = document.getElementById('lat');
latInput.addEventListener("change", coordChange)
const lngInput = document.getElementById('lng');
lngInput.addEventListener("change", coordChange)

// Add click event to the map
map.on('click', function (e) {
    const { lat, lng } = e.latlng;

    // Update input fields with the clicked coordinates
    latInput.value = lat.toFixed(6);
    lngInput.value = lng.toFixed(6);

    // Add or move the marker to the clicked location
    if (marker) {
        marker.setLatLng(e.latlng); // Move existing marker
    } else {
        marker = L.marker([lat, lng]).addTo(map); // Add new marker
    }
});

function coordChange() {
    if (marker) {
        marker.setLatLng([latInput.value, lngInput.value]) // Move existing marker
    } else {
        marker = L.marker([lat, lng]).addTo(map); // Add new marker
    }
}