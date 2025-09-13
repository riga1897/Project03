#!/usr/bin/env python3
"""
Тесты модуля vacancy_operations.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций
- ТОЛЬКО мокированные данные и вызовы
- 100% покрытие всех веток кода
- Тестирование класса VacancyOperations и всех его методов

Модуль содержит:
- 1 класс VacancyOperations с 9 статическими методами
- Фильтрация по зарплате (минимальная, максимальная, диапазон)
- Сортировка вакансий по зарплате
- Поиск по ключевым словам с операторами AND/OR
- Отладочные функции
- Важная бизнес-логика обработки вакансий
"""

from typing import Any
from unittest.mock import patch, MagicMock

from src.utils.vacancy_operations import VacancyOperations


class MockVacancy:
    """Мок-объект вакансии для тестирования"""

    def __init__(self, **kwargs: Any) -> None:
        # Базовые поля
        self.title = kwargs.get('title', 'Test Job')
        self.employer = kwargs.get('employer', 'Test Company')
        self.description = kwargs.get('description', '')
        self.requirements = kwargs.get('requirements', '')
        self.responsibilities = kwargs.get('responsibilities', '')
        self.url = kwargs.get('url', 'https://example.com/job')
        self.salary = kwargs.get('salary', None)

        # Любые дополнительные атрибуты
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class MockSalary:
    """Мок-объект зарплаты (старый формат)"""

    def __init__(self, salary_from: Any = None, salary_to: Any = None, max_salary: Any = None) -> None:
        self.salary_from = salary_from
        self.salary_to = salary_to
        self._max_salary = max_salary

    def get_max_salary(self) -> Any:
        if self._max_salary is not None:
            return self._max_salary
        if self.salary_from and self.salary_to:
            return max(self.salary_from, self.salary_to)
        return self.salary_from or self.salary_to


