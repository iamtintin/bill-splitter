$( function() {

    // On submit of Add Friend to Party button, create POST request
    $( '#addpartyuser' ).submit(function(event) {

        event.preventDefault();
        
        // Obtain Form values from document
        var uid = $( this ).find('#user').find(':selected').val();
        var pid = $( this ).find('input[name="partyid"]').val();
        var node = $( this );

        // AJAX POST request to add user and return response
        $.post(
            "/adduserparty",
            {
                user_id: uid,
                party_id: pid
            },
            function(data, status){
                displayError(data.error, !(data.error.length == 0));
                if (!data.error) {
                    updateUsers(data, uid, node);
                }
            }
        );
        
        return false;

    });
});

// Function to add User to list of Members in Party
function updateUsers(response, uid, node) {
    // Remove option from list and check if option dropdown is empty
    node.find('option[value=\'' + uid + '\']').remove();
    if (node.find('option').length == 0){
        node.parent().append(`<p class="p-user">No more friends to add to this Party.</p>`)
        node.remove();
    }
    // Add user to member list
    $( '#memberlist' ).append(`<p class="p-user"><span class="p-name">${titleFilter(response.name)}</span>(${response.username})</p>`);
}