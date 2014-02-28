/* Namespace Spread */ spread = {

submitSpread:function(event){
	event.preventDefault();
	$.ajax({
		url:'spread/spread',
		type:'POST',
		data:{'content':$('#spreadtext').val()},
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){
			$.get('twitter/post',{'content':$('#spreadtext').val()},function(data){});
			$.get('facebook/post',{'content':$('#spreadtext').val()},function(data){});
			$.fn.showMosaic();
		}
	});
},

submitImage:function(event){
	event.preventDefault();
},

showSpreadable:function(event){
	event.preventDefault();
	var spread_id = $('.id',this).text().trim();
	$.get('spread/spreadable',{'id':spread_id},function(data){
		$('#Espaco').html(data).modal();
		$.fn.eventLoop();
	});
},

showImage:function(event){
	event.preventDefault();
	var image_id = $('.id',this).text().trim();
	$.get('spread/image',{'id':image_id},function(data){
		$('#Espaco').html(data).modal();
		$.fn.eventLoop();
	});
},

spreadSpread:function(event){
	event.preventDefault();
	var object_id = $('#Espaco .id').text().trim();
	$.get('spread/spreadspread',{'id':object_id},function(data){
		$('.spreadcontent').html(data);
		$('.send').removeClass('spread')
		.addClass('objectspread');
		$.fn.eventLoop();
	});
},

spreadObject:function(event){
	event.preventDefault();
	var object_id = $('#Espaco .id').text().trim();
	var object_token = $('#Espaco .token').text().trim();
	$.ajax({
		url:'spread/spreadspread',
		type:'POST',
		data:{
			'id':object_id,
			'token':object_token,
			'content':$('#spreadtext').val(),
		},
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){
			$.fn.showMosaic();
		}
	});
},

