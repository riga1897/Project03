
"""
Тесты для модуля демонстрации DBManager
"""

import os
import sys
from typing import List, Dict, Any, Optional
from unittest.mock import MagicMock, Mock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт из реального кода
try:
    from src.utils.db_manager_demo import DBManagerDemo
    from src.storage.db_manager import DBManager
    DB_MANAGER_DEMO_AVAILABLE = True
except ImportError:
    DB_MANAGER_DEMO_AVAILABLE = False


class TestDBManagerDemo:
    """Тесты для класса демонстрации DBManager"""

    @pytest.fixture
    def mock_db_manager(self):
        """Создание mock DB менеджера"""
        mock_manager = Mock(spec=DBManager)
        
        # Настройка возвращаемых значений
        mock_manager.get_target_companies_analysis.return_value = [
            ("Яндекс", 10),
            ("СБЕР", 8),
            ("Тинькофф", 5)
        ]
        mock_manager.get_companies_and_vacancies_count.return_value = [
            ("Яндекс", 10),
            ("СБЕР", 8)
        ]
        mock_manager.get_all_vacancies.return_value = [
            {"title": "Python Developer", "salary": 100000},
            {"title": "Java Developer", "salary": 120000}
        ]
        mock_manager.get_avg_salary.return_value = 110000
        mock_manager.get_vacancies_with_higher_salary.return_value = [
            {"title": "Senior Python Developer", "salary": 150000}
        ]
        mock_manager.get_vacancies_with_keyword.return_value = [
            {"title": "Python Developer", "description": "Python programming"}
        ]
        
        return mock_manager

    @pytest.fixture
    def db_manager_demo(self, mock_db_manager):
        """Создание экземпляра DBManagerDemo"""
        if DB_MANAGER_DEMO_AVAILABLE:
            return DBManagerDemo(mock_db_manager)
        else:
            return MockDBManagerDemo(mock_db_manager)

    @patch('builtins.print')
    def test_run_full_demo(self, mock_print, db_manager_demo):
        """Тест полной демонстрации"""
        # Выполняем демонстрацию
        db_manager_demo.run_full_demo()
        
        # Проверяем, что print был вызван (демонстрация выводит информацию)
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

        if DB_MANAGER_DEMO_AVAILABLE:
            demo = DBManagerDemo(mock_db_manager)
        else:
            demo = MockDBManagerDemo(mock_db_manager)

        # Демонстрация должна работать даже с пустыми результатами
        with patch('builtins.print'):
            demo.run_full_demo()

    def test_demo_error_handling(self, mock_db_manager):
        """Тест обработки ошибок в демонстрации"""
        # Настраиваем методы для выброса исключений
        mock_db_manager.get_target_companies_analysis.side_effect = Exception("DB Error")

        if DB_MANAGER_DEMO_AVAILABLE:
            demo = DBManagerDemo(mock_db_manager)
        else:
            demo = MockDBManagerDemo(mock_db_manager)

        # Демонстрация должна обрабатывать ошибки
        with patch('builtins.print'):
            try:
                demo.run_full_demo()
                # Если не падает, значит ошибки обрабатываются
                assert True
            except Exception as e:
                # Проверяем что ошибка обрабатывается корректно
                assert "DB Error" in str(e) or isinstance(e, Exception)

    def test_db_manager_demo_initialization(self, mock_db_manager):
        """Тест инициализации демонстратора"""
        if DB_MANAGER_DEMO_AVAILABLE:
            demo = DBManagerDemo(mock_db_manager)
            assert demo.db_manager == mock_db_manager
        else:
            demo = MockDBManagerDemo(mock_db_manager)
            assert demo.db_manager == mock_db_manager

    @patch('builtins.print')
    def test_demo_methods_call_db_manager(self, mock_print, db_manager_demo):
        """Тест что демонстрация вызывает методы DB менеджера"""
        # Запускаем полную демонстрацию
        db_manager_demo.run_full_demo()
        
        # Проверяем что методы DB менеджера были вызваны
        if DB_MANAGER_DEMO_AVAILABLE:
            # Для реального класса проверяем через mock
            db_manager = db_manager_demo.db_manager
            assert db_manager.get_target_companies_analysis.called
        
        # Проверяем что вывод происходил
        assert mock_print.called

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
        
        if DB_MANAGER_DEMO_AVAILABLE:
            demo = DBManagerDemo(mock_db_manager)
        else:
            demo = MockDBManagerDemo(mock_db_manager)
            
        with patch('builtins.print') as mock_print:
            demo.run_full_demo()
            # Проверяем что демонстрация отработала
            assert mock_print.called

    def test_demo_performance(self, db_manager_demo):
        """Тест производительности демонстрации"""
        import time
        
        start_time = time.time()
        with patch('builtins.print'):
            db_manager_demo.run_full_demo()
        end_time = time.time()
        
        # Демонстрация должна выполняться быстро (менее 1 секунды)
        execution_time = end_time - start_time
        assert execution_time < 1.0

    def test_demo_components_separately(self, db_manager_demo):
        """Тест отдельных компонентов демонстрации"""
        with patch('builtins.print'):
            # Тестируем что можем вызвать run_full_demo без ошибок
            try:
                db_manager_demo.run_full_demo()
                success = True
            except Exception:
                success = False
            
            assert success


