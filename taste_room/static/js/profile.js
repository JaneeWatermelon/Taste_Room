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

$(".subs_section > .subs_wrapper > .subs_item > .sub_button").toArray().forEach(element => {
    if ($(element).width() > max_width) {
        max_width = $(element).width();
    }
});

$(".subs_section > .subs_wrapper > .subs_item > .sub_button").css("width", `${max_width}px`);