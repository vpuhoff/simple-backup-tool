#!/usr/bin/env python3
"""
Тесты для simple-backup
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml

# Импортируем функции из main.py
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import (
    should_skip_directory,
    should_include_file,
    read_file_content,
    scan_directory,
    create_directory_structure
)


class TestUtilityFunctions:
    """Тесты для вспомогательных функций"""
    
    def test_should_skip_directory(self):
        """Тест функции should_skip_directory"""
        assert should_skip_directory('.venv') == True
        assert should_skip_directory('__pycache__') == True
        assert should_skip_directory('.git') == True
        assert should_skip_directory('node_modules') == True
        assert should_skip_directory('.hidden') == True
        assert should_skip_directory('src') == False
        assert should_skip_directory('tests') == False
    
    def test_should_include_file(self):
        """Тест функции should_include_file"""
        assert should_include_file(Path('test.py')) == True
        assert should_include_file(Path('README.md')) == True
        assert should_include_file(Path('config.yml')) == True
        assert should_include_file(Path('data.json')) == True
        assert should_include_file(Path('setup.toml')) == True
        assert should_include_file(Path('config.cfg')) == True
        assert should_include_file(Path('image.jpg')) == False
        assert should_include_file(Path('binary.exe')) == False
    
    def test_read_file_content(self):
        """Тест функции read_file_content"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("Тестовый контент")
            temp_path = Path(f.name)
        
        try:
            content = read_file_content(temp_path)
            assert content == "Тестовый контент"
        finally:
            temp_path.unlink()


class TestDirectoryScanning:
    """Тесты для сканирования директорий"""
    
    def test_scan_empty_directory(self):
        """Тест сканирования пустой директории"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = scan_directory(Path(temp_dir))
            
            assert 'metadata' in result
            assert 'structure' in result
            assert result['metadata']['total_files'] == 0
            assert result['metadata']['total_directories'] == 0
    
    def test_scan_directory_with_files(self):
        """Тест сканирования директории с файлами"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Создаем тестовые файлы
            (temp_path / 'test.py').write_text('print("hello")', encoding='utf-8')
            (temp_path / 'README.md').write_text('# Test', encoding='utf-8')
            (temp_path / 'config.yml').write_text('key: value', encoding='utf-8')
            
            # Создаем файл, который должен быть исключен
            (temp_path / 'image.jpg').write_bytes(b'fake image data')
            
            result = scan_directory(temp_path)
            
            assert result['metadata']['total_files'] == 3
            assert 'test.py' in result['structure']
            assert 'README.md' in result['structure']
            assert 'config.yml' in result['structure']
            assert 'image.jpg' not in result['structure']


class TestDirectoryStructure:
    """Тесты для создания структуры директорий"""
    
    def test_create_simple_structure(self):
        """Тест создания простой структуры"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_path = temp_path / 'output'
            
            structure = {
                'file1.py': {
                    'type': 'file',
                    'content': 'print("hello")',
                    'size': 20,
                    'modified': 1234567890
                },
                'subdir': {
                    'file2.md': {
                        'type': 'file',
                        'content': '# Test',
                        'size': 10,
                        'modified': 1234567890
                    }
                }
            }
            
            created_files = create_directory_structure(output_path, structure)
            
            assert created_files == 2
            assert (output_path / 'file1.py').exists()
            assert (output_path / 'subdir' / 'file2.md').exists()
            assert (output_path / 'file1.py').read_text(encoding='utf-8') == 'print("hello")'
            assert (output_path / 'subdir' / 'file2.md').read_text(encoding='utf-8') == '# Test'


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_overwrite_mode(self):
        """Тест режима перезаписи без удаления директорий"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / 'source'
            backup_path = temp_path / 'backup.yml'
            restore_path = temp_path / 'restore'
            
            # Создаем исходную структуру
            source_path.mkdir()
            (source_path / 'main.py').write_text('print("hello")', encoding='utf-8')
            (source_path / 'README.md').write_text('# Project', encoding='utf-8')
            
            # Создаем бэкап
            project_structure = scan_directory(source_path)
            
            # Сохраняем в YAML
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(project_structure, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False, indent=2)
            
            # Создаем существующую директорию с файлами
            restore_path.mkdir()
            (restore_path / 'existing_file.txt').write_text('existing content', encoding='utf-8')
            (restore_path / 'subdir').mkdir()
            (restore_path / 'subdir' / 'nested.txt').write_text('nested content', encoding='utf-8')
            
            # Восстанавливаем в режиме overwrite
            with open(backup_path, 'r', encoding='utf-8') as f:
                restored_data = yaml.safe_load(f)
            
            created_files = create_directory_structure(restore_path, restored_data['structure'])
            
            # Проверяем, что файлы из бэкапа перезаписаны
            assert created_files == 2
            assert (restore_path / 'main.py').exists()
            assert (restore_path / 'README.md').exists()
            assert (restore_path / 'main.py').read_text(encoding='utf-8') == 'print("hello")'
            assert (restore_path / 'README.md').read_text(encoding='utf-8') == '# Project'
            
            # Проверяем, что существующие файлы остались (не удалены)
            assert (restore_path / 'existing_file.txt').exists()
            assert (restore_path / 'subdir' / 'nested.txt').exists()
            assert (restore_path / 'existing_file.txt').read_text(encoding='utf-8') == 'existing content'
            assert (restore_path / 'subdir' / 'nested.txt').read_text(encoding='utf-8') == 'nested content'
    
    def test_full_backup_restore_cycle(self):
        """Тест полного цикла создания и восстановления бэкапа"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / 'source'
            backup_path = temp_path / 'backup.yml'
            restore_path = temp_path / 'restore'
            
            # Создаем исходную структуру
            source_path.mkdir()
            (source_path / 'main.py').write_text('print("hello")', encoding='utf-8')
            (source_path / 'README.md').write_text('# Project', encoding='utf-8')
            (source_path / 'config').mkdir()
            (source_path / 'config' / 'settings.yml').write_text('debug: true', encoding='utf-8')
            
            # Создаем бэкап
            project_structure = scan_directory(source_path)
            
            # Сохраняем в YAML
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(project_structure, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False, indent=2)
            
            # Восстанавливаем из YAML
            with open(backup_path, 'r', encoding='utf-8') as f:
                restored_data = yaml.safe_load(f)
            
            created_files = create_directory_structure(restore_path, restored_data['structure'])
            
            # Проверяем результат
            assert created_files == 3
            assert (restore_path / 'main.py').exists()
            assert (restore_path / 'README.md').exists()
            assert (restore_path / 'config' / 'settings.yml').exists()
            
            # Проверяем содержимое
            assert (restore_path / 'main.py').read_text(encoding='utf-8') == 'print("hello")'
            assert (restore_path / 'README.md').read_text(encoding='utf-8') == '# Project'
            assert (restore_path / 'config' / 'settings.yml').read_text(encoding='utf-8') == 'debug: true'


if __name__ == '__main__':
    pytest.main([__file__])
