const heart_wrappers = $(".image_wrapper > .heart_wrapper")

heart_wrappers.on("click", function() {
    const heart = $(this).find("img");
    heart.css({
        "transform": "scale(0.8)",
    });
    setTimeout(function() {
        heart.attr("src", "../static/svg/Random_icons/Heart_fill.svg");
        heart.css({
            "transform": "scale(1)",
        });
    }, 150)
})