$( function() {

    /*Functions for accessability for keyboard-only access - better 
    highlighting of focused elements. */
    
    $( '.btn_block a' ).on("focus", function(event){
        $( this ).parent().addClass("btn-block-focus");
    });

    $( '.btn_block a' ).on("focusout", function(event){
        $( this ).parent().removeClass("btn-block-focus");
    });

    $( '.innerblock a').on("focus", function(event){
        $( this ).siblings('.title').addClass("innerblock-focus");
    });

    $( '.innerblock a').on("focusout", function(event){
        $( this ).siblings('.title').removeClass("innerblock-focus");
    });

    $( '.flex-cell a').on("focus", function(event){
        $( this ).parent().addClass("flex-cell-focus");
    });

    $( '.flex-cell a').on("focusout", function(event){
        $( this ).parent().removeClass("flex-cell-focus");
    });
});