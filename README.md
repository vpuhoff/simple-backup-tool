# Simple Backup

Простой инструмент для создания и восстановления бэкапов проектов в YAML формате.

## Установка

```bash
pip install simple-backup
```

## Использование

### Создание бэкапа

```bash
# Создать бэкап текущей директории
python -m simple-backup create backup.yml

# Создать бэкап конкретной директории
python -m simple-backup create backup.yml --path /path/to/project

# Подробный вывод
python -m simple-backup create backup.yml --verbose
```

### Восстановление из бэкапа

```bash
# Восстановить проект
python -m simple-backup restore backup.yml /path/to/restore

# Предварительный просмотр
python -m simple-backup restore backup.yml /path/to/restore --preview

# Принудительная перезапись
python -m simple-backup restore backup.yml /path/to/restore --force
```

## Примеры использования

### Создание бэкапа проекта
```bash
cd /path/to/your/project
python -m simple-backup create project_backup.yml
```

### Перенос на другой компьютер
1. Скопируйте `project_backup.yml` на другой компьютер
2. Установите simple-backup: `pip install simple-backup`
3. Восстановите проект: `python -m simple-backup restore project_backup.yml /mnt/data/project_folder`

## Поддерживаемые файлы

- `.py` - Python файлы
- `.md` - Markdown файлы
- `.yml`, `.yaml` - YAML файлы
- `.txt` - Текстовые файлы
- `.json` - JSON файлы
- `.toml` - TOML файлы
- `.cfg`, `.ini` - Конфигурационные файлы

## Исключаемые директории

- `.venv`, `__pycache__`, `.git`
- `node_modules`, `.pytest_cache`, `.mypy_cache`
- `build`, `dist`
- Все директории, начинающиеся с `.`

## Особенности

- ✅ Поддержка различных кодировок (UTF-8, CP1251, Latin-1)
- ✅ Сохранение метаданных (размер файлов, дата изменения)
- ✅ Прогресс-бары для длительных операций
- ✅ Цветной вывод и эмодзи для лучшего UX
- ✅ Предварительный просмотр перед восстановлением
- ✅ Безопасная обработка ошибок

## Требования

- Python 3.9+
- PyYAML
- Click

## Разработка

### Установка для разработки

```bash
git clone https://github.com/yourusername/simple-backup.git
cd simple-backup
pip install -e .
```

### Тестирование

```bash
# Локальное тестирование
python -m simple-backup create test_backup.yml
python -m simple-backup restore test_backup.yml test_restore

# Запуск тестов
pytest
```

### CI/CD

Проект использует GitHub Actions для автоматической сборки и публикации:

- **CI**: Автоматическое тестирование на Python 3.9-3.12
- **Release**: Автоматическая публикация на PyPI при создании релиза
- **Auto Release**: Публикация при создании тега `v*`

### Создание релиза

1. Обновите версию в `pyproject.toml`
2. Создайте тег: `git tag v0.1.0 && git push origin v0.1.0`
3. GitHub Actions автоматически опубликует пакет на PyPI

Подробные инструкции в [.github/RELEASE_SETUP.md](.github/RELEASE_SETUP.md)

## Лицензия

MIT License
