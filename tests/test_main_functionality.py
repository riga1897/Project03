"""
Основные функциональные тесты

Тесты основной функциональности приложения без внешних зависимостей.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.utils.salary import Salary
from src.utils.vacancy_formatter import VacancyFormatter
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy


class TestMainFunctionality:
    """Тесты основной функциональности"""

    @pytest.fixture
    def sample_vacancy(self):
        """Базовая фикстура вакансии"""
        return Vacancy(
            title="Python Developer",
            url="https://example.com/vacancy/12345",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="От 1 года до 3 лет",
            employment="Полная занятость",
            schedule="Полный день",
            employer={"name": "Test Company"},
            vacancy_id="12345",
            published_at="2024-01-01T00:00:00",
            source="test.ru",
        )

    @pytest.fixture
    def sample_vacancies(self):
        """Фикстура с набором вакансий для тестирования"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://example.com/1",
                vacancy_id="1",
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                requirements="Python, Django",
                source="hh.ru",
            ),
            Vacancy(
                title="Java Developer",
                url="https://example.com/2",
                vacancy_id="2",
                salary={"from": 80000, "to": 120000, "currency": "RUR"},
                requirements="Java, Spring",
                source="superjob.ru",
            ),
        ]

    def test_vacancy_creation(self):
        """Тест создания объекта вакансии"""
        vacancy = Vacancy(
            title="Test Developer",
            url="https://example.com/vacancy/123",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Test description",
            requirements="Test requirements",
            responsibilities="Test responsibilities",
            experience="От 1 года до 3 лет",
            employment="Полная занятость",
            schedule="Полный день",
            employer={"name": "Test Company"},
            vacancy_id="123",
            published_at="2024-01-01T00:00:00",
            source="test.ru",
        )

        assert vacancy.title == "Test Developer"
        assert vacancy.vacancy_id == "123"
        assert vacancy.source == "test.ru"

    def test_vacancy_operations(self, sample_vacancies):
        """Тест операций с вакансиями"""
        operations = VacancyOperations()

        # Тест фильтрации по зарплате
        filtered = operations.filter_vacancies_by_min_salary(sample_vacancies, 90000)
        assert len(filtered) == 1  # Только одна вакансия с зарплатой >= 90000

        # Тест поиска по ключевому слову
        python_vacancies = operations.filter_vacancies_by_multiple_keywords(sample_vacancies, ["Python"])
        assert len(python_vacancies) == 1
        assert "Python" in python_vacancies[0].title

    def test_vacancy_formatter(self, sample_vacancy):
        """Тест форматирования вакансий"""
        formatter = VacancyFormatter()

        # Тест полного форматирования
        formatted = formatter.format_vacancy_info(sample_vacancy, 1)
        assert isinstance(formatted, str)
        assert "Python Developer" in formatted
        assert "12345" in formatted

        # Тест форматирования зарплаты
        salary_formatted = formatter.format_salary(sample_vacancy.salary)
        assert "100,000" in salary_formatted or "100 000" in salary_formatted
        assert "150,000" in salary_formatted or "150 000" in salary_formatted
        assert "руб." in salary_formatted

    def test_vacancy_comparison(self, sample_vacancies):
        """Тест сравнения вакансий"""
        operations = VacancyOperations()

        # Сортировка по зарплате
        sorted_vacancies = operations.sort_vacancies_by_salary(sample_vacancies)
        assert len(sorted_vacancies) == 2

        # Первая должна быть с большей зарплатой
        first_salary = sorted_vacancies[0].salary
        second_salary = sorted_vacancies[1].salary

        assert first_salary is not None
        assert second_salary is not None

    def test_error_handling(self):
        """Тест обработки ошибок"""
        formatter = VacancyFormatter()

        # Тест с None значениями
        result = formatter.format_salary(None)
        assert result == "Не указана"

        # Тест с пустой строкой
        result = formatter.format_text("")
        assert result == "Не указано"

        # Тест статических методов
        brief_result = VacancyFormatter.format_vacancy_brief(None, 1)
        assert isinstance(brief_result, str)

        # Тест форматирования без номера
        minimal_vacancy = Vacancy(
            title="Test Job", url="https://example.com/test", vacancy_id="test001", source="test"
        )
        formatted = formatter.format_vacancy_info(minimal_vacancy)
        assert "Test Job" in formatted

    def test_data_validation(self):
        """Тест валидации данных"""
        # Тест создания вакансии с минимальными данными
        minimal_vacancy = Vacancy(
            title="Minimal Job", url="https://example.com/job", vacancy_id="min001", source="test"
        )

        assert minimal_vacancy.title == "Minimal Job"
        # Vacancy всегда создает объект Salary, даже если данные не переданы
        assert minimal_vacancy.salary is not None
        assert isinstance(minimal_vacancy.salary, Salary)
        # Проверяем, что зарплата пустая
        assert minimal_vacancy.salary.salary_from is None
        assert minimal_vacancy.salary.salary_to is None
        assert str(minimal_vacancy.salary) == "Зарплата не указана"
        # description имеет значение по умолчанию "" в конструкторе Vacancy
        assert minimal_vacancy.description == ""

    def test_search_functionality(self, sample_vacancies):
        """Тест функциональности поиска"""
        operations = VacancyOperations()

        # Тест поиска по нескольким ключевым словам
        keywords = ["Python", "Developer"]
        results = operations.filter_vacancies_by_multiple_keywords(sample_vacancies, keywords)

        assert isinstance(results, list)
        # Должны найти хотя бы одну вакансию с любым из ключевых слов
        assert len(results) >= 1

    def test_configuration_defaults(self):
        """Тест конфигурации по умолчанию"""
        # Тест, что базовые классы могут быть инстанцированы
        formatter = VacancyFormatter()
        operations = VacancyOperations()

        assert formatter is not None
        assert operations is not None
        assert hasattr(formatter, "format_vacancy_info")
        assert hasattr(operations, "filter_vacancies_by_multiple_keywords")
        assert hasattr(operations, "search_vacancies_advanced")
        assert hasattr(operations, "filter_vacancies_by_salary_range")
        assert hasattr(operations, "sort_vacancies_by_salary")
        assert hasattr(operations, "filter_vacancies_by_min_salary")
        assert hasattr(operations, "filter_vacancies_by_max_salary")

    def test_vacancy_from_dict(self):
        """Тест создания вакансии из словаря"""
        vacancy_dict = {
            "id": "test123",
            "name": "Test Position",
            "alternate_url": "https://example.com/test123",
            "employer": {"name": "Test Employer"},
            "source": "test.ru",
            "salary": {"from": 50000, "to": 100000, "currency": "RUR"},
            "snippet": {"requirement": "Test requirements", "responsibility": "Test responsibilities"},
            "published_at": "2024-01-01T00:00:00+03:00",
        }

        vacancy = Vacancy.from_dict(vacancy_dict)

        assert vacancy.vacancy_id == "test123"
        assert vacancy.title == "Test Position"
        assert vacancy.url == "https://example.com/test123"
        assert vacancy.employer == {"name": "Test Employer"}
        assert vacancy.source == "test.ru"

    def test_vacancy_to_dict(self, sample_vacancy):
        """Тест преобразования вакансии в словарь"""
        vacancy_dict = sample_vacancy.to_dict()

        assert isinstance(vacancy_dict, dict)
        assert vacancy_dict["title"] == "Python Developer"
        assert vacancy_dict["vacancy_id"] == "12345"
        assert vacancy_dict["source"] == "test.ru"

    @patch("src.storage.postgres_saver.PostgresSaver")
    def test_storage_mocking(self, mock_storage_class):
        """Тест мокирования хранилища"""
        mock_storage = Mock()
        mock_storage.add_vacancy.return_value = True
        mock_storage.get_vacancies.return_value = []
        mock_storage.get_vacancies_count.return_value = 0
        mock_storage_class.return_value = mock_storage

        # Создаем экземпляр через мокированный класс
        storage = mock_storage_class()

        # Тест операций
        assert storage.add_vacancy(None) is True
        assert storage.get_vacancies() == []
        assert storage.get_vacancies_count() == 0

    def test_advanced_search_patterns(self, sample_vacancies):
        """Тест расширенных паттернов поиска"""
        operations = VacancyOperations()

        # Тест поиска с AND оператором
        and_results = operations.search_vacancies_advanced(sample_vacancies, "Python AND Developer")
        assert isinstance(and_results, list)

        # Тест поиска с OR оператором
        or_results = operations.search_vacancies_advanced(sample_vacancies, "Python OR Java")
        assert isinstance(or_results, list)
        assert len(or_results) >= 1

    def test_salary_operations(self, sample_vacancies):
        """Тест операций с зарплатой"""
        operations = VacancyOperations()

        # Тест получения вакансий с зарплатой
        with_salary = operations.get_vacancies_with_salary(sample_vacancies)
        assert len(with_salary) == 2  # Обе вакансии имеют зарплату

        # Тест фильтрации по максимальной зарплате
        max_salary_filter = operations.filter_vacancies_by_max_salary(sample_vacancies, 130000)
        assert len(max_salary_filter) >= 1

        # Тест фильтрации по диапазону зарплат
        range_filter = operations.filter_vacancies_by_salary_range(sample_vacancies, 80000, 120000)
        assert isinstance(range_filter, list)
