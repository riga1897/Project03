"""
Комплексные тесты для модуля ui_helpers
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pytest

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import ui_helpers
# Assuming Vacancy class is available for type hinting and instantiation
# If Vacancy class is not in src.utils, you might need to adjust the import
# For now, assuming it's globally available or from another mockable module
try:
    from src.vacancy import Vacancy
except ImportError:
    # If Vacancy is not importable, create a placeholder for the tests to run
    class Vacancy:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        @classmethod
        def from_dict(cls, data, source):
            return cls(**data)
        def __str__(self):
            return str(self.__dict__)

@pytest.fixture
def sample_vacancies():
    """Предоставляет набор мок-вакансий для тестов."""
    mock_vacancy1 = Mock()
    mock_vacancy1.title = "Python Developer"
    mock_vacancy1.description = "We need a Python developer with experience"
    mock_vacancy1.salary = Mock()
    mock_vacancy1.salary.salary_from = 100000
    mock_vacancy1.salary.salary_to = 150000
    mock_vacancy1.employer = Mock()
    mock_vacancy1.employer.name = "Tech Company A"
    mock_vacancy1.url = "http://example.com/pydev"

    mock_vacancy2 = Mock()
    mock_vacancy2.title = "Java Developer"
    mock_vacancy2.description = "We need a Java developer"
    mock_vacancy2.salary = Mock()
    mock_vacancy2.salary.salary_from = 120000
    mock_vacancy2.salary.salary_to = 180000
    mock_vacancy2.employer = Mock()
    mock_vacancy2.employer.name = "Soft Solutions B"
    mock_vacancy2.url = "http://example.com/javadev"

    mock_vacancy3 = Mock()
    mock_vacancy3.title = "Senior Python Developer"
    mock_vacancy3.description = "Experienced Python developer required"
    mock_vacancy3.salary = Mock()
    mock_vacancy3.salary.salary_from = 180000
    mock_vacancy3.salary.salary_to = 250000
    mock_vacancy3.employer = Mock()
    mock_vacancy3.employer.name = "Global Tech C"
    mock_vacancy3.url = "http://example.com/seniorpydev"

    mock_vacancy4 = Mock()
    mock_vacancy4.title = "Junior Python Developer"
    mock_vacancy4.description = "Entry level Python role"
    mock_vacancy4.salary = Mock()
    mock_vacancy4.salary.salary_from = 70000
    mock_vacancy4.salary.salary_to = 90000
    mock_vacancy4.employer = Mock()
    mock_vacancy4.employer.name = "Startup D"
    mock_vacancy4.url = "http://example.com/juniorpydev"

    return [mock_vacancy1, mock_vacancy2, mock_vacancy3, mock_vacancy4]


class TestUIHelpers:
    """Тесты для функций пользовательского интерфейса"""

    @patch('builtins.input')
    def test_get_user_input_valid_required(self, mock_input):
        """Тест получения валидного обязательного ввода"""
        mock_input.return_value = "test input"
        result = ui_helpers.get_user_input("Enter text: ", required=True)
        assert result == "test input"

    @patch('builtins.input')
    def test_get_user_input_valid_not_required(self, mock_input):
        """Тест получения валидного необязательного ввода"""
        mock_input.return_value = "test input"
        result = ui_helpers.get_user_input("Enter text: ", required=False)
        assert result == "test input"

    @patch('builtins.input')
    def test_get_user_input_empty_not_required(self, mock_input):
        """Тест пустого ввода для необязательного поля"""
        mock_input.return_value = ""
        result = ui_helpers.get_user_input("Enter text: ", required=False)
        assert result is None

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_empty_required_then_valid(self, mock_print, mock_input):
        """Тест пустого ввода для обязательного поля с последующим валидным вводом"""
        mock_input.side_effect = ["", "valid input"]
        result = ui_helpers.get_user_input("Enter text: ", required=True)
        assert result == "valid input"
        mock_print.assert_called_with("Поле не может быть пустым!")

    @patch('builtins.input')
    def test_get_user_input_whitespace_trimmed(self, mock_input):
        """Тест обрезки пробелов во вводе"""
        mock_input.return_value = "  test input  "
        result = ui_helpers.get_user_input("Enter text: ")
        assert result == "test input"

    @patch('builtins.input')
    def test_get_positive_integer_valid(self, mock_input):
        """Тест получения валидного положительного числа"""
        mock_input.return_value = "42"
        result = ui_helpers.get_positive_integer("Enter number: ")
        assert result == 42

    @patch('builtins.input')
    def test_get_positive_integer_with_default(self, mock_input):
        """Тест использования значения по умолчанию"""
        mock_input.return_value = ""
        result = ui_helpers.get_positive_integer("Enter number: ", default=10)
        assert result == 10

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_empty_no_default(self, mock_print, mock_input):
        """Тест пустого ввода без значения по умолчанию"""
        mock_input.return_value = ""
        result = ui_helpers.get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Введите корректное число!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_negative(self, mock_print, mock_input):
        """Тест отрицательного числа"""
        mock_input.return_value = "-5"
        result = ui_helpers.get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Число должно быть положительным!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_zero(self, mock_print, mock_input):
        """Тест нуля"""
        mock_input.return_value = "0"
        result = ui_helpers.get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Число должно быть положительным!")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_positive_integer_invalid_format(self, mock_print, mock_input):
        """Тест неверного формата числа"""
        mock_input.return_value = "abc"
        result = ui_helpers.get_positive_integer("Enter number: ")
        assert result is None
        mock_print.assert_called_with("Введите корректное число!")

    def test_parse_salary_range_valid_range(self):
        """Тест парсинга валидного диапазона зарплат"""
        result = ui_helpers.parse_salary_range("100000 - 150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_valid_range_spaces(self):
        """Тест парсинга диапазона с разным количеством пробелов"""
        result = ui_helpers.parse_salary_range("100000-150000")
        assert result == (100000, 150000)

    def test_parse_salary_range_single_value(self):
        """Тест парсинга одного значения"""
        result = ui_helpers.parse_salary_range("100000")
        assert result is None

    def test_parse_salary_range_invalid_format(self):
        """Тест парсинга неверного формата"""
        result = ui_helpers.parse_salary_range("abc - def")
        assert result is None

    def test_parse_salary_range_empty_string(self):
        """Тест парсинга пустой строки"""
        result = ui_helpers.parse_salary_range("")
        assert result is None

    def test_parse_salary_range_reversed_values(self):
        """Тест парсинга диапазона с перевернутыми значениями"""
        result = ui_helpers.parse_salary_range("150000-100000")
        # Функция должна вернуть корректный диапазон
        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch('builtins.input')
    def test_confirm_action_yes(self, mock_input):
        """Тест подтверждения действия - да"""
        mock_input.return_value = "y"
        result = ui_helpers.confirm_action("Continue?")
        assert result is True

    @patch('builtins.input')
    def test_confirm_action_no(self, mock_input):
        """Тест подтверждения действия - нет"""
        mock_input.return_value = "n"
        result = ui_helpers.confirm_action("Continue?")
        assert result is False

    @patch('builtins.input')
    @patch('builtins.print')
    def test_confirm_action_invalid_then_valid(self, mock_print, mock_input):
        """Тест неверного ввода с последующим валидным"""
        mock_input.side_effect = ["maybe", "y"]
        result = ui_helpers.confirm_action("Continue?")
        assert result is True
        mock_print.assert_called_with("Введите 'y' для да или 'n' для нет.")

    def test_filter_vacancies_by_keyword_basic(self, sample_vacancies):
        """Тест базовой фильтрации по ключевому слову"""
        # Создаем реальные вакансии вместо Mock
        real_vacancies = []
        for i, mock_v in enumerate(sample_vacancies):
            vacancy_data = {
                'id': f'test_{i}',
                'name': f'Python Developer {i}',
                'url': f'https://test.com/{i}',
                'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
                'employer': {'name': f'Company {i}'},
                'area': {'name': 'Москва'},
                'experience': {'name': 'От 1 года до 3 лет'},
                'employment': {'name': 'Полная занятость'},
                'schedule': {'name': 'Полный день'},
                'snippet': {'requirement': 'Python', 'responsibility': 'Development'},
                'published_at': '2025-01-01T00:00:00+0300'
            }
            real_vacancies.append(Vacancy.from_dict(vacancy_data, 'hh'))

        result = ui_helpers.filter_vacancies_by_keyword(real_vacancies, "Python")
        assert isinstance(result, list)
        assert len(result) == 2 # Expecting "Python Developer 0" and "Senior Python Developer 2"


    def test_display_vacancy_info_basic(self):
        """Тест отображения информации о вакансии"""
        # Создаем реальную вакансию для более точного теста
        vacancy_data = {
            'id': 'test_1',
            'name': 'Test Developer',
            'url': 'http://test.com',
            'salary': {'from': 50000, 'to': 70000, 'currency': 'RUR'},
            'employer': {'name': 'Test Company'},
            'area': {'name': 'Санкт-Петербург'},
            'experience': {'name': 'От 1 года до 3 лет'},
            'employment': {'name': 'Полная занятость'},
            'schedule': {'name': 'Полный день'},
            'snippet': {'requirement': 'Good skills', 'responsibility': 'Coding'},
            'published_at': '2025-01-01T00:00:00+0300'
        }
        vacancy = Vacancy.from_dict(vacancy_data, 'hh')

        with patch('builtins.print') as mock_print:
            ui_helpers.display_vacancy_info(vacancy, 1)

        # Проверяем, что print был вызван с ожидаемым форматом
        # Примерные строки, которые должны быть напечатаны
        expected_calls = [
            pytest.call("Вакансия № 1:"),
            pytest.call(f"Название: {vacancy.name}"),
            pytest.call(f"Компания: {vacancy.employer.name}"),
            pytest.call(f"Зарплата: от {vacancy.salary.salary_from} до {vacancy.salary.salary_to} RUR"),
            pytest.call(f"URL: {vacancy.url}")
        ]
        mock_print.assert_has_calls(expected_calls, any_order=True)


    def test_filter_vacancies_by_min_salary_basic(self, sample_vacancies):
        """Тест фильтрации по минимальной зарплате"""
        # Используем реальные вакансии для теста
        real_vacancies = []
        for i, mock_v in enumerate(sample_vacancies):
            vacancy_data = {
                'id': f'test_{i}',
                'name': f'Python Developer {i}',
                'url': f'https://test.com/{i}',
                'salary': {'from': 100000 + i * 30000, 'to': 150000 + i * 50000, 'currency': 'RUR'},
                'employer': {'name': f'Company {i}'},
                'area': {'name': 'Москва'},
                'experience': {'name': 'От 1 года до 3 лет'},
                'employment': {'name': 'Полная занятость'},
                'schedule': {'name': 'Полный день'},
                'snippet': {'requirement': 'Python', 'responsibility': 'Development'},
                'published_at': '2025-01-01T00:00:00+0300'
            }
            real_vacancies.append(Vacancy.from_dict(vacancy_data, 'hh'))

        min_salary_threshold = 120000
        result = ui_helpers.filter_vacancies_by_min_salary(real_vacancies, min_salary_threshold)

        assert isinstance(result, list)
        # Ожидаем вакансии с зарплатой от >= 120000
        # sample_vacancies[0] -> from: 100000 (не проходит)
        # sample_vacancies[1] -> from: 130000 (проходит)
        # sample_vacancies[2] -> from: 160000 (проходит)
        # sample_vacancies[3] -> from: 190000 (проходит)
        assert len(result) == 3
        assert all(v.salary.salary_from >= min_salary_threshold for v in result)


    def test_get_vacancies_with_salary_basic(self, sample_vacancies):
        """Тест получения вакансий с зарплатой"""
        # Используем реальные вакансии для теста
        real_vacancies = []
        for i, mock_v in enumerate(sample_vacancies):
            salary_data = {'from': 100000 + i * 20000, 'to': 150000 + i * 30000, 'currency': 'RUR'} if i % 2 == 0 else None
            vacancy_data = {
                'id': f'test_{i}',
                'name': f'Developer {i}',
                'url': f'https://test.com/{i}',
                'salary': salary_data,
                'employer': {'name': f'Company {i}'},
                'area': {'name': 'Москва'},
                'experience': {'name': 'От 1 года до 3 лет'},
                'employment': {'name': 'Полная занятость'},
                'schedule': {'name': 'Полный день'},
                'snippet': {'requirement': 'Skills', 'responsibility': 'Tasks'},
                'published_at': '2025-01-01T00:00:00+0300'
            }
            real_vacancies.append(Vacancy.from_dict(vacancy_data, 'hh'))

        result = ui_helpers.get_vacancies_with_salary(real_vacancies)

        assert isinstance(result, list)
        # Ожидаем вакансии с не None зарплатой
        # sample_vacancies[0] -> salary: present
        # sample_vacancies[1] -> salary: None
        # sample_vacancies[2] -> salary: present
        # sample_vacancies[3] -> salary: None
        assert len(result) == 2
        assert all(v.salary is not None for v in result)


    def test_sort_vacancies_by_salary_basic(self, sample_vacancies):
        """Тест сортировки вакансий по зарплате"""
        # Используем реальные вакансии для теста
        real_vacancies = []
        for i, mock_v in enumerate(sample_vacancies):
            salary_data = {'from': 100000 + i * 30000, 'to': 150000 + i * 50000, 'currency': 'RUR'}
            vacancy_data = {
                'id': f'test_{i}',
                'name': f'Developer {i}',
                'url': f'https://test.com/{i}',
                'salary': salary_data,
                'employer': {'name': f'Company {i}'},
                'area': {'name': 'Москва'},
                'experience': {'name': 'От 1 года до 3 лет'},
                'employment': {'name': 'Полная занятость'},
                'schedule': {'name': 'Полный день'},
                'snippet': {'requirement': 'Skills', 'responsibility': 'Tasks'},
                'published_at': '2025-01-01T00:00:00+0300'
            }
            real_vacancies.append(Vacancy.from_dict(vacancy_data, 'hh'))

        result = ui_helpers.sort_vacancies_by_salary(real_vacancies)

        assert isinstance(result, list)
        assert len(result) == 4
        # Проверяем, что зарплаты отсортированы по возрастанию
        # sample_vacancies[0] -> from: 100000
        # sample_vacancies[1] -> from: 130000
        # sample_vacancies[2] -> from: 160000
        # sample_vacancies[3] -> from: 190000
        expected_salaries = [100000, 130000, 160000, 190000]
        actual_salaries = [v.salary.salary_from for v in result]
        assert actual_salaries == expected_salaries