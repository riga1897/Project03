#!/usr/bin/env python3
"""
Тесты для модуля hh_api.py
"""

import logging
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.api_modules.hh_api import HeadHunterAPI
from src.config.api_config import APIConfig
from src.config.target_companies import TargetCompanies


class TestHeadHunterAPI:
    """Тесты для класса HeadHunterAPI"""
    
    @pytest.fixture
    def mock_api_config(self):
        """Создание мок-конфигурации API"""
        config = Mock(spec=APIConfig)
        
        # Мокаем hh_config
        mock_hh_config = Mock()
        mock_hh_config.get_params.return_value = {
            "text": "python",
            "page": 0,
            "per_page": 20
        }
        config.hh_config = mock_hh_config
        
        # Мокаем get_pagination_params
        config.get_pagination_params.return_value = {"max_pages": 5}
        
        return config
    
    @pytest.fixture
    def hh_api(self, mock_api_config):
        """Создание экземпляра HeadHunterAPI для тестов"""
        with patch('src.api_modules.hh_api.APIConnector'):
            with patch('src.api_modules.hh_api.Paginator'):
                api = HeadHunterAPI(mock_api_config)
                return api
    
    def test_hh_api_initialization(self, mock_api_config):
        """Тест инициализации HeadHunterAPI"""
        with patch('src.api_modules.hh_api.APIConnector') as mock_connector:
            with patch('src.api_modules.hh_api.Paginator') as mock_paginator:
                api = HeadHunterAPI(mock_api_config)
                
                assert api._config == mock_api_config
                assert api.BASE_URL == "https://api.hh.ru/vacancies"
                assert api.DEFAULT_CACHE_DIR == "data/cache/hh"
                assert api.REQUIRED_VACANCY_FIELDS == {"name", "alternate_url", "salary"}
                assert api.connector is not None
                assert api._paginator is not None
    
    def test_hh_api_inheritance(self, hh_api):
        """Тест наследования от базовых классов"""
        from src.api_modules.base_api import BaseJobAPI
        from src.api_modules.cached_api import CachedAPI
        
        assert isinstance(hh_api, BaseJobAPI)
        assert isinstance(hh_api, CachedAPI)
    
    def test_get_empty_response(self, hh_api):
        """Тест получения пустого ответа"""
        result = hh_api._get_empty_response()
        
        assert result == {"items": []}
        assert isinstance(result, dict)
        assert "items" in result
    
    def test_validate_vacancy_valid(self, hh_api):
        """Тест валидации валидной вакансии"""
        valid_vacancy = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {"from": 100000, "to": 150000}
        }
        
        result = hh_api._validate_vacancy(valid_vacancy)
        assert result is True
    
    def test_validate_vacancy_invalid_missing_name(self, hh_api):
        """Тест валидации вакансии без названия"""
        invalid_vacancy = {
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {"from": 100000}
        }
        
        result = hh_api._validate_vacancy(invalid_vacancy)
        assert result is False
    
    def test_validate_vacancy_invalid_missing_url(self, hh_api):
        """Тест валидации вакансии без URL"""
        invalid_vacancy = {
            "name": "Python Developer",
            "salary": {"from": 100000}
        }
        
        result = hh_api._validate_vacancy(invalid_vacancy)
        assert result is False
    
    def test_validate_vacancy_invalid_empty_name(self, hh_api):
        """Тест валидации вакансии с пустым названием"""
        invalid_vacancy = {
            "name": "",
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {"from": 100000}
        }
        
        result = hh_api._validate_vacancy(invalid_vacancy)
        assert result is False
    
    def test_validate_vacancy_invalid_empty_url(self, hh_api):
        """Тест валидации вакансии с пустым URL"""
        invalid_vacancy = {
            "name": "Python Developer",
            "alternate_url": "",
            "salary": {"from": 100000}
        }
        
        result = hh_api._validate_vacancy(invalid_vacancy)
        assert result is False
    
    def test_validate_vacancy_invalid_not_dict(self, hh_api):
        """Тест валидации невалидного типа вакансии"""
        invalid_vacancy = "not a dict"
        
        result = hh_api._validate_vacancy(invalid_vacancy)
        assert result is False
    
    def test_validate_vacancy_invalid_none_values(self, hh_api):
        """Тест валидации вакансии с None значениями"""
        invalid_vacancy = {
            "name": None,
            "alternate_url": None,
            "salary": {"from": 100000}
        }
        
        result = hh_api._validate_vacancy(invalid_vacancy)
        assert result is False
    
    @patch('src.api_modules.hh_api.logger')
    def test_connect_success(self, mock_logger, hh_api):
        """Тест успешного подключения к API"""
        test_params = {"text": "python"}
        test_data = {"items": [{"id": "1", "name": "Python Developer"}]}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            result = hh_api._HeadHunterAPI__connect("https://api.hh.ru/vacancies", test_params)
            
            assert result == test_data
            mock_logger.error.assert_not_called()
    
    @patch('src.api_modules.hh_api.logger')
    def test_connect_exception_handling(self, mock_logger, hh_api):
        """Тест обработки исключений при подключении"""
        test_params = {"text": "python"}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=Exception("Connection error")):
            result = hh_api._HeadHunterAPI__connect("https://api.hh.ru/vacancies", test_params)
            
            assert result == {}
            mock_logger.error.assert_called_once_with("Ошибка при подключении к API: Connection error")
    
    def test_connect_with_none_params(self, hh_api):
        """Тест подключения с None параметрами"""
        test_data = {"items": []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            result = hh_api._HeadHunterAPI__connect("https://api.hh.ru/vacancies", None)
            
            assert result == test_data
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_page_success(self, mock_logger, hh_api, mock_api_config):
        """Тест успешного получения страницы вакансий"""
        test_data = {
            "items": [
                {
                    "id": "1",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/1"
                },
                {
                    "id": "2",
                    "name": "Java Developer",
                    "alternate_url": "https://hh.ru/vacancy/2"
                }
            ]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            result = hh_api.get_vacancies_page("Python", 0)
            
            assert len(result) == 2
            assert all(item["source"] == "hh.ru" for item in result)
            assert all(hh_api._validate_vacancy(item) for item in result)
            mock_logger.error.assert_not_called()
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_page_exception_handling(self, mock_logger, hh_api):
        """Тест обработки исключений при получении страницы"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=Exception("API error")):
            result = hh_api.get_vacancies_page("Python", 0)
            
            assert result == []
            mock_logger.error.assert_called_once_with("Failed to get vacancies page 0: API error")
    
    def test_get_vacancies_page_lowercase_query(self, hh_api, mock_api_config):
        """Тест приведения поискового запроса к нижнему регистру"""
        test_data = {"items": []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            hh_api.get_vacancies_page("Python Developer", 0)
            
            # Проверяем, что запрос был приведен к нижнему регистру
            mock_api_config.hh_config.get_params.assert_called_once()
            call_args = mock_api_config.hh_config.get_params.call_args
            assert call_args[1]["text"] == "python developer"
    
    def test_get_vacancies_page_none_query(self, hh_api, mock_api_config):
        """Тест обработки None поискового запроса"""
        test_data = {"items": []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            hh_api.get_vacancies_page(None, 0)
            
            # Проверяем, что None запрос обработан корректно
            mock_api_config.hh_config.get_params.assert_called_once()
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_success(self, mock_logger, hh_api, mock_api_config):
        """Тест успешного получения вакансий"""
        # Мокаем начальные данные
        initial_data = {"found": 50, "pages": 3}
        page_data = {"items": [{"id": "1", "name": "Python", "alternate_url": "https://hh.ru/1"}]}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=[initial_data, page_data]):
            with patch.object(hh_api, 'get_vacancies_page', return_value=page_data["items"]):
                with patch.object(hh_api, '_paginator') as mock_paginator:
                    mock_paginator.paginate.return_value = page_data["items"] * 3
                    
                    result = hh_api.get_vacancies("Python", per_page=20)
                    
                    assert len(result) == 3
                    mock_logger.info.assert_called()
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_no_results(self, mock_logger, hh_api, mock_api_config):
        """Тест получения вакансий без результатов"""
        initial_data = {"found": 0, "pages": 0}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=initial_data):
            result = hh_api.get_vacancies("Python")
            
            assert result == []
            mock_logger.warning.assert_called_with("Вакансии по запросу 'Python' не найдены")
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_keyboard_interrupt(self, mock_logger, hh_api, mock_api_config):
        """Тест обработки KeyboardInterrupt"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=KeyboardInterrupt()):
            with patch('builtins.print') as mock_print:
                result = hh_api.get_vacancies("Python")
                
                assert result == []
                mock_logger.info.assert_called_with("Получение вакансий прервано пользователем")
                mock_print.assert_called_with("\nПолучение вакансий остановлено.")
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_exception_handling(self, mock_logger, hh_api, mock_api_config):
        """Тест обработки исключений при получении вакансий"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=Exception("API error")):
            result = hh_api.get_vacancies("Python")
            
            assert result == []
            mock_logger.error.assert_called_with("Ошибка получения вакансий: API error")
    
    def test_get_vacancies_with_deduplication(self, hh_api):
        """Тест получения вакансий с дедупликацией"""
        with patch.object(hh_api, 'get_vacancies', return_value=[{"id": "1"}]):
            result = hh_api.get_vacancies_with_deduplication("Python")
            
            assert result == [{"id": "1"}]
    
    @patch('src.api_modules.hh_api.logger')
    @patch('src.api_modules.hh_api.TargetCompanies')
    def test_get_vacancies_from_target_companies(self, mock_target_companies, mock_logger, hh_api):
        """Тест получения вакансий от целевых компаний"""
        mock_target_companies.get_hh_ids.return_value = ["company1", "company2"]
        
        with patch.object(hh_api, 'get_vacancies_by_company', side_effect=[[{"id": "1"}], [{"id": "2"}]]):
            with patch('src.api_modules.hh_api.VacancyStats') as mock_stats_class:
                mock_stats = Mock()
                mock_stats_class.return_value = mock_stats
                
                result = hh_api.get_vacancies_from_target_companies("Python")
                
                assert len(result) == 2
                mock_logger.info.assert_called()
                mock_stats.display_company_stats.assert_called_once()
    
    @patch('src.api_modules.hh_api.logger')
    @patch('src.api_modules.hh_api.TargetCompanies')
    def test_get_vacancies_from_target_companies_empty(self, mock_target_companies, mock_logger, hh_api):
        """Тест получения вакансий от целевых компаний без результатов"""
        mock_target_companies.get_hh_ids.return_value = ["company1"]
        
        with patch.object(hh_api, 'get_vacancies_by_company', return_value=[]):
            result = hh_api.get_vacancies_from_target_companies("Python")
            
            assert result == []
            mock_logger.warning.assert_called_with("Получен пустой список вакансий от целевых компаний")
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_by_company_success(self, mock_logger, hh_api, mock_api_config):
        """Тест успешного получения вакансий компании"""
        initial_data = {"found": 25, "pages": 2}
        page_data = {"items": [{"id": "1", "name": "Python", "alternate_url": "https://hh.ru/1"}]}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=[initial_data, page_data]):
            with patch.object(hh_api, 'get_vacancies_page_by_company', return_value=page_data["items"]):
                with patch.object(hh_api, '_paginator') as mock_paginator:
                    mock_paginator.paginate.return_value = page_data["items"] * 2
                    
                    result = hh_api.get_vacancies_by_company("company123", "Python")
                    
                    assert len(result) == 2
                    mock_logger.debug.assert_called()
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_by_company_no_results(self, mock_logger, hh_api, mock_api_config):
        """Тест получения вакансий компании без результатов"""
        initial_data = {"found": 0, "pages": 0}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=initial_data):
            result = hh_api.get_vacancies_by_company("company123", "Python")
            
            assert result == []
            mock_logger.debug.assert_called_with("Компания company123: вакансий не найдено")
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_by_company_exception_handling(self, mock_logger, hh_api):
        """Тест обработки исключений при получении вакансий компании"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=Exception("Company API error")):
            result = hh_api.get_vacancies_by_company("company123", "Python")
            
            assert result == []
            mock_logger.error.assert_called_with("Ошибка получения вакансий компании company123: Company API error")
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_page_by_company_success(self, mock_logger, hh_api, mock_api_config):
        """Тест успешного получения страницы вакансий компании"""
        test_data = {
            "items": [
                {
                    "id": "1",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/1"
                }
            ]
        }
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            result = hh_api.get_vacancies_page_by_company("company123", "Python", 0)
            
            assert len(result) == 1
            assert all(item["source"] == "hh.ru" for item in result)
            assert all(hh_api._validate_vacancy(item) for item in result)
            mock_logger.error.assert_not_called()
    
    @patch('src.api_modules.hh_api.logger')
    def test_get_vacancies_page_by_company_exception_handling(self, mock_logger, hh_api):
        """Тест обработки исключений при получении страницы вакансий компании"""
        with patch.object(hh_api, '_CachedAPI__connect_to_api', side_effect=Exception("Page API error")):
            result = hh_api.get_vacancies_page_by_company("company123", "Python", 0)
            
            assert result == []
            mock_logger.error.assert_called_with("Ошибка получения страницы 0 для компании company123: Page API error")
    
    def test_get_vacancies_page_by_company_lowercase_query(self, hh_api, mock_api_config):
        """Тест приведения поискового запроса к нижнему регистру для компании"""
        test_data = {"items": []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            hh_api.get_vacancies_page_by_company("company123", "Python Developer", 0)
            
            # Проверяем, что запрос был приведен к нижнему регистру
            mock_api_config.hh_config.get_params.assert_called_once()
            call_args = mock_api_config.hh_config.get_params.call_args
            assert call_args[1]["text"] == "python developer"
    
    def test_get_vacancies_page_by_company_none_query(self, hh_api, mock_api_config):
        """Тест обработки None поискового запроса для компании"""
        test_data = {"items": []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            hh_api.get_vacancies_page_by_company("company123", None, 0)
            
            # Проверяем, что None запрос обработан корректно
            mock_api_config.hh_config.get_params.assert_called_once()
    
    def test_clear_cache(self, hh_api):
        """Тест очистки кэша"""
        with patch.object(hh_api, 'super') as mock_super:
            mock_super_instance = Mock()
            mock_super.return_value = mock_super_instance
            
            hh_api.clear_cache("test")
            
            mock_super_instance.clear_cache.assert_called_once_with("hh")
    
    def test_pagination_calculation_single_page(self, hh_api, mock_api_config):
        """Тест расчета пагинации для одной страницы"""
        initial_data = {"found": 15, "pages": 1}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=initial_data):
            with patch.object(hh_api, 'get_vacancies_page', return_value=[{"id": "1"}]):
                with patch.object(hh_api, '_paginator') as mock_paginator:
                    mock_paginator.paginate.return_value = [{"id": "1"}] * 15
                    
                    result = hh_api.get_vacancies("Python", per_page=20)
                    
                    assert len(result) == 15
    
    def test_pagination_calculation_multiple_pages(self, hh_api, mock_api_config):
        """Тест расчета пагинации для нескольких страниц"""
        initial_data = {"found": 150, "pages": 8}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=initial_data):
            with patch.object(hh_api, 'get_vacancies_page', return_value=[{"id": "1"}]):
                with patch.object(hh_api, '_paginator') as mock_paginator:
                    mock_paginator.paginate.return_value = [{"id": "1"}] * 100
                    
                    result = hh_api.get_vacancies("Python", per_page=20)
                    
                    assert len(result) == 100
    
    def test_employer_id_filter_addition(self, hh_api, mock_api_config):
        """Тест добавления фильтра по ID работодателя"""
        test_data = {"items": []}
        
        with patch.object(hh_api, '_CachedAPI__connect_to_api', return_value=test_data):
            hh_api.get_vacancies_by_company("company123", "Python")
            
            # Проверяем, что employer_id был добавлен в kwargs
            mock_api_config.hh_config.get_params.assert_called()
            call_args = mock_api_config.hh_config.get_params.call_args
            assert "employer_id" in call_args[1]
            assert call_args[1]["employer_id"] == "company123"
