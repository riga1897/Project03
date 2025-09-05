
"""
Полные тесты для SuperJob API
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.sj_api import SuperJobAPI
    from src.api_modules.base_api import BaseJobAPI
    from src.config.sj_api_config import SJAPIConfig
    SJ_API_AVAILABLE = True
except ImportError:
    SJ_API_AVAILABLE = False
    SuperJobAPI = object
    BaseJobAPI = object
    SJAPIConfig = object


@pytest.mark.skipif(not SJ_API_AVAILABLE, reason="SJ API modules not available")
class TestSuperJobAPIComplete:
    """Полное тестирование SuperJob API"""
    
    @pytest.fixture
    def mock_sj_config(self):
        """Мок конфигурации SJ"""
        config = Mock()
        config.get_params.return_value = {
            "keyword": "python",
            "count": 100,
            "page": 0
        }
        return config
    
    @pytest.fixture
    def sj_api(self, mock_sj_config):
        """Экземпляр SJ API с мокированной конфигурацией"""
        with patch('src.api_modules.sj_api.APIConnector'), \
             patch('src.api_modules.sj_api.Paginator'), \
             patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="test_key"):
            api = SuperJobAPI(mock_sj_config)
            api.connector = Mock()
            api._paginator = Mock()
            return api
    
    def test_init_with_config(self, mock_sj_config):
        """Тест инициализации с конфигурацией"""
        with patch('src.api_modules.sj_api.APIConnector'), \
             patch('src.api_modules.sj_api.Paginator'), \
             patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="test_key"):
            api = SuperJobAPI(mock_sj_config)
            assert api.config == mock_sj_config
    
    def test_init_without_config(self):
        """Тест инициализации без конфигурации"""
        with patch('src.api_modules.sj_api.APIConnector'), \
             patch('src.api_modules.sj_api.Paginator'), \
             patch('src.api_modules.sj_api.SJAPIConfig') as mock_sj_config, \
             patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="test_key"):
            api = SuperJobAPI()
            mock_sj_config.assert_called_once()
    
    def test_get_empty_response(self, sj_api):
        """Тест получения пустого ответа"""
        result = sj_api._get_empty_response()
        assert result == {"objects": []}
    
    def test_validate_vacancy_valid(self, sj_api):
        """Тест валидации корректной вакансии"""
        vacancy = {
            "profession": "Python Developer",
            "link": "https://superjob.ru/vacancy/12345"
        }
        assert sj_api._validate_vacancy(vacancy) is True
    
    def test_validate_vacancy_invalid(self, sj_api):
        """Тест валидации некорректной вакансии"""
        # Пустая профессия
        vacancy1 = {
            "profession": "",
            "link": "https://superjob.ru/vacancy/12345"
        }
        assert sj_api._validate_vacancy(vacancy1) is False
        
        # Нет ссылки
        vacancy2 = {
            "profession": "Python Developer",
            "link": ""
        }
        assert sj_api._validate_vacancy(vacancy2) is False
        
        # Не словарь
        assert sj_api._validate_vacancy("not a dict") is False
    
    def test_get_vacancies_page_success(self, sj_api):
        """Тест успешного получения страницы вакансий"""
        mock_data = {
            "objects": [
                {
                    "profession": "Python Developer",
                    "link": "https://superjob.ru/vacancy/1"
                }
            ]
        }
        
        with patch.object(sj_api, '_CachedAPI__connect_to_api', return_value=mock_data):
            result = sj_api.get_vacancies_page("python", page=0)
            
            assert len(result) == 1
            assert result[0]["source"] == "superjob.ru"
    
    def test_get_vacancies_page_error(self, sj_api):
        """Тест обработки ошибок при получении страницы"""
        with patch.object(sj_api, '_CachedAPI__connect_to_api', side_effect=Exception("API Error")):
            result = sj_api.get_vacancies_page("python", page=0)
            assert result == []
    
    def test_get_vacancies_success(self, sj_api):
        """Тест успешного получения вакансий"""
        mock_initial_data = {
            "total": 100
        }
        
        mock_page_data = [
            {"profession": "Python Dev 1", "link": "https://sj.ru/1", "source": "superjob.ru"},
            {"profession": "Python Dev 2", "link": "https://sj.ru/2", "source": "superjob.ru"}
        ]
        
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="real_key"), \
             patch.object(sj_api, '_CachedAPI__connect_to_api', return_value=mock_initial_data), \
             patch.object(sj_api._paginator, 'paginate', return_value=mock_page_data):
            
            result = sj_api.get_vacancies("python")
            assert len(result) == 2
    
    def test_get_vacancies_no_api_key(self, sj_api):
        """Тест получения вакансий без API ключа"""
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value=""):
            result = sj_api.get_vacancies("python")
            assert result == []
    
    def test_get_vacancies_test_key(self, sj_api):
        """Тест получения вакансий с тестовым ключом"""
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="v3.r.137440105.example.test_tool"):
            result = sj_api.get_vacancies("python")
            assert result == []
    
    def test_get_vacancies_no_results(self, sj_api):
        """Тест получения вакансий когда ничего не найдено"""
        mock_initial_data = {
            "total": 0
        }
        
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="real_key"), \
             patch.object(sj_api, '_CachedAPI__connect_to_api', return_value=mock_initial_data):
            result = sj_api.get_vacancies("nonexistent")
            assert result == []
    
    def test_get_vacancies_keyboard_interrupt(self, sj_api):
        """Тест прерывания получения вакансий"""
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="real_key"), \
             patch.object(sj_api, '_CachedAPI__connect_to_api', side_effect=KeyboardInterrupt):
            result = sj_api.get_vacancies("python")
            assert result == []
    
    def test_get_vacancies_with_deduplication(self, sj_api):
        """Тест получения вакансий с дедупликацией"""
        mock_data = [{"id": "1", "profession": "Test"}]
        
        with patch.object(sj_api, 'get_vacancies', return_value=mock_data), \
             patch.object(sj_api, '_deduplicate_vacancies', return_value=mock_data):
            result = sj_api.get_vacancies_with_deduplication("python")
            assert result == mock_data
    
    def test_deduplicate_vacancies(self, sj_api):
        """Тест дедупликации вакансий"""
        mock_vacancies = [
            {"id": "1", "profession": "Test 1"},
            {"id": "2", "profession": "Test 2"}
        ]
        
        with patch('src.api_modules.cached_api.CachedAPI._deduplicate_vacancies', return_value=mock_vacancies):
            result = sj_api._deduplicate_vacancies(mock_vacancies)
            assert len(result) == 2
    
    def test_get_vacancies_from_target_companies_no_key(self, sj_api):
        """Тест получения вакансий от целевых компаний без ключа"""
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value=""):
            result = sj_api.get_vacancies_from_target_companies("python")
            assert result == []
    
    def test_get_vacancies_from_target_companies_success(self, sj_api):
        """Тест успешного получения вакансий от целевых компаний"""
        mock_all_vacancies = [
            {"id_client": "123", "profession": "Test Job 1"},
            {"id_client": "456", "profession": "Test Job 2"},
            {"id_client": "999", "profession": "Test Job 3"}  # не в целевых
        ]
        
        mock_target_ids = ["123", "456"]
        
        with patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="real_key"), \
             patch.object(sj_api, 'get_vacancies', return_value=mock_all_vacancies), \
             patch('src.api_modules.sj_api.TargetCompanies.get_sj_ids', return_value=mock_target_ids), \
             patch('src.utils.vacancy_stats.VacancyStats.display_company_stats'):
            
            result = sj_api.get_vacancies_from_target_companies("python")
            assert len(result) == 2  # только от целевых компаний
    
    def test_clear_cache(self, sj_api):
        """Тест очистки кэша"""
        with patch('src.api_modules.cached_api.CachedAPI.clear_cache') as mock_clear:
            sj_api.clear_cache("sj")
            mock_clear.assert_called_once_with("sj")


@pytest.mark.skipif(not SJ_API_AVAILABLE, reason="SJ API modules not available")  
class TestSuperJobAPIIntegration:
    """Интеграционные тесты SuperJob API"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        with patch('src.api_modules.sj_api.APIConnector'), \
             patch('src.api_modules.sj_api.Paginator'), \
             patch('src.api_modules.sj_api.SJAPIConfig'), \
             patch('src.api_modules.sj_api.EnvLoader.get_env_var', return_value="test_key"):
            
            api = SuperJobAPI()
            assert isinstance(api, BaseJobAPI)
            assert hasattr(api, 'get_vacancies')
            assert hasattr(api, '_validate_vacancy')
