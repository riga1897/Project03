
"""
Тесты для UnifiedAPI
"""

import pytest
from unittest.mock import Mock, patch
from src.api_modules.unified_api import UnifiedAPI


class TestUnifiedAPI:
    """Тесты для UnifiedAPI"""

    @pytest.fixture
    def mock_hh_api(self):
        """Мок для HH API"""
        mock_api = Mock()
        mock_api.get_vacancies.return_value = [
            {'id': '1', 'name': 'Python HH', 'source': 'hh.ru'}
        ]
        mock_api.get_companies.return_value = [
            {'id': '101', 'name': 'Company HH'}
        ]
        return mock_api

    @pytest.fixture
    def mock_sj_api(self):
        """Мок для SJ API"""
        mock_api = Mock()
        mock_api.get_vacancies.return_value = [
            {'id': '2', 'profession': 'Python SJ', 'source': 'superjob.ru'}
        ]
        mock_api.get_companies.return_value = [
            {'id': '102', 'title': 'Company SJ'}
        ]
        return mock_api

    @pytest.fixture
    def unified_api(self, mock_hh_api, mock_sj_api):
        """Фикстура UnifiedAPI с моками"""
        with patch('src.api_modules.unified_api.HeadHunterAPI', return_value=mock_hh_api), \
             patch('src.api_modules.unified_api.SuperJobAPI', return_value=mock_sj_api):
            return UnifiedAPI()

    def test_initialization(self, unified_api):
        """Тест инициализации"""
        assert unified_api.hh_api is not None
        assert unified_api.sj_api is not None

    def test_get_vacancies_from_all_sources(self, unified_api, mock_hh_api, mock_sj_api):
        """Тест получения вакансий из всех источников"""
        result = unified_api.get_vacancies_from_all_sources("Python")

        assert len(result) == 2
        mock_hh_api.get_vacancies.assert_called_once_with("Python")
        mock_sj_api.get_vacancies.assert_called_once_with("Python")

    def test_get_vacancies_from_source_hh(self, unified_api, mock_hh_api):
        """Тест получения вакансий из HeadHunter"""
        result = unified_api.get_vacancies_from_source("Python", "hh")

        assert len(result) == 1
        assert result[0]['source'] == 'hh.ru'
        mock_hh_api.get_vacancies.assert_called_once_with("Python")

    def test_get_vacancies_from_source_sj(self, unified_api, mock_sj_api):
        """Тест получения вакансий из SuperJob"""
        result = unified_api.get_vacancies_from_source("Python", "sj")

        assert len(result) == 1
        assert result[0]['source'] == 'superjob.ru'
        mock_sj_api.get_vacancies.assert_called_once_with("Python")

    def test_get_vacancies_from_source_unknown(self, unified_api):
        """Тест получения вакансий из неизвестного источника"""
        result = unified_api.get_vacancies_from_source("Python", "unknown")

        assert result == []

    def test_get_companies_from_all_sources(self, unified_api, mock_hh_api, mock_sj_api):
        """Тест получения компаний из всех источников"""
        result = unified_api.get_companies_from_all_sources()

        assert len(result) == 2
        mock_hh_api.get_companies.assert_called_once()
        mock_sj_api.get_companies.assert_called_once()

    def test_get_companies_from_source_hh(self, unified_api, mock_hh_api):
        """Тест получения компаний из HeadHunter"""
        result = unified_api.get_companies_from_source("hh")

        assert len(result) == 1
        assert result[0]['name'] == 'Company HH'
        mock_hh_api.get_companies.assert_called_once()

    def test_get_companies_from_source_sj(self, unified_api, mock_sj_api):
        """Тест получения компаний из SuperJob"""
        result = unified_api.get_companies_from_source("sj")

        assert len(result) == 1
        assert result[0]['title'] == 'Company SJ'
        mock_sj_api.get_companies.assert_called_once()

    def test_search_with_multiple_keywords(self, unified_api, mock_hh_api, mock_sj_api):
        """Тест поиска с несколькими ключевыми словами"""
        keywords = ["Python", "Django"]
        result = unified_api.search_with_multiple_keywords(keywords, "hh")

        # Должен вызваться поиск для каждого ключевого слова
        assert mock_hh_api.get_vacancies.call_count == 2

    def test_get_available_sources(self, unified_api):
        """Тест получения доступных источников"""
        sources = unified_api.get_available_sources()

        assert 'hh' in sources
        assert 'sj' in sources
        assert len(sources) == 2

    def test_api_error_handling(self, unified_api, mock_hh_api):
        """Тест обработки ошибок API"""
        mock_hh_api.get_vacancies.side_effect = Exception("API Error")

        result = unified_api.get_vacancies_from_source("Python", "hh")

        assert result == []
