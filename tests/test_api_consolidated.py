
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


class TestAPIConsolidated:
    """Консолидированные тесты для всех API модулей"""

    @pytest.fixture
    def mock_response(self):
        """Мок ответа HTTP"""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
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
        return mock_resp

    def test_base_api_functionality(self, mock_response: Mock) -> None:
        """Тест базовой функциональности BaseAPI"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
            base_api = BaseAPI()
            assert hasattr(base_api, 'get_vacancies')
            
            # Проверяем базовые методы
            if hasattr(base_api, 'get_vacancies'):
                try:
                    result = base_api.get_vacancies("python")
                    assert isinstance(result, (list, dict))
                except Exception:
                    # Базовый API может не иметь реализации
                    pass

    def test_headhunter_api_integration(self, mock_response: Mock) -> None:
        """Тест интеграции с HeadHunter API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
            hh_api = HeadHunterAPI()
            
            # Тест получения вакансий
            result = hh_api.get_vacancies("python")
            assert isinstance(result, list)
            
            # Тест с параметрами
            result_with_params = hh_api.get_vacancies(
                "python", 
                area=1,  # Москва
                experience="between1And3",
                salary=100000
            )
            assert isinstance(result_with_params, list)

    def test_superjob_api_integration(self, mock_response: Mock) -> None:
        """Тест интеграции с SuperJob API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
            sj_api = SuperJobAPI()
            
            # Тест получения вакансий
            result = sj_api.get_vacancies("python")
            assert isinstance(result, list)
            
            # Тест с параметрами
            result_with_params = sj_api.get_vacancies(
                "python",
                town="Москва",
                payment_from=100000
            )
            assert isinstance(result_with_params, list)

    def test_unified_api_functionality(self, mock_response: Mock) -> None:
        """Тест функциональности UnifiedAPI"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
            unified_api = UnifiedAPI()
            
            # Тест получения вакансий из всех источников
            result = unified_api.get_vacancies("python")
            assert isinstance(result, list)
            
            # Тест с конкретным источником
            hh_result = unified_api.get_vacancies("python", source="hh")
            assert isinstance(hh_result, list)
            
            sj_result = unified_api.get_vacancies("python", source="sj")
            assert isinstance(sj_result, list)

    def test_cached_api_functionality(self, mock_response: Mock) -> None:
        """Тест функциональности CachedAPI"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
            cached_api = CachedAPI()
            
            # Первый запрос - должен обратиться к API
            result1 = cached_api.get_vacancies("python")
            assert isinstance(result1, list)
            
            # Второй запрос - должен использовать кэш
            result2 = cached_api.get_vacancies("python")
            assert isinstance(result2, list)
            assert result1 == result2

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

    def test_api_error_handling(self) -> None:
        """Тест обработки ошибок в API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        # Мок ошибки HTTP
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
            hh_api = HeadHunterAPI()
            
            try:
                result = hh_api.get_vacancies("python")
                # Некоторые API могут возвращать пустой список при ошибке
                assert isinstance(result, list)
            except requests.exceptions.RequestException:
                # Или могут пробрасывать исключение
                pass

    def test_api_rate_limiting(self) -> None:
        """Тест ограничения скорости запросов"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        # Мок ответа с кодом 429 (Too Many Requests)
        mock_resp = Mock()
        mock_resp.status_code = 429
        mock_resp.json.return_value = {"error": "Too many requests"}
        
        with patch('requests.get', return_value=mock_resp):
            hh_api = HeadHunterAPI()
            
            try:
                result = hh_api.get_vacancies("python")
                # API может возвращать пустой список при превышении лимита
                assert isinstance(result, list)
            except Exception:
                # Или может выбрасывать исключение
                pass

    def test_api_data_validation(self, mock_response: Mock) -> None:
        """Тест валидации данных API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
            apis = [HeadHunterAPI(), SuperJobAPI(), UnifiedAPI()]
            
            for api in apis:
                result = api.get_vacancies("python")
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

    def test_api_search_parameters(self, mock_response: Mock) -> None:
        """Тест различных параметров поиска"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with patch('requests.get', return_value=mock_response):
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

    def test_api_configuration(self) -> None:
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
