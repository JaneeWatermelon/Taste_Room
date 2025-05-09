$(document).ready(function () {
    function setAutocompleteIngredientsEventHandler() {
        $("#ingredient-search").off("input").on("input", function () {
            const $this = $(this);
            const data_term = $this.val(); // ID рецепта
            const data_url = $this.attr("data-url"); // ID рецепта

            // Отправляем AJAX-запрос
            $.ajax({
                url: data_url, // URL для загрузки комментариев
                method: "GET",
                data: {
                    data_term: data_term,
                },
                success: function (data) {
                    console.log("added");
                    $("#ingredients_choices").html("");
                    let result_str = '';
                    data.ingredients_choices.forEach(element => {
                        result_str += `<option data-id="${element.id}" value="${element.value}">`;
                    });
                    $("#ingredients_choices").html(result_str);
                },
                error: function (error) {
                    console.error("Ошибка при загрузке ингредиентов:", error);
                },
            });
        });
    }

    setAutocompleteIngredientsEventHandler();

    function setAddIngredientsEventHandler() {
        $("#ingredient-search").off("change").on("change", function () {
            const $this = $(this);
            const data_id = $(`#ingredients_choices > option[value='${$this.val()}']`).attr("data-id"); // ID рецепта
            const data_url = $this.attr("data-url-click"); // ID рецепта
            const next_item_number = $("#ingredients-container > *").length + 1; // ID рецепта

            // Отправляем AJAX-запрос
            $.ajax({
                url: data_url, // URL для загрузки комментариев
                method: "GET",
                data: {
                    data_id: data_id,
                    next_item_number: next_item_number,
                },
                success: function (data) {
                    $this.val("");
                    $("#ingredients_choices").html("");
                    $("#ingredients-container").append(data.html_data);
                    delete_ingredient_event_handler();
                },
                error: function (error) {
                    console.error("Ошибка при загрузке ингредиентов:", error);
                },
            });
        });
    }

    setAddIngredientsEventHandler();

    function reorder_ingredients() {
        const ingredients_list = $("#ingredients-container > *");
        for (let i = 0; i < ingredients_list.length; i++) {
            let item = $(ingredients_list[i]);
            item.find(".order").html(`${i + 1}.`);
            item.find(".ingredient_id_input").attr('name', `ingredient_id_${i + 1}`);
            item.find(".ingredient_checkbox_input").attr('name', `ingredient_checkbox_${i + 1}`);
            item.find(".input_wrapper > input").attr('name', `ingredient_count_${i + 1}`);
            item.find(".input_wrapper > select").attr('name', `ingredient_measurement_${i + 1}`);
            item.find(".recipe_ingredient_id_input").attr('name', `recipe_ingredient_id_${i + 1}`);
        }
        delete_ingredient_event_handler();
    }

    function delete_ingredient_event_handler() {
        $(".ingredient_item > .trash_icon").off("click").on("click", function () {
            const item = $(this).closest(".ingredient_item");
            $("#ingredients-container").attr("data-delete-ids", $("#ingredients-container").attr("data-delete-ids") + item.find(".recipe_ingredient_id_input").val() + ',');
            console.log(item);
            item.remove();
            reorder_ingredients();
        })
    }
    delete_ingredient_event_handler();
});

$("form.edit_section").on("submit", function (event) {
    event.preventDefault();
    const $this = $(this);
    const data_url = $this.attr("action"); // ID рецепта

    const button = $(document.activeElement);
    const isPublish = button.attr('name') === 'publish';

    const formData = new FormData(this);

    formData.append("ingredients_count", $(".edit_section > .ingredients_and_portions > .ingredients > .ingredient_item").length);
    formData.append("delete_step_ids", $(".edit_section > .step_photos > .steps_list").attr("data-delete-ids"));
    formData.append("delete_recipe_ingredient_ids", $("#ingredients-container").attr("data-delete-ids"));
    if (isPublish) {
        formData.append("publish", true);
    }
    else {
        formData.append("save", true);
    }

    // Отправляем AJAX-запрос
    $.ajax({
        url: data_url, // URL для загрузки комментариев
        method: "POST",
        data: formData,
        processData: false, // Не обрабатывать данные
        contentType: false, // Не устанавливать тип содержимого
        success: function (data) {
            if (data.redirect) {
                window.location.href = data.url;  // Перенаправление в браузере
            } else {
                console.log("added");
                $(".edit_section > .step_photos > .steps_list").attr("data-delete-ids", "");
                $("#ingredients-container").attr("data-delete-ids", "");
                Object.keys(data.new_step_ids).forEach(name => {
                    $(`input[name='${name}']`).prop("value", `${data.new_step_ids[name]}`);
                });
            }
        },
        error: function (error) {
            console.error("Ошибка:", error);
        },
    });
})