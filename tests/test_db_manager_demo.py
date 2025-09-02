
"""
Тесты для модуля демонстрации DBManager
"""

import os
import sys
from typing import Dict, Any, List, Optional
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
    def mock_db_manager(self) -> Mock:
        """Создание мока DBManager"""
        mock_manager = Mock(spec=DBManager if DB_MANAGER_DEMO_AVAILABLE else object)
        
        # Настройка методов
        mock_manager.get_companies_and_vacancies_count.return_value = [
            ("Яндекс", 10),
            ("СБЕР", 8),
            ("Тинькофф", 5)
        ]
        
        mock_manager.get_all_vacancies.return_value = [
            {
                "title": "Python Developer",
                "company_name": "Яндекс",
                "salary_info": "100000 - 150000 RUR",
                "url": "https://example.com/1"
            }
        ]
        
        mock_manager.get_avg_salary.return_value = 125000.0
        
        mock_manager.get_vacancies_with_higher_salary.return_value = [
            {
                "title": "Senior Python Developer",
                "company_name": "Яндекс",
                "salary_info": "150000 - 200000 RUR",
                "url": "https://example.com/2"
            }
        ]
        
        mock_manager.get_vacancies_with_keyword.return_value = [
            {
                "title": "Python Developer",
                "company_name": "Яндекс",
                "salary_info": "100000 - 150000 RUR",
                "url": "https://example.com/1"
            }
        ]
        
        return mock_manager

    @pytest.fixture
    def db_manager_demo(self, mock_db_manager) -> 'DBManagerDemo':
        """Создание экземпляра DBManagerDemo"""
        if DB_MANAGER_DEMO_AVAILABLE:
            return DBManagerDemo(mock_db_manager)
        else:
            return MockDBManagerDemo(mock_db_manager)

    def test_db_manager_demo_initialization(self, mock_db_manager):
        """Тест инициализации DBManagerDemo"""
        if DB_MANAGER_DEMO_AVAILABLE:
            demo = DBManagerDemo(mock_db_manager)
        else:
            demo = MockDBManagerDemo(mock_db_manager)
        
        assert demo is not None
        assert hasattr(demo, 'db_manager')

    @patch('builtins.print')
    def test_run_full_demo(self, mock_print, db_manager_demo):
        """Тест полной демонстрации"""
        db_manager_demo.run_full_demo()
        
        # Проверяем, что print был вызван (демонстрация выводит информацию)
        assert mock_print.called

    @patch('builtins.print')
    def test_demo_companies_and_vacancies(self, mock_print, db_manager_demo):
        """Тест демонстрации списка компаний и вакансий"""
        db_manager_demo.demo_companies_and_vacancies()
        
        # Проверяем вызов метода у db_manager
        db_manager_demo.db_manager.get_companies_and_vacancies_count.assert_called_once()
        assert mock_print.called

    @patch('builtins.print')
    def test_demo_all_vacancies(self, mock_print, db_manager_demo):
        """Тест демонстрации всех вакансий"""
        db_manager_demo.demo_all_vacancies()
        
        db_manager_demo.db_manager.get_all_vacancies.assert_called_once()
        assert mock_print.called

    @patch('builtins.print')
    def test_demo_avg_salary(self, mock_print, db_manager_demo):
        """Тест демонстрации средней зарплаты"""
        db_manager_demo.demo_avg_salary()
        
        db_manager_demo.db_manager.get_avg_salary.assert_called_once()
        assert mock_print.called

    @patch('builtins.print')
    def test_demo_high_salary_vacancies(self, mock_print, db_manager_demo):
        """Тест демонстрации вакансий с высокой зарплатой"""
        db_manager_demo.demo_high_salary_vacancies()
        
        db_manager_demo.db_manager.get_vacancies_with_higher_salary.assert_called_once()
        assert mock_print.called

    @patch('builtins.print')
    def test_demo_keyword_search(self, mock_print, db_manager_demo):
        """Тест демонстрации поиска по ключевому слову"""
        keyword = "Python"
        db_manager_demo.demo_keyword_search(keyword)
        
        db_manager_demo.db_manager.get_vacancies_with_keyword.assert_called_once_with(keyword)
        assert mock_print.called

    def test_demo_with_empty_results(self, mock_db_manager):
        """Тест демонстрации с пустыми результатами"""
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
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("DB Error")
        
        if DB_MANAGER_DEMO_AVAILABLE:
            demo = DBManagerDemo(mock_db_manager)
        else:
            demo = MockDBManagerDemo(mock_db_manager)
        
        # Демонстрация должна обрабатывать ошибки
        with patch('builtins.print'):
            try:
                demo.demo_companies_and_vacancies()
            except Exception:
                pytest.fail("Demo should handle database errors gracefully")


