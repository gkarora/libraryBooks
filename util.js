$(document).on("pageshow", "#chart",function(){    
  displayChart();


  $("#dataEntry").bind("popupbeforeposition", function(){
      setDefaultDD();
  });

  $("#renewData").bind("popupbeforeposition", function(){
    setDefaultDD();
    $("#cancelRenew").on("click", function(){
        $("#renewData").popup("close"); 
        $("#bookRecord").popup("open");      
    });
    $("#submitDate").on("click", function(){
      $.ajax({
          url: "/datachart.html",
          type: "UPDATE",
          data: {newDate : $("#dateNew").val(),
                  idb : $(".nameOfBook").data("idb")},
          success: function (){
              $("#renewData").popup("close");
              location.hash="";
              location.reload(true);
          },
          failure: function() {console.log("NO");},
      });
    });
  });

  $("#bookRecord").bind("popupbeforeposition", function(){
    $("#return").on("click", function(){
      $.ajax({
        url: "/datachart.html",
        type: "DELETE",
        data: {id:$("#bookRecord .nameOfBook").data("idb")},
        success: function(){
                  $("#bookRecord").popup("close");
                  location.hash="";
                  location.reload(true);    
                 },
        failure: function(){console.log("fail");},
      });
    });
  });
});

function displayChart(){
  $.get('/data.txt', function(data){
  lines = data.split("\n");
    $.each(lines, function(n, elem) {
    arr = elem.split(', ');
    if (arr[1] != undefined) {
        idb= arr[0];	
        book= arr[1];	    
        day = arr[2];

        $("ul").append(
          "<li class='ui-btn ui-btn-icon-right ui-icon-carat-r book' data-id="
          + idb +"><a><h2>"+ book + "</h2><p class='ui-li-desc'>" + 
	  getDayString(day) + "</p></a></li>");
        status = getStatus(day);
        $("li").last().data('status', status);
	if (status=="Due Soon")
          $("li").last().attr('data-theme', 'e');
        else if (status =="Due Today")
	  $("li").last().addClass('dueToday');
	else if (status == "Overdue")
	  $("li").last().addClass('overdue');
      }
    });
  
    $(".book").click(function(){
      $("#bookRecord").popup("open");
      idb=this.getAttribute("data-id");
      bookName=this.getElementsByTagName("h2")[0].innerHTML;
      $(".nameOfBook").empty();
      $(".nameOfBook").append(bookName).data("idb", idb);

      dueDate=this.getElementsByTagName("p")[0].innerHTML;
      status = $(this).data('status');
      $("#status").empty();
      $("#status").append(status); 
    });
    $("ul").listview('refresh'); 
  });
}

function getDayString(d){
    day = d.split('-');
    dd = new Date(day[0], day[1]-1, day[2]);
    return dd.toDateString();
}

function setDefaultDD(){
  today=getDefaultDD();
  $(".date").val(today[0] + '-' + today[1] + '-'+ today[2]);
}

function getDefaultDD(){	
  date = new Date();
  date.setDate(date.getDate()+14);
  d = date.getDate();
  m = date.getMonth()+1;
  y = date.getFullYear();

  if(m < 10) 
    m = "0" + m;
  if(d < 10) 
    d = "0" + d;
  
  return [ y, m, d];
}

function getStatus(dueDate){
  t = new Date()
  t = Date.parse(t.toDateString());

  duestr = getDayString(dueDate[0]+ '-' + dueDate[1] + '-' + dueDate[2]);
  due = Date.parse(duestr);
  dd = new Date(due);

  tdd = new Date();
  threeDaysMS = 3*24*60*60*1000;
  tdd = dd.getTime()-threeDaysMS;

  if (t>due)
    return "Overdue";
  else if (t == due)
    return "Due Today";
  else if (t >= tdd)
    return "Due Soon";
  else 
    return "Borrowed";
}      

