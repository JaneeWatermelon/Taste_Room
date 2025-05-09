const stars_wrapper = $(".rating_wrapper > .stars");
const rating_wrapper_info = $(".rating_wrapper > .info");

function set_order() {
    for (let i=0; i < stars_wrapper.children().length; i++) {
        let star = $(stars_wrapper.find("img")[i]);
        star.attr('data-src', star.attr('src'));
        star.attr("data-src2", star.attr('src'));
        star.attr('data-order', i+1);
    }
}

set_order();

stars_wrapper.on("mouseenter", "img", function() {
    const data_order = Number($(this).attr("data-order"));

    for (let i=0; i < 5; i++) {
        let star = $(stars_wrapper.find("img")[i]);
        if (i < data_order) {
            star.attr('src', star_on_icon);
        }
        else {
            star.attr('src', star.attr("data-src"));
        }
    }
})

stars_wrapper.on("mouseleave", function() {
    let children = stars_wrapper.find("img");
    const data_order = Number(children.attr("data-order"));

    for (let i=0; i < 5; i++) {
        let star = $(children[i]);
        star.attr('src', star.attr("data-src"));
    }
})

stars_wrapper.on("click", "img", function() {
    const item_id = stars_wrapper.attr("data-id");
    // const item_type = stars_wrapper.attr("data-type");
    let data_url = stars_wrapper.attr("data-url");
    const new_rating = Number($(this).attr("data-order"));

    if (user_review_rating && user_review_rating == new_rating) {
        data_url = stars_wrapper.attr("data-url-delete");
        $.ajax({
            url: data_url,
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: {
                item_id: item_id,
                // item_type: item_type,
            },
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                let children = stars_wrapper.find("img");
                for (let i=0; i < 5; i++) {
                    let star = $(children[i]);
                    star.attr("data-src", star.attr("data-src2"));
                    star.attr('src', star.attr("data-src"));
                }
                user_review_rating = null;
                $(".rating_wrapper > .info").load(window.location.href + " .rating_wrapper > .info > *");
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
    else {
        $.ajax({
            url: data_url,
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: {
                item_id: item_id,
                // item_type: item_type,
                new_rating: new_rating,
            },
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                let children = stars_wrapper.find("img");
                for (let i=0; i < 5; i++) {
                    let star = $(children[i]);
                    if (i < new_rating) {
                        star.attr("data-src", star_on_icon);
                        star.attr('src', star.attr("data-src"));
                    }
                    else {
                        star.attr("data-src", star.attr("data-src2"));
                        star.attr('src', star.attr("data-src"));
                    }
                }
                user_review_rating = new_rating;
                $(".rating_wrapper > .info").load(window.location.href + " .rating_wrapper > .info > *");
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
})

if (user_review_exists == 1) {
    console.log(user_review_rating);
    for (let i=0; i < user_review_rating; i++) {
        let star = $(stars_wrapper.find("img")[i]);
        star.attr('src', star_on_icon);
        star.attr('data-src', star_on_icon);
    }
}