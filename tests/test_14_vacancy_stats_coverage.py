#!/usr/bin/env python3
"""
Тесты для 100% покрытия src/utils/vacancy_stats.py
Систематично покрываем каждый метод и ветку кода с мокингом всех I/O операций.
"""

import pytest
from unittest.mock import Mock, patch
from collections import defaultdict

# Импорты из реального кода для покрытия
from src.utils.vacancy_stats import VacancyStats, VacancyStatsExtended, calculate_statistics


class TestVacancyStatsInit:
    """100% покрытие инициализации VacancyStats."""
    
    def test_init(self):
        """Покрытие __init__ метода."""
        stats = VacancyStats()
        assert stats is not None


class TestCalculateSalaryStatistics:
    """100% покрытие calculate_salary_statistics."""
    
    def test_empty_vacancies_list(self):
        """Покрытие пустого списка вакансий."""
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([])
        
        expected = {
            "average": 0, "min": 0, "max": 0, "count": 0,
            "with_salary_count": 0, "without_salary_count": 0
        }
        assert result == expected
    
    def test_vacancy_with_salary_from(self):
        """Покрытие вакансии с salary_from."""
        mock_salary = Mock()
        mock_salary.amount_from = 100000
        mock_salary.amount_to = None
        
        mock_vacancy = Mock()
        mock_vacancy.salary = mock_salary
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        assert result["average"] == 100000
        assert result["min"] == 100000
        assert result["max"] == 100000
        assert result["count"] == 1
        assert result["with_salary_count"] == 1
        assert result["without_salary_count"] == 0
    
    def test_vacancy_with_salary_to(self):
        """Покрытие вакансии с salary_to."""
        mock_salary = Mock()
        mock_salary.amount_from = None
        mock_salary.amount_to = 150000
        
        mock_vacancy = Mock()
        mock_vacancy.salary = mock_salary
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        assert result["average"] == 150000
        assert result["with_salary_count"] == 1
    
    def test_vacancy_without_salary(self):
        """Покрытие вакансии без salary."""
        mock_vacancy = Mock()
        mock_vacancy.salary = None
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        assert result["with_salary_count"] == 0
        assert result["without_salary_count"] == 1
    
    def test_vacancy_with_invalid_salary_types(self):
        """Покрытие вакансий с некорректными типами зарплат."""
        mock_salary = Mock()
        mock_salary.amount_from = "invalid"
        mock_salary.amount_to = "invalid"
        
        mock_vacancy = Mock()
        mock_vacancy.salary = mock_salary
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        assert result["without_salary_count"] == 1
    
    def test_vacancy_with_zero_salary(self):
        """Покрытие вакансий с нулевой зарплатой."""
        mock_salary = Mock()
        mock_salary.amount_from = 0
        mock_salary.amount_to = 0
        
        mock_vacancy = Mock()
        mock_vacancy.salary = mock_salary
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        assert result["without_salary_count"] == 1
    
    def test_vacancy_with_attribute_error(self):
        """Покрытие AttributeError при обработке зарплаты."""
        mock_vacancy = Mock()
        # Создаем объект, который вызовет AttributeError при обращении к salary
        del mock_vacancy.salary
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        assert result["without_salary_count"] == 1
    
    def test_multiple_vacancies_mixed(self):
        """Покрытие смешанного списка вакансий."""
        # Вакансия с зарплатой
        mock_salary1 = Mock()
        mock_salary1.amount_from = 100000
        mock_salary1.amount_to = None
        mock_vacancy1 = Mock()
        mock_vacancy1.salary = mock_salary1
        
        # Вакансия без зарплаты
        mock_vacancy2 = Mock()
        mock_vacancy2.salary = None
        
        # Вакансия с зарплатой to
        mock_salary3 = Mock()
        mock_salary3.amount_from = None
        mock_salary3.amount_to = 200000
        mock_vacancy3 = Mock()
        mock_vacancy3.salary = mock_salary3
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy1, mock_vacancy2, mock_vacancy3])
        
        assert result["count"] == 2
        assert result["with_salary_count"] == 2
        assert result["without_salary_count"] == 1
        assert result["min"] == 100000
        assert result["max"] == 200000
        assert result["average"] == 150000


