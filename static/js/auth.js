$( function() {

    // Validate login form data on submit
    $( '#loginform' ).submit(function(event) {

        event.preventDefault();

        // Retrieve input data from form
        var email = $( this ).find('input[name="email"]').val();
        var pass = $( this ).find('input[name="user_pass"]').val();

        // AJAX POST request for server to validate username and password
        $.post(
            "/login",
            {
                email: email,
                user_pass: pass
            },
            function(data, status){
                // Display error if one occurred, else redirect
                if(data["error"]) {
                    displayError(data["error"], true);
                } else {
                    displayError(data["error"], false);
                    window.location.replace("/overview");
                }
            }
        );
        
        return false;
    });

    // Validate register form data on submit
    $( '#registerform' ).submit(function(event) {

        event.preventDefault()

        // Retrieve input data from form
        var fname = $( this ).find('input[name="name"]').val();
        var uname = $( this ).find('input[name="username"]').val();
        var pass = $( this ).find('input[name="user_pass"]').val();
        var email = $( this ).find('input[name="email"]').val();

        // AJAX POST request for server to validate user input
        $.post(
            "/register",
            {
                username: uname,
                name: fname,
                email: email,
                user_pass: pass
            },
            function(data, status){
                // Display error if one occurred, else redirect
                if(data["error"]) {
                    displayError(data["error"], true);
                } else {
                    displayError(data["error"], false);
                    window.location.replace("/overview");
                }
            }
        );

        return false;
    });
});