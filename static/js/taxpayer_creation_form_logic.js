$(document).ready(function(){
	$(".arg").hide();
    $(".usa").hide();
    $("input").prop("required", false);
    set_optionals()

});

function set_optionals(){
    $(".optional>input").prop("required", false);
    console.log("ejecutando set_optionals");
}

function arg_bank_required(){
    $(".arg-bank>input").prop("required", true);
    console.log("ejecutando arg_bank_required");
}

function arg_bank_unrequired(){
    $(".arg-bank>input").prop("required", false);
    $(".arg-attach>input").prop("required", false);
    console.log("ejecutando arg_bank_unrequired");
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
        arg_bank_unrequired();
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

$("#id_taxpayer_form-taxpayer_condition").change(function(){
    if ($("#id_taxpayer_form-taxpayer_condition").val() == "responsable_inscripto"){
		$(".ri").show();
        console.log("es ri");
        arg_is_ri();

    }
    else {
        $(".ri").hide();
        $(".mono").show();
        arg_is_mono();
        console.log("es mono");
    }
});