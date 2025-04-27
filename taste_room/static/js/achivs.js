// const CSRF_TOKEN = $('meta[name="csrf-token"]').attr("content");
const change_profile_current_achiv_url = $(".achievements_section").attr("data-url");

$(".achievements_section > * .achiv_list > .achiv_item > img").on("click", function() {
    $this = $(this);
    achiv_item = $(this).closest(".achiv_item");
    if (!achiv_item.hasClass("disabled")) {
        const data_url = change_profile_current_achiv_url;
        const item_id = achiv_item.attr("data-id");

        console.log($this);
        console.log(achiv_item);

        $(`.achievements_section > * .achiv_list > .achiv_item[data-id=${item_id}] > img`).toggleClass("active");

        const active = $this.hasClass("active");

        $.ajax({
            url: data_url,
            method: "POST",
    
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: {
                active: active,
                item_id: item_id,
            },
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                if (window.innerWidth <= 720) {
                    $(".profile_header.d_desktop_none > .content > .info > .name_tag_descr_achiv").load(window.location.href + " .profile_header.d_desktop_none > .content > .info > .name_tag_descr_achiv > *");
                } else {
                    $(".profile_header.d_mobile_none > .content > .info > .name_tag_descr_achiv").load(window.location.href + " .profile_header.d_mobile_none > .content > .info > .name_tag_descr_achiv > *");
                }
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
})