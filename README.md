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

## Как пользоваться

1. Откройте `https://localhost:8000`
2. Войдите под администратором
3. Перейдите в `Управление пользователями` и создайте аккаунты
4. Загрузите книги через страницу `Загрузка`
5. Слушайте и отслеживайте прогресс
