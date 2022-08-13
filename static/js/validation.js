// Function to Validate Username using regex
function validUsername(str) {
    var regexp = /^[a-zA-Z0-9,.'"@\#\-_]+$/;
    return !(str.search(regexp) === -1);
}

// Function to Validate generic strings using regex
function validGenericString(str) {
    var regexp = /^[A-Za-z0-9(): ,.'-]+[A-Za-z0-9():,.'-]$/;
    return !(str.search(regexp) === -1);
}

// Function to display / remove error message box
function displayError(str, error) {
    var div = $('#errmsg');
    // If there is an error message, make error box visible
    if(error){
        if (div.hasClass("hidden")) {
            div.removeClass("hidden");
            div.addClass("visible-err");
        }
        div.html("<p>" + str + "</p>");

        // Scroll to view error message
        $('html, body').animate({
            scrollTop: $("#errmsg").offset().top
        }, 1000);    
    // If no err message, make error box invisible
    } else {
        if (!div.hasClass("hidden")) {
            div.removeClass("visible-err");
            div.addClass("hidden");
        }
        div.html("");
    }
}

// Function to capitalise 1st Letter of each word
function titleFilter(str) {
    const words = str.split(" ");

    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
    }

    return words.join(" ");
}

// Function to round number to fixed no. of decimal places
function toFixed(num, fixed) {
    var re = new RegExp('^-?\\d+(?:\.\\d{0,' + (fixed || -1) + '})?');
    return num.toString().match(re)[0];
}