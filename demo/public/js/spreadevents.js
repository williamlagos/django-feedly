$.fn.unloadEvents = function(){
	$('.spreaded').off('click');
	$('.productspread').off('click');
	$('.objectspread').off('click');
	$('.uploadspread').off('click');
	$('.videospread').off('click');
	$('.imagespread').off('click');
	$('.postspread').off('click');
	$('.spreadable').off('click');
	$('.playable').off('click');
	$('.image').off('click');
	$('.spread').off('click');
	$('.product').off('click');
	$('.products').off('click');
	$('.moreproducts').off('click');
}

$.fn.listenEvents = function(){
	$('.spreaded').on('click',spread.showSpreaded);
	$('.productspread').on('click',store.submitProduct);
	$('.objectspread').on('click',spread.spreadObject);
	$('.uploadspread').on('click',play.submitContent);
	$('.videospread').on('click',play.submitVideoInfo);
	$('.imagespread').on('click',spread.submitImage);
	$('.postspread').on('click',spread.submitSpread);
	$('.spreadable').on('click',spread.showSpreadable);
	$('.playable').on('click',play.showPlayable);
	$('.image').on('click',spread.showImage);
	$('.spread').on('click',spread.spreadSpread);
	$('#Espaco').on('hide',play.hidePlayable);
	$('.product').on('click',store.openProduct);
	$('.products').on('click',store.showProducts);
	$('.moreproducts').on('click',store.showMoreProducts);
}

$.fn.mainLoop = function(){
    $.fn.unloadEvents();
    $.fn.listenEvents();
}

$(document).ready($.fn.mainLoop);
