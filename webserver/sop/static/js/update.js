/**
 * Updates the progress in the details view
 */
document.addEventListener("DOMContentLoaded", function (event) {
    if (window.location.href.includes("details")) {
        var progress = document.getElementById("progress");
        var status = document.getElementById("status");
        var i = 0;
        setInterval(function () {
            response = fetch(window.location.href, {
                method: "GET", headers: {
                    "X-Requested-With": "XMLHttpRequest",
                }
            })
                .then(response => response.json())
                .then(data => {
                    var interval = setInterval(function () {
                        if (i < data["update_progress"]) {
                            i++;
                            progress.style.width = i + "%";
                            progress.innerHTML = i + "%";
                        } else {
                            clearInterval(interval);
                        }
                    }, 20);
                    status.innerHTML = "Status: " + data["update_status"];
                });
        }, 2000);
    }
});