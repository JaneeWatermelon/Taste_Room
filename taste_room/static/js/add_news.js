$("input").on("input", function() {
    const Min = Number($(this).attr("min"));
    const Max = Number($(this).attr("max"));
    let my_symbols_span = $(this).parent().siblings().filter(".marks_limits").find(".my_symbols");
    my_symbols_span.html($(this).val().length);
    if ($(this).val().length >= Min && $(this).val().length <= Max) {
        my_symbols_span.addClass("orange");
        my_symbols_span.removeClass("heart");
    } else {
        my_symbols_span.addClass("heart");
        my_symbols_span.removeClass("orange");
    }
})
$("textarea").on("input", function() {
    const Min = Number($(this).attr("minlength"));
    const Max = Number($(this).attr("maxlength"));
    let my_symbols_span = $(this).parent().siblings().filter(".marks_limits").find(".my_symbols");
    my_symbols_span.html($(this).val().length);
    if ($(this).val().length >= Min && $(this).val().length <= Max) {
        my_symbols_span.addClass("orange");
        my_symbols_span.removeClass("heart");
    } else {
        my_symbols_span.addClass("heart");
        my_symbols_span.removeClass("orange");
    }
})

$(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']").on("input", function() {
    const count = $(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']:checked").length;
    $(".edit_section > .categories .categories_count").html(`${count}/10`);

    if (count >= 10) {
      $(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']:not(:checked)").attr("disabled", true);
    } else {
      $(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']").removeAttr("disabled");
    }
});

$(".edit_section > .categories > .categories_list > .title_and_list > .category_item > .first_category > img").on("click", function() {
  
  $(this).siblings().filter("img").toggleClass("d_none");
  $(this).toggleClass("d_none");

  if ($(this).hasClass("plus")) {
    $(this).parent().siblings().filter(".second_categories").removeClass("d_none");
  } else if ($(this).hasClass("minus")) {
    $(this).parent().siblings().filter(".second_categories").addClass("d_none");
  }
})

$(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .delete_and_change > .delete").on("click", function() {

  const item = $(`.edit_section > .ready_dish_photo > .photo_list > .photo_item`);
  
  item.remove();
})

$(document).ready(function () {
    const menuLinks = $('.navigation_section > .links_wrapper > .link_item > h4'); // Все ссылки меню
    const sections = $('.edit_section > .sub_section'); // Все разделы страницы
  
    // Функция для проверки видимости раздела
    function isSectionInViewport(section) {
      const rect = section.getBoundingClientRect();
      return (
        rect.top <= $(window).height() / 2 && // Раздел находится выше середины экрана
        rect.bottom >= $(window).height() / 2 // Раздел находится ниже середины экрана
      );
    }
  
    // Функция для обновления активного пункта меню
    function updateActiveMenu() {
      sections.each(function (index, section) {
        if (isSectionInViewport(section)) {
          // Удаляем класс `current` у всех пунктов меню
          menuLinks.removeClass('current');
          // Добавляем класс `current` к соответствующему пункту меню
          menuLinks.eq(index).addClass('current');
        }
      });
    }
  
    // Отслеживаем прокрутку страницы
    $(window).on('scroll', updateActiveMenu);
  
    // Вызываем функцию при загрузке страницы
    updateActiveMenu();
  });