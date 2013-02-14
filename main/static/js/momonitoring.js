
var sortableTable = function(table$) {
    $('th',table$)
	.wrapInner("<span title='sort this column' />")
	.each(function() {
	    var th$ = $(this),
	    thIndex = th$.index(),
	    inverse = false;

            th$.click(function(){
                
                table$.find('td').filter(function(){
                    
                    return $(this).index() === thIndex;
                    
                }).sortElements(function(a, b){
                    
                    return $.text([a]) > $.text([b]) ?
                        inverse ? -1 : 1
                        : inverse ? 1 : -1;
                    
                }, function(){
                    
                    // parentNode is the element we want to move
                    return this.parentNode; 
                    
                });
                
                inverse = !inverse;
                    
            });
	})
}

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

    $('.table-sortable').each(function() {sortableTable($(this));});

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

    $('form.ajaxForm').submit(function(event) {
    	event.preventDefault()	
    	var form$ = $(this);
	data = form$.serializeObject()
	
	//hack to fix foreign key attribute w/ tastypie. need to do this better
	if (("service" in data) && form$.attr("action").indexOf("scriptservicecheck")==-1) {
	    data['service'] = toTastypieResourceUrl('service',data['service'])
	}
	//hack to fix foreign key attribute w/ tastypie. need to do this better
	if ("complex_check" in data) {
	    data['complex_check'] = toTastypieResourceUrl('complexservicecheck',data['complex_check'])
	}
	//hack to fix foreign key attribute w/ tastypie. need to do this better
	if ("object_type" in data) {
	    data['object_type'] = toTastypieResourceUrl('objecttype',data['object_type'])
	}
	//hack to fix. need to do this better
	for (var key in data) {
	    if (!data.hasOwnProperty(key)) {continue;}
	    //another hack to make sure silenced works
	    if (key==="silenced") {continue;}
	    if (data[key]==="") { data[key] = null;}
	}

	method = form$.attr("method")
	var contentType = "application/json";
	
	$("#loading-container").show();
    	$.ajax({
    	    'url':form$.attr('action'),
    	    'type':method,
	    'dataType':'json',
	    'contentType':contentType,
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

    $('.toggle-hide').click(function(e) {
	e.preventDefault()	
	$($(this).attr("href")).toggle();
    });

}

function toTastypieResourceUrl(resourceName,resourceId) {
    return "/api/v1/"+resourceName+"/"+resourceId+"/";
}

$(document).ready(function() {
    init();
});


