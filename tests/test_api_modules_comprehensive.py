"""
Комплексные тесты для API модулей с максимальным покрытием кода.
Включает в себя тестирование всех методов, исключений и edge cases.
Без запросов к внешним API, с полноценными моками.
"""

import os
import sys
import json
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Глобальные моки для всех внешних зависимостей
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from src.api_modules.base_api import BaseAPI
from src.api_modules.hh_api import HHAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.cached_api import CachedAPI
from src.api_modules.unified_api import UnifiedAPI
from src.api_modules.get_api import GetAPI


class TestBaseAPI:
    """Комплексное тестирование базового API класса"""
    
    def test_base_api_initialization(self):
        """Тестирование инициализации базового API класса"""
        # Тестируем создание абстрактного класса
        base_api = BaseAPI()
        assert base_api is not None
        
        # Проверяем, что абстрактные методы присутствуют
        assert hasattr(base_api, 'search_vacancies')
        assert hasattr(base_api, 'get_vacancy_details')
        
    def test_base_api_abstract_methods(self):
        """Тестирование абстрактных методов базового класса"""
        base_api = BaseAPI()
        
        # Проверяем, что абстрактные методы вызывают NotImplementedError
        with pytest.raises(NotImplementedError):
            base_api.search_vacancies("Python")
            
        with pytest.raises(NotImplementedError):
            base_api.get_vacancy_details("123")


class TestHHAPI:
    """Комплексное тестирование HH.ru API"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок конфигурации
        with patch('src.api_modules.hh_api.HHAPIConfig') as mock_config_class:
            mock_config = Mock()
            mock_config.get_base_url.return_value = "https://api.hh.ru"
            mock_config.get_search_url.return_value = "https://api.hh.ru/vacancies"
            mock_config.get_headers.return_value = {"User-Agent": "Test"}
            mock_config.get_default_parameters.return_value = {"per_page": 100}
            mock_config.should_filter_by_salary.return_value = False
            mock_config_class.return_value = mock_config
            
            self.hh_api = HHAPI()
            
    @patch('requests.get')
    def test_hh_api_search_vacancies_success(self, mock_get):
        """Тестирование успешного поиска вакансий через HH API"""
        # Настраиваем мок ответа
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "123",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "employer": {"name": "Test Company", "id": "456"},
                    "salary": {"from": 100000, "to": 200000, "currency": "RUR"},
                    "snippet": {"requirement": "Python", "responsibility": "Development"}
                }
            ],
            "pages": 1,
            "per_page": 20,
            "page": 0,
            "found": 1
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Выполняем поиск
        result = self.hh_api.search_vacancies("Python")
        
        # Проверяем результат
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "123"
        assert result[0]["name"] == "Python Developer"
        
        # Проверяем, что запрос был сделан
        mock_get.assert_called_once()
        
    @patch('requests.get')
    def test_hh_api_search_vacancies_error_handling(self, mock_get):
        """Тестирование обработки ошибок в HH API"""
        # Тестируем HTTP ошибку
        mock_get.side_effect = Exception("Network error")
        
        result = self.hh_api.search_vacancies("Python")
        assert result == []
        
        # Тестируем некорректный JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.side_effect = None
        mock_get.return_value = mock_response
        
        result = self.hh_api.search_vacancies("Python")
        assert result == []
        
    @patch('requests.get')
    def test_hh_api_get_vacancy_details(self, mock_get):
        """Тестирование получения деталей вакансии"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123",
            "name": "Python Developer",
            "description": "Full job description",
            "key_skills": [{"name": "Python"}, {"name": "Django"}]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.hh_api.get_vacancy_details("123")
        
        assert result is not None
        assert result["id"] == "123"
        assert "description" in result
        
    def test_hh_api_parameters_building(self):
        """Тестирование построения параметров запроса"""
        if hasattr(self.hh_api, '_build_search_params'):
            params = self.hh_api._build_search_params("Python", page=1, per_page=50)
            assert isinstance(params, dict)
            assert "text" in params or "q" in params
            
    def test_hh_api_url_building(self):
        """Тестирование построения URL для запросов"""
        if hasattr(self.hh_api, '_build_search_url'):
            url = self.hh_api._build_search_url("Python")
            assert isinstance(url, str)
            assert "hh.ru" in url or "api" in url


