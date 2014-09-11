
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

function highchartize(target$) {

    dataSeries = target$.data("series");	
    errorSeries = target$.data("error");
    var containerWrapper$ = $(target$.data("container"))
    var containerId = target$.attr("id")+"-container"
    containerWrapper$.html("<div id='"+containerId+"'>");

    //hack to get highchartize to work with both slideshow and modals
    var chartHeight = Math.max(containerWrapper$.height(),400)

    var chartOptions = {
	chart : {
	    renderTo:containerId,
	    type:'line',
	    height:chartHeight
	},
	title : {
	    text : target$.data("title") || "No title given"
	},
	plotOptions : {
	    series : {
		fillOpacity : 0.4
	    }
	},
	series : [
	    {
		"name" : "Last Value",
		"data" : dataSeries
	    },
	    {
		"name" : "Valid Range",
		"type" : "arearange",
		"lineWidth":.2,
		"data" : errorSeries
	    }
	],
	yAxis : {
	    min : 0
	}
    }
    var chart = new Highcharts.Chart(chartOptions);
    if (containerWrapper$.hasClass("modal")) {
	containerWrapper$.modal();
    }
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

function setSilencedDescriptionFromField() {
    if ($("#id_silenced_until").length === 0) {
        return;
    }

    // Both of these vars are timestamps (seconds since the epoch).
    var now = new Date().getTime() / 1000;
    var silencedUntil = parseInt($("#id_silenced_until").val());

    function round(num) {
        // Rounds 1.8 to 2, but 1.79 to 1.
        return Math.floor(num + 0.2);
    }

    var diffSeconds = round(silencedUntil - now);
    var diffMinutes = round(diffSeconds / 60);
    var diffHours   = round(diffMinutes / 60);
    var diffDays    = round(diffHours / 24);

    var description;

    if (2000000000 <= silencedUntil) {
        description = "Silenced forever";
    } else if (silencedUntil < now) {
        description = "Not silenced";
    } else if (diffDays >= 2) {
        description = "Silenced for ~" + diffDays + " day(s)";
    } else if (diffHours >= 2) {
        description = "Silenced for ~" + diffHours + " hour(s)";
    } else if (diffMinutes >= 1) {
        description = "Silenced for " + diffMinutes + " minute(s)";
    } else {
        description = "Silenced for " + diffSeconds + " second(s)";
    }

    $("#silenced_description").text(description);
}

function setSilencedFor(secondsFromNow) {
    var now = new Date().getTime() / 1000; // Timestamp (seconds since the epoch).
    var silencedUntil = Math.floor(now + secondsFromNow);
    $("#id_silenced_until").val(silencedUntil);
    setSilencedDescriptionFromField();
}

function setSilencedForever() {
    $("#id_silenced_until").val(2000000000);
    setSilencedDescriptionFromField();
}

function setUnSilenced() {
    $("#id_silenced_until").val(0);
    setSilencedDescriptionFromField();
}

function setSilencedForXHours() {
    var hoursToSilenceFor = parseFloat($("#silence_hours").val());
    setSilencedFor(hoursToSilenceFor * 60 * 60);
}

function init(container$) {    
    console.log("hello")
    if(typeof(container$)==='undefined') container$ = $('body');

    $('.choicebox',container$).each(function() {
	var selectName = $(this).data("name");
	var select$ = $('select[name='+selectName+']',container$);
	var choicebox$ = $(this)
	var choices$ = $('.choice',choicebox$);
	select$.change(function() {
	    choices$.each(function() {
		if ($(this).attr("id")!==select$.val()) {
		    $(this).hide();
		} else {
		    $(this).show();
		}
	    });
	});
	select$.change();
    });
	
    $('.tooltipped',container$).tooltip()

    $('.table-sortable',container$).each(function() {sortableTable($(this));});

    $('.modalize',container$).click(function(event) {
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
    $('a.highchartize',container$).click(function(event) {
	event.preventDefault();
	highchartize($(this));
    });
    $('div.highchartize',container$).each(function(index,element) {
	highchartize($(element));
    });

    $('.delete',container$).click(function(event) {
	event.preventDefault();
	deleteResource($(this).attr("href"));
    });
    
    $('.ajaxify',container$).click(function(event) {
    	event.preventDefault();
    	$('#loading-container').show()
    	$.ajax({'url':$(this).attr("href"),
    		'type':'GET',
    		'complete': function() {
    		    location.reload();
    		},
    	       });
    });

    $('form.ajaxForm',container$).submit(function(event) {
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

    setSilencedDescriptionFromField();
    $('#id_silenced_until',container$).change(setSilencedDescriptionFromField);
    $('#id_silenced_until',container$).click(setSilencedDescriptionFromField);
    $('#id_silenced_until',container$).focus(setSilencedDescriptionFromField);
    $('#id_silenced_until',container$).blur(setSilencedDescriptionFromField);
    $('#id_silenced_until',container$).keyup(setSilencedDescriptionFromField);
    $('#id_silenced_until',container$).keydown(setSilencedDescriptionFromField);

    $('#unsilence',container$).click(setUnSilenced);
    $('#silence_for_x_hours',container$).click(setSilencedForXHours);
    $('#silence_forever',container$).click(setSilencedForever);

    $('form',container$).each(function() {
	var form$ = $(this);
	$('input',form$).keypress(function(event) {
	    if (event.which == 13) {
		event.preventDefault();
		form$.submit();
	    }
	});
    });

    $('.toggle-hide',container$).click(function(e) {
	e.preventDefault()	
	$($(this).attr("href")).toggle();
    });

}

function toTastypieResourceUrl(resourceName,resourceId) {
    return "/api/v1/"+resourceName+"/"+resourceId+"/";
}

$(document).ready(function() {
    init();
    $('div[data-role=page]').live("pageinit",
				  function() { init($(this)); });
});


