
document.addEventListener("DOMContentLoaded", function(event) {
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
