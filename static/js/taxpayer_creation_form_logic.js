// Hides fields from 2nd and 3rd step, and sets required to the 1st step mandatory fields
// Also sets optional to optinal fields if the page has to reload with the cache still on
$(document).ready(function(){
	$(".arg").hide();
    $(".usa").hide();
    $(".hidden").hide();
    $("input").prop("required", false);
    $("select").prop("required", false);
    set_optionals();
    set_mandatory();
    country_change();
    arg_bank_change();
});

// Removes the required prop from optional fields
function set_optionals(){
    $(".optional>input").prop("required", false);
}

// Adds required prop to mandatory fields from first step
function set_mandatory(){
    $(".mandatory>input").prop("required", true);
    $(".mandatory>select").prop("required", true);
}

// Adds required prop to mandatory fields from argentinian bank step
function arg_bank_required(){
    $(".arg-bank>input").prop("required", true);
    $(".arg-bank>select").prop("required", true);
}

// Resets value from Argentinian fields
function empty_arg(){
    $(".arg>input").val("");
    $(".arg>select").val("");
}

// Removes required prop from Argentinian fields
function arg_unrequired(){
    $(".arg>input").prop("required", false);
    $(".arg>select").prop("required", false);
}

// Reports the validity upong value change for special fields
$(".special-rules>input").change(function(){
    var validating = $(this);
    validating.get(0).reportValidity();
});

// Depending on what country was chosen, it shows the corresponding fieldsets and hides the other ones
function country_change(){
    if ($("#id_address_form-country").val() == "AR"){
		$(".arg-bank").show();
        $(".usa").hide();
        arg_bank_required();
    }
    else if ($("#id_address_form-country").val() == "BR"){
    }
    else if ($("#id_address_form-country").val() == "US"){
        $(".usa").show();
        $(".arg").hide();
        arg_unrequired();
        empty_arg();
    }
}

// Event listener for country change
$("#id_address_form-country").change(function(){
    country_change()
});

// Makes responsable inscripto 'ri' fields mandatory and sets optional fields for responsable inscripto
function arg_is_responsable_inscripto(){
    $(".ri").show();
    $(".ri>input").prop("required", true);
    set_optionals();
}

// Makes monotributista 'mono' fields mandatory and responsable inscripto 'ri' fields to unrequired
function arg_is_monotributista(){
    $(".ri").hide();
    $(".mono").show();
    $(".ri>input").prop("required", false);
    $(".mono>input").prop("required", true);
}

// Depending on the value for taxpayer condition executes the corresponding function
function arg_bank_change(){
    if ($("#id_taxpayer_form-taxpayer_condition").val() == "responsable_inscripto"){
        arg_is_responsable_inscripto();
    }
    else if ($("#id_taxpayer_form-taxpayer_condition").val() == "monotributista"){
        arg_is_monotributista();
    }
}

// Event listener for taxpayer condition value change
$("#id_taxpayer_form-taxpayer_condition").change(function(){
    arg_bank_change()
});