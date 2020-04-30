$(document).ready(function(){
	$(".arg").hide();
    $(".usa").hide();
    $("input").prop("required", false);
    $("select").prop("required", false);
    set_optionals();
    country_change();
    arg_bank_change();

});

function set_optionals(){
    $(".optional>input").prop("required", false);
    console.log("ejecutando set_optionals");
}

function arg_bank_required(){
    $(".arg-bank>input").prop("required", true);
    $(".arg-bank>select").prop("required", true);
    console.log("ejecutando arg_bank_required");
}

function arg_bank_unrequired(){
    $(".arg-bank>input").prop("required", false);
    $(".arg-attach>input").prop("required", false);
    $(".arg-bank>select").prop("required", false);
    console.log("ejecutando arg_bank_unrequired");
}

function empty_arg(){
    $(".arg>input").val("");
    $(".arg>select").val("");
}

function arg_unrequired(){
    $(".arg>input").prop("required", false);
    $(".arg>select").prop("required", false);
}

function country_change(){
    if ($("#id_address_form-country").val() == "AR"){
		$(".arg-bank").show();
        $(".usa").hide();
        console.log("es required");
        arg_bank_required();

    }
    else if ($("#id_address_form-country").val() == "BR"){

    }
    else if ($("#id_address_form-country").val() == "US"){
        $(".usa").show();
        $(".arg").hide();
        console.log("no es required");
        arg_unrequired();
        empty_arg();
    }
    else{
        console.log("nothing to do")
    }
}
$("#id_address_form-country").change(function(){
    if ($("#id_address_form-country").val() == "AR"){
		$(".arg-bank").show();
        $(".usa").hide();
        console.log("es required");
        arg_bank_required();

    }
    else if ($("#id_address_form-country").val() == "BR"){

    }
    else if ($("#id_address_form-country").val() == "US"){
        $(".usa").show();
        $(".arg").hide();
        console.log("no es required");
        arg_unrequired();
        empty_arg();
    }
});

function arg_is_ri(){
    $(".ri>input").prop("required", true);
    set_optionals();
    console.log("ejecutando arg_is_ri");

}
function arg_is_mono(){
    $(".ri>input").prop("required", false);
    $(".mono>input").prop("required", true);
    console.log("ejecutando arg_is_mono");

}

function arg_bank_change(){
    if ($("#id_taxpayer_form-taxpayer_condition").val() == "responsable_inscripto"){
		$(".ri").show();
        console.log("es ri");
        arg_is_ri();

    }
    else if ($("#id_taxpayer_form-taxpayer_condition").val() == "monotributista"){
        $(".ri").hide();
        $(".mono").show();
        arg_is_mono();
        console.log("es mono");
    }
    else {
        console.log("nothing to do for bank");
    }
}

$("#id_taxpayer_form-taxpayer_condition").change(function(){
    if ($("#id_taxpayer_form-taxpayer_condition").val() == "responsable_inscripto"){
		$(".ri").show();
        console.log("es ri");
        arg_is_ri();

    }
    else if ($("#id_taxpayer_form-taxpayer_condition").val() == "monotributista"){
        $(".ri").hide();
        $(".mono").show();
        arg_is_mono();
        console.log("es mono");
    }
});