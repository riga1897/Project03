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
        """Тест форматирования названия компании None"""
        formatter = VacancyFormatter()
        result = formatter.format_company_name(None)
        assert result == "Не указана"

    def test_format_company_name_empty_dict(self):
        """Тест форматирования названия компании с пустым dict"""
        formatter = VacancyFormatter()
        company = {"name": ""}
        result = formatter.format_company_name(company)
        assert result == "Не указана"

    def test_extract_company_name_various_formats(self):
        """Тест извлечения названия компании из различных форматов"""
        formatter = VacancyFormatter()
        
        # Mock vacancy объекты для тестирования
        class MockVacancy:
            def __init__(self, employer):
                self.employer = employer
        
        # Тест с dict employer
        vacancy1 = MockVacancy({"name": "Dict Company"})
        assert formatter._extract_company_name(vacancy1) == "Dict Company"
        
        # Тест со string employer
        vacancy2 = MockVacancy("String Company")
        assert formatter._extract_company_name(vacancy2) == "String Company"
        
        # Тест с None employer
        vacancy3 = MockVacancy(None)
        assert formatter._extract_company_name(vacancy3) == "Не указана"
        
        # Тест с пустым string employer
        vacancy4 = MockVacancy("")
        assert formatter._extract_company_name(vacancy4) == "Не указана"

    def test_extract_salary_info(self):
        """Тест извлечения информации о зарплате"""
        formatter = VacancyFormatter()
        
        class MockVacancy:
            def __init__(self, salary):
                self.salary = salary
        
        # Тест с зарплатой
        salary_dict = {"from": 100000, "to": 150000, "currency": "RUR"}
        vacancy1 = MockVacancy(salary_dict)
        result = formatter._extract_salary_info(vacancy1)
        assert "от 100" in result and "до 150" in result
        
        # Тест без зарплаты
        vacancy2 = MockVacancy(None)
        result = formatter._extract_salary_info(vacancy2)
        assert result is None

    def test_extract_responsibilities(self):
        """Тест извлечения обязанностей"""
        formatter = VacancyFormatter()
        
        class MockVacancy:
            def __init__(self, responsibilities):
                self.responsibilities = responsibilities
        
        vacancy = MockVacancy("Python development")
        result = formatter._extract_responsibilities(vacancy)
        assert result == "Python development"

    def test_extract_requirements(self):
        """Тест извлечения требований"""
        formatter = VacancyFormatter()
        
        class MockVacancy:
            def __init__(self, requirements):
                self.requirements = requirements
        
        vacancy = MockVacancy("Python, Django")
        result = formatter._extract_requirements(vacancy)
        assert result == "Python, Django"

    def test_extract_conditions(self):
        """Тест извлечения условий"""
        formatter = VacancyFormatter()
        
        class MockVacancy:
            def __init__(self, conditions=None, schedule=None):
                self.conditions = conditions
                self.schedule = schedule
        
        # Тест с conditions
        vacancy1 = MockVacancy(conditions="Remote work")
        result = formatter._extract_conditions(vacancy1)
        assert result == "Remote work"
        
        # Тест без conditions, но с schedule
        vacancy2 = MockVacancy(schedule="Full time")
        result = formatter._extract_conditions(vacancy2)
        assert "График: Full time" in result
        
        # Тест без conditions и schedule
        vacancy3 = MockVacancy()
        result = formatter._extract_conditions(vacancy3)
        assert result is None

    def test_format_salary_dict_various_combinations(self):
        """Тест форматирования различных комбинаций зарплаты"""
        formatter = VacancyFormatter()
        
        # Только from
        salary1 = {"from": 80000, "currency": "RUR"}
        result = formatter._format_salary_dict(salary1)
        assert "от 80" in result and "руб." in result
        
        # Только to
        salary2 = {"to": 120000, "currency": "USD"}
        result = formatter._format_salary_dict(salary2)
        assert "до 120" in result and "долл." in result
        
        # Без from и to
        salary3 = {"currency": "EUR"}
        result = formatter._format_salary_dict(salary3)
        assert result == "Не указана"
        
        # Пустой dict
        result = formatter._format_salary_dict({})
        assert result == "Не указана"
        
        # None
        result = formatter._format_salary_dict(None)
        assert result == "Не указана"

    def test_format_date_various_formats(self):
        """Тест форматирования различных форматов дат"""
        formatter = VacancyFormatter()
        
        # ISO формат
        iso_date = "2024-01-15T10:30:00+03:00"
        result = formatter.format_date(iso_date)
        assert "15.01.2024" in result
        
        # Только дата
        date_only = "2024-12-31"
        result = formatter.format_date(date_only)
        assert "31.12.2024" in result
        
        # Некорректный формат
        invalid_date = "invalid-date"
        result = formatter.format_date(invalid_date)
        assert result == "invalid-date"
        
        # Пустая строка
        result = formatter.format_date("")
        assert result == "Не указано"

    def test_build_vacancy_lines_complete(self):
        """Тест полного построения строк вакансии"""
        formatter = VacancyFormatter()
        
        class MockVacancy:
            def __init__(self):
                self.vacancy_id = "123456"
                self.title = "Senior Python Developer"
                self.employer = {"name": "TechCorp"}
                self.salary = {"from": 150000, "to": 250000, "currency": "RUR"}
                self.experience = "От 3 до 6 лет"
                self.employment = "Полная занятость"
                self.source = "hh.ru"
                self.url = "https://hh.ru/vacancy/123456"
                self.responsibilities = "Разработка на Python"
                self.requirements = "Python, Django, PostgreSQL"
                self.conditions = "Удаленная работа"
        
        vacancy = MockVacancy()
        lines = formatter._build_vacancy_lines(vacancy, 1)
        
        # Проверяем наличие всех основных полей
        text = '\n'.join(lines)
        assert "1." in text
        assert "ID: 123456" in text
        assert "Senior Python Developer" in text
        assert "TechCorp" in text
        assert "150" in text and "250" in text  # зарплата
        assert "От 3 до 6 лет" in text
        assert "Полная занятость" in text
        assert "hh.ru" in text
        assert "https://hh.ru/vacancy/123456" in text
        assert "Разработка на Python" in text
        assert "Python, Django, PostgreSQL" in text
        assert "Удаленная работа" in text

    def test_format_vacancy_brief_complete(self):
        """Тест краткого форматирования с полными данными"""
        formatter = VacancyFormatter()
        
        class MockVacancy:
            def __init__(self):
                self.title = "Data Scientist"
                self.employer = {"name": "DataCorp"}
                self.salary = {"from": 120000, "currency": "RUR"}
                self.url = "https://hh.ru/vacancy/789"
        
        vacancy = MockVacancy()
        result = VacancyFormatter.format_vacancy_brief(vacancy, 2)
        
        assert "2." in result
        assert "Data Scientist" in result
        assert "DataCorp" in result
        assert "от 120" in result
        assert "https://hh.ru/vacancy/789" in result

    def test_format_vacancy_brief_minimal_data(self):
        """Тест краткого форматирования с минимальными данными"""
        class MockVacancy:
            def __init__(self):
                self.title = "Junior Developer"
                self.employer = None
                self.salary = None
                self.url = None
        
        vacancy = MockVacancy()
        result = VacancyFormatter.format_vacancy_brief(vacancy)
        
        assert "Junior Developer" in result
        assert "Зарплата не указана" in result

    def test_display_vacancy_info_static_method(self):
        """Тест статического метода отображения"""
        class MockVacancy:
            def __init__(self):
                self.title = "Test Job"
                self.employer = {"name": "Test Company"}
        
        vacancy = MockVacancy()
        
        # Проверяем, что метод вызывается без ошибок
        try:
            with patch('builtins.print') as mock_print:
                VacancyFormatter.display_vacancy_info(vacancy, 1)
                mock_print.assert_called_once()
        except Exception as e:
            pytest.fail(f"display_vacancy_info raised an exception: {e}")

    def test_clean_html_tags_complex(self):
        """Тест очистки сложных HTML тегов"""
        formatter = VacancyFormatter()
        
        # Сложный HTML
        complex_html = """
        <div class="description">
            <p>Мы ищем <strong>Python разработчика</strong> для работы над проектами.</p>
            <ul>
                <li>Опыт работы с Django</li>
                <li>Знание PostgreSQL</li>
            </ul>
            <br/>
            <span style="color: red;">Удаленная работа</span>
        </div>
        """
        
        result = formatter.clean_html_tags(complex_html)
        
        # Проверяем, что HTML теги удалены
        assert "<div>" not in result
        assert "<p>" not in result
        assert "<strong>" not in result
        assert "<ul>" not in result
        assert "<li>" not in result
        assert "<br/>" not in result
        assert "<span>" not in result
        
        # Проверяем, что текст остался
        assert "Python разработчика" in result
        assert "Django" in result
        assert "PostgreSQL" in result
        assert "Удаленная работа" in result

    def test_format_number_edge_cases(self):
        """Тест форматирования чисел с крайними случаями"""
        formatter = VacancyFormatter()
        
        # Большие числа
        assert "1 000 000" in formatter.format_number(1000000)
        
        # Отрицательные числа
        result = formatter.format_number(-5000)
        assert "-5" in result and "000" in result
        
        # Дробные числа
        result = formatter.format_number(1234.56)
        assert "1" in result and "234" in result
        
        # Ноль
        assert formatter.format_number(0) == "0"
        
        # Строка
        assert formatter.format_number("abc") == "abc"
        
        # None
        assert formatter.format_number(None) == "None"

    def test_currency_mapping_complete(self):
        """Тест полного маппинга валют"""
        formatter = VacancyFormatter()
        
        assert formatter.format_currency("RUR") == "руб."
        assert formatter.format_currency("RUB") == "руб."
        assert formatter.format_currency("USD") == "долл."
        assert formatter.format_currency("EUR") == "евро"
        assert formatter.format_currency("UNKNOWN") == "UNKNOWN"  # неизвестная валюта

    def test_extract_fields_with_getattr_fallback(self):
        """Тест извлечения полей с различными именами"""
        formatter = VacancyFormatter()
        
        class MockVacancy1:
            def __init__(self):
                self.vacancy_id = "hh_123"
                self.title = "HH Job"
                self.url = "https://hh.ru/vacancy/123"
        
        class MockVacancy2:
            def __init__(self):
                self.id = "sj_456"
                self.name = "SJ Job"
                self.alternate_url = "https://superjob.ru/vakansii/456"
        
        # Тест с vacancy_id/title/url
        lines1 = formatter._build_vacancy_lines(MockVacancy1())
        text1 = '\n'.join(lines1)
        assert "hh_123" in text1
        assert "HH Job" in text1
        assert "https://hh.ru/vacancy/123" in text1
        
        # Тест с id/name/alternate_url
        lines2 = formatter._build_vacancy_lines(MockVacancy2())
        text2 = '\n'.join(lines2)
        assert "sj_456" in text2
        assert "SJ Job" in text2
        assert "https://superjob.ru/vakansii/456" in text2(self):
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
import pytest
from unittest.mock import Mock
from src.utils.vacancy_formatter import VacancyFormatter, vacancy_formatter


