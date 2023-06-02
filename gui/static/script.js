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
    const response = await fetch(`http://127.0.0.1:5000/search/?query=${encodeURIComponent($("#searchBar").val())}`);
    response.json().then(data => {
        results = data["results"];
        $("#results").empty();
        $.each(results, (_, res) => {
            let p = $("<p/>").addClass("resultP");
            let title = res["title"];
            if (!title) title = res["url"];
            let a = $("<a>", {
                text: title,
                href: res["url"]
            });
            p.append(a);
            p.append($("<br/>"));
            p.append(res["summary"]);
            $("#results").append(p);
        });
        if (results.length === 0) {
            let p = $("<p/>").addClass("resultP");
            p.append($("<h3/>", {text: "Oops!"}));
            p.append("Sorry, we couldn't find any results for that query. ");
            p.append(`But if you're determined to find a result, then <a href="https://www.google.com/search?q=${encodeURIComponent($("#searchBar").val())}" target="_blank">this</a> might be helpful.`)
            $("#results").append(p);
        }
        let info = $("<p/>");
        info.append($("<span/>").text(`Query Time: ${data["time"]} ms`));
        info.append($("<br/>"));
        info.append($("<span/>").text(`Total Results: ${data["count"]}`));
        $("#info").empty();
        $("#info").append(info);
        $("h1").addClass("searched");
    });
}

// run setup after dom is loaded
$(document).ready(() => {
    setup();
});