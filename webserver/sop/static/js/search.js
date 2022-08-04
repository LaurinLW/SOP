/**
 * Add a search feature
 */
document.addEventListener("DOMContentLoaded", function (event) {
    var searchable = document.getElementsByClassName("searchable");
    var search = document.getElementsByClassName("search");
    var j;
    let search_var = "";
    for (j = 0; j < search.length; j++) {
        search[j].addEventListener("input", function (e) {
            search_var = e.target.value.toLowerCase();
            var i;
            for (i = 0; i < searchable.length; i++) {
                if (searchable[i].tagName != "TR" && searchable[i].value.toLowerCase().includes(search_var)) {
                    searchable[i].style.display = "block";
                } else if (searchable[i].id.toLowerCase().includes(search_var)){
                    searchable[i].style.display = "table-row";
                } else {
                    searchable[i].style.display = "none";
                }
            }
        });
    }
});