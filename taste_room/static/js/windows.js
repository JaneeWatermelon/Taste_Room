function showBackBlack() {
    $(".back_black").removeClass('d_none');
    setTimeout(function() {
        $(".back_black").css({
            "opacity": 1,
        });
    }, 1);
}
window.hideBackBlack_andPopup = function(popup) {
    $(".back_black").css({
        "opacity": 0, 
    });
    setTimeout(function() {
        $(".back_black").addClass('d_none');
        popup.addClass('d_none');
    }, 300);
}

window.showHideBackBlack = function(event, popup) {
    event.stopPropagation(); // Останавливаем всплытие события, чтобы оно не достигло document
    $(".back_black > *").addClass("d_none");
    if (popup.hasClass('d_none')) {
        popup.removeClass('d_none');
        showBackBlack();
        console.log("if");
    } else {
        console.log("else");
        hideBackBlack_andPopup(popup);
    }
}
window.HideBackBlackOverWindowClick = function(event, popup, hoverEl = null) {
    if (!$(event.target).closest(popup).length && !$(event.target).closest(hoverEl).length) {
        $(".back_black").css({
            "opacity": 0,
        });
        setTimeout(function() {
            $(".back_black").addClass('d_none');
            popup.addClass('d_none');
        }, 300);
    }
}

window.reloadPage = function(pop_up_id, redirect_url=null) {
    sessionStorage.setItem("reloading", pop_up_id);
    if (redirect_url != null) {
        window.location.href = redirect_url;
    }
    else {
        location.reload();
    }
}
$(window).on('load', function(event) {
    var reloading = sessionStorage.getItem("reloading");
    if (reloading) {
        sessionStorage.removeItem("reloading");
        const pop_up = $(`#${reloading}`);
        window.showHideBackBlack(event, pop_up)
    }
});

window.setListenersWithBlackBack = function(popup, hoverEl) {
    // Обработчик клика на элемент, который открывает окно
    hoverEl.on('click', function (event) {
        showHideBackBlack(event, popup);
    });
  
    // Обработчик клика вне окна
    $(document).on('click', function (event) {
        HideBackBlackOverWindowClick(event, popup, hoverEl);
    });
  
    popup.on('click', function (event) {
        event.stopPropagation(); // Останавливаем всплытие события
    });
}

if (window.innerWidth <= 720) {
    $(".profile_window > .overflow_icon").css({
        "top": `-${$(".profile_window > .overflow_icon").height()*2/3}px`,
    });

    const burgerEl = $(".header_buttons > .burger");
    const burgerPop = $('.burger_menu');
    setListenersWithBlackBack(burgerPop, burgerEl);

} else {
    $(".profile_window > .overflow_icon").css({
        "top": `-${$(".profile_window > .overflow_icon").height()/2}px`,
        "left": `-${$(".profile_window > .overflow_icon").height()/2}px`,
    });
}

