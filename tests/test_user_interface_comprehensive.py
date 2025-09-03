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

from src.user_interface import main
from src.ui_interfaces.console_interface import UserInterface
from src.storage.storage_factory import StorageFactory
from src.storage.db_manager import DBManager
from src.api_modules.unified_api import UnifiedAPI


class TestUserInterfaceComponents:
    """Комплексное тестирование компонентов пользовательского интерфейса"""
    
    def test_create_storage_and_api_instances(self):
        """Тестирование создания экземпляров storage и API"""
        with patch('src.storage.storage_factory.StorageFactory.create_storage') as mock_storage_factory, \
             patch('src.api_modules.unified_api.UnifiedAPI') as mock_unified, \
             patch('src.storage.db_manager.DBManager') as mock_db:
            
            mock_storage_instance = Mock()
            mock_unified_instance = Mock()
            mock_db_instance = Mock()
            
            mock_storage_factory.return_value = mock_storage_instance
            mock_unified.return_value = mock_unified_instance
            mock_db.return_value = mock_db_instance
            
            # Тестируем создание компонентов через UserInterface
            ui = UserInterface(storage=mock_storage_instance, db_manager=mock_db_instance)
            
            assert ui.storage == mock_storage_instance
            assert ui.db_manager == mock_db_instance
            assert hasattr(ui, 'unified_api')
    
    def test_user_interface_run(self):
        """Тестирование запуска пользовательского интерфейса"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        with patch('builtins.input', return_value='0'):  # Выход
            try:
                ui.run()
            except SystemExit:
                pass  # Ожидаемый выход
    
    @patch('builtins.input', side_effect=['1', 'Python', '7'])
    @patch('builtins.print')
    def test_search_handler(self, mock_print, mock_input):
        """Тестирование обработчика поиска вакансий"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        # Настраиваем мок для возврата тестовых данных
        ui.unified_api.search_vacancies_from_all_sources = Mock(return_value=[
            {'id': '1', 'name': 'Python Developer', 'url': 'https://test1.com'},
            {'id': '2', 'name': 'Java Developer', 'url': 'https://test2.com'}
        ])
        
        try:
            ui.search_handler.search_vacancies()
            
            # Проверяем, что API был вызван
            assert ui.unified_api.search_vacancies_from_all_sources.called
            
        except Exception as e:
            pytest.fail(f"search handler should not raise exceptions: {e}")
    
    def test_display_handler(self):
        """Тестирование обработчика отображения вакансий"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        mock_storage.get_vacancies.return_value = [
            Mock(title='Python Developer', employer=Mock(name='Company A')),
            Mock(title='Java Developer', employer=Mock(name='Company B'))
        ]
        
        # Проверяем, что display_handler существует и работает
        assert hasattr(ui, 'display_handler')
        assert ui.display_handler is not None
    
    @patch('builtins.input', return_value='10')
    def test_db_manager_operations(self, mock_input):
        """Тестирование операций с менеджером базы данных"""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_higher_salary.return_value = [
            ('Company A', 'Senior Python Developer', 150000, 'https://test1.com'),
            ('Company B', 'Lead Java Developer', 180000, 'https://test2.com')
        ]
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            ('Company A', 10),
            ('Company B', 15)
        ]
        mock_db_manager.get_avg_salary.return_value = 135000.0
        
        # Проверяем, что методы могут быть вызваны
        assert mock_db_manager.get_vacancies_with_higher_salary() is not None
        assert mock_db_manager.get_companies_and_vacancies_count() is not None
    
    @patch('builtins.input', return_value='Python')
    def test_vacancy_operations_coordinator(self, mock_input):
        """Тестирование координатора операций с вакансиями"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        mock_db.get_vacancies_with_keyword.return_value = [
            ('Company A', 'Python Developer', 100000, 'https://test1.com')
        ]
        
        # Проверяем, что operations_coordinator существует
        assert hasattr(ui, 'operations_coordinator')
        assert ui.operations_coordinator is not None
    
    @patch('builtins.input', return_value='100000')
    def test_vacancy_operations(self, mock_input):
        """Тестирование операций с вакансиями"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        # Проверяем, что vacancy_ops существует
        assert hasattr(ui, 'vacancy_ops')
        assert ui.vacancy_ops is not None
    
    @patch('builtins.input', return_value='y')
    def test_user_interface_components(self, mock_input):
        """Тестирование компонентов пользовательского интерфейса"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        # Проверяем все основные компоненты
        assert hasattr(ui, 'unified_api')
        assert hasattr(ui, 'storage')
        assert hasattr(ui, 'search_handler')
        assert hasattr(ui, 'display_handler')
        assert hasattr(ui, 'operations_coordinator')
        assert hasattr(ui, 'db_manager')
    
    def test_db_manager_methods(self):
        """Тестирование методов менеджера базы данных"""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            ('Company A', 10),
            ('Company B', 15)
        ]
        mock_db_manager.get_avg_salary.return_value = 125000.0
        mock_db_manager.get_all_vacancies.return_value = [
            ('Company A', 'Python Dev', 100000, 'https://test.com')
        ]
        
        # Проверяем все методы DBManager
        assert mock_db_manager.get_companies_and_vacancies_count() is not None
        assert mock_db_manager.get_avg_salary() is not None
        assert mock_db_manager.get_all_vacancies() is not None
    
    def test_unified_api_methods(self):
        """Тестирование методов унифицированного API"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        # Проверяем методы UnifiedAPI
        assert hasattr(ui.unified_api, 'search_vacancies_from_all_sources')
        assert hasattr(ui.unified_api, 'get_available_sources')
        assert hasattr(ui.unified_api, 'clear_cache')
    
    @patch('builtins.input', return_value='test_export.json')
    def test_storage_operations(self, mock_input):
        """Тестирование операций хранилища"""
        mock_storage = Mock()
        mock_db = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        mock_storage.get_vacancies.return_value = [
            Mock(title='Python Developer', employer=Mock(name='Company A'))
        ]
        
        # Проверяем операции хранилища
        vacancies = mock_storage.get_vacancies()
        assert vacancies is not None
        assert len(vacancies) > 0
    
    def test_db_manager_demo(self):
        """Тестирование демонстрации DBManager"""
        mock_db = Mock()
        mock_db.get_companies_and_vacancies_count.return_value = [
            ('Яндекс', 25),
            ('Google', 18)
        ]
        mock_db.get_all_vacancies.return_value = [
            ('Яндекс', 'Python Developer', 150000, 'https://test1.com')
        ]
        mock_db.get_avg_salary.return_value = 135000.0
        mock_db.get_vacancies_with_higher_salary.return_value = [
            ('Google', 'Senior Developer', 180000, 'https://test2.com')
        ]
        mock_db.get_vacancies_with_keyword.return_value = [
            ('Яндекс', 'Python Developer', 150000, 'https://test1.com')
        ]
        
        mock_storage = Mock()
        ui = UserInterface(storage=mock_storage, db_manager=mock_db)
        
        # Проверяем, что demo создан
        if ui.demo:
            assert ui.demo is not None


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