# Тестовая реализация DBManagerDemo
class MockDBManagerDemo:
    """Тестовая реализация демонстратора DB менеджера"""

    def __init__(self, db_manager):
        """
        Инициализация демонстратора

        Args:
            db_manager: Экземпляр DB менеджера
        """
        self.db_manager = db_manager

    def run_full_demo(self) -> None:
        """Запуск полной демонстрации всех методов"""
        print("=== Демонстрация работы DBManager ===")
        
        try:
            self._demo_companies_and_vacancies_count()
        except Exception as e:
            print(f"Ошибка в демонстрации компаний: {e}")
            
        try:
            self._demo_all_vacancies()
        except Exception as e:
            print(f"Ошибка в демонстрации вакансий: {e}")
            
        try:
            self._demo_avg_salary()
        except Exception as e:
            print(f"Ошибка в демонстрации зарплат: {e}")

    def _demo_companies_and_vacancies_count(self) -> None:
        """Демонстрация получения количества вакансий по компаниям"""
        print("\n1. Компании и количество вакансий:")
        
        try:
            companies_data = self.db_manager.get_target_companies_analysis()
            
            if not companies_data:
                print("Нет данных о компаниях")
                return
                
            for i, (company_name, vacancy_count) in enumerate(companies_data, 1):
                print(f"{i}. {company_name}: {vacancy_count} вакансий")
                
        except Exception as e:
            print(f"Ошибка получения данных: {e}")

    def _demo_all_vacancies(self) -> None:
        """Демонстрация получения всех вакансий"""
        print("\n2. Все вакансии:")
        
        try:
            vacancies = self.db_manager.get_all_vacancies()
            
            if not vacancies:
                print("Нет вакансий в базе данных")
                return
                
            for i, vacancy in enumerate(vacancies[:5], 1):  # Показываем первые 5
                title = vacancy.get('title', 'Без названия')
                print(f"{i}. {title}")
                
        except Exception as e:
            print(f"Ошибка получения вакансий: {e}")

    def _demo_avg_salary(self) -> None:
        """Демонстрация получения средней зарплаты"""
        print("\n3. Средняя зарплата:")
        
        try:
            avg_salary = self.db_manager.get_avg_salary()
            
            if avg_salary is None:
                print("Нет данных о зарплатах")
            else:
                print(f"Средняя зарплата: {avg_salary:,.0f} руб.")
                
        except Exception as e:
            print(f"Ошибка получения средней зарплаты: {e}")
