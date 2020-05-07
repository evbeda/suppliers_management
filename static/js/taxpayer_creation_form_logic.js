$(document).ready(function(){
	$(".arg").hide();
    $(".usa").hide();
    $("input").prop("required", false);
    $("select").prop("required", false);
    set_optionals();
    set_mandatory();
    country_change();
    arg_bank_change();
    $(".hidden").hide();
});

function set_optionals(){
    $(".optional>input").prop("required", false);
}

function set_mandatory(){
    $(".mandatory>input").prop("required", true);
}

function arg_bank_required(){
    $(".arg-bank>input").prop("required", true);
    $(".arg-bank>select").prop("required", true);
}

function arg_bank_unrequired(){
    $(".arg-bank>input").prop("required", false);
    $(".arg-attach>input").prop("required", false);
    $(".arg-bank>select").prop("required", false);
}

function empty_arg(){
    $(".arg>input").val("");
    $(".arg>select").val("");
}

function arg_unrequired(){
    $(".arg>input").prop("required", false);
    $(".arg>select").prop("required", false);
}

$(".special-rules>input").change(function(){
    var validating = $(this);
    validating.get(0).reportValidity();
});

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
$("#id_address_form-country").change(function(){
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
});

function arg_is_responsable_inscripto(){
    $(".ri>input").prop("required", true);
    set_optionals();
}
function arg_is_monotributista(){
    $(".ri>input").prop("required", false);
    $(".mono>input").prop("required", true);
}

function arg_bank_change(){
    if ($("#id_taxpayer_form-taxpayer_condition").val() == "responsable_inscripto"){
		$(".ri").show();
        arg_is_responsable_inscripto();
    }
    else if ($("#id_taxpayer_form-taxpayer_condition").val() == "monotributista"){
        $(".ri").hide();
        $(".mono").show();
        arg_is_monotributista();
    }
}

$("#id_taxpayer_form-taxpayer_condition").change(function(){
    if ($("#id_taxpayer_form-taxpayer_condition").val() == "responsable_inscripto"){
		$(".ri").show();
        arg_is_responsable_inscripto();

    }
    else if ($("#id_taxpayer_form-taxpayer_condition").val() == "monotributista"){
        $(".ri").hide();
        $(".mono").show();
        arg_is_monotributista();
    }
});