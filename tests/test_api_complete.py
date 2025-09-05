
"""
Полные тесты для API модулей
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.base_api import BaseJobAPI
    from src.api_modules.hh_api import HeadHunterAPI
    from src.api_modules.sj_api import SuperJobAPI
    from src.api_modules.unified_api import UnifiedAPI
    from src.api_modules.cached_api import CachedAPI
    API_MODULES_AVAILABLE = True
except ImportError:
    API_MODULES_AVAILABLE = False
    BaseJobAPI = object
    HeadHunterAPI = object
    SuperJobAPI = object
    UnifiedAPI = object
    CachedAPI = object


class ConcreteJobAPI(BaseJobAPI if API_MODULES_AVAILABLE else object):
    """Конкретная реализация BaseJobAPI для тестирования"""
    
    def get_vacancies(self, search_query, **kwargs):
        return [{"id": "1", "title": search_query}]
    
    def _validate_vacancy(self, vacancy):
        return isinstance(vacancy, dict) and "id" in vacancy


class TestBaseJobAPI:
    """Тесты для базового класса API"""

    def test_base_api_cannot_be_instantiated(self):
        """Тест что базовый класс нельзя инстанциировать"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_concrete_implementation_works(self):
        """Тест что конкретная реализация работает"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")

        api = ConcreteJobAPI()
        assert api is not None

        # Тест get_vacancies
        result = api.get_vacancies("Python")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Python"

        # Тест _validate_vacancy
        assert api._validate_vacancy({"id": "123"}) == True
        assert api._validate_vacancy({}) == False
    
    @patch('os.path.exists', return_value=True)
    @patch('shutil.rmtree')
    @patch('os.makedirs')
    def test_clear_cache(self, mock_makedirs, mock_rmtree, mock_exists):
        """Тест очистки кэша"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        api = ConcreteJobAPI()
        api.clear_cache("test_source")
        
        mock_rmtree.assert_called_once()
        mock_makedirs.assert_called_once()


class TestHeadHunterAPI:
    """Тесты для HeadHunter API"""
    
    @pytest.fixture
    def hh_api(self):
        """Фикстура HH API"""
        if not API_MODULES_AVAILABLE:
            return Mock()
        
        with patch('src.config.api_config.APIConfig'), \
             patch('src.utils.cache.FileCache'), \
             patch('src.utils.paginator.Paginator'):
            return HeadHunterAPI()
    
    @patch('requests.get')
    def test_get_vacancies(self, mock_get, hh_api):
        """Тест получения вакансий"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"id": "123", "name": "Python Developer"}],
            "found": 1
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        with patch.object(hh_api, '_parse_vacancy_response', return_value={"id": "123"}):
            result = hh_api.get_vacancies("Python", per_page=1)
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["id"] == "123"
            assert result[0]["name"] == "Python Developer"
            assert result[0]["source"] == "hh"
            assert "url" in result[0]

    
#     def test_validate_vacancy(self, hh_api):
#         """Тест валидации вакансии"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         valid_vacancy = {"id": "123", "name": "Test", "employer": {"name": "Company"}}
#         invalid_vacancy = {"id": "123"}
        
#         assert hh_api._validate_vacancy(valid_vacancy) == True
#         assert hh_api._validate_vacancy(invalid_vacancy) == False


# class TestSuperJobAPI:
#     """Тесты для SuperJob API"""
    
#     @pytest.fixture
#     def sj_api(self):
#         """Фикстура SJ API"""
#         if not API_MODULES_AVAILABLE:
#             return Mock()
        
#         with patch('src.config.api_config.APIConfig'), \
#              patch('src.utils.cache.FileCache'), \
#              patch('src.utils.paginator.Paginator'):
#             return SuperJobAPI()
    
#     @patch('requests.get')
#     def test_get_vacancies(self, mock_get, sj_api):
#         """Тест получения вакансий"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         # Мокаем ответ API
#         mock_response = Mock()
#         mock_response.json.return_value = {
#             "objects": [{"id": 123, "profession": "Python Developer"}],
#             "total": 1
#         }
#         mock_response.status_code = 200
#         mock_get.return_value = mock_response
        
#         with patch.object(sj_api, '_parse_vacancy_response', return_value={"id": "123"}):
#             result = sj_api.get_vacancies("Python", per_page=1)
#             assert isinstance(result, list)
    
