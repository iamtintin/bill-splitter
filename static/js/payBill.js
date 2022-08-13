$( function() {

    // On submit of bill payment button, create POST request
    $( '#billpayform' ).submit(function(event) {

        event.preventDefault();

        // Obtain Form values from document
        var billid = $( this ).find('input[name="id"]').val();

        // AJAX POST request to pay bill and return response
        $.post(
            "/paybill",
            {
                id: billid
            },
            function(data, status){
                displayError(data.error, !(data.error.length == 0));
                if (!data.error){
                    updateBill(data);
                }
            }
        );

        return false;

    });
});

// Function to update bill page with response
function updateBill(response) {
    // Remove Payment Form
    if ($( '#billpayform' ).length) {
        $( '#billpayform' ).remove();
    }
    // Update status, paid date and confirmed status of bill on page
    $( '#status' ).html(`<span class="bill-label"> Status: </span><span class="bill-paid"> PAID </span>`);
    $( '#paidtime').html(`<span class="bill-label"> Paid Date: </span>${response.paid_dt}`);
    $( '#confirm' ).html(`<span class="bill-label"> Confirmed: </span><span class="${response.confirmed ? "bill-paid" : "bill-pending"}"> ${response.confirmed ? "CONFIRMED" : "PENDING"} </span>`);
}