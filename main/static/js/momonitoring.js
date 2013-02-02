function fetchModal(urlEndpoint,modalContainerSelector) {
    $.ajax({'url':urlEndpoint,
	    'type':'GET',
	    'dataType':'html',
	    'success':function(data) {
		$(modalContainerSelector).html(data);
		$(modalContainerSelector).modal();
	    }
	   })
}

function init() {
    $('.modalize').click(function(event) {
	event.preventDefault();
	var urlEndpoint = $(this).attr("href");
	fetchModal(urlEndpoint,"#myModalContainer")
    });
}

$(document).ready(init);
