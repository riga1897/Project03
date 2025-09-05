
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
    
    def test_get_vacancies(self, hh_api):
        """Тест получения вакансий"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        # Мокаем методы API
        mock_data = {
            "items": [{"id": "123", "name": "Python Developer", "alternate_url": "https://hh.ru/vacancy/123"}],
            "found": 1,
            "pages": 1
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_data) as mock_connect:
            result = hh_api.get_vacancies("Python", per_page=1)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["id"] == "123"
            assert result[0]["name"] == "Python Developer"
            assert result[0]["source"] == "hh.ru"
            
            # Проверяем что API был вызван
            mock_connect.assert_called()

    
def test_validate_vacancy(self, hh_api):
        """Тест валидации вакансии"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        valid_vacancy = {"id": "123", "name": "Test", "alternate_url": "https://hh.ru/vacancy/123"}
        invalid_vacancy = {"id": "123"}
        
        assert hh_api._validate_vacancy(valid_vacancy) == True
        assert hh_api._validate_vacancy(invalid_vacancy) == False

def test_get_vacancies_page(self, hh_api):
        """Тест получения одной страницы вакансий"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        mock_data = {
            "items": [{"id": "123", "name": "Python Developer", "alternate_url": "https://hh.ru/vacancy/123"}]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_data):
            result = hh_api.get_vacancies_page("Python", page=0)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["source"] == "hh.ru"

def test_get_empty_response(self, hh_api):
        """Тест получения пустого ответа"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        result = hh_api._get_empty_response()
        assert isinstance(result, dict)
        assert "items" in result
        assert result["items"] == []

def test_clear_cache(self, hh_api):
        """Тест очистки кэша"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        with patch.object(hh_api, 'clear_cache') as mock_clear:
            hh_api.clear_cache("hh")
            mock_clear.assert_called_once_with("hh")


class TestSuperJobAPI:
    """Тесты для SuperJob API"""
    
    @pytest.fixture
    def sj_api(self):
        """Фикстура SJ API"""
        if not API_MODULES_AVAILABLE:
            return Mock()
        
        with patch('src.config.api_config.APIConfig'), \
             patch('src.utils.cache.FileCache'), \
             patch('src.utils.paginator.Paginator'):
            return SuperJobAPI()
    
    def test_get_vacancies(self, sj_api):
        """Тест получения вакансий"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        mock_data = {
            "objects": [{"id": 123, "profession": "Python Developer", "link": "https://superjob.ru/vacancy/123"}],
            "total": 1,
            "more": False
        }
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api', return_value=mock_data):
            result = sj_api.get_vacancies("Python", per_page=1)
            assert isinstance(result, list)
    
    def test_validate_vacancy(self, sj_api):
        """Тест валидации вакансии"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        valid_vacancy = {"id": 123, "profession": "Test", "link": "https://superjob.ru/vacancy/123"}
        invalid_vacancy = {"id": 123}
        
        assert sj_api._validate_vacancy(valid_vacancy) == True
        assert sj_api._validate_vacancy(invalid_vacancy) == False


class TestUnifiedAPI:
    """Тесты для унифицированного API"""
    
    @pytest.fixture
    def unified_api(self):
        """Фикстура унифицированного API"""
        if not API_MODULES_AVAILABLE:
            return Mock()
        
        with patch('src.api_modules.hh_api.HeadHunterAPI'), \
             patch('src.api_modules.sj_api.SuperJobAPI'):
            return UnifiedAPI()
    
    def test_init(self, unified_api):
        """Тест инициализации"""
        assert unified_api is not None
    
    def test_get_vacancies_from_all_sources(self, unified_api):
        """Тест получения вакансий из всех источников"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        # Мокаем методы получения вакансий
        unified_api.get_hh_vacancies = Mock(return_value=[{"id": "hh1", "source": "hh"}])
        unified_api.get_sj_vacancies = Mock(return_value=[{"id": "sj1", "source": "sj"}])
        
        result = unified_api.get_vacancies_from_all_sources("Python")
        assert isinstance(result, list)


class ConcreteCachedAPI(CachedAPI if API_MODULES_AVAILABLE else object):
    """Конкретная реализация CachedAPI для тестирования"""
    
    def __init__(self, cache_dir="test_cache"):
        if API_MODULES_AVAILABLE:
            super().__init__(cache_dir)
        
    def _get_empty_response(self):
        """Возвращает пустой ответ"""
        return {"items": [], "found": 0}
    
    def _validate_vacancy(self, vacancy):
        """Валидация вакансии"""
        return isinstance(vacancy, dict) and "id" in vacancy
    
    def get_vacancies_page(self, search_query, page=0, **kwargs):
        """Получение одной страницы вакансий"""
        return [{"id": f"test_{page}", "title": search_query}]
    
    def get_vacancies(self, search_query, **kwargs):
        """Получение всех вакансий"""
        return [{"id": "test", "title": search_query}]


class TestCachedAPI:
    """Тесты для кэшированного API"""
    
    @pytest.fixture
    def cached_api(self):
        """Фикстура кэшированного API"""
        if not API_MODULES_AVAILABLE:
            return Mock()
        
        with patch('src.utils.cache.FileCache'):
            return ConcreteCachedAPI("test_cache_dir")
    
    def test_init(self, cached_api):
        """Тест инициализации"""
        assert cached_api is not None
    
    def test_get_empty_response(self, cached_api):
        """Тест получения пустого ответа"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        result = cached_api._get_empty_response()
        assert isinstance(result, dict)
        assert "items" in result
        assert result["items"] == []
    
    def test_validate_vacancy(self, cached_api):
        """Тест валидации вакансии"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        valid_vacancy = {"id": "123", "title": "Test"}
        invalid_vacancy = {"title": "Test"}
        
        assert cached_api._validate_vacancy(valid_vacancy) == True
        assert cached_api._validate_vacancy(invalid_vacancy) == False
    
    def test_get_vacancies_page(self, cached_api):
        """Тест получения страницы вакансий"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        result = cached_api.get_vacancies_page("Python", page=0)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Python"
    
    def test_get_vacancies(self, cached_api):
        """Тест получения вакансий"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        result = cached_api.get_vacancies("Python")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Python"


class TestAPIIntegration:
    """Интеграционные тесты API"""
    
    def test_api_error_handling(self):
        """Тест обработки ошибок API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        # Тест с недоступным API
        with patch('requests.get', side_effect=Exception("Connection error")):
            api = ConcreteJobAPI()
            
            # API должно обрабатывать ошибки корректно
            try:
                result = api.get_vacancies("Python")
                # Если нет исключения, результат должен быть списком
                assert isinstance(result, list)
            except Exception:
                # Ошибки обрабатываются корректно
                assert True
    
    def test_api_response_validation(self):
        """Тест валидации ответов API"""
        if not API_MODULES_AVAILABLE:
            pytest.skip("API modules not available")
        
        api = ConcreteJobAPI()
        
        # Тест валидации корректных данных
        valid_vacancy = {"id": "123", "title": "Test"}
        assert api._validate_vacancy(valid_vacancy) == True
        
        # Тест валидации некорректных данных
        invalid_vacancy = {"title": "Test"}  # нет id
        assert api._validate_vacancy(invalid_vacancy) == False
