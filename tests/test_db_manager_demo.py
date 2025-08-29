"""
Тесты для модуля демонстрации DBManager
"""

from unittest.mock import Mock, patch

import pytest

from src.utils.db_manager_demo import DBManagerDemo


class TestDBManagerDemo:
    """Тесты для класса DBManagerDemo"""

    @pytest.fixture
    def mock_db_manager(self):
        """Фикстура с мок DBManager"""
        mock_manager = Mock()
        mock_manager.get_companies_and_vacancies_count.return_value = [("TechCorp", 5), ("DevCompany", 3)]
        mock_manager.get_target_companies_analysis.return_value = [("TechCorp", 5), ("DevCompany", 3)]
        mock_manager.get_all_vacancies.return_value = [
            {
                "title": "Python Developer",
                "company_name": "TechCorp",
                "salary_info": "150000 RUR",
                "url": "http://example.com/1",
            },
            {
                "title": "Java Developer",
                "company_name": "DevCompany",
                "salary_info": "120000 RUR",
                "url": "http://example.com/2",
            },
        ]
        mock_manager.get_avg_salary.return_value = 135000
        mock_manager.get_vacancies_with_higher_salary.return_value = [
            {"title": "Senior Python Developer", "calculated_salary": 180000}
        ]
        mock_manager.get_vacancies_with_keyword.return_value = [
            {"title": "Python Developer", "company_name": "TechCorp"}
        ]
        mock_manager.check_connection.return_value = True
        mock_manager.get_database_stats.return_value = {
            "total_vacancies": 100,
            "total_companies": 15,
            "vacancies_with_salary": 75,
            "latest_vacancy_date": "2024-01-15",
        }
        return mock_manager

    @patch("src.utils.db_manager_demo.DBManager")
    def test_demo_initialization(self, mock_db_manager_class):
        """Тест инициализации демо"""
        mock_instance = Mock()
        mock_db_manager_class.return_value = mock_instance

        demo = DBManagerDemo()
        assert demo.db_manager is not None

    @patch("builtins.print")
    def test_run_full_demo(self, mock_print, mock_db_manager):
        """Тест запуска полной демонстрации"""
        demo = DBManagerDemo(db_manager=mock_db_manager)
        demo.run_full_demo()

        # Проверяем, что print был вызван (демонстрация запущена)
        assert mock_print.called

    @patch("src.utils.db_manager_demo.DBManager")
    def test_get_db_manager_creation(self, mock_db_manager_class):
        """Тест создания экземпляра DBManager"""
        mock_instance = Mock()
        mock_db_manager_class.return_value = mock_instance

        demo = DBManagerDemo()

        assert demo.db_manager is not None
        mock_db_manager_class.assert_called_once()

    @patch("builtins.print")
    def test_display_database_stats(self, mock_print, mock_db_manager):
        """Тест отображения статистики базы данных"""
        demo = DBManagerDemo(db_manager=mock_db_manager)
        demo._demo_database_stats()

        # Проверяем, что статистика была выведена
        assert mock_print.called
