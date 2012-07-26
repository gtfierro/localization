$('#actuate').click(function() {
    $.ajax("isolate/" + current_zone);
});
