function readURL(input, place_target) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            place_target.attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

const new_steps = $('.edit_section > .step_photos > .steps_list > .step_item');
for (let i = 0; i < new_steps.length; i++) {
    $(new_steps[i]).attr("data-order", i + 1);
    $(new_steps[i]).find(".action_item").attr("data-order", i + 1);
}

// Функция для обновления порядка фотографий
function updateStepsOrder() {
    const new_steps = $('.edit_section > .step_photos > .steps_list > .step_item');
    for (let i = 0; i < new_steps.length; i++) {
        $(new_steps[i]).attr("data-order", i + 1);
        // $(new_steps[i]).find("label").attr("for", `id_text_${i+1}`);
        $(new_steps[i]).find("textarea").attr("name", `text_${i + 1}`);
        $(new_steps[i]).find(".step_id_input").attr("name", `step_id_${i + 1}`);
        $(new_steps[i]).find(".action_item").attr("data-order", i + 1);
        $(new_steps[i]).find(".image_input").attr("name", `step_image_${i + 1}`);
        $(new_steps[i]).find('h3').html(`Шаг ${i + 1}`);
    }
}

// Инициализация SortableJS
const stepsList = $('.edit_section > .step_photos > .steps_list')[0];
const sortable_steps = new Sortable(stepsList, {
    animation: 150, // Анимация перетаскивания
    ghostClass: 'sortable-ghost', // Класс для элемента-призрака
    chosenClass: 'sortable-chosen', // Класс для выбранного элемента
    dragClass: 'sortable-drag', // Класс для перетаскиваемого элемента
    handle: '.move_bar',
    onEnd: function (evt) {
        updateStepsOrder();
    }
});

function updateReadyPhotosOrder() {
    const new_steps = $('.edit_section > .ready_dish_photo > .photo_list > .photo_item');
    console.log(new_steps);
    for (let i = 0; i < new_steps.length; i++) {
        console.log($(new_steps[i]).find(".image_input").attr("name"));
        $(new_steps[i]).attr("data-order", i + 1);
        $(new_steps[i]).find(".action_item").attr("data-order", i + 1);
        $(new_steps[i]).find(".image_input").attr("name", `preview_${i + 1}`);
        $(new_steps[i]).find(".existing_preview_position").attr("name", `existing_preview_position_${i + 1}`);
        $(new_steps[i]).find('h3').html(`Шаг ${i + 1}`);
    }
}

// Инициализация SortableJS
const photosList = $('.edit_section > .ready_dish_photo > .photo_list')[0];
const sortable_photos = new Sortable(photosList, {
    animation: 150, // Анимация перетаскивания
    ghostClass: 'sortable-ghost', // Класс для элемента-призрака
    chosenClass: 'sortable-chosen', // Класс для выбранного элемента
    dragClass: 'sortable-drag', // Класс для перетаскиваемого элемента
    handle: '.move_bar',
    onEnd: function (evt) {
        updateReadyPhotosOrder();
    }
});

function addRecipeStep(add_button) {
    const data_url = add_button.attr("data-url");
    const next_item_number = $(".edit_section > .step_photos > .steps_list > .step_item").length + 1;

    if (next_item_number >= 20) {
        add_button.attr("disabled", "disabled");
    }

    $.ajax({
        url: data_url,
        method: "GET",
        data: {
            next_item_number: next_item_number,
        },
        success: function (data) {
            if (!data.overflow) {
                $(".edit_section > .step_photos > .steps_list").append(data.html_data);
                setChangeStepImageEventHandler();
                setClickStepImageEventHandler();
                setDeleteStepEventHandler();

            }
        },
        error: function (error) {
            console.error("Ошибка:", error);
        }
    });
}

$(".edit_section > .step_photos > .add_step_button").on("click", function () {
    addRecipeStep($(this));
});


function setChangeStepImageEventHandler() {
    $(".edit_section > .step_photos > .steps_list > .step_item > .content > .photo_wrapper > .image_wrapper > .image_input").off("change").on("change", function () {
        readURL(this, $(this).closest(".image_wrapper").find(".back_image"));
    });
}
function setDeleteStepEventHandler() {
    $(".edit_section > .step_photos > .steps_list > .step_item > .content > .photo_wrapper > .image_wrapper > .delete_and_change > .delete").off("click").on("click", function () {
        const step_list = $(`.edit_section > .step_photos > .steps_list`);
        const item = step_list.find(`.step_item[data-order=${$(this).attr("data-order")}]`);
        const item_id = item.attr("data-id");

        step_list.attr("data-delete-ids", step_list.attr("data-delete-ids") + item_id + ',');
        $(".edit_section > .step_photos > .add_step_button").removeAttr("disabled");

        item.css("height", `${item.height()}px`);
        setTimeout(() => {
            item.css("height", 0);
        }, 1);
        item.css("opacity", 0);
        setTimeout(() => {
            item.remove();
            updateStepsOrder();
        }, 300);
    })
}
function setClickStepImageEventHandler() {
    $(".edit_section > .step_photos > .steps_list > .step_item > .content > .photo_wrapper > .image_wrapper > .delete_and_change > .change").off("click").on("click", function () {
        $(this).closest(".image_wrapper").find(".image_input").click();
    })
}

setChangeStepImageEventHandler();
setClickStepImageEventHandler();
setDeleteStepEventHandler();


function addReadyPhoto() {
    const data_url = $(".edit_section > .ready_dish_photo > .add_photo_button").attr("data-url");
    const next_item_number = $(".edit_section > .ready_dish_photo > .photo_list > *").length + 1;

    $.ajax({
        url: data_url,
        method: "GET",
        data: {
            next_item_number: next_item_number,
        },
        success: function (data) {
            if (!data.overflow) {
                $(".edit_section > .ready_dish_photo > .photo_list").append(data.html_data);
                setChangeReadyImageEventHandler();
                setDeleteReadyImageEventHandler();
                setClickReadyImageImageEventHandler();

                if ($(".edit_section > .ready_dish_photo > .photo_list > .photo_item").length >= 3) {
                    $(".edit_section > .ready_dish_photo > .add_photo_button").addClass("d_none");
                }
            }
        },
        error: function (error) {
            console.error("Ошибка:", error);
        }
    });
}

$(".edit_section > .ready_dish_photo > .add_photo_button").on("click", function () {
    addReadyPhoto();
});


function setChangeReadyImageEventHandler() {
    $(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .image_input").off("change").on("change", function () {
        readURL(this, $(this).closest(".image_wrapper").find(".back_image"));
    });
}

function setDeleteReadyImageEventHandler() {
    $(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .delete_and_change > .delete").off("click").on("click", function () {
        const item = $(this).closest(".photo_item");
        if ($(".edit_section > .ready_dish_photo > .photo_list > .photo_item").length > 1) {
            item.css("width", `${item.width()}px`);
            setTimeout(() => {
                item.css("width", 0);
            }, 1);
            item.css("opacity", 0);
            setTimeout(() => {
                item.remove();
                updateReadyPhotosOrder();
            }, 300);
        } else {
            item.remove();
        }
        $(".edit_section > .ready_dish_photo > .add_photo_button").removeClass("d_none");
    })
}
function setClickReadyImageImageEventHandler() {
    $(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .delete_and_change > .change").off("click").on("click", function () {
        $(this).closest(".image_wrapper").find(".image_input").click();
    })
}

setChangeReadyImageEventHandler();
setDeleteReadyImageEventHandler();
setClickReadyImageImageEventHandler();