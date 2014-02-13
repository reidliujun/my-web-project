$(document).ready(function() {
	$('.carousel').carousel({
       interval: false
   	});

    var upload_photo = function() {
        var img_number = $('img').length;
        // var name = $('#title').attr('title');

        // $('.orderattr').bind('click', function () {
	     if (img_number != 0){
	        $.ajax({
	            type: "POST",
	            url: window.location.pathname,
	            data: {'number': img_number}
	        })
	        .done(function(data){
	            if(data.status=="Image full"){
	              $(".photoadd-form").hide();
	            }
	            else{
	              $(".photoadd-form").show();
	            }
	            
	        });
	     }
	     
    };
    $(".imageadd").hover(function(){
    	
    	var img_number = $('img').length;

     //    // var name = $('#title').attr('title');

     // //    // $('.orderattr').bind('click', function () {
	      if (img_number != 0){
	    	  // alert("test");
	        $.ajax({
	            type: "POST",
	            url: window.location.pathname,
	            // url: "/album/",
	            // url:"/album/liujun/page/3/layout/1/",
	            data: {'number': img_number}
	        })
	        .done(function(data){
	            if(data.status=="Image full"){
	              $(".photoadd-form").hide();
	            }
	            else{
	              $(".photoadd-form").show();
	            }  
	        });
	     }
	 });



    $( "#albumadd_title" ).focusout(function(){
    	var value = $('#albumadd_title').val();
        // var name = $('#title').attr('title');

        // $('.orderattr').bind('click', function () {
	     if (value != ""){
	        $.ajax({
	            type: "POST",
	            url:"/album_form/",
	            data: {'title': value}
	        })
	        .done(function(data){
	            if(data.status=="fail to create"){
	              $('#result1')[0].innerHTML="Album title conflicts, choose another title!";
	            }
	            else{
	              $('#result2')[0].innerHTML="Album title is good!";
	            }
	            
	        });
	     }
	     else{
	     	$('#result1')[0].innerHTML=" ";
	     	$('#result2')[0].innerHTML=" ";
	     }
	 });

    //Make the image draggable
    $(".dragdiv").draggable({
      // cancel: "a.ui-icon", // clicking an icon won't initiate dragging
      revert: "invalid", // when not dropped, the item will revert back to its initial position
      // containment: "document",
      // helper: "clone",
      // cursor: "move"
    });
    $(".photorow").droppable({
    	accept: ".dragdiv",
    	activeClass: "ui-state-hover",
      	hoverClass: "ui-state-active",
      	drop: function( event, ui ) {
      	var title=ui.draggable.attr("id");
        $( this )
          .addClass( "ui-state-highlight" )
      	$.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'clear', 'title': title}
        })
        .done(function(data){
            alert(data.status);
        });
      }
    });
    
    $(".dragarea").droppable({
      accept: ".dragdiv",
      activeClass: "ui-state-hover",
      hoverClass: "ui-state-active",
      // activeClass: "ui-state-highlight",
      // drop: function( event, ui ) {
      //   deleteImage( ui.draggable );
      // }
      drop: function( event, ui ) {
      	var title=ui.draggable.attr("id");
        $( this )
          .addClass( "ui-state-highlight" )
          .html( "Dropped!" );
      	$.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'set', 'title': title}
        })
        .done(function(data){
            alert(data.status);
        });
      }
    });

});