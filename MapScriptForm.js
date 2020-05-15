var origin;
var map;
function initMap() {
  origin = {lat: 44.977276, lng: -93.232266};
  var mapOptions = {
    center: new google.maps.LatLng(44.977276, -93.232266),
    zoom: 14
  };
  map = new google.maps.Map(document.getElementById('map'), mapOptions);

  //  click on points in map and get back address
  var clickHandler = new ClickEventHandler(map, origin);

  var input = document.getElementById('autocomplete');
  var autocomplete = new google.maps.places.Autocomplete(input,{types: ['(cities)']});
  google.maps.event.addListener(autocomplete, 'place_changed', function(){
     var place = autocomplete.getPlace();
  })
};

//  trim leading and trailing spaces of favorite place and Name
function DoSubmit() {

  var name = document.getElementById('name').value.trim();
  var fav_place = document.getElementById('place').value.trim();
  document.getElementById('name').value = name;
  document.getElementById('place').value = fav_place;
  document.getElementById('myform').submit();
}

//  from google api
var ClickEventHandler = function(map, origin) {
        this.origin = origin;
        this.map = map;
        this.directionsService = new google.maps.DirectionsService;
        this.directionsRenderer = new google.maps.DirectionsRenderer;
        this.directionsRenderer.setMap(map);
        this.placesService = new google.maps.places.PlacesService(map);
        this.infowindow = new google.maps.InfoWindow;
        this.infowindowContent = document.getElementById('infowindow-content');
        this.infowindow.setContent(this.infowindowContent);

        // Listen for clicks on the map.
        this.map.addListener('click', this.handleClick.bind(this));
};

ClickEventHandler.prototype.handleClick = function(event) {
      var geocoder = new google.maps.Geocoder();
      if(event.placeId) {
        //  alert(event.placeId)
        //  use geocoder to reverse lat lng to address
        geocoder.geocode({
          'latLng': event.latLng
        }, function(results, status) {
          if (status == google.maps.GeocoderStatus.OK) {
            if (results[0]) {
              //alert(results[0].formatted_address);
              document.getElementById("autocomplete").value = results[0].formatted_address;
            }
          }
        });

      }
};
