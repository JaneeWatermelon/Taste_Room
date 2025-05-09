function readURL(input, place_target) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            place_target.attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

function setDeletePhotoEventHandler() {
    $(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .delete_and_change > .delete").off("click").on("click", function () {
        const item = $(this).closest(".photo_item");
        item.attr("data-deleted", true);

        // Устанавливаем дефолтное изображение
        item.find('.back_image').attr('src', default_load_image);
        
        // Очищаем input файла
        item.find('.image_input').val('');
    })
}
function setClickChangePhotoEventHandler() {
    $(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .delete_and_change > .change").off("click").on("click", function () {
        $(this).closest(".image_wrapper").find(".image_input").click();
    })
}

function setChangePhotoEventHandler() {
    $(".edit_section > .ready_dish_photo > .photo_list > .photo_item > .photo_wrapper > .image_wrapper > .image_input").off("change").on("change", function () {
        readURL(this, $(this).closest(".image_wrapper").find(".back_image"));
    });
}

setDeletePhotoEventHandler();
setClickChangePhotoEventHandler();
setChangePhotoEventHandler();