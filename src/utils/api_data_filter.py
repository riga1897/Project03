
"""
Утилиты для фильтрации данных из API через SQL-запросы

Предоставляет методы для фильтрации вакансий и компаний из API
с использованием временных таблиц в PostgreSQL для повышения производительности.
"""

import logging
from typing import Dict, List, Any, Optional
from src.vacancies.models import Vacancy
from src.storage.postgres_saver import PostgresSaver
from src.storage.db_manager import DBManager

logger = logging.getLogger(__name__)


class APIDataFilter:
    """
    Класс для фильтрации данных из API через SQL-запросы
    """
    
    def __init__(self):
        self.postgres_saver = PostgresSaver()
        self.db_manager = DBManager()
    
    def filter_vacancies_by_target_companies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Фильтрует вакансии по целевым компаниям используя SQL
        
        Args:
            vacancies: Список вакансий из API
            
        Returns:
            List[Vacancy]: Отфильтрованный список вакансий от целевых компаний
        """
        from src.config.target_companies import TARGET_COMPANIES
        
        target_company_names = [company['name'] for company in TARGET_COMPANIES]
        
        filters = {
            'target_employers': target_company_names,
            'exclude_existing': False  # Не исключаем существующие для фильтрации API данных
        }
        
        return self.postgres_saver.filter_api_vacancies_via_temp_table(vacancies, filters)
    
    def filter_vacancies_by_criteria(self, vacancies: List[Vacancy], criteria: Dict[str, Any]) -> List[Vacancy]:
        """
        Фильтрует вакансии по заданным критериям через SQL
        
        Args:
            vacancies: Список вакансий из API
            criteria: Критерии фильтрации
            
        Returns:
            List[Vacancy]: Отфильтрованный список вакансий
        """
        # Конвертируем критерии в формат для SQL-фильтрации
        filters = {}
        
        if criteria.get('min_salary'):
            filters['salary_from'] = criteria['min_salary']
        
        if criteria.get('max_salary'):
            filters['salary_to'] = criteria['max_salary']
        
        if criteria.get('keywords'):
            filters['keywords'] = criteria['keywords']
        
        if criteria.get('experience'):
            filters['experience'] = criteria['experience']
        
        if criteria.get('employment'):
            filters['employment'] = criteria['employment']
        
        if criteria.get('schedule'):
            filters['schedule'] = criteria['schedule']
        
        if criteria.get('area'):
            filters['area'] = criteria['area']
        
        if criteria.get('exclude_duplicates', True):
            filters['exclude_existing'] = True
        
        if criteria.get('limit'):
            filters['limit'] = criteria['limit']
        
        if criteria.get('sort_by_salary', False):
            filters['sort_by_salary'] = True
        
        return self.postgres_saver.filter_api_vacancies_via_temp_table(vacancies, filters)
    
    def get_api_data_statistics(self, vacancies: List[Vacancy]) -> Dict[str, Any]:
        """
        Получает статистику по данным из API используя SQL
        
        Args:
            vacancies: Список вакансий из API
            
        Returns:
            Dict[str, Any]: Статистика
        """
        # Конвертируем вакансии в формат для анализа
        api_data = []
        for vacancy in vacancies:
            salary_data = {}
            if vacancy.salary:
                salary_data = {
                    'from': vacancy.salary.salary_from,
                    'to': vacancy.salary.salary_to,
                    'currency': vacancy.salary.currency
                }
            
            employer_data = {}
            if vacancy.employer:
                if isinstance(vacancy.employer, dict):
                    employer_data = vacancy.employer
                else:
                    employer_data = {'name': str(vacancy.employer)}
            
            area_data = {}
            if vacancy.area:
                if isinstance(vacancy.area, dict):
                    area_data = vacancy.area
                else:
                    area_data = {'name': str(vacancy.area)}
            
            api_data.append({
                'id': vacancy.vacancy_id,
                'name': vacancy.title,
                'salary': salary_data,
                'employer': employer_data,
                'area': area_data,
                'experience': vacancy.experience,
                'employment': vacancy.employment
            })
        
        return self.db_manager.analyze_api_data_with_sql(api_data, 'vacancy_stats')
    
    def filter_high_salary_vacancies_sql(self, vacancies: List[Vacancy], percentile: float = 0.7) -> List[Vacancy]:
        """
        Фильтрует вакансии с высокой зарплатой используя SQL-вычисления
        
        Args:
            vacancies: Список вакансий из API
            percentile: Процентиль для определения высокой зарплаты (по умолчанию 70%)
            
        Returns:
            List[Vacancy]: Вакансии с зарплатой выше указанного процентиля
        """
        # Сначала получаем статистику по зарплатам
        api_data = []
        for vacancy in vacancies:
            if vacancy.salary and (vacancy.salary.salary_from or vacancy.salary.salary_to):
                salary_data = {
                    'from': vacancy.salary.salary_from,
                    'to': vacancy.salary.salary_to,
                    'currency': vacancy.salary.currency
                }
                
                api_data.append({
                    'id': vacancy.vacancy_id,
                    'name': vacancy.title,
                    'salary': salary_data,
                    'employer': vacancy.employer,
                    'area': vacancy.area
                })
        
        if not api_data:
            return []
        
        # Получаем анализ зарплат
        salary_stats = self.db_manager.analyze_api_data_with_sql(api_data, 'salary_analysis')
        
        if not salary_stats.get('avg_salary'):
            return vacancies
        
        # Используем среднюю зарплату как порог для фильтрации
        threshold_salary = salary_stats['avg_salary'] * (1 + percentile)
        
        filters = {
            'salary_from': int(threshold_salary),
            'sort_by_salary': True
        }
        
        return self.postgres_saver.filter_api_vacancies_via_temp_table(vacancies, filters)
