$.fn.Mosaic = function(data){
	/* Mosaic (Feed data)
	 * Function for loading the Efforia mosaic
	 */
	if($('.masonry').length > 0) 
	    $(this).masonry('destroy').infinitescroll('destroy').data('infinitescroll', null);
	$('.brick:not(.stamp)').remove();
	$('#Progresso').hide();
	$(this).append(data).imagesLoaded(function(){
		$(this).masonry({
			itemSelector: '.brick',
			position: 'relative',
			isAnimated: true,
			gutter: 1
		}).infinitescroll({
		    navSelector  : '.pagination',            
		    nextSelector : '.next',
		    itemSelector: '.brick',
            stamp: '.stamp',
		    path:function(number) { return ($('.navigation').attr('href') + '?page=' + number); },
		    loading:{
		    	img:'',
		    	msg:null,
		    	msgText:'',
		    	finishedMsg:'',
		    	},
			},function(elements){
				var $elems = $(elements).css({'opacity':0});
				$elems.imagesLoaded(function(){
	                $elems.animate({'opacity': 1});
	                $('#Grade').masonry('appended',$elems,true);
	                $.fn.eventLoop();
	            });
			}
		);
	});
}

$.fn.Window = function(data){
	/* Window (Modal data)
	 * Function for loading Bootstrap windows
	 */
	$(this).empty().html(data);
	$(this).modal('show');
}

$.fn.Progress = function(message){
	/* Progress (Progress message)
	 * Function for showing progress gif
	 */
	$('#Progresso').show();
	$('#Progresso .message').html(message);
}

$.fn.tosubmit = function(event){
	event.preventDefault();
	$(this).submit();
}

$.fn.input = function(event){
	event.preventDefault();
	$('input:file').click(); 
}

$.fn.redirect = function(event){
	event.preventDefault();
	window.location = $(this).attr('href');
}

$.fn.doNothing = function(event){
	event.preventDefault();
}

$.fn.logout = function(event){
	event.preventDefault();
	$.get('/efforia/leave',{},function(data){
		console.log(data);
		window.location = '/';
	});
}

$.fn.authenticate = function(event){
	event.preventDefault();
	$.ajax({
		url:'/efforia/enter', 
		data:$('#login').serialize(),
		beforeSend:function(){$('.login').button('loading');},
		success:function(data){
			return window.location = '/';
		}
	});
}

$.fn.gotoAdmin = function (event) {
    event.preventDefault();
    window.location = '/admin/';
}

$.fn.destroyMosaic = function(){
	$(this).masonry('destroy')
	.infinitescroll('pause')
	.data('infinitescroll', null);
}

$.fn.cleanBasket = function(event){
    event.preventDefault();
    $.get('efforia/basketclean',{},function(data){
    	window.location = '/';
    });
}

$.fn.generateButtons = function(name,value,qty){
    var paypal_button = "<div class='paypal hidden'></div>"
    var pagseguro_button = "<div class='pagseguro hidden'></div>"
    $(this).html(paypal_button+pagseguro_button);
    $.get('/efforia/paypal',{'product':name,'value':value,'qty':qty},function(data){
        $('.paypal').html(data).removeClass('hidden');
        $('.paypal input[name=submit]').attr('src','/static/img/paypal.png').addClass('btn btn-info').css({'width':'70%'});
    });
    $.get('/efforia/pagseguro',{'product':name,'value':value,'qty':qty},function(data){
        $('.pagseguro').html(data).removeClass('hidden');
        $('.pagseguro input[name=submit]').attr('src','/static/img/pagseguro.png').addClass('btn btn-success').css({'width':'70%'});
    });
}

$.fn.createPayments = function(){
    $.get('/efforia/paypal/cart',{},function(data){
        $('.paypal').html(data).removeClass('hidden');
        $('.paypal input[name=submit]').attr('src','/static/img/paypal.png').addClass('btn btn-info').css({'margin':'5%','width':'90%'});
    });
    $.get('/efforia/pagseguro/cart',{},function(data){
        $('.pagseguro').html(data).removeClass('hidden');
        $('.pagseguro input[name=submit]').attr('src','/static/img/pagseguro.png').addClass('btn btn-success').css({'margin':'5%','width':'90%'});
    });
}

