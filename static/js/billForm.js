$( function() {

    // On reload if option is checked, make corresponding fields visible
    if ($( '#uneven' ).is(":checked")) {
        $( '#fractions' ).removeClass("hidden");
    }

    if ($( '#tlimit' ).is(":checked")) {
        $( '#tlimit' ).parent().next().removeClass("hidden");
    }

    // When selected party is changed, retrieve party members to display
    $( '#party' ).on("change", function(event){

        // Retrieve party id from input form
        var partyID = $( this ).find(":selected").val();

        // AJAX POST request to retrieve list of party members from server
        $.post(
            "/getjsonmembers/" + partyID, 
            {}, 
            function(data, status){
                // Display error if one occurred
                if (data.error) {
                    displayError(data.error, true);
                } else {
                    displayError(data.error, false);
                    updatePortions(data);
                }
            }
        );
    });

    // When uneven portions option changes, hide/show list of input fields
    $( '#uneven' ).on("change", function(event){
        // If option is checked, show list, otherwise hide list
        if ($( this ).is(":checked")) {
            $( '#fractions' ).removeClass("hidden");
        } else {
            $( '#fractions' ).addClass("hidden");
        }

    });

    // When time limit option changes, hide/show input field for due date and time
    $( '#tlimit' ).on("change", function(event){

        var nextInput = $( this ).parent().next();
        // If option is checked, show input field, otherwise hide input field
        if ($( this ).is(":checked")) {
            nextInput.removeClass("hidden");
        } else {
            nextInput.addClass("hidden");
            nextInput.find('#dateinput').val('');
        }

    });

    // On submit of create bill button check if inputs are valid and display appropriate error message
    $( '#billform' ).submit(function() {

        var msg = ""
        
        // Check for valid name and description string formats
        var name = $( '#billform' ).find('input[name="name"]').val();
    
        var description = $( '#billform' ).find('input[name="description"]').val();
    
        var validName = validGenericString(name);
    
        if (!validName) msg += "Invalid Name entered. ";
    
        var validDescription = validGenericString(description) || description.length == 0
    
        if (!validDescription) msg += "Invalid Description entered. "
    
        if (!validDescription || !validName) {
            msg += "Bill Name and Description can only comprise of alphanumeric characters and some special characters ( ) , . ' - : <br><br>";
        }
        
        // Chec for valid amount 
        var amount = $( '#billform' ).find('input[name="amount"]').val();
        
        // Check for valid due date if option is checked
        var duedate = $( '#billform' ).find('input[name="tlimit"]').is(":checked");
        if (duedate){
            var duedate = $( '#billform' ).find('input[name="duedate"]').val();
            var duetime = $( '#billform' ).find('input[name="duetime"]').val();
            if (!duedate || !duetime) msg += "Due date option for bill is checked. Please provide a valid due date <br><br>";
        }
        
        // Ensure uneven portions sum to total amount, if option is checked
        var unevensplit = $( '#billform' ).find('input[name="uneven"]').is(":checked");
        if (unevensplit){
            var total = 0;
            $("#fractions input").each(function() {
                var portion = $( this ).val();
                if (portion.length == 0) portion = 0;
                total += parseFloat(portion);
            });
            if (total != amount) msg += "Portions of each member in party must sum to the given Bill Amount<br>";
        }
    
        // Display any error messages
        var error = msg.length != 0;
        displayError(msg, error);
    
        return !error;
    });

});


// Function to update the list of uneven portion fields for each party member
function updatePortions(response) {
    // Remove all existing input fields
    var list = $( '#fractions' );
    list.empty();
    // Add new field using template for each party member in list
    for(let i = 0; i < response.ids.length; i++ ) {
        const markup = `
        <div class="form-cell">
            <label for="user${response.ids[i]}">${response.names[i]}: </label>
            <input type="number" name="${response.ids[i]}" id="user${response.ids[i]}" min="0" step="0.01" value="0">
        </div>
        `;

        list.append(markup);
    }
}