showSpreaded:function(event){
	event.preventDefault();
	var spreaded_id = $('.spreadedid',this).text().trim();
	var spreaded_token = $('.spreadedtoken',this).text().trim();
	$.ajax({
		url:'spread/spreaded',
		data:{ 
			'spreaded_id':spreaded_id,
			'spreaded_token':spreaded_token
		},
		beforeSend: function(){ $.fn.Progress('Carregando comentários') },
		success:function(data){ 
			$('#Grade').Mosaic(data);
			$.fn.eventLoop();
		}
	});
},

}
/* Namespace Play */ play = {

submitVideoInfo:function(event){
	event.preventDefault();
	$.get('spread/expose',$('#conteudo').serialize()+'&category=0'+'&credit=0',function(data){
		$('.form').html(data);
		$('.send')
		.removeClass('postspread eventspread videospread listspread')
		.addClass('uploadspread')
		$.fn.eventLoop();
	});
},
		
submitPlay:function(event){
	event.preventDefault();
	$.post('spread/content',{},function(data){
		$.fn.hideMenus(); 
		$('#Grade').Mosaic(data);
		$.fn.eventLoop();
	});
},

hidePlayable:function(event){
	$('#Player').tubeplayer('destroy');
	$('#Espaco').removeClass('player');
},

showPlayable:function(event){
	event.preventDefault();
	var playable_id = $('.id',this).text().trim();
	var href = $(this).attr('href');
	$.get('spread/playable',{'id':playable_id},function(data){
		$('#Espaco').html(data).modal().addClass('player');
		$('.modal-body').addClass('player-height video');
		$.e.playerOpt['initialVideo'] = $.e.lastVideo = href;
		$.e.playerOpt['width'] = 770; $.e.playerOpt['height'] = 350;
		$("#player").tubeplayer($.e.playerOpt);
		$.fn.eventLoop();
	});
},

playNext:function(){
	$.e.position++;
	if($.e.position < $.e.videos.length){
		href = $.e.videos[$.e.position];
		$('#Player').empty().tubeplayer('destroy');
		$.e.playerOpt['initialVideo'] = href;
		$.e.playerOpt['onPlayerEnded'] = function(){ play.playNext($.e.position); };
		$('#Player').tubeplayer($.e.playerOpt);	
	}else{
		$.e.position = 0;
		play.playAgain();
	}
},

playlistObject:function(event){
	event.preventDefault();
	$('.playable,.causable').each(function(){ $.e.videos.push($(this).parent().attr('href')); });
	href = $.e.videos[0]
	$.get('templates/player.html',function(data){
		$('#Espaco').Window(data);
		$('#Espaco').css({'width':800,'height':500});
		$.e.playerOpt['initialVideo'] = $.e.lastVideo = href;
		$.e.playerOpt['onPlayerEnded'] = function(){ play.playNext($.e.position); };
		$('.player,.general').addClass($.e.control);
		$("#Player").tubeplayer($.e.playerOpt);
		$('#Espaco').on('dialogclose',function(event,ui){ $('#Player').tubeplayer('destroy'); });
		$('#Espaco').dialog('option','position','center');
		$.fn.eventLoop();
	});
},

play:function(event){
	event.preventDefault();
	$(this).removeClass('play').addClass('pause');
	$(this).html('<span class="ui-icon ui-icon-pause" > </span></a>');
	$('#Player').tubeplayer('play');
	$.fn.eventLoop();
},

pause:function(event){
	event.preventDefault();
	$(this).removeClass('pause').addClass('play');
	$(this).html('<span class="ui-icon ui-icon-play" > </span></a>');
	$('#Player').tubeplayer('pause'); 
	$.fn.eventLoop();
},

mute:function(event){
	event.preventDefault();
	$(this).removeClass('mute').addClass('unmute');
	$(this).html('<span class="ui-icon ui-icon-volume-on" > </span>');
	$('#Player').tubeplayer('mute');
	$.fn.eventLoop();
},

unmute:function(event){
	event.preventDefault();
	$(this).removeClass('unmute').addClass('mute');
	$(this).html('<span class="ui-icon ui-icon-volume-off" > </span>');
	$('#Player').tubeplayer('unmute');
	$.fn.eventLoop();
},

replay:function(event){
	event.preventDefault();
	$('#Player').empty().tubeplayer('destroy');
	$('#Message').hide();
	$('#Player').tubeplayer($.e.playerOpt);
	$('#Player,.player').show();
},

getVideoInformation:function(event){
	event.preventDefault();
	if($('.price').length) price = $('.price').val();
	else price = 'none';
	$.get('spread/expose',$('#conteudo').serialize()+'&category='+$.e.option+'&price='+price,function(data){
		$('#conteudo').parent().html(data);
		$('#overlay').hide();
		$.fn.eventLoop();
	});
},

submitContent:function(event){
	event.preventDefault();
	$('#conteudo').submit();
},

progressHandlingFunction:function(e){
    if(e.lengthComputable) $('progress').attr({value:e.loaded,max:e.total});
},

uploadProgress:function(){
	$('#overlay').css({ height: $('#upload').height() });
	$('#overlay').show();
	myXhr = $.ajaxSettings.xhr();
	if(myXhr.upload) myXhr.upload.addEventListener('progress',$.fn.progressHandlingFunction,false);
	return myXhr;
},

finishUpload:function(data){
	$.e.token = data;
	$('#overlay').find('p').html('Upload concluído.');
	$('#Espaco').dialog('close');
	$.ajax({
		url:'/',
		data:{'feed':'feed'},
		beforeSend:function(){ $('#Espaco').Progress(); },
		success:function(data){
			$('#Grade').Mosaic(data);
			$.fn.eventLoop();
		}
	});
	$.get('known',{'info':'user'},function(data){$('#Esquerda').html(data);}); 
},

fan:function(event){
	event.preventDefault();
	$.ajax({
		url:'spread/fan',
		data:{'text':$('#Espaco').find('.time').text()},
		beforeSend:function(){ $('#Espaco').Progress(); },
		success:function(data){
			$('#Grade').Mosaic(data);
			$('#Espaco').dialog('close');
			$.fn.eventLoop();
		}
	});
},

}


/* Namespace Store */ store = {
openProduct:function(event){
    event.preventDefault();
    $.ajax({
        url:'spread/products',
        data:{'product':$(this).find('.id').text().trim()},
        success:function(data){
            $('#Espaco').Window(data);
            $.fn.eventLoop();
        }
    });
},

submitProduct:function(event){
    event.preventDefault();
    $.post('spread/products',$('#product').serialize(),function(data){
        $('.modal-body').html(data);
        $.e.uploadOpt['url'] = $('#image').attr('action'); 
		$('.upload,.file').fileUpload($.e.uploadOpt);
        $.fn.eventLoop();
        //$('#Espaco').empty().dialog('destroy');
    });
},

showProducts:function(event){
    event.preventDefault();
    $.ajax({
        url:'spread/products',
        beforeSend:function(){ $('#Espaco').Progress(); },
        success:function(data){ $('#Grade').loadMosaic(data); }
    });
},

showMoreProducts:function(event){
    event.preventDefault();
    $.ajax({
        url:'spread/products',
        data:{'more':'more'},
        beforeSend:function(){ $('#Espaco').Progress(); },
        success:function(data){ $('#Grade').loadMosaic(data); }
    });
},

}
