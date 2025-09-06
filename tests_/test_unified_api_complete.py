
"""
Полные тесты для UnifiedAPI
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.api_modules.unified_api import UnifiedAPI
    from src.vacancies.models import Vacancy
    UNIFIED_API_AVAILABLE = True
except ImportError:
    UNIFIED_API_AVAILABLE = False
    UnifiedAPI = object
    Vacancy = object


@pytest.mark.skipif(not UNIFIED_API_AVAILABLE, reason="UnifiedAPI modules not available")
class TestUnifiedAPIComplete:
    """Полное тестирование UnifiedAPI"""
    
    @pytest.fixture
    def unified_api(self):
        """Экземпляр UnifiedAPI с мокированными зависимостями"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh, \
             patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj, \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            api.hh_api = mock_hh.return_value
            api.sj_api = mock_sj.return_value
            return api
    
    def test_init(self):
        """Тест инициализации"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            assert hasattr(api, 'hh_api')
            assert hasattr(api, 'sj_api')
            assert hasattr(api, 'parser')
            assert hasattr(api, 'apis')
    
    def test_get_vacancies_from_sources_hh_only(self, unified_api):
        """Тест получения вакансий только с HH"""
        mock_hh_data = [
            {"id": "1", "name": "HH Job", "source": "hh"}
        ]
        
        unified_api.hh_api.get_vacancies.return_value = mock_hh_data
        
        with patch.object(unified_api, '_filter_by_target_companies', return_value=mock_hh_data):
            result = unified_api.get_vacancies_from_sources("python", sources=["hh"])
            assert len(result) == 1
            unified_api.hh_api.get_vacancies.assert_called_once()
    
    def test_get_vacancies_from_sources_sj_only(self, unified_api):
        """Тест получения вакансий только с SJ"""
        mock_sj_data = [
            {"id": "2", "profession": "SJ Job", "source": "sj"}
        ]
        
        unified_api.sj_api.get_vacancies.return_value = mock_sj_data
        
        with patch.object(unified_api, '_filter_by_target_companies', return_value=mock_sj_data):
            result = unified_api.get_vacancies_from_sources("python", sources=["sj"])
            assert len(result) == 1
            unified_api.sj_api.get_vacancies.assert_called_once()
    
    def test_get_vacancies_from_sources_all(self, unified_api):
        """Тест получения вакансий из всех источников"""
        mock_hh_data = [{"id": "1", "name": "HH Job", "source": "hh"}]
        mock_sj_data = [{"id": "2", "profession": "SJ Job", "source": "sj"}]
        
        unified_api.hh_api.get_vacancies.return_value = mock_hh_data
        unified_api.sj_api.get_vacancies.return_value = mock_sj_data
        
        combined_data = mock_hh_data + mock_sj_data
        
        with patch.object(unified_api, '_filter_by_target_companies', return_value=combined_data):
            result = unified_api.get_vacancies_from_sources("python", sources=["hh", "sj"])
            assert len(result) == 2
    
    def test_get_vacancies_from_sources_no_results(self, unified_api):
        """Тест когда вакансии не найдены"""
        unified_api.hh_api.get_vacancies.return_value = []
        unified_api.sj_api.get_vacancies.return_value = []
        
        result = unified_api.get_vacancies_from_sources("nonexistent")
        assert result == []
    
    def test_get_vacancies_from_sources_with_errors(self, unified_api):
        """Тест обработки ошибок при получении вакансий"""
        unified_api.hh_api.get_vacancies.side_effect = Exception("HH API Error")
        unified_api.sj_api.get_vacancies.return_value = [{"id": "1", "source": "sj"}]
        
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}]):
            result = unified_api.get_vacancies_from_sources("python")
            assert len(result) == 1
    
    def test_filter_by_target_companies(self, unified_api):
        """Тест фильтрации по целевым компаниям"""
        mock_vacancies = [
            {
                "id": "1",
                "employer": {"id": "123"},
                "source": "hh"
            },
            {
                "id": "2", 
                "employer": {"id": "999"},  # не в целевых
                "source": "hh"
            },
            {
                "id": "3",
                "id_client": "456",  # SJ формат
                "source": "sj"
            }
        ]
        
        mock_companies = [
            Mock(hh_id=123, sj_id=None),
            Mock(hh_id=None, sj_id=456)
        ]
        
        with patch('src.api_modules.unified_api.TargetCompanies.get_all_companies', return_value=mock_companies):
            result = unified_api._filter_by_target_companies(mock_vacancies)
            assert len(result) == 2  # только от целевых компаний
    
    def test_filter_by_target_companies_empty(self, unified_api):
        """Тест фильтрации пустого списка"""
        result = unified_api._filter_by_target_companies([])
        assert result == []
    
    def test_get_hh_vacancies(self, unified_api):
        """Тест получения вакансий только с HH"""
        mock_data = [{"id": "1", "name": "Test"}]
        unified_api.hh_api.get_vacancies_with_deduplication.return_value = mock_data
        
        with patch('src.vacancies.models.Vacancy.from_dict') as mock_from_dict:
            mock_from_dict.return_value = Mock()
            result = unified_api.get_hh_vacancies("python")
            assert len(result) == 1
    
    def test_get_hh_vacancies_error(self, unified_api):
        """Тест обработки ошибок при получении вакансий HH"""
        unified_api.hh_api.get_vacancies_with_deduplication.side_effect = Exception("HH Error")
        
        result = unified_api.get_hh_vacancies("python")
        assert result == []
    
    def test_get_sj_vacancies_success(self, unified_api):
        """Тест успешного получения вакансий SJ"""
        mock_data = [{"id": "1", "profession": "Test"}]
        mock_parsed = [Mock()]
        
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = mock_data
        unified_api.parser.parse_vacancies.return_value = mock_parsed
        unified_api.parser.convert_to_unified_format.return_value = {"id": "1"}
        
        with patch('src.vacancies.models.Vacancy.from_dict') as mock_from_dict, \
             patch('builtins.print'):
            mock_from_dict.return_value = Mock()
            result = unified_api.get_sj_vacancies("python")
            assert len(result) == 1
    
    def test_get_sj_vacancies_no_data(self, unified_api):
        """Тест получения вакансий SJ когда данных нет"""
        unified_api.sj_api.get_vacancies_with_deduplication.return_value = []
        
        result = unified_api.get_sj_vacancies("python")
        assert result == []
    
    def test_get_sj_vacancies_error(self, unified_api):
        """Тест обработки ошибок при получении вакансий SJ"""
        unified_api.sj_api.get_vacancies_with_deduplication.side_effect = Exception("SJ Error")
        
        result = unified_api.get_sj_vacancies("python")
        assert result == []
    
    def test_clear_cache(self, unified_api):
        """Тест очистки кэша"""
        sources = {"hh": True, "sj": False}
        
        with patch('glob.glob', return_value=["cache1.json", "cache2.json"]), \
             patch('os.remove'), \
             patch('builtins.print'):
            
            unified_api.clear_cache(sources)
            unified_api.hh_api.clear_cache.assert_called_once_with("hh")
    
    def test_clear_cache_with_errors(self, unified_api):
        """Тест очистки кэша с ошибками"""
        sources = {"hh": True}
        
        unified_api.hh_api.clear_cache.side_effect = Exception("Cache error")
        
        with patch('builtins.print'):
            with pytest.raises(Exception):
                unified_api.clear_cache(sources)
    
    def test_get_vacancies_from_target_companies_default_sources(self, unified_api):
        """Тест получения вакансий от целевых компаний с источниками по умолчанию"""
        unified_api.hh_api.get_vacancies_from_target_companies.return_value = [{"id": "1"}]
        unified_api.sj_api.get_vacancies_from_target_companies.return_value = [{"id": "2"}]
        
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}, {"id": "2"}]):
            result = unified_api.get_vacancies_from_target_companies("python")
            assert len(result) == 2
    
    def test_get_vacancies_from_target_companies_specific_sources(self, unified_api):
        """Тест получения вакансий от целевых компаний с указанными источниками"""
        unified_api.hh_api.get_vacancies_from_target_companies.return_value = [{"id": "1"}]
        
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}]):
            result = unified_api.get_vacancies_from_target_companies("python", sources=["hh"])
            assert len(result) == 1
            unified_api.sj_api.get_vacancies_from_target_companies.assert_not_called()
    
    def test_clear_all_cache(self, unified_api):
        """Тест очистки всего кэша"""
        unified_api.clear_all_cache()
        unified_api.hh_api.clear_cache.assert_called_once_with("hh")
        unified_api.sj_api.clear_cache.assert_called_once_with("sj")
    
    def test_clear_all_cache_with_errors(self, unified_api):
        """Тест очистки всего кэша с ошибками"""
        unified_api.hh_api.clear_cache.side_effect = Exception("HH Cache error")
        unified_api.sj_api.clear_cache.side_effect = Exception("SJ Cache error")
        
        # Не должно падать, только логировать ошибки
        unified_api.clear_all_cache()
    
    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        sources = UnifiedAPI.get_available_sources()
        assert "hh" in sources
        assert "sj" in sources
    
    def test_validate_sources_valid(self, unified_api):
        """Тест валидации корректных источников"""
        sources = ["hh", "sj"]
        result = unified_api.validate_sources(sources)
        assert result == sources
    
    def test_validate_sources_invalid(self, unified_api):
        """Тест валидации некорректных источников"""
        sources = ["invalid", "unknown"]
        result = unified_api.validate_sources(sources)
        assert result == ["hh", "sj"]  # возвращает все доступные
    
    def test_validate_sources_mixed(self, unified_api):
        """Тест валидации смешанных источников"""
        sources = ["hh", "invalid", "sj"]
        result = unified_api.validate_sources(sources)
        assert result == ["hh", "sj"]
    
    def test_get_all_vacancies(self, unified_api):
        """Тест получения всех вакансий"""
        mock_data = [{"id": "1"}]
        
        with patch.object(unified_api, 'get_vacancies_from_sources', return_value=mock_data) as mock_get:
            result = unified_api.get_all_vacancies("python", test_param="value")
            assert result == mock_data
            mock_get.assert_called_once_with("python", sources=["hh", "sj"], test_param="value")
    
    def test_get_vacancies_from_source_hh(self, unified_api):
        """Тест получения вакансий из конкретного источника HH"""
        mock_data = [{"id": "1"}]
        unified_api.hh_api.get_vacancies.return_value = mock_data
        
        result = unified_api.get_vacancies_from_source("python", "hh")
        assert result == mock_data
        unified_api.hh_api.get_vacancies.assert_called_once()
    
    def test_get_vacancies_from_source_sj(self, unified_api):
        """Тест получения вакансий из конкретного источника SJ"""
        mock_data = [{"id": "1"}]
        unified_api.sj_api.get_vacancies.return_value = mock_data
        
        result = unified_api.get_vacancies_from_source("python", "sj")
        assert result == mock_data
        unified_api.sj_api.get_vacancies.assert_called_once()
    
    def test_get_vacancies_from_source_invalid(self, unified_api):
        """Тест получения вакансий из неизвестного источника"""
        result = unified_api.get_vacancies_from_source("python", "unknown")
        assert result == []
    
    def test_get_vacancies_from_source_error(self, unified_api):
        """Тест обработки ошибок при получении вакансий из источника"""
        unified_api.hh_api.get_vacancies.side_effect = Exception("API Error")
        
        result = unified_api.get_vacancies_from_source("python", "hh")
        assert result == []


@pytest.mark.skipif(not UNIFIED_API_AVAILABLE, reason="UnifiedAPI modules not available")  
class TestUnifiedAPIIntegration:
    """Интеграционные тесты UnifiedAPI"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            
            api = UnifiedAPI()
            assert hasattr(api, 'get_vacancies_from_sources')
            assert hasattr(api, 'get_all_vacancies')
            assert hasattr(api, 'clear_all_cache')
