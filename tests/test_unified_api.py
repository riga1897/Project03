
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api_modules.unified_api import UnifiedAPI


class TestUnifiedAPI:
    """Тесты для UnifiedAPI"""

    def test_unified_api_initialization(self):
        """Тест инициализации UnifiedAPI"""
        api = UnifiedAPI()
        assert hasattr(api, 'hh_api')
        assert hasattr(api, 'sj_api')

    @patch('src.api_modules.unified_api.HeadHunterAPI')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    def test_unified_api_with_mocked_apis(self, mock_sj, mock_hh):
        """Тест инициализации с моками API"""
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh.return_value = mock_hh_instance
        mock_sj.return_value = mock_sj_instance
        
        api = UnifiedAPI()
        assert api.hh_api == mock_hh_instance
        assert api.sj_api == mock_sj_instance

    def test_get_vacancies_from_multiple_sources(self):
        """Тест получения вакансий из нескольких источников"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh, \
             patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj:
            
            # Настраиваем моки
            mock_hh_instance = Mock()
            mock_sj_instance = Mock()
            mock_hh.return_value = mock_hh_instance
            mock_sj.return_value = mock_sj_instance
            
            mock_hh_instance.get_vacancies.return_value = ["hh_vacancy1", "hh_vacancy2"]
            mock_sj_instance.get_vacancies.return_value = ["sj_vacancy1"]
            
            api = UnifiedAPI()
            result = api.get_vacancies_from_sources("Python", {"hh.ru", "superjob.ru"})
            
            assert isinstance(result, list)
            mock_hh_instance.get_vacancies.assert_called_with("Python")
            mock_sj_instance.get_vacancies.assert_called_with("Python")

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        api = UnifiedAPI()
        sources = api.get_available_sources()
        
        assert isinstance(sources, set)
        assert "hh.ru" in sources
        assert "superjob.ru" in sources

    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_get_vacancies_single_source(self, mock_hh):
        """Тест получения вакансий из одного источника"""
        mock_hh_instance = Mock()
        mock_hh.return_value = mock_hh_instance
        mock_hh_instance.get_vacancies.return_value = ["vacancy1", "vacancy2"]
        
        api = UnifiedAPI()
        result = api.get_vacancies_from_sources("Python", {"hh.ru"})
        
        assert isinstance(result, list)
        mock_hh_instance.get_vacancies.assert_called_with("Python")

    def test_clear_cache(self):
        """Тест очистки кэша"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh, \
             patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj:
            
            mock_hh_instance = Mock()
            mock_sj_instance = Mock()
            mock_hh.return_value = mock_hh_instance
            mock_sj.return_value = mock_sj_instance
            
            api = UnifiedAPI()
            api.clear_cache()
            
            # Проверяем, что методы очистки кэша вызываются
            mock_hh_instance.clear_cache.assert_called_once()
            mock_sj_instance.clear_cache.assert_called_once()
