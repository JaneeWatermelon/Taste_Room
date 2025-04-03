const CSRF_TOKEN = $('meta[name="csrf-token"]').attr("content");
const objectId = $("#object_info").attr("data-id"); // ID рецепта
const object_type = $("#object_info").attr("data-type");

$("form.add_comment").on("submit", function(event) {
    event.preventDefault();
    const form = $(this);
    const data_url = form.attr("action");

    // Создаем объект FormData
    const formData = new FormData(this);
    formData.append('item_id', objectId); // Добавляем item_id в FormData
    formData.append('is_answer', false);
    formData.append('item_type', object_type);

    $.ajax({
        url: data_url,
        method: form.attr("method"),

        data: formData,
        processData: false, // Не обрабатывать данные
        contentType: false, // Не устанавливать тип содержимого

        success: function (data) {
            console.log('Ответ сервера:', data["answer"]);

            show_add_image_wrapper_comment();
            $(".add_comment > .add_image > .image_input").val('');
            $(".add_comment > .input_wrapper > textarea").val('');

            $(".comments").removeClass("d_none");

            $(".comments").load(window.location.href + " .comments > *", function() {
                setAddCommentEventHandler();
                setAuthorInfoEventHandler();
                setShowHideAnswerEventHandler();
                setLikeDislikeCommentEventHandler();
                setShowMoreEventHandler();
                setTextareaRows();
            });
        },
        error: function (error) {
            console.error('Ошибка:', error);
        },
    });
})

