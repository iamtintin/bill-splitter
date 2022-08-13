$( function() {
    // On submit of create party button check if inputs are valid and display appropriate error message
    $( '#partyform' ).submit(function() {

        var msg = ""
        
        // Check string format of name
        var name = $( '#partyform' ).find('input[name="partyname"]').val();

        if (!validGenericString(name)) msg += "Invalid Name entered. Party Name can only comprise of alphanumeric characters and some special characters ( ) , . ' - : <br><br>";
        
        // Check whether at least 1 other member is selected to be included in the party
        var members = $( '#partyform' ).find('input[name="memberlist"]:checked').length;

        if (members == 0) msg += "Select at least one friend to include in the party.<br>";

        // Display any error messages
        var error = msg.length != 0;
        displayError(msg, error);

        return !error;
    });
});