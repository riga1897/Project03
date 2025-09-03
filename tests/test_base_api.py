#!/usr/bin/env python3
"""
Тесты для модуля base_api.py
"""

import os
import shutil
import logging
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.api_modules.base_api import BaseJobAPI


class MockJobAPI(BaseJobAPI):
    """Мок-реализация абстрактного класса для тестирования"""
    
    def get_vacancies(self, search_query: str, **kwargs):
        """Мок-реализация получения вакансий"""
        return [{"id": "1", "name": "Test Job", "salary": {"from": 100000}}]
    
    def _validate_vacancy(self, vacancy):
        """Мок-реализация валидации вакансии"""
        return "id" in vacancy and "name" in vacancy


class TestBaseJobAPI:
    """Тесты для базового класса BaseJobAPI"""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Тест, что абстрактный класс нельзя создать напрямую"""
        with pytest.raises(TypeError):
            BaseJobAPI()
    
    def test_concrete_implementation_can_be_instantiated(self):
        """Тест, что конкретная реализация может быть создана"""
        api = MockJobAPI()
        assert isinstance(api, BaseJobAPI)
        assert isinstance(api, MockJobAPI)
    
    def test_abstract_methods_are_implemented(self):
        """Тест, что абстрактные методы реализованы"""
        api = MockJobAPI()
        
        # Проверяем, что методы доступны и вызываемы
        assert hasattr(api, 'get_vacancies')
        assert callable(api.get_vacancies)
        assert hasattr(api, '_validate_vacancy')
        assert callable(api._validate_vacancy)
    
    def test_get_vacancies_returns_list(self):
        """Тест, что get_vacancies возвращает список"""
        api = MockJobAPI()
        result = api.get_vacancies("Python developer")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_validate_vacancy_returns_boolean(self):
        """Тест, что _validate_vacancy возвращает boolean"""
        api = MockJobAPI()
        
        valid_vacancy = {"id": "1", "name": "Test Job"}
        invalid_vacancy = {"name": "Test Job"}  # без id
        
        assert api._validate_vacancy(valid_vacancy) is True
        assert api._validate_vacancy(invalid_vacancy) is False
    
    @patch('src.api_modules.base_api.logger')
    @patch('src.api_modules.base_api.os.path.exists')
    @patch('src.api_modules.base_api.os.makedirs')
    def test_clear_cache_existing_directory(self, mock_makedirs, mock_exists, mock_logger):
        """Тест очистки существующего кэша"""
        mock_exists.return_value = True
        
        with patch('src.api_modules.base_api.shutil.rmtree') as mock_rmtree:
            api = MockJobAPI()
            api.clear_cache("hh")
            
            # Проверяем, что папка была удалена и создана заново
            mock_rmtree.assert_called_once_with("data/cache/hh")
            mock_makedirs.assert_called_once_with("data/cache/hh", exist_ok=True)
            mock_logger.info.assert_called_with("Кэш hh очищен")
    
    @patch('src.api_modules.base_api.logger')
    @patch('src.api_modules.base_api.os.path.exists')
    @patch('src.api_modules.base_api.os.makedirs')
    def test_clear_cache_nonexistent_directory(self, mock_makedirs, mock_exists, mock_logger):
        """Тест создания папки кэша если её нет"""
        mock_exists.return_value = False
        
        api = MockJobAPI()
        api.clear_cache("sj")
        
        # Проверяем, что папка была создана
        mock_makedirs.assert_called_once_with("data/cache/sj", exist_ok=True)
        mock_logger.info.assert_called_with("Создана папка кэша data/cache/sj")
    
    @patch('src.api_modules.base_api.logger')
    @patch('src.api_modules.base_api.os.path.exists')
    @patch('src.api_modules.base_api.os.makedirs')
    def test_clear_cache_os_error(self, mock_makedirs, mock_exists, mock_logger):
        """Тест обработки ошибки ОС при очистке кэша"""
        mock_exists.return_value = True
        mock_makedirs.side_effect = OSError("Permission denied")
        
        with patch('src.api_modules.base_api.shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = OSError("Permission denied")
            
            api = MockJobAPI()
            
            with pytest.raises(OSError, match="Permission denied"):
                api.clear_cache("hh")
            
            mock_logger.error.assert_called_with("Ошибка очистки кэша hh: Permission denied")
    
    @patch('src.api_modules.base_api.logger')
    @patch('src.api_modules.base_api.os.path.exists')
    @patch('src.api_modules.base_api.os.makedirs')
    def test_clear_cache_general_exception(self, mock_makedirs, mock_exists, mock_logger):
        """Тест обработки общей ошибки при очистке кэша"""
        mock_exists.return_value = True
        
        with patch('src.api_modules.base_api.shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = Exception("Unexpected error")
            
            api = MockJobAPI()
            
            with pytest.raises(Exception, match="Unexpected error"):
                api.clear_cache("hh")
            
            mock_logger.error.assert_called_with("Ошибка очистки кэша hh: Unexpected error")
    
    def test_clear_cache_different_sources(self):
        """Тест очистки кэша для разных источников"""
        with patch('src.api_modules.base_api.os.path.exists') as mock_exists:
            with patch('src.api_modules.base_api.os.makedirs') as mock_makedirs:
                with patch('src.api_modules.base_api.shutil.rmtree') as mock_rmtree:
                    mock_exists.return_value = True
                    
                    api = MockJobAPI()
                    
                    # Тестируем разные источники
                    sources = ["hh", "sj", "test_source"]
                    for source in sources:
                        api.clear_cache(source)
                        mock_rmtree.assert_called_with(f"data/cache/{source}")
                        mock_makedirs.assert_called_with(f"data/cache/{source}", exist_ok=True)
                    
                    # Проверяем количество вызовов
                    assert mock_rmtree.call_count == len(sources)
                    assert mock_makedirs.call_count == len(sources)
    
    @patch('src.api_modules.base_api.logger')
    @patch('src.api_modules.base_api.os.path.exists')
    @patch('src.api_modules.base_api.os.makedirs')
    def test_clear_cache_logging_behavior(self, mock_makedirs, mock_exists, mock_logger):
        """Тест поведения логирования при очистке кэша"""
        mock_exists.return_value = True
        
        with patch('src.api_modules.base_api.shutil.rmtree') as mock_rmtree:
            api = MockJobAPI()
            api.clear_cache("hh")
            
            # Проверяем, что логирование работает корректно
            mock_logger.info.assert_called_once()
            mock_logger.error.assert_not_called()
    
    def test_clear_cache_method_signature(self):
        """Тест сигнатуры метода clear_cache"""
        api = MockJobAPI()
        
        # Проверяем, что метод принимает правильные параметры
        import inspect
        sig = inspect.signature(api.clear_cache)
        params = list(sig.parameters.keys())
        
        assert len(params) == 2  # self + source
        assert params[1] == 'source'
    
    def test_clear_cache_return_type(self):
        """Тест типа возвращаемого значения clear_cache"""
        api = MockJobAPI()
        result = api.clear_cache("test")
        assert result is None
    
    def test_abstract_methods_signatures(self):
        """Тест сигнатур абстрактных методов"""
        # Проверяем сигнатуру get_vacancies
        sig = inspect.signature(MockJobAPI.get_vacancies)
        params = list(sig.parameters.keys())
        
        assert len(params) >= 2  # self + search_query
        assert params[1] == 'search_query'
        
        # Проверяем сигнатуру _validate_vacancy
        sig = inspect.signature(MockJobAPI._validate_vacancy)
        params = list(sig.parameters.keys())
        
        assert len(params) == 2  # self + vacancy
        assert params[1] == 'vacancy'
    
    def test_concrete_implementation_behavior(self):
        """Тест поведения конкретной реализации"""
        api = MockJobAPI()
        
        # Тестируем get_vacancies
        vacancies = api.get_vacancies("Python", experience="3+ years")
        assert isinstance(vacancies, list)
        assert len(vacancies) == 1
        assert vacancies[0]["id"] == "1"
        assert vacancies[0]["name"] == "Test Job"
        
        # Тестируем _validate_vacancy
        assert api._validate_vacancy({"id": "1", "name": "Job"}) is True
        assert api._validate_vacancy({"name": "Job"}) is False
        assert api._validate_vacancy({}) is False