class TestGetTopEmployers:
    """100% покрытие get_top_employers."""
    
    def test_empty_vacancies(self):
        """Покрытие пустого списка вакансий."""
        stats = VacancyStats()
        result = stats.get_top_employers([])
        assert result == []
    
    def test_vacancies_with_employers(self):
        """Покрытие вакансий с работодателями."""
        mock_employer1 = Mock()
        mock_employer1.name = "Company A"
        mock_vacancy1 = Mock()
        mock_vacancy1.employer = mock_employer1
        
        mock_employer2 = Mock()
        mock_employer2.name = "Company B"
        mock_vacancy2 = Mock()
        mock_vacancy2.employer = mock_employer2
        
        # Еще одна вакансия от Company A
        mock_vacancy3 = Mock()
        mock_vacancy3.employer = mock_employer1
        
        stats = VacancyStats()
        result = stats.get_top_employers([mock_vacancy1, mock_vacancy2, mock_vacancy3])
        
        # Company A должна быть первой (2 вакансии)
        assert result[0] == ("Company A", 2)
        assert result[1] == ("Company B", 1)
    
    def test_vacancies_without_employers(self):
        """Покрытие вакансий без работодателей."""
        mock_vacancy1 = Mock()
        mock_vacancy1.employer = None
        
        mock_vacancy2 = Mock()
        mock_vacancy2.employer = Mock()
        mock_vacancy2.employer.name = None
        
        stats = VacancyStats()
        result = stats.get_top_employers([mock_vacancy1, mock_vacancy2])
        
        assert result == []
    
    def test_top_n_parameter(self):
        """Покрытие параметра top_n."""
        vacancies = []
        for i in range(15):
            mock_employer = Mock()
            mock_employer.name = f"Company {i}"
            mock_vacancy = Mock()
            mock_vacancy.employer = mock_employer
            vacancies.append(mock_vacancy)
        
        stats = VacancyStats()
        result = stats.get_top_employers(vacancies, top_n=5)
        
        assert len(result) == 5


class TestGetSourceDistribution:
    """100% покрытие get_source_distribution."""
    
    def test_empty_vacancies(self):
        """Покрытие пустого списка вакансий."""
        stats = VacancyStats()
        result = stats.get_source_distribution([])
        assert result == {}
    
    def test_vacancies_with_sources(self):
        """Покрытие вакансий с источниками."""
        mock_vacancy1 = Mock()
        mock_vacancy1.source = "hh"
        
        mock_vacancy2 = Mock()
        mock_vacancy2.source = "superjob"
        
        mock_vacancy3 = Mock()
        mock_vacancy3.source = "hh"
        
        stats = VacancyStats()
        result = stats.get_source_distribution([mock_vacancy1, mock_vacancy2, mock_vacancy3])
        
        assert result == {"hh": 2, "superjob": 1}


