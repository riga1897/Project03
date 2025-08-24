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

    def create_tables(self):
        """
        Создает таблицы компаний и вакансий в базе данных, если они не существуют
        """
        # SQL для создания таблиц
        create_companies_table = """
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            company_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            hh_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_vacancies_table = """
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            vacancy_id VARCHAR(255) UNIQUE NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            salary_from INTEGER,
            salary_to INTEGER,
            salary_currency VARCHAR(10),
            description TEXT,
            requirements TEXT,
            responsibilities TEXT,
            experience VARCHAR(100),
            employment VARCHAR(100),
            schedule VARCHAR(100),
            employer TEXT,
            area TEXT,
            source VARCHAR(50),
            published_at TIMESTAMP,
            company_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Сначала создаем таблицу компаний
                    cursor.execute(create_companies_table)
                    logger.info("Таблица компаний создана успешно")

                    # Затем создаем таблицу вакансий с FK
                    cursor.execute(create_vacancies_table)
                    logger.info("Таблица вакансий создана успешно")

        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

    def populate_companies_table(self):
        """
        Заполняет таблицу компаний данными из конфигурации
        """
        from src.config.target_companies import TARGET_COMPANIES

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Проверяем, есть ли уже данные
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    count = cursor.fetchone()[0]

                    if count == 0:
                        # Вставляем данные о компаниях
                        insert_sql = """
                        INSERT INTO companies (company_id, name, description, hh_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (company_id) DO NOTHING
                        """

                        for company in TARGET_COMPANIES:
                            cursor.execute(insert_sql, (
                                company["hh_id"],
                                company["name"], 
                                company["description"],
                                company["hh_id"]
                            ))

                        logger.info(f"Добавлено {len(TARGET_COMPANIES)} компаний в базу данных")
                    else:
                        logger.info(f"Таблица компаний уже содержит {count} записей")

        except Exception as e:
            logger.error(f"Ошибка при заполнении таблицы компаний: {e}")
            raise

    def _create_vacancies_storage_table(self):
        """
        Создает таблицу vacancies_storage для совместимости со старыми методами
        """
        create_vacancies_storage_table = """
        CREATE TABLE IF NOT EXISTS vacancies_storage (
            id SERIAL PRIMARY KEY,
            vacancy_id VARCHAR(255) UNIQUE,
            title TEXT,
            url TEXT,
            salary_from INTEGER,
            salary_to INTEGER,
            salary_currency VARCHAR(10),
            description TEXT,
            employer TEXT,
            area TEXT,
            source VARCHAR(50),
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_vacancies_storage_table)
                    logger.info("Таблица vacancies_storage создана успешно")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы vacancies_storage: {e}")
            raise

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании

        Returns:
            List[Tuple[str, int]]: Список кортежей (название_компании, количество_вакансий)
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # SQL-запрос с JOIN для связи компаний и вакансий
                    query = """
                    SELECT 
                        c.name as company_name,
                        COUNT(v.id) as vacancy_count
                    FROM companies c
                    LEFT JOIN vacancies v ON c.company_id = v.company_id
                    GROUP BY c.name, c.company_id
                    ORDER BY vacancy_count DESC, company_name
                    """

                    cursor.execute(query)
                    return cursor.fetchall()

        except Exception as e:
            logger.error(f"Ошибка при получении списка компаний и количества вакансий: {e}")
            # Fallback к старому методу если таблица компаний не готова
            try:
                with self._get_connection() as conn:
                    with conn.cursor() as cursor:
                        # Проверяем наличие данных в основной таблице вакансий
                        query_fallback = """
                        SELECT 
                            COALESCE(employer, 'Не указано') as company_name,
                            COUNT(*) as vacancy_count
                        FROM vacancies_storage 
                        WHERE employer IS NOT NULL AND employer != ''
                        GROUP BY employer
                        ORDER BY vacancy_count DESC, company_name
                        """
                        cursor.execute(query_fallback)
                        return cursor.fetchall()
            except Exception as e2:
                logger.error(f"Ошибка в fallback запросе: {e2}")
                return []

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

    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Публичный метод для получения подключения к базе данных

        Returns:
            psycopg2.extensions.connection: Подключение к БД

        Raises:
            psycopg2.Error: При ошибке подключения к БД
        """
        return self._get_connection()

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

    def filter_companies_by_targets(self, api_companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует компании из API по целевым компаниям используя SQL-запрос

        Args:
            api_companies: Список компаний из API

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список целевых компаний
        """
        from src.config.target_companies import TARGET_COMPANIES

        if not api_companies:
            return []

        # Создаем список названий целевых компаний для SQL-поиска
        target_company_names = [company['name'].lower() for company in TARGET_COMPANIES]

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу для компаний из API
                    cursor.execute("""
                        CREATE TEMP TABLE temp_api_companies (
                            company_id VARCHAR(50),
                            company_name VARCHAR(500)
                        ) ON COMMIT DROP
                    """)

                    # Вставляем данные о компаниях из API
                    api_data = [(str(comp.get('id', '')), comp.get('name', '')) for comp in api_companies]
                    from psycopg2.extras import execute_values
                    execute_values(
                        cursor,
                        "INSERT INTO temp_api_companies (company_id, company_name) VALUES %s",
                        api_data,
                        template=None,
                        page_size=1000
                    )

                    # SQL-запрос для поиска целевых компаний
                    placeholders = ','.join(['%s'] * len(target_company_names))
                    query = f"""
                    SELECT company_id, company_name 
                    FROM temp_api_companies 
                    WHERE LOWER(company_name) IN ({placeholders})
                    OR """ + " OR ".join([
                        "LOWER(company_name) LIKE %s" for _ in target_company_names
                    ])

                    # Параметры: точные совпадения + LIKE поиск
                    params = target_company_names + [f"%{name}%" for name in target_company_names]

                    cursor.execute(query, params)
                    results = cursor.fetchall()

                    # Возвращаем найденные компании из исходного списка
                    found_ids = {row[0] for row in results}
                    return [comp for comp in api_companies if str(comp.get('id', '')) in found_ids]

        except psycopg2.Error as e:
            logger.error(f"Ошибка SQL-фильтрации компаний: {e}")
            return api_companies

    def analyze_api_data_with_sql(self, api_data: List[Dict[str, Any]], analysis_type: str = 'vacancy_stats') -> Dict[str, Any]:
        """
        Анализирует данные из API используя SQL-запросы для получения статистики

        Args:
            api_data: Данные из API для анализа
            analysis_type: Тип анализа ('vacancy_stats', 'salary_analysis', 'company_analysis')

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        if not api_data:
            return {}

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Создаем временную таблицу для данных из API
                    cursor.execute("""
                        CREATE TEMP TABLE temp_api_analysis (
                            item_id VARCHAR(50),
                            title VARCHAR(500),
                            salary_from INTEGER,
                            salary_to INTEGER,
                            salary_currency VARCHAR(10),
                            employer VARCHAR(500),
                            area VARCHAR(200),
                            experience VARCHAR(200),
                            employment VARCHAR(200)
                        ) ON COMMIT DROP
                    """)

                    # Подготавливаем данные для анализа
                    analysis_data = []
                    for item in api_data:
                        salary = item.get('salary', {}) or {}
                        analysis_data.append((
                            str(item.get('id', '')),
                            item.get('name', ''),
                            salary.get('from'),
                            salary.get('to'),
                            salary.get('currency'),
                            str(item.get('employer', {}).get('name', '') if item.get('employer') else ''),
                            str(item.get('area', {}).get('name', '') if item.get('area') else ''),
                            item.get('experience', {}).get('name', '') if isinstance(item.get('experience'), dict) else str(item.get('experience', '')),
                            item.get('employment', {}).get('name', '') if isinstance(item.get('employment'), dict) else str(item.get('employment', ''))
                        ))

                    from psycopg2.extras import execute_values
                    execute_values(
                        cursor,
                        """INSERT INTO temp_api_analysis (
                            item_id, title, salary_from, salary_to, salary_currency,
                            employer, area, experience, employment
                        ) VALUES %s""",
                        analysis_data,
                        template=None,
                        page_size=1000
                    )

                    results = {}

                    if analysis_type == 'vacancy_stats':
                        # Статистика по вакансиям
                        cursor.execute("""
                            SELECT 
                                COUNT(*) as total_vacancies,
                                COUNT(DISTINCT employer) as unique_employers,
                                COUNT(CASE WHEN salary_from IS NOT NULL OR salary_to IS NOT NULL THEN 1 END) as vacancies_with_salary,
                                AVG(CASE 
                                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2
                                    WHEN salary_from IS NOT NULL THEN salary_from
                                    WHEN salary_to IS NOT NULL THEN salary_to
                                END) as avg_salary
                            FROM temp_api_analysis
                            WHERE salary_currency IN ('RUR', 'RUB', 'руб.', NULL) OR salary_currency IS NULL
                        """)

                        stats = cursor.fetchone()
                        results.update(dict(stats))

                        # Топ работодателей
                        cursor.execute("""
                            SELECT employer, COUNT(*) as vacancy_count
                            FROM temp_api_analysis 
                            WHERE employer IS NOT NULL AND employer != ''
                            GROUP BY employer
                            ORDER BY vacancy_count DESC
                            LIMIT 10
                        """)
                        results['top_employers'] = [dict(row) for row in cursor.fetchall()]

                    elif analysis_type == 'salary_analysis':
                        # Анализ зарплат
                        cursor.execute("""
                            SELECT 
                                MIN(CASE 
                                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2
                                    WHEN salary_from IS NOT NULL THEN salary_from
                                    WHEN salary_to IS NOT NULL THEN salary_to
                                END) as min_salary,
                                MAX(CASE 
                                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2
                                    WHEN salary_from IS NOT NULL THEN salary_from
                                    WHEN salary_to IS NOT NULL THEN salary_to
                                END) as max_salary,
                                AVG(CASE 
                                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2
                                    WHEN salary_from IS NOT NULL THEN salary_from
                                    WHEN salary_to IS NOT NULL THEN salary_to
                                END) as avg_salary,
                                COUNT(CASE WHEN salary_from IS NOT NULL OR salary_to IS NOT NULL THEN 1 END) as count_with_salary
                            FROM temp_api_analysis
                            WHERE salary_currency IN ('RUR', 'RUB', 'руб.', NULL) OR salary_currency IS NULL
                        """)

                        results.update(dict(cursor.fetchone()))

                    return results

        except psycopg2.Error as e:
            logger.error(f"Ошибка SQL-анализа данных API: {e}")
            return {}