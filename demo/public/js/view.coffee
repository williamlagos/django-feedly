document.documentElement.style.overflowX = "hidden"
#document.documentElement.style.overflowY = 'hidden';

$(document).ready ->
  $.ajaxSetup cache: false
  $("input:submit, button", "#botoes").button()
  href = $("#player").attr("href")
  span_width = $(".col-lg-8").width()
  $.e.playerOpt["initialVideo"] = $.e.lastVideo = href
  $.e.playerOpt["width"] = span_width
  $.e.playerOpt["height"] = span_width / 1.7
  $("#player").tubeplayer $.e.playerOpt
  $.fn.eventLoop()