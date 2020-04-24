
$(document).ready(function(){
    $("#searchInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#tableToFilter tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
    });
});
