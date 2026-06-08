# Family Alib

Локальная веб-система для семейной библиотеки аудиокниг.

## Требования

- Docker и Docker Compose

## Быстрая установка

### Клонируйте репозиторий

```powershell
git clone https://github.com/Timofey06/FamilyAlib.git
cd FamilyAudioLibrary
```

## Запуск через Docker

Выполните:

```powershell
docker compose up --build
```

После запуска приложение будет доступно на:

```text
http://localhost:8000
```

Для остановки и удаления контейнеров:

```powershell
docker compose down
```

## Админский доступ

При первом запуске автоматически создаётся администратор:

- username: `admin`
- password: `admin`

## Опциональные переменные для настройки:

- `DATABASE_URL` - URL базы данных (по умолчанию `sqlite:///data/app.db`)
- `SECRET_KEY` - секретный ключ JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES` - время жизни токена в минутах (по умолчанию `720`)
- `ADMIN_USERNAME` - логин администратора (по умолчанию `admin`)
- `ADMIN_PASSWORD` - пароль администратора (по умолчанию `admin`)

## Как пользоваться

1. Откройте `https://localhost:8000`
2. Войдите под администратором
3. Перейдите в `Управление пользователями` и создайте аккаунты
4. Загрузите книги через страницу `Загрузка`
5. Слушайте и отслеживайте прогресс
