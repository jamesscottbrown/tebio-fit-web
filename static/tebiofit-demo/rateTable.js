function fillRateTable() {
    var url = path + "rateTable.html";
    var http = new XMLHttpRequest();
    http.open('get', url);
    http.onreadystatechange = handleResponse;
    http.send(null);

    function handleResponse() {
        if (http.readyState == 4) {
            var response = http.responseText;
            document.getElementById('modelKinetics').innerHTML=response;
        }
    }
}