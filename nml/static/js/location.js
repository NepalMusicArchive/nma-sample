function sendCoordinates(latitude, longitude) {
    fetch('/location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        })
    })
        .then(response => response.text())
        .then(data => {
            console.log(data); // Location saved
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function success(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Save the coordinates by sending them to Flask
    sendCoordinates(latitude, longitude);
    //document.getElementById('coordinates').innerHTML = "<a href=https://maps.google.com?q="+ latitude + "," + longitude +"> " + latitude + "," + longitude + "</a>";

}

function error(error) {
    console.error('Error:', error.message);
}

// Trigger getLocation() when the document is ready
document.addEventListener("DOMContentLoaded", function (event) {
    getLocation();
});

