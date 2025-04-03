$(document).ready(function () {
    let pageUrl = window.location.href;  // URL текущей страницы
    let pageTitle = `Попробуйте этот рецепт! ${document.title}`;
    let pageDescription = "Ещё больше вкусных рецептов на нашем сайте!";  // Описание

    function setPageTitleDescr(title, url_for_split) {
        const splitedUrl = url_for_split.split("/");
        if (splitedUrl.includes('recipes')) {
            pageTitle = `Попробуйте этот рецепт! `;
            pageDescription = "Ещё больше вкусных рецептов на нашем сайте!";
        }
        else {
            pageTitle = `Прочтите эту новость! `;
            pageDescription = "Ещё больше интересных новостей на нашем сайте!";
        }
        pageTitle += title;
    }

    // Обработка кликов
    $('.share_option').on('click', function () {
        let data_url;

        const pop_up_share = $(this).closest(".pop_up_share");
        if (pop_up_share) {
            pageUrl = window.location.origin + pop_up_share.attr("data-url");  // URL текущей страницы
            setPageTitleDescr(pop_up_share.attr("data-title"), pageUrl);    // Заголовок страницы
        }

        if ($(this).attr('data-social') == "tg") {
            data_url = `https:\\t.me/share/url?url=${pageUrl}&text=${pageTitle}`;
        }
        else if ($(this).attr('data-social') == "vk") {
            data_url = `https:\\vk.com/share.php?url=${pageUrl}&title=${pageTitle}&description=${pageDescription}`;
        }
        else if ($(this).attr('data-social') == "ws") {
            data_url = `https:\\api.whatsapp.com/send?text=${pageTitle}%20${pageUrl}`;
        }
        else if ($(this).attr('data-social') == "pinterest") {
            data_url = `https:\\pinterest.com/pin/create/button/?url=${pageUrl}&media=${pageUrl}&description=${pageDescription}`;
        }
        window.open(data_url, '_blank');
    });

    let setTimeout_id;

    $(".copy_window").removeClass("d_none");

    $('.copy_option').on('click', function () {
        clearTimeout(setTimeout_id);
        let copy_window = $(this).closest(".copy_wrapper").find(".copy_window");
        copy_window.addClass("show");
        setTimeout_id = setTimeout(function() {
            copy_window.removeClass("show");
        }, 1000)

        const pop_up_share = $(this).closest(".pop_up_share");
        if (pop_up_share) {
            pageUrl = window.location.origin + pop_up_share.attr("data-url");  // URL текущей страницы
            setPageTitleDescr(pop_up_share.attr("data-title"), pageUrl);    // Заголовок страницы
        }

        navigator.clipboard.writeText(pageUrl.split("#")[0]);
    });

});