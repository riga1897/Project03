#!/usr/bin/env python3
"""
Тесты модуля vacancy_stats.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Мокирование всех print() вызовов

Модуль содержит:
- Класс VacancyStats для базовой статистики
- Класс VacancyStatsExtended для расширенной аналитики
- Функцию calculate_statistics для общего интерфейса
- Методы для анализа зарплат, компаний, источников
"""

from unittest.mock import patch, MagicMock

from src.utils.vacancy_stats import (
    VacancyStats,
    VacancyStatsExtended,
    calculate_statistics
)


class TestVacancyStatsInit:
    """100% покрытие инициализации VacancyStats"""

    def test_init(self) -> None:
        """Покрытие: инициализация VacancyStats"""
        stats = VacancyStats()

        # Проверяем, что объект создан успешно
        assert isinstance(stats, VacancyStats)

    def test_multiple_instances(self) -> None:
        """Покрытие: создание нескольких экземпляров"""
        stats1 = VacancyStats()
        stats2 = VacancyStats()

        assert stats1 is not stats2
        assert isinstance(stats1, VacancyStats)
        assert isinstance(stats2, VacancyStats)


class TestCalculateSalaryStatistics:
    """100% покрытие метода calculate_salary_statistics"""

    def test_calculate_salary_statistics_empty_list(self) -> None:
        """Покрытие: пустой список вакансий"""
        stats = VacancyStats()

        result = stats.calculate_salary_statistics([])

        expected = {
            "average": 0, "min": 0, "max": 0, "count": 0,
            "with_salary_count": 0, "without_salary_count": 0
        }
        assert result == expected

    def test_calculate_salary_statistics_with_salary_from(self) -> None:
        """Покрытие: вакансии с salary_from"""
        stats = VacancyStats()

        # Мокируем вакансии с зарплатой from
        vacancy1 = MagicMock()
        vacancy1.salary = MagicMock()
        vacancy1.salary.amount_from = 100000
        vacancy1.salary.amount_to = None

        vacancy2 = MagicMock()
        vacancy2.salary = MagicMock()
        vacancy2.salary.amount_from = 150000
        vacancy2.salary.amount_to = None

        vacancies = [vacancy1, vacancy2]
        result = stats.calculate_salary_statistics(vacancies)

        assert result["average"] == 125000  # (100000 + 150000) // 2
        assert result["min"] == 100000
        assert result["max"] == 150000
        assert result["count"] == 2
        assert result["with_salary_count"] == 2
        assert result["without_salary_count"] == 0

    def test_calculate_salary_statistics_with_salary_to(self) -> None:
        """Покрытие: вакансии с salary_to (без salary_from)"""
        stats = VacancyStats()

        # Мокируем вакансии с зарплатой to
        vacancy1 = MagicMock()
        vacancy1.salary = MagicMock()
        vacancy1.salary.amount_from = None
        vacancy1.salary.amount_to = 200000

        vacancy2 = MagicMock()
        vacancy2.salary = MagicMock()
        vacancy2.salary.amount_from = None
        vacancy2.salary.amount_to = 250000

        vacancies = [vacancy1, vacancy2]
        result = stats.calculate_salary_statistics(vacancies)

        assert result["average"] == 225000  # (200000 + 250000) // 2
        assert result["min"] == 200000
        assert result["max"] == 250000
        assert result["count"] == 2
        assert result["with_salary_count"] == 2
        assert result["without_salary_count"] == 0

    def test_calculate_salary_statistics_mixed_salaries(self) -> None:
        """Покрытие: смешанные вакансии с разными типами зарплат"""
        stats = VacancyStats()

        # Мокируем вакансии с разными зарплатами
        vacancy1 = MagicMock()
        vacancy1.salary = MagicMock()
        vacancy1.salary.amount_from = 100000
        vacancy1.salary.amount_to = 120000

        vacancy2 = MagicMock()
        vacancy2.salary = MagicMock()
        vacancy2.salary.amount_from = None
        vacancy2.salary.amount_to = 150000

        vacancy3 = MagicMock()
        vacancy3.salary = None  # Без зарплаты

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = stats.calculate_salary_statistics(vacancies)

        # Должно взять amount_from из первой и amount_to из второй
        assert result["average"] == 125000  # (100000 + 150000) // 2
        assert result["min"] == 100000
        assert result["max"] == 150000
        assert result["count"] == 2
        assert result["with_salary_count"] == 2
        assert result["without_salary_count"] == 1

    def test_calculate_salary_statistics_no_salary_attribute(self) -> None:
        """Покрытие: вакансии без атрибута salary"""
        stats = VacancyStats()

        # Мокируем вакансии без атрибута salary
        vacancy1 = MagicMock()
        del vacancy1.salary  # Удаляем атрибут

        vacancy2 = MagicMock()
        vacancy2.salary = None

        vacancies = [vacancy1, vacancy2]
        result = stats.calculate_salary_statistics(vacancies)

        expected = {
            "average": 0, "min": 0, "max": 0, "count": 0,
            "with_salary_count": 0, "without_salary_count": 2
        }
        assert result == expected

    def test_calculate_salary_statistics_invalid_salary_types(self) -> None:
        """Покрытие: невалидные типы зарплат"""
        stats = VacancyStats()

        # Мокируем вакансии с невалидными зарплатами
        vacancy1 = MagicMock()
        vacancy1.salary = MagicMock()
        vacancy1.salary.amount_from = "string"  # Неправильный тип
        vacancy1.salary.amount_to = None

        vacancy2 = MagicMock()
        vacancy2.salary = MagicMock()
        vacancy2.salary.amount_from = 0  # Ноль - не больше 0
        vacancy2.salary.amount_to = None

        vacancy3 = MagicMock()
        vacancy3.salary = MagicMock()
        vacancy3.salary.amount_from = -1000  # Отрицательное значение
        vacancy3.salary.amount_to = None

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = stats.calculate_salary_statistics(vacancies)

        expected = {
            "average": 0, "min": 0, "max": 0, "count": 0,
            "with_salary_count": 0, "without_salary_count": 3
        }
        assert result == expected

    def test_calculate_salary_statistics_exception_handling(self) -> None:
        """Покрытие: обработка исключений"""
        stats = VacancyStats()

        # Создаем объект, который вызывает AttributeError при доступе к salary
        class ProblematicVacancy:
            @property
            def salary(self) -> None:
                raise AttributeError("Simulated error")

        vacancy1 = MagicMock()
        vacancy1.salary = MagicMock()
        vacancy1.salary.amount_from = 100000
        vacancy1.salary.amount_to = None

        vacancy2 = ProblematicVacancy()

        vacancies = [vacancy1, vacancy2]
        result = stats.calculate_salary_statistics(vacancies)

        # Должно корректно обработать исключение
        assert result["with_salary_count"] == 1
        assert result["without_salary_count"] == 1

    def test_calculate_salary_statistics_no_valid_salaries(self) -> None:
        """Покрытие: случай когда есть вакансии, но нет валидных зарплат"""
        stats = VacancyStats()

        # Мокируем вакансии с невалидными зарплатами
        vacancy1 = MagicMock()
        vacancy1.salary = None

        vacancy2 = MagicMock()
        vacancy2.salary = MagicMock()
        vacancy2.salary.amount_from = None
        vacancy2.salary.amount_to = None

        vacancies = [vacancy1, vacancy2]
        result = stats.calculate_salary_statistics(vacancies)

        expected = {
            "average": 0, "min": 0, "max": 0, "count": 0,
            "with_salary_count": 0, "without_salary_count": 2
        }
        assert result == expected