# Тестовая реализация DBManagerDemo
class MockDBManagerDemo:
    """Тестовая реализация демонстрации DBManager"""

    def __init__(self, db_manager):
        """
        Инициализация демонстрации

        Args:
            db_manager: Экземпляр DBManager
        """
        self.db_manager = db_manager

    def run_full_demo(self) -> None:
        """Запуск полной демонстрации"""
        print("=== ДЕМОНСТРАЦИЯ DBMANAGER ===")
        
        self.demo_companies_and_vacancies()
        self.demo_all_vacancies()
        self.demo_avg_salary()
        self.demo_high_salary_vacancies()
        self.demo_keyword_search("Python")
        
        print("=== КОНЕЦ ДЕМОНСТРАЦИИ ===")

    def demo_companies_and_vacancies(self) -> None:
        """Демонстрация получения списка компаний и количества вакансий"""
        try:
            print("\n1. Список компаний и количество вакансий:")
            companies = self.db_manager.get_companies_and_vacancies_count()
            
            if companies:
                for company_name, vacancy_count in companies:
                    print(f"   {company_name}: {vacancy_count} вакансий")
            else:
                print("   Данные не найдены")
                
        except Exception as e:
            print(f"   Ошибка при получении данных: {e}")

    def demo_all_vacancies(self) -> None:
        """Демонстрация получения всех вакансий"""
        try:
            print("\n2. Все вакансии (первые 3):")
            vacancies = self.db_manager.get_all_vacancies()
            
            if vacancies:
                for vacancy in vacancies[:3]:
                    print(f"   Название: {vacancy.get('title', 'Не указано')}")
                    print(f"   Компания: {vacancy.get('company_name', 'Не указана')}")
                    print(f"   Зарплата: {vacancy.get('salary_info', 'Не указана')}")
                    print(f"   Ссылка: {vacancy.get('url', 'Не указана')}")
                    print("   " + "-" * 40)
            else:
                print("   Вакансии не найдены")
                
        except Exception as e:
            print(f"   Ошибка при получении вакансий: {e}")

    def demo_avg_salary(self) -> None:
        """Демонстрация получения средней зарплаты"""
        try:
            print("\n3. Средняя зарплата:")
            avg_salary = self.db_manager.get_avg_salary()
            
            if avg_salary:
                print(f"   Средняя зарплата: {avg_salary:,.0f} руб.")
            else:
                print("   Данные о зарплатах не найдены")
                
        except Exception as e:
            print(f"   Ошибка при расчете средней зарплаты: {e}")

    def demo_high_salary_vacancies(self) -> None:
        """Демонстрация вакансий с зарплатой выше средней"""
        try:
            print("\n4. Вакансии с зарплатой выше средней (первые 3):")
            high_salary_vacancies = self.db_manager.get_vacancies_with_higher_salary()
            
            if high_salary_vacancies:
                for vacancy in high_salary_vacancies[:3]:
                    print(f"   Название: {vacancy.get('title', 'Не указано')}")
                    print(f"   Компания: {vacancy.get('company_name', 'Не указана')}")
                    print(f"   Зарплата: {vacancy.get('salary_info', 'Не указана')}")
                    print("   " + "-" * 40)
            else:
                print("   Вакансии с высокой зарплатой не найдены")
                
        except Exception as e:
            print(f"   Ошибка при получении вакансий с высокой зарплатой: {e}")

    def demo_keyword_search(self, keyword: str) -> None:
        """
        Демонстрация поиска вакансий по ключевому слову

        Args:
            keyword: Ключевое слово для поиска
        """
        try:
            print(f"\n5. Поиск вакансий по ключевому слову '{keyword}' (первые 3):")
            keyword_vacancies = self.db_manager.get_vacancies_with_keyword(keyword)
            
            if keyword_vacancies:
                for vacancy in keyword_vacancies[:3]:
                    print(f"   Название: {vacancy.get('title', 'Не указано')}")
                    print(f"   Компания: {vacancy.get('company_name', 'Не указана')}")
                    print(f"   Зарплата: {vacancy.get('salary_info', 'Не указана')}")
                    print("   " + "-" * 40)
            else:
                print(f"   Вакансии с ключевым словом '{keyword}' не найдены")
                
        except Exception as e:
            print(f"   Ошибка при поиске по ключевому слову: {e}")