$.fn.activateSimpleEditor = function(){
	$.e.editorOpt = $.f.simpleEditor;
	$('.wysiwygtxt').wysihtml5($.e.editorOpt);
    $('.wysihtml5-toolbar .btn').addClass('btn-default');
    $('.wysihtml5-sandbox').css({'width':'100%'});
}

$.fn.activateTutorial = function(){ $('.datepicker').datepicker($.e.datepickerOpt); }

$.fn.changeOption = function(event){
	event.preventDefault();
	var next = $(this).attr('next');
	$('li.active').removeClass('active');
	$(this).parent().addClass('active');
	$.get($(this).attr('href'),{},function(data){
		$('.form').html(data);
		$('.send').removeClass().addClass('btn btn-primary send '+next);
		$.e.uploadOpt['url'] = $('#image').attr('action');
		$('.datepicker').datepicker($.e.datepickerOpt);
		$('.upload,.file').fileUpload($.e.uploadOpt);
        $.getJSON('static/json/elements.json',function(data){
            $('.typeahead').typeahead({'source':data['locale_cat']});
            $('.typeahead').css({'z-index':'5000'});
        });
        if($('.wysiwygtxt').length > 0) $.fn.activateSimpleEditor();
		$.fn.eventLoop();
        $.fn.mainLoop();
	});
}

$.fn.showContext = function(event){
	event.preventDefault();
	$.ajax({
		url:$(this).attr('href'),
		success: function (data) {
		    $('#Espaco').empty().removeClass().addClass('modal');
			$('#Espaco').html(data).modal();
			$.get($('.active').attr('href'),{},function(data){
				$('.form').html(data);
				$('.datepicker').datepicker($.e.datepickerOpt);
				$.e.uploadOpt['url'] = $('form').attr('action');
				$('input[type=file]').fileUpload($.e.uploadOpt);
				if($('.wysiwygtxt').length > 0) $.fn.activateSimpleEditor();
				$.fn.eventLoop();
			});
		}
	});
}

$.fn.submitSearch = function(event){
	event.preventDefault();
	$.ajax({
		url:'efforia/explore',
		data:$('.explore').serialize(),
		beforeSend:function(){ $.fn.Progress('Realizando a busca'); },
		success:function(data){
			$('#Grade').Mosaic(data);
			$.fn.eventLoop();
		}
	});
}

$.fn.submitPlace = function(event){
	event.preventDefault();
	$.ajax({
		url:'efforia/place',
		type:'POST',
		data:$('#place').serialize(),
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){
			$('#Espaco').modal('hide');
		}
	});
}

$.fn.submitChanges = function(event){
	event.preventDefault();
	$.ajax({
		url:'efforia/profile',
		type:'POST',
		data:$('#profile').serialize(),
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){
			$('#Espaco').modal('hide');
			return window.location = '/';
		}
	});
}

$.fn.submitPasswordChange = function(event){
	$.ajax({
		url:'efforia/password',
		success:function(data){
			$('#passwordchange').html(data);
			$('#password').attr('value','Alterar senha');
			$('#password').click(function(event){
				event.preventDefault();
				$.ajax({
					url:'efforia/password',
					type:'POST',
					data:$('#passwordform').serialize(),
					beforeSend:function(){
						$('.send').button('loading');
					},
					success:function(data){
						$('#Espaco').modal('hide');
						return window.location = '/';
					}
				});
			});
		}
	});
}

$.fn.deleteObject = function(event){
	event.preventDefault();
	var object_id = $('#Espaco .id').text().trim();
	var object_token = $('#Espaco .token').text().trim();
	$.get('efforia/delete',{'id':object_id,'token':object_token},function(data){ $.fn.showMosaic(); });
}

$.fn.verifyDeadlines = function(){
	$.ajax('efforia/deadlines',{},function(data){});
}

$.fn.showMosaic = function(){
	$('#Espaco').modal('hide');
	$.ajax({
		url:'efforia/mosaic',
		beforeSend:function(){ $.fn.Progress('Carregando seu mosaico inicial');	},
		success:function(data){
			$('#Grade').Mosaic(data);
			$.fn.eventLoop();
		}
	}); 	
}

