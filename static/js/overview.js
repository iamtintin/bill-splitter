$( function() {

    // Reset Search Field to empty
    $( "#search-box" ).val("");

    // On click of cancel search btn, return to default main overview page view 
    $( "#clear-btn" ).on("click", function(event) {
        $( "#search-box" ).val("");
        $( "#search-box" ).trigger("input");
    });

    // When key pressed in search field, handle event accordingly
    $( "#search-box" ).on("input", function(event) {
        // If search field not empty, show results
        if ($(this).val() != ""){
            $( ".grid" ).addClass("hidden");
            $( ".b-grid" ).removeClass("hidden");
            $( "#page-heading" ).text("Search Results"); 

            // Retrieve search term
            var sch_key = $(this).val();
            
            // AJAX POST request to find corresponding search results from server
            $.post(
                "/search",
                { search_key: sch_key },
                function(data, status) {
                    // Update displayed search results on page
                    updateSearchResults(data);
                }
            )
        // If search field is empty, return to default main overview page view
        } else {
            $( ".grid" ).removeClass("hidden");
            $( ".b-grid" ).addClass("hidden");
            $( "#page-heading" ).text("Overview");
        }
    });

    // AJAX Get request to retrieve notifications from server and display them
    $.get(
        "/getnotifs", 
        function(data, status){
            var notifs =  data.notifs;
            var node = $( '#notif-column' )
            // Update page with the returned notifications
            for (let i = notifs.length - 1; i >= 0; i--){
                node.append("<div class=\"compact-cell\"><p>" + notifs[i] + "</p></div>");
            }
            if (notifs.length == 0) {
                node.append("<div><p>No Notifications</p></div>");
            } else {
                // Update page with the number of notifications 
                node.parent().addClass("notif-alert");
                $( '#notif-column .flex-header' ).append("<div id=\"notif-flag\">" + notifs.length + "</div>")
                // AJAX request to update new bills as seen in the database
                $.get(
                    "/updateseenbills", 
                    function(data, status){}
                );
            }
        }
    );

});

// Function to update the displayed search results on the webpage
function updateSearchResults(response) {
    // Remove existing bill results
    var bill_node = $("#bill-results")
    $( "#bill-results .flex-cell" ).remove();
    $( "#bill-results #empty-results" ).remove();

    // If no results found, display appropriate message
    if (response.bills.length == 0) {
        bill_node.append("<p id=\"empty-results\"> No matching Bills found </p>")
    // If bills results exist use template to add results
    } else {
        for (let i = 0; i < response.bills.length; i++) {
            // Map status variables to strings for text and classes
            var status_attr = "";
            var status_str = "";
            if (response.bills[i].status && response.bills[i].confirmed) {
                status_attr = "bill-paid";
                status_str = "PAID";
            } else if (response.bills[i].status) {
                status_attr = "bill-pending";
                status_str = "PENDING";
            } else {
                status_attr = "bill-unpaid";
                status_str = "UNPAID";
            }

            // Template for matching bill result element in list
            const markup = `
            <div class="flex-cell">
                <a href="/focusedbill/${response.bills[i].id}" title="Open Bill"><span class="div-btn"></span></a>

                <div class="flex-row flex-wrap">
                    <div class="bill-attr">
                        <span class="bill-name">${response.bills[i].name}</span>
                        <span class="bill-label"> in <span class="bill-party"> ${response.bills[i].party} </span></span>
                    </div>
                    <div class="bill-attr"><span class="bill-label">Set: </span> ${response.bills[i].set} </div>
                    <div class="bill-attr">
                        <span class="bill-label"> ${response.bills[i].status ? "Paid" : "Due"}: </span> ${response.bills[i].status ? response.bills[i].paid_dt : response.bills[i].due}
                    </div>
                    <div class="bill-amount">£${response.bills[i].amount}</div>
                </div>

                <div class="flex-row flex-wrap">
                    <div class="bill-descr"> ${response.bills[i].description} </div>
                    <div class="bill-attr ${status_attr}">${status_str}</div>
                </div>
            </div>
            `;

            bill_node.append(markup)
        }
    }

    // Remove existing party results
    var party_node = $("#party-results")
    $( "#party-results .flex-cell" ).remove();
    $( "#party-results #empty-results" ).remove();

    // If no results found, display appropriate message
    if (response.parties.length == 0) {
        party_node.append("<p id=\"empty-results\"> No matching Parties found </p>")
    // If party results exist use template to add results
    } else {
        for (let i = 0; i < response.parties.length; i++) {
            // Template for matching party result element in list
            const markup = `
            <div class="flex-cell">
                <a href="/focusedparty/${response.parties[i].id}" title="Open Party"><span class="div-btn"></span></a>

                <div class="flex-row flex-wrap">
                    <div class="bill-attr">
                        <span class="bill-name">${response.parties[i].name}</span>
                    </div>
                </div>
            </div>
            `;
            party_node.append(markup);
        }
    }
}