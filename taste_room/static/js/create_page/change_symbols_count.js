window.changeProgressBarProps = function(bar, curr_text, min, max, curr_count) {

    curr_text.html(curr_count);

    if (curr_count >= min && curr_count <= max) {
        curr_text.addClass("orange");
        curr_text.removeClass("heart");
    } else {
        curr_text.addClass("heart");
        curr_text.removeClass("orange");
    }
    bar.css("width", `${(curr_count-min)*100/(max-min)}%`);
}

function change_symbols_count(input) {
    const Min = Number(input.attr("min") ?? input.attr("minlength"));
    const Max = Number(input.attr("max") ?? input.attr("maxlength"));

    let marks_limits = $(`.marks_limits[data-for='${input.attr("id")}']`);
    let my_symbols_span = marks_limits.find(".my_symbols");
    let filled_bar = marks_limits.find(".filler_bar");
    let symbols_count = input.val().length;

    changeProgressBarProps(filled_bar, my_symbols_span, Min, Max, symbols_count);
}
window.setChangeSymbolsCountEventListener = function() {
    $("input.with_marks, textarea.with_marks").on("input", function () {
        console.log("input");
        change_symbols_count($(this));
    })
}
window.setChangeSymbolsCountEventListener();
$('input.with_marks, textarea.with_marks').each(function () {
    change_symbols_count($(this));
});

function setChoosedCategoriesCount() {
    const count = $(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']:checked").length;

    const marks_limits = $(".edit_section > .categories .marks_limits");
    const my_symbols_span = marks_limits.find(".my_symbols");
    const filled_bar = marks_limits.find(".filler_bar");

    window.changeProgressBarProps(filled_bar, my_symbols_span, 0, 10, count);

    if (count >= 10) {
        $(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']:not(:checked)").attr("disabled", true);
    } else {
        $(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']").removeAttr("disabled");
    }
}


$(".edit_section > .categories > .categories_list > .title_and_list input[type='checkbox']").on("input", function () {
    setChoosedCategoriesCount();
});

setChoosedCategoriesCount();