$.fn.showFollowing = function(event){
	event.preventDefault();
	var profile_id = $('.id','.profilehead').text().trim();
	$.ajax({
		url:'efforia/following',
		data:{'profile_id':profile_id},
		beforeSend:function(){ $.fn.Progress('Vendo quem est�� seguindo'); },
		success:function(data){
			$('#Grade').Mosaic(data);
			$.fn.eventLoop();
		}
	});
}

$.fn.unfollow = function(event){
	event.preventDefault();
	var profile_id = $('.id','.profilehead').text().trim();
	$.ajax({
		url:'efforia/unfollow',
		data:{'profile_id':profile_id},
		beforeSend:function(){ $('.send').button('loading'); },
		success:function(data){
			window.location = '/';
		}
	});
}

$.fn.unfollowHover = function(event){
	event.preventDefault();
	if($.e.unfollow == false){
		$.e.unfollow = true;
		$('.unfollow')
		.removeClass('btn-success')
		.addClass('btn-danger')
		.html('Deixar de seguir');
	} else {
		$.e.unfollow = false;
		$('.unfollow')
		.removeClass('btn-danger')
		.addClass('btn-success')
		.html('Seguindo');
	}
}

$.fn.follow = function(event){
	event.preventDefault();
	var profile_id = $('.id','.profilehead').text().trim();
	$.ajax({
		url:'efforia/follow',
		data:{'profile_id':profile_id},
		beforeSend:function(){ $('.follow').button('loading'); },
		success:function(data){
			window.location = '/';
		}
	});
}

$.fn.showProfile = function(event){
	event.preventDefault();
	var profile_id = $('.id',this).text().trim();
	var profile_name = $('.name',this).text().trim();
	$.get('efforia/known',{'profile_id':profile_id},function(data){
		$('.profilename').html(profile_name);
		$('.profilehead').html(data);
		$('.profilebutton').click();
		$.fn.eventLoop();
	});
	$.get('efforia/activity',{'profile_id':profile_id},function(data){
		$('#Grade').Mosaic(data); 
		$.fn.eventLoop(); 
	});
}

$.fn.hideMenus = function(){
	$('#Canvas').css({'opacity':0,'display':'none'});
	$('.back').parent().show('fade');
}

$.fn.showMenus = function(){
	$('.back').parent().hide('fade');
	$('#Canvas').css({'opacity':1,'display':''});
}

$.fn.showPage = function(event){
    event.preventDefault();
    $.ajax({
        url: $(this).attr('href'),
        beforeSend: function(){ $.fn.Progress('Carregando página'); },
        success: function (data) {
            $('#Grade').destroyMosaic();
            $('#Grade').html(data).show();
            $('#Progresso').hide();
            $.fn.eventLoop();
        }
    });
}

$.fn.nextTutorial = function(event){
	event.preventDefault();
	$.post('/efforia/tutorial',$('form').serialize(),function(data){
		console.log(data);
	});
    $.get('/efforia/photo',{},function(data){
        $('.information').html(data);
        $('.next').removeClass('next').addClass('finish').html('Começar');
        $.e.uploadOpt['url'] = '/efforia/photo';
        $.e.uploadOpt['beforeSend'] = function(){ $('.next').button('loading'); },
        $.e.uploadOpt['success'] = function(data){ window.location = '/'; }
        $('.form').fileUpload($.e.uploadOpt);
        $.fn.eventLoop();
    });
}

$.fn.finishTutorial = function(event){
	event.preventDefault();
	$('form').submit();
}

$.fn.participate = function(event){
	event.preventDefault();
	$.post('/efforia/participate',$('.registerview').serialize(),function(data){
		$.get('/efforia/enter',{
				'username':$('.username').val(),
				'password':$('.password').val()
			},function(data){
				window.location = '/efforia/tutorial';
			}
		);
	});
}

$.fn.showBasket = function(event){
    event.preventDefault();
    $.ajax({
        url:'efforia/basket',
        beforeSend:function(){ $('#Espaco').Progress(); },
        success:function(data){ $('#Grade').Mosaic(data); }
    });
}

$.fn.cancelPurchase = function(event){
    event.preventDefault();
    $.post('efforia/cancel',{},function(data){$('#Espaco').empty().dialog('destroy'); $.fn.getInitialFeed();});
}

