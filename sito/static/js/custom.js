$(document).ready(function(){
  /* ----------------------------------------------------------- */
/*  1. DROPDOWN MENU
/* ----------------------------------------------------------- */

 // for hover dropdown menu
$('ul.nav li.dropdown').hover(function() {
    $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeIn(200);
  }, function() {
    $(this).find('.dropdown-menu').stop(true, true).delay(200).fadeOut(200);
  });

  $("#owl-demo").owlCarousel({
     navigation : false, // Show next and prev buttons
     slideSpeed : 600,
     autoPlay: 5000,
     paginationSpeed : 100,
     singleItem:true,
     mouseDrag: false,
     transitionStyle : "fade",
     pagination:false
       //mouseDrag: false,
      // transitionStyle : "fade"
       //transitionStyle : "fade"

       // "singleItem:true" is a shortcut for:
       // items : 1,
       // itemsDesktop : false,
       // itemsDesktopSmall : false,
       // itemsTablet: false,
       // itemsMobile : false

   });

  $(".submenu > a").click(function(e) {
    e.preventDefault();
    var $li = $(this).parent("li");
    var $ul = $(this).next("ul");

    if($li.hasClass("open")) {
      $ul.slideUp(350);
      $li.removeClass("open");
    } else {
      $(".nav > li > ul").slideUp(350);
      $(".nav > li").removeClass("open");
      $ul.slideDown(350);
      $li.addClass("open");
    }
  });

});
