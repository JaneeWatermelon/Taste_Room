let recipes_slidesPerView = 3;

let recipe_recs_width = $(".recipe_recs").width();
let new_recipes_section_width = $(".new_recipes_section").width()+24;

function set_swiper_nav_top(items, swiper_nav) {
    let image_height = $($(items[0]).find(".back_image")).height();
    console.log(image_height);
    swiper_nav.css({
        'top': `${8 + (image_height - swiper_nav.height())/2}px`,
    });
}

function makeSwiper({swiper, width, nav_dir=swiper, is_autoplay=true, spaceBetween=8, left=0}) {
    console.log(swiper);
    new Swiper(swiper, {
        direction: 'horizontal',
        loop: true,
        keyboard: true,
        slidesPerView: recipes_slidesPerView,
        width: width,
        spaceBetween: spaceBetween,
        autoplay: {
            delay: 3000,
            pauseOnMouseEnter: true,
        },
        navigation: {
            nextEl: nav_dir + " > .swiper_nav.next",
            prevEl: nav_dir + " > .swiper_nav.prev",
        },
        on: {
            slideChangeTransitionStart: function() {
                $(swiper + " .pop_up_share").addClass("d_none");
            },
        }
    });

    $(swiper + " .swiper-wrapper").css({
        'left': `${left}px`,
    });

    set_swiper_nav_top($(swiper + " .card_item"), $(nav_dir + " > .swiper_nav"));
}

if (window.innerWidth <= 720) {
    const new_recipes_item_width = recipes_slidesPerView*0.6*new_recipes_section_width;
    const recipe_recs_item_width = recipes_slidesPerView*0.6*recipe_recs_width;

    makeSwiper({swiper: ".swiper.new_recipes_section", width: new_recipes_item_width, left: -0.4*new_recipes_section_width});
    makeSwiper({swiper: ".swiper.news_recs_section.d_desktop_none", width: new_recipes_item_width, left: -0.4*new_recipes_section_width});
    makeSwiper({swiper: ".swiper.recipe_recs", width: recipe_recs_item_width, left: -0.4*recipe_recs_width});
    makeSwiper({swiper: ".swiper.news_recs", width: recipe_recs_item_width, left: -0.4*recipe_recs_width});
} 
else {
    const recipe_recs_item_width = recipes_slidesPerView*0.4*recipe_recs_width;

    makeSwiper({swiper: ".swiper.recipe_recs", width: recipe_recs_item_width, left: -0.1*recipe_recs_width});
    makeSwiper({swiper: ".swiper.news_recs", width: recipe_recs_item_width, left: -0.1*recipe_recs_width});
}

$(document).ready(function () {
    const swiper_detail_recipe_preview = new Swiper('.recipe_section > .recipe_header > .image_wrapper.swiper', {
        // direction: 'horizontal',
        loop: true,
        slidesPerView: 1,
        // width: new_recipes_item_width,
        autoplay: {
            delay: 3000,
        },
        effect: "fade",
        fadeEffect: {
            crossFade: true
        },
    });
});
