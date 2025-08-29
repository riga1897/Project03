"""
Тесты для форматировщика вакансий

Содержит тесты для проверки корректности форматирования
информации о вакансиях для отображения.
"""

import pytest
from unittest.mock import Mock
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestVacancyFormatter:
    """Тесты для класса VacancyFormatter"""

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура для тестовой вакансии"""
        # Создаем Mock объект для Vacancy, так как оригинальная модель может быть сложной
        # и не все поля могут быть необходимы для этих тестов.
        # Если Vacancy является простой dataclass или Pydantic моделью,
        # можно создать экземпляр напрямую.
        mock_vacancy = Mock(spec=Vacancy)
        mock_vacancy.title = "Python Developer"
        mock_vacancy.url = "https://test.com/vacancy/12345"
        mock_vacancy.employer = {"name": "Test Company"}
        mock_vacancy.salary = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }
        mock_vacancy.experience = "От 1 года до 3 лет"
        mock_vacancy.employment = "Полная занятость"
        mock_vacancy.schedule = "Полный день"
        mock_vacancy.source = "hh.ru"
        mock_vacancy.vacancy_id = "12345"
        mock_vacancy.description = "Разработка на Python с использованием Django."
        mock_vacancy.responsibilities = "Разработка веб-приложений."
        mock_vacancy.requirements = "Знание Python, Django."
        mock_vacancy.published_at = "2024-01-15T10:00:00"
        return mock_vacancy

    def test_initialization(self):
        """Тест инициализации форматировщика"""
        formatter = VacancyFormatter()
        assert formatter is not None

    def test_format_vacancy_info(self, sample_vacancy):
        """Тест форматирования полной информации о вакансии"""
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(sample_vacancy, 1)

        assert isinstance(result, str)
        assert "Python Developer" in result
        assert "12345" in result
        assert "Test Company" in result
        assert "100 000 - 150 000 руб." in result # Проверяем формат зарплаты
        assert "От 1 года до 3 лет" in result # Проверяем опыт

    def test_format_vacancy_info_without_number(self, sample_vacancy):
        """Тест форматирования без номера"""
        formatter = VacancyFormatter()
        result = formatter.format_vacancy_info(sample_vacancy)

        assert isinstance(result, str)
        assert "Python Developer" in result
        assert "1." not in result  # Номер не должен быть включен

    def test_format_salary_dict(self):
        """Тест форматирования зарплаты из словаря"""
        formatter = VacancyFormatter()

        salary_dict = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR"
        }

        result = formatter.format_salary(salary_dict)
        assert "от 100 000 до 150 000 руб." in result

    def test_format_salary_from_only(self):
        """Тест форматирования зарплаты только с минимумом"""
        formatter = VacancyFormatter()

        salary_dict = {
            "from": 100000,
            "currency": "RUR"
        }

        result = formatter.format_salary(salary_dict)
        assert "от 100 000 руб." in result

    def test_format_salary_to_only(self):
        """Тест форматирования зарплаты только с максимумом"""
        formatter = VacancyFormatter()

        salary_dict = {
            "to": 150000,
            "currency": "RUR"
        }

        result = formatter.format_salary(salary_dict)
        assert "до 150 000 руб." in result

    def test_format_salary_none(self):
        """Тест форматирования отсутствующей зарплаты"""
        formatter = VacancyFormatter()
        result = formatter.format_salary(None)
        assert result == "Не указана"

    def test_format_currency(self):
        """Тест форматирования валют"""
        formatter = VacancyFormatter()

        assert formatter.format_currency("RUR") == "руб."
        assert formatter.format_currency("USD") == "долл."
        assert formatter.format_currency("EUR") == "евро"
        assert formatter.format_currency("UNKNOWN") == "UNKNOWN"

    def test_format_text_normal(self):
        """Тест форматирования обычного текста"""
        formatter = VacancyFormatter()
        text = "Это обычный текст"
        result = formatter.format_text(text, 50)
        assert result == text

    def test_format_text_long(self):
        """Тест форматирования длинного текста"""
        formatter = VacancyFormatter()
        long_text = "Это очень длинный текст " * 10
        result = formatter.format_text(long_text, 50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")

    def test_format_text_with_html(self):
        """Тест форматирования текста с HTML тегами"""
        formatter = VacancyFormatter()
        html_text = "<p>Текст с <strong>HTML</strong> тегами</p>"
        result = formatter.format_text(html_text)
        assert "<p>" not in result
        assert "<strong>" not in result
        assert "Текст с HTML тегами" in result

    def test_clean_html_tags(self):
        """Тест очистки HTML тегов"""
        formatter = VacancyFormatter()
        html_text = "<div><p>Текст</p><br/><span>еще текст</span></div>"
        result = formatter.clean_html_tags(html_text)
        assert "<" not in result
        assert ">" not in result
        assert "Текст еще текст" in result

    def test_format_number(self):
        """Тест форматирования чисел"""
        formatter = VacancyFormatter()

        assert formatter.format_number(1000) == "1 000"
        assert formatter.format_number(123456) == "123 456"
        assert formatter.format_number(1000000) == "1 000 000"

    def test_format_experience(self):
        """Тест форматирования опыта работы"""
        formatter = VacancyFormatter()

        assert formatter.format_experience("От 1 года до 3 лет") == "От 1 года до 3 лет"
        assert formatter.format_experience("") == "Не указан"
        assert formatter.format_experience(None) == "Не указан"

    def test_format_company_name_dict(self):
        """Тест форматирования названия компании из словаря"""
        formatter = VacancyFormatter()
        company = {"name": "Test Company"}
        result = formatter.format_company_name(company)
        assert result == "Test Company"

    def test_format_company_name_string(self):
        """Тест форматирования названия компании из строки"""
        formatter = VacancyFormatter()
        result = formatter.format_company_name("String Company")
        assert result == "String Company"

    def test_format_company_name_none(self):
        """Тест форматирования отсутствующего названия компании"""
        formatter = VacancyFormatter()
        result = formatter.format_company_name(None)
        assert result == "Не указана"

    def test_format_vacancy_brief(self, sample_vacancy):
        """Тест краткого форматирования вакансии"""
        result = VacancyFormatter.format_vacancy_brief(sample_vacancy, 1)

        assert isinstance(result, str)
        assert "Python Developer" in result
        assert "|" in result  # Разделители должны быть

    def test_display_vacancy_info(self, sample_vacancy, capsys):
        """Тест статического метода отображения"""
        # Этот тест проверяет, что метод не вызывает исключений
        VacancyFormatter.display_vacancy_info(sample_vacancy, 1)
        captured = capsys.readouterr() # Читаем вывод, чтобы убедиться, что он не пустой или соответствует ожиданиям

        assert "1. Python Developer" in captured.out
        assert "Test Company" in captured.out
        assert "100 000 - 150 000 руб." in captured.out