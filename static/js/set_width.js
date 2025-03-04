function set_image_height(container, image) {
    image.addClass("d_none");
    const container_height = container.height();
    image.css("height", `${container_height}px`);
    image.removeClass("d_none");
}

set_image_height($(".recipe_section > .recipe_warning"), $(".recipe_section > .recipe_warning > img"));
set_image_height($(".profile_header > .content > .info > .name_tag_descr_achiv > .name_tag_descr"), $(".profile_header > .content > .info > .name_tag_descr_achiv > .name_tag_descr > img"));
set_image_height($(".subs_section > .subs_wrapper > .subs_item > .info > .image_wrapper"), $(".subs_section > .subs_wrapper > .subs_item > .info > .image_wrapper > img"));