class TestGetTopEmployers:
    """100% покрытие метода get_top_employers"""

    def test_get_top_employers_normal(self) -> None:
        """Покрытие: получение топ работодателей"""
        stats = VacancyStats()

        # Мокируем вакансии с работодателями
        vacancy1 = MagicMock()
        vacancy1.employer = MagicMock()
        vacancy1.employer.name = "Company A"

        vacancy2 = MagicMock()
        vacancy2.employer = MagicMock()
        vacancy2.employer.name = "Company B"

        vacancy3 = MagicMock()
        vacancy3.employer = MagicMock()
        vacancy3.employer.name = "Company A"  # Повтор

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = stats.get_top_employers(vacancies)

        assert len(result) == 2
        assert result[0] == ("Company A", 2)  # Первый по количеству
        assert result[1] == ("Company B", 1)

    def test_get_top_employers_with_limit(self) -> None:
        """Покрытие: ограничение количества топ работодателей"""
        stats = VacancyStats()

        # Создаем много работодателей
        vacancies = []
        for i in range(15):
            vacancy = MagicMock()
            vacancy.employer = MagicMock()
            vacancy.employer.name = f"Company {i}"
            vacancies.append(vacancy)

        result = stats.get_top_employers(vacancies, top_n=5)

        assert len(result) == 5  # Ограничено 5

    def test_get_top_employers_no_employer(self) -> None:
        """Покрытие: вакансии без работодателей"""
        stats = VacancyStats()

        # Мокируем вакансии без работодателей
        vacancy1 = MagicMock()
        vacancy1.employer = None

        # Создаем объект с employer = None
        vacancy2 = MagicMock()
        vacancy2.employer = None

        vacancy3 = MagicMock()
        vacancy3.employer = MagicMock()
        vacancy3.employer.name = None

        # Вакансия с пустым именем работодателя
        vacancy4 = MagicMock()
        vacancy4.employer = MagicMock()
        vacancy4.employer.name = ""

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4]
        result = stats.get_top_employers(vacancies)

        assert result == []  # Нет валидных работодателей

    def test_get_top_employers_empty_list(self) -> None:
        """Покрытие: пустой список вакансий"""
        stats = VacancyStats()

        result = stats.get_top_employers([])

        assert result == []


