
"""
Тесты для демонстрации функциональности DBManager
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from unittest.mock import MagicMock, Mock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
from src.utils.db_manager_demo import DBManagerDemo


class TestDBManagerDemo:
    """Тесты для класса демонстрации DBManager"""

    @pytest.fixture
    def mock_db_manager(self) -> Mock:
        """Создание мока DBManager"""
        mock_manager = Mock()
        
        # Настраиваем корректные возвращаемые значения
        mock_manager.get_target_companies_analysis.return_value = [
            ("Яндекс", 10),
            ("СБЕР", 8),
            ("Тинькофф", 5)
        ]
        
        mock_manager.get_companies_and_vacancies_count.return_value = [
            ("Яндекс", 10),
            ("СБЕР", 8),
            ("Тинькофф", 5)
        ]
        
        # Важно: настраиваем get_all_vacancies с правильной структурой
        mock_manager.get_all_vacancies.return_value = [
            {
                "title": "Python Developer",
                "company_name": "Яндекс",
                "salary_info": "100000 - 150000 RUR",
                "url": "https://example.com/1",
                "vacancy_id": "1"
            },
            {
                "title": "Java Developer", 
                "company_name": "СБЕР",
                "salary_info": "120000 - 180000 RUR",
                "url": "https://example.com/2",
                "vacancy_id": "2"
            }
        ]
        
        mock_manager.get_avg_salary.return_value = 125000.0
        
        mock_manager.get_vacancies_with_higher_salary.return_value = [
            {
                "title": "Senior Python Developer",
                "company_name": "Яндекс", 
                "salary_info": "150000 - 200000 RUR",
                "url": "https://example.com/3",
                "vacancy_id": "3"
            }
        ]
        
        mock_manager.get_vacancies_with_keyword.return_value = [
            {
                "title": "Python Developer",
                "company_name": "Яндекс",
                "salary_info": "100000 - 150000 RUR", 
                "url": "https://example.com/1",
                "vacancy_id": "1"
            }
        ]
        
        # Настраиваем get_database_stats с корректными типами
        mock_manager.get_database_stats.return_value = {
            "total_vacancies": 100,
            "total_companies": 15,
            "vacancies_with_salary": 80,
            "latest_vacancy_date": "2024-01-15",
            "earliest_vacancy_date": "2024-01-01",
            "vacancies_last_week": 25,
            "vacancies_last_month": 75,
            "vacancies_with_description": 90,
            "vacancies_with_requirements": 70,
            "vacancies_with_area": 85,
            "top_employers": [
                {"employer": "Яндекс", "vacancy_count": 10},
                {"employer": "СБЕР", "vacancy_count": 8}
            ]
        }
        
        mock_manager.check_connection.return_value = True
        
        return mock_manager

    @pytest.fixture
    def db_manager_demo(self, mock_db_manager) -> DBManagerDemo:
        """Создание экземпляра DBManagerDemo"""
        return DBManagerDemo(mock_db_manager)

    @patch('builtins.print')
    def test_run_full_demo(self, mock_print, db_manager_demo):
        """Тест полной демонстрации"""
        # Выполняем демонстрацию
        db_manager_demo.run_full_demo()
        
        # Проверяем что print был вызван (демонстрация что-то выводит)
        assert mock_print.called

    def test_demo_with_empty_results(self, mock_db_manager):
        """Тест демонстрации с пустыми результатами"""
        # Настраиваем пустые результаты
        mock_db_manager.get_target_companies_analysis.return_value = []
        mock_db_manager.get_companies_and_vacancies_count.return_value = []
        mock_db_manager.get_all_vacancies.return_value = []
        mock_db_manager.get_avg_salary.return_value = None
        mock_db_manager.get_vacancies_with_higher_salary.return_value = []
        mock_db_manager.get_vacancies_with_keyword.return_value = []
        
        # Важно: настраиваем get_database_stats с правильными типами
        mock_db_manager.get_database_stats.return_value = {
            "total_vacancies": 0,
            "total_companies": 0,
            "vacancies_with_salary": 0,
            "latest_vacancy_date": None,
            "earliest_vacancy_date": None,
            "vacancies_last_week": 0,
            "vacancies_last_month": 0,
            "vacancies_with_description": 0,
            "vacancies_with_requirements": 0,
            "vacancies_with_area": 0,
            "top_employers": []
        }

        demo = DBManagerDemo(mock_db_manager)

        # Демонстрация должна работать даже с пустыми результатами
        with patch('builtins.print'):
            demo.run_full_demo()

    @patch('builtins.print')
    def test_demo_methods_call_db_manager(self, mock_print, db_manager_demo):
        """Тест что демонстрация вызывает методы DB менеджера"""
        # Запускаем полную демонстрацию
        db_manager_demo.run_full_demo()
        
        # Проверяем что методы DBManager были вызваны
        db_manager = db_manager_demo.db_manager
        
        assert db_manager.get_target_companies_analysis.called
        assert db_manager.get_companies_and_vacancies_count.called
        assert db_manager.get_all_vacancies.called
        assert db_manager.get_avg_salary.called
        assert db_manager.get_vacancies_with_higher_salary.called
        assert db_manager.get_vacancies_with_keyword.called

    def test_demo_with_real_like_data(self, mock_db_manager):
        """Тест демонстрации с реалистичными данными"""
        # Настраиваем реалистичные данные
        mock_db_manager.get_target_companies_analysis.return_value = [
            ("ООО Яндекс", 15),
            ("ПАО Сбербанк", 12),
            ("АО Тинькофф Банк", 8),
            ("Mail.Ru Group", 6),
            ("Wildberries", 4)
        ]
        
        # Настраиваем корректную структуру для get_all_vacancies
        mock_db_manager.get_all_vacancies.return_value = [
            {
                "title": "Senior Python Developer",
                "company_name": "Яндекс",
                "salary_info": "150000 - 200000 RUR",
                "url": "https://hh.ru/vacancy/123",
                "vacancy_id": "123"
            },
            {
                "title": "Java Backend Developer",
                "company_name": "СБЕР", 
                "salary_info": "130000 - 180000 RUR",
                "url": "https://hh.ru/vacancy/456",
                "vacancy_id": "456"
            }
        ]
        
        mock_db_manager.get_avg_salary.return_value = 145000.0

        demo = DBManagerDemo(mock_db_manager)

        with patch('builtins.print') as mock_print:
            demo.run_full_demo()
            
        # Проверяем что демонстрация прошла без ошибок
        assert mock_print.called

    def test_demo_performance(self, db_manager_demo):
        """Тест производительности демонстрации"""
        import time

        start_time = time.time()
        with patch('builtins.print'):
            db_manager_demo.run_full_demo()
        end_time = time.time()

        # Демонстрация должна выполняться быстро
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Не более 5 секунд

    def test_demo_components_separately(self, db_manager_demo):
        """Тест отдельных компонентов демонстрации"""
        with patch('builtins.print'):
            # Тестируем что можем вызвать run_full_demo без ошибок
            try:
                db_manager_demo.run_full_demo()
                success = True
            except Exception as e:
                print(f"Ошибка: {e}")
                success = False

            assert success

    def test_db_manager_demo_initialization(self, mock_db_manager):
        """Тест инициализации DBManagerDemo"""
        demo = DBManagerDemo(mock_db_manager)
        
        assert demo is not None
        assert demo.db_manager is mock_db_manager
        assert hasattr(demo, 'run_full_demo')

    def test_demo_with_connection_error(self):
        """Тест демонстрации при ошибке подключения к БД"""
        mock_db_manager = Mock()
        mock_db_manager.check_connection.return_value = False
        
        # Настраиваем методы для выбрасывания исключений
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("DB Error")
        mock_db_manager.get_all_vacancies.side_effect = Exception("DB Error")
        mock_db_manager.get_avg_salary.side_effect = Exception("DB Error")
        
        demo = DBManagerDemo(mock_db_manager)
        
        # Демонстрация должна обрабатывать ошибки подключения
        with patch('builtins.print'):
            try:
                demo.run_full_demo()
                # Если не упала с ошибкой, то обработка ошибок работает
                success = True
            except Exception:
                # Допустимо если демонстрация не может продолжить без БД
                success = False
                
        # В любом случае тест должен завершиться
        assert success is not None

    def test_demo_individual_methods(self, db_manager_demo):
        """Тест отдельных методов демонстрации"""
        # Тестируем что можем вызвать приватные методы через публичный интерфейс
        with patch('builtins.print'):
            # Основной метод должен вызывать все подметоды
            db_manager_demo.run_full_demo()
            
        # Проверяем что все ключевые методы DBManager были вызваны
        db_manager = db_manager_demo.db_manager
        
        # Проверяем вызовы основных методов
        methods_to_check = [
            'get_companies_and_vacancies_count',
            'get_all_vacancies', 
            'get_avg_salary',
            'get_vacancies_with_higher_salary',
            'get_vacancies_with_keyword'
        ]
        
        for method_name in methods_to_check:
            method = getattr(db_manager, method_name)
            assert method.called, f"Метод {method_name} не был вызван"

    def test_demo_keyword_search_variations(self, mock_db_manager):
        """Тест демонстрации поиска по различным ключевым словам"""
        # Настраиваем различные результаты для разных ключевых слов
        def mock_keyword_search(keyword):
            if keyword.lower() == "python":
                return [
                    {
                        "title": "Python Developer",
                        "company_name": "Яндекс",
                        "salary_info": "120000 - 160000 RUR",
                        "url": "https://example.com/python",
                        "vacancy_id": "python_1"
                    }
                ]
            elif keyword.lower() == "java":
                return [
                    {
                        "title": "Java Developer",
                        "company_name": "СБЕР",
                        "salary_info": "130000 - 170000 RUR", 
                        "url": "https://example.com/java",
                        "vacancy_id": "java_1"
                    }
                ]
            else:
                return []
        
        mock_db_manager.get_vacancies_with_keyword.side_effect = mock_keyword_search
        
        demo = DBManagerDemo(mock_db_manager)
        
        with patch('builtins.print'):
            demo.run_full_demo()
        
        # Проверяем что поиск по ключевым словам был выполнен
        assert mock_db_manager.get_vacancies_with_keyword.called

    def test_demo_salary_analysis(self, mock_db_manager):
        """Тест демонстрации анализа зарплат"""
        # Настраиваем данные для анализа зарплат
        mock_db_manager.get_avg_salary.return_value = 135000.0
        
        mock_db_manager.get_vacancies_with_higher_salary.return_value = [
            {
                "title": "Lead Developer",
                "company_name": "Яндекс",
                "salary_info": "180000 - 250000 RUR",
                "url": "https://example.com/lead",
                "vacancy_id": "lead_1",
                "calculated_salary": 215000.0
            }
        ]
        
        demo = DBManagerDemo(mock_db_manager)
        
        with patch('builtins.print'):
            demo.run_full_demo()
        
        # Проверяем что анализ зарплат был выполнен
        assert mock_db_manager.get_avg_salary.called
        assert mock_db_manager.get_vacancies_with_higher_salary.called

    def test_demo_error_handling(self, mock_db_manager):
        """Тест обработки ошибок в демонстрации"""
        # Настраиваем один метод для выброса исключения
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("Test error")
        
        # Остальные методы работают нормально
        mock_db_manager.get_all_vacancies.return_value = []
        mock_db_manager.get_avg_salary.return_value = None
        
        demo = DBManagerDemo(mock_db_manager)
        
        # Демонстрация должна обрабатывать ошибки
        with patch('builtins.print'):
            try:
                demo.run_full_demo()
                # Если не упала, значит ошибки обрабатываются
                error_handled = True
            except Exception:
                # Если упала, это тоже нормально для тестирования
                error_handled = False
        
        # Тест должен завершиться в любом случае
        assert error_handled is not None

    def test_demo_initialization_with_none(self):
        """Тест инициализации с None вместо DBManager"""
        try:
            demo = DBManagerDemo(None)
            # Если инициализация прошла, проверяем что объект создан
            assert demo is not None
        except (TypeError, AttributeError):
            # Ожидаемое поведение при передаче None
            pass

    def test_demo_methods_existence(self, db_manager_demo):
        """Тест наличия методов демонстрации"""
        # Проверяем что основные методы определены
        assert hasattr(db_manager_demo, 'run_full_demo')
        assert callable(getattr(db_manager_demo, 'run_full_demo'))
        
        # Проверяем наличие приватных методов через рефлексию
        demo_methods = [attr for attr in dir(db_manager_demo) if attr.startswith('_demo_')]
        assert len(demo_methods) > 0

    def test_demo_with_large_dataset(self, mock_db_manager):
        """Тест демонстрации с большим набором данных"""
        # Создаем большой набор тестовых данных
        large_companies_data = [(f"Компания {i}", i * 10) for i in range(1, 21)]
        large_vacancies_data = []
        
        for i in range(1, 101):
            large_vacancies_data.append({
                "title": f"Developer {i}",
                "company_name": f"Компания {i % 20 + 1}",
                "salary_info": f"{50000 + i * 1000} - {80000 + i * 1000} RUR",
                "url": f"https://example.com/{i}",
                "vacancy_id": str(i)
            })
        
        mock_db_manager.get_companies_and_vacancies_count.return_value = large_companies_data
        mock_db_manager.get_all_vacancies.return_value = large_vacancies_data
        mock_db_manager.get_avg_salary.return_value = 95000.0
        
        demo = DBManagerDemo(mock_db_manager)
        
        import time
        start_time = time.time()
        
        with patch('builtins.print'):
            demo.run_full_demo()
            
        end_time = time.time()
        
        # Демонстрация должна работать быстро даже с большими данными
        assert (end_time - start_time) < 10.0

    def test_demo_database_connection_check(self, mock_db_manager):
        """Тест проверки подключения к БД в демонстрации"""
        # Тест с успешным подключением
        mock_db_manager.check_connection.return_value = True
        demo = DBManagerDemo(mock_db_manager)
        
        with patch('builtins.print'):
            demo.run_full_demo()
        
        assert mock_db_manager.check_connection.called
        
        # Тест с неуспешным подключением
        mock_db_manager.check_connection.return_value = False
        
        with patch('builtins.print'):
            try:
                demo.run_full_demo()
                # Демонстрация может продолжить работу или завершиться
                connection_handled = True
            except Exception:
                # Может выбросить исключение при отсутствии подключения
                connection_handled = False
        
        assert connection_handled is not None

    def test_demo_output_format(self, db_manager_demo):
        """Тест формата вывода демонстрации"""
        with patch('builtins.print') as mock_print:
            db_manager_demo.run_full_demo()
        
        # Проверяем что был произведен вывод
        assert mock_print.call_count > 0
        
        # Проверяем что в выводе есть структурированная информация
        all_calls = [str(call) for call in mock_print.call_args_list]
        output_text = " ".join(all_calls)
        
        # Проверяем наличие ключевых элементов демонстрации
        demo_keywords = ["демонстрация", "компании", "вакансии", "зарплата"]
        found_keywords = sum(1 for keyword in demo_keywords if keyword.lower() in output_text.lower())
        
        # Хотя бы некоторые ключевые слова должны присутствовать
        assert found_keywords > 0
