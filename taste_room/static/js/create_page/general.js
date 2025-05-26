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

$('textarea').each(function () {
    $(this).val($.trim($(this).val()));
});