
import logging
import os
from typing import Dict, List, Optional, Tuple, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DBManager:
    """
    Класс для работы с данными в БД PostgreSQL согласно требованиям проекта.
    
    Предоставляет методы для получения статистики по компаниям и вакансиям,
    анализа зарплат и фильтрации данных.
    """

    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """
        Инициализация подключения к PostgreSQL

        Args:
            db_config: Конфигурация подключения к БД (опционально)
        """
        if db_config:
            self.host = db_config.get('host', 'localhost')
            self.port = db_config.get('port', '5432')
            self.database = db_config.get('database', 'Project03')
            self.username = db_config.get('username', 'postgres')
            self.password = db_config.get('password', '')
        else:
            # Используем переменные окружения из Replit Database
            self.host = os.getenv('PGHOST', 'localhost')
            self.port = os.getenv('PGPORT', '5432')
            self.database = os.getenv('PGDATABASE', 'Project03')
            self.username = os.getenv('PGUSER', 'postgres')
            self.password = os.getenv('PGPASSWORD', '')

    def _get_connection(self):
        """Создает подключение к базе данных"""
        try:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        
        Returns:
            List[Dict]: Список словарей с названием компании и количеством вакансий
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                COALESCE(employer, 'Не указано') as company_name,
                COUNT(*) as vacancy_count
            FROM vacancies_storage 
            WHERE employer IS NOT NULL AND employer != ''
            GROUP BY employer 
            ORDER BY vacancy_count DESC, company_name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения статистики по компаниям: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании, 
        названия вакансии, зарплаты и ссылки на вакансию.
        
        Returns:
            List[Dict]: Список всех вакансий с основной информацией
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                COALESCE(employer, 'Не указано') as company_name,
                title as vacancy_title,
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN
                        CONCAT('от ', salary_from, ' до ', salary_to, ' ', COALESCE(salary_currency, 'руб.'))
                    WHEN salary_from IS NOT NULL THEN
                        CONCAT('от ', salary_from, ' ', COALESCE(salary_currency, 'руб.'))
                    WHEN salary_to IS NOT NULL THEN
                        CONCAT('до ', salary_to, ' ', COALESCE(salary_currency, 'руб.'))
                    ELSE 'Не указана'
                END as salary_info,
                url as vacancy_url,
                vacancy_id
            FROM vacancies_storage 
            ORDER BY 
                CASE WHEN salary_from IS NOT NULL THEN salary_from ELSE 0 END DESC,
                company_name,
                title
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения всех вакансий: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям.
        
        Returns:
            Optional[float]: Средняя зарплата или None если данных нет
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            
            # Вычисляем среднюю зарплату учитывая и минимальную и максимальную границы
            query = """
            SELECT AVG(
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                        (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL THEN 
                        salary_from
                    WHEN salary_to IS NOT NULL THEN 
                        salary_to
                    ELSE NULL
                END
            ) as avg_salary
            FROM vacancies_storage 
            WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)
            AND salary_currency IN ('RUR', 'RUB', 'руб.', NULL)
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            return float(result[0]) if result and result[0] is not None else None
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка вычисления средней зарплаты: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        
        Returns:
            List[Dict]: Список вакансий с зарплатой выше средней
        """
        avg_salary = self.get_avg_salary()
        if avg_salary is None:
            logger.warning("Не удалось получить среднюю зарплату")
            return []
            
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                COALESCE(employer, 'Не указано') as company_name,
                title as vacancy_title,
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN
                        CONCAT('от ', salary_from, ' до ', salary_to, ' ', COALESCE(salary_currency, 'руб.'))
                    WHEN salary_from IS NOT NULL THEN
                        CONCAT('от ', salary_from, ' ', COALESCE(salary_currency, 'руб.'))
                    WHEN salary_to IS NOT NULL THEN
                        CONCAT('до ', salary_to, ' ', COALESCE(salary_currency, 'руб.'))
                    ELSE 'Не указана'
                END as salary_info,
                url as vacancy_url,
                vacancy_id,
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                        (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL THEN 
                        salary_from
                    WHEN salary_to IS NOT NULL THEN 
                        salary_to
                    ELSE 0
                END as calculated_salary
            FROM vacancies_storage 
            WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)
            AND salary_currency IN ('RUR', 'RUB', 'руб.', NULL)
            AND (
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN 
                        (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL THEN 
                        salary_from
                    WHEN salary_to IS NOT NULL THEN 
                        salary_to
                    ELSE 0
                END
            ) > %s
            ORDER BY calculated_salary DESC
            """
            
            cursor.execute(query, (avg_salary,))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения вакансий с высокой зарплатой: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список вакансий, содержащих указанное ключевое слово в названии.
        
        Args:
            keyword: Ключевое слово для поиска
            
        Returns:
            List[Dict]: Список найденных вакансий
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                COALESCE(employer, 'Не указано') as company_name,
                title as vacancy_title,
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN
                        CONCAT('от ', salary_from, ' до ', salary_to, ' ', COALESCE(salary_currency, 'руб.'))
                    WHEN salary_from IS NOT NULL THEN
                        CONCAT('от ', salary_from, ' ', COALESCE(salary_currency, 'руб.'))
                    WHEN salary_to IS NOT NULL THEN
                        CONCAT('до ', salary_to, ' ', COALESCE(salary_currency, 'руб.'))
                    ELSE 'Не указана'
                END as salary_info,
                url as vacancy_url,
                vacancy_id
            FROM vacancies_storage 
            WHERE LOWER(title) LIKE LOWER(%s)
            ORDER BY 
                CASE WHEN salary_from IS NOT NULL THEN salary_from ELSE 0 END DESC,
                company_name,
                title
            """
            
            cursor.execute(query, (f"%{keyword}%",))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка поиска вакансий по ключевому слову '{keyword}': {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_companies_list(self) -> List[str]:
        """
        Получает список всех уникальных компаний в базе данных.
        
        Returns:
            List[str]: Список названий компаний
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            
            query = """
            SELECT DISTINCT employer 
            FROM vacancies_storage 
            WHERE employer IS NOT NULL AND employer != ''
            ORDER BY employer
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [row[0] for row in results]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения списка компаний: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_database_stats(self) -> Dict[str, int]:
        """
        Получает общую статистику по базе данных.
        
        Returns:
            Dict[str, int]: Словарь со статистикой
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            
            # Общее количество вакансий
            cursor.execute("SELECT COUNT(*) FROM vacancies_storage")
            total_vacancies = cursor.fetchone()[0]
            
            # Количество вакансий с зарплатой
            cursor.execute("""
                SELECT COUNT(*) FROM vacancies_storage 
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            vacancies_with_salary = cursor.fetchone()[0]
            
            # Количество уникальных компаний
            cursor.execute("""
                SELECT COUNT(DISTINCT employer) FROM vacancies_storage 
                WHERE employer IS NOT NULL AND employer != ''
            """)
            unique_companies = cursor.fetchone()[0]
            
            return {
                'total_vacancies': total_vacancies,
                'vacancies_with_salary': vacancies_with_salary,
                'unique_companies': unique_companies,
                'vacancies_without_salary': total_vacancies - vacancies_with_salary
            }
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения статистики БД: {e}")
            return {}
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
