function sendEventToGA() {
    const banners = $("[data-type='banner']");
    $.each(banners, function (index, value) {
        element = $(value);
        const banner_id = element.attr("id");
        const banner_name = element.attr("data-name");
        const image = $(`img[data-for='${banner_id}']`);

        let load_el;

        if (image.length) {
            load_el = image;
        }
        else {
            load_el = element;
        }
        load_el.off("load").on("load", function () {
            console.log("loaded");
            gtag('event', 'banner_load', {
                'banner_name': banner_name,
                'banner_id': banner_id,
            });
        })
        
        if (load_el.prop('complete')) load_el.trigger('load');

        element.on("click", function () {
            console.log("clicked");
            gtag('event', 'banner_click', {
                'banner_name': banner_name,
                'banner_id': banner_id,
            });
        })
    });
}

sendEventToGA();