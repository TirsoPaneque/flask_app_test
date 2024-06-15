function submitForm() {
    var address = document.getElementById('address').value;
    var county = document.getElementById('county').value;
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/calculate-route', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                
                // Display closest beaches and distances
                var beachesInfo = response.closest_beaches.map(function(beach, index) {
                    return `${index + 1}. ${beach} (${response.distance[index]} km)`;
                });
                alert("Closest Beaches:\n" + beachesInfo.join('\n'));
            } else {
                alert("Error: " + xhr.status);
            }
        }
    };
    
    var data = JSON.stringify({"address": address, "county": county});
    xhr.send(data);
}