class TestVacancyFormatter:
    """Тесты для VacancyFormatter"""

    @pytest.fixture
    def formatter(self):
        """Фикстура для создания форматировщика"""
        return VacancyFormatter()

    @pytest.fixture
    def sample_vacancy(self):
        """Фикстура с примером вакансии"""
        return Mock(
            vacancy_id="12345",
            title="Python Developer",
            employer={"name": "Test Company"},
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            experience="Опыт от 1 года до 3 лет",
            employment="Полная занятость",
            source="hh.ru",
            url="https://hh.ru/vacancy/12345",
            responsibilities="Разработка веб-приложений",
            requirements="Python, Django, PostgreSQL",
            conditions="Удаленная работа"
        )

    def test_format_vacancy_info_complete(self, formatter, sample_vacancy):
        """Тест полного форматирования вакансии"""
        result = formatter.format_vacancy_info(sample_vacancy, 1)
        
        assert "1." in result
        assert "ID: 12345" in result
        assert "Название: Python Developer" in result
        assert "Компания: Test Company" in result
        assert "Зарплата: от 100 000 до 150 000 руб. в месяц" in result

    def test_format_salary_dict(self, formatter):
        """Тест форматирования зарплаты из словаря"""
        # Полная зарплата
        salary = {"from": 100000, "to": 150000, "currency": "RUR"}
        result = formatter.format_salary(salary)
        assert result == "от 100 000 до 150 000 руб. в месяц"
        
        # Только минимум
        salary = {"from": 80000, "currency": "USD"}
        result = formatter.format_salary(salary)
        assert result == "от 80 000 долл. в месяц"
        
        # Только максимум
        salary = {"to": 120000, "currency": "EUR"}
        result = formatter.format_salary(salary)
        assert result == "до 120 000 евро в месяц"
        
        # Пустая зарплата
        result = formatter.format_salary({})
        assert result == "Не указана"

    def test_format_currency(self, formatter):
        """Тест форматирования валюты"""
        assert formatter.format_currency("RUR") == "руб."
        assert formatter.format_currency("RUB") == "руб."
        assert formatter.format_currency("USD") == "долл."
        assert formatter.format_currency("EUR") == "евро"
        assert formatter.format_currency("CHF") == "CHF"

    def test_format_text_truncation(self, formatter):
        """Тест усечения текста"""
        long_text = "A" * 200
        result = formatter.format_text(long_text, 100)
        assert len(result) == 103  # 100 символов + "..."
        assert result.endswith("...")

    def test_clean_html_tags(self, formatter):
        """Тест очистки HTML тегов"""
        html_text = "<p>Требуется <strong>Python</strong> разработчик</p>"
        result = formatter.clean_html_tags(html_text)
        assert result == "Требуется Python разработчик"
        
        # Множественные пробелы
        html_text = "<div>Text   with    spaces</div>"
        result = formatter.clean_html_tags(html_text)
        assert result == "Text with spaces"

    def test_format_number(self, formatter):
        """Тест форматирования чисел"""
        assert formatter.format_number(1000) == "1 000"
        assert formatter.format_number(1234567) == "1 234 567"
        assert formatter.format_number(100) == "100"

    def test_format_date(self, formatter):
        """Тест форматирования даты"""
        # ISO формат
        result = formatter.format_date("2024-01-15T10:30:00+03:00")
        assert result == "15.01.2024"
        
        # Некорректная дата
        result = formatter.format_date("invalid-date")
        assert result == "invalid-date"
        
        # Пустая дата
        result = formatter.format_date("")
        assert result == "Не указано"

    def test_extract_company_name(self, formatter):
        """Тест извлечения названия компании"""
        # Словарь с названием
        vacancy = Mock(employer={"name": "Test Company"})
        result = formatter._extract_company_name(vacancy)
        assert result == "Test Company"
        
        # Строка
        vacancy = Mock(employer="String Company")
        result = formatter._extract_company_name(vacancy)
        assert result == "String Company"
        
        # Пустое название
        vacancy = Mock(employer={"name": ""})
        result = formatter._extract_company_name(vacancy)
        assert result == "Не указана"
        
        # Нет работодателя
        vacancy = Mock(employer=None)
        result = formatter._extract_company_name(vacancy)
        assert result == "Не указана"

    def test_format_vacancy_brief(self):
        """Тест краткого форматирования"""
        vacancy = Mock(
            title="Developer",
            employer={"name": "Company"},
            salary={"from": 100000, "currency": "RUR"},
            url="http://example.com"
        )
        
        result = VacancyFormatter.format_vacancy_brief(vacancy, 1)
        assert "1." in result
        assert "Developer" in result
        assert "Company" in result

    def test_display_vacancy_info(self, capsys):
        """Тест отображения информации о вакансии"""
        vacancy = Mock(
            vacancy_id="123",
            title="Test Job"
        )
        
        VacancyFormatter.display_vacancy_info(vacancy)
        captured = capsys.readouterr()
        assert "ID: 123" in captured.out
        assert "Название: Test Job" in captured.out

    def test_format_experience(self, formatter):
        """Тест форматирования опыта"""
        assert formatter.format_experience("Опыт от 1 года") == "Опыт от 1 года"
        assert formatter.format_experience("") == "Не указан"
        assert formatter.format_experience(None) == "Не указан"

    def test_format_employment_type(self, formatter):
        """Тест форматирования типа занятости"""
        assert formatter.format_employment_type("Полная занятость") == "Полная занятость"
        assert formatter.format_employment_type("") == "Не указан"

    def test_format_schedule(self, formatter):
        """Тест форматирования графика работы"""
        assert formatter.format_schedule("Полный день") == "Полный день"
        assert formatter.format_schedule("") == "Не указан"

    def test_format_company_name_dict(self, formatter):
        """Тест форматирования названия компании из словаря"""
        company = {"name": "Test Company"}
        result = formatter.format_company_name(company)
        assert result == "Test Company"
        
        # Пустой словарь
        result = formatter.format_company_name({})
        assert result == "Не указана"

    def test_global_formatter_instance(self):
        """Тест глобального экземпляра форматировщика"""
        assert isinstance(vacancy_formatter, VacancyFormatter)

    def test_vacancy_without_optional_fields(self, formatter):
        """Тест вакансии без опциональных полей"""
        minimal_vacancy = Mock(
            vacancy_id="123",
            title="Job",
            employer=None,
            salary=None,
            url=None
        )
        
        result = formatter.format_vacancy_info(minimal_vacancy)
        assert "ID: 123" in result
        assert "Название: Job" in result
        # Не должно быть ошибок при отсутствии полей

    def test_extract_conditions_with_schedule(self, formatter):
        """Тест извлечения условий с графиком работы"""
        vacancy = Mock(
            conditions=None,
            schedule="Удаленная работа"
        )
        
        result = formatter._extract_conditions(vacancy)
        assert "График: Удаленная работа" in result

    def test_build_vacancy_lines_order(self, formatter):
        """Тест порядка строк в информации о вакансии"""
        vacancy = Mock(
            vacancy_id="123",
            title="Job",
            employer={"name": "Company"},
            salary={"from": 100000, "currency": "RUR"},
            source="test"
        )
        
        lines = formatter._build_vacancy_lines(vacancy, 1)
        
        # Проверяем, что номер идет первым
        assert lines[0] == "1."
        # ID должен быть вторым
        assert "ID: 123" in lines[1]
        # Название третьим
        assert "Название: Job" in lines[2]
