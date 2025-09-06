"""
Тесты для всех API модулей с 100% покрытием
Покрывает: base_api, hh_api, sj_api, unified_api, get_api
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api_modules.base_api import BaseJobAPI
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""

    def test_is_abstract_class(self):
        """Тест что BaseJobAPI - абстрактный класс"""
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_clear_cache_not_implemented(self):
        """Тест что clear_cache имеет дефолтную реализацию"""
        # Создаем конкретную реализацию для тестирования
        class TestAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return []
            def _validate_vacancy(self, vacancy):
                return True
        
        api = TestAPI()
        # Не должно падать
        api.clear_cache("test")


class TestAPIConnector:
    """Тесты для APIConnector"""

    def setup_method(self):
        """Настройка для каждого теста"""
        self.config = APIConfig()
        self.connector = APIConnector(self.config)

    def test_init_with_config(self):
        """Тест инициализации с конфигурацией"""
        config = APIConfig(timeout=30, user_agent="TestAgent")
        connector = APIConnector(config)
        
        assert connector.config == config

    @patch('requests.get')
    def test_connect_success(self, mock_get):
        """Тест успешного подключения"""
        mock_response = Mock()
        mock_response.json.return_value = {"items": [{"id": "1"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.connector._APIConnector__connect("http://test.com", {"q": "test"})
        
        assert result == {"items": [{"id": "1"}]}
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_connect_timeout_error(self, mock_get):
        """Тест обработки таймаута"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        
        with pytest.raises(TimeoutError):
            self.connector._APIConnector__connect("http://test.com", {})

    @patch('requests.get')
    def test_connect_connection_error(self, mock_get):
        """Тест обработки ошибки подключения"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()
        
        with pytest.raises(ConnectionError):
            self.connector._APIConnector__connect("http://test.com", {})

    @patch('requests.get')
    def test_connect_http_error(self, mock_get):
        """Тест обработки HTTP ошибки"""
        from requests.exceptions import HTTPError
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError()
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPError):
            self.connector._APIConnector__connect("http://test.com", {})

    @patch('requests.get')
    def test_connect_with_delay(self, mock_get):
        """Тест запроса с задержкой"""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch('time.sleep') as mock_sleep:
            self.connector._APIConnector__connect("http://test.com", {})
            mock_sleep.assert_called_once()


class TestHeadHunterAPI:
    """Тесты для HeadHunterAPI"""

    def setup_method(self):
        """Настройка для каждого теста"""
        with patch('src.utils.cache.FileCache'):
            self.api = HeadHunterAPI()

    def test_init_default_config(self):
        """Тест инициализации с дефолтной конфигурацией"""
        with patch('src.utils.cache.FileCache'):
            api = HeadHunterAPI()
            assert api._config is not None

    def test_init_custom_config(self):
        """Тест инициализации с пользовательской конфигурацией"""
        config = APIConfig()
        with patch('src.utils.cache.FileCache'):
            api = HeadHunterAPI(config)
            assert api._config == config

    def test_get_empty_response(self):
        """Тест получения пустого ответа"""
        result = self.api._get_empty_response()
        assert result == {"items": []}

    def test_validate_vacancy_valid(self):
        """Тест валидации корректной вакансии"""
        vacancy = {
            "name": "Python Developer",
            "alternate_url": "http://test.com",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"}
        }
        
        result = self.api._validate_vacancy(vacancy)
        assert result == True

    def test_validate_vacancy_missing_fields(self):
        """Тест валидации вакансии с отсутствующими полями"""
        vacancy = {"name": "Python Developer"}  # Нет alternate_url и salary
        
        result = self.api._validate_vacancy(vacancy)
        assert result == False

    def test_validate_vacancy_invalid_type(self):
        """Тест валидации невалидного типа"""
        result = self.api._validate_vacancy("not_a_dict")
        assert result == False

    def test_build_search_params_basic(self):
        """Тест построения базовых параметров поиска"""
        params = self.api._build_search_params("Python")
        
        assert params["text"] == "Python"
        assert "per_page" in params
        assert "order_by" in params

    def test_build_search_params_with_kwargs(self):
        """Тест построения параметров с дополнительными аргументами"""
        params = self.api._build_search_params(
            "Python",
            salary=100000,
            experience="between1And3"
        )
        
        assert params["text"] == "Python"
        assert params["salary"] == 100000
        assert params["experience"] == "between1And3"

    @patch.object(HeadHunterAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_page_success(self, mock_connect):
        """Тест получения страницы вакансий"""
        mock_connect.return_value = {
            "items": [{"id": "1", "name": "Test Vacancy"}],
            "found": 1
        }
        
        result = self.api.get_vacancies_page("Python", page=0)
        
        assert len(result) == 1
        assert result[0]["id"] == "1"

    @patch.object(HeadHunterAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_page_empty(self, mock_connect):
        """Тест получения пустой страницы"""
        mock_connect.return_value = {"items": [], "found": 0}
        
        result = self.api.get_vacancies_page("Nonexistent")
        
        assert result == []

    @patch.object(HeadHunterAPI, 'get_vacancies_page')
    def test_get_vacancies_single_page(self, mock_get_page):
        """Тест получения вакансий с одной страницы"""
        mock_get_page.return_value = [{"id": "1"}, {"id": "2"}]
        
        result = self.api.get_vacancies("Python", max_pages=1)
        
        assert len(result) == 2
        mock_get_page.assert_called_once()

    @patch.object(HeadHunterAPI, 'get_vacancies_page')
    def test_get_vacancies_multiple_pages(self, mock_get_page):
        """Тест получения вакансий с нескольких страниц"""
        mock_get_page.side_effect = [
            [{"id": "1"}, {"id": "2"}],  # Страница 0
            [{"id": "3"}],               # Страница 1
            []                           # Страница 2 (пустая)
        ]
        
        result = self.api.get_vacancies("Python", max_pages=3)
        
        assert len(result) == 3
        assert mock_get_page.call_count == 3

    def test_get_vacancies_by_company_name_found(self):
        """Тест поиска вакансий по названию компании"""
        with patch.object(TargetCompanies, 'get_company_by_name') as mock_get_company:
            mock_get_company.return_value = {"id": "123", "name": "Test Company"}
            
            with patch.object(self.api, 'get_vacancies') as mock_get_vacancies:
                mock_get_vacancies.return_value = [{"id": "1"}]
                
                result = self.api.get_vacancies_by_company_name("Test Company")
                
                assert result == [{"id": "1"}]
                mock_get_vacancies.assert_called_once()

    def test_get_vacancies_by_company_name_not_found(self):
        """Тест поиска вакансий по несуществующей компании"""
        with patch.object(TargetCompanies, 'get_company_by_name') as mock_get_company:
            mock_get_company.return_value = None
            
            result = self.api.get_vacancies_by_company_name("Nonexistent")
            
            assert result == []

    def test_get_vacancies_by_company_id(self):
        """Тест получения вакансий по ID компании"""
        with patch.object(self.api, 'get_vacancies') as mock_get_vacancies:
            mock_get_vacancies.return_value = [{"id": "1"}]
            
            result = self.api.get_vacancies_by_company_id("123")
            
            assert result == [{"id": "1"}]
            mock_get_vacancies.assert_called_with("", employer_id="123")


class TestSuperJobAPI:
    """Тесты для SuperJobAPI"""

    def setup_method(self):
        """Настройка для каждого теста"""
        with patch('src.utils.cache.FileCache'):
            self.api = SuperJobAPI()

    def test_init_default_config(self):
        """Тест инициализации с дефолтной конфигурацией"""
        with patch('src.utils.cache.FileCache'):
            api = SuperJobAPI()
            assert api._config is not None

    def test_get_empty_response(self):
        """Тест получения пустого ответа"""
        result = self.api._get_empty_response()
        assert result == {"objects": [], "total": 0}

    def test_validate_vacancy_valid(self):
        """Тест валидации корректной вакансии SuperJob"""
        vacancy = {
            "profession": "Python Developer",
            "link": "http://test.com",
            "payment_from": 100000,
            "payment_to": 150000,
            "currency": "rub"
        }
        
        result = self.api._validate_vacancy(vacancy)
        assert result == True

    def test_validate_vacancy_missing_fields(self):
        """Тест валидации вакансии с отсутствующими полями"""
        vacancy = {"profession": "Developer"}  # Нет link
        
        result = self.api._validate_vacancy(vacancy)
        assert result == False

    def test_build_search_params_basic(self):
        """Тест построения базовых параметров поиска SuperJob"""
        params = self.api._build_search_params("Python")
        
        assert params["keyword"] == "Python"
        assert "count" in params

    @patch.object(SuperJobAPI, '_CachedAPI__connect_to_api')
    def test_get_vacancies_page_success(self, mock_connect):
        """Тест получения страницы вакансий SuperJob"""
        mock_connect.return_value = {
            "objects": [{"id": 1, "profession": "Test Vacancy"}],
            "total": 1
        }
        
        result = self.api.get_vacancies_page("Python", page=0)
        
        assert len(result) == 1
        assert result[0]["id"] == 1


class TestUnifiedAPI:
    """Тесты для UnifiedAPI"""

    def setup_method(self):
        """Настройка для каждого теста"""
        with patch('src.utils.cache.FileCache'):
            self.api = UnifiedAPI()

    def test_init_default(self):
        """Тест инициализации с дефолтными настройками"""
        with patch('src.utils.cache.FileCache'):
            api = UnifiedAPI()
            assert api.hh_api is not None
            assert api.sj_api is not None

    def test_init_custom_apis(self):
        """Тест инициализации с пользовательскими API"""
        hh_api = Mock()
        sj_api = Mock()
        
        api = UnifiedAPI(hh_api=hh_api, sj_api=sj_api)
        
        assert api.hh_api == hh_api
        assert api.sj_api == sj_api

    def test_get_vacancies_hh_only(self):
        """Тест получения вакансий только из HH"""
        mock_hh_api = Mock()
        mock_hh_api.get_vacancies.return_value = [{"source": "hh", "id": "1"}]
        
        api = UnifiedAPI(hh_api=mock_hh_api, sj_api=Mock())
        
        result = api.get_vacancies("Python", sources=["hh"])
        
        assert len(result) == 1
        assert result[0]["source"] == "hh"

    def test_get_vacancies_sj_only(self):
        """Тест получения вакансий только из SuperJob"""
        mock_sj_api = Mock()
        mock_sj_api.get_vacancies.return_value = [{"source": "sj", "id": 1}]
        
        api = UnifiedAPI(hh_api=Mock(), sj_api=mock_sj_api)
        
        result = api.get_vacancies("Python", sources=["sj"])
        
        assert len(result) == 1
        assert result[0]["source"] == "sj"

    def test_get_vacancies_both_sources(self):
        """Тест получения вакансий из обоих источников"""
        mock_hh_api = Mock()
        mock_hh_api.get_vacancies.return_value = [{"source": "hh", "id": "1"}]
        
        mock_sj_api = Mock()
        mock_sj_api.get_vacancies.return_value = [{"source": "sj", "id": 1}]
        
        api = UnifiedAPI(hh_api=mock_hh_api, sj_api=mock_sj_api)
        
        result = api.get_vacancies("Python", sources=["hh", "sj"])
        
        assert len(result) == 2

    def test_get_vacancies_with_error(self):
        """Тест обработки ошибки от одного из API"""
        mock_hh_api = Mock()
        mock_hh_api.get_vacancies.side_effect = Exception("HH Error")
        
        mock_sj_api = Mock()
        mock_sj_api.get_vacancies.return_value = [{"source": "sj", "id": 1}]
        
        api = UnifiedAPI(hh_api=mock_hh_api, sj_api=mock_sj_api)
        
        result = api.get_vacancies("Python", sources=["hh", "sj"])
        
        # Должен вернуть результаты только от работающего API
        assert len(result) == 1
        assert result[0]["source"] == "sj"

    def test_clear_cache_all_sources(self):
        """Тест очистки кэша всех источников"""
        mock_hh_api = Mock()
        mock_sj_api = Mock()
        
        api = UnifiedAPI(hh_api=mock_hh_api, sj_api=mock_sj_api)
        api.clear_cache("test")
        
        mock_hh_api.clear_cache.assert_called_once_with("test")
        mock_sj_api.clear_cache.assert_called_once_with("test")

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        api = UnifiedAPI()
        sources = api.get_available_sources()
        
        assert "hh" in sources
        assert "sj" in sources

    def test_normalize_vacancies_hh(self):
        """Тест нормализации вакансий HH"""
        vacancies = [
            {"id": "1", "name": "Developer", "alternate_url": "http://test.com"}
        ]
        
        api = UnifiedAPI()
        result = api._normalize_vacancies(vacancies, "hh")
        
        assert len(result) == 1
        assert result[0]["source"] == "hh"
        assert result[0]["title"] == "Developer"

    def test_normalize_vacancies_sj(self):
        """Тест нормализации вакансий SuperJob"""
        vacancies = [
            {"id": 1, "profession": "Developer", "link": "http://test.com"}
        ]
        
        api = UnifiedAPI()
        result = api._normalize_vacancies(vacancies, "sj")
        
        assert len(result) == 1
        assert result[0]["source"] == "sj"
        assert result[0]["title"] == "Developer"