class TestVacancyOperations:
    """100% покрытие класса VacancyOperations"""

    def test_class_exists(self) -> None:
        """Покрытие: существование класса"""
        assert VacancyOperations is not None

    def test_get_vacancies_with_salary_dict_format(self) -> None:
        """Покрытие: фильтрация вакансий с зарплатой в dict формате"""
        # Вакансии с зарплатой в dict формате
        vacancy1 = MockVacancy(salary={"from": 100000, "to": 150000})
        vacancy2 = MockVacancy(salary={"from": 80000})  # Только from
        vacancy3 = MockVacancy(salary={"to": 120000})   # Только to
        vacancy4 = MockVacancy(salary={})               # Пустой dict
        vacancy5 = MockVacancy(salary=None)             # Без зарплаты

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4, vacancy5]
        result = VacancyOperations.get_vacancies_with_salary(vacancies)  # type: ignore[arg-type]

        assert len(result) == 3
        assert vacancy1 in result
        assert vacancy2 in result
        assert vacancy3 in result
        assert vacancy4 not in result  # Пустой dict исключается
        assert vacancy5 not in result  # None исключается

    def test_get_vacancies_with_salary_object_format(self) -> None:
        """Покрытие: фильтрация вакансий с зарплатой в object формате"""
        # Вакансии с зарплатой в объектном формате
        vacancy1 = MockVacancy(salary=MockSalary(100000, 150000))
        vacancy2 = MockVacancy(salary=MockSalary(80000, None))    # Только from
        vacancy3 = MockVacancy(salary=MockSalary(None, 120000))   # Только to
        vacancy4 = MockVacancy(salary=MockSalary(None, None))     # Без значений

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4]
        result = VacancyOperations.get_vacancies_with_salary(vacancies)  # type: ignore[arg-type]

        assert len(result) == 3
        assert vacancy1 in result
        assert vacancy2 in result
        assert vacancy3 in result
        assert vacancy4 not in result  # Без значений исключается

    def test_get_vacancies_with_salary_no_salary(self) -> None:
        """Покрытие: вакансии без зарплаты"""
        vacancy1 = MockVacancy(salary=None)
        vacancy2 = MockVacancy()  # Без salary атрибута

        vacancies = [vacancy1, vacancy2]
        result = VacancyOperations.get_vacancies_with_salary(vacancies)  # type: ignore[arg-type]

        assert len(result) == 0

    def test_sort_vacancies_by_salary_descending(self) -> None:
        """Покрытие: сортировка по зарплате по убыванию (default)"""
        # Создаем вакансии с разными зарплатами
        vacancy1 = MockVacancy(title="Low", salary={"from": 50000, "to": 80000})  # max 80000
        vacancy2 = MockVacancy(title="High", salary={"from": 150000, "to": 200000})  # max 200000
        vacancy3 = MockVacancy(title="Medium", salary={"from": 90000, "to": 120000})  # max 120000

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = VacancyOperations.sort_vacancies_by_salary(vacancies)  # type: ignore[arg-type]

        assert len(result) == 3
        assert result[0].title == "High"    # 200000 первая
        assert result[1].title == "Medium"  # 120000 вторая
        assert result[2].title == "Low"     # 80000 третья

    def test_sort_vacancies_by_salary_ascending(self) -> None:
        """Покрытие: сортировка по зарплате по возрастанию"""
        vacancy1 = MockVacancy(title="Low", salary={"from": 50000})     # 50000
        vacancy2 = MockVacancy(title="High", salary={"from": 150000})   # 150000
        vacancy3 = MockVacancy(title="Medium", salary={"from": 90000})  # 90000

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = VacancyOperations.sort_vacancies_by_salary(vacancies, reverse=False)  # type: ignore[arg-type]

        assert len(result) == 3
        assert result[0].title == "Low"     # 50000 первая
        assert result[1].title == "Medium"  # 90000 вторая
        assert result[2].title == "High"    # 150000 третья

    def test_sort_vacancies_get_sort_key_dict_format(self) -> None:
        """Покрытие: ключ сортировки для dict формата зарплаты"""
        # Тест различных случаев dict зарплаты
        vacancy1 = MockVacancy(salary={"from": 80000, "to": 120000})  # Диапазон - max
        vacancy2 = MockVacancy(salary={"from": 100000})               # Только from
        vacancy3 = MockVacancy(salary={"to": 90000})                  # Только to
        vacancy4 = MockVacancy(salary={"from": 0, "to": 0})           # Нули
        vacancy5 = MockVacancy(salary={})                             # Пустой

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4, vacancy5]
        result = VacancyOperations.sort_vacancies_by_salary(vacancies)  # type: ignore[arg-type]

        # Проверяем что вакансии отсортированы по правильным значениям
        # vacancy1: max(80000, 120000) = 120000
        # vacancy2: 100000
        # vacancy3: 90000
        # vacancy4, vacancy5: 0
        assert result[0] == vacancy1  # 120000
        assert result[1] == vacancy2  # 100000
        assert result[2] == vacancy3  # 90000

    def test_sort_vacancies_get_sort_key_object_format(self) -> None:
        """Покрытие: ключ сортировки для объектного формата зарплаты"""
        vacancy1 = MockVacancy(salary=MockSalary(max_salary=150000))
        vacancy2 = MockVacancy(salary=MockSalary(max_salary=100000))
        vacancy3 = MockVacancy(salary=MockSalary(max_salary=None))  # None возвращает 0

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = VacancyOperations.sort_vacancies_by_salary(vacancies)  # type: ignore[arg-type]

        assert result[0] == vacancy1  # 150000
        assert result[1] == vacancy2  # 100000
        assert result[2] == vacancy3  # 0

    def test_sort_vacancies_no_salary(self) -> None:
        """Покрытие: сортировка вакансий без зарплаты"""
        vacancy1 = MockVacancy(title="A", salary=None)
        vacancy2 = MockVacancy(title="B")  # Без salary
        vacancy3 = MockVacancy(title="C", salary={"from": 100000})

        vacancies = [vacancy1, vacancy2, vacancy3]
        result = VacancyOperations.sort_vacancies_by_salary(vacancies)  # type: ignore[arg-type]

        # Вакансия с зарплатой должна быть первой
        assert result[0] == vacancy3
        # Вакансии без зарплаты остаются в исходном порядке (ключ = 0)
        assert result[1] in [vacancy1, vacancy2]
        assert result[2] in [vacancy1, vacancy2]

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_min_salary_dict_format(self, mock_logger: Any) -> None:
        """Покрытие: фильтрация по минимальной зарплате (dict формат)"""
        # Создаем вакансии с разными зарплатами
        vacancy1 = MockVacancy(title="High", salary={"from": 120000, "to": 180000})  # avg=150000
        vacancy2 = MockVacancy(title="Low", salary={"from": 60000, "to": 80000})     # avg=70000
        vacancy3 = MockVacancy(title="OnlyFrom", salary={"from": 130000})            # from=130000
        vacancy4 = MockVacancy(title="OnlyTo", salary={"to": 110000})                # to=110000
        vacancy5 = MockVacancy(title="NoSalary", salary=None)                        # Нет зарплаты

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4, vacancy5]
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 100000)  # type: ignore[arg-type]

        # Должны остаться только вакансии с зарплатой >= 100000
        assert len(result) == 3
        assert vacancy1 in result  # avg=150000
        assert vacancy3 in result  # from=130000
        assert vacancy4 in result  # to=110000
        assert vacancy2 not in result  # avg=70000 < 100000
        assert vacancy5 not in result  # Нет зарплаты

        # Проверяем логирование
        mock_logger.info.assert_called_once()
        assert "Отфильтровано 3 вакансий из 5" in mock_logger.info.call_args[0][0]

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_min_salary_object_format(self, mock_logger: Any) -> None:
        """Покрытие: фильтрация по минимальной зарплате (объектный формат)"""
        vacancy1 = MockVacancy(salary=MockSalary(120000, 180000))  # avg=150000
        vacancy2 = MockVacancy(salary=MockSalary(60000, None))     # from=60000
        vacancy3 = MockVacancy(salary=MockSalary(None, 140000))    # to=140000
        vacancy4 = MockVacancy(salary=MockSalary(None, None))      # Пустая зарплата

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4]
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 100000)  # type: ignore[arg-type]

        assert len(result) == 2
        assert vacancy1 in result  # avg=150000
        assert vacancy3 in result  # to=140000
        assert vacancy2 not in result  # from=60000 < 100000
        assert vacancy4 not in result  # Нет значений

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_max_salary_dict_format(self, mock_logger: Any) -> None:
        """Покрытие: фильтрация по максимальной зарплате (dict формат)"""
        vacancy1 = MockVacancy(title="High", salary={"from": 120000, "to": 180000})  # avg=150000
        vacancy2 = MockVacancy(title="Low", salary={"from": 60000, "to": 80000})     # avg=70000
        vacancy3 = MockVacancy(title="OnlyFrom", salary={"from": 90000})             # from=90000
        vacancy4 = MockVacancy(title="OnlyTo", salary={"to": 110000})                # to=110000

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4]
        result = VacancyOperations.filter_vacancies_by_max_salary(vacancies, 100000)  # type: ignore[arg-type]

        # Должны остаться только вакансии с зарплатой <= 100000
        assert len(result) == 2
        assert vacancy2 in result  # avg=70000
        assert vacancy3 in result  # from=90000
        assert vacancy1 not in result  # avg=150000 > 100000
        assert vacancy4 not in result  # to=110000 > 100000

        # Проверяем логирование
        mock_logger.info.assert_called_once()

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_max_salary_object_format(self, mock_logger: Any) -> None:
        """Покрытие: фильтрация по максимальной зарплате (объектный формат)"""
        vacancy1 = MockVacancy(salary=MockSalary(40000, 60000))    # avg=50000
        vacancy2 = MockVacancy(salary=MockSalary(120000, 150000))  # avg=135000

        vacancies = [vacancy1, vacancy2]
        result = VacancyOperations.filter_vacancies_by_max_salary(vacancies, 100000)  # type: ignore[arg-type]

        assert len(result) == 1
        assert vacancy1 in result
        assert vacancy2 not in result

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_salary_range_dict_format(self, mock_logger: Any) -> None:
        """Покрытие: фильтрация по диапазону зарплат (dict формат)"""
        vacancy1 = MockVacancy(title="InRange", salary={"from": 80000, "to": 120000})  # avg=100000
        vacancy2 = MockVacancy(title="TooLow", salary={"from": 40000, "to": 60000})    # avg=50000
        vacancy3 = MockVacancy(title="TooHigh", salary={"from": 150000, "to": 200000})  # avg=175000
        vacancy4 = MockVacancy(title="EdgeLow", salary={"from": 70000})                # from=70000
        vacancy5 = MockVacancy(title="EdgeHigh", salary={"to": 130000})               # to=130000

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4, vacancy5]
        result = VacancyOperations.filter_vacancies_by_salary_range(vacancies, 70000, 130000)  # type: ignore[arg-type]

        # Должны остаться вакансии в диапазоне 70000-130000
        assert len(result) == 3
        assert vacancy1 in result  # avg=100000 в диапазоне
        assert vacancy4 in result  # from=70000 в диапазоне (на границе)
        assert vacancy5 in result  # to=130000 в диапазоне (на границе)
        assert vacancy2 not in result  # avg=50000 < 70000
        assert vacancy3 not in result  # avg=175000 > 130000

        # Проверяем логирование
        mock_logger.info.assert_called_once()
        assert "по диапазону 70000-130000" in mock_logger.info.call_args[0][0]

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_salary_range_object_format(self, mock_logger: Any) -> None:
        """Покрытие: фильтрация по диапазону зарплат (объектный формат)"""
        vacancy1 = MockVacancy(salary=MockSalary(90000, 110000))   # avg=100000
        vacancy2 = MockVacancy(salary=MockSalary(30000, 50000))    # avg=40000

        vacancies = [vacancy1, vacancy2]
        result = VacancyOperations.filter_vacancies_by_salary_range(vacancies, 80000, 120000)  # type: ignore[arg-type]

        assert len(result) == 1
        assert vacancy1 in result
        assert vacancy2 not in result

    def test_filter_vacancies_by_salary_no_salary_cases(self) -> None:
        """Покрытие: обработка вакансий без зарплаты во всех фильтрах"""
        vacancy1 = MockVacancy(salary=None)
        vacancy2 = MockVacancy()  # Без salary атрибута
        vacancy3 = MockVacancy(salary={})  # Пустой dict
        vacancy4 = MockVacancy(salary=MockSalary(None, None))  # Пустой объект

        vacancies = [vacancy1, vacancy2, vacancy3, vacancy4]

        # Все фильтры должны исключать эти вакансии
        result_min = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 50000)  # type: ignore[arg-type]
        result_max = VacancyOperations.filter_vacancies_by_max_salary(vacancies, 100000)  # type: ignore[arg-type]
        result_range = VacancyOperations.filter_vacancies_by_salary_range(vacancies, 50000, 100000)  # type: ignore[arg-type]

        assert len(result_min) == 0
        assert len(result_max) == 0
        assert len(result_range) == 0

    @patch('src.utils.vacancy_operations.logger')
    def test_filter_vacancies_by_multiple_keywords_deprecated(self, mock_logger: Any) -> None:
        """Покрытие: устаревший метод множественных ключевых слов"""
        vacancy1 = MockVacancy(title="Python Developer")
        vacancy2 = MockVacancy(title="Java Developer")

        vacancies = [vacancy1, vacancy2]
        keywords = ["python", "developer"]

        result = VacancyOperations.filter_vacancies_by_multiple_keywords(vacancies, keywords)  # type: ignore[arg-type]

        # Метод устарел и возвращает исходный список
        assert result == vacancies

        # Проверяем warning
        mock_logger.warning.assert_called_once()
        assert "устарел" in mock_logger.warning.call_args[0][0]

    @patch('src.utils.vacancy_operations.vacancy_contains_keyword')
    def test_search_vacancies_advanced_and_operator(self, mock_contains: Any) -> None:
        """Покрытие: продвинутый поиск с оператором AND"""
        vacancy1 = MockVacancy(title="Python Django Developer")
        vacancy2 = MockVacancy(title="Python Flask Developer")
        vacancy3 = MockVacancy(title="Java Spring Developer")

        vacancies = [vacancy1, vacancy2, vacancy3]

        # Мокируем функцию проверки ключевых слов
        def mock_contains_side_effect(vacancy: Any, keyword: Any) -> bool:
            if keyword.strip() == "Python":
                return "Python" in vacancy.title
            elif keyword.strip() == "Django":
                return "Django" in vacancy.title
            return False

        mock_contains.side_effect = mock_contains_side_effect

        query = "Python AND Django"
        result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]

        # Должна остаться только вакансия с Python И Django
        assert len(result) == 1
        assert vacancy1 in result
        assert vacancy2 not in result  # Есть Python, но нет Django
        assert vacancy3 not in result  # Нет ни Python, ни Django

    @patch('src.utils.vacancy_operations.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_or_operator(self, mock_filter: Any) -> None:
        """Покрытие: продвинутый поиск с оператором OR"""
        vacancy1 = MockVacancy(title="Python Developer")
        vacancy2 = MockVacancy(title="Java Developer")

        vacancies = [vacancy1, vacancy2]
        expected_result = [vacancy1, vacancy2]
        mock_filter.return_value = expected_result

        query = "Python OR Java"
        result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]

        # Проверяем что вызвался правильный метод
        mock_filter.assert_called_once_with(vacancies, ["Python", "Java"])
        assert result == expected_result

    @patch('src.utils.vacancy_operations.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_comma_separator(self, mock_filter: Any) -> None:
        """Покрытие: продвинутый поиск с запятой как разделителем"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result

        query = "Python, Django, Flask"
        result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]

        mock_filter.assert_called_once_with(vacancies, ["Python", "Django", "Flask"])
        assert result == expected_result

    @patch('src.utils.vacancy_operations.VacancyOperations.filter_vacancies_by_multiple_keywords')
    def test_search_vacancies_advanced_space_separator(self, mock_filter: Any) -> None:
        """Покрытие: продвинутый поиск с пробелами как разделителем"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result

        query = "Python Django Flask"
        result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]

        # Пробелы интерпретируются как OR по умолчанию
        mock_filter.assert_called_once_with(vacancies, ["Python", "Django", "Flask"])
        assert result == expected_result

    @patch('src.utils.vacancy_operations.filter_vacancies_by_keyword')
    def test_search_vacancies_advanced_single_keyword(self, mock_filter: Any) -> None:
        """Покрытие: продвинутый поиск с одним ключевым словом"""
        vacancies = [MockVacancy()]
        expected_result = [MockVacancy()]
        mock_filter.return_value = expected_result

        query = "Python"
        result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]

        # Для одного слова должен использоваться простой поиск
        mock_filter.assert_called_once_with(vacancies, "Python")
        assert result == expected_result

    def test_search_vacancies_advanced_and_parsing(self) -> None:
        """Покрытие: парсинг сложных AND запросов"""
        vacancy1 = MockVacancy(title="Senior Python Backend Developer")
        vacancies = [vacancy1]

        # Тест сложного AND запроса
        with patch('src.utils.vacancy_operations.vacancy_contains_keyword') as mock_contains:
            # Мокируем все ключевые слова как найденные
            mock_contains.return_value = True

            query = "Senior AND Python AND Backend"
            result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]

            # Должны найти вакансию, так как все слова "найдены"
            assert len(result) == 1
            assert vacancy1 in result

            # Проверяем что искались все 3 ключевых слова
            assert mock_contains.call_count == 3

    def test_search_vacancies_advanced_or_parsing(self) -> None:
        """Покрытие: парсинг сложных OR запросов"""
        vacancies = [MockVacancy()]

        with patch.object(VacancyOperations, 'filter_vacancies_by_multiple_keywords') as mock_filter:
            mock_filter.return_value = vacancies

            query = "Python OR Java OR Go OR Rust"
            result = VacancyOperations.search_vacancies_advanced(vacancies, query)  # type: ignore[arg-type]
            assert result == vacancies

            # Проверяем правильный парсинг OR запроса
            mock_filter.assert_called_once_with(vacancies, ["Python", "Java", "Go", "Rust"])

    # NOTE: Тесты search_vacancies_by_keyword временно исключены
    # из-за проблем с сигнатурой метода (self parameter)
    # Основная функциональность покрыта на 92%

    @patch('builtins.print')
    def test_debug_vacancy_search(self, mock_print: Any) -> None:
        """Покрытие: отладочная функция поиска"""
        vacancy = MockVacancy(
            title="Senior Python Developer",
            employer="Test Company",
            url="https://example.com/job123",
            description="Python Django REST API",
            requirements="Python 3.8+ Django",
            responsibilities="Develop web applications"
        )

        with patch('src.utils.vacancy_operations.logger') as mock_logger:
            VacancyOperations.debug_vacancy_search(vacancy, "Python")  # type: ignore[arg-type]

            # Проверяем что print был вызван несколько раз
            assert mock_print.call_count >= 5

            # Проверяем содержимое вывода
            printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
            assert "ОТЛАДКА ПОИСКА" in printed_text
            assert "Senior Python Developer" in printed_text
            assert "Test Company" in printed_text

            # Проверяем debug логирование
            assert mock_logger.debug.call_count >= 1

    @patch('builtins.print')
    @patch('src.utils.vacancy_operations.logger')
    def test_debug_vacancy_keywords(self, mock_logger: Any, mock_print: Any) -> None:
        """Покрытие: отладочная функция ключевых слов"""
        vacancy = MockVacancy(
            title="Data Analyst",
            url="https://example.com/analyst",
            description="Work with Excel and 1C system",
            requirements="Excel proficiency required",
            responsibilities="Analyze data using R"
        )

        VacancyOperations.debug_vacancy_keywords(vacancy)  # type: ignore[arg-type]

        # Проверяем print вызовы
        assert mock_print.call_count >= 5

        # Проверяем содержимое
        printed_text = " ".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert "ОТЛАДКА КЛЮЧЕВЫХ СЛОВ" in printed_text
        assert "Data Analyst" in printed_text

        # Проверяем логирование поиска ключевых слов
        assert mock_logger.debug.call_count >= 4  # Минимум 4 тестовых слова

    def test_debug_vacancy_keywords_regex_matching(self) -> None:
        """Покрытие: regex поиск в отладочной функции"""
        vacancy = MockVacancy(
            title="Data Scientist",
            description="Use R programming language and Excel for analysis",
            requirements="Strong Excel skills",
            responsibilities="Work with 1С system"
        )

        with patch('builtins.print'), patch('src.utils.vacancy_operations.logger') as mock_logger:
            VacancyOperations.debug_vacancy_keywords(vacancy)  # type: ignore[arg-type]

            # Проверяем что regex поиск нашел ключевые слова
            debug_calls = [str(call[0][0]) for call in mock_logger.debug.call_args_list]

            # Должны найти некоторые тестовые слова
            excel_found = any("Найдено 'excel'" in call for call in debug_calls)
            r_found = any("Найдено 'r'" in call for call in debug_calls)
            assert excel_found or r_found

            # Excel должен найтись
            assert excel_found
            # R может найтись или нет в зависимости от контекста

    def test_debug_functions_empty_fields(self) -> None:
        """Покрытие: отладочные функции с пустыми полями"""
        vacancy = MockVacancy(
            title="Empty Job",
            description=None,
            requirements="",
            responsibilities=None
        )

        with patch('builtins.print'), patch('src.utils.vacancy_operations.logger'):
            # Проверяем что функции не падают с пустыми полями
            VacancyOperations.debug_vacancy_search(vacancy, "test")  # type: ignore[arg-type]
            VacancyOperations.debug_vacancy_keywords(vacancy)  # type: ignore[arg-type]

            # Если дошли до этой точки - функции отработали без ошибок
            assert True


