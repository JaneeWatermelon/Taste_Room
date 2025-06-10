$(document).ready(function () {
    function setAutocompleteIngredientsEventHandler() {
        const $input = $("#ingredient-search");
        const data_url = $input.attr("data-url");
        let isProcessing = false;

        // Удаляем старые обработчики и datalist (если был)
        $input.off("input").autocomplete({
            source: function(request, response) {
                if (isProcessing) return;
                isProcessing = true;

                $.ajax({
                    url: data_url,
                    method: "GET",
                    data: { data_term: request.term },
                    success: function(data) {
                        // Преобразуем данные для Autocomplete
                        const suggestions = data.ingredients_choices.map(item => ({
                            label: item.value,  // Отображаемый текст
                            value: item.value,  // Значение для input
                            id: item.id         // Дополнительные данные
                        }));
                        response(suggestions);
                    },
                    error: function(error) {
                        console.error("Ошибка:", error);
                        response([]); // Возвращаем пустой список при ошибке
                    },
                    complete: function() {
                        isProcessing = false;
                    }
                });
            },
            minLength: 2, // Минимальное количество символов для запроса
            select: function(event, ui) {
                // Обработка выбора элемента
                console.log("Выбран ингредиент:", ui.item.label, "ID:", ui.item.id);
                const data_url = $input.attr("data-url-click"); // ID рецепта
                const next_item_number = $("#ingredients-container > *").length + 1; // ID рецепта

                // Отправляем AJAX-запрос
                $.ajax({
                    url: data_url, // URL для загрузки комментариев
                    method: "GET",
                    data: {
                        data_id: ui.item.id,
                        next_item_number: next_item_number,
                    },
                    success: function (data) {
                        $input.val("");
                        $("#ingredients_choices").html("");
                        $("#ingredients-container").append(data.html_data);
                        delete_ingredient_event_handler();
                    },
                    error: function (error) {
                        console.error("Ошибка при загрузке ингредиентов:", error);
                    },
                });
            },
            focus: function(event, ui) {
                // Предотвращаем автоматическую подстановку значения при фокусировке
                event.preventDefault();
            }
        });

        // Стилизация для мобильных устройств
        $input.autocomplete("instance")._renderItem = function(ul, item) {
            return $("<li>")
                .append(`<div>${item.label}</div>`)
                .appendTo(ul);
        };
    }

    setAutocompleteIngredientsEventHandler();

    function reorder_ingredients() {
        const ingredients_list = $("#ingredients-container > *");
        for (let i = 0; i < ingredients_list.length; i++) {
            let item = $(ingredients_list[i]);
            item.find(".order").html(`${i + 1}.`);
            item.find(".ingredient_id_input").attr('name', `ingredient_id_${i + 1}`);
            item.find(".ingredient_checkbox_input").attr('name', `ingredient_checkbox_${i + 1}`);
            item.find(".settings > input").attr('name', `ingredient_count_${i + 1}`);
            item.find(".settings > select").attr('name', `ingredient_measurement_${i + 1}`);
            item.find(".recipe_ingredient_id_input").attr('name', `recipe_ingredient_id_${i + 1}`);
        }
        delete_ingredient_event_handler();
    }

    function delete_ingredient_event_handler() {
        $(".ingredient_item button[name='button_remove_recipe_ingredient']").off("click").on("click", function () {
            const item = $(this).closest(".ingredient_item");
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

    console.log(data_url);

    const button = $(document.activeElement);
    const isPublish = button.attr('name') === 'publish';

    const formData = new FormData(this);

    formData.append("ingredients_count", $(".edit_section > .ingredients_and_portions > .ingredients > .ingredient_item").length);
    formData.append("steps_count", $(".edit_section > .step_photos > .steps_list > .step_item").length);
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
                if (data.is_published) {
                    window.reloadPage("recipe_in_moderation_message", data.url);
                } 
                else {
                    window.location.href = data.url;
                }
            } else {
                console.log("added");
                location.reload();
            }
        },
        error: function (error) {
            console.error("Ошибка:", error);
        },
    });
})