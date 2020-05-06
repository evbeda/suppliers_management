
var current_fs, next_fs, previous_fs; 
var left, opacity, scale; 
var animating; 


// Checks if first part of form is complete
function check_first_fieldset_complete(){
	var token = true
	$(".mandatory>input:text, .mandatory>input[type='number'], .mandatory>select, .mandatory>input[type='email']").each(function(index){
		if ($(this).val() == "") {
			token = false;
		}
		else if($(this).get(0).checkValidity() == false){
			token = false;
		}
	});
	return token
}

// Click on First "next" button
$("#first-next").click(function(){
	var esto = $(this);
	if (check_first_fieldset_complete()){
		next_page(esto);
	}
	else{
		alert("Porfavor termine de completar el formulario antes de continuar");
	}
});

// Checks if argentinian BANK form is filled
function check_arg_bank_complete(){
	var token = true;
	$(".arg-bank>input:text, .arg-bank>input[type='number'], .arg-bank>select").each(function(index){
		if ($(this).val() == "") {
			token = false;
		}
		else if($(this).get(0).checkValidity() == false){
			token = false;
		}
	});
	return token
}

// Click on the arg-bank "next" button
$("#arg-bank-next").click(function(){
	var esto = $(this);
	if (check_arg_bank_complete()){
		next_page(esto);
	}
	else {
		alert("Porfavor termine de completar el formulario antes de continuar");
	}
});

// Moves to the next page of the form
function next_page(esto){

	if(animating) return false;
	animating = true;

	current_fs = esto.parent();
	next_fs = esto.parent().next();

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

