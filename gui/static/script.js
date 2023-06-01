function setup() {
    // search on hit enter while typing search query
    $("#searchBar").on("keyup", ev => {
        if (ev.key === "Enter") {
            ev.preventDefault();
            $("#searchButton").click();
        }
    })
}

// add click event for search button and insert results
async function search() {
    const response = await fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent($("#searchBar").val())}`);
    response.json().then(data => {
        results = data["results"];
        $("#results").empty();
        $.each(results, (_, url) => {
            let p = $("<p/>");
            let a = $("<a>", {
                text: url,
                href: url
            });
            p.append(a);
            $("#results").append(p);
            let info = $("<p/>");
            info.append($("<span/>").text(`Query Time: ${data["time"]} ms`));
            info.append($("<br/>"));
            info.append($("<span/>").text(`Total Results: ${data["count"]}`));
            $("#info").empty();
            $("#info").append(info);
        });
    });
}

// run setup after dom is loaded
$(document).ready(() => {
    setup();
});