#     def test_validate_vacancy(self, sj_api):
#         """Тест валидации вакансии"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         valid_vacancy = {"id": 123, "profession": "Test", "firm_name": "Company"}
#         invalid_vacancy = {"id": 123}
        
#         assert sj_api._validate_vacancy(valid_vacancy) == True
#         assert sj_api._validate_vacancy(invalid_vacancy) == False


# class TestUnifiedAPI:
#     """Тесты для унифицированного API"""
    
#     @pytest.fixture
#     def unified_api(self):
#         """Фикстура унифицированного API"""
#         if not API_MODULES_AVAILABLE:
#             return Mock()
        
#         with patch('src.api_modules.hh_api.HeadHunterAPI'), \
#              patch('src.api_modules.sj_api.SuperJobAPI'):
#             return UnifiedAPI()
    
#     def test_init(self, unified_api):
#         """Тест инициализации"""
#         assert unified_api is not None
    
#     @patch('src.api_modules.hh_api.HeadHunterAPI')
#     @patch('src.api_modules.sj_api.SuperJobAPI')
#     def test_get_vacancies_from_all_sources(self, mock_sj, mock_hh, unified_api):
#         """Тест получения вакансий из всех источников"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         # Мокаем ответы API
#         mock_hh_instance = Mock()
#         mock_hh_instance.get_vacancies.return_value = [{"id": "hh1", "source": "hh"}]
#         mock_hh.return_value = mock_hh_instance
        
#         mock_sj_instance = Mock()
#         mock_sj_instance.get_vacancies.return_value = [{"id": "sj1", "source": "sj"}]
#         mock_sj.return_value = mock_sj_instance
        
#         unified_api.hh_api = mock_hh_instance
#         unified_api.sj_api = mock_sj_instance
        
#         with patch.object(unified_api, '_filter_by_target_companies', side_effect=lambda x: x):
#             result = unified_api.get_vacancies_from_all_sources("Python")
#             assert isinstance(result, list)


# class TestCachedAPI:
#     """Тесты для кэшированного API"""
    
#     @pytest.fixture
#     def cached_api(self):
#         """Фикстура кэшированного API"""
#         if not API_MODULES_AVAILABLE:
#             return Mock()
        
#         base_api = Mock()
#         base_api.get_vacancies.return_value = [{"id": "1", "title": "Test"}]
        
#         with patch('src.utils.cache.FileCache'):
#             return CachedAPI(base_api)
    
#     def test_init(self, cached_api):
#         """Тест инициализации"""
#         assert cached_api is not None
    
#     def test_get_vacancies_cached(self, cached_api):
#         """Тест получения вакансий с кэшированием"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         with patch.object(cached_api, 'cache') as mock_cache:
#             mock_cache.get.return_value = None
#             mock_cache.set = Mock()
            
#             cached_api.api = Mock()
#             cached_api.api.get_vacancies.return_value = [{"id": "1"}]
            
#             result = cached_api.get_vacancies("Python")
#             assert isinstance(result, list)


# class TestAPIIntegration:
#     """Интеграционные тесты API"""
    
#     def test_api_error_handling(self):
#         """Тест обработки ошибок API"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         # Тест с недоступным API
#         with patch('requests.get', side_effect=Exception("Connection error")):
#             api = ConcreteJobAPI()
            
#             # API должно обрабатывать ошибки корректно
#             try:
#                 result = api.get_vacancies("Python")
#                 # Если нет исключения, результат должен быть списком
#                 assert isinstance(result, list)
#             except Exception:
#                 # Ошибки обрабатываются корректно
#                 assert True
    
#     def test_api_response_validation(self):
#         """Тест валидации ответов API"""
#         if not API_MODULES_AVAILABLE:
#             pytest.skip("API modules not available")
        
#         api = ConcreteJobAPI()
        
#         # Тест валидации корректных данных
#         valid_vacancy = {"id": "123", "title": "Test"}
#         assert api._validate_vacancy(valid_vacancy) == True
        
#         # Тест валидации некорректных данных
#         invalid_vacancy = {"title": "Test"}  # нет id
#         assert api._validate_vacancy(invalid_vacancy) == False
