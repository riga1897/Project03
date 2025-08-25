
"""
Тесты для модуля форматирования вакансий
"""

import pytest
from unittest.mock import Mock
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy
from src.utils.salary import Salary


class TestVacancyFormatter:
    """Тесты для класса VacancyFormatter"""

    @pytest.fixture
    def sample_salary(self):
        """Фикстура для тестовой зарплаты"""
        return Salary({
            'from': 100000,
            'to': 150000,
            'currency': 'RUR'
        })

    @pytest.fixture
    def sample_vacancy(self, sample_salary):
        """Фикстура для тестовой вакансии"""
        return Vacancy(
            title="Python Developer",
            url="https://test.com/vacancy/1",
            salary={'from': 100000, 'to': 150000, 'currency': 'RUR'},
            description="Разработка на Python",
            requirements="Знание Python, Django",
            responsibilities="Разработка веб-приложений",
            experience="От 3 лет",
            employment="Полная занятость",
            schedule="Полный день",
            employer={'name': 'Test Company'},
            vacancy_id="test_1",
            published_at="2024-01-15T10:00:00",
            source="hh.ru"
        )

    def test_format_vacancy_brief(self, sample_vacancy):
        """Тест краткого форматирования вакансии"""
        result = VacancyFormatter.format_vacancy_brief(sample_vacancy, 1)
        
        assert "1. Python Developer" in result
        assert "Test Company" in result
        assert "100,000 - 150,000 ₽" in result
        assert "https://test.com/vacancy/1" in result

    def test_format_vacancy_brief_no_number(self, sample_vacancy):
        """Тест краткого форматирования без номера"""
        result = VacancyFormatter.format_vacancy_brief(sample_vacancy)
        
        assert "Python Developer" in result
        assert not result.startswith("1.")

    def test_format_vacancy_brief_no_salary(self, sample_vacancy):
        """Тест краткого форматирования без зарплаты"""
        sample_vacancy.salary = None
        result = VacancyFormatter.format_vacancy_brief(sample_vacancy, 1)
        
        assert "Зарплата не указана" in result

    def test_format_vacancy_brief_partial_salary(self, sample_vacancy):
        """Тест краткого форматирования с частичной зарплатой"""
        # Только минимальная зарплата
        sample_vacancy.salary = Salary(100000, None, "RUR")
        result = VacancyFormatter.format_vacancy_brief(sample_vacancy, 1)
        assert "от 100,000 ₽" in result

        # Только максимальная зарплата
        sample_vacancy.salary = Salary(None, 150000, "RUR")
        result = VacancyFormatter.format_vacancy_brief(sample_vacancy, 1)
        assert "до 150,000 ₽" in result

    def test_format_vacancy_info_with_dict(self):
        """Тест форматирования информации о вакансии из словаря"""
        vacancy_dict = {
            'vacancy_id': 'test_1',
            'title': 'Python Developer',
            'url': 'https://test.com/vacancy/1',
            'employer': {'name': 'Test Company'},
            'salary': {'from': 100000, 'to': 150000, 'currency': 'RUR'},
            'experience': 'От 3 лет',
            'employment': 'Полная занятость',
            'source': 'hh.ru',
            'description': 'Разработка на Python'
        }

        result = VacancyFormatter.format_vacancy_info(vacancy_dict, 1)

        assert "1." in result
        assert "ID: test_1" in result
        assert "Название: Python Developer" in result
        assert "Компания: Test Company" in result
        assert "Зарплата: от 100000 до 150000 RUR" in result

    def test_format_vacancy_info_with_object(self, sample_vacancy):
        """Тест форматирования информации о вакансии из объекта"""
        result = VacancyFormatter.format_vacancy_info(sample_vacancy, 1)

        assert "1." in result
        assert "ID: test_1" in result
        assert "Название: Python Developer" in result
        assert "Компания: Test Company" in result

    def test_display_vacancy_info(self, sample_vacancy, capsys):
        """Тест отображения информации о вакансии"""
        VacancyFormatter.display_vacancy_info(sample_vacancy, 1)
        captured = capsys.readouterr()

        assert "1." in captured.out
        assert "Python Developer" in captured.out
        assert "Test Company" in captured.out

    def test_format_salary_dict(self):
        """Тест форматирования зарплаты из словаря"""
        salary_dict = {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        result = VacancyFormatter._format_salary_dict(salary_dict)
        assert result == "от 100000 до 150000 RUR"

        # Только минимальная
        salary_dict = {'from': 100000, 'currency': 'RUR'}
        result = VacancyFormatter._format_salary_dict(salary_dict)
        assert result == "от 100000 RUR"

        # Только максимальная
        salary_dict = {'to': 150000, 'currency': 'RUR'}
        result = VacancyFormatter._format_salary_dict(salary_dict)
        assert result == "до 150000 RUR"

        # Пустой словарь
        result = VacancyFormatter._format_salary_dict({})
        assert result == "Зарплата не указана"

    def test_format_company_info(self):
        """Тест форматирования информации о компании"""
        # Словарь с названием
        employer = {'name': 'Test Company'}
        result = VacancyFormatter.format_company_info(employer)
        assert result == "Test Company"

        # Строка
        result = VacancyFormatter.format_company_info("Test Company")
        assert result == "Test Company"

        # Пустое значение
        result = VacancyFormatter.format_company_info(None)
        assert result == "Не указана"

        # Пустой словарь
        result = VacancyFormatter.format_company_info({})
        assert result == "Не указана"

    def test_extract_company_name(self):
        """Тест извлечения названия компании"""
        # Из атрибута employer (словарь)
        vacancy = Mock()
        vacancy.employer = {'name': 'Test Company'}
        result = VacancyFormatter._extract_company_name(vacancy)
        assert result == "Test Company"

        # Из атрибута employer (строка)
        vacancy.employer = "Test Company"
        result = VacancyFormatter._extract_company_name(vacancy)
        assert result == "Test Company"

        # Из атрибута company (fallback)
        vacancy.employer = None
        vacancy.company = "Test Company"
        result = VacancyFormatter._extract_company_name(vacancy)
        assert result == "Test Company"

        # Неизвестная компания
        vacancy.employer = None
        vacancy.company = None
        result = VacancyFormatter._extract_company_name(vacancy)
        assert result == "Не указана"

    def test_extract_salary_info(self):
        """Тест извлечения информации о зарплате"""
        # Объект Salary
        vacancy = Mock()
        vacancy.salary = Mock()
        vacancy.salary.salary_from = 100000
        vacancy.salary.salary_to = 150000
        vacancy.salary.currency = 'RUR'
        
        result = VacancyFormatter._extract_salary_info(vacancy)
        assert "от 100,000" in result and "до 150,000" in result

        # Словарь
        vacancy.salary = {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        result = VacancyFormatter._extract_salary_info(vacancy)
        assert "от 100000 до 150000 RUR" in result

        # Отсутствует
        vacancy.salary = None
        result = VacancyFormatter._extract_salary_info(vacancy)
        assert result == "Не указана"

    def test_extract_description(self):
        """Тест извлечения описания"""
        vacancy = Mock()
        
        # Обычное описание
        vacancy.description = "Разработка на Python с использованием Django"
        result = VacancyFormatter._extract_description(vacancy)
        assert "Разработка на Python" in result

        # HTML-теги
        vacancy.description = "<p>Разработка на <strong>Python</strong></p>"
        result = VacancyFormatter._extract_description(vacancy)
        assert "<p>" not in result and "<strong>" not in result
        assert "Разработка на Python" in result

        # Длинное описание (должно обрезаться)
        long_text = "А" * 200
        vacancy.description = long_text
        result = VacancyFormatter._extract_description(vacancy)
        assert len(result) <= 153  # 150 символов + "..."
        assert result.endswith("...")

        # Пустое описание
        vacancy.description = ""
        result = VacancyFormatter._extract_description(vacancy)
        assert result == "Описание отсутствует"

        # Fallback на detailed_description
        vacancy.description = None
        vacancy.detailed_description = "Детальное описание"
        result = VacancyFormatter._extract_description(vacancy)
        assert "Детальное описание" in result

    def test_extract_responsibilities(self, sample_vacancy):
        """Тест извлечения обязанностей"""
        sample_vacancy.responsibilities = "Разработка веб-приложений"
        result = VacancyFormatter._extract_responsibilities(sample_vacancy)
        assert result == "Разработка веб-приложений"

        sample_vacancy.responsibilities = None
        result = VacancyFormatter._extract_responsibilities(sample_vacancy)
        assert result is None

    def test_extract_requirements(self, sample_vacancy):
        """Тест извлечения требований"""
        sample_vacancy.requirements = "Знание Python, Django"
        result = VacancyFormatter._extract_requirements(sample_vacancy)
        assert result == "Знание Python, Django"

        sample_vacancy.requirements = None
        result = VacancyFormatter._extract_requirements(sample_vacancy)
        assert result is None

    def test_extract_conditions(self, sample_vacancy):
        """Тест извлечения условий"""
        sample_vacancy.schedule = "Полный день"
        result = VacancyFormatter._extract_conditions(sample_vacancy)
        assert "График: Полный день" in result

        sample_vacancy.schedule = None
        result = VacancyFormatter._extract_conditions(sample_vacancy)
        assert result is None

    def test_build_vacancy_lines(self, sample_vacancy):
        """Тест построения строк информации о вакансии"""
        lines = VacancyFormatter._build_vacancy_lines(sample_vacancy, 1)

        # Проверяем наличие основных разделов
        line_text = "\n".join(lines)
        assert "1." in line_text
        assert "ID: test_1" in line_text
        assert "Название: Python Developer" in line_text
        assert "Компания: Test Company" in line_text
        assert "Источник: hh.ru" in line_text
        assert "Ссылка:" in line_text

    def test_build_vacancy_lines_with_api_url(self, sample_vacancy):
        """Тест построения строк с API URL (должен преобразоваться в веб-URL)"""
        sample_vacancy.url = "https://api.hh.ru/vacancies/12345"
        lines = VacancyFormatter._build_vacancy_lines(sample_vacancy, 1)
        
        line_text = "\n".join(lines)
        assert "https://hh.ru/vacancy/12345" in line_text

    def test_format_salary_with_object(self, sample_salary):
        """Тест форматирования зарплаты с объектом Salary"""
        result = VacancyFormatter.format_salary(sample_salary)
        assert result == str(sample_salary)

    def test_format_salary_with_dict(self):
        """Тест форматирования зарплаты со словарем"""
        salary_dict = {'from': 100000, 'to': 150000, 'currency': 'RUR'}
        result = VacancyFormatter.format_salary(salary_dict)
        assert "от 100000 до 150000 RUR" in result

    def test_format_salary_none(self):
        """Тест форматирования пустой зарплаты"""
        result = VacancyFormatter.format_salary(None)
        assert result == "Зарплата не указана"
