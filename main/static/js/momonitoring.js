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
    //unchecked checkbox dont show up in serialize array. fuck me right?
    $('input[type=checkbox]:not(:checked)').each(function() {
	o[this.name] = ""; //FUCK YOU TASTYPIE
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

    $('.tooltipped').tooltip()

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
	data = form$.serializeObject()

	//hack to fix foreign key attribute w/ tastypie. need to do this better
	if ("service" in data) {
	    data['service'] = toTastypieResourceUrl('service',data['service'])
	}
	//hack to fix timeout. need to do this better
	if ("timeout" in data && data['timeout']==="") {
	    data['timeout'] = null;
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

    $('form').each(function() {
	var form$ = $(this);
	$('input',form$).keypress(function(event) {
	    if (event.which == 13) {
		event.preventDefault();
		form$.submit();
	    }
	});
    });

}

function toTastypieResourceUrl(resourceName,resourceId) {
    return "/api/v1/"+resourceName+"/"+resourceId+"/";
}

$(document).ready(function() {
    init();
});


