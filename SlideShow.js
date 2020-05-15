var icon;
var pictures = ["david.jpeg","girl.jpg", "harshit.jpg","ruofeng.jfif","yang.jfif","Goldy2.png", "dan.jpg"];
var descriptions = ["one", "two", "three", "four", "five", "six", "seven"];
var index = 0;
var intervalId;

function ShowImage() {
	icon.setAttribute("src",  pictures[index]);
	icon.setAttribute("alt", descriptions[index]);
	index = (index+1) % pictures.length;
}

function Start() {
	icon = document.getElementById("image");
  clearInterval(intervalId); // need this otherwise slideshow speeds up when clicking start multiple times
	intervalId = setInterval(ShowImage, 2000);
}
function Stop() {
  clearInterval(intervalId);
}
