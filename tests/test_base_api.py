
import pytest
from unittest.mock import MagicMock, patch, Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Импортируем из реального кода
from src.api_modules.base_api import BaseJobAPI

# Создаем конкретную реализацию BaseJobAPI для тестирования
class ConcreteBaseJobAPI(BaseJobAPI):
    """Конкретная реализация BaseJobAPI для тестов"""

    def get_vacancies(self, search_query: str, **kwargs):
        """Базовая реализация получения вакансий"""
        # Мок реализация для тестов
        return [
            {
                "id": "123",
                "name": "Test Vacancy",
                "employer": {"name": "Test Company"},
                "salary": {"from": 100000, "to": 150000}
            }
        ]

    def _validate_vacancy(self, vacancy):
        """Базовая реализация валидации вакансии"""
        required_fields = ["id", "name", "employer"]
        return all(field in vacancy for field in required_fields)


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('shutil.rmtree')
    def test_clear_cache_existing_directory(self, mock_rmtree, mock_makedirs, mock_exists):
        """Тест очистки существующего кэша"""
        # Консолидированный мок для всех операций с файловой системой
        mock_exists.return_value = True
        
        api = ConcreteBaseJobAPI()
        api.clear_cache("hh")
        
        mock_exists.assert_called_once_with("data/cache/hh")
        mock_rmtree.assert_called_once_with("data/cache/hh")
        mock_makedirs.assert_called_once_with("data/cache/hh", exist_ok=True)

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_clear_cache_non_existing_directory(self, mock_makedirs, mock_exists):
        """Тест создания нового кэша"""
        # Консолидированный мок для операций с несуществующей директорией
        mock_exists.return_value = False
        
        api = ConcreteBaseJobAPI()
        api.clear_cache("sj")
        
        mock_exists.assert_called_once_with("data/cache/sj")
        mock_makedirs.assert_called_once_with("data/cache/sj", exist_ok=True)

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_clear_cache_exception_handling(self, mock_makedirs, mock_exists):
        """Тест обработки исключений при очистке кэша"""
        # Консолидированный мок с исключением
        mock_exists.side_effect = OSError("Permission denied")
        
        api = ConcreteBaseJobAPI()
        
        with pytest.raises(OSError):
            api.clear_cache("test")

    def test_get_vacancies_abstract_method(self):
        """Тест абстрактного метода get_vacancies"""
        api = ConcreteBaseJobAPI()
        
        # Проверяем, что конкретная реализация работает
        vacancies = api.get_vacancies("Python developer")
        assert isinstance(vacancies, list)
        assert len(vacancies) > 0
        assert "id" in vacancies[0]

    def test_validate_vacancy_abstract_method(self):
        """Тест абстрактного метода _validate_vacancy"""
        api = ConcreteBaseJobAPI()
        
        # Тест валидной вакансии
        valid_vacancy = {
            "id": "123",
            "name": "Test Vacancy",
            "employer": {"name": "Test Company"}
        }
        assert api._validate_vacancy(valid_vacancy) is True
        
        # Тест невалидной вакансии
        invalid_vacancy = {"id": "123"}
        assert api._validate_vacancy(invalid_vacancy) is False

    def test_base_job_api_abstract_class(self):
        """Тест что BaseJobAPI является абстрактным классом"""
        with pytest.raises(TypeError):
            BaseJobAPI()
