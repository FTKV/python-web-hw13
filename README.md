# python-web-hw13

Домашнє завдання №13

Перша частина
У цьому домашньому завданні ми продовжуємо доопрацьовувати застосунок REST API із домашнього завдання 12.

Завдання

Реалізуйте механізм верифікації електронної пошти зареєстрованого користувача;
Обмежуйте кількість запитів до своїх маршрутів контактів. Обов’язково обмежте швидкість - створення контактів для користувача;
Увімкніть CORS для свого REST API;
Реалізуйте можливість оновлення аватара користувача. Використовуйте сервіс Cloudinary;

Загальні вимоги

Усі змінні середовища повинні зберігатися у файлі .env. Всередині коду не повинно бути конфіденційних даних у «чистому» вигляді;
Для запуску всіх сервісів і баз даних у застосунку використовується Docker Compose;

Додаткове завдання

Реалізуйте механізм кешування за допомогою бази даних Redis. Виконайте кешування поточного користувача під час авторизації;
Реалізуйте механізм скидання паролю для застосунку REST API;

Друга частина
У цьому домашньому завданні необхідно доопрацювати застосунок Django із домашнього завдання 10.

Завдання

Реалізуйте механізм скидання паролю для зареєстрованого користувача;
Усі змінні середовища повинні зберігатися у файлі .env та використовуватися у файлі settings.py;

# Реалізація

Друга частина виконана у проекті ДЗ №10: https://github.com/FTKV/python-web-hw10

Перша частина тут. В т.ч. додаткове завдання. Схема роботи механізму скидання паролю для REST API наступна:

1. POST-запит на /api/auth/request-password-reset-email. Якщо email присутній в базі, буде змінено прапор is_password_valid моделі User на False, що унеможливить аутентифікацію, та буде відправлено на пошту лінк з токеном скидання паролю, який валідний 7 днів, у шляху.

2. GET-запит на /api/auth/reset-password/{token} (лінк у електронному листі) з токеном скидання паролю. Якщо email присутній в базі, прапор is_password_valid встановлений у False та токен скидання паролю валідний, повертається у відповіді токен підтвердження скидання паролю, який валідний 15 хвилин.

3. PATCH-запит на /api/auth/reset-password-confirmation/{token} з токеном підтвердження скидання паролю та тілом з полями username (фактично ігнорується далі при оновленні облікового запису юзера), email та password (яке й буде новим паролем).
   Питання: можливо створити тут нову модель та прибрати поле username?

Для запуску необхідно виконати наступні дії:

1. docker-compose up -d

2. alembic init migrations

3. Add to env:

from src.conf.config import settings
from src.database.models import Base
...
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_url_sync)

4. alembic revision --autogenerate -m "Init"

5. alembic upgrade head

6. python main.py

В корені проекту необхідно створити налаштувати файл .env у такому форматі:

API_HOST=127.0.0.1
API_PORT=8000

SECRET_KEY=...
ALGORITHM=HS256

DATABASE=postgresql
DRIVER_SYNC=psycopg2
DRIVER_ASYNC=asyncpg
POSTGRES_DB=...
POSTGRES_USER=${POSTGRES_DB}
POSTGRES_PASSWORD=...
POSTGRES_HOST=${API_HOST}
POSTGRES_PORT=5432

SQLALCHEMY_DATABASE_URL_SYNC=${DATABASE}+${DRIVER_SYNC}://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
SQLALCHEMY_DATABASE_URL_ASYNC=${DATABASE}+${DRIVER_ASYNC}://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

REDIS_HOST=${API_HOST}
REDIS_PORT=6379

MAIL_SERVER=...
MAIL_PORT=465
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_FROM=...
MAIL_FROM_NAME=Contacts API

CLOUDINARY_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

Щоб записати таблицю в БД, можно обійтись без алембіка, запустивши src/database/create_all.py

Щоб заповнити базу фейковими контактами, змініть тимчасово у src/routes/contacts.py у

@router.post(
"/",
response_model=ContactResponse,
status_code=status.HTTP_201_CREATED,
description="No more than 2 requests per 5 seconds",
dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def create_contact...

параметр times на наприклад, 1000, щоб пом’якшити обмеження Ratelimiter, зареєструйтесь через Swagger або Postman, скопіюйте access_token у src/utils/seed.py, та запустіть. Потім бажано поверніть значення times на 2.
