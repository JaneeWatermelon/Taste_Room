function change_symbols_count(input) {
    const Min = Number(input.attr("min") ?? input.attr("minlength"));
    const Max = Number(input.attr("max") ?? input.attr("maxlength"));
    let my_symbols_span = input.parent().siblings().filter(".marks_limits").find(".my_symbols");
    my_symbols_span.html(input.val().length);
    if (input.val().length >= Min && input.val().length <= Max) {
        my_symbols_span.addClass("orange");
        my_symbols_span.removeClass("heart");
    } else {
        my_symbols_span.addClass("heart");
        my_symbols_span.removeClass("orange");
    }
}

$("input, textarea").on("input", function () {
    change_symbols_count($(this));
})
$('input, textarea').each(function () {
    change_symbols_count($(this));
});