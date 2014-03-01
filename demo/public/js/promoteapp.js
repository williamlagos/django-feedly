/* Namespace Create */ create = {

submitCause:function(event){
	event.preventDefault();
	$.ajax({
		url:'/promote/projects',
		type:'POST',
		data:$('#project').serialize(),
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){
			$.get('/efforia/twitter/post',{
				'content':'Criei o projeto #'+$('input[name=title]').val()+' no Efforia.'
			},function(data){});
			$.get('/efforia/facebook/post',{
				'content':'Criei o projeto #'+$('input[name=title]').val()+' no Efforia.'
			},function(data){});
			$('#projects').html(data);
			$('.send').button('reset')
			.removeClass('projectcreate')
			.addClass('linkcreate');
			$.fn.eventLoop();
            $.fn.mainLoop();
		}
	});
},

submitVideo:function(event){
	event.preventDefault();
	$('.send').button('loading');
	$('#video').submit();
},

submitMovement:function(event){
	event.preventDefault();
	var movement_title = $('#movement_title').val();
	var movement_interest = $('.selected').text().trim();
	$.ajax({
		url:'/promote/movement',
		type:'POST',
		data:{
			'title':movement_title,
			'interest':movement_interest
		},
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){ $.fn.showMosaic(); }
	});
},

selectKeyword:function(event){
	event.preventDefault();
	$('.keyword').removeClass('selected')
	$(this).addClass('selected');
},

showMovement:function(event){
	event.preventDefault();
	movement = $('.title',this).text().trim();
	$.ajax({
		url:'/promote/movement',
		data:{'title':movement},
		beforeSend:function(){ $.fn.Progress('Carregando projetos'); },
		success:function(data){
			$('#Grade').Mosaic(data);
			$.fn.eventLoop(data);
		}
	});
},

promoteProject:function(event){
	event.preventDefault();
	$.get('/promote/promote',{},function(data){
		$('.promotecontent').html(data);
		$('.send').removeClass('promote')
		.addClass('objectpromote');
		$.fn.eventLoop();
        $.fn.mainLoop();
	});
},

promoteObject:function(event){
	event.preventDefault();
	var object_id = $('#Espaco .id').text().trim();
	var object_token = $('#Espaco .token').text().trim();
    var object_text = $('#promotetext').val(); 
	$.ajax({
		url:'/promote/promote',
		type:'POST',
		data:{
			'id':object_id,
			'token':object_token,
			'content':object_text,
		},
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){ 
            $.get('/efforia/facebook/post',{'id':data,'content':object_text},function(data){
                $.fn.showMosaic(); 
            });
        }
	})
},

showPromoted:function(event){
	event.preventDefault();
	var promoted = $('.promotedid',this).text().trim();
	$.ajax({
		url:'/promote/promoted',
		data:{'id':promoted},
		beforeSend:function(data){ $.fn.Progress('Carregando conte��do promovido'); },
		success:function(data){
		    $('#Grade').Mosaic(data);	
            $.fn.eventLoop();
            $.fn.mainLoop();
		}
	});
},

selectVideo:function(event){
	event.preventDefault();
	$.fn.hideMenus();
	$.post('/promote/collection',{},function(data){
		$('#Espaco').dialog('close');
		$('#Grade').empty();
		$('#Grade').html(data);
		$('.mosaic-block').mosaic();
		$('.playable').click(function(event){
			event.preventDefault();
			$.e.token = $(this).parent().attr('href');
			$.fn.showMenus();
			$('#Espaco').dialog('open');
		});
	});
},
 
showProject:function(event){
	event.preventDefault();
	var project_id = $('.id',this).text().trim();
	$.get('/promote/project',{'id':project_id},function(data){
		$('#Grade').html($.parseHTML(data.trim())).addClass('player');
		var href = $('#player').attr('href');
		var span_width = $('.span4').width();
		$.e.playerOpt['initialVideo'] = $.e.lastVideo = href;
		$.e.playerOpt['width'] = span_width; 
		$.e.playerOpt['height'] = span_width/1.7;
		$("#player").tubeplayer($.e.playerOpt);
		$.fn.eventLoop();
        $.fn.mainLoop();
	});
},