class TestDisplayCompanyStats:
    """100% покрытие display_company_stats."""
    
    @patch('builtins.print')
    def test_empty_vacancies(self, mock_print):
        """Покрытие пустого списка вакансий."""
        stats = VacancyStats()
        stats.display_company_stats([])
        
        mock_print.assert_called_with("Нет вакансий для отображения статистики")
    
    @patch('builtins.print')
    def test_vacancies_dict_format(self, mock_print):
        """Покрытие вакансий в формате словаря."""
        vacancy_dict = {
            "employer": {
                "name": "Test Company"
            }
        }
        
        stats = VacancyStats()
        stats.display_company_stats([vacancy_dict], "Test Source")
        
        # Проверяем что функция была вызвана
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_vacancies_object_format(self, mock_print):
        """Покрытие вакансий в формате объектов."""
        mock_employer = Mock()
        mock_employer.name = "Object Company"
        mock_vacancy = Mock()
        mock_vacancy.employer = mock_employer
        
        stats = VacancyStats()
        stats.display_company_stats([mock_vacancy])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_vacancy_with_string_employer(self, mock_print):
        """Покрытие вакансии с работодателем-строкой."""
        vacancy_dict = {
            "employer": "String Company"
        }
        
        stats = VacancyStats()
        stats.display_company_stats([vacancy_dict])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_vacancy_with_exception(self, mock_print):
        """Покрытие исключения при обработке вакансии."""
        # Создаем mock объект, который будет вызывать исключение при доступе к employer.name
        mock_vacancy = Mock()
        mock_employer = Mock()
        
        # Настраиваем property name чтобы вызывал исключение при обращении
        def raise_error():
            raise Exception("Test error")
        
        type(mock_employer).name = property(lambda self: raise_error())
        mock_vacancy.employer = mock_employer
        
        stats = VacancyStats()
        stats.display_company_stats([mock_vacancy])
        
        # Проверяем что сообщение об ошибке было выведено
        mock_print.assert_any_call("Ошибка обработки вакансии для статистики: Test error")
    
    @patch('builtins.print')
    def test_no_company_stats(self, mock_print):
        """Покрытие случая когда не удалось определить статистику."""
        # Вакансия без информации о работодателе
        vacancy_dict = {}
        
        stats = VacancyStats()
        stats.display_company_stats([vacancy_dict])
        
        # Все вакансии попадут в "Неизвестная компания", так что статистика будет
        mock_print.assert_called()


class TestCalculateStatisticsFunction:
    """100% покрытие функции calculate_statistics."""
    
    def test_calculate_statistics_function(self):
        """Покрытие функции calculate_statistics."""
        mock_vacancy = Mock()
        mock_vacancy.source = "test"
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        mock_vacancy.salary = None
        
        result = calculate_statistics([mock_vacancy])
        
        assert "salary_stats" in result
        assert "top_employers" in result  
        assert "source_distribution" in result
        assert "total_count" in result
        assert result["total_count"] == 1


