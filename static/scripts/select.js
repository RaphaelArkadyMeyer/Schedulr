
document.addEventListener("DOMContentLoaded", function(event) {
	function setInnerText(element,text){
		while (element.firstChild!==null)
			element.removeChild(element.firstChild);
		element.appendChild(document.createTextNode(text));
	}


	var gap_preference_display = document.getElementById('gap_preference_display');
	var gap_preference         = document.getElementById('gap_preference');
	var gap_preference_changed = function() {
		setInnerText(gap_preference_display, gap_preference.value);
	}
	gap_preference.addEventListener('input', gap_preference_changed);
	gap_preference_changed();

	var time_preference_display = document.getElementById('time_preference_display');
	var time_preference         = document.getElementById('time_preference');
	var time_preference_changed = function() {
		var value = +time_preference.value;
		var text = ((value-1)%12+1) + ":00 " + (value < 12 ? "AM" : "PM");
		setInnerText(time_preference_display, text);
	}
	time_preference.addEventListener('input', time_preference_changed);
	time_preference_changed();

	var fields = document.querySelectorAll('form>div.courses>div.form-group');
	function hideFields() {
		var lastVisible = 0;
		for (var i = fields.length-1; i >= 0; i--) {
			if (
					fields[i].classList.contains("has-error") ||
					fields[i].children[1].value
			   ) {
				lastVisible = i+1;
				break;
			}
		}
		for (var i = 0; i < fields.length; i++) {
			if (i <= lastVisible) {
				fields[i].classList.add   ("form-revealed");
			} else {
				fields[i].classList.remove("form-revealed");
			}
		}
	}
	hideFields();
	for (var i = 0; i < fields.length; i++) {
		fields[i].addEventListener("keyup", hideFields);
	}
});
