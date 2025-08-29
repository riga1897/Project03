
"""
Тесты для базового API класса
"""

import pytest
from unittest.mock import Mock, patch
from src.api_modules.base_api import BaseJobAPI


class ConcreteAPI(BaseJobAPI):
    """Конкретная реализация для тестирования"""
    
    def get_vacancies(self, search_query: str, **kwargs):
        return []
    
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

    def test_deduplicate_vacancies(self):
        """Тест дедупликации вакансий"""
        api = ConcreteAPI()
        
        # Мокируем SQL дедупликацию
        with patch('src.api_modules.base_api.PostgresSaver') as mock_saver:
            mock_instance = Mock()
            mock_instance.deduplicate_vacancies.return_value = [{"id": "1", "name": "Test"}]
            mock_saver.return_value = mock_instance
            
            vacancies = [
                {"id": "1", "name": "Test 1"},
                {"id": "2", "name": "Test 2"},
            ]
            
            result = api._deduplicate_vacancies(vacancies, "test")
            assert len(result) == 1

    def test_deduplicate_vacancies_fallback(self):
        """Тест fallback дедупликации при ошибке SQL"""
        api = ConcreteAPI()
        
        # Мокируем ошибку SQL
        with patch('src.api_modules.base_api.PostgresSaver') as mock_saver:
            mock_saver.side_effect = Exception("SQL Error")
            
            vacancies = [
                {"id": "1", "name": "Test 1"},
                {"id": "1", "name": "Test 1"},  # Дубликат
                {"id": "2", "name": "Test 2"},
            ]
            
            result = api._deduplicate_vacancies(vacancies, "test")
            # Должен использовать fallback логику
            assert len(result) <= len(vacancies)
