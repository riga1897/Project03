"""
Утилиты для фильтрации данных из API через SQL-запросы

Предоставляет методы для фильтрации вакансий и компаний из API
с использованием временных таблиц в PostgreSQL для повышения производительности.
"""

import logging
import time  # Импорт time для генерации временных имен таблиц
from typing import Dict, List, Any, Optional, Union # Добавлен Union
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

    def filter_vacancies_by_target_companies(self, vacancies: List[Union[Dict, 'Vacancy']]) -> List[Union[Dict, 'Vacancy']]:
        """
        Фильтрация вакансий по целевым компаниям с использованием временной таблицы

        Args:
            vacancies: Список вакансий (словари или объекты Vacancy)

        Returns:
            List: Отфильтрованные вакансии от целевых компаний
        """
        if not vacancies:
            return []

        try:
            # Создаем временную таблицу
            temp_table = f"temp_vacancies_{int(time.time())}"

            # SQL для создания временной таблицы
            create_temp_sql = f"""
            CREATE TEMPORARY TABLE {temp_table} (
                id VARCHAR(255),
                title TEXT,
                company_name TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                source VARCHAR(50)
            );
            """

            # Заполняем временную таблицу данными
            insert_data = []
            for vacancy in vacancies:
                if isinstance(vacancy, dict):
                    # Работаем со словарем
                    salary_data = vacancy.get('salary') or {}
                    company_name = (
                        vacancy.get('employer', {}).get('name') if vacancy.get('employer') 
                        else vacancy.get('firm_name', '')
                    )

                    insert_data.append((
                        str(vacancy.get('id', '')),
                        vacancy.get('title') or vacancy.get('name') or vacancy.get('profession', ''),
                        company_name,
                        salary_data.get('from') or salary_data.get('payment_from'),
                        salary_data.get('to') or salary_data.get('payment_to'), 
                        salary_data.get('currency') or 'RUR',
                        vacancy.get('source', 'unknown')
                    ))
                else:
                    # Работаем с объектом Vacancy
                    salary_from = None
                    salary_to = None
                    currency = 'RUR'

                    # Безопасно получаем данные о зарплате
                    if hasattr(vacancy, 'salary') and vacancy.salary:
                        if hasattr(vacancy.salary, 'salary_from'):
                            salary_from = vacancy.salary.salary_from
                        if hasattr(vacancy.salary, 'salary_to'):
                            salary_to = vacancy.salary.salary_to
                        if hasattr(vacancy.salary, 'currency'):
                            currency = vacancy.salary.currency

                    # Безопасно получаем название компании
                    company_name = ''
                    if hasattr(vacancy, 'employer') and vacancy.employer:
                        if isinstance(vacancy.employer, dict):
                            company_name = vacancy.employer.get('name', '')
                        elif hasattr(vacancy.employer, 'name'):
                            company_name = vacancy.employer.name

                    insert_data.append((
                        str(getattr(vacancy, 'vacancy_id', '')),
                        getattr(vacancy, 'title', ''),
                        company_name,
                        salary_from,
                        salary_to,
                        currency,
                        getattr(vacancy, 'source', 'unknown')
                    ))

            # Выполняем SQL-операции
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу
                    cursor.execute(create_temp_sql)

                    # Вставляем данные
                    insert_sql = f"""
                    INSERT INTO {temp_table} (id, title, company_name, salary_from, salary_to, currency, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_sql, insert_data)

                    # Получаем список целевых компаний
                    from src.config.target_companies import get_target_company_names
                    target_companies = get_target_company_names()

                    # Создаем плейсхолдеры для IN запроса
                    placeholders = ','.join(['%s'] * len(target_companies))

                    # SQL-запрос для фильтрации по целевым компаниям
                    filter_sql = f"""
                    SELECT id FROM {temp_table}
                    WHERE company_name ILIKE ANY(ARRAY[{','.join(['%s'] * len(target_companies))}])
                    """

                    # Подготавливаем параметры для поиска (с wildcards)
                    search_params = [f'%{company}%' for company in target_companies]

                    cursor.execute(filter_sql, search_params)
                    target_ids = {row[0] for row in cursor.fetchall()}

                    # Очищаем временную таблицу
                    cursor.execute(f"DROP TABLE {temp_table}")

            # Фильтруем исходный список по найденным ID
            filtered_vacancies = []
            for vacancy in vacancies:
                if isinstance(vacancy, dict):
                    vacancy_id = str(vacancy.get('id', ''))
                else:
                    vacancy_id = str(getattr(vacancy, 'vacancy_id', ''))

                if vacancy_id in target_ids:
                    filtered_vacancies.append(vacancy)

            logger.info(f"SQL-фильтрация: найдено {len(filtered_vacancies)} вакансий от целевых компаний из {len(vacancies)}")
            return filtered_vacancies

        except Exception as e:
            logger.error(f"Ошибка SQL-фильтрации по целевым компаниям: {e}")
            # В случае ошибки возвращаем исходный список
            return vacancies

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