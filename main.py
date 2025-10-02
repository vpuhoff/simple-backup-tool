#!/usr/bin/env python3
"""
Simple Backup - Простой инструмент для создания и восстановления бэкапов проектов.
"""

import click
import yaml
from pathlib import Path
from typing import Dict, Any
import shutil


def should_skip_directory(dir_name: str) -> bool:
    """Проверяет, нужно ли пропустить директорию."""
    skip_dirs = {
        '.venv', '__pycache__', '.git', 'node_modules', 
        '.pytest_cache', '.mypy_cache', 'build', 'dist'
    }
    return dir_name in skip_dirs or dir_name.startswith('.')


def should_include_file(file_path: Path) -> bool:
    """Проверяет, нужно ли включить файл в бэкап."""
    extensions = {'.py', '.md', '.yml', '.yaml', '.txt', '.json', '.toml', '.cfg', '.ini'}
    return file_path.suffix.lower() in extensions


def read_file_content(file_path: Path) -> str:
    """Читает содержимое файла с обработкой ошибок кодировки."""
    encodings = ['utf-8', 'cp1251', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    return f"<ОШИБКА: Не удалось прочитать файл {file_path}>"


def scan_directory(root_path: Path) -> Dict[str, Any]:
    """Сканирует директорию и возвращает структуру проекта."""
    project_structure = {
        'metadata': {
            'root_path': str(root_path.absolute()),
            'backup_date': str(Path().cwd()),
            'total_files': 0,
            'total_directories': 0
        },
        'structure': {}
    }
    
    files_count = 0
    dirs_count = 0
    
    for item in root_path.rglob('*'):
        if item.is_file() and should_include_file(item):
            rel_path = item.relative_to(root_path)
            path_parts = list(rel_path.parts)
            
            current_level = project_structure['structure']
            for i, part in enumerate(path_parts[:-1]):
                if part not in current_level:
                    current_level[part] = {}
                    dirs_count += 1
                current_level = current_level[part]
            
            filename = path_parts[-1]
            content = read_file_content(item)
            current_level[filename] = {
                'type': 'file',
                'content': content,
                'size': item.stat().st_size,
                'modified': item.stat().st_mtime
            }
            files_count += 1
            
        elif item.is_dir() and should_skip_directory(item.name):
            continue
    
    project_structure['metadata']['total_files'] = files_count
    project_structure['metadata']['total_directories'] = dirs_count
    
    return project_structure


def create_directory_structure(base_path: Path, structure: Dict[str, Any]) -> int:
    """Рекурсивно создает структуру директорий и файлов."""
    created_files = 0
    
    for name, content in structure.items():
        current_path = base_path / name
        
        if isinstance(content, dict) and content.get('type') == 'file':
            try:
                current_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(current_path, 'w', encoding='utf-8') as f:
                    f.write(content['content'])
                
                created_files += 1
                click.echo(f"✓ Создан файл: {current_path}")
                
            except Exception as e:
                click.echo(f"✗ Ошибка при создании файла {current_path}: {e}")
                
        elif isinstance(content, dict):
            try:
                current_path.mkdir(parents=True, exist_ok=True)
                click.echo(f"📁 Создана директория: {current_path}")
                
                created_files += create_directory_structure(current_path, content)
                
            except Exception as e:
                click.echo(f"✗ Ошибка при создании директории {current_path}: {e}")
    
    return created_files


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Simple Backup - Простой инструмент для создания и восстановления бэкапов проектов."""
    pass


@cli.command()
@click.argument('output_file', type=click.Path())
@click.option('--path', '-p', default='.', help='Путь к корневой директории проекта')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
def create(output_file, path, verbose):
    """Создать бэкап проекта в YAML файл."""
    root_path = Path(path).resolve()
    
    if not root_path.exists():
        click.echo(f"✗ Ошибка: Директория {root_path} не существует!", err=True)
        raise click.Abort()
    
    if verbose:
        click.echo(f"Сканирование директории: {root_path}")
        click.echo("Исключаемые директории: .venv, __pycache__, .git, node_modules, .pytest_cache, .mypy_cache, build, dist")
        click.echo("Включаемые файлы: .py, .md, .yml, .yaml, .txt, .json, .toml, .cfg, .ini")
    
    try:
        with click.progressbar(length=1, label='Создание бэкапа') as bar:
            project_structure = scan_directory(root_path)
            bar.update(1)
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(project_structure, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, indent=2)
        
        click.echo(f"\n✓ Бэкап создан успешно!")
        click.echo(f"📄 Файл сохранен: {output_path.absolute()}")
        click.echo(f"📊 Статистика:")
        click.echo(f"   - Всего файлов: {project_structure['metadata']['total_files']}")
        click.echo(f"   - Всего директорий: {project_structure['metadata']['total_directories']}")
        click.echo(f"   - Размер YAML файла: {output_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        click.echo(f"✗ Ошибка при создании бэкапа: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--preview', '-p', is_flag=True, help='Показать предварительный просмотр')
@click.option('--force', '-f', is_flag=True, help='Принудительно перезаписать существующую директорию')
def restore(yaml_file, output_dir, preview, force):
    """Восстановить проект из YAML файла."""
    yaml_path = Path(yaml_file)
    output_path = Path(output_dir)
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            project_data = yaml.safe_load(f)
        
        if not project_data or 'structure' not in project_data:
            click.echo("✗ Неверный формат YAML файла!", err=True)
            raise click.Abort()
        
        metadata = project_data.get('metadata', {})
        
        if preview:
            click.echo("🔍 Предварительный просмотр восстановления:")
            click.echo("=" * 50)
            click.echo(f"Оригинальный проект: {metadata.get('root_path', 'неизвестно')}")
            click.echo(f"Дата бэкапа: {metadata.get('backup_date', 'неизвестно')}")
            click.echo(f"Всего файлов: {metadata.get('total_files', 'неизвестно')}")
            click.echo(f"Всего директорий: {metadata.get('total_directories', 'неизвестно')}")
            return
        
        if output_path.exists() and not force:
            if not click.confirm(f"Директория {output_path} уже существует. Удалить и пересоздать?"):
                click.echo("Отменено пользователем")
                return
            else:
                shutil.rmtree(output_path)
                click.echo(f"🗑️  Удалена существующая директория: {output_path}")
        
        click.echo(f"🔄 Восстановление проекта в: {output_path.absolute()}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        with click.progressbar(length=metadata.get('total_files', 1), label='Восстановление файлов') as bar:
            created_files = create_directory_structure(output_path, project_data['structure'])
            bar.update(created_files)
        
        click.echo(f"\n✓ Восстановление завершено!")
        click.echo(f"📊 Статистика:")
        click.echo(f"   - Создано файлов: {created_files}")
        click.echo(f"   - Ожидалось файлов: {metadata.get('total_files', 'неизвестно')}")
        click.echo(f"   - Восстановлено в: {output_path.absolute()}")
        
    except FileNotFoundError:
        click.echo(f"✗ Файл {yaml_path} не найден!", err=True)
        raise click.Abort()
    except yaml.YAMLError as e:
        click.echo(f"✗ Ошибка при чтении YAML файла: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Ошибка при восстановлении: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
