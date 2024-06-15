function submitForm() {
    var address = document.getElementById('address').value;
    var county = document.getElementById('county').value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/calculate-route', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            alert("County: " + response.county + "\nAddress: " + response.address);
        } else if (xhr.readyState === 4) {
            alert("Error: " + xhr.status);
        }
    };
    var data = JSON.stringify({"address": address, "county": county});
    xhr.send(data);
}
