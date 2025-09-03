"""
Расширенные тесты для модуля vacancy_operations
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pytest

# Мокаем psycopg2 перед импортом
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.sql'] = MagicMock()

# Добавляем путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.vacancy_operations import VacancyOperations


class MockSalary:
    """Мок зарплаты"""
    
    def __init__(self, salary_from=None, salary_to=None):
        self.salary_from = salary_from
        self.salary_to = salary_to
    
    def get_max_salary(self):
        """Возвращает максимальную зарплату"""
        if self.salary_to:
            return self.salary_to
        if self.salary_from:
            return self.salary_from
        return None


class MockVacancy:
    """Мок вакансии"""
    
    def __init__(self, title="Test Job", salary=None):
        self.title = title
        self.salary = salary
        self.employer = Mock()
        self.employer.name = "Test Company"
        self.url = "http://test.com"


class TestVacancyOperations:
    """Расширенные тесты для операций с вакансиями"""
    
    def test_get_vacancies_with_salary_valid_salaries(self):
        """Тест фильтрации вакансий с валидными зарплатами"""
        vacancies = [
            MockVacancy("Job 1", MockSalary(100000, 150000)),
            MockVacancy("Job 2", MockSalary(80000, None)),
            MockVacancy("Job 3", MockSalary(None, 120000)),
            MockVacancy("Job 4", None),  # Без зарплаты
            MockVacancy("Job 5", MockSalary(None, None))  # Пустая зарплата
        ]
        
        result = VacancyOperations.get_vacancies_with_salary(vacancies)
        
        assert len(result) == 3
        assert result[0].title == "Job 1"
        assert result[1].title == "Job 2"
        assert result[2].title == "Job 3"
    
    def test_get_vacancies_with_salary_empty_list(self):
        """Тест фильтрации пустого списка вакансий"""
        result = VacancyOperations.get_vacancies_with_salary([])
        
        assert result == []
    
    def test_get_vacancies_with_salary_no_valid_salaries(self):
        """Тест фильтрации когда нет валидных зарплат"""
        vacancies = [
            MockVacancy("Job 1", None),
            MockVacancy("Job 2", MockSalary(None, None))
        ]
        
        result = VacancyOperations.get_vacancies_with_salary(vacancies)
        
        assert result == []
    
    def test_sort_vacancies_by_salary_descending(self):
        """Тест сортировки вакансий по зарплате по убыванию"""
        vacancies = [
            MockVacancy("Low Job", MockSalary(50000, 80000)),
            MockVacancy("High Job", MockSalary(150000, 200000)),
            MockVacancy("Medium Job", MockSalary(100000, 130000)),
            MockVacancy("No Salary Job", None)
        ]
        
        result = VacancyOperations.sort_vacancies_by_salary(vacancies, reverse=True)
        
        assert len(result) == 4
        assert result[0].title == "High Job"
        assert result[1].title == "Medium Job"
        assert result[2].title == "Low Job"
        assert result[3].title == "No Salary Job"
    
    def test_sort_vacancies_by_salary_ascending(self):
        """Тест сортировки вакансий по зарплате по возрастанию"""
        vacancies = [
            MockVacancy("Low Job", MockSalary(50000, 80000)),
            MockVacancy("High Job", MockSalary(150000, 200000)),
            MockVacancy("Medium Job", MockSalary(100000, 130000))
        ]
        
        result = VacancyOperations.sort_vacancies_by_salary(vacancies, reverse=False)
        
        assert len(result) == 3
        assert result[0].title == "Low Job"
        assert result[1].title == "Medium Job"
        assert result[2].title == "High Job"
    
    def test_sort_vacancies_by_salary_empty_list(self):
        """Тест сортировки пустого списка"""
        result = VacancyOperations.sort_vacancies_by_salary([])
        
        assert result == []
    
    def test_sort_vacancies_by_salary_no_max_salary_method(self):
        """Тест сортировки когда у зарплаты нет метода get_max_salary"""
        vacancy = MockVacancy("Test Job", Mock())
        # Удаляем метод get_max_salary
        delattr(vacancy.salary, 'get_max_salary')
        
        result = VacancyOperations.sort_vacancies_by_salary([vacancy])
        
        assert len(result) == 1
        assert result[0].title == "Test Job"
    
    def test_filter_vacancies_by_min_salary_valid_range(self):
        """Тест фильтрации по минимальной зарплате с диапазоном"""
        vacancies = [
            MockVacancy("Job 1", MockSalary(100000, 150000)),  # Среднее: 125000
            MockVacancy("Job 2", MockSalary(80000, 120000)),   # Среднее: 100000
            MockVacancy("Job 3", MockSalary(50000, 70000)),    # Среднее: 60000
        ]
        
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 90000)
        
        assert len(result) == 2
        assert result[0].title == "Job 1"
        assert result[1].title == "Job 2"
    
    def test_filter_vacancies_by_min_salary_only_from(self):
        """Тест фильтрации по минимальной зарплате только с salary_from"""
        vacancies = [
            MockVacancy("Job 1", MockSalary(120000, None)),
            MockVacancy("Job 2", MockSalary(80000, None)),
            MockVacancy("Job 3", MockSalary(60000, None))
        ]
        
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 90000)
        
        assert len(result) == 1
        assert result[0].title == "Job 1"
    
    def test_filter_vacancies_by_min_salary_only_to(self):
        """Тест фильтрации по минимальной зарплате только с salary_to"""
        vacancies = [
            MockVacancy("Job 1", MockSalary(None, 150000)),
            MockVacancy("Job 2", MockSalary(None, 100000)),
            MockVacancy("Job 3", MockSalary(None, 70000))
        ]
        
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 90000)
        
        assert len(result) == 2
        assert result[0].title == "Job 1"
        assert result[1].title == "Job 2"
    
    def test_filter_vacancies_by_min_salary_no_salary(self):
        """Тест фильтрации когда у вакансий нет зарплаты"""
        vacancies = [
            MockVacancy("Job 1", None),
            MockVacancy("Job 2", MockSalary(None, None))
        ]
        
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 90000)
        
        assert result == []
    
    def test_filter_vacancies_by_min_salary_edge_cases(self):
        """Тест граничных случаев фильтрации по зарплате"""
        vacancies = [
            MockVacancy("Exact Match", MockSalary(100000, 100000)),  # Точное совпадение
            MockVacancy("Just Below", MockSalary(99999, 99999)),     # На 1 меньше
            MockVacancy("Just Above", MockSalary(100001, 100001))    # На 1 больше
        ]
        
        result = VacancyOperations.filter_vacancies_by_min_salary(vacancies, 100000)
        
        assert len(result) == 2
        assert result[0].title == "Exact Match"
        assert result[1].title == "Just Above"
    
    @patch('src.utils.vacancy_operations.filter_vacancies_by_keyword')
    def test_filter_vacancies_by_criteria_with_keyword(self, mock_filter):
        """Тест фильтрации вакансий по критериям с ключевым словом"""
        vacancies = [MockVacancy("Python Developer"), MockVacancy("Java Developer")]
        mock_filter.return_value = [vacancies[0]]
        
        criteria = {"keyword": "Python"}
        result = VacancyOperations.filter_vacancies_by_criteria(vacancies, criteria)
        
        assert len(result) == 1
        assert result[0].title == "Python Developer"
        mock_filter.assert_called_once_with(vacancies, "Python")
    
    def test_filter_vacancies_by_criteria_with_min_salary(self):
        """Тест фильтрации вакансий по критериям с минимальной зарплатой"""
        vacancies = [
            MockVacancy("High Salary Job", MockSalary(150000, 200000)),
            MockVacancy("Low Salary Job", MockSalary(50000, 80000))
        ]
        
        criteria = {"min_salary": 100000}
        result = VacancyOperations.filter_vacancies_by_criteria(vacancies, criteria)
        
        assert len(result) == 1
        assert result[0].title == "High Salary Job"
    
    def test_filter_vacancies_by_criteria_combined(self):
        """Тест фильтрации по комбинированным критериям"""
        vacancies = [
            MockVacancy("Python Developer", MockSalary(150000, 200000)),
            MockVacancy("Python Junior", MockSalary(50000, 80000)),
            MockVacancy("Java Developer", MockSalary(120000, 150000))
        ]
        
        with patch('src.utils.vacancy_operations.filter_vacancies_by_keyword') as mock_filter:
            # Мокаем чтобы вернуть только Python вакансии
            mock_filter.return_value = [vacancies[0], vacancies[1]]
            
            criteria = {"keyword": "Python", "min_salary": 100000}
            result = VacancyOperations.filter_vacancies_by_criteria(vacancies, criteria)
            
            assert len(result) == 1
            assert result[0].title == "Python Developer"
    
    def test_filter_vacancies_by_criteria_empty_criteria(self):
        """Тест фильтрации с пустыми критериями"""
        vacancies = [MockVacancy("Job 1"), MockVacancy("Job 2")]
        
        result = VacancyOperations.filter_vacancies_by_criteria(vacancies, {})
        
        assert len(result) == 2
        assert result == vacancies
    
    def test_get_vacancies_statistics_comprehensive(self):
        """Тест получения комплексной статистики по вакансиям"""
        vacancies = [
            MockVacancy("Python Developer", MockSalary(100000, 150000)),
            MockVacancy("Java Developer", MockSalary(80000, 120000)),
            MockVacancy("No Salary Job", None),
            MockVacancy("Frontend Developer", MockSalary(70000, 100000))
        ]
        
        stats = VacancyOperations.get_vacancies_statistics(vacancies)
        
        assert stats["total_count"] == 4
        assert stats["with_salary_count"] == 3
        assert stats["without_salary_count"] == 1
        assert stats["avg_min_salary"] == (100000 + 80000 + 70000) // 3  # 83333
        assert stats["avg_max_salary"] == (150000 + 120000 + 100000) // 3  # 123333
    
    def test_get_vacancies_statistics_empty_list(self):
        """Тест статистики для пустого списка"""
        stats = VacancyOperations.get_vacancies_statistics([])
        
        assert stats["total_count"] == 0
        assert stats["with_salary_count"] == 0
        assert stats["without_salary_count"] == 0
        assert stats["avg_min_salary"] == 0
        assert stats["avg_max_salary"] == 0
    
    def test_get_vacancies_statistics_no_salaries(self):
        """Тест статистики когда нет зарплат"""
        vacancies = [
            MockVacancy("Job 1", None),
            MockVacancy("Job 2", MockSalary(None, None))
        ]
        
        stats = VacancyOperations.get_vacancies_statistics(vacancies)
        
        assert stats["total_count"] == 2
        assert stats["with_salary_count"] == 0
        assert stats["without_salary_count"] == 2
        assert stats["avg_min_salary"] == 0
        assert stats["avg_max_salary"] == 0
    
    def test_deduplicate_vacancies_by_url(self):
        """Тест дедупликации вакансий по URL"""
        vacancies = [
            MockVacancy("Job 1"),
            MockVacancy("Job 2"),
            MockVacancy("Job 1 Duplicate")
        ]
        
        # Устанавливаем одинаковые URL для дубликатов
        vacancies[0].url = "http://test.com/job1"
        vacancies[1].url = "http://test.com/job2"
        vacancies[2].url = "http://test.com/job1"  # Дубликат
        
        result = VacancyOperations.deduplicate_vacancies(vacancies)
        
        assert len(result) == 2
        # Проверяем что остались уникальные URL
        urls = [v.url for v in result]
        assert len(set(urls)) == 2
    
    def test_deduplicate_vacancies_empty_list(self):
        """Тест дедупликации пустого списка"""
        result = VacancyOperations.deduplicate_vacancies([])
        
        assert result == []
    
    def test_deduplicate_vacancies_no_duplicates(self):
        """Тест дедупликации когда дубликатов нет"""
        vacancies = [
            MockVacancy("Job 1"),
            MockVacancy("Job 2"),
            MockVacancy("Job 3")
        ]
        
        # Устанавливаем уникальные URL
        for i, vacancy in enumerate(vacancies):
            vacancy.url = f"http://test.com/job{i+1}"
        
        result = VacancyOperations.deduplicate_vacancies(vacancies)
        
        assert len(result) == 3
        assert result == vacancies