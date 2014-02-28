var CurrentTime = new Date()
var CurrentYear = CurrentTime.getFullYear()-13

var uploader = {
	type:'POST',
	imageMaxWidth:1280,
	imageMaxHeight:720,
	allowUploadOriginalImage:true,
	beforeSend:function(){ $('.send').button('loading'); },
	success:function(data){ window.location = '/'; }
}
var datepick = { 
	format:'dd/mm/yyyy',
	language:'pt-BR' 
}

$.f = {
	simpleEditor:{
		lists:false,
		image:false,
		color:true,
		link:false,
		locale:'pt-BR'
	},
	advancedEditor:{
		lists:true,
		image:true,
		color:true,
		link:true,
		html:true,
		locale:'pt-BR'
	}
}

$.e = {
    buttons:'',
	navigation:'',
	spin:false,
	brand:false,
	unfollow:false,
	editorOpt:{},
	uploadOpt:uploader,
	datepickerOpt:datepick,
	w:window.innerWidth,
	h:window.innerHeight,
	lastObject:'',
	lastId:'',
	marginMax:0,
	angle:0,
	widthNow:$('html').width(),
	heightNow:$('html').height(),
	last:0,
	velocity:0,
	acceleration:50,
	holding:false,
	clicked:false,
	currentTime:CurrentTime,
	selection:false,
	price:1.19,
	option:0,
	token:'',
	objects:[],
	openedMenu:false,
	value:true, 
	marginFactor:10,
	marginTop:0,
	initial:false,
	currentYear:CurrentYear,
	position:0,
	lastVideo:'',
	videos:[],
	playerOpt:{
		// The width of the player
		width: 790, 
		// The height of the player
		height: 430, 
		autoPlay: true,
		showinfo: false,
		autoHide: true,
		iframed: true,
		showControls: 0,
		// Preferred quality: default, small, medium, large, hd720
		preferredQuality: "default",
	}
}