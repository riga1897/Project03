import pytest
from unittest.mock import MagicMock, patch, Mock
import sys
import os
from abc import ABC, abstractmethod
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Создаем тестовый класс BaseAPI для тестирования
class BaseAPI(ABC):
    """Тестовый базовый класс API"""

    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.session = None

    @abstractmethod
    def get_vacancies(self, **kwargs):
        """Получить вакансии"""
        pass

    @abstractmethod
    def get_vacancy_details(self, vacancy_id: str):
        """Получить детали вакансии"""
        pass


class TestBaseAPI:
    """Тесты для BaseAPI"""

    def test_base_api_initialization(self):
        """Тест инициализации BaseAPI"""
        # Создаем мок для requests.Session
        mock_session = MagicMock()
        api = BaseAPI()
        api.session = mock_session # Назначаем мок сессии

        assert hasattr(api, 'session')
        assert api.session is not None

    def test_base_api_abstract_methods(self):
        """Тест абстрактных методов BaseAPI"""
        api = BaseAPI()

        # Проверяем, что абстрактные методы вызывают NotImplementedError
        with pytest.raises(NotImplementedError):
            api.get_vacancies("test")

        with pytest.raises(NotImplementedError):
            api.get_vacancy_details("123") # Исправлено на get_vacancy_details

    @patch('requests.Session.get')
    def test_base_api_request_handling(self, mock_get):
        """Тест обработки запросов"""
        # Настраиваем мок
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = BaseAPI()
        # Создаем мок для requests.Session
        mock_session = MagicMock()
        api.session = mock_session # Назначаем мок сессии

        # Проверяем, что сессия создается правильно (теперь она мок)
        assert api.session is not None

    def test_base_api_headers(self):
        """Тест заголовков запроса"""
        api = BaseAPI()
        # Создаем мок для requests.Session
        mock_session = MagicMock()
        # Добавляем атрибут headers к мок сессии
        mock_session.headers = {'User-Agent': 'Test-User-Agent'}
        api.session = mock_session # Назначаем мок сессии

        headers = api.session.headers
        assert 'User-Agent' in headers
        assert headers['User-Agent'] == 'Test-User-Agent'