class TestVacancyStatsExtended:
    """100% покрытие VacancyStatsExtended методов."""
    
    def test_get_company_distribution_empty(self):
        """Покрытие get_company_distribution с пустым списком."""
        result = VacancyStatsExtended.get_company_distribution([])
        assert result == {}
    
    def test_get_company_distribution_with_data(self):
        """Покрытие get_company_distribution с данными."""
        vacancy = {"employer": {"name": "Test Company"}}
        result = VacancyStatsExtended.get_company_distribution([vacancy])
        assert result == {"Test Company": 1}
    
    def test_extract_company_name_vacancy_object_dict_employer(self):
        """Покрытие _extract_company_name для объекта с dict employer."""
        mock_vacancy = Mock()
        mock_vacancy.employer = {"name": "Dict Employer"}
        
        result = VacancyStatsExtended._extract_company_name(mock_vacancy)
        assert result == "Dict Employer"
    
    def test_extract_company_name_vacancy_object_string_employer(self):
        """Покрытие _extract_company_name для объекта со string employer."""
        mock_vacancy = Mock()
        mock_vacancy.employer = "String Employer"
        
        result = VacancyStatsExtended._extract_company_name(mock_vacancy)
        assert result == "String Employer"
    
    def test_extract_company_name_dict_hh_format(self):
        """Покрытие _extract_company_name для HH формата."""
        vacancy = {
            "employer": {
                "name": "HH Company"
            }
        }
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "HH Company"
    
    def test_extract_company_name_dict_employer_string(self):
        """Покрытие _extract_company_name для employer как строки."""
        vacancy = {
            "employer": "Employer String"
        }
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "Employer String"
    
    def test_extract_company_name_superjob_format(self):
        """Покрытие _extract_company_name для SuperJob формата."""
        vacancy = {
            "firm_name": "SuperJob Company",
            "firm_id": "123"
        }
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "SuperJob Company"
    
    def test_extract_company_name_raw_data(self):
        """Покрытие _extract_company_name для raw_data."""
        mock_vacancy = Mock()
        mock_vacancy.raw_data = {
            "employer": {
                "name": "Raw Data Company"
            }
        }
        # Убираем employer атрибут чтобы дойти до raw_data
        del mock_vacancy.employer
        
        result = VacancyStatsExtended._extract_company_name(mock_vacancy)
        assert result == "Raw Data Company"
    
    def test_extract_company_name_company_field(self):
        """Покрытие _extract_company_name для поля company."""
        vacancy = {
            "company": "company field value"
        }
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "Company Field Value"
    
    def test_extract_company_name_unknown(self):
        """Покрытие _extract_company_name для неизвестных случаев."""
        vacancy = {}
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "Неизвестная компания"
    
    def test_extract_company_name_none_values(self):
        """Покрытие _extract_company_name для None значений."""
        vacancy = {
            "firm_name": None,
            "company": "None"
        }
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "Неизвестная компания"
    
    @patch('builtins.print')
    def test_display_company_stats_static_empty(self, mock_print):
        """Покрытие статического display_company_stats с пустым списком."""
        VacancyStatsExtended.display_company_stats([])
        
        mock_print.assert_called_with("Нет вакансий для отображения статистики")
    
    @patch('builtins.print')
    def test_display_company_stats_static_no_stats(self, mock_print):
        """Покрытие статического display_company_stats без статистики."""
        # Создаем вакансию которая не даст статистики
        vacancy = {}
        
        with patch.object(VacancyStatsExtended, 'get_company_distribution', return_value={}):
            VacancyStatsExtended.display_company_stats([vacancy])
        
        mock_print.assert_called_with("Не удалось извлечь информацию о компаниях")
    
    @patch('builtins.print')
    def test_display_company_stats_static_with_stats(self, mock_print):
        """Покрытие статического display_company_stats с статистикой."""
        vacancy = {"employer": {"name": "Test Company"}}
        
        VacancyStatsExtended.display_company_stats([vacancy], "Test Source")
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_company_distribution(self, mock_print):
        """Покрытие _display_company_distribution."""
        company_stats = {"Company A": 5, "Company B": 3}
        
        VacancyStatsExtended._display_company_distribution(company_stats, 8, "Test Source")
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_source_stats_empty(self, mock_print):
        """Покрытие display_source_stats с пустыми списками."""
        VacancyStatsExtended.display_source_stats([], [])
        
        mock_print.assert_called_with("Нет вакансий для отображения статистики")
    
    @patch('builtins.print')
    def test_display_source_stats_with_data(self, mock_print):
        """Покрытие display_source_stats с данными."""
        hh_vacancy = {"employer": {"name": "HH Company"}}
        sj_vacancy = {"firm_name": "SJ Company"}
        
        with patch.object(VacancyStatsExtended, 'display_company_stats'):
            VacancyStatsExtended.display_source_stats([hh_vacancy], [sj_vacancy])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_source_stats_only_hh(self, mock_print):
        """Покрытие display_source_stats только с HH данными."""
        hh_vacancy = {"employer": {"name": "HH Company"}}
        
        with patch.object(VacancyStatsExtended, 'display_company_stats'):
            VacancyStatsExtended.display_source_stats([hh_vacancy], [])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_source_stats_only_sj(self, mock_print):
        """Покрытие display_source_stats только с SJ данными."""
        sj_vacancy = {"firm_name": "SJ Company"}
        
        with patch.object(VacancyStatsExtended, 'display_company_stats'):
            VacancyStatsExtended.display_source_stats([], [sj_vacancy])
        
        mock_print.assert_called()
    
    def test_analyze_company_mapping_empty(self):
        """Покрытие analyze_company_mapping с пустым списком."""
        result = VacancyStatsExtended.analyze_company_mapping([])
        
        expected = {
            "total_vacancies": 0,
            "with_employer": 0,
            "without_employer": 0,
            "employer_coverage": 0,
            "unique_employers": 0,
            "employer_names": [],
        }
        assert result == expected
    
    def test_analyze_company_mapping_with_data(self):
        """Покрытие analyze_company_mapping с данными."""
        vacancies = [
            {"employer": {"name": "Company A"}},
            {"employer": {"name": "Company B"}},
            {"employer": {"name": "Company A"}},  # Дубликат
            {}  # Без работодателя
        ]
        
        result = VacancyStatsExtended.analyze_company_mapping(vacancies)
        
        assert result["total_vacancies"] == 4
        assert result["with_employer"] == 3
        assert result["without_employer"] == 1
        assert result["employer_coverage"] == 75.0
        assert result["unique_employers"] == 2
        assert "Company A" in result["employer_names"]
        assert "Company B" in result["employer_names"]
    
    @patch('builtins.print')
    def test_display_company_mapping_analysis_empty(self, mock_print):
        """Покрытие display_company_mapping_analysis с пустыми данными."""
        with patch.object(VacancyStatsExtended, 'analyze_company_mapping', return_value={
            "total_vacancies": 0,
            "with_employer": 0,
            "without_employer": 0,
            "employer_coverage": 0,
            "unique_employers": 0,
            "employer_names": [],
        }):
            VacancyStatsExtended.display_company_mapping_analysis([])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_company_mapping_analysis_with_few_employers(self, mock_print):
        """Покрытие display_company_mapping_analysis с небольшим количеством работодателей."""
        employer_names = ["Company A", "Company B"]
        
        with patch.object(VacancyStatsExtended, 'analyze_company_mapping', return_value={
            "total_vacancies": 5,
            "with_employer": 4,
            "without_employer": 1,
            "employer_coverage": 80.0,
            "unique_employers": 2,
            "employer_names": employer_names,
        }):
            VacancyStatsExtended.display_company_mapping_analysis([])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_display_company_mapping_analysis_with_many_employers(self, mock_print):
        """Покрытие display_company_mapping_analysis с большим количеством работодателей."""
        employer_names = [f"Company {i}" for i in range(15)]
        
        with patch.object(VacancyStatsExtended, 'analyze_company_mapping', return_value={
            "total_vacancies": 20,
            "with_employer": 18,
            "without_employer": 2,
            "employer_coverage": 90.0,
            "unique_employers": 15,
            "employer_names": employer_names,
        }):
            VacancyStatsExtended.display_company_mapping_analysis([])
        
        mock_print.assert_called()


