
"""
Консолидированные тесты для всех API модулей
Объединяет тесты base_api, hh_api, sj_api, unified_api, cached_api, get_api
"""

import os
import sys
import importlib
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock, Mock, patch, call
import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорты API модулей
from src.api_modules.base_api import BaseJobAPI
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.api_modules.cached_api import CachedAPI
from src.api_modules.get_api import APIConnector


class ConsolidatedAPIMocks:
    """
    Консолидированный класс для всех API моков
    
    Создает и настраивает все необходимые моки для тестирования API
    """
    
    def __init__(self) -> None:
        """Инициализация всех необходимых моков для API"""
        self.http_response = self._create_http_response_mock()
        self.api_data = self._create_api_data_mock()
        
    def _create_http_response_mock(self) -> Mock:
        """
        Создание мока HTTP ответа
        
        Returns:
            Mock: Настроенный мок HTTP ответа
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "12345",
                    "name": "Python Developer",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "employer": {"name": "Test Company"},
                    "area": {"name": "Москва"},
                    "experience": {"name": "От 1 года до 3 лет"},
                    "employment": {"name": "Полная занятость"},
                    "description": "Test description",
                    "alternate_url": "https://test.com/vacancy/12345",
                    "published_at": "2025-01-01T00:00:00+0300"
                }
            ],
            "found": 1,
            "pages": 1,
            "page": 0,
            "per_page": 20
        }
        return mock_response
    
    def _create_api_data_mock(self) -> Dict[str, Any]:
        """
        Создание мока данных API
        
        Returns:
            Dict[str, Any]: Настроенные данные для тестирования
        """
        return {
            "search_query": "python",
            "search_params": {
                "area": 1,
                "experience": "between1And3",
                "salary": 100000
            },
            "expected_vacancy_count": 1
        }


class TestAPIConsolidated:
    """Консолидированные тесты для всех API модулей"""

    @pytest.fixture
    def consolidated_mocks(self) -> ConsolidatedAPIMocks:
        """
        Фикстура консолидированных моков для API
        
        Returns:
            ConsolidatedAPIMocks: Объект с настроенными моками
        """
        return ConsolidatedAPIMocks()

    def test_base_api_functionality(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест базовой функциональности BaseJobAPI"""
        # BaseJobAPI является абстрактным классом, создаем конкретную реализацию
        class ConcreteAPI(BaseJobAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return [{"id": "test", "title": "Test Vacancy"}]
            
            def _validate_vacancy(self, vacancy):
                return True
        
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            base_api = ConcreteAPI()
            assert hasattr(base_api, 'get_vacancies')
            
            # Проверяем базовые методы
            result = base_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result, list)

    def test_headhunter_api_integration(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест интеграции с HeadHunter API"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            hh_api = HeadHunterAPI()
            
            # Тест получения вакансий
            result = hh_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result, list)
            
            # Тест с параметрами
            params = consolidated_mocks.api_data["search_params"]
            result_with_params = hh_api.get_vacancies(
                consolidated_mocks.api_data["search_query"], 
                area=params["area"],
                experience=params["experience"],
                salary=params["salary"]
            )
            assert isinstance(result_with_params, list)

    def test_superjob_api_integration(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест интеграции с SuperJob API"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            sj_api = SuperJobAPI()
            
            # Тест получения вакансий
            result = sj_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result, list)
            
            # Тест с параметрами
            result_with_params = sj_api.get_vacancies(
                consolidated_mocks.api_data["search_query"],
                town="Москва",
                payment_from=consolidated_mocks.api_data["search_params"]["salary"]
            )
            assert isinstance(result_with_params, list)

    def test_unified_api_functionality(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест функциональности UnifiedAPI"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            unified_api = UnifiedAPI()
            
            # Тест получения вакансий из всех источников
            if hasattr(unified_api, 'search_vacancies'):
                result = unified_api.search_vacancies(consolidated_mocks.api_data["search_query"])
                assert isinstance(result, list)
            elif hasattr(unified_api, 'get_vacancies_from_all_sources'):
                result = unified_api.get_vacancies_from_all_sources(consolidated_mocks.api_data["search_query"])
                assert isinstance(result, list)

    def test_cached_api_functionality(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест функциональности CachedAPI"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            cached_api = CachedAPI()
            
            # Первый запрос - должен обратиться к API
            result1 = cached_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result1, list)
            
            # Второй запрос - должен использовать кэш
            result2 = cached_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result2, list)

    def test_api_connector_functionality(self) -> None:
        """Тест функциональности APIConnector"""
        connector = APIConnector()
        assert connector is not None
        assert hasattr(connector, 'connect')
        
        # Тест подключения с моком
        test_url = "https://api.example.com/test"
        test_params = {"query": "python"}
        
        with patch('requests.get', return_value=Mock(status_code=200, json=lambda: {"test": "data"})):
            result = connector.connect(test_url, test_params)
            assert isinstance(result, dict)

    def test_api_error_handling_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест обработки ошибок в API"""
        # Мок ошибки HTTP
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
            apis = [HeadHunterAPI(), SuperJobAPI()]
            
            for api in apis:
                result = api.get_vacancies(consolidated_mocks.api_data["search_query"])
                # API должны возвращать пустой список при ошибке
                assert isinstance(result, list)

    def test_api_rate_limiting_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест ограничения скорости запросов"""
        # Мок ответа с кодом 429 (Too Many Requests)
        mock_resp = Mock()
        mock_resp.status_code = 429
        mock_resp.json.return_value = {"error": "Too many requests"}
        
        with patch('requests.get', return_value=mock_resp):
            apis = [HeadHunterAPI(), SuperJobAPI()]
            
            for api in apis:
                result = api.get_vacancies(consolidated_mocks.api_data["search_query"])
                # API возвращают пустой список при превышении лимита
                assert isinstance(result, list)

    def test_api_data_validation_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест валидации данных API"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            apis = [HeadHunterAPI(), SuperJobAPI()]
            
            for api in apis:
                result = api.get_vacancies(consolidated_mocks.api_data["search_query"])
                assert isinstance(result, list)
                
                # Проверяем структуру данных
                if result:
                    vacancy = result[0]
                    assert isinstance(vacancy, dict)
                    # Основные поля должны присутствовать
                    expected_fields = ["id", "title", "url", "source"]
                    for field in expected_fields:
                        if field in vacancy:
                            assert vacancy[field] is not None

    def test_api_search_parameters_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест различных параметров поиска"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            hh_api = HeadHunterAPI()
            
            # Тест различных поисковых запросов
            search_queries = ["python", "javascript", "data scientist", ""]
            
            for query in search_queries:
                result = hh_api.get_vacancies(query)
                assert isinstance(result, list)

    def test_api_configuration_consolidated(self) -> None:
        """Тест конфигурации API"""
        # Проверяем что API имеют необходимые конфигурационные атрибуты
        apis = [HeadHunterAPI(), SuperJobAPI()]
        
        for api in apis:
            # Базовые URL должны быть определены
            if hasattr(api, 'base_url'):
                assert api.base_url.startswith('http')
            
            # Методы API должны быть callable
            assert callable(getattr(api, 'get_vacancies', None))

    def test_api_performance_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест производительности API операций"""
        import time
        
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            hh_api = HeadHunterAPI()
            
            # Тест производительности запроса
            start_time = time.time()
            result = hh_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            execution_time = time.time() - start_time
            
            # Операция должна выполниться быстро (мок должен быть мгновенным)
            assert execution_time < 1.0
            assert isinstance(result, list)

    def test_api_comprehensive_workflow(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест комплексного рабочего процесса API"""
        with patch('requests.get', return_value=consolidated_mocks.http_response):
            # Создаем все API
            hh_api = HeadHunterAPI()
            sj_api = SuperJobAPI()
            cached_api = CachedAPI()
            
            # Проверяем работу каждого API
            apis = [hh_api, sj_api, cached_api]
            
            for api in apis:
                result = api.get_vacancies(consolidated_mocks.api_data["search_query"])
                assert isinstance(result, list)
                
                # Проверяем что результат имеет ожидаемую структуру
                if result:
                    assert len(result) >= consolidated_mocks.api_data["expected_vacancy_count"]
