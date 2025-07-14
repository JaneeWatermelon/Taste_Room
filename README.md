# Сайт рецептов

Этот проект — сайт для обмена и поиска рецептов, основной задачей которого являлось создание удобного и визуально понятного интерфейса по сравнению с сайтами аналогами.

![Главная страница](https://github.com/user-attachments/assets/ead9acb7-7f9a-4c7d-b7a5-a7fd49a77834)

## Технологии
- **Django** — основной backend-фреймворк
- **HTML, CSS, JavaScript** — фронтенд
- **PostgreSQL** — база данных
- **Redis** — кэширование и брокер сообщений
- **Celery** — асинхронные задачи (Отправка email с кодом для сброса пароля)

## Возможности
- Регистрация и аутентификация пользователей
- Детальные user-friendly формы для добавления, редактирования и удаления рецептов
- Поиск и фильтрация рецептов по названию и ингредиентам
- Комментарии и рейтинги

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/JaneeWatermelon/Taste_Room.git
   cd taste_room
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Примените миграции:
   ```bash
   python manage.py migrate
   ```
4. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```
5. Запустите Redis и Celery:
   ```bash
   redis-server
   celery -A taste_room worker -l info
   ```
