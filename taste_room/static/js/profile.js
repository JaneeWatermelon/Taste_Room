let news_active_status = $(".articles_section > .publish_types > .publish_type_item.active").attr("data-status");
let recipes_active_status = $("#my_recipes_section > .publish_types > .publish_type_item.active").attr("data-status");

// const COLORS = [
//     "#D68C45",
//     "#E9A96D",
//     "#FFCD9C",
//     "#4C956C",
//     "#C7E580",
//     "#50DA8C",
//     "#FF6766",
//     "#FF7BAC",
//     "#FFC9B9",
// ]

const color_items = $(".settings_section .background > .colors > .color_item");
const color_items2 = $(".profile_window.back_fon > .background > .colors > .color_item");

color_items2.on("click", function() {
    color_items2.removeClass("active");
    $(this).addClass("active");
})

function setAvatarAddImageEventHandler() {
    $(".settings_section > .settings > .background_and_avatar > .avatar > .image_item.add_image, .profile_header .image_wrapper").off("click").on("click", function() {
        $("#hidden_profile_image_input").click();
    });
    $("#hidden_profile_image_input").off("change").on("change", function() {
        const input = $(this)
        if (this.files && this.files[0]) {
            $(".settings_section > .settings > .background_and_avatar > form.avatar").submit();
        }
    })
}

setAvatarAddImageEventHandler();

