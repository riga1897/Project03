
"""
Тесты для модуля демонстрации DBManager
"""

import pytest
from unittest.mock import patch, Mock
from src.utils.db_manager_demo import DBManagerDemo


class TestDBManagerDemo:
    """Тесты для класса DBManagerDemo"""

    @pytest.fixture
    def mock_db_manager(self):
        """Фикстура с мок DBManager"""
        mock_manager = Mock()
        mock_manager.get_companies_and_vacancies_count.return_value = [
            {"company_name": "TechCorp", "vacancy_count": 5},
            {"company_name": "DevCompany", "vacancy_count": 3}
        ]
        mock_manager.get_all_vacancies.return_value = [
            {"title": "Python Developer", "company": "TechCorp", "salary": 150000, "url": "http://example.com/1"},
            {"title": "Java Developer", "company": "DevCompany", "salary": 120000, "url": "http://example.com/2"}
        ]
        mock_manager.get_avg_salary.return_value = 135000
        mock_manager.get_vacancies_with_higher_salary.return_value = [
            {"title": "Senior Python Developer", "salary": 180000}
        ]
        mock_manager.get_vacancies_with_keyword.return_value = [
            {"title": "Python Developer", "company": "TechCorp"}
        ]
        return mock_manager

    def test_demo_initialization(self):
        """Тест инициализации демо"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager'):
            demo = DBManagerDemo()
            assert demo is not None

    @patch('builtins.print')
    @patch('builtins.input', return_value='0')
    def test_run_demo_exit(self, mock_input, mock_print, mock_db_manager):
        """Тест запуска демо с немедленным выходом"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            demo.run_demo()
            
            # Проверяем, что демо корректно завершилось
            assert mock_print.called

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['1', '0'])
    def test_show_companies_and_vacancies_count(self, mock_input, mock_print, mock_db_manager):
        """Тест показа количества компаний и вакансий"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            demo.run_demo()
            
            # Проверяем, что метод был вызван
            mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
            
            # Проверяем, что данные были выведены
            assert mock_print.called
            call_args = [str(call) for call in mock_print.call_args_list]
            output_text = " ".join(call_args)
            assert "TechCorp" in output_text or "компани" in output_text.lower()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['2', '0'])
    def test_show_all_vacancies(self, mock_input, mock_print, mock_db_manager):
        """Тест показа всех вакансий"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            demo.run_demo()
            
            # Проверяем, что метод был вызван
            mock_db_manager.get_all_vacancies.assert_called_once()
            
            # Проверяем, что данные были выведены
            assert mock_print.called

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['3', '0'])
    def test_show_avg_salary(self, mock_input, mock_print, mock_db_manager):
        """Тест показа средней зарплаты"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            demo.run_demo()
            
            # Проверяем, что метод был вызван
            mock_db_manager.get_avg_salary.assert_called_once()
            
            # Проверяем, что данные были выведены
            assert mock_print.called
            call_args = [str(call) for call in mock_print.call_args_list]
            output_text = " ".join(call_args)
            assert "135000" in output_text or "средн" in output_text.lower()

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['4', '0'])
    def test_show_vacancies_with_higher_salary(self, mock_input, mock_print, mock_db_manager):
        """Тест показа вакансий с зарплатой выше средней"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            demo.run_demo()
            
            # Проверяем, что метод был вызван
            mock_db_manager.get_vacancies_with_higher_salary.assert_called_once()
            
            # Проверяем, что данные были выведены
            assert mock_print.called

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['5', 'Python', '0'])
    def test_search_vacancies_by_keyword(self, mock_input, mock_print, mock_db_manager):
        """Тест поиска вакансий по ключевому слову"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            demo.run_demo()
            
            # Проверяем, что метод был вызван с правильным аргументом
            mock_db_manager.get_vacancies_with_keyword.assert_called_with('Python')
            
            # Проверяем, что данные были выведены
            assert mock_print.called

    @patch('builtins.print')
    @patch('builtins.input', return_value='invalid')
    def test_invalid_menu_choice(self, mock_input, mock_print, mock_db_manager):
        """Тест обработки неверного выбора меню"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            
            # Тестируем один цикл с неверным вводом
            try:
                demo.run_demo()
            except:
                pass  # Ожидаем, что может быть исключение из-за бесконечного цикла
            
            # Проверяем, что было выведено сообщение об ошибке
            assert mock_print.called

    def test_format_companies_data(self, mock_db_manager):
        """Тест форматирования данных компаний"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            
            companies_data = [
                {"company_name": "TechCorp", "vacancy_count": 5},
                {"company_name": "DevCompany", "vacancy_count": 3}
            ]
            
            # Вызываем приватный метод через публичный интерфейс
            formatted = demo._format_companies_display(companies_data)
            
            assert isinstance(formatted, str)
            assert "TechCorp" in formatted
            assert "5" in formatted

    def test_format_vacancies_data(self, mock_db_manager):
        """Тест форматирования данных вакансий"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            
            vacancies_data = [
                {"title": "Python Developer", "company": "TechCorp", "salary": 150000, "url": "http://example.com/1"}
            ]
            
            # Вызываем приватный метод
            formatted = demo._format_vacancies_display(vacancies_data)
            
            assert isinstance(formatted, str)
            assert "Python Developer" in formatted
            assert "TechCorp" in formatted

    @patch('src.storage.db_manager.DBManager')
    def test_get_db_manager_creation(self, mock_db_manager_class):
        """Тест создания экземпляра DBManager"""
        mock_instance = Mock()
        mock_db_manager_class.return_value = mock_instance
        
        demo = DBManagerDemo()
        db_manager = demo._get_db_manager()
        
        assert db_manager is not None
        mock_db_manager_class.assert_called_once()

    @patch('builtins.print')
    def test_display_menu(self, mock_print):
        """Тест отображения меню"""
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager'):
            demo = DBManagerDemo()
            demo._display_menu()
            
            # Проверяем, что меню было выведено
            assert mock_print.called
            call_args = [str(call) for call in mock_print.call_args_list]
            output_text = " ".join(call_args)
            assert "компани" in output_text.lower() or "вакан" in output_text.lower()

    @patch('builtins.print')
    def test_error_handling_db_connection(self, mock_print, mock_db_manager):
        """Тест обработки ошибок подключения к БД"""
        # Настраиваем мок для генерации исключения
        mock_db_manager.get_companies_and_vacancies_count.side_effect = Exception("DB Connection Error")
        
        with patch('src.utils.db_manager_demo.DBManagerDemo._get_db_manager', return_value=mock_db_manager):
            demo = DBManagerDemo()
            
            # Тестируем обработку ошибки
            result = demo._safe_db_operation(lambda: mock_db_manager.get_companies_and_vacancies_count())
            
            assert result is None  # Ошибка должна быть обработана
