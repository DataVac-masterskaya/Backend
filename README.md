
# Проект "DataVac"
Backend на Django DRF для веб-сайта.

## 🛠️ Старт локальной разработки в Docker

### Создаем файл с переменными окружения простым копированием шаблона:
```bash
cp .env.example .env
```

### Запуск сервисов:
*Если локальных `docker images` нет — они будут загружены из DockerHub или собраны автоматически.*
```bash
docker compose up -d
```

### Применяем миграции и создаем суперпользователя на чистой базе:
```bash
docker compose exec -it web python backend/manage.py migrate
docker compose exec -it web python backend/manage.py createsuperuser
```

### Доступ к приложению
* Откройте http://localhost:8000/ в браузере

## Работа с API

После запуска проекта документация API доступна по адресам:

* Swagger UI: http://localhost:8000/api/docs/
* OpenAPI schema JSON: http://localhost:8000/api/schema/

Swagger UI поддерживает выполнение запросов через `Try it out`. Для авторизованных
эндпоинтов нажмите `Authorize` и передайте токен в формате:

```text
Bearer <token>
```

Окно `Authorize` не выполняет вход пользователя и не проверяет токен при вводе.
Swagger UI только сохраняет это значение и добавляет его в заголовок
`Authorization` при запросах через `Try it out`. Проверка токена выполняется на
стороне API для защищённых эндпоинтов.

Скачать OpenAPI-схему можно из браузера по адресу
http://localhost:8000/api/schema/ или командой:

```bash
curl -o openapi-schema.json http://localhost:8000/api/schema/
```

## Установка новых зависимостей
### Запускаем uv внутри временного контейнера с правами root 
```bash
docker compose run --rm --user root web uv add <python_package_name>
```
При этом будут обновлены pyproject.toml и uv.lock

### Пересобираем образ приложения с новым окружением и рестартуем проект 
```bash
docker compose build web
docker compose up -d
```

## ✅ Проверка кода перед PullRequest

Форматируем:
```bash
docker compose run --rm -it web ruff format
```

Исправляем более существенные проблемы (неиспользуемые импорты и т.п.):
```bash
docker compose run --rm -it web ruff check . --fix
```

Запуск проверок и тестов так же, как в CI/CD
Должен завершится `[ci finished]`:

```bash
docker compose run --rm -it web bash ./docker/django/ci.sh
```


## 🔄 Команды обслуживания и решение проблем

Очистка проекта (удаляет volumes, включая базу данных):
```bash
docker compose down -v
```

Пересборка контейнера (если изменились зависимости или возникли проблемы):
```bash
docker compose build web
docker compose up -d
```


## Импорт противопоказаний

Для импорта противопоказаний из Excel-файла используется команда:

```bash
python manage.py import_contraindications path/to/file.xlsx
```

Файл должен содержать лист contraindications_list с колонками:
``` bash
contraindication_ID

contraindication_name
```

При повторном импорте существующие записи обновляются по contraindication_ID.

## Импорт базы данных

Для импорта базы данных из Excel-файла используется команда:

```bash
docker compose exec -it web python backend/manage.py import_database path/to/file.xlsx
```

Файл должен содержать используемые в команде листы и колонки, иначе выведется ошибка 
и импорт не завершится.

При повторном импорте существующие записи обновляются по old_id.

## ДЛЯ ТЕСТЕРОВ

Для заполнения пустых полей для тестов используется команда:

```bash
docker compose exec -it web python backend/manage.py set_test_db
```
Значения полей задаются исходя из значения id объектов.