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
    $(".settings_section > .settings > .background_and_avatar > .avatar > .image_item.add_image, .profile_header > .content > .image_wrapper").off("click").on("click", function() {
        console.log("press to change image");
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

    console.log(image);
    console.log(image.files);

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

let max_width = 0;

// $(".subs_section > .subs_wrapper > .subs_item > .sub_button").toArray().forEach(element => {
//     if ($(element).width() > max_width) {
//         max_width = $(element).width();
//     }
// });

// $(".subs_section > .subs_wrapper > .subs_item > .sub_button").css("width", `${max_width}px`);

function set_news_active_status(status) {
    news_active_status = status;
}
function set_recipes_active_status(status) {
    recipes_active_status = status;
}

$(".profile_chapters > .chapter_wrapper > .chapter > .chapter_item").on("click", function() {
    $this = $(this);
    all_buttons = $(".profile_chapters > .chapter_wrapper > .chapter > .chapter_item");
    linked_block = $(`#${$this.attr("data-for")}`);
    possible_blocks = $(".possible_block");

    if (!$this.hasClass("active") && !$this.closest(".chapter").hasClass("add_button")) {
        all_buttons.removeClass("active");
        $(".profile_header > .settings_wrapper > .settings > .settings_item.change_settings").removeClass("active");
        $this.addClass("active");
        
        possible_blocks.addClass("d_none");
        linked_block.removeClass("d_none");
    }
})
$(".profile_header > .settings_wrapper > .settings > .settings_item.change_settings").on("click", function() {
    $this = $(this);
    all_buttons = $(".profile_chapters > .chapter_wrapper > .chapter > .chapter_item");
    linked_block = $(`#${$this.attr("data-for")}`);
    possible_blocks = $(".possible_block");

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
            setRecipeCardButtonsEventHandler();

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
                console.log('Ответ сервера:', data["answer"]);
                window.setCardShareWindows();
                setNewsCardButtonsEventHandler();
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

    console.log(tagValue);

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

function setRecipeCardButtonsEventHandler() {
    const hover_el = $(".recipe_item > .recipe_item_header > .image_wrapper > .buttons > .unpublic");
    const pop_up = $(".profile_window.unpublic_warning#recipe_unpublic_warning");

    $(document).on('click', function (event) {
        window.HideBackBlackOverWindowClick(event, pop_up, hover_el);
    });

    pop_up.off("click").on('click', function (event) {
        event.stopPropagation(); // Останавливаем всплытие события
    });

    $(".recipe_item > .recipe_item_header > .image_wrapper > .buttons > *").off("click").on("click", function(event) {
        $this = $(this);
        let action_status;
        const data_url = $this.attr("data-url");
        const item_id = $this.closest(".recipe_item").attr("data-id");
    
        if ($this.hasClass("unpublic")) {
            action_status = "2";

            window.showHideBackBlack(event, pop_up);

            pop_up.attr("data-url", data_url);
            pop_up.attr("data-id", item_id);
        }
        else if ($this.hasClass("public")) {
            action_status = "1";
            $.ajax({
                url: data_url,
                method: "POST",
    
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                },
                data: {
                    action_status: action_status,
                    data_status: recipes_active_status,
                    item_id: item_id,
                },
        
                success: function (data) {
                    console.log('Ответ сервера:', data["answer"]);
                    $("#my_recipes_section > .cards_wrapper").html(data.html);
                    window.setCardShareWindows();
                    setRecipeCardButtonsEventHandler();
                },
                error: function (error) {
                    console.error('Ошибка:', error);
                },
            });
        }
    })
}

setRecipeCardButtonsEventHandler();

$(".profile_window.unpublic_warning#recipe_unpublic_warning > .buttons > .button_item.unpublic").on("click", function(event) {
    $this = $(this);
    let action_status = "2";
    const unpublic_warning = $this.closest(".unpublic_warning");
    const data_url = unpublic_warning.attr("data-url");
    const item_id = unpublic_warning.attr("data-id");

    window.showHideBackBlack(event, unpublic_warning);

    $.ajax({
        url: data_url,
        method: "POST",

        headers: {
            'X-CSRFToken': CSRF_TOKEN,
        },
        data: {
            action_status: action_status,
            data_status: recipes_active_status,
            item_id: item_id,
        },

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);
            $("#my_recipes_section > .cards_wrapper").html(data.html);
            window.setCardShareWindows();
            
            setRecipeCardButtonsEventHandler();
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})

$(".profile_window.unpublic_warning#recipe_unpublic_warning > .buttons > .button_item.save_public").on("click", function(event) {
    const unpublic_warning = $this.closest(".unpublic_warning");
    window.showHideBackBlack(event, unpublic_warning);
})


function setNewsCardButtonsEventHandler() {
    const hover_el = $(".news_item > .news_item_header > .image_wrapper > .buttons > .unpublic");
    const pop_up = $(".profile_window.unpublic_warning#news_unpublic_warning");

    $(document).on('click', function (event) {
        window.HideBackBlackOverWindowClick(event, pop_up, hover_el);
    });

    pop_up.off("click").on('click', function (event) {
        event.stopPropagation(); // Останавливаем всплытие события
    });

    $(".news_item > .news_item_header > .image_wrapper > .buttons > *").off("click").on("click", function(event) {
        $this = $(this);
        let action_status;
        const data_url = $this.attr("data-url");
        const item_id = $this.closest(".news_item").attr("data-id");
    
        if ($this.hasClass("unpublic")) {
            action_status = "2";

            window.showHideBackBlack(event, pop_up);

            pop_up.attr("data-url", data_url);
            pop_up.attr("data-id", item_id);
        }
        else if ($this.hasClass("public")) {
            action_status = "1";
            $.ajax({
                url: data_url,
                method: "POST",
    
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                },
                data: {
                    action_status: action_status,
                    data_status: news_active_status,
                    item_id: item_id,
                },
        
                success: function (data) {
                    console.log('Ответ сервера:', data["answer"]);
                    $(".articles_section > .cards_wrapper").html(data.html);
                    window.setCardShareWindows();
                    setNewsCardButtonsEventHandler();
                },
                error: function (error) {
                    console.error('Ошибка:', error);
                },
            });
        }
    })
}

setNewsCardButtonsEventHandler();

$(".profile_window.unpublic_warning#news_unpublic_warning > .buttons > .button_item.unpublic").on("click", function(event) {
    $this = $(this);
    let action_status = "2";
    const unpublic_warning = $this.closest(".unpublic_warning");
    const data_url = unpublic_warning.attr("data-url");
    const item_id = unpublic_warning.attr("data-id");

    window.showHideBackBlack(event, unpublic_warning);

    $.ajax({
        url: data_url,
        method: "POST",

        headers: {
            'X-CSRFToken': CSRF_TOKEN,
        },
        data: {
            action_status: action_status,
            data_status: news_active_status,
            item_id: item_id,
        },

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);
            $(".articles_section > .cards_wrapper").html(data.html);
            window.setCardShareWindows();
            
            setNewsCardButtonsEventHandler();
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})

$(".profile_window.unpublic_warning#news_unpublic_warning > .buttons > .button_item.save_public").on("click", function(event) {
    const unpublic_warning = $this.closest(".unpublic_warning");
    window.showHideBackBlack(event, unpublic_warning);
})

function setPaginationEventHandler() {
    $(".pagination a").off("click").on("click", function(event) {
        event.preventDefault();
        console.log("in a");
        $this = $(this);

        const data_url = $this.attr("href");
        const page = $this.attr("data-page");
        const data_type = $this.closest(".possible_block").attr("data-type");

        if (data_type == "my_recipes") {
            reloadMyRecipesAJAX(data_url, recipes_active_status, page);
        }
        
    })
}