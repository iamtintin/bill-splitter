$( function() {

    // On submission of friend request, validate username and send data to server
    $( '#friendform' ).submit(function(event) {

        event.preventDefault();

        // Retrieve username from input form and validate
        var msg = "";
        var uname = $( '#friendform' ).find('input[name="username"]').val();
        if (!validUsername(uname)) msg += "Invalid Name entered. Username can only comprise of alphanumeric characters and some special characters , . ' \" @ # - : <br>Whitespaces are not accepted. <br>";

        // Display Error message if invalid username
        var error = msg.length != 0;
        if (error) displayError(msg, error);

        if (!error) {
            // AJAX POST request to create friend request object / add friend if incoming friend request exists
            $.post(
                "/friendrequest", 
                { username: uname }, 
                function(data, status){
                    // Display error if one occurred
                    if (data["error"]) {
                        displayError(data["error"], true);
                    } else {
                        displayError(data["error"], false);
                        // Update list of friends if friend was added
                        if (data["added"]) {
                            updateFriends(data);    
                        // Otherwise update list of outgoing requests
                        } else {
                            updateOutRequests(data);
                        }
                        // Reset input field to empty
                        $( '#friendform' ).find('input[name="username"]').val("");
                    }
                }
            );
        }

        return false;
    });

    // Handling response to incoming friend requests
    $( '.friendreqform' ).on("click", ":submit", function(event) {

        event.preventDefault();
        
        // Retrieve id of friend request and user action from input form
        var requestid = $( this ).parent().find('input[name="id"]').val();
        var result  = $( this ).val();

        // AJAX POST request to server in order to carry out corresponding action 
        $.post(
            "/friendreqresponse",
            { 
                id: requestid,
                action: result,
            },
            function(data, status){
                // Display error if one occurred
                if (data["error"]) {
                    displayError(data["error"], true);
                } else {
                    displayError(data["error"], false);
                    // If request accepted, add friend to list of friends
                    if (data["added"]) {
                        updateFriends(data);
                    // If request rejected, remove request from list of incoming requests
                    } else {
                        removeInRequests(data["id"]);
                    }
                }
            }
        );

        return false;
    });

    // When the remove friend button is clicked, send data to server to update database
    $( '#friendlist' ).on("click", ":submit", function(event) {

        event.preventDefault();

        // Retrieve friend id from input form
        var userid = $( this ).parent().find('input[name="id"]').val()
        var node = $( this ).parent();

        // AJAX POST request to delete friend and return corresponding response
        $.post(
            "/deletefriend", 
            { id: userid },
            function(data, status) {
                // Display error if one occurred
                if (data["error"]) {
                    displayError(data["error"], true);
                // Remove friend from list of friends on page
                } else {
                    displayError(data["error"], false);
                    removeFriend(node);
                }
            }
        );

        return false;
    });
});

// Function to add to list of friends in page
function updateFriends(response) {
    // Convert list of common parties to string
    var partyList = "";
    response.common.map(party => partyList += party + ", ");

    partyList = (response.common.length == 0) ? "No common parties" : partyList.slice(0, -2);

    // Generate HTML for friend flex panel using template
    const markup = `
    <div class="innerblock flex-block">
        <div class="flex-row">
            <p class="title"> ${titleFilter(response.name)}</p>
            <form class="friendremoveform" method="POST">
                <input type="hidden" name="id" value="${response.uid}">
                <input type="submit" class="btn remove-btn" value="Remove">
            </form>
        </div>
        <p><span class="bill-label">Username:</span> ${response.username}</p>
        <p><span class="bill-label">Common parties:</span> ${partyList}</p>
    </div>
    `;

    // Add new friend panel to list of friends 
    var panel = $( '#friendlist' );
    if (panel.find(".innerblock").length == 0) {
        panel.empty();
    }
    panel.append(markup);

    // Remove incoming friend request 
    removeInRequests(response["id"]);
}


// Function to remove incoming friend request from list of incoming friend request
function removeInRequests(id){
    $( '#inreq' + id ).remove();
    // If no incoming requests remain, add placeholder string
    if ($( '#infriendrequest' ).children().length == 0) {
        $( '#infriendrequest' ).append(`<p id="no-in-req">No friend requests</p>`);
    }
}


// Function to add outgoing friend request to list
function updateOutRequests(response) {
    // Remove placeholder string, if it exists
    if ($( '#outfriendrequests' ).find( '#no-out-req' ).length) {
        $( '#no-out-req' ).remove()
    }
    // Add outgoing friend request element to list using template
    const html = `<p>Name: ${response.name}<br>Username: ${response.username}</p>`;
    $( '#outfriendrequests' ).append(html);
}


// Function to delete friend panel from list
function removeFriend(node) {
    var parentpanel = node.parent().parent().parent();
    node.parent().parent().remove();
    // If list of friends is empty, add placeholder string
    if ($( '#friendlist' ).find(".innerblock").length == 0) {
        parentpanel.append(`<p>No friends</p>`);
    }
}