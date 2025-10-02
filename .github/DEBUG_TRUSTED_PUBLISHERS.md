# Отладка PyPI Trusted Publishers

## Проблема: "invalid-publisher"

Если вы получаете ошибку `invalid-publisher`, это означает, что PyPI не может найти соответствующий Trusted Publisher.

## Claims из ошибки

Из вашей ошибки видно следующие claims:
```
* `sub`: `repo:vpuhoff/simple-backup-tool:ref:refs/tags/v0.1.2`
* `repository`: `vpuhoff/simple-backup-tool`
* `repository_owner`: `vpuhoff`
* `repository_owner_id`: `2313869`
* `workflow_ref`: `vpuhoff/simple-backup-tool/.github/workflows/auto-release.yml@refs/tags/v0.1.2`
* `job_workflow_ref`: `vpuhoff/simple-backup-tool/.github/workflows/auto-release.yml@refs/tags/v0.1.2`
* `ref`: `refs/tags/v0.1.2`
```

## Правильная настройка в PyPI

1. **Зайдите на [PyPI](https://pypi.org)**
2. **Account Settings → Trusted Publishers**
3. **"Add a new pending publisher"**
4. **Заполните точно так:**

### Основные параметры:
- **Project name**: `simple-backup`
- **Owner**: `vpuhoff` (точно как в `repository_owner`)
- **Repository name**: `simple-backup-tool` (точно как в `repository`)

### Workflow параметры:
- **Workflow filename**: `auto-release.yml` ⚠️ **ТОЛЬКО ИМЯ ФАЙЛА!**
- **Environment name**: оставьте **ПУСТЫМ** (не указывайте никакое окружение)

**КРИТИЧЕСКИ ВАЖНО**: В поле "Workflow filename" нужно указывать только имя файла `auto-release.yml`, а НЕ полный путь `.github/workflows/auto-release.yml`!

### Дополнительные проверки:
- ✅ Убедитесь, что проект `simple-backup` уже существует на PyPI
- ✅ Убедитесь, что вы владелец репозитория `vpuhoff/simple-backup-tool`
- ✅ Убедитесь, что workflow файл существует по пути `.github/workflows/auto-release.yml`

## Альтернативное решение

Если Trusted Publishers не работают, можно использовать старый способ с API токеном:

1. **PyPI → Account Settings → API tokens**
2. **Create API token** с правами на загрузку
3. **GitHub → Settings → Secrets → Actions**
4. **Добавить секрет**: `PYPI_API_TOKEN` = ваш токен
5. **Вернуть старый workflow** с `TWINE_USERNAME` и `TWINE_PASSWORD`

## Проверка статуса

После настройки Trusted Publisher:
1. Проверьте статус в PyPI → Trusted Publishers
2. Должен быть статус "Active" или "Pending"
3. Создайте новый тег для тестирования: `git tag v0.1.3 && git push origin v0.1.3`
