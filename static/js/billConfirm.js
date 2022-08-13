$( function() {

    // On submission of bill request response, send data to server to carry out function
    $( '.billreqform' ).on("click", ":submit", function(event) {

        event.preventDefault();

        // Retrieve input data from form
        var billid = $( this ).parent().find('input[name="id"]').val();
        var result  = $( this ).val();
        var node = $( this );

        // AJAX POST request to obtain action response from server
        $.post(
            "/billconfirm",
            { 
                id: billid,
                action: result,
            },
            function(data, status){
                // Display error is one occurred
                if (data["error"]) {
                    displayError(data["error"], true);
                } else {
                    displayError(data["error"], false);
                    updateUserBill(data, result, node);
                }
            }
        );

        return false;
    });
});

// Function to update party-bill page according to the action of user and response from server
function updateUserBill(response, action, node) {
    // If bill request accepted
    if (action == "Accept") {

        // Set Confirmed status
        node.parent().parent().find( '.confirm' ).html(`<span class="bill-label">Confirmed: </span><span class="bill-paid">CONFIRMED</span>`);

        // Update Party bill total paid amount
        $( '#allamount' ).html(`<span class="bill-label">Paid: </span> £${parseFloat(response.billamount).toFixed(2)}`);

        var paid = response["billpaid"] ? "PAID" : "UNPAID";
        var status_class = response["billpaid"] ? "bill-paid" : "bill-unpaid";

        // Update whether Party bill is fully paid
        $( '#allpaid' ).html(`<span class="bill-label">Status: </span><span class="${status_class}"> ${paid} </span>`);

        // Remove form for bill request response
        node.parent().remove();
        
    // If bill request rejected
    } else if (action == "Deny") {

        // Return bill component status to unpaid
        node.parent().parent().find( '.paid' ).html(`<span class="bill-label">Paid: </span><span class="bill-unpaid">UNPAID</span>`);

        // Remove unneeded attributes and form for bill request response
        node.parent().parent().find( '.confirm' ).remove();
        node.parent().parent().find( '.paidtime' ).remove();
        node.parent().remove();
    }
}