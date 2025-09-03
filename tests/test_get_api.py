#!/usr/bin/env python3
"""
Тесты для модуля get_api.py
"""

import os
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig


class TestAPIConnector:
    """Тесты для класса APIConnector"""
    
    @pytest.fixture
    def api_config(self):
        """Создание мок-конфигурации API"""
        config = Mock(spec=APIConfig)
        config.user_agent = "Test User Agent"
        config.timeout = 30
        return config
    
    @pytest.fixture
    def api_connector(self, api_config):
        """Создание экземпляра APIConnector для тестов"""
        return APIConnector(api_config)
    
    def test_api_connector_initialization_with_config(self, api_config):
        """Тест инициализации APIConnector с конфигурацией"""
        connector = APIConnector(api_config)
        
        assert connector.config == api_config
        assert connector.headers["User-Agent"] == "Test User Agent"
        assert connector.headers["Accept"] == "application/json"
        assert connector._progress is None
    
    def test_api_connector_initialization_without_config(self):
        """Тест инициализации APIConnector без конфигурации"""
        with patch('src.api_modules.get_api.APIConfig') as mock_config_class:
            mock_config = Mock()
            mock_config.user_agent = "Default User Agent"
            mock_config.timeout = 30
            mock_config_class.return_value = mock_config
            
            connector = APIConnector()
            
            assert connector.config == mock_config
            assert connector.headers["User-Agent"] == "Default User Agent"
            assert connector.headers["Accept"] == "application/json"
    
    @patch('src.api_modules.get_api.tqdm')
    def test_init_progress(self, mock_tqdm, api_connector):
        """Тест инициализации прогресс-бара"""
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        api_connector._init_progress(10, "Test Description")
        
        mock_tqdm.assert_called_once()
        assert api_connector._progress == mock_progress
    
    @patch('src.api_modules.get_api.os.getenv')
    @patch('src.api_modules.get_api.tqdm')
    def test_init_progress_disabled_in_tests(self, mock_tqdm, mock_getenv, api_connector):
        """Тест автоматического отключения прогресс-бара в тестах"""
        mock_getenv.return_value = "1"  # DISABLE_TQDM=1
        mock_progress = Mock()
        mock_tqdm.return_value = mock_progress
        
        api_connector._init_progress(10, "Test Description")
        
        # Проверяем, что tqdm был вызван с disable=True
        mock_tqdm.assert_called_once()
        call_args = mock_tqdm.call_args[1]
        assert call_args["disable"] is True
    
    def test_update_progress_with_progress_bar(self, api_connector):
        """Тест обновления прогресс-бара"""
        mock_progress = Mock()
        api_connector._progress = mock_progress
        
        api_connector._update_progress(5)
        
        mock_progress.update.assert_called_once_with(5)
    
    def test_update_progress_without_progress_bar(self, api_connector):
        """Тест обновления прогресс-бара без прогресс-бара"""
        api_connector._progress = None
        
        # Не должно быть ошибок
        api_connector._update_progress(5)
    
    def test_close_progress_with_progress_bar(self, api_connector):
        """Тест закрытия прогресс-бара"""
        mock_progress = Mock()
        api_connector._progress = mock_progress
        
        api_connector._close_progress()
        
        mock_progress.close.assert_called_once()
        assert api_connector._progress is None
    
    def test_close_progress_without_progress_bar(self, api_connector):
        """Тест закрытия прогресс-бара без прогресс-бара"""
        api_connector._progress = None
        
        # Не должно быть ошибок
        api_connector._close_progress()
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_successful_request(self, mock_get, mock_sleep, api_connector):
        """Тест успешного API запроса"""
        # Мокаем ответ
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "1"}]}
        mock_get.return_value = mock_response
        
        # Мокаем tqdm
        with patch('src.api_modules.get_api.tqdm') as mock_tqdm:
            mock_progress = Mock()
            mock_tqdm.return_value = mock_progress
            
            result = api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"},
                show_progress=True,
                progress_desc="Test Request"
            )
            
            assert result == {"items": [{"id": "1"}]}
            mock_sleep.assert_called_once_with(0.15)
            mock_get.assert_called_once()
            mock_progress.update.assert_called_once()
            mock_progress.close.assert_called_once()
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_without_progress(self, mock_get, mock_sleep, api_connector):
        """Тест API запроса без прогресс-бара"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        result = api_connector._APIConnector__connect(
            "https://api.test.com/vacancies",
            {"text": "Python"}
        )
        
        assert result == {"items": []}
        assert api_connector._progress is None
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_rate_limit_handling(self, mock_get, mock_sleep, api_connector):
        """Тест обработки ограничения скорости (429)"""
        # Первый ответ с 429
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "2"}
        
        # Второй успешный ответ
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"items": [{"id": "1"}]}
        
        mock_get.side_effect = [mock_response_429, mock_response_success]
        
        result = api_connector._APIConnector__connect(
            "https://api.test.com/vacancies",
            {"text": "Python"}
        )
        
        assert result == {"items": [{"id": "1"}]}
        # Проверяем, что sleep был вызван для Retry-After
        assert mock_sleep.call_count >= 2
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_timeout_error(self, mock_get, mock_sleep, api_connector):
        """Тест обработки ошибки таймаута"""
        mock_get.side_effect = requests.Timeout("Request timeout")
        
        with pytest.raises(ConnectionError, match="Timeout error: Request timeout"):
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_http_error(self, mock_get, mock_sleep, api_connector):
        """Тест обработки HTTP ошибки"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_http_error = requests.HTTPError("500 Server Error")
        mock_http_error.response = mock_response
        mock_get.side_effect = mock_http_error
        
        with pytest.raises(ConnectionError, match="HTTP error 500: Internal Server Error"):
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_http_error_no_response(self, mock_get, mock_sleep, api_connector):
        """Тест обработки HTTP ошибки без деталей ответа"""
        mock_http_error = requests.HTTPError("HTTP Error")
        mock_http_error.response = None
        mock_get.side_effect = mock_http_error
        
        with pytest.raises(ConnectionError, match="HTTP error \\(no response details\\)"):
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_request_exception(self, mock_get, mock_sleep, api_connector):
        """Тест обработки общей ошибки запроса"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with pytest.raises(ConnectionError, match="Connection error: Network error"):
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_json_decode_error(self, mock_get, mock_sleep, api_connector):
        """Тест обработки ошибки декодирования JSON"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(ConnectionError, match="JSON decode error: Invalid JSON"):
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_unexpected_error(self, mock_get, mock_sleep, api_connector):
        """Тест обработки неожиданной ошибки"""
        mock_get.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ConnectionError, match="Unexpected error: Unexpected error"):
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_filters_none_params(self, mock_get, mock_sleep, api_connector):
        """Тест фильтрации None параметров"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        api_connector._APIConnector__connect(
            "https://api.test.com/vacancies",
            {"text": "Python", "page": None, "per_page": 20}
        )
        
        # Проверяем, что None параметры были отфильтрованы
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert "page" not in params
        assert "per_page" in params
        assert params["per_page"] == 20
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_custom_delay(self, mock_get, mock_sleep, api_connector):
        """Тест пользовательской задержки между запросами"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        api_connector._APIConnector__connect(
            "https://api.test.com/vacancies",
            {"text": "Python"},
            delay=0.5
        )
        
        mock_sleep.assert_called_once_with(0.5)
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_progress_description_auto_generation(self, mock_get, mock_sleep, api_connector):
        """Тест автоматической генерации описания прогресса"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        with patch('src.api_modules.get_api.tqdm') as mock_tqdm:
            mock_progress = Mock()
            mock_tqdm.return_value = mock_progress
            
            api_connector._APIConnector__connect(
                "https://api.test.com/vacancies/search",
                {"text": "Python"},
                show_progress=True
            )
            
            # Проверяем, что описание было сгенерировано автоматически
            mock_tqdm.assert_called_once()
            call_args = mock_tqdm.call_args[1]
            assert call_args["desc"] == "Request to search"
    
    def test_connect_public_method(self, api_connector):
        """Тест публичного метода connect"""
        with patch.object(api_connector, '_APIConnector__connect') as mock_private:
            mock_private.return_value = {"items": []}
            
            result = api_connector.connect(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
            
            assert result == {"items": []}
            mock_private.assert_called_once_with(
                "https://api.test.com/vacancies",
                {"text": "Python"}
            )
    
    def test_connect_public_method_default_params(self, api_connector):
        """Тест публичного метода connect с параметрами по умолчанию"""
        with patch.object(api_connector, '_APIConnector__connect') as mock_private:
            mock_private.return_value = {"items": []}
            
            result = api_connector.connect("https://api.test.com/vacancies")
            
            assert result == {"items": []}
            mock_private.assert_called_once_with(
                "https://api.test.com/vacancies",
                None
            )
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_headers_in_request(self, mock_get, mock_sleep, api_connector):
        """Тест передачи заголовков в запросе"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        api_connector._APIConnector__connect(
            "https://api.test.com/vacancies",
            {"text": "Python"}
        )
        
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert headers["User-Agent"] == "Test User Agent"
        assert headers["Accept"] == "application/json"
    
    @patch('src.api_modules.get_api.sleep')
    @patch('src.api_modules.get_api.requests.get')
    def test_connect_timeout_config(self, mock_get, mock_sleep, api_connector):
        """Тест использования конфигурации таймаута"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        api_connector._APIConnector__connect(
            "https://api.test.com/vacancies",
            {"text": "Python"}
        )
        
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 30
    
    def test_progress_bar_cleanup_on_error(self, api_connector):
        """Тест очистки прогресс-бара при ошибке"""
        with patch('src.api_modules.get_api.tqdm') as mock_tqdm:
            mock_progress = Mock()
            mock_tqdm.return_value = mock_progress
            
            with patch('src.api_modules.get_api.requests.get', side_effect=Exception("Test error")):
                with pytest.raises(ConnectionError):
                    api_connector._APIConnector__connect(
                        "https://api.test.com/vacancies",
                        {"text": "Python"},
                        show_progress=True
                    )
                
                # Проверяем, что прогресс-бар был закрыт даже при ошибке
                mock_progress.close.assert_called_once()
                assert api_connector._progress is None
