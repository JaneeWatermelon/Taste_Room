$(".edit_section > .categories > .categories_list > .title_and_list > .category_item > .first_category > img").on("click", function() {
    $(this).siblings().filter("img").toggleClass("d_none");
    $(this).toggleClass("d_none");
  
    if ($(this).hasClass("plus")) {
        $(this).parent().siblings().filter(".second_categories").removeClass("d_none");
    } else if ($(this).hasClass("minus")) {
        $(this).parent().siblings().filter(".second_categories").addClass("d_none");
    }
})
$(".category_item > .category_content > .main_name > img").on("click", function() {
    $(this).siblings().filter("img").toggleClass("d_none");
    $(this).toggleClass("d_none");
  
    if ($(this).hasClass("plus")) {
        $(this).parent().siblings().filter("ul").removeClass("d_none");
    } else if ($(this).hasClass("minus")) {
        $(this).parent().siblings().filter("ul").addClass("d_none");
    }
})

const category_wrapper_height_full = $(".category_wrapper").height();
$(".category_wrapper").css("height", `${category_wrapper_height_full}px`);

$(".category_wrapper > .category_show_hide_wrapper").on("click", function() {
    let hide_wrapper = $(this).find(".hide_wrapper");

    if (hide_wrapper.hasClass("d_none")) {
        $(".category_wrapper").css("height", `${category_wrapper_height_full}px`);
    } else {
        $(".category_wrapper").css("height", `${$(".category_wrapper > .category_show_hide_wrapper").height()}`);
    }

    hide_wrapper.toggleClass("d_none");
    hide_wrapper.siblings().toggleClass("d_none");
})

$(".category_wrapper > .category_show_hide_wrapper").trigger('click');