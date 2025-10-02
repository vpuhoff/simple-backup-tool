# Настройка автоматических релизов

## Настройка PyPI Trusted Publishers (рекомендуется)

### Новый способ через Trusted Publishers (без API токенов!)

1. Зайдите на [PyPI](https://pypi.org) и войдите в аккаунт
2. Перейдите в Account Settings → Trusted Publishers
3. Нажмите "Add a new pending publisher"
4. Заполните форму:
   - **Project name**: `simple-backup`
   - **Owner**: `vpuhoff`
   - **Repository name**: `simple-backup-tool`
   - **Workflow filename**: `.github/workflows/auto-release.yml`
   - **Environment name**: оставьте пустым (или укажите конкретное окружение)
5. Нажмите "Add pending publisher"
6. После этого PyPI будет автоматически публиковать пакеты при запуске workflow

### Старый способ через API Token (если нужен)

1. Зайдите на [PyPI](https://pypi.org) и войдите в аккаунт
2. Перейдите в Account Settings → API tokens
3. Создайте новый API token с правами на загрузку пакетов
4. Скопируйте токен

## Настройка GitHub Secrets (только для старого способа)

1. Перейдите в настройки репозитория GitHub
2. Выберите Settings → Secrets and variables → Actions
3. Добавьте новый секрет:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: ваш PyPI API token

## Создание релиза

### Автоматический релиз (рекомендуется)

1. Обновите версию в `pyproject.toml`
2. Создайте и запушьте тег:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
3. GitHub Actions автоматически:
   - Соберет пакет
   - Загрузит на PyPI
   - Создаст GitHub Release

### Ручной релиз

1. Перейдите в GitHub → Releases
2. Нажмите "Create a new release"
3. Выберите тег или создайте новый
4. Заполните описание релиза
5. Нажмите "Publish release"

## Workflow файлы

- **`.github/workflows/ci.yml`** - тестирование и сборка при push/PR
- **`.github/workflows/release.yml`** - публикация при создании GitHub Release
- **`.github/workflows/auto-release.yml`** - автоматическая публикация при создании тега

## Проверка статуса

Все workflow можно посмотреть в разделе "Actions" на GitHub.