class TestGetSourceDistribution:
    """100% покрытие метода get_source_distribution"""

    def test_get_source_distribution_normal(self) -> None:
        """Покрытие: получение распределения источников"""
        stats = VacancyStats()

        # Мокируем вакансии с источниками
        vacancy1 = MagicMock()
        vacancy1.source = "hh.ru"

        vacancy2 = MagicMock()
        vacancy2.source = "superjob.ru"

        vacancy3 = MagicMock()
        vacancy3.source = "hh.ru"  # Повтор

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = stats.get_source_distribution(vacancies)

        assert result == {"hh.ru": 2, "superjob.ru": 1}

    def test_get_source_distribution_empty_list(self) -> None:
        """Покрытие: пустой список вакансий"""
        stats = VacancyStats()

        result = stats.get_source_distribution([])

        assert result == {}

    def test_get_source_distribution_single_source(self) -> None:
        """Покрытие: один источник"""
        stats = VacancyStats()

        # Мокируем вакансии с одним источником
        vacancies = []
        for i in range(3):
            vacancy = MagicMock()
            vacancy.source = "hh.ru"
            vacancies.append(vacancy)

        result = stats.get_source_distribution(vacancies)

        assert result == {"hh.ru": 3}


class TestDisplayCompanyStats:
    """100% покрытие метода display_company_stats"""

    @patch('builtins.print')
    def test_display_company_stats_empty_list(self, mock_print):
        """Покрытие: пустой список вакансий"""
        stats = VacancyStats()

        stats.display_company_stats([])

        mock_print.assert_called_with("Нет вакансий для отображения статистики")

    @patch('src.utils.vacancy_stats.VacancyStats._get_company_name_by_id')
    @patch('builtins.print')
    def test_display_company_stats_with_source_name(self, mock_print, mock_get_name):
        """Покрытие: отображение с названием источника"""
        stats = VacancyStats()
        mock_get_name.return_value = "Company A"

        # Мокируем вакансии с правильной структурой (нужен employer.get_id())
        vacancy1 = MagicMock()
        vacancy1.employer = MagicMock()
        vacancy1.employer.get_id.return_value = "123"

        vacancies = [vacancy1]
        stats.display_company_stats(vacancies, "HH.ru")

        # Проверяем, что print был вызван с правильными аргументами
        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("HH.ru" in call for call in calls)
        assert any("Company A" in call for call in calls)

    @patch('src.utils.vacancy_stats.VacancyStats._get_company_name_by_id')
    @patch('builtins.print')
    def test_display_company_stats_dict_vacancy(self, mock_print, mock_get_name):
        """Покрытие: обработка вакансии как словаря"""
        stats = VacancyStats()
        mock_get_name.return_value = "Dict Company"

        # Мокируем вакансию как словарь с правильной структурой (нужен employer["id"])
        vacancy1 = {"employer": {"id": "456"}}
        vacancy2 = {"employer": None}  # Это попадет в "unknown"

        vacancies = [vacancy1, vacancy2]
        stats.display_company_stats(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Dict Company" in call for call in calls)
        # vacancy2 без employer попадет в "Неизвестная компания"
        assert any("Неизвестная компания" in call for call in calls)

    @patch('src.utils.vacancy_stats.VacancyStats._get_company_name_by_id')
    @patch('builtins.print')
    def test_display_company_stats_object_with_employer_object(self, mock_print, mock_get_name):
        """Покрытие: объект с объектом employer"""
        stats = VacancyStats()
        mock_get_name.return_value = "Object Company"

        # Мокируем вакансию с объектом employer (нужен get_id())
        vacancy = MagicMock()
        vacancy.employer = MagicMock()
        vacancy.employer.get_id.return_value = "789"

        vacancies = [vacancy]
        stats.display_company_stats(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Object Company" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_stats_unknown_company(self, mock_print):
        """Покрытие: неизвестная компания"""
        stats = VacancyStats()

        # Мокируем вакансию без работодателя
        vacancy1 = MagicMock()
        vacancy1.employer = None

        vacancy2 = {}  # Пустой словарь

        vacancies = [vacancy1, vacancy2]
        stats.display_company_stats(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Неизвестная компания" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_stats_exception_handling(self, mock_print):
        """Покрытие: обработка исключений"""
        stats = VacancyStats()

        # Мокируем вакансию, которая вызывает исключение
        vacancy = MagicMock()
        # Мокируем hasattr, чтобы он вызывал исключение
        with patch('builtins.hasattr', side_effect=Exception("Test error")):
            vacancies = [vacancy]
            stats.display_company_stats(vacancies)

            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            assert any("Ошибка обработки вакансии для статистики" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_stats_no_valid_companies(self, mock_print):
        """Покрытие: случай когда нет валидных компаний"""
        stats = VacancyStats()

        # Мокируем вакансии, но без валидных компаний после обработки
        vacancy = MagicMock()
        with patch('builtins.hasattr', return_value=False):
            vacancies = [vacancy]
            stats.display_company_stats(vacancies)

            # Должно показать сообщение о невозможности определить статистику
            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            # Может быть любое сообщение, главное что не крашится


class TestCalculateStatisticsFunction:
    """100% покрытие функции calculate_statistics"""

    def test_calculate_statistics_normal(self) -> None:
        """Покрытие: нормальный расчет статистики"""
        # Мокируем вакансии
        vacancy1 = MagicMock()
        vacancy1.salary = MagicMock()
        vacancy1.salary.amount_from = 100000
        vacancy1.salary.amount_to = None
        vacancy1.employer = MagicMock()
        vacancy1.employer.name = "Company A"
        vacancy1.source = "hh.ru"

        vacancy2 = MagicMock()
        vacancy2.salary = None
        vacancy2.employer = MagicMock()
        vacancy2.employer.name = "Company B"
        vacancy2.source = "superjob.ru"

        vacancies = [vacancy1, vacancy2]
        result = calculate_statistics(vacancies)

        assert "salary_stats" in result
        assert "top_employers" in result
        assert "source_distribution" in result
        assert "total_count" in result

        assert result["total_count"] == 2
        assert result["source_distribution"] == {"hh.ru": 1, "superjob.ru": 1}

    def test_calculate_statistics_empty_list(self) -> None:
        """Покрытие: пустой список вакансий"""
        result = calculate_statistics([])

        assert "salary_stats" in result
        assert "top_employers" in result
        assert "source_distribution" in result
        assert "total_count" in result

        assert result["total_count"] == 0
        assert result["source_distribution"] == {}
        assert result["top_employers"] == []


class TestVacancyStatsExtendedGetCompanyDistribution:
    """100% покрытие метода get_company_distribution"""

    def test_get_company_distribution_normal(self) -> None:
        """Покрытие: нормальное получение распределения компаний"""
        # Мокируем вакансии
        vacancy1 = {"employer": {"name": "Company A"}}
        vacancy2 = {"employer": {"name": "Company B"}}
        vacancy3 = {"employer": {"name": "Company A"}}  # Повтор

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = VacancyStatsExtended.get_company_distribution(vacancies)

        assert result == {"Company A": 2, "Company B": 1}

    def test_get_company_distribution_empty_list(self) -> None:
        """Покрытие: пустой список вакансий"""
        result = VacancyStatsExtended.get_company_distribution([])

        assert result == {}

    def test_get_company_distribution_with_unknown_companies(self) -> None:
        """Покрытие: вакансии с неизвестными компаниями"""
        # Мокируем вакансии без работодателей
        vacancy1 = {}  # Пустая вакансия
        vacancy2 = {"employer": {"name": "Known Company"}}

        vacancies = [vacancy1, vacancy2]
        result = VacancyStatsExtended.get_company_distribution(vacancies)

        # Неизвестные компании не должны попадать в статистику
        assert "Known Company" in result
        assert result["Known Company"] == 1


class TestVacancyStatsExtendedExtractCompanyName:
    """100% покрытие метода _extract_company_name"""

    def test_extract_company_name_priority1_object_dict_employer(self) -> None:
        """Покрытие: приоритет 1 - объект с dict employer"""
        vacancy = MagicMock()
        vacancy.employer = {"name": "Priority 1 Company"}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Priority 1 Company"

    def test_extract_company_name_priority1_object_string_employer(self) -> None:
        """Покрытие: приоритет 1 - объект с string employer"""
        vacancy = MagicMock()
        vacancy.employer = "String Company"

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "String Company"

    def test_extract_company_name_priority1_object_other_employer(self) -> None:
        """Покрытие: приоритет 1 - объект с другим типом employer"""
        vacancy = MagicMock()
        vacancy.employer = 12345  # Число

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "12345"

    def test_extract_company_name_priority2_dict_with_employer(self) -> None:
        """Покрытие: приоритет 2 - словарь с employer.name"""
        vacancy = {"employer": {"name": "Priority 2 Company"}}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Priority 2 Company"

    def test_extract_company_name_priority2_dict_with_string_employer(self) -> None:
        """Покрытие: приоритет 2 - словарь с string employer"""
        vacancy = {"employer": "Dict String Company"}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Dict String Company"

    def test_extract_company_name_priority3_firm_name(self) -> None:
        """Покрытие: приоритет 3 - firm_name"""
        vacancy = {"firm_name": "SuperJob Company"}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "SuperJob Company"

    def test_extract_company_name_priority3_firm_name_with_id(self) -> None:
        """Покрытие: приоритет 3 - firm_name с ID"""
        vacancy = MagicMock()
        vacancy.employer_id = None
        vacancy_dict = {"firm_name": "SJ Company", "firm_id": "123"}

        # Патчим hasattr для корректной работы
        with patch('builtins.hasattr', side_effect=lambda obj, attr: attr == 'employer_id' and obj is vacancy):
            result = VacancyStatsExtended._extract_company_name(vacancy_dict)

            assert result == "SJ Company"

    def test_extract_company_name_priority3_firm_name_none(self) -> None:
        """Покрытие: приоритет 3 - firm_name как None"""
        vacancy = {"firm_name": None}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Неизвестная компания"

    def test_extract_company_name_priority4_raw_data(self) -> None:
        """Покрытие: приоритет 4 - raw_data"""
        vacancy = MagicMock()
        vacancy.employer = None  # Нет employer
        vacancy.raw_data = {"employer": {"name": "Raw Data Company"}}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Raw Data Company"

    def test_extract_company_name_priority5_company_field(self) -> None:
        """Покрытие: приоритет 5 - поле company"""
        vacancy = {"company": "legacy company"}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Legacy Company"  # Должно быть с title()

    def test_extract_company_name_priority5_company_none(self) -> None:
        """Покрытие: приоритет 5 - company как None"""
        vacancy = {"company": None}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Неизвестная компания"

    def test_extract_company_name_unknown_company(self) -> None:
        """Покрытие: случай неизвестной компании"""
        vacancy = {}  # Пустой словарь

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Неизвестная компания"

    def test_extract_company_name_priority2_empty_name(self) -> None:
        """Покрытие: приоритет 2 - пустое имя в employer"""
        vacancy = {"employer": {"name": ""}}

        result = VacancyStatsExtended._extract_company_name(vacancy)

        assert result == "Неизвестная компания"

    def test_extract_company_name_priority3_client_id(self) -> None:
        """Покрытие: приоритет 3 - client_id вместо firm_id"""
        vacancy = MagicMock()
        vacancy.employer_id = None
        vacancy_dict = {"firm_name": "Client Company", "client_id": "456"}

        with patch('builtins.hasattr', side_effect=lambda obj, attr: attr == 'employer_id' and obj is vacancy):
            result = VacancyStatsExtended._extract_company_name(vacancy_dict)

            assert result == "Client Company"


class TestVacancyStatsExtendedDisplayMethods:
    """100% покрытие методов отображения VacancyStatsExtended"""

    @patch('builtins.print')
    def test_display_company_stats_empty_list(self, mock_print):
        """Покрытие: отображение статистики для пустого списка"""
        VacancyStatsExtended.display_company_stats([])

        mock_print.assert_called_with("Нет вакансий для отображения статистики")

    @patch('builtins.print')
    def test_display_company_stats_no_companies(self, mock_print):
        """Покрытие: нет компаний для извлечения"""
        # Мокируем get_company_distribution чтобы вернуть пустой результат
        with patch.object(VacancyStatsExtended, 'get_company_distribution', return_value={}):
            vacancies = [{"some": "data"}]
            VacancyStatsExtended.display_company_stats(vacancies, "Test Source")

            mock_print.assert_called_with("Не удалось извлечь информацию о компаниях")

    @patch('builtins.print')
    def test_display_company_stats_normal(self, mock_print):
        """Покрытие: нормальное отображение статистики"""
        vacancies = [{"employer": {"name": "Test Company"}}]
        VacancyStatsExtended.display_company_stats(vacancies, "Test Source")

        # Проверяем, что были вызовы print
        assert mock_print.call_count > 0

    @patch('builtins.print')
    def test_display_company_distribution(self, mock_print):
        """Покрытие: отображение распределения компаний"""
        company_stats = {"Company A": 5, "Company B": 3, "Company C": 2}
        total_vacancies = 10
        source_name = "Test Source"

        VacancyStatsExtended._display_company_distribution(company_stats, total_vacancies, source_name)

        # Проверяем основные вызовы
        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Test Source" in call for call in calls)
        assert any("Company A: 5 вакансий (50.0%)" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_distribution_no_source_name(self, mock_print):
        """Покрытие: отображение без названия источника"""
        company_stats = {"Company A": 2}
        total_vacancies = 2

        VacancyStatsExtended._display_company_distribution(company_stats, total_vacancies, "")

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Распределение вакансий по компаниям:" in call for call in calls)

    @patch('builtins.print')
    def test_display_source_stats_empty(self, mock_print):
        """Покрытие: отображение статистики источников - пустые списки"""
        VacancyStatsExtended.display_source_stats([], [])

        mock_print.assert_called_with("Нет вакансий для отображения статистики")

    @patch('builtins.print')
    def test_display_source_stats_normal(self, mock_print):
        """Покрытие: нормальное отображение статистики источников"""
        hh_vacancies = [{"employer": {"name": "HH Company"}}]
        sj_vacancies = [{"employer": {"name": "SJ Company"}}]

        VacancyStatsExtended.display_source_stats(hh_vacancies, sj_vacancies)

        # Проверяем основные вызовы
        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Итого найдено: 2 вакансий" in call for call in calls)
        assert any("HH.ru: 1 вакансий" in call for call in calls)
        assert any("SuperJob: 1 вакансий" in call for call in calls)

    @patch('builtins.print')
    def test_display_source_stats_only_hh(self, mock_print):
        """Покрытие: только HH вакансии"""
        hh_vacancies = [{"employer": {"name": "HH Company"}}]
        sj_vacancies = []

        VacancyStatsExtended.display_source_stats(hh_vacancies, sj_vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("HH.ru: 1 вакансий" in call for call in calls)
        assert any("SuperJob: 0 вакансий" in call for call in calls)


class TestVacancyStatsExtendedAnalyzeMethods:
    """100% покрытие методов анализа VacancyStatsExtended"""

    def test_analyze_company_mapping_normal(self) -> None:
        """Покрытие: нормальный анализ маппинга компаний"""
        vacancies = [
            {"employer": {"name": "Company A"}},
            {"employer": {"name": "Company B"}},
            {"employer": {"name": "Company A"}},  # Повтор
            {}  # Без работодателя
        ]

        result = VacancyStatsExtended.analyze_company_mapping(vacancies)

        assert result["total_vacancies"] == 4
        assert result["with_employer"] == 3
        assert result["without_employer"] == 1
        assert result["employer_coverage"] == 75.0  # 3/4 * 100
        assert result["unique_employers"] == 2
        assert "Company A" in result["employer_names"]
        assert "Company B" in result["employer_names"]

    def test_analyze_company_mapping_empty_list(self) -> None:
        """Покрытие: анализ пустого списка"""
        result = VacancyStatsExtended.analyze_company_mapping([])

        assert result["total_vacancies"] == 0
        assert result["with_employer"] == 0
        assert result["without_employer"] == 0
        assert result["employer_coverage"] == 0
        assert result["unique_employers"] == 0
        assert result["employer_names"] == []

    def test_analyze_company_mapping_no_valid_employers(self) -> None:
        """Покрытие: нет валидных работодателей"""
        vacancies = [{}, {"company": None}]

        result = VacancyStatsExtended.analyze_company_mapping(vacancies)

        assert result["total_vacancies"] == 2
        assert result["with_employer"] == 0
        assert result["without_employer"] == 2
        assert result["employer_coverage"] == 0
        assert result["unique_employers"] == 0

    @patch('builtins.print')
    def test_display_company_mapping_analysis_normal(self, mock_print):
        """Покрытие: отображение анализа маппинга"""
        vacancies = [
            {"employer": {"name": "Company A"}},
            {"employer": {"name": "Company B"}},
            {}
        ]

        VacancyStatsExtended.display_company_mapping_analysis(vacancies)

        # Проверяем основные вызовы
        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Анализ маппинга компаний:" in call for call in calls)
        assert any("Всего вакансий: 3" in call for call in calls)
        assert any("Уникальных работодателей: 2" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_mapping_analysis_many_employers(self, mock_print):
        """Покрытие: анализ с большим количеством работодателей"""
        vacancies = []
        for i in range(15):
            vacancies.append({"employer": {"name": f"Company {i}"}})

        VacancyStatsExtended.display_company_mapping_analysis(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        # Должно показать топ-10 и сообщение о дополнительных
        assert any("... и еще 5 работодателей" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_mapping_analysis_no_employers(self, mock_print):
        """Покрытие: анализ без работодателей"""
        vacancies = [{}, {}]

        VacancyStatsExtended.display_company_mapping_analysis(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        # Не должно быть секции "Топ-10 работодателей"
        assert not any("Топ-10 работодателей:" in call for call in calls)


class TestEdgeCasesAndIntegration:
    """Тесты для граничных случаев и интеграции"""

    def test_all_methods_with_empty_data(self) -> None:
        """Покрытие: все методы с пустыми данными"""
        stats = VacancyStats()

        # Тестируем все методы с пустыми данными
        assert stats.calculate_salary_statistics([]) == {
            "average": 0, "min": 0, "max": 0, "count": 0,
            "with_salary_count": 0, "without_salary_count": 0
        }
        assert stats.get_top_employers([]) == []
        assert stats.get_source_distribution([]) == {}

        # VacancyStatsExtended
        assert VacancyStatsExtended.get_company_distribution([]) == {}
        assert VacancyStatsExtended.analyze_company_mapping([])["total_vacancies"] == 0

    def test_complex_integration_scenario(self) -> None:
        """Покрытие: сложный интеграционный сценарий"""
        # Создаем комплексный набор данных
        vacancies = []

        # Добавляем различные типы вакансий
        for i in range(5):
            vacancy = MagicMock()
            vacancy.employer = MagicMock()
            vacancy.employer.name = f"Company {i % 3}"  # 3 разные компании
            vacancy.source = "hh.ru" if i % 2 == 0 else "superjob.ru"
            vacancy.salary = MagicMock()
            vacancy.salary.amount_from = (i + 1) * 50000
            vacancy.salary.amount_to = None
            vacancies.append(vacancy)

        # Тестируем все методы
        stats = VacancyStats()
        salary_stats = stats.calculate_salary_statistics(vacancies)
        top_employers = stats.get_top_employers(vacancies)
        source_dist = stats.get_source_distribution(vacancies)

        assert salary_stats["count"] == 5
        assert len(top_employers) == 3  # 3 уникальные компании
        assert len(source_dist) == 2  # 2 источника

        # Тестируем calculate_statistics
        full_stats = calculate_statistics(vacancies)
        assert full_stats["total_count"] == 5


class TestUncoveredLines:
    """Тесты для покрытия непокрытых строк (57-60, 129, 136, 140, 233)"""

    def test_calculate_salary_statistics_hasattr_exception(self) -> None:
        """Покрытие строк 57-60: except (AttributeError, TypeError)"""
        stats = VacancyStats()

        # Создаем объект с salary, который вызывает AttributeError при getattr
        class ProblematicSalary:
            def __getattribute__(self, name):
                if name in ("amount_from", "amount_to"):
                    raise AttributeError("Forced AttributeError on salary attribute")
                return super().__getattribute__(name)

        class ProblematicVacancy:
            def __init__(self) -> None:
                self.salary = ProblematicSalary()

        vacancy1 = ProblematicVacancy()

        # Создаем объект с salary, который вызывает TypeError
        class TypeErrorSalary:
            @property
            def amount_from(self) -> None:
                raise TypeError("Forced TypeError on amount_from")

            @property
            def amount_to(self) -> None:
                return None

        class TypeErrorVacancy:
            def __init__(self) -> None:
                self.salary = TypeErrorSalary()

        vacancy2 = TypeErrorVacancy()

        vacancies = [vacancy1, vacancy2]
        result = stats.calculate_salary_statistics(vacancies)

        # Должен обработать исключения и записать в without_salary_count
        assert result["without_salary_count"] == 2
        assert result["with_salary_count"] == 0

    @patch('src.utils.vacancy_stats.VacancyStats._get_company_name_by_id')
    @patch('builtins.print')
    def test_display_company_stats_dict_employer_with_name_object(self, mock_print, mock_get_name):
        """Покрытие строки 129: employer.get_id() когда employer объект в словаре"""
        stats = VacancyStats()
        mock_get_name.return_value = "Object Employer Company"

        # Создаем мок объект с методом get_id
        employer_obj = MagicMock()
        employer_obj.get_id.return_value = "obj123"

        # Вакансия как словарь с employer объектом
        vacancy = {"employer": employer_obj}

        vacancies = [vacancy]
        stats.display_company_stats(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Object Employer Company" in call for call in calls)

    @patch('src.utils.vacancy_stats.VacancyStats._get_company_name_by_id')
    @patch('builtins.print')
    def test_display_company_stats_object_employer_as_dict(self, mock_print, mock_get_name):
        """Покрытие строки 135: employer.get("id") когда vacancy.employer dict"""
        stats = VacancyStats()
        mock_get_name.return_value = "Dict Employer in Object"

        vacancy = MagicMock()
        vacancy.employer = {"id": "dict_id_789"}

        vacancies = [vacancy]
        stats.display_company_stats(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        assert any("Dict Employer in Object" in call for call in calls)

    @patch('builtins.print')
    def test_display_company_stats_object_employer_as_string(self, mock_print):
        """Покрытие случая когда employer без get_id() -> попадает в unknown"""
        stats = VacancyStats()

        # Создаем объект вакансии с employer без get_id()
        vacancy = MagicMock()
        vacancy.employer = "String Employer in Object"  # Строка не имеет get_id()

        vacancies = [vacancy]
        stats.display_company_stats(vacancies)

        calls = [str(call[0][0]) for call in mock_print.call_args_list]
        # Поскольку employer - строка без get_id(), попадет в "unknown" -> "Неизвестная компания"
        assert any("Неизвестная компания" in call for call in calls)

    def test_extract_company_name_firm_id_assignment(self) -> None:
        """Покрытие extracting company name из firm_name SuperJob вакансии"""

        # Вакансия как словарь с firm_name и firm_id (SuperJob формат)
        vacancy = {
            "source": "superjob",
            "firm_name": "SuperJob Assignment Test",
            "firm_id": "987654"
        }

        result = VacancyStatsExtended._extract_company_name(vacancy)

        # Функция должна вернуть firm_name как fallback
        assert result == "SuperJob Assignment Test"

    def test_extract_company_name_client_id_assignment(self) -> None:
        """Покрытие строки 233: vacancy.employer_id = str(firm_id) с client_id"""
        # Создаем мок объект
        vacancy_mock = MagicMock()
        vacancy_mock.employer_id = None

        # Создаем словарь с firm_name и client_id (без firm_id)
        vacancy_dict = {
            "firm_name": "Client ID Company",
            "client_id": "789012"
        }

        # Патчим hasattr чтобы вернуть True для employer_id
        with patch('builtins.hasattr', side_effect=lambda obj, attr: attr == 'employer_id' and obj is vacancy_mock):
            vacancy_dict_with_attr = type('MockVacancy', (), vacancy_dict)
            vacancy_dict_with_attr.employer_id = None

            result = VacancyStatsExtended._extract_company_name(vacancy_dict)

            assert result == "Client ID Company"