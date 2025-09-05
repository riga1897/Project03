
"""
Полные тесты для HeadHunter API
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.hh_api import HeadHunterAPI
    from src.api_modules.base_api import BaseJobAPI
    from src.config.api_config import APIConfig
    HH_API_AVAILABLE = True
except ImportError:
    HH_API_AVAILABLE = False
    HeadHunterAPI = object
    BaseJobAPI = object
    APIConfig = object


@pytest.mark.skipif(not HH_API_AVAILABLE, reason="HH API modules not available")
class TestHeadHunterAPIComplete:
    """Полное тестирование HeadHunter API"""
    
    @pytest.fixture
    def mock_config(self):
        """Мок конфигурации"""
        config = Mock()
        config.hh_config.get_params.return_value = {
            "text": "python",
            "per_page": 50,
            "page": 0
        }
        config.get_pagination_params.return_value = {"max_pages": 20}
        return config
    
    @pytest.fixture
    def hh_api(self, mock_config):
        """Экземпляр HH API с мокированной конфигурацией"""
        with patch('src.api_modules.hh_api.APIConnector'), \
             patch('src.api_modules.hh_api.Paginator'), \
             patch('src.api_modules.hh_api.APIConfig', return_value=mock_config):
            api = HeadHunterAPI(mock_config)
            api.connector = Mock()
            api._paginator = Mock()
            return api
    
    def test_init_with_config(self, mock_config):
        """Тест инициализации с конфигурацией"""
        with patch('src.api_modules.hh_api.APIConnector'), \
             patch('src.api_modules.hh_api.Paginator'):
            api = HeadHunterAPI(mock_config)
            assert api._config == mock_config
    
    def test_init_without_config(self):
        """Тест инициализации без конфигурации"""
        with patch('src.api_modules.hh_api.APIConnector'), \
             patch('src.api_modules.hh_api.Paginator'), \
             patch('src.api_modules.hh_api.APIConfig') as mock_api_config:
            api = HeadHunterAPI()
            mock_api_config.assert_called_once()
    
    def test_get_empty_response(self, hh_api):
        """Тест получения пустого ответа"""
        result = hh_api._get_empty_response()
        assert result == {"items": []}
    
    def test_validate_vacancy_valid(self, hh_api):
        """Тест валидации корректной вакансии"""
        vacancy = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/12345"
        }
        assert hh_api._validate_vacancy(vacancy) is True
    
    def test_validate_vacancy_invalid(self, hh_api):
        """Тест валидации некорректной вакансии"""
        # Пустое название
        vacancy1 = {
            "name": "",
            "alternate_url": "https://hh.ru/vacancy/12345"
        }
        assert hh_api._validate_vacancy(vacancy1) is False
        
        # Нет URL
        vacancy2 = {
            "name": "Python Developer",
            "alternate_url": ""
        }
        assert hh_api._validate_vacancy(vacancy2) is False
        
        # Не словарь
        assert hh_api._validate_vacancy("not a dict") is False
    
    def test_get_vacancies_page_success(self, hh_api):
        """Тест успешного получения страницы вакансий"""
        mock_data = {
            "items": [
                {
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/1"
                }
            ]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_data):
            result = hh_api.get_vacancies_page("python", page=0)
            
            assert len(result) == 1
            assert result[0]["source"] == "hh.ru"
    
    def test_get_vacancies_page_error(self, hh_api):
        """Тест обработки ошибок при получении страницы"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=Exception("API Error")):
            result = hh_api.get_vacancies_page("python", page=0)
            assert result == []
    
    def test_get_vacancies_success(self, hh_api):
        """Тест успешного получения вакансий"""
        mock_initial_data = {
            "found": 100,
            "pages": 5
        }
        
        mock_page_data = [
            {"name": "Python Dev 1", "alternate_url": "https://hh.ru/1", "source": "hh.ru"},
            {"name": "Python Dev 2", "alternate_url": "https://hh.ru/2", "source": "hh.ru"}
        ]
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_initial_data), \
             patch.object(hh_api._paginator, 'paginate', return_value=mock_page_data):
            
            result = hh_api.get_vacancies("python", per_page=50)
            assert len(result) == 2
    
    def test_get_vacancies_no_results(self, hh_api):
        """Тест получения вакансий когда ничего не найдено"""
        mock_initial_data = {
            "found": 0,
            "pages": 0
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_initial_data):
            result = hh_api.get_vacancies("nonexistent")
            assert result == []
    
    def test_get_vacancies_keyboard_interrupt(self, hh_api):
        """Тест прерывания получения вакансий"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=KeyboardInterrupt):
            result = hh_api.get_vacancies("python")
            assert result == []
    
    def test_get_vacancies_with_deduplication(self, hh_api):
        """Тест получения вакансий с дедупликацией"""
        mock_data = [{"id": "1", "name": "Test"}]
        
        with patch.object(hh_api, 'get_vacancies', return_value=mock_data):
            result = hh_api.get_vacancies_with_deduplication("python")
            assert result == mock_data
    
    def test_get_vacancies_by_company(self, hh_api):
        """Тест получения вакансий конкретной компании"""
        mock_initial_data = {
            "found": 10,
            "pages": 1
        }
        
        mock_results = [{"name": "Test Job", "alternate_url": "test.com", "source": "hh.ru"}]
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_initial_data), \
             patch.object(hh_api._paginator, 'paginate', return_value=mock_results):
            
            result = hh_api.get_vacancies_by_company("123", "python")
            assert len(result) == 1
    
    def test_get_vacancies_by_company_no_results(self, hh_api):
        """Тест получения вакансий компании без результатов"""
        mock_initial_data = {
            "found": 0,
            "pages": 0
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_initial_data):
            result = hh_api.get_vacancies_by_company("123", "python")
            assert result == []
    
    def test_get_vacancies_from_target_companies(self, hh_api):
        """Тест получения вакансий от целевых компаний"""
        mock_target_ids = ["1", "2", "3"]
        mock_vacancies = [{"id": "job1", "name": "Test Job"}]
        
        with patch('src.api_modules.hh_api.TargetCompanies.get_hh_ids', return_value=mock_target_ids), \
             patch.object(hh_api, 'get_vacancies_by_company', return_value=mock_vacancies), \
             patch('src.utils.vacancy_stats.VacancyStats'):
            
            result = hh_api.get_vacancies_from_target_companies("python")
            assert len(result) == len(mock_target_ids)
    
    def test_get_vacancies_page_by_company(self, hh_api):
        """Тест получения страницы вакансий компании"""
        mock_data = {
            "items": [
                {
                    "name": "Company Job",
                    "alternate_url": "https://hh.ru/vacancy/1"
                }
            ]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=mock_data):
            result = hh_api.get_vacancies_page_by_company("123", "python", 0)
            
            assert len(result) == 1
            assert result[0]["source"] == "hh.ru"
    
    def test_clear_cache(self, hh_api):
        """Тест очистки кэша"""
        with patch('src.api_modules.cached_api.CachedAPI.clear_cache') as mock_clear:
            hh_api.clear_cache("hh")
            mock_clear.assert_called_once_with("hh")


@pytest.mark.skipif(not HH_API_AVAILABLE, reason="HH API modules not available")  
class TestHeadHunterAPIIntegration:
    """Интеграционные тесты HH API"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        with patch('src.api_modules.hh_api.APIConnector'), \
             patch('src.api_modules.hh_api.Paginator'), \
             patch('src.api_modules.hh_api.APIConfig'):
            
            api = HeadHunterAPI()
            assert isinstance(api, BaseJobAPI)
            assert hasattr(api, 'get_vacancies')
            assert hasattr(api, '_validate_vacancy')
