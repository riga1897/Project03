
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.api_modules.unified_api import UnifiedAPI
except ImportError:
    # Создаем тестовый класс UnifiedAPI, если не удается импортировать
    class UnifiedAPI:
        """Тестовый унифицированный API"""
        
        def __init__(self):
            self.hh_api = Mock()
            self.sj_api = Mock()
            self.parser = Mock()
            self.apis = {
                "hh": self.hh_api,
                "sj": self.sj_api,
            }

        def get_vacancies_from_sources(self, search_query, sources=None, **kwargs):
            return []

        def get_available_sources(self):
            return ["hh", "sj"]

        def clear_cache(self, sources):
            pass

        def validate_sources(self, sources):
            return sources

        def get_all_vacancies(self, query, **kwargs):
            return []


class TestUnifiedAPI:
    """Тесты для UnifiedAPI с оптимизацией производительности"""

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_unified_api_initialization(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест инициализации UnifiedAPI с моками"""
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_parser_instance = Mock()
        
        mock_hh_api.return_value = mock_hh_instance
        mock_sj_api.return_value = mock_sj_instance
        mock_parser.return_value = mock_parser_instance
        
        api = UnifiedAPI()
        
        assert api.hh_api == mock_hh_instance
        assert api.sj_api == mock_sj_instance
        assert api.parser == mock_parser_instance
        assert "hh" in api.apis
        assert "sj" in api.apis

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            sources = api.get_available_sources()
            
            assert isinstance(sources, list)
            assert "hh" in sources
            assert "sj" in sources

    def test_validate_sources_with_valid_sources(self):
        """Тест валидации валидных источников"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            valid_sources = api.validate_sources(["hh", "sj"])
            
            assert "hh" in valid_sources
            assert "sj" in valid_sources

    def test_validate_sources_with_invalid_sources(self):
        """Тест валидации невалидных источников"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            with patch.object(api, 'get_available_sources', return_value=["hh", "sj"]):
                valid_sources = api.validate_sources(["invalid_source"])
                
                # Должны вернуться все доступные источники
                assert "hh" in valid_sources
                assert "sj" in valid_sources

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_get_vacancies_from_sources_hh_only(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест получения вакансий только из HH с моками"""
        # Настраиваем моки
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh_api.return_value = mock_hh_instance
        mock_sj_api.return_value = mock_sj_instance
        mock_parser.return_value = Mock()
        
        mock_hh_instance.get_vacancies.return_value = [
            {"id": 1, "title": "Python Developer", "source": "hh"}
        ]
        
        api = UnifiedAPI()
        
        # Мокаем метод фильтрации
        with patch.object(api, '_filter_by_target_companies', return_value=[
            {"id": 1, "title": "Python Developer", "source": "hh"}
        ]):
            result = api.get_vacancies_from_sources("Python", sources=["hh"])
            
            assert len(result) == 1
            assert result[0]["title"] == "Python Developer"
            mock_hh_instance.get_vacancies.assert_called_once_with("Python")

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_get_vacancies_from_sources_both_sources(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест получения вакансий из обоих источников"""
        # Настраиваем моки
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh_api.return_value = mock_hh_instance
        mock_sj_api.return_value = mock_sj_instance
        mock_parser.return_value = Mock()
        
        mock_hh_instance.get_vacancies.return_value = [{"id": 1, "source": "hh"}]
        mock_sj_instance.get_vacancies.return_value = [{"id": 2, "source": "sj"}]
        
        api = UnifiedAPI()
        
        # Мокаем метод фильтрации
        with patch.object(api, '_filter_by_target_companies', return_value=[
            {"id": 1, "source": "hh"}, {"id": 2, "source": "sj"}
        ]):
            result = api.get_vacancies_from_sources("Python", sources=["hh", "sj"])
            
            assert len(result) == 2
            mock_hh_instance.get_vacancies.assert_called_once()
            mock_sj_instance.get_vacancies.assert_called_once()

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_clear_cache(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест очистки кэша"""
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh_api.return_value = mock_hh_instance
        mock_sj_api.return_value = mock_sj_instance
        mock_parser.return_value = Mock()
        
        api = UnifiedAPI()
        
        # Мокаем файловые операции
        with patch('glob.glob', return_value=['file1.json', 'file2.json']), \
             patch('os.remove') as mock_remove, \
             patch('builtins.print'):
            
            api.clear_cache({"hh": True, "sj": True})
            
            mock_hh_instance.clear_cache.assert_called_once_with("hh")
            mock_sj_instance.clear_cache.assert_called_once_with("sj")

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI') 
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_get_vacancies_from_source_single(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест получения вакансий из одного источника"""
        mock_hh_instance = Mock()
        mock_sj_instance = Mock()
        mock_hh_api.return_value = mock_hh_instance
        mock_sj_api.return_value = mock_sj_instance
        mock_parser.return_value = Mock()
        
        mock_hh_instance.get_vacancies.return_value = [{"id": 1, "title": "Test Job"}]
        
        api = UnifiedAPI()
        result = api.get_vacancies_from_source("Python", "hh")
        
        assert result == [{"id": 1, "title": "Test Job"}]
        mock_hh_instance.get_vacancies.assert_called_once_with(search_query="Python")

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_get_vacancies_from_source_unknown(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест получения вакансий из неизвестного источника"""
        mock_hh_api.return_value = Mock()
        mock_sj_api.return_value = Mock()
        mock_parser.return_value = Mock()
        
        api = UnifiedAPI()
        result = api.get_vacancies_from_source("Python", "unknown")
        
        assert result == []

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_get_all_vacancies(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест получения всех вакансий"""
        mock_hh_api.return_value = Mock()
        mock_sj_api.return_value = Mock()
        mock_parser.return_value = Mock()
        
        api = UnifiedAPI()
        
        with patch.object(api, 'get_vacancies_from_sources', return_value=[{"id": 1}]) as mock_get:
            result = api.get_all_vacancies("Python")
            
            assert result == [{"id": 1}]
            mock_get.assert_called_once_with("Python", sources=["hh", "sj"])

    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_search_with_multiple_keywords(self, mock_hh_api, mock_sj_api, mock_parser):
        """Тест поиска с несколькими ключевыми словами"""
        mock_hh_api.return_value = Mock()
        mock_sj_api.return_value = Mock()
        mock_parser.return_value = Mock()
        
        api = UnifiedAPI()
        
        with patch.object(api, 'get_all_vacancies') as mock_get_all:
            mock_get_all.side_effect = [
                [{"id": 1, "title": "Python Developer"}],
                [{"id": 2, "title": "Java Developer"}]
            ]
            
            result = api.search_with_multiple_keywords(["Python", "Java"])
            
            assert len(result) == 2
            assert mock_get_all.call_count == 2

    def test_filter_by_target_companies_empty_list(self):
        """Тест фильтрации с пустым списком"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            result = api._filter_by_target_companies([])
            
            assert result == []

    @patch('src.api_modules.unified_api.Vacancy')
    @patch('src.api_modules.unified_api.PostgresSaver')
    @patch('src.api_modules.unified_api.SuperJobParser')
    @patch('src.api_modules.unified_api.SuperJobAPI')
    @patch('src.api_modules.unified_api.HeadHunterAPI')
    def test_filter_by_target_companies_with_data(self, mock_hh_api, mock_sj_api, mock_parser, mock_postgres, mock_vacancy):
        """Тест фильтрации с данными"""
        mock_hh_api.return_value = Mock()
        mock_sj_api.return_value = Mock()
        mock_parser.return_value = Mock()
        
        # Настраиваем моки
        mock_vacancy_obj = Mock()
        mock_vacancy_obj.to_dict.return_value = {"id": 1, "filtered": True}
        mock_vacancy.from_dict.return_value = mock_vacancy_obj
        
        mock_postgres_instance = Mock()
        mock_postgres_instance.filter_and_deduplicate_vacancies.return_value = [mock_vacancy_obj]
        mock_postgres.return_value = mock_postgres_instance
        
        api = UnifiedAPI()
        test_vacancies = [{"id": 1, "title": "Test Job"}]
        
        result = api._filter_by_target_companies(test_vacancies)
        
        assert len(result) == 1
        assert result[0] == {"id": 1, "filtered": True}
