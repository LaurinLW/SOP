/**
 * After pressing upload this class shows a circle on the screen
 */
document.addEventListener("DOMContentLoaded", function (event) {
    var uploadButton = document.getElementsByName("upload_btn");
    var loader = document.getElementsByClassName("loader")[0];
    var div = document.getElementById("upload_algo_dataset_div");
    var i;
    for (i = 0; i < uploadButton.length; i++) {
        uploadButton[i].addEventListener("click", function () {
            loader.style.display = "block";
            div.style.display = "none";
        });
    }
});