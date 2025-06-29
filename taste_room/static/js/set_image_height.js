function set_image_height(container, image) {
    image.addClass("d_none");
    const container_height = container.height();
    image.css("height", `${container_height}px`);
    image.removeClass("d_none");
}

set_image_height($(".recipe_section > .recipe_warning"), $(".recipe_section > .recipe_warning > img"));
set_image_height($(".subs_section > .subs_wrapper > .subs_item > .info > .image_wrapper"), $(".subs_section > .subs_wrapper > .subs_item > .info > .image_wrapper > img"));
set_image_height($(".profile_window > .info_form > #messages_wrapper_id"), $(".profile_window > .info_form > #messages_wrapper_id > img"));
set_image_height($(".profile_chapters .chapter_wrapper > .chapter > .chapter_item"), $(".profile_chapters .chapter_wrapper > .chapter > .chapter_item > img"));
set_image_height($(".profile_chapters .chapter_wrapper > .chapter > .chapter_item"), $(".profile_chapters .chapter_wrapper > .chapter > .chapter_item > svg"));