$(document).ready(function () {

    function updatePopupPositionDesktop(event, popup) {
        const offset = 10;
      
        let left = event.clientX + offset;
        let top = event.clientY + offset;
      
        popup.css({
            left: `${left}px`,
            top: `${top}px`,
        });
    }
    function updatePopupPositionMobile(event, popup) {
        const offset = 10;

        popup.css({
            opacity: 0,
        });
        popup.removeClass("d_none");

        let left = event.clientX - popup.width()/2 - offset;
        let top = event.clientY - popup.height() - 30;
        
        popup.css({
            left: `${left}px`,
            top: `${top}px`,
            opacity: 1,
        });
    }

    let timeoutId;

    function setListenersDesktop(popup, hoverEl) {
        hoverEl.on('mouseenter', function (event) {
            updatePopupPosition(event, popup);
            timeoutId = setTimeout(function() {
                popup.removeClass("d_none");
            }, 500)
        });
        hoverEl.on('mouseleave', function () {
            clearTimeout(timeoutId);
            popup.addClass("d_none");
        });
        hoverEl.on('mousemove', function (event) {
            updatePopupPosition(event, popup);
        });
    }

    let setListeners;
    let updatePopupPosition;

    // Обработчик скроллинга
    $(window).on('scroll', function () {
        $(".pop_up_window").addClass('d_none');
        $(".pop_up_share").addClass("d_none");
    });
    
    function setListenersMobile(popup, hoverEl) {
        // Обработчик клика на элемент, который открывает окно
        hoverEl.on('click', function (event) {
            event.stopPropagation(); // Останавливаем всплытие события, чтобы оно не достигло document
            $(".pop_up_window").addClass('d_none');
            if (popup.hasClass('d_none')) {
                updatePopupPosition(event, popup);
                popup.removeClass('d_none');
            } else {
                popup.addClass('d_none');
            }
        });
      
        // Обработчик клика вне окна
        $(document).on('click', function (event) {
            if (!$(event.target).closest(popup).length && !$(event.target).closest(hoverEl).length) {
                popup.addClass('d_none');
            }
        });
      
        // Обработчик клика внутри окна (чтобы окно не закрывалось при клике внутри него)
        popup.on('click', function (event) {
            event.stopPropagation(); // Останавливаем всплытие события
        });
    }

    if (window.innerWidth <= 720) {
        setListeners = setListenersMobile;
        updatePopupPosition = updatePopupPositionMobile;
    } else {
        setListeners = setListenersDesktop;
        updatePopupPosition = updatePopupPositionDesktop;
    }


    const backFonEl = $(".profile_header .settings > .settings_item.change_fon");
    const backFonPop = $('.back_black > .profile_window.back_fon');
    setListenersWithBlackBack(backFonPop, backFonEl);



    
    window.setCardIngredientAndCooktimeWindows = function() {
        const cookTimeLongEl = $('.recipe_item_long .recipe_item_body > .info > .calories_and_time > .time');
        const cookTimeEl = $('.recipe_item > .recipe_item_header > .info > .time');

        cookTimeEl.each(function() {
            const element = $(this);
            const data_id = element.attr("data-id");
            const cookTimePop = $(`.pop_up_window.cook_time_window[data-id=${data_id}]`);
            setListeners(cookTimePop, element);
        });
        cookTimeLongEl.each(function() {
            const element = $(this);
            const data_id = element.attr("data-id");
            const cookTimeLongPop = $(`.pop_up_window.cook_time_window[data-id=${data_id}]`);
            setListeners(cookTimeLongPop, element);
        });

        const ingredientsLongEl = $('.recipe_item_long > .recipe_item_header > .image_wrapper .back_image');
        const ingredientsEl = $('.recipe_item > .recipe_item_header > .image_wrapper .back_image');

        ingredientsEl.each(function() {
            const element = $(this);
            const data_id = element.attr("data-id");
            const ingredientsPop = $(`.pop_up_window.ingredients_window[data-id=${data_id}]`);
            setListeners(ingredientsPop, element);
        });
        ingredientsLongEl.each(function() {
            const element = $(this);
            const data_id = element.attr("data-id");
            const ingredientsLongPop = $(`.pop_up_window.ingredients_window[data-id=${data_id}]`);
            setListeners(ingredientsLongPop, element);
        });
    }

    window.setCardIngredientAndCooktimeWindows();

    window.setCardShareWindows = function() {
        const shareCardNewsEl = $('.news_item > .news_item_footer .share_button');
        const shareCardRecipeEl = $('.recipe_item > .recipe_item_footer .share_button');
        const shareCardRecipeLongEl = $('.recipe_item_long .recipe_item_footer .share_button');

        shareCardNewsEl.each(function() {
            const element = $(this);
            const shareCardPop = element.closest(".news_item_footer").find(".socials.pop_up_share");
            element.on('click', function (event) {
                event.preventDefault();
                shareCardPop.toggleClass("d_none");
            });
        });
        shareCardRecipeEl.each(function() {
            const element = $(this);
            const shareCardPop = element.closest(".recipe_item_footer").find(".socials.pop_up_share");
            element.on('click', function (event) {
                event.preventDefault();
                shareCardPop.toggleClass("d_none");
            });
        });
        shareCardRecipeLongEl.each(function() {
            const element = $(this);
            const shareCardPop = element.closest(".recipe_item_footer").find(".socials.pop_up_share");
            element.on('click', function (event) {
                event.preventDefault();
                shareCardPop.toggleClass("d_none");
            });
        });
    }

    window.setCardShareWindows();


    const spicyEl = $('.recipe_section > .recipe_stats > .column > .recipe_stats_item.spicy');
    const spicyPop = $('.pop_up_window.spicy_window');
    setListeners(spicyPop, spicyEl);

    const difficultyEl = $('.recipe_section > .recipe_stats > .column > .recipe_stats_item.difficulty');
    const difficultyPop = $('.pop_up_window.difficulty_window');
    setListeners(difficultyPop, difficultyEl);


    const supported_linkEl = $('.edit_section .title > .sub_title_and_mark > .supported_link');
    const supported_linkPop = $('.pop_up_window.supported_links_window');
    setListeners(supported_linkPop, supported_linkEl);

    const alt_linkEl = $('.edit_section .title > .sub_title_and_mark > .alt_link');
    const alt_linkPop = $('.pop_up_window.alt_links_window');
    setListeners(alt_linkPop, alt_linkEl);


    const part_1El = $('.edit_section .title > .sub_title_and_mark > .part_1');
    const part_1Pop = $('.pop_up_window.part_1_window');
    setListeners(part_1Pop, part_1El);

    const insertionEl = $('.edit_section .title > .sub_title_and_mark > .insertion');
    const insertionPop = $('.pop_up_window.insertion_window');
    setListeners(insertionPop, insertionEl);

    const part_2El = $('.edit_section .title > .sub_title_and_mark > .part_2');
    const part_2Pop = $('.pop_up_window.part_2_window');
    setListeners(part_2Pop, part_2El);

    const profile_pop_ids = [
        "profile_description",
        "recipe_description",
        "news_description",
    ]

    profile_pop_ids.forEach(element => {
        setListeners($(`.pop_up_window#${element}`), $(`.settings_section > .settings > .fields_form > .fields_wrapper > .fields_part > .fields > .field_item > .title_and_mark[data-popup-id=${element}] > img`));
    });

});