class TestEdgeCases:
    """Покрытие крайних случаев и специфичных ветвей кода."""
    
    def test_extract_company_name_with_employer_id_mapping(self):
        """Покрытие маппинга employer_id в SuperJob формате."""
        # Тестируем словарь с данными SuperJob для проверки firm_name и firm_id
        vacancy = {
            "firm_name": "Test Firm",
            "firm_id": "123"
        }
        
        # Метод должен найти firm_name в словаре
        result = VacancyStatsExtended._extract_company_name(vacancy)
        
        # Ожидаем, что метод вернет название фирмы
        assert result == "Test Firm"
    
    def test_salary_statistics_with_float_salaries(self):
        """Покрытие зарплат с float значениями."""
        mock_salary = Mock()
        mock_salary.amount_from = 100000.5
        mock_salary.amount_to = None
        
        mock_vacancy = Mock()
        mock_vacancy.salary = mock_salary
        
        stats = VacancyStats()
        result = stats.calculate_salary_statistics([mock_vacancy])
        
        # Проверяем что float преобразуется в int
        assert result["average"] == 100000
        assert result["min"] == 100000
        assert result["max"] == 100000
    
    def test_display_company_stats_object_with_dict_employer(self):
        """Покрытие объекта вакансии с dict employer."""
        mock_vacancy = Mock()
        mock_vacancy.employer = {"name": "Dict Employer"}
        
        stats = VacancyStats()
        
        with patch('builtins.print'):
            stats.display_company_stats([mock_vacancy])
    
    def test_extract_company_name_empty_strings(self):
        """Покрытие пустых строк в названиях компаний."""
        vacancy = {
            "employer": "",
            "firm_name": "  ",
            "company": ""
        }
        
        result = VacancyStatsExtended._extract_company_name(vacancy)
        assert result == "Неизвестная компания"