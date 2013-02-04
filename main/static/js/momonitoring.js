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
    $("#loading-container").show();
    $.ajax({'url':urlEndpoint,
	    'type':'GET',
	    'dataType':'html',
	    'success':function(data) {
		var modalContainer$ = $(modalContainerSelector);
		modalContainer$.html(data);
		init(modalContainer$);
		$(modalContainerSelector).modal();
	    },
	    'complete': function() {
		$("#loading-container").hide();
	    }
	   })
}

/* for now send a DELETE and refresh. backbone to come */
function deleteResource(urlEndpoint) {
    if (!confirm("Are you sure you want to delete this resource?")) {
	return;
    }
    $("#loading-container").show();
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
	var dataType = $(this).data("type") || "html"
	if (dataType==="image") {
	    $("#myModalContainer").html("<img src='"+urlEndpoint+"' />");
	    $("#myModalContainer").modal();
	} else {
	    fetchModal(urlEndpoint,"#myModalContainer",dataType)
	}
    });

    $('.delete').click(function(event) {
	event.preventDefault();
	deleteResource($(this).attr("href"));
    });
    
    $('.ajaxify').click(function(event) {
	event.preventDefault();
	$('#loading-container').show()
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
	$("#loading-container").show();
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
	    },
	    'complete':function() {
		$("#loading-container").hide();
	    }
    	});
    });
}

function toTastypieResourceUrl(resourceName,resourceId) {
    return "/api/v1/"+resourceName+"/"+resourceId+"/";
}

$(document).ready(function() {
    init();
    var context = cubism.context();
    graphite = context.graphite("http://statsd.graphite.mopub.com:8080/")
});