$(".settings_section > .settings > .background_and_avatar > form.avatar").on("submit", function(event) {
    event.preventDefault();
    const form = $(this);
    const data_url = form.attr("action");
    const image = $("#hidden_profile_image_input")[0];

    // Создаем объект FormData
    const formData = new FormData(this);

    if (image.files) {
        formData.append('image', image.files[0]);
    }

    $.ajax({
        url: data_url,
        method: "POST",

        data: formData,
        processData: false, // Не обрабатывать данные
        contentType: false, // Не устанавливать тип содержимого

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);

            $(".profile_header > .content > .image_wrapper").load(window.location.href + " .profile_header > .content > .image_wrapper > *");
            $(".profile_header > .avatar_and_settings > .image_wrapper").load(window.location.href + " .profile_header > .avatar_and_settings > .image_wrapper > *");
            $(".header_buttons > .profile_icon_wrapper").load(window.location.href + " .header_buttons > .profile_icon_wrapper > *");
            $(".settings_section > .settings > .background_and_avatar > form.avatar").load(window.location.href + " .settings_section > .settings > .background_and_avatar > form.avatar > *", function() {
                setAvatarAddImageEventHandler();
            });
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})

$("form.profile_window.back_fon").on("submit", function(event) {
    event.preventDefault();
    const form = $(this);
    const data_url = form.attr("action");
    const data_id = form.find(".color_item.active").attr("data-id");

    // Создаем объект FormData
    const formData = new FormData(this);

    formData.append('data_id', data_id);

    window.showHideBackBlack(event, form);

    $.ajax({
        url: data_url,
        method: "POST",

        data: formData,
        processData: false, // Не обрабатывать данные
        contentType: false, // Не устанавливать тип содержимого

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);

            $(".profile_header").css({
                "background-color": data.background_hash
            })
            $(".text_hash").css({
                "color": data.text_hash
            })
            color_items.removeClass("active");
            $(`.settings_section .background > .colors > .color_item[data-id=${data_id}]`).addClass("active");
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})
$(".settings_section > .settings > .background_and_avatar > form.background").on("submit", function(event) {
    event.preventDefault();
    const form = $(this);
    const submitter = event.originalEvent.submitter;
    const clickedButton = $(submitter);

    const data_url = form.attr("action");
    const data_id = clickedButton.attr("data-id");

    color_items.removeClass("active");
    color_items2.removeClass("active");
    $(`.settings_section .background > .colors > .color_item[data-id=${data_id}]`).addClass("active");
    $(`.profile_window.back_fon > .background > .colors > .color_item[data-id=${data_id}]`).addClass("active");

    // Создаем объект FormData
    const formData = new FormData(this);

    formData.append('data_id', data_id);

    $.ajax({
        url: data_url,
        method: "POST",
        
        data: formData,
        processData: false, // Не обрабатывать данные
        contentType: false, // Не устанавливать тип содержимого

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);

            $(".profile_header").css({
                "background-color": data.background_hash
            })
            $(".text_hash").css({
                "color": data.text_hash
            })
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})

$(".settings_section > .settings > form.fields_form").on("submit", function(event) {
    event.preventDefault();
    const $this = $(this);

    const telegram_input = $("input[name='telegram']");
    const vk_input = $("input[name='vk']");
    const pinterest_input = $("input[name='pinterest']");
    const youtube_input = $("input[name='youtube']");
    const rutube_input = $("input[name='rutube']");

    let can_continue = true;

    if (telegram_input.val() 
        && !telegram_input.val().trim().startsWith("https://t.me/") 
        && !telegram_input.val().trim().startsWith("https://telegram.me/")) 
        {
        telegram_input.closest(".field_item").find(".error_message").removeClass("d_none");
        can_continue = false;
    }
    else {
        telegram_input.closest(".field_item").find(".error_message").addClass("d_none");
    }

    if (vk_input.val() 
        && !vk_input.val().trim().startsWith("https://vk.com/") 
        && !vk_input.val().trim().startsWith("https://m.vk.com/")) 
        {
        vk_input.closest(".field_item").find(".error_message").removeClass("d_none");
        can_continue = false;
    }
    else {
        vk_input.closest(".field_item").find(".error_message").addClass("d_none");
    }

    if (pinterest_input.val() 
        && !pinterest_input.val().trim().startsWith("https://pinterest.com/") 
        && !pinterest_input.val().trim().startsWith("https://www.pinterest.com/")) 
        {
        pinterest_input.closest(".field_item").find(".error_message").removeClass("d_none");
        can_continue = false;
    }
    else {
        pinterest_input.closest(".field_item").find(".error_message").addClass("d_none");
    }

    if (youtube_input.val() 
        && !youtube_input.val().trim().startsWith("https://youtube.com/") 
        && !youtube_input.val().trim().startsWith("https://www.youtube.com/")) 
        {
        youtube_input.closest(".field_item").find(".error_message").removeClass("d_none");
        can_continue = false;
    }
    else {
        youtube_input.closest(".field_item").find(".error_message").addClass("d_none");
    }

    if (rutube_input.val() 
        && !rutube_input.val().trim().startsWith("https://rutube.ru/") 
        && !rutube_input.val().trim().startsWith("https://www.rutube.ru/")) 
        {
        rutube_input.closest(".field_item").find(".error_message").removeClass("d_none");
        can_continue = false;
    }
    else {
        rutube_input.closest(".field_item").find(".error_message").addClass("d_none");
    }

    if (can_continue) {
        this.submit();
    }
})

let max_width = 0;

function set_news_active_status(status) {
    news_active_status = status;
}
function set_recipes_active_status(status) {
    recipes_active_status = status;
}

$(".profile_chapters .chapter_wrapper > .chapter > .chapter_item").on("click", function() {
    $this = $(this);
    all_buttons = $(".profile_chapters .chapter_wrapper > .chapter > .chapter_item");
    linked_block = $(`#${$this.attr("data-for")}`);
    possible_blocks = $(".possible_block");

    if (!$this.hasClass("active") && !$this.closest(".chapter").hasClass("add_button")) {
        all_buttons.removeClass("active");
        $(".profile_header .settings > .settings_item.change_settings").removeClass("active");
        $this.addClass("active");
        
        possible_blocks.addClass("d_none");
        linked_block.removeClass("d_none");
    }
})

function hideChapterItems() {
    $(".profile_chapters .chapter_wrapper.navigation.inner").addClass("d_none");
    $(".profile_chapters .chapter_wrapper > .chapter > .chapter_item.show_hide_chapter_items > #chapters_arrow").addClass("rotate_180");
}

$(".profile_chapters .chapter_wrapper > .chapter > .chapter_item.show_hide_chapter_items").off("click").on("click", function(event) {
    $this = $(this);
    navigation_wrapper = $(".profile_chapters .chapter_wrapper.navigation.inner");
    chapters_arrow = $this.find("#chapters_arrow");

    if (!navigation_wrapper.hasClass("d_none")) {
        navigation_wrapper.addClass("d_none");
        chapters_arrow.addClass("rotate_180");
    }
    else {
        navigation_wrapper.removeClass("d_none");
        chapters_arrow.removeClass("rotate_180");
    }
})
$(".profile_header .settings > .settings_item.change_settings").on("click", function() {
    $this = $(this);
    all_buttons = $(".profile_chapters .chapter_wrapper > .chapter > .chapter_item");
    linked_block = $(`#${$this.attr("data-for")}`);
    possible_blocks = $(".possible_block");

    hideChapterItems();

    if (!$this.hasClass("active")) {
        all_buttons.removeClass("active");
        $this.addClass("active");
        
        possible_blocks.addClass("d_none");
        linked_block.removeClass("d_none");
    }
})

function reloadMyRecipesAJAX(data_url, data_status, page=1) {
    $.ajax({
        url: data_url,
        method: 'GET',
        data: {
            data_status: data_status,
            page: page,
        },
        success: function (data) {
            $("#my_recipes_section > .cards_wrapper").html(data.html);
            $("#my_recipes_section > .pagination_wrapper").load(window.location.href + " #my_recipes_section > .pagination_wrapper > *");

            window.setCardShareWindows();
            window.setCardIngredientAndCooktimeWindows();
            window.setHeartAnimEventHandler();
            // setMultipleCardButtonsEventHandler();
            
            if (data.html.trim()) {
                $("#my_recipes_section > .empty_section").addClass("d_none");
            }
            else {
                $("#my_recipes_section > .empty_section").removeClass("d_none");
            }
            console.log('Ответ сервера:', data["answer"]);
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
}

$("#my_recipes_section > .publish_types > .publish_type_item").on("click", function() {
    $this = $(this);
    all_buttons = $("#my_recipes_section > .publish_types > .publish_type_item");

    if (!$this.hasClass("active")) {
        all_buttons.removeClass("active");
        $this.addClass("active");

        data_url = $this.parent().attr("data-url");
        data_status = $this.attr("data-status");

        set_recipes_active_status(data_status);

        reloadMyRecipesAJAX(data_url, data_status);
    }
})
$(".articles_section > .publish_types > .publish_type_item").on("click", function() {
    $this = $(this);
    all_buttons = $(".articles_section > .publish_types > .publish_type_item");

    if (!$this.hasClass("active")) {
        all_buttons.removeClass("active");
        $this.addClass("active");

        data_url = $this.parent().attr("data-url");
        data_status = $this.attr("data-status");

        set_news_active_status(data_status);

        $.ajax({
            url: data_url,
            method: 'GET',
            data: {
                data_status: data_status,
            },
            success: function (data) {
                $(".articles_section > .cards_wrapper").html(data.html);
                window.setCardShareWindows();
                // setMultipleCardButtonsEventHandler();
                if (data.html.trim()) {
                    $(".articles_section > .empty_section").addClass("d_none");
                }
                else {
                    $(".articles_section > .empty_section").removeClass("d_none");
                }
                console.log('Ответ сервера:', data["answer"]);
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
})

function sub_or_unsub_AJAX(data_url, data_id, data_type, after_func = () => null) {
    $.ajax({
        url: data_url,
        method: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN,
        },
        data: {
            data_id: data_id,
            data_type: data_type,
        },
        success: function (data) {
            after_func();
            console.log('Ответ сервера:', data["answer"]);
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
}

$(".subs_section > .subs_wrapper").on("click", ".subs_item > .sub_button", function() {
    $this = $(this);
    $this.parent().find(".sub_button").toggleClass("d_none");

    data_type = $this.attr("data-type");
    data_url = $this.parent().attr("data-url");
    data_id = $this.parent().attr("data-id");

    sub_or_unsub_AJAX(data_url, data_id, data_type);
})
$(".profile_header .settings_wrapper > .settings").on("click", ".sub_action_wrapper", function() {
    $this = $(this);
    // $this.parent().find(".sub_action_wrapper").toggleClass("d_none");

    data_type = $this.attr("data-type");
    data_url = $this.parent().attr("data-url");
    data_id = $this.parent().attr("data-id");

    if (window.innerWidth <= 720) {
        function after_func() {
            $(".profile_header > .avatar_and_settings > .settings_wrapper > .settings").load(window.location.href + " .profile_header > .avatar_and_settings > .settings_wrapper > .settings > *");
        }
    } else {
        function after_func() {
            $(".profile_header > .settings_wrapper > .settings").load(window.location.href + " .profile_header > .settings_wrapper > .settings > *");
        }
    }

    sub_or_unsub_AJAX(data_url, data_id, data_type, after_func);
})

$("form#sub_search_form").on("submit", function(event) {
    event.preventDefault();
    const form = $(this);
    const data_url = form.attr("action");
    const tagValue = form.find('input[name="tag"]').val();

    $.ajax({
        url: data_url,
        method: form.attr("method"),

        data: {
            "tag": tagValue,
        },

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);

            $(".subs_section > .remove_filters").removeClass("d_none");

            $(".subs_section > .subs_wrapper").html(data.html);
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})

$(".subs_section > .remove_filters").on("click", function() {
    $this = $(this);
    $("form#sub_search_form > input[name='tag']").val('');
    $(".subs_section > .subs_wrapper").load(window.location.href + " .subs_section > .subs_wrapper > *", function() {
        $this.addClass("d_none");
    });
})

function setCardPublicEventHandler() {
    $(".cards_wrapper").on("click", ".card_item .image_wrapper > .buttons > .public", function(event) {
        $this = $(this);
        let action_status;
        let data_status;
        let card_type;
        const data_url = $this.attr("data-url");
        const card_item = $this.closest(".card_item");
        const item_id = card_item.attr("data-id");
    
        if (card_item.hasClass("recipe_item")) {
            card_type = "recipe";
        }
        else {
            card_type = "news";
        }
    
        action_status = "4";
        if (card_type == "recipe") {
            data_status = recipes_active_status;
        }
        else {
            data_status = news_active_status;
        }
        $.ajax({
            url: data_url,
            method: "POST",

            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: {
                action_status: action_status,
                data_status: data_status,
                item_id: item_id,
            },
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                $this.closest(".cards_wrapper").html(data.html);
                window.setCardShareWindows();
                // setMultipleCardButtonsEventHandler();
                // const pop_up = $("#recipe_in_moderation_message");

                // window.showHideBackBlack(event, pop_up);
                // $(document).off('click').on('click', function (my_event) {
                //     window.HideBackBlackOverWindowClick(my_event, pop_up, $this);
                // });

                // pop_up.off('click').on('click', function (my_event) {
                //     my_event.stopPropagation(); // Останавливаем всплытие события
                // });
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    })

}

setCardPublicEventHandler();


function setElementAttrs(element, kwargs={}) {
    Object.keys(kwargs).forEach(key => {
        element.attr(key, kwargs[key]);
    });
}

function setMultipleCardButtonsEventHandler() {
    $(".cards_wrapper").on("click", ".card_item .image_wrapper > .buttons > .unpublic", function(event) {
        const $this = $(this);
        setCardButtonsEventHandler(
            $this, 
            $this.attr("data-url"),
            $this.closest(".card_item").attr("data-id"),
            {action_status: "3",},
            event,
        );
    });

    const delete_button = $(".image_wrapper > .visibility_and_adds > .delete");
    $(".cards_wrapper").on("click", ".card_item .image_wrapper > .visibility_and_adds > .delete", function(event) {
        const $this = $(this);
        setCardButtonsEventHandler(
            $this, 
            $this.attr("data-url"),
            $this.closest(".card_item").attr("data-id"),
            {},
            event,
        );
    });

}

function setCardButtonsEventHandler(target_button, data_url, item_id, send_kwargs={}, target_event) {
    const pop_up = $(`#${target_button.attr("data-popup-id")}`);

    window.showHideBackBlack(target_event, pop_up);
    $(document).off('click').on('click', function (event) {
        window.HideBackBlackOverWindowClick(event, pop_up, target_button);
    });

    pop_up.off("click").on('click', function (event) {
        event.stopPropagation(); // Останавливаем всплытие события
    });

    if (target_button.closest(".card_item").hasClass("recipe_item")) {
        card_type = "recipe";
    }
    else {
        card_type = "news";
    }


    const agree_button = pop_up.find(".buttons > .button_item.agree");
    
    agree_button.off("click").on("click", function(event) {
        $this = $(this);
        let data_status;

        console.log("clicked agree_button");

        window.showHideBackBlack(event, pop_up);

        if (card_type == "recipe") {
            data_status = recipes_active_status;
        }
        else {
            data_status = news_active_status;
        }

        let pre_data = {
            data_status: data_status,
            item_id: item_id,
        }

        let data = Object.assign({}, pre_data, send_kwargs);

        $.ajax({
            url: data_url,
            method: "POST",

            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: data,

            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                if (card_type == "recipe") {
                    $("#my_recipes_section > .cards_wrapper").html(data.html);
                }
                else {
                    $("#articles_section > .cards_wrapper").html(data.html);
                }
                window.setCardShareWindows();

                window.hideBackBlack_andPopup(pop_up);
                
                // setMultipleCardButtonsEventHandler();
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    })

}

setMultipleCardButtonsEventHandler();

$(".profile_window.unpublic_warning > .buttons > .button_item.disagree").on("click", function(event) {
    const unpublic_warning = $(this).closest(".unpublic_warning");
    window.hideBackBlack_andPopup(unpublic_warning);
})

function setPaginationEventHandler() {
    $(".pagination a").off("click").on("click", function(event) {
        event.preventDefault();
        $this = $(this);

        const data_url = $this.attr("href");
        const page = $this.attr("data-page");
        const data_type = $this.closest(".possible_block").attr("data-type");

        if (data_type == "my_recipes") {
            reloadMyRecipesAJAX(data_url, recipes_active_status, page);
        }
        
    })
}