pledgeProject:function(event){
	event.preventDefault();
	$.get('/promote/pledge',{'id':$('#Espaco').find('.id').text().trim()},function(data){
		$('.promotecontent').html(data);
		$('.second').removeClass('pledge').addClass('objectpledge');
		$.fn.eventLoop();
        $.fn.mainLoop();
	});
},

transferPledge:function(event){
	event.preventDefault();
	var credits = $('#promotecredit').val();
	var project = $('#Espaco .id').text().trim();
    var projnam = 'Doação para '+$('.projectname').text().trim();
	$.ajax({
		url:'/efforia/basket/',
		type:'POST',
		data:{'value':credits,'id':project,'token':projnam,'visual':'static/img/projects.png'},
		beforeSend:function(){ $('.objectpledge').button('loading'); },
		success:function(data){ 
            if(document.cookie.indexOf('permissions=view_only') > -1) $('.promotecontent').generateButtons(projnam,credits,1);
            else{ $('#Espaco').modal('hide'); window.location = '/'; }
        }
	});
},

enrollEvent:function(event){
    event.preventDefault();
    var credits = $('#Espaco .eventvalue').text().trim();
    var eventnam = 'Ingresso para '+$('.eventname').text().trim();
    var eventid = $('#Espaco .id').text().trim();
    var quantity = $('#promotecredit').val().trim();
    $.ajax({
		url:'/efforia/basket/',
		type:'POST',
		data:{
            'qty':quantity,
            'value':credits,
            'id':eventid,
            'token':eventnam,
            'visual':'static/img/events.png'
        },
		beforeSend:function(){ $('.participateevent').button('loading'); },
		success:function(data){ 
            if(document.cookie.indexOf('permissions=view_only') > -1) $('.promotecontent').generateButtons(eventnam,credits,quantity);
            else{ $('#Espaco').modal('hide'); window.location = '/'; }
        }
	});
},

showBackers:function(event){
	event.preventDefault();
	var project_id = $('#Espaco .id').text().trim();
	$.ajax({
		url:'/promote/backers',
		data:{'project_id':project_id},
		beforeSend:function(){ $.fn.Progress('Carregando apoiadores'); },
		success:function(data){	$('#Espaco').modal('hide'); $('#Grade').Mosaic(data); }
	});
},

showEvent:function(event){
	event.preventDefault();
	var event_id = $('.id',this).text().trim();
	$.get('/promote/event',{'id':event_id},function(data){
		$('#Grade').empty().html($.parseHTML(data.trim())).addClass('player');
		$.fn.eventLoop();
	});
},

submitEvent:function(event){
	event.preventDefault();
	$.post('/promote/calendar',$('#evento').serialize(),function(data){
		$.get('/efforia/facebook/event',$('#evento').serialize(),function(data){
			var ident = data;
            $.e.uploadOpt['url'] = $('#image').attr('action');
	        $.e.uploadOpt['success'] = function(data){
                $.get('efforia/facebook/eventcover',{'id':ident,'url':data},function(data){
                    $.get('promote/eventid',{'id':ident},function(data){});
                    $.fn.showMosaic();
                });
	        }
	        $('.upload,.file').fileUpload($.e.uploadOpt);
	        $.fn.eventLoop();
	        $.fn.mainLoop();
		});
		$('#event').html(data);
	});
},

showEnroll:function(event){
    event.preventDefault();
    var eventid = $('#Espaco .id').text().trim();
    $.get('/promote/enroll',{'id':eventid},function(data){
        $('.promotecontent').html(data);
        $('.enroll').removeClass('enroll').addClass('participateevent');
        $.fn.eventLoop();
        $.fn.mainLoop();
    });
},

}
