//Used for serializing form object to json
$.fn.serializeObject = function()
{
   var o = {};
   var a = this.serializeArray();
   $.each(a, function() {
       if (o[this.name]) {
           if (!o[this.name].push) {
               o[this.name] = [o[this.name]];
           }
           o[this.name].push(this.value || '');
       } else {
           o[this.name] = this.value || '';
       }
   });
   return o;
};

function fetchModal(urlEndpoint,modalContainerSelector) {
    $.ajax({'url':urlEndpoint,
	    'type':'GET',
	    'dataType':'html',
	    'success':function(data) {
		var modalContainer$ = $(modalContainerSelector);
		modalContainer$.html(data);
		init(modalContainer$);
		$(modalContainerSelector).modal();
	    }
	   })
}

/* for now send a DELETE and refresh. backbone to come */
function deleteResource(urlEndpoint) {
    if (!confirm("Are you sure you want to delete this resource?")) {
	return;
    }
    $.ajax({'url':urlEndpoint,
	    'type':'DELETE',
	    'success':function(data) {
		location.reload()
	    }
	   });
}

function init(container$) {
    if(typeof(container$)==='undefined') container$ = $('body');

    $('.modalize').click(function(event) {
	event.preventDefault();
	var urlEndpoint = $(this).attr("href");
	fetchModal(urlEndpoint,"#myModalContainer")
    });

    $('.delete').click(function(event) {
	event.preventDefault();
	deleteResource($(this).attr("href"));
    });
    
    $('.ajaxify').click(function(event) {
	event.preventDefault();
	$.ajax({'url':$(this).attr("href"),
		'type':'GET',
		'complete': function() {
		    location.reload();
		},
	       });
    });

    $('form').submit(function(event) {
    	event.preventDefault()
    	var form$ = $(this);
	var data = form$.serializeObject()
	if ("service" in data) {
	    data['service'] = toTastypieResourceUrl('service',data['service'])
	}
    	$.ajax({
    	    'url':form$.attr('action'),
    	    'type':form$.attr('method'),
	    'dataType':'json',
	    'contentType':'application/json',
    	    'data':JSON.stringify(data),
    	    'success':function(data) {
    		location.reload();
    	    },
	    'error':function(d) {
		a = d;
	    }
    	});
    });
}

function toTastypieResourceUrl(resourceName,resourceId) {
    return "/api/v1/"+resourceName+"/"+resourceId+"/";
}

$(document).ready(function() {init()});
