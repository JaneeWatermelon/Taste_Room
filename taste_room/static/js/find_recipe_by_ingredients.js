$(document).ready(function () {
    let plateOrDishTimeOutId;
    
    function showHidePlate(action) {
        clearTimeout(plateOrDishTimeOutId);
        if (action == "show") {
            $(".plate_wrapper").removeClass("d_none");
            setTimeout(function() {
                $(".plate_wrapper").css({
                    "opacity": "1",
                });
            }, 10);

            plateOrDishTimeOutId = setTimeout(function() {
                $(".dishes_wrapper").addClass("d_none");
            }, 300)
        } 
        else {
            $(".dishes_wrapper").removeClass("d_none");
            setTimeout(function() {
                $(".plate_wrapper").css({
                    "opacity": "0",
                });
            }, 10);

            plateOrDishTimeOutId = setTimeout(function() {
                $(".plate_wrapper").addClass("d_none");
            }, 300)
        }
    }

    function removeReadyIngreadient(ingredient) {
        ingredient.remove();
            
        if (!$("#ready_ingredients_container > .ingredient_item").length) {
            showHidePlate("hide");
            $("form#search_by_ingredients_form").find("button").attr("disabled", "disabled");
        }
    }

    function ingredientYesIconVisibility(ingredient_item) {
        ingredient_item.toggleClass("active");
    }
    
    function setAutocompleteIngredientsEventHandler() {
        $("#enter_ingredient_title_input").off("input").on("input", function () {
            const $this = $(this);
            const data_term = $this.val(); // ID рецепта
            const data_url = $this.attr("data-url"); // ID рецепта

            let active_ids_list = [];

            $('#ready_ingredients_container > .ingredient_item').each(function(index, element) {
                const id = $(this).attr('data-id');
                if (id) {
                    active_ids_list.push(id);
                }
            });

            // Отправляем AJAX-запрос
            $.ajax({
                url: data_url, // URL для загрузки комментариев
                method: "GET",
                traditional: true,
                data: {
                    data_term: data_term,
                    active_ids_list: active_ids_list,
                },
                success: function (data) {
                    $("#choices_ingredients_container").html(data.html_data);
                    setAddIngredientsEventHandler();
                },
                error: function (error) {
                    console.error("Ошибка:", error);
                },
            });
        });
    }
    setAutocompleteIngredientsEventHandler();

    function setAddIngredientsEventHandler() {
        $("#choices_ingredients_container > .ingredient_item").off("click").on("click", function () {
            const $this = $(this);
            const is_active = $this.hasClass("active");
            const data_id = $this.attr("data-id"); 
            const data_url = $("#choices_ingredients_container").attr("data-url-click");

            if (is_active) {
                removeReadyIngreadient($(`#ready_ingredients_container > .ingredient_item[data-id=${data_id}]`));
                ingredientYesIconVisibility($this);
            }
            else {
                // Отправляем AJAX-запрос
                $.ajax({
                    url: data_url, // URL для загрузки комментариев
                    method: "GET",
                    data: {
                        data_id: data_id,
                        
                    },
                    success: function (data) {
                        $("#ready_ingredients_container").append(data.html_data);

                        $("form#search_by_ingredients_form").find("button").removeAttr("disabled");
    
                        ingredientYesIconVisibility($this);

                        showHidePlate("show");
    
                        setClickReadyIngredientsEventHandler();
                        setMouseEnterReadyIngredientsEventHandler();
                        setMouseLeaveReadyIngredientsEventHandler();
                    },
                    error: function (error) {
                        console.error("Ошибка:", error);
                    },
                });
            }

        });
    }
    setAddIngredientsEventHandler();

    function setClickReadyIngredientsEventHandler() {
        $("#ready_ingredients_container > .ingredient_item").off("click").on("click", function () {
            const $this = $(this);
            const data_id = $this.attr("data-id"); 
            $(`#choices_ingredients_container > .ingredient_item[data-id=${data_id}]`).removeClass("active");
            removeReadyIngreadient($this);
        });
    }
    setClickReadyIngredientsEventHandler();

    function setMouseEnterReadyIngredientsEventHandler() {
        $("#ready_ingredients_container > .ingredient_item").off("mouseenter").on("mouseenter", function () {
            const $this = $(this);
            $this.addClass("deactive");
        });
    }
    setMouseEnterReadyIngredientsEventHandler();

    function setMouseLeaveReadyIngredientsEventHandler() {
        $("#ready_ingredients_container > .ingredient_item").off("mouseleave").on("mouseleave", function () {
            const $this = $(this);
            $this.removeClass("deactive");
        });
    }
    setMouseLeaveReadyIngredientsEventHandler();

    $("form#search_by_ingredients_form").on("submit", function () {
        let active_ids_list = [];

        $('#ready_ingredients_container > .ingredient_item').each(function(index, element) {
            const id = $(this).attr('data-id');
            if (id) {
                active_ids_list.push(id);
            }
        });
        $("input[name='ingredients_ids']").val(active_ids_list);

    });
});