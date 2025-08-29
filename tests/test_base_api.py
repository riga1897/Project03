
import pytest
from unittest.mock import Mock, patch
from abc import ABC

from src.api_modules.base_api import BaseJobAPI


class ConcreteAPI(BaseJobAPI):
    """Конкретная реализация BaseJobAPI для тестов"""
    
    def get_vacancies(self, search_query: str, **kwargs):
        return [
            {"id": "1", "name": "Test Vacancy 1"},
            {"id": "2", "name": "Test Vacancy 2"}
        ]
    
    def _validate_vacancy(self, vacancy):
        return True


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""

    def test_abstract_methods(self):
        """Тест абстрактных методов"""
        # BaseJobAPI нельзя инстанцировать напрямую
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_concrete_implementation(self):
        """Тест конкретной реализации"""
        api = ConcreteAPI()
        assert api is not None
        assert hasattr(api, 'get_vacancies')
        assert hasattr(api, '_validate_vacancy')

    def test_get_vacancies_implementation(self):
        """Тест реализации get_vacancies"""
        api = ConcreteAPI()
        result = api.get_vacancies("python")
        
        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

    def test_validate_vacancy_implementation(self):
        """Тест реализации _validate_vacancy"""
        api = ConcreteAPI()
        
        assert api._validate_vacancy({"id": "1", "name": "Test"}) is True

    def test_clear_cache_method_exists(self):
        """Тест что метод clear_cache существует и создает директории"""
        api = ConcreteAPI()
        
        with patch('os.path.exists') as mock_exists, \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('os.makedirs') as mock_makedirs:
            
            mock_exists.return_value = True
            
            api.clear_cache("test")
            
            mock_rmtree.assert_called_once()
            mock_makedirs.assert_called_once()

    def test_clear_cache_creates_directory_if_not_exists(self):
        """Тест создания директории кэша если её нет"""
        api = ConcreteAPI()
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.makedirs') as mock_makedirs:
            
            mock_exists.return_value = False
            
            api.clear_cache("test")
            
            mock_makedirs.assert_called_once_with("data/cache/test", exist_ok=True)

    def test_clear_cache_error_handling(self):
        """Тест обработки ошибок при очистке кэша"""
        api = ConcreteAPI()
        
        with patch('os.path.exists') as mock_exists, \
             patch('shutil.rmtree') as mock_rmtree:
            
            mock_exists.return_value = True
            mock_rmtree.side_effect = OSError("Permission denied")
            
            with pytest.raises(OSError):
                api.clear_cache("test")

    def test_inheritance_structure(self):
        """Тест структуры наследования"""
        api = ConcreteAPI()
        
        assert isinstance(api, BaseJobAPI)
        assert isinstance(api, ABC)

    def test_abstract_method_enforcement(self):
        """Тест принуждения к реализации абстрактных методов"""
        
        # Класс без реализации get_vacancies не может быть создан
        with pytest.raises(TypeError):
            class IncompleteAPI(BaseJobAPI):
                def _validate_vacancy(self, vacancy):
                    return True
            IncompleteAPI()

        # Класс без реализации _validate_vacancy не может быть создан  
        with pytest.raises(TypeError):
            class AnotherIncompleteAPI(BaseJobAPI):
                def get_vacancies(self, search_query: str, **kwargs):
                    return []
            AnotherIncompleteAPI()

    def test_method_signatures(self):
        """Тест сигнатур методов"""
        api = ConcreteAPI()
        
        # Проверяем что методы принимают правильные параметры
        vacancies = api.get_vacancies("test", per_page=50, salary_from=100000)
        assert isinstance(vacancies, list)
        
        is_valid = api._validate_vacancy({"test": "data"})
        assert isinstance(is_valid, bool)


class TestBaseJobAPIIntegration:
    """Интеграционные тесты для BaseJobAPI"""

    def test_multiple_implementations(self):
        """Тест множественных реализаций BaseJobAPI"""
        
        class APIImplementation1(BaseJobAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return [{"id": "api1_1", "source": "api1"}]
            
            def _validate_vacancy(self, vacancy):
                return vacancy.get("source") == "api1"

        class APIImplementation2(BaseJobAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return [{"id": "api2_1", "source": "api2"}]
            
            def _validate_vacancy(self, vacancy):
                return vacancy.get("source") == "api2"

        api1 = APIImplementation1()
        api2 = APIImplementation2()
        
        # Каждая реализация работает независимо
        result1 = api1.get_vacancies("test")
        result2 = api2.get_vacancies("test")
        
        assert result1[0]["source"] == "api1"
        assert result2[0]["source"] == "api2"
        
        assert api1._validate_vacancy({"source": "api1"}) is True
        assert api1._validate_vacancy({"source": "api2"}) is False
        assert api2._validate_vacancy({"source": "api2"}) is True
        assert api2._validate_vacancy({"source": "api1"}) is False

    def test_polymorphic_usage(self):
        """Тест полиморфного использования"""
        
        class MockAPI1(BaseJobAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return [{"id": "mock1", "name": "Mock Vacancy 1"}]
            
            def _validate_vacancy(self, vacancy):
                return True

        class MockAPI2(BaseJobAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return [{"id": "mock2", "name": "Mock Vacancy 2"}]
            
            def _validate_vacancy(self, vacancy):
                return True

        apis = [MockAPI1(), MockAPI2()]
        
        # Можем работать с любыми реализациями через общий интерфейс
        all_results = []
        for api in apis:
            assert isinstance(api, BaseJobAPI)
            results = api.get_vacancies("test")
            all_results.extend(results)
        
        assert len(all_results) == 2
        assert all_results[0]["id"] == "mock1"
        assert all_results[1]["id"] == "mock2"

    def test_cache_operations_multiple_sources(self):
        """Тест операций с кэшем для множественных источников"""
        api = ConcreteAPI()
        
        sources = ["hh", "sj", "custom"]
        
        with patch('os.path.exists') as mock_exists, \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('os.makedirs') as mock_makedirs:
            
            mock_exists.return_value = True
            
            for source in sources:
                api.clear_cache(source)
            
            assert mock_rmtree.call_count == len(sources)
            assert mock_makedirs.call_count == len(sources)