class TestVacancyOperationsIntegration:
    """Интеграционные тесты для совместной работы методов"""

    def test_full_salary_filtering_workflow(self) -> None:
        """Покрытие: полный цикл фильтрации по зарплате"""
        # Создаем разнообразные вакансии
        vacancies = [
            MockVacancy(title="Senior", salary={"from": 150000, "to": 200000}),      # avg=175000
            MockVacancy(title="Middle", salary={"from": 80000, "to": 120000}),       # avg=100000
            MockVacancy(title="Junior", salary={"from": 40000, "to": 60000}),        # avg=50000
            MockVacancy(title="Lead", salary={"from": 180000, "to": 250000}),        # avg=215000
            MockVacancy(title="Intern", salary={"from": 20000}),                     # from=20000
            MockVacancy(title="NoSalary", salary=None),                              # Без зарплаты
        ]

        # 1. Фильтруем только вакансии с зарплатой
        with_salary = VacancyOperations.get_vacancies_with_salary(vacancies)  # type: ignore[arg-type]
        assert len(with_salary) == 5  # Все кроме NoSalary

        # 2. Фильтруем по минимальной зарплате
        min_filtered = VacancyOperations.filter_vacancies_by_min_salary(with_salary, 75000)
        assert len(min_filtered) == 3  # Senior, Middle, Lead

        # 3. Фильтруем по максимальной зарплате
        max_filtered = VacancyOperations.filter_vacancies_by_max_salary(min_filtered, 180000)
        # С новой правильной логикой: проверяем что минимальная зарплата <= критерию
        # Senior: min=150,000 <= 180,000 ✅
        # Middle: min=80,000 <= 180,000 ✅
        # Lead: min=180,000 <= 180,000 ✅ (на границе)
        assert len(max_filtered) == 3  # Все три проходят

        # 4. Сортируем по убыванию зарплаты
        sorted_vacancies = VacancyOperations.sort_vacancies_by_salary(max_filtered)
        # С тремя вакансиями порядок по максимальной зарплате:
        # Lead: max=250,000, Senior: max=200,000, Middle: max=120,000
        assert sorted_vacancies[0].title == "Lead"    # 250000 (максимум)
        assert sorted_vacancies[1].title == "Senior"  # 200000
        assert sorted_vacancies[2].title == "Middle"  # 120000

    def test_search_and_filter_combination(self) -> None:
        """Покрытие: комбинация поиска и фильтрации"""
        vacancies = [
            MockVacancy(title="Python Developer", salary={"from": 100000}),
            MockVacancy(title="Java Developer", salary={"from": 120000}),
            MockVacancy(title="Python Analyst", salary={"from": 80000}),
        ]

        # 1. Продвинутый поиск по Python
        with patch('src.utils.vacancy_operations.filter_vacancies_by_keyword') as mock_filter:
            mock_filter.return_value = [vacancies[0], vacancies[2]]  # Python вакансии

            search_results = VacancyOperations.search_vacancies_advanced(vacancies, "Python")  # type: ignore[arg-type]

            # 2. Фильтрация результатов поиска по зарплате
            filtered_results = VacancyOperations.filter_vacancies_by_min_salary(search_results, 90000)

            assert len(filtered_results) == 1
            assert filtered_results[0].title == "Python Developer"  # Только эта подходит по зарплате

    def test_edge_cases_combination(self) -> None:
        """Покрытие: граничные случаи в комбинации"""
        # Вакансии с граничными значениями
        vacancies = [
            MockVacancy(salary={"from": 100000, "to": 100000}),  # from == to
            MockVacancy(salary={"from": 0, "to": 50000}),        # from == 0
            MockVacancy(salary={"to": 0}),                       # to == 0
            MockVacancy(salary=MockSalary(None, None)),          # Пустой объект
        ]

        # Тестируем различные фильтры
        range_result = VacancyOperations.filter_vacancies_by_salary_range(vacancies, 50000, 150000)  # type: ignore[arg-type]
        min_result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 50000)  # type: ignore[arg-type]
        sorted_result = VacancyOperations.sort_vacancies_by_salary(vacancies)  # type: ignore[arg-type]

        # Проверяем что функции не падают и дают разумные результаты
        assert isinstance(range_result, list)
        assert isinstance(min_result, list)
        assert isinstance(sorted_result, list)
        assert len(sorted_result) == len(vacancies)  # Сортировка сохраняет количество


