let profile_chapters_height = $(".profile_chapters").height();
console.log(profile_chapters_height);

const COLORS = [
    "#D68C45",
    "#E9A96D",
    "#FFCD9C",
    "#4C956C",
    "#C7E580",
    "#50DA8C",
    "#FF6766",
    "#FF7BAC",
    "#FFC9B9",
]

const color_items = $(".settings_section .background > .colors > .color_item");
const color_items2 = $(".profile_window.back_fon > .background > .colors > .color_item");

for (let i = 0; i < 9; i++) {
    $(color_items[i]).css({
        "background-color": COLORS[i],
    })
    $(color_items2[i]).css({
        "background-color": COLORS[i],
    })
}

$(".profile_chapters > .line").css('height', `${profile_chapters_height}px`);

let max_width = 0;

// $(".subs_section > .subs_wrapper > .subs_item > .sub_button").toArray().forEach(element => {
//     if ($(element).width() > max_width) {
//         max_width = $(element).width();
//     }
// });

// $(".subs_section > .subs_wrapper > .subs_item > .sub_button").css("width", `${max_width}px`);

$(".profile_chapters > .chapter_wrapper > h4").on("click", function() {
    $this = $(this);
    all_buttons = $(".profile_chapters > .chapter_wrapper > h4");
    linked_block = $(`#${$this.attr("data-for")}`);
    possible_blocks = $(".possible_block");

    if (!$this.hasClass("active")) {
        all_buttons.removeClass("active");
        $this.addClass("active");
        
        possible_blocks.addClass("d_none");
        linked_block.removeClass("d_none");
    }
})
$("#my_recipes_section > .publish_types > .publish_type_item").on("click", function() {
    $this = $(this);
    all_buttons = $("#my_recipes_section > .publish_types > .publish_type_item");

    if (!$this.hasClass("active")) {
        all_buttons.removeClass("active");
        $this.addClass("active");

        data_url = $this.parent().attr("data-url");
        data_status = $this.attr("data-status");

        $.ajax({
            url: data_url,
            method: 'GET',
            data: {
                data_status: data_status,
            },
            success: function (data) {
                $("#my_recipes_section > .cards_wrapper").html(data.html);

                window.setCardShareWindows();
                window.setCardIngredientAndCooktimeWindows();

                console.log('Ответ сервера:', data["answer"]);
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
})
$(".articles_section > .publish_types > .publish_type_item").on("click", function() {
    $this = $(this);
    all_buttons = $(".articles_section > .publish_types > .publish_type_item");

    if (!$this.hasClass("active")) {
        all_buttons.removeClass("active");
        $this.addClass("active");

        data_url = $this.parent().attr("data-url");
        data_status = $this.attr("data-status");

        $.ajax({
            url: data_url,
            method: 'GET',
            data: {
                data_status: data_status,
            },
            success: function (data) {
                $(".articles_section > .cards_wrapper").html(data.html);
                console.log('Ответ сервера:', data["answer"]);
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
})