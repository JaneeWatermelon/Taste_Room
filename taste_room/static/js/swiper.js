let recipes_slidesPerView = 3;

let recipe_recs_width = $(".recipe_recs").width();
let new_recipes_section_width = $(".new_recipes_section").width()+24;

if (window.innerWidth <= 720) {

    $(".new_recipes_section .swiper-wrapper").css({
        'left': `${-0.4*(new_recipes_section_width)}px`,
    })
    $(".news_recs_section .swiper-wrapper").css({
        'left': `${-0.4*(new_recipes_section_width)}px`,
    })

    const item_width = recipes_slidesPerView*0.6*new_recipes_section_width;

    const swiper_new_recipes_section = new Swiper('.swiper.new_recipes_section', {
        direction: 'horizontal',
        loop: true,
        slidesPerView: recipes_slidesPerView,
        width: item_width,
        spaceBetween: 8,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.new_recipes_section > .swiper_nav.next',
            prevEl: '.new_recipes_section > .swiper_nav.prev',
        },
    });
    const swiper_news_recs_section = new Swiper('.swiper.news_recs_section.d_desktop_none', {
        direction: 'horizontal',
        loop: true,
        slidesPerView: recipes_slidesPerView,
        width: item_width,
        spaceBetween: 8,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.news_recs_section > .swiper_nav.next',
            prevEl: '.news_recs_section > .swiper_nav.prev',
        },
    });


    $(".recipe_recs .swiper-wrapper").css({
        'left': `${-0.4*recipe_recs_width}px`,
    })
    $(".news_recs .swiper-wrapper").css({
        'left': `${-0.4*recipe_recs_width}px`,
    })
    
    const swiper_recipes = new Swiper('.swiper.recipe_recs', {
        direction: 'horizontal',
        loop: true,
        slidesPerView: recipes_slidesPerView,
        width: recipes_slidesPerView*0.6*recipe_recs_width,
        spaceBetween: 8,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.recipe_recs > .swiper_nav.next',
            prevEl: '.recipe_recs > .swiper_nav.prev',
        },
    });
    const swiper_news = new Swiper('.swiper.news_recs', {
        direction: 'horizontal',
        loop: true,
        slidesPerView: recipes_slidesPerView,
        width: recipes_slidesPerView*0.6*recipe_recs_width,
        spaceBetween: 8,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.news_recs > .swiper_nav.next',
            prevEl: '.news_recs > .swiper_nav.prev',
        },
    });
} 
else {
    $(".recipe_recs .swiper-wrapper").css({
        'left': `${-0.1*recipe_recs_width}px`,
    })
    $(".news_recs .swiper-wrapper").css({
        'left': `${-0.1*recipe_recs_width}px`,
    })
    
    const swiper_recipes = new Swiper('.swiper.recipe_recs', {
        direction: 'horizontal',
        loop: true,
        slidesPerView: recipes_slidesPerView,
        keyboard: true,
        width: recipes_slidesPerView*0.4*recipe_recs_width,
        spaceBetween: 8,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.recipe_recs > .swiper_nav.next',
            prevEl: '.recipe_recs > .swiper_nav.prev',
        },
        on: {
            slideChangeTransitionStart: function() {
                $('.swiper.recipe_recs').find(".pop_up_share").addClass("d_none");
            },
        }
    });
    const swiper_news = new Swiper('.swiper.news_recs', {
        direction: 'horizontal',
        loop: true,
        slidesPerView: recipes_slidesPerView,
        keyboard: true,
        width: recipes_slidesPerView*0.4*recipe_recs_width,
        spaceBetween: 8,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: '.news_recs > .swiper_nav.next',
            prevEl: '.news_recs > .swiper_nav.prev',
        },
        on: {
            slideChangeTransitionStart: function() {
                $('.swiper.news_recs').find(".pop_up_share").addClass("d_none");
            },
        }
    });
}

$(document).ready(function () {

    const swiper_detail_recipe_preview = new Swiper('.recipe_section > .recipe_header > .image_wrapper.swiper', {
        // direction: 'horizontal',
        loop: true,
        slidesPerView: 1,
        // width: item_width,
        autoplay: {
            delay: 3000,
        },
        effect: "fade",
        fadeEffect: {
            crossFade: true
        },
    });

    function set_swiper_nav_top(items, swiper_nav) {
        let image_height = $($(items[0]).find(".back_image")).height();
        swiper_nav.css({
            'top': `${8 + (image_height - swiper_nav.height())/2}px`,
        });
    }

    set_swiper_nav_top($(".recipe_recs .recipe_item"), $(".recipe_recs.swiper > .swiper_nav"));
    set_swiper_nav_top($(".news_recs .news_item"), $(".news_recs.swiper > .swiper_nav"));
    set_swiper_nav_top($(".news_recs_section .news_item"), $(".news_recs_section.swiper > .swiper_nav"));
    set_swiper_nav_top($(".new_recipes_section.swiper .recipe_item"), $(".new_recipes_section.swiper > .swiper_nav"));

});
