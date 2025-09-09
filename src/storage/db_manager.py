"""
Чистая версия DBManager с единым инициализатором соединений.
"""

import logging
from typing import Any, Dict, Optional

from src.storage.db_psycopg2_compat import get_psycopg2, get_psycopg_error, is_available as psycopg2_available
from src.storage.db_connection_config import get_db_connection_params

logger = logging.getLogger(__name__)

try:
    PsycopgError = get_psycopg_error()
except ImportError:
    PsycopgError = Exception


class DBManager:
    """
    Менеджер базы данных с единым инициализатором соединений.
    
    Использует контекстный менеджер для управления соединениями.
    """

    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """Инициализация менеджера БД."""
        # Используем универсальный конфигуратор подключения
        connection_params = get_db_connection_params(db_config)
        
        self.host = connection_params["host"]
        self.port = connection_params["port"] 
        self.database = connection_params["database"]
        self.username = connection_params["user"]
        self.password = connection_params["password"]

    def _get_connection(self):
        """Создает подключение к базе данных."""
        if not psycopg2_available():
            raise ConnectionError("psycopg2 не установлен или недоступен")

        try:
            psycopg2 = get_psycopg2()
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                client_encoding="utf8",
            )
            connection.set_client_encoding("UTF8")
            return connection
        except PsycopgError as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def initialize_database(self) -> bool:
        """ЕДИНЫЙ ИНИЦИАЛИЗАТОР БД с контекстным менеджером.
        
        Создает таблицы и заполняет компании в одном соединении.
        """
        try:
            # ЕДИНОЕ соединение с контекстным менеджером для всех операций
            with self._get_connection() as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    logger.debug("🔧 Создание структуры базы данных...")
                    cursor.execute("SET client_encoding TO 'UTF8'")

                    # СОЗДАНИЕ ТАБЛИЦ
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS companies (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL UNIQUE,
                            hh_id VARCHAR(50),
                            sj_id VARCHAR(50)
                        );
                        """
                    )
                    logger.debug("✅ Таблица companies создана")
                    
                    cursor.execute(
                        """
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
                            area TEXT,
                            source VARCHAR(50),
                            published_at TIMESTAMP,
                            company_id INTEGER,
                            search_query TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """
                    )
                    logger.debug("✅ Таблица vacancies создана")
                    
                    # ЗАПОЛНЕНИЕ КОМПАНИЙ
                    logger.debug("📊 Заполнение таблицы компаний...")
                    self._fill_companies_table(cursor)
                    
                    logger.debug("✅ Инициализация БД завершена")
                    logger.info("✓ База данных инициализирована с единым инициализатором")
                    
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            logger.error(f"Ошибка при инициализации БД: {e}")
            return False
        return True
        
    def _fill_companies_table(self, cursor) -> None:
        """Заполняет таблицу компаний используя переданный cursor."""
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        if count > 0:
            logger.debug(f"ℹ️ Таблица companies уже содержит {count} записей")
            return
            
        from src.config.target_companies import TargetCompanies
        
        added = 0
        for company in TargetCompanies.COMPANIES:
            try:
                cursor.execute(
                    """
                    INSERT INTO companies (name, hh_id, sj_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (company.name, company.hh_id, company.sj_id)
                )
                added += 1
            except Exception as e:
                logger.warning(f"Не удалось добавить компанию {company.name}: {e}")
        
        logger.debug(f"✅ Добавлено {added} компаний")

    def check_connection(self) -> bool:
        """Проверяет подключение к базе данных."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False

    def get_companies_and_vacancies_count(self) -> dict:
        """Возвращает количество компаний и вакансий в БД."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    companies_count = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM vacancies")
                    vacancies_count = cursor.fetchone()[0]
                    return {
                        "companies": companies_count,
                        "vacancies": vacancies_count
                    }
        except Exception as e:
            logger.error(f"Ошибка при подсчёте записей: {e}")
            return {"companies": 0, "vacancies": 0}

    def get_target_companies_analysis(self) -> list:
        """Получает анализ ТОЛЬКО по целевым компаниям.

        Этот метод специально предназначен для демонстрации п.10.

        Returns:
            Список кортежей (название_целевой_компании, количество_вакансий).
        """
        try:
            from src.config.target_companies import TargetCompanies
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Получаем статистику по целевым компаниям
                    target_companies = TargetCompanies.get_all_companies()
                    result = []
                    
                    for company in target_companies:
                        # Считаем вакансии для каждой целевой компании
                        cursor.execute("""
                            SELECT COUNT(v.id) 
                            FROM vacancies v 
                            JOIN companies c ON v.company_id = c.id 
                            WHERE c.name = %s
                        """, (company.name,))
                        
                        count = cursor.fetchone()[0]
                        result.append((company.name, count))
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Ошибка при анализе целевых компаний: {e}")
            # В случае ошибки возвращаем все целевые компании с нулями
            from src.config.target_companies import TargetCompanies
            return [(company.name, 0) for company in TargetCompanies.get_all_companies()]

    def get_all_vacancies(self) -> list:
        """Получает все вакансии из базы данных с форматированной информацией о зарплате.

        Returns:
            Список словарей с данными вакансий.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            v.vacancy_id, 
                            v.title, 
                            v.url, 
                            v.salary_from, 
                            v.salary_to, 
                            v.salary_currency, 
                            -- Формируем salary_info для совместимости с демонстрацией
                            CASE
                                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                                    CONCAT(v.salary_from, ' - ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))
                                WHEN v.salary_from IS NOT NULL THEN
                                    CONCAT('от ', v.salary_from, ' ', COALESCE(v.salary_currency, 'RUR'))
                                WHEN v.salary_to IS NOT NULL THEN
                                    CONCAT('до ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))
                                ELSE 'Не указана'
                            END as salary_info,
                            v.description, 
                            v.requirements, 
                            v.responsibilities,
                            v.experience, 
                            v.employment, 
                            v.schedule, 
                            v.area, 
                            v.source, 
                            v.published_at, 
                            COALESCE(c.name, 'Неизвестная компания') as company_name
                        FROM vacancies v
                        LEFT JOIN companies c ON v.company_id = c.id
                        ORDER BY v.salary_from DESC NULLS LAST, c.name, v.title
                    """)
                    
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    return [dict(zip(columns, row)) for row in rows]
                    
        except Exception as e:
            logger.error(f"Ошибка при получении всех вакансий: {e}")
            return []

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по всем вакансиям.

        Returns:
            Средняя зарплата в рублях или None если данных нет.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT AVG(
                            CASE
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN
                                    (salary_from + salary_to) / 2
                                WHEN salary_from IS NOT NULL THEN salary_from
                                WHEN salary_to IS NOT NULL THEN salary_to
                                ELSE NULL
                            END
                        ) as avg_salary
                        FROM vacancies
                        WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)
                        AND salary_currency IN ('RUR', 'RUB', 'руб.', 'rub', NULL)
                    """)
                    
                    result = cursor.fetchone()
                    return float(result[0]) if result and result[0] is not None else None
                    
        except Exception as e:
            logger.error(f"Ошибка при расчете средней зарплаты: {e}")
            return None

    def get_vacancies_with_higher_salary(self) -> list:
        """Получает вакансии с зарплатой выше средней.

        Returns:
            Список словарей с данными вакансий.
        """
        try:
            # Сначала получаем среднюю зарплату
            avg_salary = self.get_avg_salary()
            if avg_salary is None:
                logger.warning("Не удалось рассчитать среднюю зарплату")
                return []

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            v.title,
                            COALESCE(c.name, 'Неизвестная компания') as company_name,
                            CASE
                                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                                    CONCAT(v.salary_from, ' - ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))
                                WHEN v.salary_from IS NOT NULL THEN
                                    CONCAT('от ', v.salary_from, ' ', COALESCE(v.salary_currency, 'RUR'))
                                WHEN v.salary_to IS NOT NULL THEN
                                    CONCAT('до ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))
                                ELSE 'Не указана'
                            END as salary_info,
                            v.url,
                            v.vacancy_id
                        FROM vacancies v
                        LEFT JOIN companies c ON v.company_id = c.id
                        WHERE (
                            CASE
                                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                                    (v.salary_from + v.salary_to) / 2
                                WHEN v.salary_from IS NOT NULL THEN v.salary_from
                                WHEN v.salary_to IS NOT NULL THEN v.salary_to
                                ELSE NULL
                            END
                        ) > %s
                        ORDER BY 
                            CASE
                                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                                    (v.salary_from + v.salary_to) / 2
                                WHEN v.salary_from IS NOT NULL THEN v.salary_from
                                WHEN v.salary_to IS NOT NULL THEN v.salary_to
                                ELSE 0
                            END DESC
                    """, (avg_salary,))
                    
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    return [dict(zip(columns, row)) for row in rows]
                    
        except Exception as e:
            logger.error(f"Ошибка при получении вакансий с высокой зарплатой: {e}")
            return []

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """Поиск вакансий по ключевому слову.

        Args:
            keyword: Ключевое слово для поиска.

        Returns:
            Список словарей с данными найденных вакансий.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    search_pattern = f"%{keyword.lower()}%"
                    cursor.execute("""
                        SELECT 
                            v.title,
                            COALESCE(c.name, 'Неизвестная компания') as company_name,
                            CASE
                                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                                    CONCAT(v.salary_from, ' - ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))
                                WHEN v.salary_from IS NOT NULL THEN
                                    CONCAT('от ', v.salary_from, ' ', COALESCE(v.salary_currency, 'RUR'))
                                WHEN v.salary_to IS NOT NULL THEN
                                    CONCAT('до ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))
                                ELSE 'Не указана'
                            END as salary_info,
                            v.url,
                            v.vacancy_id
                        FROM vacancies v
                        LEFT JOIN companies c ON v.company_id = c.id
                        WHERE 
                            LOWER(v.title) LIKE %s OR 
                            LOWER(v.description) LIKE %s OR
                            LOWER(v.requirements) LIKE %s OR
                            LOWER(v.responsibilities) LIKE %s
                        ORDER BY v.title
                    """, (search_pattern, search_pattern, search_pattern, search_pattern))
                    
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    return [dict(zip(columns, row)) for row in rows]
                    
        except Exception as e:
            logger.error(f"Ошибка при поиске по ключевому слову '{keyword}': {e}")
            return []

    def get_database_stats(self) -> dict:
        """Получает статистику базы данных.

        Returns:
            Словарь со статистикой БД.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Общая статистика
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    companies_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM vacancies")
                    vacancies_count = cursor.fetchone()[0]
                    
                    # Статистика по зарплатам
                    cursor.execute("""
                        SELECT COUNT(*) FROM vacancies 
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    """)
                    vacancies_with_salary = cursor.fetchone()[0]
                    
                    # Статистика по источникам
                    cursor.execute("""
                        SELECT source, COUNT(*) as count 
                        FROM vacancies 
                        GROUP BY source 
                        ORDER BY count DESC
                    """)
                    source_stats = cursor.fetchall()
                    
                    # Топ компаний по количеству вакансий
                    cursor.execute("""
                        SELECT c.name, COUNT(v.id) as count 
                        FROM companies c 
                        LEFT JOIN vacancies v ON c.id = v.company_id 
                        GROUP BY c.name 
                        HAVING COUNT(v.id) > 0
                        ORDER BY count DESC 
                        LIMIT 5
                    """)
                    top_companies = cursor.fetchall()
                    
                    return {
                        'companies': companies_count,
                        'vacancies': vacancies_count,
                        'vacancies_with_salary': vacancies_with_salary,
                        'vacancy_salary_percentage': round((vacancies_with_salary / vacancies_count * 100), 1) if vacancies_count > 0 else 0,
                        'source_stats': [{'source': row[0], 'count': row[1]} for row in source_stats],
                        'top_companies': [{'name': row[0], 'count': row[1]} for row in top_companies]
                    }
                    
        except Exception as e:
            logger.error(f"Ошибка при получении статистики БД: {e}")
            return {
                'companies': 0,
                'vacancies': 0,
                'vacancies_with_salary': 0,
                'vacancy_salary_percentage': 0,
                'source_stats': [],
                'top_companies': []
            }

    # МЕТОДЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
    def create_tables(self) -> bool:
        """[УСТАРЕЛО] Используйте initialize_database()."""
        logger.warning("Метод create_tables() устарел. Используйте initialize_database()")
        return self.initialize_database()

    def populate_companies_table(self) -> bool:
        """[УСТАРЕЛО] Используйте initialize_database().""" 
        logger.warning("Метод populate_companies_table() устарел. Теперь выполняется в initialize_database()")
        return True