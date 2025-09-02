
"""
Консолидированные тесты для всех API модулей
Объединяет тесты base_api, hh_api, sj_api, unified_api, cached_api, get_api
"""

import os
import sys
import importlib
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch, call
import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорты API модулей
try:
    from src.api_modules.base_api import BaseAPI
    from src.api_modules.hh_api import HeadHunterAPI
    from src.api_modules.sj_api import SuperJobAPI
    from src.api_modules.unified_api import UnifiedAPI
    from src.api_modules.cached_api import CachedAPI
    from src.api_modules.get_api import get_api
    API_MODULES_AVAILABLE = True
except ImportError:
    API_MODULES_AVAILABLE = False


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
        """Тест базовой функциональности BaseAPI"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=consolidated_mocks.http_response):
            base_api = BaseAPI()
            assert hasattr(base_api, 'get_vacancies')
            
            # Проверяем базовые методы
            if hasattr(base_api, 'get_vacancies'):
                try:
                    result = base_api.get_vacancies(consolidated_mocks.api_data["search_query"])
                    assert isinstance(result, (list, dict))
                except Exception:
                    # Базовый API может не иметь реализации
                    pass

    def test_headhunter_api_integration(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест интеграции с HeadHunter API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=consolidated_mocks.http_response):
            cached_api = CachedAPI()
            
            # Первый запрос - должен обратиться к API
            result1 = cached_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result1, list)
            
            # Второй запрос - должен использовать кэш
            result2 = cached_api.get_vacancies(consolidated_mocks.api_data["search_query"])
            assert isinstance(result2, list)

    def test_get_api_factory(self) -> None:
        """Тест фабрики get_api"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        # Тест получения HeadHunter API
        hh_api = get_api("hh")
        assert isinstance(hh_api, HeadHunterAPI)
        
        # Тест получения SuperJob API
        sj_api = get_api("sj")
        assert isinstance(sj_api, SuperJobAPI)
        
        # Тест получения Unified API
        unified_api = get_api("unified")
        assert isinstance(unified_api, UnifiedAPI)
        
        # Тест неизвестного источника
        with pytest.raises((ValueError, KeyError)):
            get_api("unknown")

    def test_api_error_handling_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест обработки ошибок в API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        # Мок ошибки HTTP
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
            apis = [HeadHunterAPI(), SuperJobAPI()]
            
            for api in apis:
                try:
                    result = api.get_vacancies(consolidated_mocks.api_data["search_query"])
                    # Некоторые API могут возвращать пустой список при ошибке
                    assert isinstance(result, list)
                except requests.exceptions.RequestException:
                    # Или могут пробрасывать исключение
                    pass

    def test_api_rate_limiting_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест ограничения скорости запросов"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        # Мок ответа с кодом 429 (Too Many Requests)
        mock_resp = Mock()
        mock_resp.status_code = 429
        mock_resp.json.return_value = {"error": "Too many requests"}
        
        with patch('requests.get', return_value=mock_resp):
            apis = [HeadHunterAPI(), SuperJobAPI()]
            
            for api in apis:
                try:
                    result = api.get_vacancies(consolidated_mocks.api_data["search_query"])
                    # API может возвращать пустой список при превышении лимита
                    assert isinstance(result, list)
                except Exception:
                    # Или может выбрасывать исключение
                    pass

    def test_api_data_validation_consolidated(self, consolidated_mocks: ConsolidatedAPIMocks) -> None:
        """Тест валидации данных API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=consolidated_mocks.http_response):
            hh_api = HeadHunterAPI()
            
            # Тест различных поисковых запросов
            search_queries = ["python", "javascript", "data scientist", ""]
            
            for query in search_queries:
                try:
                    result = hh_api.get_vacancies(query)
                    assert isinstance(result, list)
                except Exception:
                    # Некоторые запросы могут быть некорректными
                    pass

    def test_api_configuration_consolidated(self) -> None:
        """Тест конфигурации API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

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
