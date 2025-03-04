const new_steps = $('.edit_section > .step_photos > .steps_list > .step_item');
for(let i = 0; i < new_steps.length; i++) {
    $(new_steps[i]).attr("data-order", i+1);
    $(new_steps[i]).find(".action_item").attr("data-order", i+1);
}

// Инициализация SortableJS
const stepsList = $('.edit_section > .step_photos > .steps_list')[0];
const sortable_steps = new Sortable(stepsList, {
    animation: 150, // Анимация перетаскивания
    ghostClass: 'sortable-ghost', // Класс для элемента-призрака
    chosenClass: 'sortable-chosen', // Класс для выбранного элемента
    dragClass: 'sortable-drag', // Класс для перетаскиваемого элемента
    handle: '.move_bar',
    onEnd: function (evt) {
      updateStepsOrder();
    }
});

// Функция для обновления порядка фотографий
function updateStepsOrder() {
    const new_steps = $('.edit_section > .step_photos > .steps_list > .step_item');
    for(let i = 0; i < new_steps.length; i++) {
        $(new_steps[i]).attr("data-order", i+1);
        $(new_steps[i]).find(".action_item").attr("data-order", i+1);
        $(new_steps[i]).find('h3').html(`Шаг ${i+1}`);
    }
}



const new_photos = $('.edit_section > .ready_dish_photo > .photo_list > .photo_item');
for(let i = 0; i < new_photos.length; i++) {
    $(new_photos[i]).attr("data-order", i+1);
    $(new_photos[i]).find(".action_item").attr("data-order", i+1);
}

// Инициализация SortableJS
const photosList = $('.edit_section > .ready_dish_photo > .photo_list')[0];
const sortable_photos = new Sortable(photosList, {
    animation: 150, // Анимация перетаскивания
    ghostClass: 'sortable-ghost', // Класс для элемента-призрака
    chosenClass: 'sortable-chosen', // Класс для выбранного элемента
    dragClass: 'sortable-drag', // Класс для перетаскиваемого элемента
    handle: '.move_bar',
    onEnd: function (evt) {
        updatePhotoOrder();
    }
});

// Функция для обновления порядка фотографий
function updatePhotoOrder() {
    const new_steps = $('.edit_section > .ready_dish_photo > .photo_list > .photo_item');
    for(let i = 0; i < new_steps.length; i++) {
        $(new_steps[i]).attr("data-order", i+1);
        $(new_steps[i]).find(".action_item").attr("data-order", i+1);
    }
}

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


$(".trash_icon").on("click", function() {
  $(this).parent().remove();
})
$(".edit_section > .step_photos > .steps_list > .step_item > .content > .photo_wrapper > .image_wrapper > .delete_and_change > .delete").on("click", function() {
  
  // Удаляем элемент из DOM
  const item = $(`.edit_section > .step_photos > .steps_list > .step_item[data-order=${$(this).attr("data-order")}]`);
  item.css("height", `${item.height()}px`);
  setTimeout(() => {
    item.css("height", 0);
  }, 1);
  item.css("opacity", 0);
  setTimeout(() => {
    item.remove();
    updateStepsOrder();
  }, 300);
})
$(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .delete_and_change > .delete").on("click", function() {
  // Удаляем элемент из DOM
  const item = $(`.edit_section > .ready_dish_photo > .photo_list > .photo_item[data-order=${$(this).attr("data-order")}]`);
  
  if ($(".edit_section > .ready_dish_photo > .photo_list > .photo_item").length > 1) {
    item.css("width", `${item.width()}px`);
    setTimeout(() => {
      item.css("width", 0);
    }, 1);
    item.css("opacity", 0);
    setTimeout(() => {
      item.remove();
      updatePhotoOrder();
    }, 300);
  } else {
    item.remove();
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