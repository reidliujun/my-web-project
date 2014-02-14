$(document).ready(function() {
	$('.carousel').carousel({
       interval: false
   	});


    //Detection whether the input album title is already existed or not.
    $( "#albumadd_title" ).focusout(function(){
    	var value = $('#albumadd_title').val();
	     if (value != ""){
	        $.ajax({
	            type: "POST",
	            url:"/album_form/",
	            data: {'title': value}
	        })
	        .done(function(data){
            // alert(data.status);
	            if(data.status=="confilct"){
	              $('#result1')[0].innerHTML="Album title conflicts, choose another title!";
	            }
              else if(data.status=="Special symbols"){
                $('#result1')[0].innerHTML="Please input title without space and symbols!";
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

   
    // image draggable feature, below code is referred from: http://jsfiddle.net/circle73/gqSaq/3/
        // image deletion function


    // there's the gallery and the trash
    var $gallery = $( ".gallery" );
    var $trash = $( "#trash");
    var $trash1 = $( "#trash1");
    var $trash2 = $( "#trash2");
    var $trash3 = $( "#trash3");
    var $trash4 = $( "#trash4");
    var $trash5 = $( "#trash5");

    function deleteImage( $item ) {
      $item.fadeOut(function() {
        var $list = $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash );
        $item.appendTo( $list ).fadeIn(function() {
          $item
            .animate({ width: "400px" })
            .find( "img" )
              .animate({ height: "300px" });
        });
      });
    }
    function deleteImage1( $item ) {
      $item.fadeOut(function() {
        var $list = $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash1 );
        $item.appendTo( $list ).fadeIn(function() {
          $item
            .animate({ width: "180px" })
            .find( "img" )
              .animate({ height: "140px" });
        });
      });
    }
    function deleteImage2( $item ) {
      $item.fadeOut(function() {
        var $list = $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash2 );
        $item.appendTo( $list ).fadeIn(function() {
          $item
            .animate({ width: "180px" })
            .find( "img" )
              .animate({ height: "140px" });
        });
      });
    }
    function deleteImage3( $item ) {
      $item.fadeOut(function() {
        var $list = $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash3 );
        $item.appendTo( $list ).fadeIn(function() {
          $item
            .animate({ width: "180px" })
            .find( "img" )
              .animate({ height: "140px" });
        });
      });
    }
    function deleteImage4( $item ) {
      $item.fadeOut(function() {
        var $list = $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash4 );
        $item.appendTo( $list ).fadeIn(function() {
          $item
            .animate({ width: "180px" })
            .find( "img" )
              .animate({ height: "140px" });
        });
      });
    }

    function deleteImage5( $item ) {
      $item.fadeOut(function() {
        var $list = $( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash5 );
      });
    }

    // image recycle function
    function recycleImage( $item ) {
      $item.fadeOut(function() {
        $item
          .css( "width", "96px")
          .find( "img" )
            .css( "height", "72px" )
          .end()
          .appendTo( $gallery )
          .fadeIn();
      });
    }

    // let the gallery items be draggable
    $( "li", $gallery ).draggable({
      cancel: "a.ui-icon", // clicking an icon won't initiate dragging
      revert: "invalid", // when not dropped, the item will revert back to its initial position
      containment: "document",
      helper: "clone",
      cursor: "move"
    });

    // let the gallery be droppable as well, accepting items from the trash
    $gallery.droppable({
      accept: ".trash li",
      activeClass: "custom-state-active",
      drop: function( event, ui ) {
        recycleImage( ui.draggable );
        var img_id=ui.draggable.attr("id");
        //ajax to clear the image from the model
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'clear', 'id': img_id}
        })
        .done(function(data){
            // alert(data.status);
        });
      }
    });

    // let the trash be droppable, accepting the gallery items
    $trash.droppable({
      accept: "#gallery > li",
      activeClass: "ui-state-highlight",
      drop: function( event, ui ) {

        deleteImage( ui.draggable );
        // $trash.droppable( "option", "disabled", true );
        var img_id=ui.draggable.attr("id");
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'set', 'id': img_id}
        })
        .done(function(data){
          if(data.status!="OK"){
            alert("try again!");
          }
      });
      }
    });

    $trash1.droppable({
      accept: "#gallery > li",
      activeClass: "ui-state-highlight",
      drop: function( event, ui ) {

        deleteImage1( ui.draggable );
        // $trash1.droppable( "option", "disabled", true );
        var img_id=ui.draggable.attr("id");
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'set', 'id': img_id}
        })
        .done(function(data){
            if(data.status!="OK"){
            alert("try again!");
          }
        });
        
      }
    });

    $trash2.droppable({
      accept: "#gallery > li",
      activeClass: "ui-state-highlight",
      drop: function( event, ui ) {

        deleteImage2( ui.draggable );
        // $trash2.droppable( "option", "disabled", true );
        var img_id=ui.draggable.attr("id");
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'set', 'id': img_id}
        })
        .done(function(data){
            if(data.status!="OK"){
            alert("try again!");
          }
        });
        
      }
    });

    $trash3.droppable({
      accept: "#gallery > li",
      activeClass: "ui-state-highlight",
      drop: function( event, ui ) {

        deleteImage3( ui.draggable );
        // $trash3.droppable( "option", "disabled", true );
        var img_id=ui.draggable.attr("id");
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'set', 'id': img_id}
        })
        .done(function(data){
            if(data.status!="OK"){
            alert("try again!");
          }
        });
        
      }
    });

    $trash4.droppable({
      accept: "#gallery > li",
      activeClass: "ui-state-highlight",
      drop: function( event, ui ) {

        deleteImage4( ui.draggable );
        // $trash4.droppable( "option", "disabled", true );
        var img_id=ui.draggable.attr("id");
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'set', 'id': img_id}
        })
        .done(function(data){
            if(data.status!="OK"){
            alert("try again!");
          }
        });
        
      }
    });

    $trash5.droppable({
      accept: "#gallery > li",
      activeClass: "ui-state-highlight",
      drop: function( event, ui ) {

        deleteImage5( ui.draggable );
        var img_id=ui.draggable.attr("id");
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: {'setting':'delete', 'id': img_id}
        })
        .done(function(data){
            if(data.status!="OK"){
            alert("try again!");
          }
        });
        
      }
    });



});