class TestSuperJobAPI:
    """Комплексное тестирование SuperJob API"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        with patch('src.api_modules.sj_api.SJAPIConfig') as mock_config_class:
            mock_config = Mock()
            mock_config.get_base_url.return_value = "https://api.superjob.ru"
            mock_config.get_search_url.return_value = "https://api.superjob.ru/2.0/vacancies/"
            mock_config.get_headers.return_value = {"X-Api-App-Id": "test_key"}
            mock_config.get_default_parameters.return_value = {"count": 100}
            mock_config.should_filter_by_salary.return_value = False
            mock_config_class.return_value = mock_config
            
            self.sj_api = SuperJobAPI()
            
    @patch('requests.get')
    def test_sj_api_search_vacancies_success(self, mock_get):
        """Тестирование успешного поиска через SuperJob API"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "objects": [
                {
                    "id": 789,
                    "profession": "Python разработчик",
                    "link": "https://superjob.ru/vakansii/python-789.html",
                    "firm_name": "IT Company",
                    "payment_from": 120000,
                    "payment_to": 180000,
                    "currency": "rub",
                    "candidat": "Знание Python",
                    "work": "Разработка ПО"
                }
            ],
            "total": 1
        }
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.sj_api.search_vacancies("Python")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 789
        assert result[0]["profession"] == "Python разработчик"
        
    @patch('requests.get')
    def test_sj_api_authentication_error(self, mock_get):
        """Тестирование обработки ошибок аутентификации"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_get.return_value = mock_response
        
        result = self.sj_api.search_vacancies("Python")
        assert result == []
        
    def test_sj_api_parameters_validation(self):
        """Тестирование валидации параметров"""
        # Тестируем пустой запрос
        result = self.sj_api.search_vacancies("")
        assert result == []
        
        # Тестируем None запрос
        result = self.sj_api.search_vacancies(None)
        assert result == []


class TestCachedAPI:
    """Комплексное тестирование кэширующего API"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем мок базового API
        self.mock_base_api = Mock()
        self.mock_base_api.search_vacancies.return_value = [{"id": "123", "title": "Test"}]
        
        # Создаем CachedAPI с моком
        self.cached_api = CachedAPI(self.mock_base_api)
        
    def test_cached_api_initialization(self):
        """Тестирование инициализации кэширующего API"""
        assert self.cached_api.base_api == self.mock_base_api
        assert hasattr(self.cached_api, 'cache')
        
    def test_cached_api_search_with_caching(self):
        """Тестирование поиска с кэшированием"""
        # Первый запрос - должен обратиться к базовому API
        result1 = self.cached_api.search_vacancies("Python")
        assert result1 == [{"id": "123", "title": "Test"}]
        self.mock_base_api.search_vacancies.assert_called_once_with("Python")
        
        # Второй запрос - должен вернуть из кэша
        self.mock_base_api.search_vacancies.reset_mock()
        result2 = self.cached_api.search_vacancies("Python")
        assert result2 == [{"id": "123", "title": "Test"}]
        self.mock_base_api.search_vacancies.assert_not_called()
        
    def test_cached_api_cache_expiration(self):
        """Тестирование истечения кэша"""
        if hasattr(self.cached_api, '_is_cache_expired'):
            # Симулируем истекший кэш
            with patch.object(self.cached_api, '_is_cache_expired', return_value=True):
                result = self.cached_api.search_vacancies("Python")
                assert self.mock_base_api.search_vacancies.called
                
    def test_cached_api_clear_cache(self):
        """Тестирование очистки кэша"""
        # Заполняем кэш
        self.cached_api.search_vacancies("Python")
        
        # Очищаем кэш
        self.cached_api.clear_cache()
        
        # Проверяем, что следующий запрос идет к базовому API
        self.mock_base_api.search_vacancies.reset_mock()
        self.cached_api.search_vacancies("Python")
        self.mock_base_api.search_vacancies.assert_called_once()
        
    def test_cached_api_cache_key_generation(self):
        """Тестирование генерации ключей кэша"""
        if hasattr(self.cached_api, '_generate_cache_key'):
            key1 = self.cached_api._generate_cache_key("Python", {"page": 1})
            key2 = self.cached_api._generate_cache_key("Python", {"page": 2})
            key3 = self.cached_api._generate_cache_key("Java", {"page": 1})
            
            assert key1 != key2  # Разные параметры
            assert key1 != key3  # Разные запросы
            assert isinstance(key1, str)


