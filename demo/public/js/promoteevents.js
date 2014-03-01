$.fn.unloadEvents = function () {
    $('.objectpledge').off('click');
    $('.pledge').off('click');
    $('.promoted').off('click');
    $('.movementcreate').off('click');
    $('.keyword').off('click');
    $('.promote').off('click');
    $('.objectpromote').off('click');
    //$('.project').off('click');
    $('.movement').off('click');
    $('.projectcreate').off('click');
    $('.linkcreate').off('click');
    $('.backers').off('click');
    $('.eventcreate').off('click');
    //$('.event').off('click');
    $('.participateevent').off('click');
    $('.enroll').off('click');
}

$.fn.listenEvents = function () {
    $('.objectpledge').on('click', create.transferPledge);
    $('.pledge').on('click', create.pledgeProject);
    $('.promoted').on('click', create.showPromoted);
    $('.movementcreate').on('click', create.submitMovement);
    $('.keyword').on('click', create.selectKeyword);
    $('.promote').on('click', create.promoteProject);
    $('.objectpromote').on('click', create.promoteObject);
    //$('.project').on('click', create.showProject);
    $('.movement').on('click', create.showMovement);
    $('.projectcreate').on('click', create.submitCause);
    $('.linkcreate').on('click', create.submitVideo);
    $('.backers').on('click', create.showBackers);
    $('.eventcreate').on('click', create.submitEvent);
    //$('.event').on('click', create.showEvent);
    $('.participateevent').on('click', create.enrollEvent);
    $('.enroll').on('click',create.showEnroll);
}

$.fn.mainLoop = function(){
    $.fn.unloadEvents();
    $.fn.listenEvents();
}

$(document).ready($.fn.mainLoop);
