
var current_fs, next_fs, previous_fs; 
var left, opacity, scale; 
var animating; 


// Recieves an array of inputs and checks each one for completeness and validity of data 
function check_completed_form_section(section){
	var token = true
	section.each(function(index){
		if ($(this).val() == "") {
			token = false;
		}
		else if($(this).get(0).checkValidity() == false){
			token = false;
		}
	});
	return token
}

// Click the "next" button, and sends corresponding inputs to inspect for completion
$(".next").click(function(){
	var can_advance = true
	if ($(this).is("#first-next")){
		var first_fieldset_mandatory_inputs = $(".mandatory>input:text, .mandatory>input[type='number'], .mandatory>select, .mandatory>input[type='email']")
		if (check_completed_form_section(first_fieldset_mandatory_inputs) == false){
			can_advance = false;
		}
	}
	else if ($(this).is("#arg-bank-next")){
		var arg_bank_mandatory_inputs = $(".arg-bank>input:text, .arg-bank>input[type='number'], .arg-bank>select")
		if (check_completed_form_section(arg_bank_mandatory_inputs) == false){
			can_advance = false;
		}
	} // Add future fieldests to this if statement sending their inputs

	if (can_advance){
		next_page($(this));
	}
	else{
		alert("Porfavor termine de completar el formulario antes de continuar");
	}
});

// Moves to the next page of the form
function next_page(current_component){
	if(animating) return false;
	animating = true;

	current_fs = current_component.parent();
	next_fs = current_component.parent().next();

	$("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

	next_fs.show(); 
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			scale = 1 - (1 - now) * 0.2;
			left = (now * 50)+"%";
			opacity = 1 - now;
			current_fs.css({
			'transform': 'scale('+scale+')',
			'position': 'absolute'
        });
			next_fs.css({'left': left, 'opacity': opacity});
		}, 
		duration: 800, 
		complete: function(){
			current_fs.hide();
			animating = false;
		}, 
		easing: 'easeInOutBack'
	});
};

// Moves to the previous page of the form
$(".previous").click(function(){
	if(animating) return false;
	animating = true;
	
	current_fs = $(this).parent();
	previous_fs = $(this).parent().prev();
	
	$("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");
	
	previous_fs.show(); 
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			scale = 0.8 + (1 - now) * 0.2;
			left = ((1-now) * 50)+"%";
			opacity = 1 - now;
			current_fs.css({'left': left});
			previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
		}, 
		duration: 800, 
		complete: function(){
			current_fs.hide();
			animating = false;
		}, 
		easing: 'easeInOutBack'
	});
});

