if (screen.width <= 720) {
  $(".d_mobile_none").remove();
} else {
  $(".d_desktop_none").remove();
}

let top_waves_height = $('#top_waves').height();
let header_height = $('header').height();
let header_wrapper_height = $('.header_wrapper').height();
let body_gap = Number($("body").css("gap").slice(0, -2));

$("#top_waves").css('height', `${top_waves_height}px`);

$("body").css({
  "padding-top": `${header_height + body_gap}px`,
});
$(".navigation_section").css({
  "top": `${header_height}px`,
});

$(window).on('load', function () {
  $("main").css({
    "opacity": "1",
  });
});

let scrollTimeoutId;
let settedTimeout = false;

$(window).scroll(function () {
  const scrollPosition = $(this).scrollTop();
  const element = $('#top_waves');

  if (scrollPosition > document.querySelector('body').scrollHeight / 4) {
    $("#go_up_wrapper").css({
      "display": "flex",
    });
    setTimeout(function () {
      $("#go_up_wrapper").css("opacity", "1");
    }, 1)
  }
  else {
    $("#go_up_wrapper").css({
      "display": "none",
      "opacity": "0",
    });
  }


  if (scrollPosition > 0) {

    if (!settedTimeout) {
      settedTimeout = true;
      element.css('clip-path', 'inset(0 0 100% 0)');
      scrollTimeoutId = setTimeout(function () {
        $("header > .header_wrapper").css('outline', '3px solid black');
        element.addClass("d_none");
      }, 300);
    }

  } else {

    clearTimeout(scrollTimeoutId);
    settedTimeout = false;


    setTimeout(function () {
      $("header > .header_wrapper").css('outline', 'none');
    }, 300);

    element.removeClass("d_none");
    setTimeout(function () {
      element.css('clip-path', `inset(0 0 0 0)`);
    }, 1);
  }
});