
"""
Класс DBManager для работы с данными в БД PostgreSQL

Реализует специфические методы согласно требованиям проекта по работе с БД.
Использует библиотеку psycopg2 для подключения к PostgreSQL.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import psycopg2
from psycopg2.extras import RealDictCursor

from src.config.db_config import DatabaseConfig

logger = logging.getLogger(__name__)


class DBManager:
    """
    Класс для работы с данными в БД PostgreSQL согласно требованиям проекта
    
    Предоставляет методы согласно требованиям проекта:
    - get_companies_and_vacancies_count() — получает список всех компаний и количество вакансий у каждой компании
    - get_all_vacancies() — получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию
    - get_avg_salary() — получает среднюю зарплату по вакансиям
    - get_vacancies_with_higher_salary() — получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
    - get_vacancies_with_keyword() — получает список всех вакансий, в названии которых содержатся переданные слова
    
    Использует библиотеку psycopg2 и SQL-запросы для работы с PostgreSQL.
    """
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None):
        """
        Инициализация DBManager
        
        Args:
            db_config: Конфигурация базы данных. Если None, используется по умолчанию
        """
        self.db_config = db_config or DatabaseConfig()
        
    def _get_connection(self) -> psycopg2.extensions.connection:
        """
        Создает подключение к базе данных используя SQL-драйвер psycopg2
        
        Returns:
            psycopg2.extensions.connection: Подключение к БД
            
        Raises:
            psycopg2.Error: При ошибке подключения к БД
        """
        try:
            connection = psycopg2.connect(**self.db_config.get_connection_params())
            return connection
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список целевых компаний и количество вакансий у каждой компании
        Использует SQL-запрос с поиском по названиям целевых компаний
        
        Returns:
            List[Tuple[str, int]]: Список кортежей (название_компании, количество_вакансий)
        """
        from src.config.target_companies import TARGET_COMPANIES
        
        # Создаем список названий целевых компаний для поиска
        target_company_names = [company['name'] for company in TARGET_COMPANIES]
        
        # SQL-запрос для получения только целевых компаний и подсчета вакансий
        query = """
        SELECT 
            COALESCE(employer, 'Неизвестная компания') as company_name,
            COUNT(*) as vacancy_count
        FROM vacancies_storage 
        WHERE employer IS NOT NULL AND employer != ''
        AND (
            """ + " OR ".join([
                "LOWER(employer) LIKE LOWER(%s)" for _ in target_company_names
            ]) + """
        )
        GROUP BY employer 
        ORDER BY vacancy_count DESC, company_name
        """
        
        try:
            # Создаем параметры для поиска (добавляем % для LIKE)
            search_params = [f"%{name}%" for name in target_company_names]
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, search_params)
                    results = cursor.fetchall()
                    
                    # Если найдены совпадения в БД, возвращаем их
                    if results:
                        return [(row[0], row[1]) for row in results]
                    
                    # Если нет совпадений, возвращаем все целевые компании с 0 вакансий
                    return [(company['name'], 0) for company in TARGET_COMPANIES]
                    
        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для получения списка целевых компаний: {e}")
            # В случае ошибки возвращаем целевые компании с 0 вакансий
            return [(company['name'], 0) for company in TARGET_COMPANIES]
    
    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании, 
        названия вакансии, зарплаты и ссылки на вакансию
        Использует SQL-запрос с CASE для форматирования зарплаты
        
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о вакансиях
        """
        # SQL-запрос для получения всех вакансий с форматированной зарплатой
        query = """
        SELECT 
            title,
            COALESCE(employer, 'Неизвестная компания') as company_name,
            CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                    CONCAT(salary_from, ' - ', salary_to, ' ', COALESCE(salary_currency, 'RUR'))
                WHEN salary_from IS NOT NULL THEN 
                    CONCAT('от ', salary_from, ' ', COALESCE(salary_currency, 'RUR'))
                WHEN salary_to IS NOT NULL THEN 
                    CONCAT('до ', salary_to, ' ', COALESCE(salary_currency, 'RUR'))
                ELSE 'Не указана'
            END as salary_info,
            url
        FROM vacancies_storage 
        ORDER BY company_name, title
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для получения списка вакансий: {e}")
            return []
    
    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям
        Использует SQL-функцию AVG() для вычисления средней зарплаты
        
        Returns:
            Optional[float]: Средняя зарплата или None если данных нет
        """
        # SQL-запрос для вычисления средней зарплаты
        query = """
        SELECT AVG(
            CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                    (salary_from + salary_to) / 2
                WHEN salary_from IS NOT NULL THEN salary_from
                WHEN salary_to IS NOT NULL THEN salary_to
                ELSE NULL
            END
        ) as avg_salary
        FROM vacancies_storage 
        WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)
        AND salary_currency IN ('RUR', 'RUB', 'руб.', NULL)
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    return float(result[0]) if result[0] is not None else None
                    
        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для расчета средней зарплаты: {e}")
            return None
    
    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        Использует SQL-подзапрос для сравнения с средней зарплатой
        
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о вакансиях
        """
        # Сначала получаем среднюю зарплату
        avg_salary = self.get_avg_salary()
        
        if avg_salary is None:
            logger.warning("Не удалось рассчитать среднюю зарплату")
            return []
        
        # SQL-запрос для получения вакансий с зарплатой выше средней
        query = """
        SELECT 
            title,
            COALESCE(employer, 'Неизвестная компания') as company_name,
            CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                    CONCAT(salary_from, ' - ', salary_to, ' ', COALESCE(salary_currency, 'RUR'))
                WHEN salary_from IS NOT NULL THEN 
                    CONCAT('от ', salary_from, ' ', COALESCE(salary_currency, 'RUR'))
                WHEN salary_to IS NOT NULL THEN 
                    CONCAT('до ', salary_to, ' ', COALESCE(salary_currency, 'RUR'))
                ELSE 'Не указана'
            END as salary_info,
            url,
            CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                    (salary_from + salary_to) / 2
                WHEN salary_from IS NOT NULL THEN salary_from
                WHEN salary_to IS NOT NULL THEN salary_to
                ELSE NULL
            END as calculated_salary
        FROM vacancies_storage 
        WHERE (
            CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                    (salary_from + salary_to) / 2
                WHEN salary_from IS NOT NULL THEN salary_from
                WHEN salary_to IS NOT NULL THEN salary_to
                ELSE NULL
            END
        ) > %s
        AND salary_currency IN ('RUR', 'RUB', 'руб.', NULL)
        ORDER BY calculated_salary DESC, company_name, title
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (avg_salary,))
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для получения вакансий с высокой зарплатой: {e}")
            return []
    
    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова
        Использует SQL-оператор LIKE для поиска по ключевому слову
        
        Args:
            keyword: Ключевое слово для поиска
            
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о вакансиях
        """
        if not keyword or not keyword.strip():
            return []
        
        # SQL-запрос для поиска вакансий по ключевому слову
        query = """
        SELECT 
            title,
            COALESCE(employer, 'Неизвестная компания') as company_name,
            CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                    CONCAT(salary_from, ' - ', salary_to, ' ', COALESCE(salary_currency, 'RUR'))
                WHEN salary_from IS NOT NULL THEN 
                    CONCAT('от ', salary_from, ' ', COALESCE(salary_currency, 'RUR'))
                WHEN salary_to IS NOT NULL THEN 
                    CONCAT('до ', salary_to, ' ', COALESCE(salary_currency, 'RUR'))
                ELSE 'Не указана'
            END as salary_info,
            url,
            description
        FROM vacancies_storage 
        WHERE LOWER(title) LIKE LOWER(%s)
        ORDER BY company_name, title
        """
        
        try:
            search_pattern = f"%{keyword.strip()}%"
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (search_pattern,))
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                    
        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для поиска вакансий по ключевому слову '{keyword}': {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Получает статистику базы данных используя различные SQL-запросы
        
        Returns:
            Dict[str, Any]: Словарь со статистикой
        """
        # Словарь SQL-запросов для получения статистики
        stats_queries = {
            'total_vacancies': "SELECT COUNT(*) FROM vacancies_storage",
            'total_companies': "SELECT COUNT(DISTINCT employer) FROM vacancies_storage WHERE employer IS NOT NULL AND employer != ''",
            'vacancies_with_salary': "SELECT COUNT(*) FROM vacancies_storage WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)",
            'latest_vacancy_date': "SELECT MAX(published_at) FROM vacancies_storage"
        }
        
        stats = {}
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Выполняем каждый SQL-запрос для получения статистики
                    for stat_name, query in stats_queries.items():
                        cursor.execute(query)
                        result = cursor.fetchone()
                        stats[stat_name] = result[0] if result else 0
                        
            return stats
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запросов для получения статистики БД: {e}")
            return {}
    
    def check_connection(self) -> bool:
        """
        Проверяет подключение к базе данных используя простой SQL-запрос
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Простой SQL-запрос для проверки подключения
                    cursor.execute("SELECT 1")
                    return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False
