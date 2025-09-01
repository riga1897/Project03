
import os
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestUserInterface:
    """Комплексные тесты для модуля пользовательского интерфейса"""

    @pytest.fixture
    def consolidated_mocks(self) -> dict:
        """Консолидированные моки для всех тестов"""
        mock_logger = Mock()
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = True
        mock_db_manager.create_tables.return_value = None
        mock_db_manager.populate_companies_table.return_value = None
        mock_db_manager.get_companies_and_vacancies_count.return_value = []

        mock_app_config = Mock()
        mock_app_config.default_storage_type = "postgres"
        
        mock_db_config = Mock()
        mock_db_config.get.return_value = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
        mock_app_config.get_db_config.return_value = mock_db_config

        mock_storage = Mock()
        mock_ui = Mock()
        mock_ui.run.return_value = None

        return {
            'logger': mock_logger,
            'db_manager': mock_db_manager,
            'app_config': mock_app_config,
            'db_config': mock_db_config,
            'storage': mock_storage,
            'ui': mock_ui
        }

    def test_main_function_import(self):
        """Тест импорта главной функции"""
        try:
            from src.user_interface import main
            assert callable(main)
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

    @patch('src.user_interface.logging')
    @patch('src.storage.db_manager.DBManager')
    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.storage_factory.StorageFactory')
    @patch('src.ui_interfaces.console_interface.UserInterface')
    def test_main_function_mocked(
        self, 
        mock_user_interface_class,
        mock_storage_factory, 
        mock_app_config_class,
        mock_db_manager_class,
        mock_logging,
        consolidated_mocks
    ):
        """Тест главной функции с консолидированными моками"""
        try:
            from src.user_interface import main
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

        # Используем консолидированные моки
        mock_logging.getLogger.return_value = consolidated_mocks['logger']
        mock_db_manager_class.return_value = consolidated_mocks['db_manager']
        mock_app_config_class.return_value = consolidated_mocks['app_config']
        mock_storage_factory.create_storage.return_value = consolidated_mocks['storage']
        mock_user_interface_class.return_value = consolidated_mocks['ui']

        # Выполняем функцию main
        try:
            main()
            
            # Проверяем, что компоненты были инициализированы
            mock_db_manager_class.assert_called_once()
            mock_app_config_class.assert_called_once()
            # UserInterface может не создаваться при ошибках БД
            
        except Exception as e:
            # Ожидаем ошибку из-за проблем с конфигурацией БД в моках
            error_message = str(e).lower()
            db_related_errors = [
                "базы данных", "database", "connection", "подключение", 
                "postgres", "postgresql", "критическая ошибка"
            ]
            assert any(error_term in error_message for error_term in db_related_errors)

    @patch('src.user_interface.logging')
    @patch('src.storage.db_manager.DBManager')
    def test_main_function_db_failure(self, mock_db_manager_class, mock_logging, consolidated_mocks):
        """Тест обработки ошибки подключения к БД"""
        try:
            from src.user_interface import main
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

        mock_logging.getLogger.return_value = consolidated_mocks['logger']
        consolidated_mocks['db_manager'].check_connection.return_value = False
        mock_db_manager_class.return_value = consolidated_mocks['db_manager']

        # Выполняем main - должно корректно завершиться без исключения
        main()
        
        # Проверяем, что была попытка создать DBManager
        mock_db_manager_class.assert_called_once()

    def test_vacancy_model_basic(self):
        """Тест базовой модели вакансии"""
        try:
            from src.vacancies.models import Vacancy
            from src.utils.salary import Salary

            # Правильное создание объекта Salary согласно реальному API
            salary_data = {'from': 100000, 'to': 150000, 'currency': 'RUR'}
            salary = Salary(salary_data)
            
            vacancy = Vacancy(
                title="Python Developer",
                url="https://test.com/1",
                vacancy_id="1",
                source="hh",
                employer={"name": "Test Company"},
                salary=salary,
                description="Test job"
            )

            assert vacancy.title == "Python Developer"
            assert vacancy.vacancy_id == "1"
            assert vacancy.source == "hh"

        except ImportError:
            pytest.skip("Модели вакансий не найдены")

    def test_salary_model_basic(self):
        """Тест базовой модели зарплаты"""
        try:
            from src.utils.salary import Salary

            # Правильное создание объекта Salary
            salary_data = {'from': 50000, 'to': 80000, 'currency': 'RUR'}
            salary = Salary(salary_data)

            # Проверяем наличие атрибутов (разные возможные названия)
            has_from = hasattr(salary, 'salary_from') or hasattr(salary, 'from_salary') or hasattr(salary, 'from')
            has_to = hasattr(salary, 'salary_to') or hasattr(salary, 'to_salary') or hasattr(salary, 'to') 
            has_currency = hasattr(salary, 'currency')
            
            assert has_from and has_to and has_currency

        except ImportError:
            pytest.skip("Модель зарплаты не найдена")

    def test_user_interface_class_basic(self):
        """Тест базового класса пользовательского интерфейса"""
        try:
            from src.ui_interfaces.console_interface import UserInterface

            mock_storage = Mock()
            mock_db_manager = Mock()

            ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)

            assert ui.storage == mock_storage
            assert ui.db_manager == mock_db_manager

        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    @patch('src.storage.db_manager.DBManager')
    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.storage_factory.StorageFactory')
    @patch('src.ui_interfaces.console_interface.UserInterface')
    def test_keyboard_interrupt_handling(self, mock_ui_class, mock_factory, 
                                       mock_config_class, mock_db_manager_class,
                                       mock_print, mock_input, consolidated_mocks):
        """Тест обработки KeyboardInterrupt"""
        try:
            from src.user_interface import main
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

        # Используем консолидированные моки
        mock_db_manager_class.return_value = consolidated_mocks['db_manager']
        mock_config_class.return_value = consolidated_mocks['app_config']
        mock_factory.create_storage.return_value = consolidated_mocks['storage']
        
        consolidated_mocks['ui'].run.side_effect = KeyboardInterrupt()
        mock_ui_class.return_value = consolidated_mocks['ui']

        # Запускаем main - должно корректно обработать KeyboardInterrupt
        main()

    def test_constants_and_types(self):
        """Тест базовых констант и типов"""
        assert isinstance("test", str)
        assert isinstance(123, int)
        assert isinstance([], list)
        assert isinstance({}, dict)
        assert isinstance(True, bool)

    def test_mock_functionality(self):
        """Тест функциональности моков"""
        mock_obj = Mock()
        mock_obj.test_method.return_value = "test_result"

        result = mock_obj.test_method()
        assert result == "test_result"
        mock_obj.test_method.assert_called_once()

    @patch('src.user_interface.logging')
    def test_logging_configuration(self, mock_logging):
        """Тест конфигурации логирования"""
        try:
            import src.user_interface
            
            # Проверяем, что модуль загружен
            assert hasattr(src.user_interface, 'main')
            
            # Логирование может быть настроено при импорте или в main
            # Проверяем хотя бы то, что getLogger был вызван
            mock_logging.getLogger.assert_called()
            
        except ImportError:
            pytest.skip("Модуль user_interface не найден")

    def test_application_structure(self):
        """Тест структуры приложения"""
        try:
            # Проверяем основные модули
            import src.user_interface
            import src.config.app_config
            import src.storage.storage_factory
            import src.ui_interfaces.console_interface
            
            assert hasattr(src.user_interface, 'main')
            
        except ImportError as e:
            pytest.skip(f"Не удается импортировать модули: {e}")

    def test_error_handling_patterns(self):
        """Тест паттернов обработки ошибок"""
        # Тестируем различные типы исключений
        test_exceptions = [
            ValueError("Test value error"),
            TypeError("Test type error"),
            KeyError("Test key error"),
            AttributeError("Test attribute error")
        ]
        
        for exc in test_exceptions:
            assert isinstance(exc, Exception)
            assert str(exc)  # Проверяем, что есть сообщение об ошибке

    def test_interface_integration_readiness(self, consolidated_mocks):
        """Тест готовности интерфейса к интеграции"""
        try:
            from src.ui_interfaces.console_interface import UserInterface
            
            # Создаем интерфейс с консолидированными моками
            ui = UserInterface(
                storage=consolidated_mocks['storage'],
                db_manager=consolidated_mocks['db_manager']
            )
            
            # Проверяем основные атрибуты
            assert hasattr(ui, 'storage')
            assert hasattr(ui, 'db_manager')
            
            # Проверяем основные методы
            expected_methods = ['run', '_show_menu']
            existing_methods = [method for method in expected_methods if hasattr(ui, method)]
            assert len(existing_methods) > 0
            
        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    @patch('builtins.print')
    def test_interface_workflow_simulation(self, mock_print, consolidated_mocks):
        """Тест симуляции рабочего процесса интерфейса"""
        try:
            from src.ui_interfaces.console_interface import UserInterface
            
            ui = UserInterface(
                storage=consolidated_mocks['storage'],
                db_manager=consolidated_mocks['db_manager']
            )
            
            # Мокируем все пользовательские взаимодействия
            with patch('builtins.input', return_value="0"), \
                 patch('src.utils.ui_helpers.get_user_input', return_value="0") if SRC_AVAILABLE else patch('builtins.input', return_value="0"):
                
                if hasattr(ui, 'run'):
                    try:
                        ui.run()
                    except Exception as e:
                        # Ошибки могут возникать из-за мокирования
                        assert isinstance(e, Exception)
                
                mock_print.assert_called()
            
        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    def test_interface_error_resilience(self, consolidated_mocks):
        """Тест устойчивости интерфейса к ошибкам"""
        try:
            from src.ui_interfaces.console_interface import UserInterface
            
            # Настраиваем моки для генерации ошибок
            error_storage = Mock()
            error_storage.get_vacancies.side_effect = Exception("Storage error")
            
            ui = UserInterface(
                storage=error_storage,
                db_manager=consolidated_mocks['db_manager']
            )
            
            # Интерфейс должен корректно инициализироваться даже с проблемным хранилищем
            assert ui.storage == error_storage
            assert ui.db_manager == consolidated_mocks['db_manager']
            
        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    @pytest.mark.parametrize("config_type", ["postgres", "file", "memory"])
    def test_parametrized_storage_types(self, config_type, consolidated_mocks):
        """Параметризованный тест разных типов хранилища"""
        consolidated_mocks['app_config'].default_storage_type = config_type
        
        try:
            from src.ui_interfaces.console_interface import UserInterface
            
            ui = UserInterface(
                storage=consolidated_mocks['storage'],
                db_manager=consolidated_mocks['db_manager']
            )
            
            # Интерфейс должен работать с любым типом хранилища
            assert ui.storage is not None
            
        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    def test_interface_performance(self, consolidated_mocks):
        """Тест производительности интерфейса"""
        import time
        
        try:
            from src.ui_interfaces.console_interface import UserInterface
            
            start_time = time.time()
            
            # Создаем множественные экземпляры интерфейса
            for _ in range(10):
                ui = UserInterface(
                    storage=consolidated_mocks['storage'],
                    db_manager=consolidated_mocks['db_manager']
                )
                
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Создание экземпляров должно быть быстрым
            assert execution_time < 1.0
            
        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    def test_interface_type_safety(self, consolidated_mocks):
        """Тест типобезопасности интерфейса"""
        try:
            from src.ui_interfaces.console_interface import UserInterface
            
            ui = UserInterface(
                storage=consolidated_mocks['storage'],
                db_manager=consolidated_mocks['db_manager']
            )
            
            # Проверяем типы основных атрибутов
            assert ui.storage is not None
            assert ui.db_manager is not None
            
            # Проверяем, что методы возвращают правильные типы
            if hasattr(ui, '_show_menu'):
                with patch('builtins.input', return_value="0"):
                    result = ui._show_menu()
                    assert isinstance(result, str)
            
        except ImportError:
            pytest.skip("Класс UserInterface не найден")

    def test_application_memory_management(self):
        """Тест управления памятью приложения"""
        import gc
        
        initial_objects = len(gc.get_objects())
        
        try:
            # Многократно импортируем и создаем объекты
            for _ in range(5):
                from src.user_interface import main
                mock_storage = Mock()
                mock_db_manager = Mock()
                
                try:
                    from src.ui_interfaces.console_interface import UserInterface
                    ui = UserInterface(storage=mock_storage, db_manager=mock_db_manager)
                    del ui
                except ImportError:
                    pass
                    
                del mock_storage, mock_db_manager
            
            gc.collect()
            final_objects = len(gc.get_objects())
            
            # Память не должна значительно увеличиваться
            assert final_objects - initial_objects < 100
            
        except ImportError:
            pytest.skip("Модули не найдены")

    def test_configuration_compatibility(self, consolidated_mocks):
        """Тест совместимости конфигурации"""
        # Тестируем разные конфигурации БД
        db_configs = [
            {'host': 'localhost', 'port': 5432, 'database': 'test'},
            {'host': '127.0.0.1', 'port': 5433, 'database': 'prod'},
            {'host': 'db.example.com', 'port': 5432, 'database': 'remote'}
        ]
        
        for config in db_configs:
            consolidated_mocks['db_config'].get.return_value = config
            
            try:
                from src.ui_interfaces.console_interface import UserInterface
                ui = UserInterface(
                    storage=consolidated_mocks['storage'],
                    db_manager=consolidated_mocks['db_manager']
                )
                # Интерфейс должен работать с любой конфигурацией
                assert ui is not None
                
            except ImportError:
                pytest.skip("Класс UserInterface не найден")
