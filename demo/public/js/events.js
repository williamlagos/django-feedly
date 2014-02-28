$.fn.clearEvents = function(){
	$('.app').off('click');
	$('.page').off('click');
	$('.login').off('click');
	$('.logout').off('click');
	$('.register').off('click');
	$('.option').off('click');
	$('.upload').off('click');
	$('.procfg').off('click');
	$('.placecfg').off('click');
	$('.change').off('click');
	$('.integration,.social,.redirect').off('click');
	$('.deletable').off('click');
	$('.submit').off('click');
	$('.explore').off('submit');
	$('.brand').off('click');
	$('.next').off('click');
	$('.following').off('click');
	$('.profile').off('click');
	$('.unfollow').off('click');
	$('.unfollow').off('hover');
	$('.follow').off('click');
	$('.cancelpurchase').off('click');
	$('.deliver').off('click');
	$('.payment').off('click');
	$('.cartmore').off('click'); 
	$('.cart').off('click');
	$('.buyable').off('click');
	$('.calculate').off('click');
	$('.purchase').off('click');
	$('.passwordchange').off('click');
	$('.admin').off('click');
	$('.cartclean').off('click');
	$('.finish').off('click')
}

$.fn.eventLoop = function () {
    $.fn.clearEvents();
	$('a').on('click',function(){ this.blur(); });
	$('.app').on('click',$(this).showContext);
	$('.page').on('click',$(this).showPage);
	$('.login').on('click',$.fn.authenticate);
	$('.logout').on('click',$.fn.logout);
	$('.register').on('click',$.fn.showParticipate);
	$('.option').on('click',$(this).changeOption);
	$('.upload').on('click',$.fn.input);
	$('.procfg').on('click',$.fn.submitChanges);
	$('.placecfg').on('click',$.fn.submitPlace);
	$('.change').on('click',$.fn.doNothing);
	$('.integration,.social,.redirect').on('click',$(this).redirect);
	$('.deletable').on('click',$.fn.deleteObject);
	$('.submit').on('click',function(event){ $('form').tosubmit(event); });
	$('.explore').on('submit',$(this).submitSearch);
	$('.brand').on('click',$.fn.reloadMosaic);
	$('.next').on('click',$.fn.nextTutorial);
	$('.following').on('click',$.fn.showFollowing);
	$('.profile').on('click',$.fn.showProfile);
	$('.unfollow').on('click',$.fn.unfollow);
	$('.unfollow').on('hover',$.fn.unfollowHover);
	$('.follow').on('click',$.fn.follow);
	$('.cancelpurchase').on('click',$.fn.cancelPurchase);
	$('.deliver').on('click',$.fn.calculateDelivery);
	$('.payment').on('click',$.fn.pay);
	$('.cartmore').on('click',$.fn.addtoBasket); 
	$('.cart').on('click',$.fn.showBasket);
	$('.buyable').on('click',$.fn.buyCoins);
	$('.calculate').on('click',$.fn.calculatePrice);
	$('.purchase').on('click',$.fn.openDeliverable);
	$('.passwordchange').on('click', $.fn.submitPasswordChange);
	$('.admin').on('click', $.fn.gotoAdmin);
	$('.cartclean').on('click',$.fn.cleanBasket);
	$('.finish').on('click',$.fn.finishTutorial)
}

$.fn.mainLoop = function(){
    $.e.buttons += ' procfg imgcfg placecfg socialcfg ';
    $.fn.eventLoop();
}
