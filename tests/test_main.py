#!/usr/bin/env python3
"""
Тесты для главного модуля main.py
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest

# Мокаем переменные окружения
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Мокаем переменные окружения"""
    with patch.dict(os.environ, {
        'PGHOST': 'localhost',
        'PGPORT': '5432',
        'PGDATABASE': 'test_db',
        'PGUSER': 'test_user',
        'PGPASSWORD': 'test_password',
        'SUPERJOB_API_KEY': 'test_key',
        'CACHE_TTL': '3600',
        'LOG_LEVEL': 'INFO'
    }):
        yield


class TestMainModule:
    """Тесты для главного модуля main.py"""
    
    def test_main_module_imports(self):
        """Тест импорта модулей в main.py"""
        # Мокаем EnvLoader
        with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
            mock_env_loader.load_env_file.return_value = None
            
            # Мокаем user_interface.main
            with patch('src.user_interface.main') as mock_main:
                mock_main.return_value = None
                
                # Импортируем main.py
                import main
                
                # Проверяем, что EnvLoader.load_env_file был вызван
                mock_env_loader.load_env_file.assert_called_once()
    
    def test_main_module_path_setup(self):
        """Тест настройки путей в main.py"""
        original_path = sys.path.copy()
        
        try:
            # Мокаем EnvLoader
            with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
                mock_env_loader.load_env_file.return_value = None
                
                # Мокаем user_interface.main
                with patch('src.user_interface.main') as mock_main:
                    mock_main.return_value = None
                    
                    # Импортируем main.py
                    import main
                    
                    # Проверяем, что корневая директория добавлена в sys.path
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(current_dir)
                    assert project_root in sys.path
                    
        finally:
            # Восстанавливаем оригинальный sys.path
            sys.path = original_path
    
    def test_main_module_env_loading(self):
        """Тест загрузки переменных окружения"""
        with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
            mock_env_loader.load_env_file.return_value = None
            
            with patch('src.user_interface.main') as mock_main:
                mock_main.return_value = None
                
                import main
                
                # Проверяем, что EnvLoader.load_env_file был вызван
                mock_env_loader.load_env_file.assert_called_once()
    
    def test_main_module_user_interface_import(self):
        """Тест импорта user_interface.main"""
        with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
            mock_env_loader.load_env_file.return_value = None
            
            with patch('src.user_interface.main') as mock_main:
                mock_main.return_value = None
                
                import main
                
                # Проверяем, что user_interface.main доступен
                assert hasattr(main, 'main')
    
    def test_main_module_sys_path_modification(self):
        """Тест модификации sys.path"""
        original_path = sys.path.copy()
        
        try:
            with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
                mock_env_loader.load_env_file.return_value = None
                
                with patch('src.user_interface.main') as mock_main:
                    mock_main.return_value = None
                    
                    import main
                    
                    # Проверяем, что sys.path был модифицирован
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(current_dir)
                    
                    # Проверяем, что корневая директория проекта добавлена в начало sys.path
                    assert sys.path[0] == project_root
                    
        finally:
            sys.path = original_path
    
    def test_main_module_file_path_handling(self):
        """Тест обработки путей к файлам"""
        with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
            mock_env_loader.load_env_file.return_value = None
            
            with patch('src.user_interface.main') as mock_main:
                mock_main.return_value = None
                
                with patch('os.path.dirname') as mock_dirname:
                    with patch('os.path.abspath') as mock_abspath:
                        mock_abspath.return_value = '/test/path/main.py'
                        mock_dirname.return_value = '/test/path'
                        
                        import main
                        
                        # Проверяем, что os.path функции были вызваны
                        mock_abspath.assert_called()
                        mock_dirname.assert_called()
    
    def test_main_module_conditional_execution(self):
        """Тест условного выполнения в main.py"""
        with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
            mock_env_loader.load_env_file.return_value = None
            
            with patch('src.user_interface.main') as mock_main:
                mock_main.return_value = None
                
                # Мокаем __name__ для проверки условного выполнения
                with patch('builtins.__name__', '__main__'):
                    import main
                    
                    # Проверяем, что main функция доступна
                    assert callable(main.main)
    
    def test_main_module_complete_flow(self):
        """Тест полного потока выполнения main.py"""
        with patch('src.utils.env_loader.EnvLoader') as mock_env_loader:
            mock_env_loader.load_env_file.return_value = None
            
            with patch('src.user_interface.main') as mock_main:
                mock_main.return_value = None
                
                # Импортируем main.py
                import main
                
                # Проверяем все необходимые атрибуты
                assert hasattr(main, 'main')
                assert callable(main.main)
                
                # Проверяем, что все моки были вызваны
                mock_env_loader.load_env_file.assert_called_once()