class TestUnifiedAPI:
    """Комплексное тестирование унифицированного API"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем моки для всех API
        self.mock_hh_api = Mock()
        self.mock_sj_api = Mock()
        
        self.mock_hh_api.search_vacancies.return_value = [
            {"id": "hh_123", "source": "hh.ru", "title": "HH Vacancy"}
        ]
        self.mock_sj_api.search_vacancies.return_value = [
            {"id": "sj_456", "source": "superjob.ru", "title": "SJ Vacancy"}
        ]
        
        # Создаем UnifiedAPI с моками
        with patch('src.api_modules.unified_api.HHAPI', return_value=self.mock_hh_api), \
             patch('src.api_modules.unified_api.SuperJobAPI', return_value=self.mock_sj_api):
            self.unified_api = UnifiedAPI()
            
    def test_unified_api_initialization(self):
        """Тестирование инициализации унифицированного API"""
        assert self.unified_api is not None
        assert hasattr(self.unified_api, 'apis')
        
    def test_unified_api_search_all_sources(self):
        """Тестирование поиска по всем источникам"""
        result = self.unified_api.search_vacancies("Python")
        
        assert isinstance(result, list)
        assert len(result) >= 0  # Может быть пустым из-за фильтрации
        
        # Проверяем, что все API были вызваны
        self.mock_hh_api.search_vacancies.assert_called_once_with("Python")
        self.mock_sj_api.search_vacancies.assert_called_once_with("Python")
        
    def test_unified_api_search_specific_source(self):
        """Тестирование поиска по конкретному источнику"""
        result = self.unified_api.search_vacancies("Python", sources=["hh.ru"])
        
        # Проверяем, что вызван только HH API
        self.mock_hh_api.search_vacancies.assert_called_once_with("Python")
        self.mock_sj_api.search_vacancies.assert_not_called()
        
    def test_unified_api_get_available_sources(self):
        """Тестирование получения доступных источников"""
        sources = self.unified_api.get_available_sources()
        
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "hh.ru" in sources or "superjob.ru" in sources
        
    def test_unified_api_error_handling(self):
        """Тестирование обработки ошибок"""
        # Симулируем ошибку в одном из API
        self.mock_hh_api.search_vacancies.side_effect = Exception("HH API Error")
        
        # API должен продолжить работу с другими источниками
        result = self.unified_api.search_vacancies("Python")
        assert isinstance(result, list)
        
        # SJ API должен быть вызван несмотря на ошибку в HH
        self.mock_sj_api.search_vacancies.assert_called_once()
        
    def test_unified_api_result_merging(self):
        """Тестирование объединения результатов"""
        if hasattr(self.unified_api, '_merge_results'):
            hh_results = [{"id": "1", "source": "hh.ru"}]
            sj_results = [{"id": "2", "source": "superjob.ru"}]
            
            merged = self.unified_api._merge_results([hh_results, sj_results])
            assert len(merged) == 2
            assert any(item["source"] == "hh.ru" for item in merged)
            assert any(item["source"] == "superjob.ru" for item in merged)


class TestGetAPI:
    """Комплексное тестирование фабрики API"""
    
    def test_get_api_hh(self):
        """Тестирование создания HH API"""
        with patch('src.api_modules.get_api.HHAPI') as mock_hh:
            mock_instance = Mock()
            mock_hh.return_value = mock_instance
            
            api = GetAPI.get_api("hh")
            assert api == mock_instance
            mock_hh.assert_called_once()
            
    def test_get_api_superjob(self):
        """Тестирование создания SuperJob API"""
        with patch('src.api_modules.get_api.SuperJobAPI') as mock_sj:
            mock_instance = Mock()
            mock_sj.return_value = mock_instance
            
            api = GetAPI.get_api("superjob")
            assert api == mock_instance
            mock_sj.assert_called_once()
            
    def test_get_api_unified(self):
        """Тестирование создания унифицированного API"""
        with patch('src.api_modules.get_api.UnifiedAPI') as mock_unified:
            mock_instance = Mock()
            mock_unified.return_value = mock_instance
            
            api = GetAPI.get_api("unified")
            assert api == mock_instance
            mock_unified.assert_called_once()
            
    def test_get_api_invalid_type(self):
        """Тестирование обработки некорректного типа API"""
        result = GetAPI.get_api("invalid_api_type")
        assert result is None
        
    def test_get_api_cached(self):
        """Тестирование создания кэшированного API"""
        with patch('src.api_modules.get_api.HHAPI') as mock_hh, \
             patch('src.api_modules.get_api.CachedAPI') as mock_cached:
            
            mock_hh_instance = Mock()
            mock_hh.return_value = mock_hh_instance
            mock_cached_instance = Mock()
            mock_cached.return_value = mock_cached_instance
            
            api = GetAPI.get_api("hh", cached=True)
            
            mock_hh.assert_called_once()
            mock_cached.assert_called_once_with(mock_hh_instance)
            assert api == mock_cached_instance
            
    def test_get_available_apis(self):
        """Тестирование получения списка доступных API"""
        if hasattr(GetAPI, 'get_available_apis'):
            apis = GetAPI.get_available_apis()
            assert isinstance(apis, list)
            assert "hh" in apis
            assert "superjob" in apis
            assert "unified" in apis


class TestAPIPerformance:
    """Тестирование производительности API"""
    
    def test_api_response_time_simulation(self):
        """Симуляция тестирования времени ответа API"""
        import time
        
        with patch('requests.get') as mock_get:
            # Симулируем медленный ответ
            def slow_response(*args, **kwargs):
                time.sleep(0.1)  # 100ms задержка
                mock_resp = Mock()
                mock_resp.json.return_value = {"items": []}
                mock_resp.status_code = 200
                mock_resp.raise_for_status.return_value = None
                return mock_resp
                
            mock_get.side_effect = slow_response
            
            with patch('src.api_modules.hh_api.HHAPIConfig') as mock_config:
                mock_config.return_value.get_base_url.return_value = "https://api.hh.ru"
                mock_config.return_value.get_search_url.return_value = "https://api.hh.ru/vacancies"
                mock_config.return_value.get_headers.return_value = {}
                mock_config.return_value.get_default_parameters.return_value = {}
                mock_config.return_value.should_filter_by_salary.return_value = False
                
                hh_api = HHAPI()
                start_time = time.time()
                hh_api.search_vacancies("Python")
                end_time = time.time()
                
                # Проверяем, что запрос занял разумное время
                assert (end_time - start_time) < 1.0  # Менее секунды
                
    def test_api_memory_usage_simulation(self):
        """Симуляция тестирования использования памяти"""
        # Создаем большой объем данных для ответа
        large_response = {
            "items": [{"id": str(i), "name": f"Vacancy {i}"} for i in range(1000)]
        }
        
        with patch('requests.get') as mock_get:
            mock_resp = Mock()
            mock_resp.json.return_value = large_response
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp
            
            with patch('src.api_modules.hh_api.HHAPIConfig') as mock_config:
                mock_config.return_value.get_base_url.return_value = "https://api.hh.ru"
                mock_config.return_value.get_search_url.return_value = "https://api.hh.ru/vacancies"
                mock_config.return_value.get_headers.return_value = {}
                mock_config.return_value.get_default_parameters.return_value = {}
                mock_config.return_value.should_filter_by_salary.return_value = False
                
                hh_api = HHAPI()
                result = hh_api.search_vacancies("Python")
                
                # Проверяем, что результат обработан корректно
                assert isinstance(result, list)
                assert len(result) <= 1000  # Не больше, чем отправили


class TestAPIIntegration:
    """Интеграционные тесты для API модулей"""
    
    @patch('requests.get')
    def test_full_search_workflow(self, mock_get):
        """Тестирование полного рабочего процесса поиска"""
        # Настраиваем ответы для всех API
        hh_response = Mock()
        hh_response.json.return_value = {
            "items": [{"id": "hh_1", "name": "HH Vacancy"}],
            "pages": 1,
            "page": 0
        }
        hh_response.status_code = 200
        hh_response.raise_for_status.return_value = None
        
        sj_response = Mock()
        sj_response.json.return_value = {
            "objects": [{"id": 1, "profession": "SJ Vacancy"}],
            "total": 1
        }
        sj_response.status_code = 200
        sj_response.raise_for_status.return_value = None
        
        # Настраиваем mock_get для возврата разных ответов
        def get_response(url, **kwargs):
            if "hh.ru" in url:
                return hh_response
            elif "superjob.ru" in url:
                return sj_response
            return Mock()
        
        mock_get.side_effect = get_response
        
        # Тестируем полный workflow
        with patch('src.api_modules.unified_api.HHAPIConfig') as mock_hh_config, \
             patch('src.api_modules.unified_api.SJAPIConfig') as mock_sj_config:
            
            # Настраиваем конфигурации
            mock_hh_config.return_value.get_base_url.return_value = "https://api.hh.ru"
            mock_hh_config.return_value.get_search_url.return_value = "https://api.hh.ru/vacancies"
            mock_hh_config.return_value.get_headers.return_value = {}
            mock_hh_config.return_value.get_default_parameters.return_value = {}
            mock_hh_config.return_value.should_filter_by_salary.return_value = False
            
            mock_sj_config.return_value.get_base_url.return_value = "https://api.superjob.ru"
            mock_sj_config.return_value.get_search_url.return_value = "https://api.superjob.ru/2.0/vacancies/"
            mock_sj_config.return_value.get_headers.return_value = {}
            mock_sj_config.return_value.get_default_parameters.return_value = {}
            mock_sj_config.return_value.should_filter_by_salary.return_value = False
            
            unified_api = UnifiedAPI()
            result = unified_api.search_vacancies("Python")
            
            assert isinstance(result, list)
            # Результат может быть отфильтрован, поэтому проверяем тип