function setAddCommentEventHandler() {
    $("form.add_answer_comment").off("submit").on("submit", function(event) {
        event.preventDefault();
        const form = $(this);
        const data_url = form.attr("action");

        const data_parent_id = form.attr("data-parent-id");
    
        // Создаем объект FormData
        const formData = new FormData(this);

        formData.append('item_id', objectId); // Добавляем item_id в FormData
        formData.append('data_parent_id', data_parent_id);

        const page = $(`.comments > .comment_wrapper[data-parent-id=${data_parent_id}]`).attr("data-page");

        let loader;

        if (page) {
            const window_url = window.location.origin + `/users/comments_partial_view?recipe_id=${objectId}&page=${page}`;
            loader = window_url + ` .comment_wrapper[data-parent-id=${data_parent_id}] > *`;
        }
        else {
            loader = window.location.href + ` .comments > .comment_wrapper[data-parent-id=${data_parent_id}] > *`;
        }

    
        $.ajax({
            url: data_url,
            method: form.attr("method"),
    
            data: formData,
            processData: false, // Не обрабатывать данные
            contentType: false, // Не устанавливать тип содержимого
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
    
                $(`.comments > .comment_wrapper[data-parent-id=${data_parent_id}]`).load(loader, function() {
                    setAuthorInfoEventHandler();
                    setShowHideAnswerEventHandler();
                    setLikeDislikeCommentEventHandler();
                    setAddCommentEventHandler();
                    setTextareaRows();
                });
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    })
}

setAddCommentEventHandler();

function setShowMoreEventHandler() {
    $(".comments > .show_more > h5").off("click").on("click", function() {
        const button = $(this).parent();
        const page = button.attr("data-page"); // Получаем номер следующей страницы
        const data_url = button.attr("data-url"); // ID рецепта
    
        // Отправляем AJAX-запрос
        $.ajax({
            url: data_url, // URL для загрузки комментариев
            method: "GET",
            data: {
                page: page,
                object_id: objectId,
                object_type: object_type,
            },
            success: function(data) {
                // Добавляем новые комментарии в конец списка
                $(".comments").append(data.comments_html);

                button.appendTo(".comments");
    
                // Обновляем кнопку "Показать ещё"
                if (data.has_next) {
                    button.attr("data-page", data.next_page);
                } else {
                    button.remove(); // Удаляем кнопку, если больше нет комментариев
                }

                setAddCommentEventHandler();
                setAuthorInfoEventHandler();
                setShowHideAnswerEventHandler();
                setLikeDislikeCommentEventHandler();
                setTextareaRows();
            },
            error: function(error) {
                console.error("Ошибка при загрузке комментариев:", error);
            },
        });
    });
}

setShowMoreEventHandler();

function show_image_comment() {
    $(".recipe_section > .recipe_add_comment > .add_image").addClass("d_none");
    $(".recipe_section > .recipe_add_comment > .image_wrapper").removeClass("d_none");
}
function show_add_image_wrapper_comment() {
    $(".recipe_section > .recipe_add_comment > .add_image").removeClass("d_none");
    $(".recipe_section > .recipe_add_comment > .image_wrapper").addClass("d_none");
}

$(".recipe_section > .recipe_add_comment > .image_wrapper > .delete_and_change > .delete").on("click", function() {

    $(".recipe_section > .recipe_add_comment > .add_image > .image_input").val('');

    show_add_image_wrapper_comment();
});

$(".recipe_section > .recipe_add_comment > .image_wrapper > .delete_and_change > .change").on("click", function() {
    
    const item = $(".recipe_section > .recipe_add_comment > .add_image > .image_input");

    item.click();

});

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('.recipe_section > .recipe_add_comment > .image_wrapper .back_image').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$(".recipe_section > .recipe_add_comment > .add_image > .image_input").on("input", function() {

    if ($(this).val()) {
        show_image_comment();
    }
    else {
        show_add_image_wrapper_comment();
    }

    
});

$(".recipe_section > .recipe_add_comment > .add_image > .image_input").change(function(){
    readURL(this);
});

function setAuthorInfoEventHandler() {
    const author_info = $(".comments > .comment_wrapper .comment_item > .author_info");
    const all_add_answer_comment = $(".comments > .comment_wrapper > .add_answer_comment");
    author_info.off("click");

    author_info.each(function() {
        const element = $(this);
        const add_answer_comment = element.closest(".comment_wrapper").find(".add_answer_comment");

        element.on("click", function(event) {

            element.toggleClass("active");

            if (element.hasClass("active")) {
                element.find(".comment_actions").removeClass("d_none");
            }
            else {
                element.find(".comment_actions").addClass("d_none");
            }

            console.log(event.target);

            if ($(event.target).closest(".answer").length > 0) {
                all_add_answer_comment.each(function() {
                    if (!$(this).is(add_answer_comment)) {
                        $(this).addClass("d_none");
                    }
                });

                add_answer_comment.toggleClass("d_none");
            }

            if ($(event.target).closest(".delete").length > 0) {
                
                const comment_item = element.closest(".comment_item");
                const data_comment_id = comment_item.attr("data-comment-id");
                const data_url = $(event.target).closest(".delete").attr("data-url");

                const data_parent_id = element.closest(".comment_wrapper").attr("data-parent-id");

                const page = $(`.comments > .comment_wrapper[data-parent-id=${data_parent_id}]`).attr("data-page");

                let loader;

                if (page) {
                    const window_url = window.location.origin + `/users/comments_partial_view?recipe_id=${objectId}&page=${page}`;
                    loader = window_url + ` .comment_wrapper[data-parent-id=${data_parent_id}] > *`;
                }
                else {
                    loader = window.location.href + ` .comments > .comment_wrapper[data-parent-id=${data_parent_id}] > *`;
                }
                
                $.ajax({
                    url: data_url,
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': CSRF_TOKEN,
                    },
                    data: {
                        comment_id: data_comment_id,
                    },
                    success: function (data) {
                        console.log('Ответ сервера:', data["answer"]);
        
                        // if (comment_item.hasClass("parent")) {
                        //     element.closest(".comment_wrapper").remove();
                        // }
                        // else{
                        //     comment_item.remove();
                        // }

                        $(`.comments > .comment_wrapper[data-parent-id=${data_parent_id}]`).load(loader, function() {
                            setAuthorInfoEventHandler();
                            setShowHideAnswerEventHandler();
                            setLikeDislikeCommentEventHandler();
                            setAddCommentEventHandler();
                            setTextareaRows();
                        });
                        
                    },
                    error: function (error) {
                        console.error('Ошибка:', error);
                    },
                });
            }
        
        });
    });
}

setAuthorInfoEventHandler();

function setShowHideAnswerEventHandler() {
    const show_hide_button = $(".comments > .comment_wrapper > .change_visibility_answers > h5");
    show_hide_button.off("click");

    show_hide_button.each(function() {
        const element = $(this);
        const change_visibility_answers = element.closest(".comment_wrapper").find(".change_visibility_answers");
        const answers = element.closest(".comment_wrapper").find(".answers");

        element.on("click", function() {

            change_visibility_answers.toggleClass("d_none");
            answers.toggleClass("d_none");
        
        });
    });
}

setShowHideAnswerEventHandler();

function setTextareaRows() {
    $('textarea').attr('rows', 4);
}



function setLikeDislikeCommentEventHandler() {
    const likes_and_dislikes = $(".comments > .comment_wrapper .comment_item > .rating > * > img");

    likes_and_dislikes.off("click").on("click", function() {
        const reaction = $(this);
        const data_url = $(this).closest(".rating").attr("data-url");
        
        let reaction_type;
        if ($(this).parent().hasClass("likes")) {
            reaction_type = 'like';
        }
        else {
            reaction_type = 'dislike';
        }
    
        const data_id = $(this).closest(".comment_wrapper").attr("data-parent-id");
        const data_comment_id = $(this).closest(".comment_item").attr("data-comment-id");
    
        let is_plus;
    
        if (reaction.hasClass("active")) {
            is_plus = false;
        }
        else {
            is_plus = true;
        }

        const page = $(`.comments > .comment_wrapper[data-parent-id=${data_id}]`).attr("data-page");

        let loader;

        if (page) {
            const window_url = window.location.origin + `/users/comments_partial_view?recipe_id=${objectId}&page=${page}`;
            loader = window_url + ` .comment_wrapper[data-parent-id=${data_id}] .comment_item[data-comment-id=${data_comment_id}] > .rating > *`;
        }
        else {
            loader = window.location.href + ` .comments > .comment_wrapper[data-parent-id=${data_id}] .comment_item[data-comment-id=${data_comment_id}] > .rating > *`;
        }
    
        $.ajax({
            url: data_url,
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: {
                comment_id: data_comment_id,
                reaction_type: reaction_type,
            },
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);

                $(`.comments > .comment_wrapper[data-parent-id=${data_id}] .comment_item[data-comment-id=${data_comment_id}] > .rating`).load(loader, function() {
                    setLikeDislikeCommentEventHandler();
                });
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    })
}

setLikeDislikeCommentEventHandler();

