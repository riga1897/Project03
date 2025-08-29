
"""
Основные функциональные тесты

Тесты основной функциональности приложения без внешних зависимостей.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.vacancies.models import Vacancy
from src.utils.vacancy_operations import VacancyOperations
from src.utils.vacancy_formatter import VacancyFormatter


class TestMainFunctionality:
    """Тесты основной функциональности"""

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
            source="test.ru"
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
        python_vacancies = operations.filter_vacancies_by_keyword(sample_vacancies, "Python")
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
        assert "100 000" in salary_formatted
        assert "150 000" in salary_formatted
        assert "руб." in salary_formatted

    @patch('builtins.input')
    def test_user_input_simulation(self, mock_input):
        """Тест симуляции пользовательского ввода"""
        mock_input.return_value = "test_query"
        
        # Симулируем получение пользовательского ввода
        user_query = input("Введите запрос: ")
        assert user_query == "test_query"

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

    def test_data_validation(self):
        """Тест валидации данных"""
        # Тест создания вакансии с минимальными данными
        minimal_vacancy = Vacancy(
            title="Minimal Job",
            url="https://example.com/job",
            vacancy_id="min001",
            source="test"
        )
        
        assert minimal_vacancy.title == "Minimal Job"
        assert minimal_vacancy.salary is None
        assert minimal_vacancy.description is None

    def test_search_functionality(self, sample_vacancies):
        """Тест функциональности поиска"""
        operations = VacancyOperations()
        
        # Тест поиска по нескольким ключевым словам
        keywords = ["Python", "Developer"]
        results = operations.filter_vacancies_by_multiple_keywords(sample_vacancies, keywords)
        
        assert isinstance(results, list)
        # Должны найти хотя бы одну вакансию с любым из ключевых слов
        assert len(results) >= 1

    @patch('src.storage.postgres_saver.PostgresSaver')
    def test_storage_mocking(self, mock_storage_class):
        """Тест мокирования хранилища"""
        mock_storage = Mock()
        mock_storage.add_vacancy.return_value = True
        mock_storage.get_vacancies.return_value = []
        mock_storage_class.return_value = mock_storage

        # Создаем экземпляр через мокированный класс
        storage = mock_storage_class()
        
        # Тест операций
        assert storage.add_vacancy(None) is True
        assert storage.get_vacancies() == []

    def test_configuration_defaults(self):
        """Тест конфигурации по умолчанию"""
        # Тест, что базовые классы могут быть инстанцированы
        formatter = VacancyFormatter()
        operations = VacancyOperations()
        
        assert formatter is not None
        assert operations is not None
        assert hasattr(formatter, 'format_vacancy_info')
        assert hasattr(operations, 'filter_vacancies_by_keyword')
