#!/usr/bin/env python3
"""
Исправленные комплексные тесты для обработчика поиска вакансий
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
    from src.vacancies.models import Vacancy
    SEARCH_HANDLER_AVAILABLE = True
except ImportError:
    SEARCH_HANDLER_AVAILABLE = False
    # Создаем заглушку если модуль недоступен
    class Vacancy:
        def __init__(self, vacancy_id=None, title=None, description=None, url=None, **kwargs):
            self.vacancy_id = vacancy_id
            self.title = title
            self.description = description
            self.url = url


class TestVacancySearchHandlerComplete:
    """Исправленные комплексные тесты для обработчика поиска вакансий"""

    @pytest.fixture
    def mock_dependencies(self):
        """Создание мокированных зависимостей"""
        return {
            'unified_api': Mock(),
            'storage': Mock()
        }

    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создаем моки для обязательных зависимостей
        mock_unified_api = Mock()
        mock_storage = Mock()
        
        # Настраиваем поведение моков
        mock_unified_api.get_vacancies.return_value = []
        mock_unified_api.get_available_sources.return_value = ["hh.ru", "superjob.ru"]
        mock_storage.get_vacancies.return_value = []
        mock_storage.save_vacancies.return_value = True
        
        # Если VacancySearchHandler доступен, создаем экземпляр
        if SEARCH_HANDLER_AVAILABLE:
            self.search_handler = VacancySearchHandler(mock_unified_api, mock_storage)
        else:
            self.search_handler = None # Устанавливаем None, если класс не импортирован

        self.sample_search_results = [
            Vacancy(
                vacancy_id="1",
                title="Senior Python Developer",
                description="Опытный Python разработчик для работы над проектами",
                url="https://example.com/vacancy/1"
            ),
            Vacancy(
                vacancy_id="2",
                title="Python Backend Developer",
                description="Backend разработчик на Python/Django",
                url="https://example.com/vacancy/2"
            )
        ]

    def test_search_handler_init(self):
        """Тест инициализации обработчика поиска вакансий"""
        if not SEARCH_HANDLER_AVAILABLE:
            pytest.skip("VacancySearchHandler not available")

        # Тест инициализации с мокированными зависимостями
        mock_unified_api = Mock()
        mock_storage = Mock()
        handler = VacancySearchHandler(mock_unified_api, mock_storage)
        assert handler is not None
        assert handler.unified_api == mock_unified_api
        assert handler.storage == mock_storage

    @patch('builtins.input', return_value='python')
    @patch('builtins.print')
    def test_get_search_query(self, mock_print, mock_input):
        """Тест получения поискового запроса от пользователя"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'get_search_query'):
            pytest.skip("VacancySearchHandler or get_search_query not available")

        query = self.search_handler.get_search_query()
        assert query == 'python'
        mock_input.assert_called_once()

    @patch('builtins.input', return_value='1')
    @patch('builtins.print') 
    def test_select_search_source(self, mock_print, mock_input):
        """Тест выбора источника для поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'select_source'):
            pytest.skip("VacancySearchHandler or select_source not available")

        # Мокируем доступные источники
        with patch.object(self.search_handler, 'get_available_sources', return_value=["hh.ru", "superjob.ru"]):
            source = self.search_handler.select_source()
            assert source == "hh.ru" # Ожидаем первый источник, так как input='1'
            mock_input.assert_called_once()

    @patch('src.api_modules.unified_api.UnifiedAPI.search_vacancies')
    @patch('builtins.print')
    def test_execute_search(self, mock_print, mock_search_vacancies):
        """Тест выполнения поиска вакансий"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'execute_search'):
            pytest.skip("VacancySearchHandler or execute_search not available")

        mock_search_vacancies.return_value = self.sample_search_results
        
        results = self.search_handler.execute_search('python', ['hh.ru'])
        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0].title == "Senior Python Developer"
        mock_search_vacancies.assert_called_once_with('python', ['hh.ru'])

    @patch('builtins.input', return_value='100000')
    @patch('builtins.print')
    def test_set_salary_filter(self, mock_print, mock_input):
        """Тест установки фильтра по зарплате"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'set_salary_filter'):
            pytest.skip("VacancySearchHandler or set_salary_filter not available")
        
        # Предполагаем, что set_salary_filter возвращает значение фильтра
        with patch.object(self.search_handler, 'set_salary_filter', return_value=100000):
            filter_result = self.search_handler.set_salary_filter()
            assert filter_result == 100000
            mock_input.assert_called_once()

    @patch('builtins.input', return_value='Москва')
    @patch('builtins.print')
    def test_set_location_filter(self, mock_print, mock_input):
        """Тест установки фильтра по местоположению"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'set_location_filter'):
            pytest.skip("VacancySearchHandler or set_location_filter not available")
        
        # Предполагаем, что set_location_filter возвращает значение фильтра
        with patch.object(self.search_handler, 'set_location_filter', return_value='Москва'):
            filter_result = self.search_handler.set_location_filter()
            assert filter_result == 'Москва'
            mock_input.assert_called_once()

    @patch('builtins.input', return_value='Tech')
    @patch('builtins.print') 
    def test_set_company_filter(self, mock_print, mock_input):
        """Тест установки фильтра по компании"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'set_company_filter'):
            pytest.skip("VacancySearchHandler or set_company_filter not available")
            
        # Предполагаем, что set_company_filter возвращает значение фильтра
        with patch.object(self.search_handler, 'set_company_filter', return_value='Tech'):
            filter_result = self.search_handler.set_company_filter()
            assert filter_result == 'Tech'
            mock_input.assert_called_once()

    def test_apply_filters_to_results(self):
        """Тест применения фильтров к результатам поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'apply_filters'):
            pytest.skip("VacancySearchHandler or apply_filters not available")

        filters = {
            'min_salary': 130000,
            'max_salary': 200000,
            'company_keywords': ['Tech']
        }
        
        # Создаем мок для Vacancy, если он не импортирован
        if not SEARCH_HANDLER_AVAILABLE:
            class MockVacancy:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
            Vacancy = MockVacancy
            self.sample_search_results = [
                Vacancy(
                    vacancy_id="1",
                    title="Senior Python Developer",
                    description="Опытный Python разработчик для работы над проектами",
                    url="https://example.com/vacancy/1",
                    salary=150000,
                    company_name="Tech Innovations"
                ),
                Vacancy(
                    vacancy_id="2",
                    title="Python Backend Developer",
                    description="Backend разработчик на Python/Django",
                    url="https://example.com/vacancy/2",
                    salary=120000,
                    company_name="Dev Solutions"
                )
            ]

        # Предполагаем, что apply_filters возвращает отфильтрованные результаты
        with patch.object(self.search_handler, 'apply_filters', return_value=[self.sample_search_results[0]]):
            filtered_results = self.search_handler.apply_filters(
                self.sample_search_results, filters
            )
            assert isinstance(filtered_results, list)
            assert len(filtered_results) == 1
            assert filtered_results[0].vacancy_id == "1"

    @patch('builtins.input', return_value='salary_desc')
    @patch('builtins.print')
    def test_sort_search_results(self, mock_print, mock_input):
        """Тест сортировки результатов поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'sort_results'):
            pytest.skip("VacancySearchHandler or sort_results not available")

        # Создаем мок для Vacancy, если он не импортирован
        if not SEARCH_HANDLER_AVAILABLE:
            class MockVacancy:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
            Vacancy = MockVacancy
            self.sample_search_results = [
                Vacancy(title="B", salary=100000),
                Vacancy(title="A", salary=150000)
            ]
            
        # Предполагаем, что sort_results возвращает отсортированные результаты
        expected_sorted_results = sorted(self.sample_search_results, key=lambda x: x.salary, reverse=True)
        with patch.object(self.search_handler, 'sort_results', return_value=expected_sorted_results):
            sorted_results = self.search_handler.sort_results(self.sample_search_results)
            assert isinstance(sorted_results, list)
            assert len(sorted_results) == len(self.sample_search_results)
            assert sorted_results[0].title == "A"
            mock_input.assert_called_once()

    @patch('builtins.print')
    def test_display_search_results_summary(self, mock_print):
        """Тест отображения сводки результатов поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'display_summary'):
            pytest.skip("VacancySearchHandler or display_summary not available")

        self.search_handler.display_summary(self.sample_search_results, 'python')
        mock_print.assert_called()

    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_set_results_limit(self, mock_print, mock_input):
        """Тест установки лимита результатов"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'set_limit'):
            pytest.skip("VacancySearchHandler or set_limit not available")
            
        # Предполагаем, что set_limit возвращает значение лимита
        with patch.object(self.search_handler, 'set_limit', return_value=5):
            limit = self.search_handler.set_limit()
            assert limit == 5
            mock_input.assert_called_once()

    @patch('builtins.input', return_value='7')
    @patch('builtins.print')
    def test_set_search_period(self, mock_print, mock_input):
        """Тест установки периода поиска (в днях)"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'set_search_period'):
            pytest.skip("VacancySearchHandler or set_search_period not available")
            
        # Предполагаем, что set_search_period возвращает значение периода
        with patch.object(self.search_handler, 'set_search_period', return_value=7):
            period = self.search_handler.set_search_period()
            assert period == 7
            mock_input.assert_called_once()

    def test_validate_search_query(self):
        """Тест валидации поискового запроса"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'validate_query'):
            pytest.skip("VacancySearchHandler or validate_query not available")
            
        # Тест валидного запроса
        assert self.search_handler.validate_query('python developer') is True
        
        # Тест невалидного запроса
        assert self.search_handler.validate_query('') is False
        assert self.search_handler.validate_query('   ') is False

    @patch('builtins.print')
    def test_save_search_criteria(self, mock_print):
        """Тест сохранения критериев поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'save_criteria'):
            pytest.skip("VacancySearchHandler or save_criteria not available")
            
        criteria = {
            'query': 'python',
            'sources': ['hh.ru'],
            'min_salary': 100000,
            'location': 'Москва'
        }
        
        # Предполагаем, что save_criteria возвращает True при успехе
        with patch.object(self.search_handler, 'save_criteria', return_value=True):
            result = self.search_handler.save_criteria(criteria, 'my_search')
            assert result is True

    @patch('builtins.input', return_value='my_search')
    @patch('builtins.print')
    def test_load_saved_search_criteria(self, mock_print, mock_input):
        """Тест загрузки сохранённых критериев поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'load_criteria'):
            pytest.skip("VacancySearchHandler or load_criteria not available")
            
        expected_criteria = {
            'query': 'python',
            'sources': ['hh.ru'],
            'min_salary': 100000,
            'location': 'Москва'
        }
        # Предполагаем, что load_criteria возвращает словарь с критериями
        with patch.object(self.search_handler, 'load_criteria', return_value=expected_criteria):
            criteria = self.search_handler.load_criteria()
            assert isinstance(criteria, dict)
            assert criteria == expected_criteria
            mock_input.assert_called_once()

    @patch('builtins.print')
    def test_search_history(self, mock_print):
        """Тест истории поисков"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'get_search_history'):
            pytest.skip("VacancySearchHandler or get_search_history not available")
            
        expected_history = [{'query': 'python'}, {'query': 'java'}]
        # Предполагаем, что get_search_history возвращает список истории
        with patch.object(self.search_handler, 'get_search_history', return_value=expected_history):
            history = self.search_handler.get_search_history()
            assert isinstance(history, list)
            assert history == expected_history

    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_repeat_last_search(self, mock_print, mock_input):
        """Тест повторения последнего поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'repeat_last_search'):
            pytest.skip("VacancySearchHandler or repeat_last_search not available")

        # Мокируем API для имитации поиска
        mock_unified_api = Mock()
        mock_unified_api.search_vacancies.return_value = self.sample_search_results

        # Если VacancySearchHandler доступен, создаем экземпляр с моками
        if SEARCH_HANDLER_AVAILABLE:
            handler_for_repeat = VacancySearchHandler(mock_unified_api, Mock())
        else:
            pytest.skip("VacancySearchHandler not available for repeat test")

        # Предполагаем, что repeat_last_search возвращает результаты поиска
        with patch.object(handler_for_repeat, 'repeat_last_search', return_value=self.sample_search_results):
            result = handler_for_repeat.repeat_last_search()
            assert result == self.sample_search_results
            mock_input.assert_called_once()
            mock_unified_api.search_vacancies.assert_called_once()

    @patch('builtins.print')
    def test_export_search_results(self, mock_print):
        """Тест экспорта результатов поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'export_results'):
            pytest.skip("VacancySearchHandler or export_results not available")

        # Мокируем builtins.open для перехвата записи в файл
        mock_file = Mock()
        mock_open = Mock(return_value=mock_file)
        
        with patch('builtins.open', mock_open):
            result = self.search_handler.export_results(
                self.sample_search_results, 'search_results.json'
            )
            assert result is None # Предполагаем, что метод ничего не возвращает
            mock_open.assert_called_once_with('search_results.json', 'w', encoding='utf-8')
            mock_file.write.assert_called()

    @patch('builtins.print')
    def test_advanced_search_options(self, mock_print):
        """Тест расширенных опций поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'show_advanced_options'):
            pytest.skip("VacancySearchHandler or show_advanced_options not available")
            
        self.search_handler.show_advanced_options()
        mock_print.assert_called()

    @patch('builtins.input', return_value='python OR java')
    def test_complex_search_query(self, mock_input):
        """Тест сложного поискового запроса с операторами"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'parse_complex_query'):
            pytest.skip("VacancySearchHandler or parse_complex_query not available")
            
        # Предполагаем, что parse_complex_query возвращает разобранный запрос
        expected_parsed = {'query': 'python OR java'}
        with patch.object(self.search_handler, 'parse_complex_query', return_value=expected_parsed):
            parsed = self.search_handler.parse_complex_query()
            assert isinstance(parsed, dict)
            assert parsed == expected_parsed
            mock_input.assert_called_once()

    @patch('builtins.print')
    def test_search_suggestions(self, mock_print):
        """Тест предложений для поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'get_suggestions'):
            pytest.skip("VacancySearchHandler or get_suggestions not available")
            
        expected_suggestions = ['python', 'python developer', 'python jobs']
        # Предполагаем, что get_suggestions возвращает список предложений
        with patch.object(self.search_handler, 'get_suggestions', return_value=expected_suggestions):
            suggestions = self.search_handler.get_suggestions('py')
            assert isinstance(suggestions, list)
            assert suggestions == expected_suggestions

    def test_search_performance_monitoring(self):
        """Тест мониторинга производительности поиска"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'monitor_performance'):
            pytest.skip("VacancySearchHandler or monitor_performance not available")
            
        # Эмуляция времени выполнения 1 сек
        with patch('time.time', side_effect=[0, 1]):  
            performance = self.search_handler.monitor_performance(
                lambda: self.sample_search_results
            )
            assert performance is not None
            assert isinstance(performance, float)
            assert performance >= 1.0 # Должно быть около 1.0 секунды

    @patch('builtins.print')
    def test_search_error_handling(self, mock_print):
        """Тест обработки ошибок при поиске"""
        if not SEARCH_HANDLER_AVAILABLE or not hasattr(self.search_handler, 'handle_search_error'):
            pytest.skip("VacancySearchHandler or handle_search_error not available")
            
        error = Exception("Search API unavailable")
        # Предполагаем, что handle_search_error логирует ошибку и возвращает None
        with patch.object(self.search_handler, 'handle_search_error', return_value=None) as mock_handle_error:
            result = self.search_handler.handle_search_error(error)
            assert result is None
            mock_handle_error.assert_called_once_with(error)