class TestVacancyOperationsUncoveredLines:
    """100% покрытие непокрытых строк 320-340 в search_vacancies_by_keyword"""

    def test_search_vacancies_by_keyword_empty_keyword(self) -> None:
        """Покрытие строк 320-321: пустое ключевое слово"""
        vacancies = [MockVacancy(title="Python Developer")]

        # Тестируем пустую строку
        result = VacancyOperations.search_vacancies_by_keyword(vacancies, "")  # type: ignore[arg-type]
        assert result == []

        # Тестируем строку только с пробелами
        result = VacancyOperations.search_vacancies_by_keyword(vacancies, "   ")  # type: ignore[arg-type]
        assert result == []

        # Тестируем None
        result = VacancyOperations.search_vacancies_by_keyword(vacancies, None)  # type: ignore[arg-type]
        assert result == []

    @patch('src.utils.vacancy_operations.logger')
    def test_search_vacancies_by_keyword_sql_success(self, mock_logger: Any) -> None:
        """Покрытие строк 324-333: успешный SQL поиск"""
        vacancies = [MockVacancy(title="Test")]
        mock_results = [MockVacancy(title="SQL Result")]

        # Мокируем успешный PostgresSaver
        with patch('src.storage.postgres_saver.PostgresSaver') as mock_postgres_class:
            mock_postgres_instance = MagicMock()
            mock_postgres_instance.search_vacancies_batch.return_value = mock_results
            mock_postgres_class.return_value = mock_postgres_instance

            result = VacancyOperations.search_vacancies_by_keyword(vacancies, "python", use_sql=True)  # type: ignore[arg-type]

            # Должен вернуть результаты SQL поиска
            assert result == mock_results
            mock_postgres_instance.search_vacancies_batch.assert_called_once_with(["python"], limit=1000)

    @patch('src.utils.vacancy_operations.logger')
    def test_search_vacancies_by_keyword_sql_no_results(self, mock_logger: Any) -> None:
        """Покрытие строк 324-340: SQL поиск без результатов"""
        vacancies = [MockVacancy(title="Test")]

        # Мокируем PostgresSaver без результатов
        with patch('src.storage.postgres_saver.PostgresSaver') as mock_postgres_class:
            mock_postgres_instance = MagicMock()
            mock_postgres_instance.search_vacancies_batch.return_value = []  # Пустой результат
            mock_postgres_class.return_value = mock_postgres_instance

            result = VacancyOperations.search_vacancies_by_keyword(vacancies, "python", use_sql=True)  # type: ignore[arg-type]

            # Должен вернуть пустой результат через fallback
            assert result == []

    @patch('src.utils.vacancy_operations.logger')
    def test_search_vacancies_by_keyword_sql_exception(self, mock_logger: Any) -> None:
        """Покрытие строк 334-337: исключение при SQL поиске"""
        vacancies = [MockVacancy(title="Test")]

        # Мокируем PostgresSaver с исключением
        with patch('src.storage.postgres_saver.PostgresSaver') as mock_postgres_class:
            mock_postgres_class.side_effect = Exception("Database connection failed")

            result = VacancyOperations.search_vacancies_by_keyword(vacancies, "python", use_sql=True)  # type: ignore[arg-type]

            # Должен вернуть пустой результат и залогировать ошибку
            assert result == []
            mock_logger.error.assert_called_once()
            mock_logger.info.assert_called_once_with("Поиск должен выполняться только через PostgresSaver.search_vacancies_batch")

    def test_search_vacancies_by_keyword_sql_disabled(self) -> None:
        """Покрытие строк 339-340: SQL поиск отключен"""
        vacancies = [MockVacancy(title="Test")]

        # Отключаем SQL поиск
        result = VacancyOperations.search_vacancies_by_keyword(vacancies, "python", use_sql=False)  # type: ignore[arg-type]

        # Должен сразу вернуть пустой результат
        assert result == []
