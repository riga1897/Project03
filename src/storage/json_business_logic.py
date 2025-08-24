
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import re

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class JSONBusinessLogic:
    """Fallback бизнес-логика для JSON хранилища"""
    
    @staticmethod
    def get_vacancies_paginated(vacancies: List[Vacancy], page: int = 1, page_size: int = 10, 
                              filters: Optional[Dict[str, Any]] = None,
                              sort_by: str = "created_at", sort_desc: bool = True) -> Tuple[List[Vacancy], int]:
        """Python-реализация пагинации"""
        # Применяем фильтры
        filtered_vacancies = JSONBusinessLogic._apply_filters(vacancies, filters)
        
        # Сортировка
        sorted_vacancies = JSONBusinessLogic._sort_vacancies(filtered_vacancies, sort_by, sort_desc)
        
        # Пагинация
        total_count = len(sorted_vacancies)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return sorted_vacancies[start_idx:end_idx], total_count

    @staticmethod
    def search_vacancies_advanced(vacancies: List[Vacancy], keywords: List[str], 
                                salary_range: Optional[Tuple[int, int]] = None,
                                experience_levels: Optional[List[str]] = None,
                                employment_types: Optional[List[str]] = None,
                                page: int = 1, page_size: int = 10) -> Tuple[List[Vacancy], int]:
        """Python-реализация расширенного поиска"""
        filtered_vacancies = []
        
        for vacancy in vacancies:
            # Поиск по ключевым словам
            if keywords:
                matches_keywords = all(
                    JSONBusinessLogic._matches_keyword(vacancy, keyword) 
                    for keyword in keywords
                )
                if not matches_keywords:
                    continue
            
            # Фильтр по зарплате
            if salary_range:
                min_sal, max_sal = salary_range
                vacancy_salary = JSONBusinessLogic._get_max_salary(vacancy)
                if not vacancy_salary or vacancy_salary < min_sal or vacancy_salary > max_sal:
                    continue
            
            # Фильтр по опыту
            if experience_levels:
                if not vacancy.experience or not any(
                    exp.lower() in vacancy.experience.lower() 
                    for exp in experience_levels
                ):
                    continue
            
            # Фильтр по типу занятости
            if employment_types:
                if not vacancy.employment or not any(
                    emp.lower() in vacancy.employment.lower() 
                    for emp in employment_types
                ):
                    continue
            
            filtered_vacancies.append(vacancy)
        
        # Сортировка по релевантности и зарплате
        filtered_vacancies.sort(
            key=lambda v: (
                JSONBusinessLogic._get_max_salary(v) or 0,
                v.published_at or ""
            ), 
            reverse=True
        )
        
        # Пагинация
        total_count = len(filtered_vacancies)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return filtered_vacancies[start_idx:end_idx], total_count

    @staticmethod
    def get_salary_statistics(vacancies: List[Vacancy], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Python-реализация статистики зарплат"""
        filtered_vacancies = JSONBusinessLogic._apply_filters(vacancies, filters)
        
        salaries = []
        vacancies_with_salary = 0
        
        for vacancy in filtered_vacancies:
            salary = JSONBusinessLogic._get_max_salary(vacancy)
            if salary and salary > 0:
                salaries.append(salary)
                vacancies_with_salary += 1
        
        if not salaries:
            return {
                'total_vacancies': len(filtered_vacancies),
                'vacancies_with_salary': 0,
                'min_salary': 0,
                'max_salary': 0,
                'avg_salary': 0,
                'median_salary': 0,
                'salary_coverage': 0
            }
        
        salaries.sort()
        median_salary = salaries[len(salaries) // 2] if salaries else 0
        
        return {
            'total_vacancies': len(filtered_vacancies),
            'vacancies_with_salary': vacancies_with_salary,
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'avg_salary': round(sum(salaries) / len(salaries), 2),
            'median_salary': median_salary,
            'salary_coverage': round((vacancies_with_salary / len(filtered_vacancies) * 100), 2) if filtered_vacancies else 0
        }

    @staticmethod
    def get_top_employers(vacancies: List[Vacancy], limit: int = 10, 
                         filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Python-реализация топа работодателей"""
        filtered_vacancies = JSONBusinessLogic._apply_filters(vacancies, filters)
        
        employer_stats = {}
        
        for vacancy in filtered_vacancies:
            employer_name = JSONBusinessLogic._get_employer_name(vacancy)
            if not employer_name:
                continue
            
            if employer_name not in employer_stats:
                employer_stats[employer_name] = {
                    'vacancy_count': 0,
                    'total_salary': 0,
                    'salary_count': 0
                }
            
            employer_stats[employer_name]['vacancy_count'] += 1
            
            salary = JSONBusinessLogic._get_max_salary(vacancy)
            if salary and salary > 0:
                employer_stats[employer_name]['total_salary'] += salary
                employer_stats[employer_name]['salary_count'] += 1
        
        # Формируем результат
        result = []
        for employer, stats in employer_stats.items():
            avg_salary = 0
            if stats['salary_count'] > 0:
                avg_salary = round(stats['total_salary'] / stats['salary_count'], 2)
            
            result.append({
                'employer': employer,
                'vacancy_count': stats['vacancy_count'],
                'avg_salary': avg_salary,
                'vacancies_with_salary': stats['salary_count']
            })
        
        # Сортируем по количеству вакансий
        result.sort(key=lambda x: x['vacancy_count'], reverse=True)
        return result[:limit]

    @staticmethod
    def get_popular_keywords(vacancies: List[Vacancy], limit: int = 20, 
                           filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Python-реализация анализа ключевых слов"""
        filtered_vacancies = JSONBusinessLogic._apply_filters(vacancies, filters)
        
        all_words = []
        stop_words = {
            'для', 'что', 'как', 'все', 'вас', 'мы', 'наш', 'ваш', 'это', 'или', 'так', 
            'может', 'быть', 'его', 'ее', 'их', 'и', 'в', 'на', 'с', 'от', 'до', 'по',
            'the', 'and', 'or', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by', 'from'
        }
        
        for vacancy in filtered_vacancies:
            if vacancy.requirements:
                # Простое разделение по словам и очистка
                words = re.findall(r'\b[а-яёa-z]{4,}\b', vacancy.requirements.lower())
                words = [word for word in words if word not in stop_words]
                all_words.extend(words)
        
        # Подсчет частоты
        word_counter = Counter(all_words)
        
        return [
            {'keyword': word, 'frequency': count}
            for word, count in word_counter.most_common(limit)
        ]

    # Вспомогательные методы
    @staticmethod
    def _apply_filters(vacancies: List[Vacancy], filters: Optional[Dict[str, Any]]) -> List[Vacancy]:
        """Применение фильтров к списку вакансий"""
        if not filters:
            return vacancies
        
        filtered = []
        for vacancy in vacancies:
            if filters.get('title') and filters['title'].lower() not in (vacancy.title or '').lower():
                continue
            
            if filters.get('employer'):
                employer_name = JSONBusinessLogic._get_employer_name(vacancy)
                if not employer_name or filters['employer'].lower() not in employer_name.lower():
                    continue
            
            if filters.get('salary_from'):
                salary = JSONBusinessLogic._get_max_salary(vacancy)
                if not salary or salary < filters['salary_from']:
                    continue
            
            if filters.get('salary_to'):
                salary = JSONBusinessLogic._get_max_salary(vacancy)
                if not salary or salary > filters['salary_to']:
                    continue
            
            filtered.append(vacancy)
        
        return filtered

    @staticmethod
    def _sort_vacancies(vacancies: List[Vacancy], sort_by: str, sort_desc: bool) -> List[Vacancy]:
        """Сортировка вакансий"""
        def get_sort_key(vacancy):
            if sort_by == "salary":
                return JSONBusinessLogic._get_max_salary(vacancy) or 0
            elif sort_by == "title":
                return vacancy.title or ""
            elif sort_by == "published_at":
                return vacancy.published_at or ""
            else:  # created_at или любое другое
                return vacancy.published_at or ""
        
        return sorted(vacancies, key=get_sort_key, reverse=sort_desc)

    @staticmethod
    def _matches_keyword(vacancy: Vacancy, keyword: str) -> bool:
        """Проверка соответствия вакансии ключевому слову"""
        keyword_lower = keyword.lower()
        
        search_fields = [
            vacancy.title,
            vacancy.description,
            vacancy.requirements,
            vacancy.responsibilities
        ]
        
        return any(
            field and keyword_lower in field.lower()
            for field in search_fields
        )

    @staticmethod
    def _get_max_salary(vacancy: Vacancy) -> Optional[int]:
        """Получение максимальной зарплаты из вакансии"""
        if not vacancy.salary:
            return None
        
        if hasattr(vacancy.salary, 'salary_to') and vacancy.salary.salary_to:
            return vacancy.salary.salary_to
        elif hasattr(vacancy.salary, 'salary_from') and vacancy.salary.salary_from:
            return vacancy.salary.salary_from
        
        return None

    @staticmethod
    def _get_employer_name(vacancy: Vacancy) -> Optional[str]:
        """Получение имени работодателя"""
        if not vacancy.employer:
            return None
        
        if isinstance(vacancy.employer, dict):
            return vacancy.employer.get('name')
        
        return str(vacancy.employer)
