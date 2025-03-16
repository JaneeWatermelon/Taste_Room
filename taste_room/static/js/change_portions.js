const portions_buttons_wrapper = $(".recipe_section > .recipe_ingredients > .title_and_portions > .portions > .counter");
const default_portions_number = Number($("#portions_number").html());

portions_buttons_wrapper.on("click", "button", function() {
    const button_id = $(this).attr("id");
    const recipe_id = portions_buttons_wrapper.attr("data-id");
    const data_url = portions_buttons_wrapper.attr("data-url");
    const CSRF_TOKEN = $('meta[name="csrf-token"]').attr("content");

    let old_number = Number($("#portions_number").html());
    let new_number;
    let can_send_ajax = true;

    if (button_id == "minus_portions_button") {
        if (old_number > 1) {
            $("#portions_number").html(old_number-1);
            new_number = old_number-1;
        }
        else {
            can_send_ajax = false;
        }
    }
    else {
        $("#portions_number").html(old_number+1);
        new_number = old_number+1;
    }

    if (default_portions_number != new_number) {
        $(".recipe_section > .recipe_warning").show();
    }
    else {
        $(".recipe_section > .recipe_warning").hide();
    }

    if (can_send_ajax) {
        $.ajax({
            url: data_url,
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
            data: {
                new_portions: new_number,
                recipe_id: recipe_id,
            },
            success: function (data) {
                console.log('Ответ сервера:', data["answer"]);
                const ingredientsList = $(".recipe_section > .recipe_ingredients > .ingredients");
                ingredientsList.html(
                    data.ingredients.map(ingredient => `
                        <div class="ingredient_item">
                            <div class="image_wrapper">
                                <img src="${ingredient.icon || default_ingredient_icon}">
                            </div>
                            <h4>${ingredient.title} - ${ingredient.quantity} ${ingredient.unit}</h4>
                        </div>
                    `).join('')
                );
//                $(".recipe_section > .recipe_ingredients > .ingredients").load(window.location.href + " .recipe_section > .recipe_ingredients > .ingredients > *");
            },
            error: function (error) {
                console.error('Ошибка:', error);
            },
        });
    }
})