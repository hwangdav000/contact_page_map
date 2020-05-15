//  code gotten form ex2
var map;
var myLatLng;
var markersList
var directionsService
var directionsRenderer
function initMap() {
  markersList = [];
  myLatLng = {lat: 44.977276, lng:-93.232266};
  map = new google.maps.Map(document.getElementById('map'), {
    center: myLatLng,
    zoom: 14
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();

  directionsRenderer.setMap(map);
  directionsRenderer.setPanel(document.getElementById('right-panel'));

var address = [];
var name = [];
var coord = [];
var address2 = [];
var t_r = 1;
var t_c = 0;

//  get name and addresses
var table = document.getElementById('mytable');
for (var r = 1, m = table.rows.length; r < m; r++) {
  for (var c = 0, n = 3; c < n; c++) {
    //  skip column
    if (c == 1) {
      continue;
    }
    //  get vars in scope
    t_r = r;
    t_c = c;

    var remove_br = table.rows[r].cells[c].innerHTML;
    //  remove breaks in string
    remove_br = remove_br.replace(/\<br\>/g, " ");
    //  remove img alt in name
    remove_br = remove_br.replace(/<img alt="[^"]+" src="[^"]+">/, " ");

    if (c == 2) {
      //  store room number
      var sub_br = table.rows[t_r].cells[t_c].innerHTML;

      //  remove breaks in string
      sub_br = sub_br.replace(/\<br\>/g, "|");
      //alert(sub_br);
      var match1 = sub_br.match(/\|(.*?)\|/);
      address2.push(match1[1]);
      //alert(match1[1]);

    }

    if (c == 0) {
      name.push(remove_br);
    } else {
      address.push(remove_br);
    }
  }
}

var geocoder = new google.maps.Geocoder();
var i = 0;
for (var c = 0, n = address.length; c < n; c++) {
geocoder.geocode( { 'address': address[c] }, function(r, s) {
  var marker = new google.maps.Marker({
  position: r[0].geometry.location,
  map: map,
  title: 'marker',
  icon: {
    url:'Goldy.png',
    scaledSize: new google.maps.Size(40,40)
  }
  });

  //  push marker to list
  markersList.push(marker);

  //  create infowindow
  var contentString = '<div id="content">' +
          '<div id="bodyContent">' +
          name[i] +
          '<p> address: ' + address2[i] +'<p>' +
          '</div>' +
          '</div>';
  var infowindow = new google.maps.InfoWindow({
    content: contentString
  });
	marker.addListener('click', function() { infowindow.open(map,marker); });
  i++;
  });
}
var form = document.getElementById("myForm");
form.addEventListener('submit', handleForm);

var form2 = document.getElementById("myForm2");
form2.addEventListener('submit', handleForm);
}
// Stop form from refreshing page
// will call init again
function handleForm(event) { event.preventDefault(); }


//  right side of map
function turnOn(drop) {

  var item = document.getElementById("other");
  if(drop.value == "other") {
    item.disabled = false;
  } else {
    item.disabled = true;
  }
}

//  delete all markersList
function deleteMarkers() {
  for (var r = 0 ; r < markersList.length; r++) {
    markersList[r].setMap(null);
  }
  markersList= [];
}

function find_service(){
  var myLocation = new google.maps.LatLng(44.977276, -93.232266);
  deleteMarkers();

  //  get variables from dom
  var other;
  var other_t = 0;
  var loc = document.getElementById("mySelect").value;
  var range = document.getElementById("range").value;

  // check if drop down is marker value
  if (loc == "other") {
    other = document.getElementById("other").value;
    other_t = 1;
  }

  if (other_t == 1) {
    //if other_t is true then want other, range
    var service = new google.maps.places.PlacesService(map);
                service.nearbySearch({
                    location : myLocation,
                    radius : range.toString(),
                    type :  other
                }, callback);
  } else {

    //else false want loc and ranged
    var service = new google.maps.places.PlacesService(map);
                service.nearbySearch({
                    location : myLocation,
                    radius : range.toString(),
                    type :  loc
                }, callback);
  }
}
// functions referenced from google examples
function callback(results, status) {

            if (status === google.maps.places.PlacesServiceStatus.OK) {
                for (var i = 0; i < results.length; i++) {
                    createMarker(results[i]);

                }
            }
}

function createMarker(place) {

            var placeLoc = place.geometry.location;
            var marker = new google.maps.Marker({
                map : map,
                position : place.geometry.location
            });

            var infowindow = new google.maps.InfoWindow({
              content: contentString
            });
            //  create infowindow
            var contentString = '<div id="content">' +
                    '<div id="bodyContent">' +
                    place.name +
                    '</div>' +
                    '</div>';
            var infowindow = new google.maps.InfoWindow({
              content: contentString
            });
            marker.addListener('click', function() { infowindow.open(map,marker); });
                    //  push marker onto list to remove later
            markersList.push(marker);
}
////////////// second part

var start;
var destination;
function GetDirections(){
    // displays route on map
    // displays directions as well
    deleteMarkers();
    calculateAndDisplayRoute(directionsService, directionsRenderer);
}

function handleLocationError(browserHasGeolocation, infoWindow, start) {
        infoWindow.setPosition(start);
        infoWindow.setContent(browserHasGeolocation ?
          'Error: The Geolocation service failed.' :
          'Error: Your browser doesn\'t support geolocation.');
        infoWindow.open(map);
}
var city;
var state;
var s_start;
function calculateAndDisplayRoute(directionsService, directionsRenderer) {
  //  initialize variables

  var by = document.querySelector('input[name="by"]:checked').value;
  destination = document.getElementById("destination").value;
  //  get start by geolocation
  var infoWindow = new google.maps.InfoWindow;

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      //  need to get in terms of city, state
    start = {
      lat: position.coords.latitude,
      lng: position.coords.longitude
    };
    s_start = position.coords.latitude + ',' +position.coords.longitude
    //alert("codelatlng");
    //codeLatLng(position.coords.latitude, position.coords.longitude);
    }, function() {
      handleLocationError(true, infoWindow, map.getCenter());
    });

    } else {
      // Browser doesn't support Geolocation
      handleLocationError(false, infoWindow, map.getCenter());
    }


    directionsService.route({
          origin: s_start,
          destination: destination,
          travelMode: by
        }, function(response, status) {
          if (status === 'OK') {
            //alert("ok");
            directionsRenderer.setDirections(response);
          } else {
            window.alert('Directions request failed due to ' + status);
          }
    });
}
