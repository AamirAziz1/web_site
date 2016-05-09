var timeout	= 1000;
var closetimer	= 1000;
var ddmenuitem	= 0;



// open hidden layer
function mopen(id,sid)
{
	// cancel close timer
	mcancelclosetime();
	if(ddmenuitem) ddmenuitem.style.visibility = 'hidden';
	// get new layer and show it
    ddmenuitem = document.getElementById(id);
	// close old layer
	$(".draw-two").css("opacity","0")
	if (ddmenuitem.style.visibility == 'visible'){
	    ddmenuitem.style.visibility = 'hidden';
	}else{
        $("a.draw-link").css("opacity","0.4")
        $("a.draw-link").css("transition","opacity .3s ease-in-out")
        $(".draw-two").css("opacity","1")
        document.getElementById(sid).style.opacity = '1';
        ddmenuitem.style.visibility = 'visible';
	}
}
// close showed layer
function mclose()
{
	if(ddmenuitem) ddmenuitem.style.visibility = 'hidden';
	$("a.draw-link").css("opacity","1")
	$(".draw-two").css("opacity","0")
	$("a.draw-link").css("transition","opacity .3s ease-in-out")
}

// go close timer
function mclosetime()
{
	closetimer = window.setTimeout(mclose, timeout);
}

// cancel close timer
function mcancelclosetime()
{
	if(closetimer)
	{
		window.clearTimeout(closetimer);
		closetimer = null;
	}
}
// close layer when click-out
//function click_close(){
//
//    document.getElementById("m1").style.visibility = 'hidden';
//    document.getElementById("m2").style.visibility = 'hidden';
//    document.getElementById("m3").style.visibility = 'hidden';
//	$("a.draw-link").css("opacity","1")
//	$(".draw-two").css("opacity","0")
//	$("a.draw-link").css("transition","opacity .3s ease-in-out")
//};
//$(document).ready(function(){
//    console.info('ss');
//    if (document.getElementById("m1").style.visibility == 'hidden') return;
//    if (document.getElementById("m2").style.visibility == 'hidden') return;
//    if (document.getElementById("m3").style.visibility == 'hidden') return;
//    $(document).bind('click', Hide);
//});
//function Hide(e){
//    if($(e.target)[0].id =="m1")
//        return;
//    $("#m1").hide();
//    switch($(e.target)[0].id){
//        case "m1":
//            return
//            break;
//        case "m2":
//            return
//            break;
//        case "m3":
//            return
//            break;
//        default:
//            click_close();
//    }
//}