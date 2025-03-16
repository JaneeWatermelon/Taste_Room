const heart_wrappers = $(".image_wrapper > .heart_wrapper")

heart_wrappers.on("click", function() {
    const heart = $(this).find("img");
    const heart_wrapper = $(this);
    const data_url = $(this).attr("data-url");
    const data_id = $(this).attr("data-id");
    const CSRF_TOKEN = $('meta[name="csrf-token"]').attr("content");

    heart.css({
        "transform": "scale(0.8)",
    });
    setTimeout(function() {
        if (heart_wrapper.hasClass("active")) {
            heart.attr("src", heart_blank_icon);
        }
        else {
            heart.attr("src", heart_fill_icon);
        }
        console.log(heart_wrapper);
        heart_wrapper.toggleClass("active");
        heart.css({
            "transform": "scale(1)",
        });
    }, 150)
    $.ajax({
        url: data_url,
        method: 'POST',
        headers: {
            'X-CSRFToken': CSRF_TOKEN,
        },
        data: {
            recipe_id: data_id,
        },
        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})