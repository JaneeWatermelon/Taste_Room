$("form.edit_section").on("submit", function (event) {
  event.preventDefault();
  const $this = $(this);
  const data_url = $this.attr("action"); // ID рецепта

  const button = $(document.activeElement);
  const isPublish = button.attr('name') === 'publish';

  const formData = new FormData(this);
  const photo_item =  $(".edit_section > .ready_dish_photo > .photo_list > .photo_item");
  if (photo_item.attr("data-deleted") != undefined) {
    formData.append("preview_deleted", $(".edit_section > .ready_dish_photo > .photo_list > .photo_item").attr("data-deleted"));
  }

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
        console.log("done");
      }
    },
    error: function (error) {
      console.error("Ошибка:", error);
    },
  });
})