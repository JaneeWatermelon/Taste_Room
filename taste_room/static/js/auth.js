

function setHideBackBlackOverWindowClickEventListener(popup) {
    $(document).off('click').on('click', function (event) {
        if (!$(event.target).closest(".profile_window").length) {
            $(".back_black").css({
                "opacity": 0,
            });
            setTimeout(function() {
                $(".back_black").addClass('d_none');
                $(".profile_window").addClass('d_none');
                $(".profile_window").css({
                    "opacity": 1,
                });
            }, 300);
        }
    });
}

$(window).on('load', function() {
    var reloading = sessionStorage.getItem("reloading");
    if (reloading) {
        sessionStorage.removeItem("reloading");
        $('#login_window').removeClass('d_none');
        $(".back_black").removeClass('d_none');
        setTimeout(function() {
            $(".back_black").css({
                "opacity": 1,
            });
        }, 1);
    }
});

function reloadPage() {
    sessionStorage.setItem("reloading", "true");
    location.reload();
}

window.swapProfileWindows = function(current_popup, target_popup) {
    current_popup.css({
        "opacity": 0,
    });
    target_popup.css({
        "opacity": 0,
    });
    setTimeout(function() {
        current_popup.addClass('d_none');
        target_popup.removeClass('d_none');
        setTimeout(function() {
            target_popup.css({
                "opacity": 1,
            });
        }, 10);
    }, 300);
}

$(document).ready(function() {
    let popup = $('#login_window');
    const $authLinks = $('[data-require-auth]');
    
    // Обработчик для всех защищённых ссылок
    $authLinks.on('click', function(e) {
        if (!USER_AUTHENTICATED) {
            e.preventDefault();
            // if (!$(".back_black").hasClass(".d_none")) {
            //     const target_pop = $(`#${$(this).attr("data-target-id")}`);
            //     window.swapProfileWindows(target_pop, popup)
            // }
            // else {

                
            // }
            window.showHideBackBlack(e, popup);
            
            // Сохраняем оригинальный URL и позицию прокрутки
            localStorage.setItem('post_login_redirect', $(this).attr('href'));
            localStorage.setItem('scroll_position', $(window).scrollTop());
        }
    });
    
    // Обработчик клика вне окна
    setHideBackBlackOverWindowClickEventListener(popup);
  
    popup.on('click', function (event) {
        event.stopPropagation(); // Останавливаем всплытие события
    });

    $(".sub_action_href").on('click', function(e) {
        const $this = $(this);
        e.preventDefault();
        console.log($this);
        const current_popup = $this.closest(".profile_window");
        const target_popup = $(`#${$this.attr("data-action-id")}`);

        swapProfileWindows(current_popup, target_popup);
    });



    $("#registration_window > form").on("submit", function(event) {
        event.preventDefault();

        const form = $(this);
        const data_url = form.attr("action");

        const formData = new FormData(this);

        $.ajax({
            url: data_url,
            method: "POST",
    
            data: formData,
            processData: false, // Не обрабатывать данные
            contentType: false, // Не устанавливать тип содержимого
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                reloadPage();
            },
            error: function (error) {
                console.error('Ошибка:', error);

                const errorResponse = error.responseJSON;
                const messages_wrapper = form.find(".messages_wrapper")
                messages_wrapper.html(errorResponse.html_errors);
                messages_wrapper.removeClass("d_none");
            },
        });
    })
    $("#login_window > form").on("submit", function(event) {
        event.preventDefault();

        const form = $(this);
        const data_url = form.attr("action");

        const formData = new FormData(this);

        $.ajax({
            url: data_url,
            method: "POST",
    
            data: formData,
            processData: false, // Не обрабатывать данные
            contentType: false, // Не устанавливать тип содержимого
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                location.reload();
            },
            error: function (error) {
                console.error('Ошибка:', error);

                const errorResponse = error.responseJSON;
                const messages_wrapper = form.find(".messages_wrapper")
                messages_wrapper.html(errorResponse.html_errors);
                messages_wrapper.removeClass("d_none");
            },
        });
    })
    $("#reset_password > form").on("click", "[name='send_code_reset_password']", function(event) {
        event.preventDefault();

        const $this = $(this);

        const data_url = $this.parent().attr("data-url");
        const email = $("#send_code_reset_password").val();

        const form = $this.closest("form");
        const messages_wrapper = form.find(".messages_wrapper");
        const success_button = form.find(".success_button");

        const formData = new FormData();
        formData.append('email', email);

        if (email != "") {

            $this.addClass("black_50");
            $this.attr("disabled", "True");

            $.ajax({
                url: data_url,
                method: "POST",
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                },
                data: formData,
                processData: false, // Не обрабатывать данные
                contentType: false, // Не устанавливать тип содержимого
        
                success: function (data) {
                    console.log('Ответ сервера:', data["answer"]);

                    let i = 30;
                    $this.html(i);

                    const timer = setInterval(function(){
                        i--;
                        $this.html(i);
                    }, 1000)

                    setTimeout(function() {
                        clearTimeout(timer);
                        $this.html("Отправить");
                        $this.removeClass("black_50");
                        $this.removeAttr("disabled");
                    }, 30000);
                },
                error: function (error) {
                    console.error('Ошибка:', error);

                    const errorResponse = error.responseJSON;
                    messages_wrapper.html(errorResponse.html_errors);
                    messages_wrapper.removeClass("d_none");

                    $this.removeClass("black_50");
                    $this.removeAttr("disabled");
                },
            });
        }
        else {
            messages_wrapper.find("h4").html("Укажите электронную почту");
            messages_wrapper.removeClass("d_none");
        }
    })
    $("#reset_password > form").on("submit", function(event) {
        event.preventDefault();

        const form = $(this);
        const data_url = form.attr("action");

        const formData = new FormData(this);

        $.ajax({
            url: data_url,
            method: "POST",
            
            data: formData,
            processData: false, // Не обрабатывать данные
            contentType: false, // Не устанавливать тип содержимого
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                console.log(data.accepted);

                const current_popup = form.closest(".profile_window");
                const target_popup = $(`#set_new_password`);

                swapProfileWindows(current_popup, target_popup);

            },
            error: function (error) {
                console.error('Ошибка:', error);

                const errorResponse = error.responseJSON;
                const messages_wrapper = form.find(".messages_wrapper")
                messages_wrapper.html(errorResponse.html_errors);
                messages_wrapper.removeClass("d_none");
            },
        });
    })
    $("#set_new_password > form").on("submit", function(event) {
        event.preventDefault();

        const form = $(this);
        const data_url = form.attr("action");

        const formData = new FormData(this);

        $.ajax({
            url: data_url,
            method: "POST",
            
            data: formData,
            processData: false, // Не обрабатывать данные
            contentType: false, // Не устанавливать тип содержимого
    
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);

                reloadPage();
            },
            error: function (error) {
                console.error('Ошибка:', error);

                const errorResponse = error.responseJSON;
                const messages_wrapper = form.find(".messages_wrapper")
                messages_wrapper.html(errorResponse.html_errors);
                messages_wrapper.removeClass("d_none");
            },
        });
    })
});