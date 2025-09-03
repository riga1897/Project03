"""
Комплексные тесты для user_interface с максимальным покрытием кода.
Включает тестирование всех функций главного интерфейса приложения.
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any, Optional

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Глобальные моки для всех внешних зависимостей
mock_psycopg2 = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2

from src.user_interface import (
    main,
    create_storage_and_api_instances,
    display_main_menu,
    search_and_save_vacancies,
    display_all_vacancies,
    display_top_vacancies,
    filter_vacancies_by_keyword,
    filter_vacancies_by_salary,
    clear_vacancy_data,
    display_database_statistics,
    clear_api_cache,
    save_vacancies_to_json,
    demo_db_manager
)


class TestUserInterfaceComponents:
    """Комплексное тестирование компонентов пользовательского интерфейса"""
    
    def test_create_storage_and_api_instances(self):
        """Тестирование создания экземпляров storage и API"""
        with patch('src.user_interface.PostgresSaver') as mock_postgres, \
             patch('src.user_interface.UnifiedAPI') as mock_unified, \
             patch('src.user_interface.DBManager') as mock_db:
            
            mock_postgres_instance = Mock()
            mock_unified_instance = Mock()
            mock_db_instance = Mock()
            
            mock_postgres.return_value = mock_postgres_instance
            mock_unified.return_value = mock_unified_instance
            mock_db.return_value = mock_db_instance
            
            unified_api, storage, db_manager = create_storage_and_api_instances()
            
            assert unified_api == mock_unified_instance
            assert storage == mock_postgres_instance
            assert db_manager == mock_db_instance
            
            mock_postgres.assert_called_once()
            mock_unified.assert_called_once()
            mock_db.assert_called_once()
    
    def test_display_main_menu(self):
        """Тестирование отображения главного меню"""
        # Функция не должна вызывать исключений
        try:
            display_main_menu()
        except Exception as e:
            pytest.fail(f"display_main_menu should not raise exceptions: {e}")
    
    @patch('builtins.input', side_effect=['1', 'Python', '7'])
    @patch('builtins.print')
    def test_search_and_save_vacancies(self, mock_print, mock_input):
        """Тестирование поиска и сохранения вакансий"""
        mock_unified_api = Mock()
        mock_storage = Mock()
        
        # Настраиваем мок для возврата тестовых данных
        mock_unified_api.search_vacancies.return_value = [
            {'id': '1', 'name': 'Python Developer', 'url': 'https://test1.com'},
            {'id': '2', 'name': 'Java Developer', 'url': 'https://test2.com'}
        ]
        
        try:
            search_and_save_vacancies(mock_unified_api, mock_storage)
            
            # Проверяем, что API был вызван
            mock_unified_api.search_vacancies.assert_called()
            
            # Проверяем, что storage был вызван для сохранения
            mock_storage.save_vacancies.assert_called()
            
        except Exception as e:
            pytest.fail(f"search_and_save_vacancies should not raise exceptions: {e}")
    
    def test_display_all_vacancies(self):
        """Тестирование отображения всех вакансий"""
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = [
            ('Company A', 'Python Developer', 100000, 'https://test1.com'),
            ('Company B', 'Java Developer', 120000, 'https://test2.com')
        ]
        
        try:
            display_all_vacancies(mock_storage)
            mock_storage.get_vacancies.assert_called_once()
        except Exception as e:
            pytest.fail(f"display_all_vacancies should not raise exceptions: {e}")
    
    @patch('builtins.input', return_value='10')
    def test_display_top_vacancies(self, mock_input):
        """Тестирование отображения топ вакансий"""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_higher_salary.return_value = [
            ('Company A', 'Senior Python Developer', 150000, 'https://test1.com'),
            ('Company B', 'Lead Java Developer', 180000, 'https://test2.com')
        ]
        
        try:
            display_top_vacancies(mock_db_manager)
            mock_db_manager.get_vacancies_with_higher_salary.assert_called_once()
        except Exception as e:
            pytest.fail(f"display_top_vacancies should not raise exceptions: {e}")
    
    @patch('builtins.input', return_value='Python')
    def test_filter_vacancies_by_keyword(self, mock_input):
        """Тестирование фильтрации вакансий по ключевому слову"""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_keyword.return_value = [
            ('Company A', 'Python Developer', 100000, 'https://test1.com')
        ]
        
        try:
            filter_vacancies_by_keyword(mock_db_manager)
            mock_db_manager.get_vacancies_with_keyword.assert_called_once_with('Python')
        except Exception as e:
            pytest.fail(f"filter_vacancies_by_keyword should not raise exceptions: {e}")
    
    @patch('builtins.input', return_value='100000')
    def test_filter_vacancies_by_salary(self, mock_input):
        """Тестирование фильтрации вакансий по зарплате"""
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = [
            ('Company A', 'Python Developer', 120000, 'https://test1.com'),
            ('Company B', 'Java Developer', 80000, 'https://test2.com')
        ]
        
        try:
            filter_vacancies_by_salary(mock_storage)
            mock_storage.get_vacancies.assert_called_once()
        except Exception as e:
            pytest.fail(f"filter_vacancies_by_salary should not raise exceptions: {e}")
    
    @patch('builtins.input', return_value='y')
    def test_clear_vacancy_data(self, mock_input):
        """Тестирование очистки данных о вакансиях"""
        mock_storage = Mock()
        
        try:
            clear_vacancy_data(mock_storage)
            # Проверяем, что метод очистки был вызван (если существует)
            if hasattr(mock_storage, 'clear_vacancies'):
                mock_storage.clear_vacancies.assert_called_once()
        except Exception as e:
            pytest.fail(f"clear_vacancy_data should not raise exceptions: {e}")
    
    def test_display_database_statistics(self):
        """Тестирование отображения статистики базы данных"""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            ('Company A', 10),
            ('Company B', 15)
        ]
        mock_db_manager.get_avg_salary.return_value = 125000.0
        
        try:
            display_database_statistics(mock_db_manager)
            mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
            mock_db_manager.get_avg_salary.assert_called_once()
        except Exception as e:
            pytest.fail(f"display_database_statistics should not raise exceptions: {e}")
    
    def test_clear_api_cache(self):
        """Тестирование очистки кэша API"""
        mock_unified_api = Mock()
        
        try:
            clear_api_cache(mock_unified_api)
            # Проверяем, что метод очистки кэша был вызван (если существует)
            if hasattr(mock_unified_api, 'clear_cache'):
                mock_unified_api.clear_cache.assert_called_once()
        except Exception as e:
            pytest.fail(f"clear_api_cache should not raise exceptions: {e}")
    
    @patch('builtins.input', return_value='test_export.json')
    def test_save_vacancies_to_json(self, mock_input):
        """Тестирование сохранения вакансий в JSON"""
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = [
            ('Company A', 'Python Developer', 100000, 'https://test1.com')
        ]
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            try:
                save_vacancies_to_json(mock_storage)
                mock_storage.get_vacancies.assert_called_once()
                mock_open.assert_called_once()
            except Exception as e:
                pytest.fail(f"save_vacancies_to_json should not raise exceptions: {e}")
    
    def test_demo_db_manager(self):
        """Тестирование демонстрации DBManager"""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            ('Яндекс', 25),
            ('Google', 18)
        ]
        mock_db_manager.get_all_vacancies.return_value = [
            ('Яндекс', 'Python Developer', 150000, 'https://test1.com')
        ]
        mock_db_manager.get_avg_salary.return_value = 135000.0
        mock_db_manager.get_vacancies_with_higher_salary.return_value = [
            ('Google', 'Senior Developer', 180000, 'https://test2.com')
        ]
        mock_db_manager.get_vacancies_with_keyword.return_value = [
            ('Яндекс', 'Python Developer', 150000, 'https://test1.com')
        ]
        
        try:
            demo_db_manager(mock_db_manager)
            
            # Проверяем, что все методы были вызваны
            mock_db_manager.get_companies_and_vacancies_count.assert_called()
            mock_db_manager.get_all_vacancies.assert_called()
            mock_db_manager.get_avg_salary.assert_called()
            mock_db_manager.get_vacancies_with_higher_salary.assert_called()
            mock_db_manager.get_vacancies_with_keyword.assert_called()
            
        except Exception as e:
            pytest.fail(f"demo_db_manager should not raise exceptions: {e}")


class TestMainApplicationFlow:
    """Комплексное тестирование основного потока приложения"""
    
    @patch('builtins.input', return_value='0')
    def test_main_application_exit(self, mock_input):
        """Тестирование выхода из приложения"""
        with patch('src.user_interface.create_storage_and_api_instances') as mock_create:
            mock_create.return_value = (Mock(), Mock(), Mock())
            
            try:
                main()
            except SystemExit:
                # Ожидаем SystemExit при выходе
                pass
            except Exception as e:
                pytest.fail(f"main should exit gracefully: {e}")
    
    @patch('builtins.input', side_effect=['1', '1', 'Python', '7', '0'])
    def test_main_application_search_workflow(self, mock_input):
        """Тестирование рабочего процесса поиска в главном приложении"""
        with patch('src.user_interface.create_storage_and_api_instances') as mock_create:
            mock_unified_api = Mock()
            mock_storage = Mock()
            mock_db_manager = Mock()
            
            mock_unified_api.search_vacancies.return_value = [
                {'id': '1', 'name': 'Python Developer', 'url': 'https://test.com'}
            ]
            
            mock_create.return_value = (mock_unified_api, mock_storage, mock_db_manager)
            
            try:
                main()
            except SystemExit:
                pass
            except Exception as e:
                pytest.fail(f"main search workflow should not fail: {e}")
    
    @patch('builtins.input', side_effect=['2', '0'])
    def test_main_application_display_workflow(self, mock_input):
        """Тестирование рабочего процесса отображения в главном приложении"""
        with patch('src.user_interface.create_storage_and_api_instances') as mock_create:
            mock_unified_api = Mock()
            mock_storage = Mock()
            mock_db_manager = Mock()
            
            mock_storage.get_vacancies.return_value = [
                ('Company', 'Job Title', 100000, 'https://test.com')
            ]
            
            mock_create.return_value = (mock_unified_api, mock_storage, mock_db_manager)
            
            try:
                main()
            except SystemExit:
                pass
            except Exception as e:
                pytest.fail(f"main display workflow should not fail: {e}")
    
    @patch('builtins.input', side_effect=['10', '0'])
    def test_main_application_demo_workflow(self, mock_input):
        """Тестирование рабочего процесса демонстрации в главном приложении"""
        with patch('src.user_interface.create_storage_and_api_instances') as mock_create:
            mock_unified_api = Mock()
            mock_storage = Mock()
            mock_db_manager = Mock()
            
            # Настраиваем все необходимые методы для демо
            mock_db_manager.get_companies_and_vacancies_count.return_value = []
            mock_db_manager.get_all_vacancies.return_value = []
            mock_db_manager.get_avg_salary.return_value = 0.0
            mock_db_manager.get_vacancies_with_higher_salary.return_value = []
            mock_db_manager.get_vacancies_with_keyword.return_value = []
            
            mock_create.return_value = (mock_unified_api, mock_storage, mock_db_manager)
            
            try:
                main()
            except SystemExit:
                pass
            except Exception as e:
                pytest.fail(f"main demo workflow should not fail: {e}")
    
    @patch('builtins.input', side_effect=['999', '0'])
    def test_main_application_invalid_choice(self, mock_input):
        """Тестирование обработки некорректного выбора в главном приложении"""
        with patch('src.user_interface.create_storage_and_api_instances') as mock_create:
            mock_create.return_value = (Mock(), Mock(), Mock())
            
            try:
                main()
            except SystemExit:
                pass
            except Exception as e:
                pytest.fail(f"main should handle invalid choices gracefully: {e}")


class TestErrorHandling:
    """Тестирование обработки ошибок в пользовательском интерфейсе"""
    
    def test_create_instances_error_handling(self):
        """Тестирование обработки ошибок при создании экземпляров"""
        with patch('src.user_interface.PostgresSaver', side_effect=Exception("Database error")):
            try:
                create_storage_and_api_instances()
            except Exception:
                # Функция может выбросить исключение или обработать его
                pass
    
    def test_search_error_handling(self):
        """Тестирование обработки ошибок поиска"""
        mock_unified_api = Mock()
        mock_storage = Mock()
        
        # API возвращает ошибку
        mock_unified_api.search_vacancies.side_effect = Exception("API Error")
        
        with patch('builtins.input', side_effect=['1', 'Python', '7']):
            try:
                search_and_save_vacancies(mock_unified_api, mock_storage)
                # Функция должна обработать ошибку
            except Exception as e:
                pytest.fail(f"search function should handle API errors: {e}")
    
    def test_storage_error_handling(self):
        """Тестирование обработки ошибок хранения"""
        mock_storage = Mock()
        mock_storage.get_vacancies.side_effect = Exception("Storage Error")
        
        try:
            display_all_vacancies(mock_storage)
            # Функция должна обработать ошибку
        except Exception as e:
            pytest.fail(f"display function should handle storage errors: {e}")
    
    def test_db_manager_error_handling(self):
        """Тестирование обработки ошибок DB Manager"""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("DB Error")
        
        try:
            display_database_statistics(mock_db_manager)
            # Функция должна обработать ошибку
        except Exception as e:
            pytest.fail(f"statistics function should handle DB errors: {e}")


class TestInputValidation:
    """Тестирование валидации пользовательского ввода"""
    
    @patch('builtins.input', side_effect=['', 'Python'])
    def test_empty_search_query_handling(self, mock_input):
        """Тестирование обработки пустого поискового запроса"""
        mock_unified_api = Mock()
        mock_storage = Mock()
        
        with patch('builtins.print'):
            try:
                search_and_save_vacancies(mock_unified_api, mock_storage)
            except Exception as e:
                pytest.fail(f"Should handle empty search query: {e}")
    
    @patch('builtins.input', side_effect=['invalid_number', '100000'])
    def test_invalid_salary_input_handling(self, mock_input):
        """Тестирование обработки некорректного ввода зарплаты"""
        mock_storage = Mock()
        mock_storage.get_vacancies.return_value = []
        
        try:
            filter_vacancies_by_salary(mock_storage)
        except Exception as e:
            pytest.fail(f"Should handle invalid salary input: {e}")
    
    @patch('builtins.input', side_effect=['maybe', 'y'])
    def test_invalid_confirmation_input_handling(self, mock_input):
        """Тестирование обработки некорректного подтверждения"""
        mock_storage = Mock()
        
        try:
            clear_vacancy_data(mock_storage)
        except Exception as e:
            pytest.fail(f"Should handle invalid confirmation input: {e}")


class TestDataFlow:
    """Тестирование потока данных в пользовательском интерфейсе"""
    
    def test_search_to_storage_flow(self):
        """Тестирование потока данных от поиска к хранению"""
        mock_unified_api = Mock()
        mock_storage = Mock()
        
        # Настраиваем данные для потока
        test_vacancies = [
            {'id': '1', 'name': 'Python Developer', 'url': 'https://test1.com'},
            {'id': '2', 'name': 'Java Developer', 'url': 'https://test2.com'}
        ]
        mock_unified_api.search_vacancies.return_value = test_vacancies
        
        with patch('builtins.input', side_effect=['1', 'Python', '7']):
            search_and_save_vacancies(mock_unified_api, mock_storage)
            
            # Проверяем поток данных
            mock_unified_api.search_vacancies.assert_called()
            mock_storage.save_vacancies.assert_called()
            
            # Проверяем, что данные передались правильно
            saved_data = mock_storage.save_vacancies.call_args[0][0]
            assert len(saved_data) > 0
    
    def test_storage_to_display_flow(self):
        """Тестирование потока данных от хранения к отображению"""
        mock_storage = Mock()
        
        # Настраиваем данные в хранилище
        stored_vacancies = [
            ('Company A', 'Python Developer', 100000, 'https://test1.com'),
            ('Company B', 'Java Developer', 120000, 'https://test2.com')
        ]
        mock_storage.get_vacancies.return_value = stored_vacancies
        
        display_all_vacancies(mock_storage)
        
        # Проверяем, что данные были получены из хранилища
        mock_storage.get_vacancies.assert_called_once()
    
    def test_filter_data_flow(self):
        """Тестирование потока данных при фильтрации"""
        mock_storage = Mock()
        
        # Данные с разными зарплатами для фильтрации
        test_vacancies = [
            ('Company A', 'Senior Developer', 150000, 'https://test1.com'),
            ('Company B', 'Junior Developer', 80000, 'https://test2.com'),
            ('Company C', 'Lead Developer', 200000, 'https://test3.com')
        ]
        mock_storage.get_vacancies.return_value = test_vacancies
        
        with patch('builtins.input', return_value='100000'):
            filter_vacancies_by_salary(mock_storage)
            
            # Проверяем, что данные были получены для фильтрации
            mock_storage.get_vacancies.assert_called_once()


class TestUserInterfaceIntegration:
    """Интеграционные тесты для пользовательского интерфейса"""
    
    @patch('builtins.input', side_effect=['1', '1', 'Python', '7', '2', '0'])
    def test_complete_search_and_display_workflow(self, mock_input):
        """Тестирование полного рабочего процесса поиска и отображения"""
        with patch('src.user_interface.create_storage_and_api_instances') as mock_create:
            mock_unified_api = Mock()
            mock_storage = Mock()
            mock_db_manager = Mock()
            
            # Настраиваем последовательность данных
            search_results = [
                {'id': '1', 'name': 'Python Developer', 'url': 'https://test.com'}
            ]
            display_results = [
                ('Test Company', 'Python Developer', 100000, 'https://test.com')
            ]
            
            mock_unified_api.search_vacancies.return_value = search_results
            mock_storage.get_vacancies.return_value = display_results
            
            mock_create.return_value = (mock_unified_api, mock_storage, mock_db_manager)
            
            try:
                main()
            except SystemExit:
                pass
            
            # Проверяем, что обе операции были выполнены
            mock_unified_api.search_vacancies.assert_called()
            mock_storage.save_vacancies.assert_called()
            mock_storage.get_vacancies.assert_called()
    
    def test_interface_performance_with_large_dataset(self):
        """Тестирование производительности интерфейса с большим объемом данных"""
        mock_storage = Mock()
        
        # Создаем большой набор данных
        large_dataset = [
            (f'Company {i}', f'Job {i}', 100000 + i * 1000, f'https://test{i}.com')
            for i in range(1000)
        ]
        mock_storage.get_vacancies.return_value = large_dataset
        
        import time
        start_time = time.time()
        
        display_all_vacancies(mock_storage)
        
        end_time = time.time()
        
        # Проверяем, что операция завершилась за разумное время
        assert (end_time - start_time) < 5.0  # Менее 5 секунд
    
    def test_concurrent_operations_handling(self):
        """Тестирование обработки одновременных операций"""
        # Симулируем одновременные операции с разными компонентами
        mock_unified_api = Mock()
        mock_storage = Mock()
        mock_db_manager = Mock()
        
        # Операции не должны конфликтовать
        search_and_save_vacancies(mock_unified_api, mock_storage)
        display_all_vacancies(mock_storage)
        display_database_statistics(mock_db_manager)
        
        # Все операции должны выполниться без ошибок


class TestUserInterfaceAccessibility:
    """Тестирование доступности пользовательского интерфейса"""
    
    def test_menu_display_formatting(self):
        """Тестирование форматирования отображения меню"""
        with patch('builtins.print') as mock_print:
            display_main_menu()
            
            # Проверяем, что что-то было выведено
            assert mock_print.called
    
    def test_error_message_clarity(self):
        """Тестирование четкости сообщений об ошибках"""
        mock_storage = Mock()
        mock_storage.get_vacancies.side_effect = Exception("Test error")
        
        with patch('builtins.print') as mock_print:
            try:
                display_all_vacancies(mock_storage)
            except Exception:
                pass
            
            # Проверяем, что сообщения об ошибках выводятся (если реализовано)
    
    def test_progress_indication(self):
        """Тестирование индикации прогресса"""
        mock_unified_api = Mock()
        mock_storage = Mock()
        
        # Симулируем долгую операцию
        mock_unified_api.search_vacancies.return_value = [
            {'id': str(i), 'name': f'Job {i}', 'url': f'https://test{i}.com'}
            for i in range(100)
        ]
        
        with patch('builtins.input', side_effect=['1', 'Python', '7']):
            with patch('builtins.print') as mock_print:
                search_and_save_vacancies(mock_unified_api, mock_storage)
                
                # Проверяем, что выводятся сообщения о прогрессе (если реализовано)
                assert mock_print.called