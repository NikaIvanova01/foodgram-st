# Foodgram - Продуктовый помощник

![Foodgram Workflow](https://github.com/username/foodgram-project/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание проекта

"Фудграм" - это веб-приложение, которое позволяет пользователям публиковать рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для выбранных рецептов.

## Функционал

- Регистрация и авторизация пользователей
- Создание, просмотр, редактирование и удаление рецептов
- Фильтрация рецептов по тегам
- Добавление рецептов в избранное
- Подписка на авторов
- Добавление рецептов в список покупок
- Скачивание списка покупок в формате TXT

## Технологии

- **Backend**: Django, Django REST framework, Gunicorn
- **Frontend**: React
- **Database**: PostgreSQL
- **Infrastructure**: Docker, Nginx
- **CI/CD**: GitHub Actions

## Инструкция для ревьюера

### Предварительные требования

- Docker и Docker Compose
- Git

### Шаги по запуску проекта

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/username/foodgram-project.git
   cd foodgram-project
   ```

2. Создайте файл `.env` в директории `infra/` со следующими переменными окружения:
   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=127.0.0.1,localhost
   ```

3. Запустите проект с помощью Docker Compose:
   ```bash
   cd infra
   docker-compose up -d
   ```

4. После запуска контейнеров будут автоматически выполнены:
   - Миграции базы данных
   - Сбор статических файлов
   - Загрузка ингредиентов в базу данных

5. Перейдите по адресу http://localhost для доступа к веб-интерфейсу.

### Доступ к API и документации

- Документация API доступна по адресу http://localhost/api/docs/
- API эндпоинты доступны по адресу http://localhost/api/

### Учетные записи для тестирования

По умолчанию доступен админ-аккаунт:
- Email: admin@example.com
- Пароль: admin

### Управление контейнерами

- Остановка контейнеров:
  ```bash
  docker-compose stop
  ```

- Удаление контейнеров:
  ```bash
  docker-compose down
  ```

### Резервное копирование базы данных

Для создания резервной копии базы данных выполните:
```bash
docker-compose exec db pg_dump -U postgres postgres > backup_$(date +%Y-%m-%d_%H-%M-%S).sql
```

### Восстановление базы данных

Для восстановления базы данных из резервной копии:
```bash
cat backup_file.sql | docker-compose exec -T db psql -U postgres postgres
```

## Сборка и отправка образа на Docker Hub

Для отправки образа в свой Docker Hub репозиторий:
```bash
cd infra
bash build_and_push.sh your_docker_username
```

## CI/CD

Проект настроен для автоматического тестирования, сборки и деплоя с использованием GitHub Actions. При пуше в ветку main/master:
1. Запускаются тесты
2. Собирается Docker-образ и отправляется на Docker Hub
3. Образ деплоится на сервер

## Автор

Your Name

## Лицензия
MIT

