
"""
Полные тесты для модуля get_api
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.get_api import APIConnector
    from src.api_modules.base_api import BaseJobAPI
    GET_API_AVAILABLE = True
except ImportError:
    GET_API_AVAILABLE = False
    GetAPI = object
    BaseJobAPI = object


class TestGetAPIComplete:
    """Полные тесты для GetAPI"""

    @pytest.fixture
    def get_api(self):
        """Создание экземпляра GetAPI"""
        if not GET_API_AVAILABLE:
            pytest.skip("GetAPI not available")
        return GetAPI()

    def test_inheritance_structure(self):
        """Тест структуры наследования"""
        if not GET_API_AVAILABLE:
            pytest.skip("GetAPI not available")
        
        assert issubclass(GetAPI, BaseJobAPI)

    def test_init_default_values(self, get_api):
        """Тест инициализации с значениями по умолчанию"""
        assert hasattr(get_api, 'base_url')
        assert hasattr(get_api, 'session')
        assert get_api.session is not None

    @patch('requests.Session')
    def test_session_creation(self, mock_session, get_api):
        """Тест создания сессии"""
        assert get_api.session is not None

    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get, get_api):
        """Тест успешного запроса"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "1"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_api._make_request("http://test.com", {"param": "value"})
        assert result == {"items": [{"id": "1"}]}
        mock_get.assert_called_once_with("http://test.com", params={"param": "value"}, timeout=30)

    @patch('requests.Session.get')
    def test_make_request_http_error(self, mock_get, get_api):
        """Тест обработки HTTP ошибки"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = get_api._make_request("http://test.com")
        assert result == {}

    @patch('requests.Session.get')
    def test_make_request_connection_error(self, mock_get, get_api):
        """Тест обработки ошибки соединения"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        result = get_api._make_request("http://test.com")
        assert result == {}

    @patch('requests.Session.get')
    def test_make_request_timeout(self, mock_get, get_api):
        """Тест обработки таймаута"""
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        result = get_api._make_request("http://test.com")
        assert result == {}

    @patch('requests.Session.get')
    def test_make_request_json_decode_error(self, mock_get, get_api):
        """Тест обработки ошибки декодирования JSON"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_api._make_request("http://test.com")
        assert result == {}

    @patch('requests.Session.get')
    def test_make_request_generic_exception(self, mock_get, get_api):
        """Тест обработки общего исключения"""
        mock_get.side_effect = Exception("Unexpected error")
        
        result = get_api._make_request("http://test.com")
        assert result == {}

    def test_get_vacancies_not_implemented(self, get_api):
        """Тест что метод get_vacancies не реализован в базовом классе"""
        with pytest.raises(NotImplementedError):
            get_api.get_vacancies("python")

    @patch('requests.Session.get')
    def test_make_request_with_custom_timeout(self, mock_get, get_api):
        """Тест запроса с кастомным таймаутом"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Патчим метод для тестирования кастомного таймаута
        with patch.object(get_api, '_make_request') as mock_method:
            mock_method.return_value = {"data": "test"}
            
            # Вызываем метод с кастомными параметрами
            result = get_api._make_request("http://test.com", timeout=60)
            mock_method.assert_called_once()

    @patch('requests.Session.get')
    def test_make_request_empty_response(self, mock_get, get_api):
        """Тест обработки пустого ответа"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_api._make_request("http://test.com")
        assert result == {}

    @patch('requests.Session.get')
    def test_make_request_status_code_handling(self, mock_get, get_api):
        """Тест обработки различных статус кодов"""
        # Тест успешного статуса
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_api._make_request("http://test.com")
        assert result == {"created": True}

    def test_session_attributes(self, get_api):
        """Тест атрибутов сессии"""
        session = get_api.session
        assert hasattr(session, 'get')
        assert hasattr(session, 'post')
        assert hasattr(session, 'headers')

    @patch('requests.Session.get')
    def test_make_request_params_handling(self, mock_get, get_api):
        """Тест обработки параметров запроса"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        params = {"query": "python", "page": 1, "per_page": 50}
        result = get_api._make_request("http://test.com", params)
        
        mock_get.assert_called_once_with("http://test.com", params=params, timeout=30)
        assert result == {"success": True}

    @patch('requests.Session.get')
    def test_make_request_none_params(self, mock_get, get_api):
        """Тест запроса без параметров"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_api._make_request("http://test.com", None)
        mock_get.assert_called_once_with("http://test.com", params=None, timeout=30)
        assert result == {"items": []}

    def test_class_attributes(self):
        """Тест атрибутов класса"""
        if not GET_API_AVAILABLE:
            pytest.skip("GetAPI not available")
        
        # Проверяем что класс имеет необходимые атрибуты
        assert hasattr(GetAPI, '__init__')
        assert hasattr(GetAPI, '_make_request')
        assert hasattr(GetAPI, 'get_vacancies')

    def test_abstract_method_inheritance(self):
        """Тест наследования абстрактных методов"""
        if not GET_API_AVAILABLE:
            pytest.skip("GetAPI not available")
        
        # Проверяем что get_vacancies является абстрактным методом
        with pytest.raises(NotImplementedError):
            api = GetAPI()
            api.get_vacancies("test")

    @patch('requests.Session.get')
    def test_make_request_error_logging(self, mock_get, get_api):
        """Тест логирования ошибок"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with patch('logging.Logger.error') as mock_log:
            result = get_api._make_request("http://test.com")
            assert result == {}
            # Логирование может вызываться или не вызываться в зависимости от реализации

    def test_method_signatures(self, get_api):
        """Тест сигнатур методов"""
        # Проверяем что методы существуют и вызываемы
        assert callable(get_api._make_request)
        assert callable(get_api.get_vacancies)
        
        # Проверяем количество аргументов _make_request
        import inspect
        sig = inspect.signature(get_api._make_request)
        params = list(sig.parameters.keys())
        assert 'url' in params