$.fn.addtoBasket = function(event){
    event.preventDefault();
    $.ajax({
        type:'POST',
        url:'efforia/cart',
        data:{'id':$('#Espaco').find('.id').text().trim()},
        beforeSend:function(){ $('#Espaco').Progress(); },
        success:function(data){ 
            $('#Espaco').modal('hide');
            $('#Grade').Mosaic(data); 
        }
    });
}

$.fn.calculatePrice = function(event){
    event.preventDefault();
    value = ($('#credits').val()*$.e.price).toFixed(2);
    $('#value').attr('value',value);
    store.getRealPrice();
}

$.fn.getRealPrice = function(){
    real_value = $.e.price.toFixed(2);
    $('#payment').children().find('#id_amount').attr('value',real_value);
    $('#payment').children().find('#id_quantity').attr('value',$('#credits').val());
}

$.fn.calculateDelivery = function(event,callback){
    event.preventDefault();
    $.ajax({
        url:'efforia/correios',
        data:{'address':$('#id_address').val(),'object':$('.code').text()},
        beforeSend:function(){ $('.address').html('Pesquisando pelo endere��o, aguarde...'); },
        success:function(data){
            $('.address').html(data);
            $('#payment').find('#id_amount').attr('value',$('.delivery').text());
            callback();
        }
    });
}

$.fn.pay = function(event){
    if($('#id_amount').val() == '1.00'){
        if($('#id_address').val() == ''){
            alert('Defina o destino de sua compra primeiro.');
            event.preventDefault();
        }else{
            store.calculateDelivery(event,function(){ $.post('efforia/payment',{'credit':credits},function(data){$('#payment').find('form').submit();}); });
        }
    }
}

$.fn.openDeliverable = function(event){
    event.preventDefault();
    credits = $('.description').text();
    objects = $('.time')[0].textContent;
    $.ajax({
        url:'efforia/delivery',
        data:{'quantity':$('.title').text(),'credit':credits},
        beforeSend:function(){ $('#Espaco').Progress(); },
        success:function(data){
            button = "<a class=\"deliver\">Calcular frete</a><div class=\"code\" style=\"display:none;\">"+objects+"</div><div class=\"address\"></div>"
            $.fn.showMenus();
            $('#Espaco').Context(data,$('#Canvas').height()-10,$('#Canvas').width()-5);
            $('#Espaco').css({'background':'#222','border-radius':'50px','height':$('#Canvas').height()-20});
            $('.header').html('Compra de Produto');
            $('.tutor').html('Aqui �� poss��vel comprar produtos com os cr��ditos do Efforia. Eles podem ser adquiridos na barra lateral ou no painel de controle do site, localizado logo ao lado da barra de busca. O CEP a ser informado �� neste formato: 00000-000.');
            $('.tutor').css({'margin-top':'5%'});
            $('.image').html('<img src="images/present.png" width="80%" style="margin-left:10%;"/>');
            $('#id_address').parent().append(button);
            $('#payment').find('input[type=image]').attr('width','240');
            $('#payment').find('input[type=image]').attr('src','images/paypal.png');
            $('.deliver').button();
            $('#payment').find('input[type=image]').addClass('payment');
            $.fn.eventLoop();
        }
    });
}

/* Namespace Explore */ explore = {

selectFilter:function(event){
	event.preventDefault();
	if(!$.e.openedMenu){
		$('#Menu').slideDown("slow");
		$.e.openedMenu = true;	
	}else{
		$('#Menu').slideUp("slow");
		$('.lupa').focus();
		$.e.openedMenu = false;
	}
},

submitSearch:function(event){
	event.preventDefault(); 
	all = '';
	query = 'efforia/search?explore='+$('.search-query').val();
	filters = '&filters='
	leastone = false;
	$('.checkbox').each(function(){
		if($(this).css('background-position') == '0px -55px'){
			filters += $(this).parent().text().toLowerCase().replace(/^\s+|\s+$/g,'')+',';
			leastone = true;
		}
		all += $(this).parent().text().toLowerCase().replace(/^\s+|\s+$/g,'')+',';
	});
	if(!leastone) filters += all;
	$.ajax({
		url:query,//+filters,
		beforeSend:function(){ /*$('#Espaco').Progress();*/ },
		success:function(data){
			$.fn.hideMenus();
			$('#Grade').loadMosaic(data);
		}
	});
}

}