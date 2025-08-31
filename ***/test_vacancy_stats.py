"""
Тесты для модуля статистики вакансий
"""

from unittest.mock import patch

import pytest

from src.utils.vacancy_stats import VacancyStats
from src.vacancies.models import Vacancy


class TestVacancyStats:
    """Тесты для класса VacancyStats"""

    @pytest.fixture
    def sample_vacancies_dict(self):
        """Фикстура с тестовыми вакансиями в виде словарей"""
        return [
            {
                "id": "1",
                "name": "Python Developer",
                "employer": {"name": "TechCorp"},
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            },
            {
                "id": "2",
                "profession": "Java Developer",
                "firm_name": "JavaCorp",
                "payment_from": 120000,
                "payment_to": 180000,
            },
            {"id": "3", "name": "Frontend Developer", "employer": {"name": "TechCorp"}, "salary": None},
        ]

    @pytest.fixture
    def sample_vacancy_objects(self):
        """Фикстура с тестовыми объектами Vacancy"""
        return [
            Vacancy(
                title="Python Developer",
                url="https://example.com/1",
                vacancy_id="1",
                employer={"name": "TechCorp"},
                salary={"from": 100000, "to": 150000, "currency": "RUR"},
                source="hh.ru",
            ),
            Vacancy(
                title="Java Developer",
                url="https://example.com/2",
                vacancy_id="2",
                employer={"name": "JavaCorp"},
                salary={"from": 120000, "to": 180000, "currency": "RUR"},
                source="superjob.ru",
            ),
        ]

    def test_get_company_distribution_dict_data(self, sample_vacancies_dict):
        """Тест получения распределения компаний из словарей"""
        stats = VacancyStats.get_company_distribution(sample_vacancies_dict)

        assert isinstance(stats, dict)
        assert "TechCorp" in stats
        assert "JavaCorp" in stats
        assert stats["TechCorp"] == 2  # Python и Frontend разработчики
        assert stats["JavaCorp"] == 1

    def test_get_company_distribution_vacancy_objects(self, sample_vacancy_objects):
        """Тест получения распределения компаний из объектов Vacancy"""
        stats = VacancyStats.get_company_distribution(sample_vacancy_objects)

        assert isinstance(stats, dict)
        assert "TechCorp" in stats
        assert "JavaCorp" in stats
        assert stats["TechCorp"] == 1
        assert stats["JavaCorp"] == 1

    def test_extract_company_name_hh_format(self):
        """Тест извлечения названия компании из формата HH"""
        vacancy = {"employer": {"name": "HH Test Company"}}

        company = VacancyStats._extract_company_name(vacancy)
        assert company == "HH Test Company"

    def test_extract_company_name_sj_format(self):
        """Тест извлечения названия компании из формата SuperJob"""
        vacancy = {"firm_name": "SJ Test Company", "firm_id": "123"}

        company = VacancyStats._extract_company_name(vacancy)
        assert company == "SJ Test Company"

    def test_extract_company_name_vacancy_object(self, sample_vacancy_objects):
        """Тест извлечения названия компании из объекта Vacancy"""
        vacancy = sample_vacancy_objects[0]

        company = VacancyStats._extract_company_name(vacancy)
        assert company == "TechCorp"

    def test_extract_company_name_unknown(self):
        """Тест извлечения названия компании из неизвестного формата"""
        vacancy = {"unknown_field": "value"}

        company = VacancyStats._extract_company_name(vacancy)
        assert company == "Неизвестная компания"

    def test_extract_company_name_empty_employer(self):
        """Тест извлечения названия компании с пустым работодателем"""
        vacancy = {"employer": {"name": ""}}

        company = VacancyStats._extract_company_name(vacancy)
        assert company == "Неизвестная компания"

    @patch("builtins.print")
    def test_display_company_stats_with_data(self, mock_print, sample_vacancies_dict):
        """Тест отображения статистики компаний с данными"""
        VacancyStats.display_company_stats(sample_vacancies_dict, "Test Source")

        # Проверяем, что функция print была вызвана
        assert mock_print.called

        # Проверяем, что в выводе есть информация о компаниях
        call_args = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(call_args)
        assert "TechCorp" in output_text
        assert "JavaCorp" in output_text

    @patch("builtins.print")
    def test_display_company_stats_empty_data(self, mock_print):
        """Тест отображения статистики для пустых данных"""
        VacancyStats.display_company_stats([], "Test Source")

        # Проверяем, что была показана соответствующая ошибка
        assert mock_print.called
        call_args = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(call_args)
        assert "Нет вакансий" in output_text

    @patch("builtins.print")
    def test_display_source_stats(self, mock_print, sample_vacancies_dict):
        """Тест отображения статистики по источникам"""
        hh_vacancies = sample_vacancies_dict[:2]
        sj_vacancies = sample_vacancies_dict[2:]

        VacancyStats.display_source_stats(hh_vacancies, sj_vacancies)

        assert mock_print.called
        call_args = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(call_args)
        assert "Итого найдено" in output_text

    def test_analyze_company_mapping(self, sample_vacancies_dict):
        """Тест анализа маппинга компаний"""
        analysis = VacancyStats.analyze_company_mapping(sample_vacancies_dict)

        assert isinstance(analysis, dict)
        assert "total_vacancies" in analysis
        assert "with_employer" in analysis
        assert "without_employer" in analysis
        assert "employer_coverage" in analysis
        assert "unique_employers" in analysis
        assert "employers_list" in analysis

        assert analysis["total_vacancies"] == 3
        assert analysis["unique_employers"] == 2  # TechCorp и JavaCorp

    @patch("builtins.print")
    def test_display_company_mapping_analysis(self, mock_print, sample_vacancies_dict):
        """Тест отображения анализа маппинга компаний"""
        VacancyStats.display_company_mapping_analysis(sample_vacancies_dict)

        assert mock_print.called
        call_args = [call[0][0] for call in mock_print.call_args_list]
        output_text = " ".join(call_args)
        assert "Анализ маппинга компаний" in output_text
        assert "Всего вакансий" in output_text

    def test_company_distribution_edge_cases(self):
        """Тест граничных случаев для распределения компаний"""
        # Пустой список
        stats = VacancyStats.get_company_distribution([])
        assert stats == {}

        # Список с None значениями
        stats = VacancyStats.get_company_distribution([None, None])
        assert isinstance(stats, dict)

        # Список с некорректными данными
        stats = VacancyStats.get_company_distribution([{"invalid": "data"}])
        assert isinstance(stats, dict)
