"""
Интеграционные тесты для приложения поиска вакансий
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from src.storage.json_saver import JSONSaver
from src.utils.vacancy_operations import VacancyOperations
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy


class TestIntegrationWorkflow:
    """Интеграционные тесты основного workflow приложения"""

    def test_complete_vacancy_workflow_json(self, temp_json_file):
        """Тест полного цикла работы с вакансиями через JSON"""
        # 1. Создаем хранилище
        storage = JSONSaver(temp_json_file)

        # 2. Создаем тестовые вакансии
        vacancies = [
            Vacancy(
                title="Senior Python Developer",
                url="https://hh.ru/vacancy/1",
                vacancy_id="1",
                salary={"from": 150000, "to": 200000, "currency": "RUR"},
                requirements="Python, Django, PostgreSQL",
                source="hh.ru"
            ),
            Vacancy(
                title="DevOps Engineer",
                url="https://superjob.ru/vacancy/2",
                vacancy_id="2",
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                requirements="Docker, Kubernetes, Python",
                source="superjob.ru"
            ),
            Vacancy(
                title="Junior Frontend Developer",
                url="https://hh.ru/vacancy/3",
                vacancy_id="3",
                requirements="JavaScript, React, HTML/CSS",
                source="hh.ru"
            )
        ]

        # 3. Добавляем вакансии в хранилище
        for vacancy in vacancies:
            messages = storage.add_vacancy(vacancy)
            assert len(messages) > 0

        # 4. Получаем все вакансии
        stored_vacancies = storage.get_vacancies()
        assert len(stored_vacancies) == 3

        # 5. Тестируем операции поиска
        ops = VacancyOperations()

        # Поиск по Python
        python_vacancies = ops.search_vacancies_advanced(stored_vacancies, "Python")
        assert len(python_vacancies) == 2  # Senior Python + DevOps (Python в requirements)

        # Сортировка по зарплате
        vacancies_with_salary = ops.get_vacancies_with_salary(stored_vacancies)
        sorted_by_salary = ops.sort_vacancies_by_salary(vacancies_with_salary)
        assert sorted_by_salary[0].title == "Senior Python Developer"  # Самая высокая зарплата

        # 6. Тестируем форматирование
        formatter = VacancyFormatter()
        formatted = formatter.format_vacancy_info(sorted_by_salary[0], number=1)
        assert "1." in formatted
        assert "Senior Python Developer" in formatted
        assert "150,000" in formatted

        # 7. Тестируем удаление
        assert storage.delete_vacancy_by_id("2") is True
        remaining = storage.get_vacancies()
        assert len(remaining) == 2

        # 8. Тестируем очистку
        assert storage.delete_all_vacancies() is True
        final_vacancies = storage.get_vacancies()
        assert len(final_vacancies) == 0

    def test_search_and_filter_integration(self):
        """Тест интеграции поиска и фильтрации"""
        vacancies = [
            Vacancy(
                title="Senior Python Developer",
                url="https://hh.ru/vacancy/1",
                vacancy_id="1",
                salary={"from": 150000, "currency": "RUR"},
                description="Senior Python developer with Django",
                requirements="Python, Django, PostgreSQL",
                source="hh.ru"
            ),
            Vacancy(
                title="Middle Python Developer",
                url="https://hh.ru/vacancy/2",
                vacancy_id="2",
                salary={"from": 100000, "currency": "RUR"},
                description="Python developer with Flask",
                requirements="Python, Flask, MySQL",
                source="hh.ru"
            ),
            Vacancy(
                title="Junior Python Developer",
                url="https://hh.ru/vacancy/3",
                vacancy_id="3",
                salary={"from": 70000, "currency": "RUR"},
                description="Entry level Python position",
                requirements="Python basics",
                source="hh.ru"
            ),
            Vacancy(
                title="Java Developer",
                url="https://hh.ru/vacancy/4",
                vacancy_id="4",
                salary={"from": 120000, "currency": "RUR"},
                description="Java Spring developer",
                requirements="Java, Spring Boot",
                source="hh.ru"
            )
        ]

        ops = VacancyOperations()

        # 1. Поиск всех Python разработчиков
        python_devs = ops.search_vacancies_advanced(vacancies, "Python")
        assert len(python_devs) == 3

        # 2. Фильтрация по уровню (Senior)
        senior_devs = ops.search_vacancies_advanced(python_devs, "Senior")
        assert len(senior_devs) == 1
        assert senior_devs[0].vacancy_id == "1"

        # 3. Комбинированный поиск
        senior_python = ops.search_vacancies_advanced(vacancies, "Senior AND Python")
        assert len(senior_python) == 1
        assert senior_python[0].vacancy_id == "1"

        # 4. Сортировка и фильтрация по зарплате
        high_salary_vacancies = ops.get_vacancies_with_salary(vacancies)
        sorted_vacancies = ops.sort_vacancies_by_salary(high_salary_vacancies)

        # Проверяем, что первые позиции имеют большую зарплату
        assert sorted_vacancies[0].salary.salary_from >= sorted_vacancies[1].salary.salary_from
        assert sorted_vacancies[1].salary.salary_from >= sorted_vacancies[2].salary.salary_from

    def test_error_handling_integration(self, temp_json_file):
        """Тест обработки ошибок в интегрированном workflow"""
        storage = JSONSaver(temp_json_file)
        ops = VacancyOperations()

        # 1. Работа с пустым хранилищем
        empty_vacancies = storage.get_vacancies()
        assert empty_vacancies == []

        search_result = ops.search_vacancies_advanced(empty_vacancies, "Python")
        assert search_result == []

        # 2. Удаление несуществующей вакансии
        delete_result = storage.delete_vacancy_by_id("nonexistent")
        assert delete_result is False

        # 3. Добавление вакансии с некорректными данными
        invalid_vacancy = Vacancy(title="", url="", vacancy_id="")
        messages = storage.add_vacancy(invalid_vacancy)
        # Вакансия должна быть добавлена, но с предупреждениями
        assert len(messages) > 0

    @patch('src.api_modules.cached_api.CachedAPI._CachedAPI__connect_to_api')
    def test_api_to_storage_integration(self, mock_api, temp_json_file):
        """Тест интеграции API -> хранилище"""
        from src.api_modules.hh_api import HeadHunterAPI
        from src.vacancies.parsers.hh_parser import HHParser

        # 1. Мокаем ответ API
        mock_api.return_value = {
            "items": [
                {
                    "id": "12345",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/12345",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {
                        "requirement": "Python, Django",
                        "responsibility": "Development"
                    },
                    "employer": {"name": "Test Company"},
                    "published_at": "2024-01-01T00:00:00+03:00"
                }
            ],
            "found": 1,
            "pages": 1
        }

        # 2. Получаем данные через API
        api = HeadHunterAPI()
        raw_vacancies = api.get_vacancies("python")

        assert len(raw_vacancies) == 1
        assert raw_vacancies[0]["name"] == "Python Developer"

        # 3. Парсим в объекты Vacancy
        parser = HHParser()
        parsed_vacancies = parser._parse_items(raw_vacancies)

        # Проверяем, что получили ожидаемую вакансию
        assert len(parsed_vacancies) == 1
        assert isinstance(parsed_vacancies[0], Vacancy)
        assert parsed_vacancies[0].title == "Python Developer"
        assert parsed_vacancies[0].url == "https://hh.ru/vacancy/12345"

        # 4. Сохраняем в хранилище
        storage = JSONSaver(temp_json_file)
        messages = storage.add_vacancy(parsed_vacancies[0])

        assert len(messages) == 1

        # 5. Проверяем сохранение
        stored = storage.get_vacancies()
        assert len(stored) == 1
        assert stored[0].title == "Python Developer"
        assert stored[0].url == "https://hh.ru/vacancy/12345"