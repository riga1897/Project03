"""
Модуль для работы с данными в базе PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Optional, Any


class DBManager:
    """
    Класс для работы с данными в БД PostgreSQL.

    Реализует методы для получения и анализа данных о компаниях и вакансиях
    с использованием SQL-запросов и библиотеки psycopg2.
    """

    def __init__(self, debug_mode: bool = False) -> None:
        """Инициализация менеджера БД с параметрами из окружения."""
        self.host: str = os.getenv('PGHOST', 'localhost')
        self.port: str = os.getenv('PGPORT', '5432')
        self.database: str = os.getenv('PGDATABASE', 'postgres')
        self.username: str = os.getenv('PGUSER', 'postgres')
        self.password: str = os.getenv('PGPASSWORD', '')
        self.debug_mode: bool = debug_mode

    def _get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """
        Создает подключение к базе данных.

        Returns:
            Optional[psycopg2.extensions.connection]: Подключение к БД или None
        """
        try:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
        except psycopg2.Error as e:
            print(f"Ошибка подключения: {e}")
            return None

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Использует SQL-запрос с JOIN для объединения данных из таблиц
        companies и vacancies.

        Returns:
            List[Dict[str, Any]]: Список компаний с количеством вакансий
        """
        connection = self._get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT 
                c.company_id,
                c.company_name,
                COUNT(v.vacancy_id) as vacancies_count
            FROM companies c
            LEFT JOIN vacancies v ON c.company_id = v.company_id
            GROUP BY c.company_id, c.company_name
            ORDER BY vacancies_count DESC;
            """

            cursor.execute(query)
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Использует SQL-запрос с JOIN для объединения данных из таблиц.

        Returns:
            List[Dict[str, Any]]: Список всех вакансий с деталями
        """
        connection = self._get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT 
                c.company_name,
                v.vacancy_name,
                v.salary_from,
                v.salary_to,
                v.salary_currency,
                v.vacancy_url,
                v.area_name,
                v.experience,
                CASE 
                    WHEN v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL 
                    THEN 'Есть зарплата'
                    ELSE 'Зарплата не указана'
                END as salary_status
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            ORDER BY 
                CASE WHEN v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL THEN 0 ELSE 1 END,
                c.company_name, v.vacancy_name;
            """

            cursor.execute(query)
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям.

        Использует SQL-функцию AVG для расчета средней зарплаты
        с учетом диапазонов зарплат.

        Returns:
            Optional[float]: Средняя зарплата или None
        """
        connection = self._get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor()

            query = """
            SELECT AVG(
                CASE 
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                    THEN (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL 
                    THEN salary_from
                    WHEN salary_to IS NOT NULL 
                    THEN salary_to
                    ELSE NULL
                END
            ) as avg_salary
            FROM vacancies
            WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)
            AND (salary_currency = 'RUR' OR salary_currency IS NULL);
            """

            cursor.execute(query)
            result = cursor.fetchone()

            if result and result[0]:
                return float(result[0])
            return None

        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Использует подзапрос для фильтрации через WHERE с условием
        сравнения со средней зарплатой.

        Returns:
            List[Dict[str, Any]]: Список вакансий с зарплатой выше средней
        """
        avg_salary = self.get_avg_salary()
        if not avg_salary:
            return []

        connection = self._get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT 
                c.company_name,
                v.vacancy_name,
                v.salary_from,
                v.salary_to,
                v.salary_currency,
                v.vacancy_url,
                CASE 
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL 
                    THEN (v.salary_from + v.salary_to) / 2.0
                    WHEN v.salary_from IS NOT NULL 
                    THEN v.salary_from
                    WHEN v.salary_to IS NOT NULL 
                    THEN v.salary_to
                    ELSE NULL
                END as calculated_salary
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            WHERE (
                CASE 
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL 
                    THEN (v.salary_from + v.salary_to) / 2.0
                    WHEN v.salary_from IS NOT NULL 
                    THEN v.salary_from
                    WHEN v.salary_to IS NOT NULL 
                    THEN v.salary_to
                    ELSE NULL
                END
            ) > %s
            AND (v.salary_currency = 'RUR' OR v.salary_currency IS NULL)
            ORDER BY calculated_salary DESC;
            """

            cursor.execute(query, (avg_salary,))
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова.

        Использует оператор LIKE для поиска по ключевым словам в названии вакансии.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            List[Dict[str, Any]]: Список найденных вакансий
        """
        if not keyword:
            return []

        connection = self._get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT 
                c.company_name,
                v.vacancy_name,
                v.salary_from,
                v.salary_to,
                v.salary_currency,
                v.vacancy_url,
                v.area_name
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            WHERE LOWER(v.vacancy_name) LIKE LOWER(%s)
            ORDER BY c.company_name, v.vacancy_name;
            """

            search_pattern = f"%{keyword}%"
            cursor.execute(query, (search_pattern,))
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_existing_vacancy_ids(self, company_ids: List[int] = None) -> set:
        """
        Получает ID всех существующих вакансий в базе данных.

        Args:
            company_ids: Список ID компаний для фильтрации (опционально)

        Returns:
            set: Множество ID существующих вакансий
        """
        connection = self._get_connection()
        if not connection:
            return set()

        try:
            cursor = connection.cursor()

            if company_ids:
                placeholders = ','.join(['%s'] * len(company_ids))
                query = f"""
                SELECT vacancy_id 
                FROM vacancies 
                WHERE company_id IN ({placeholders})
                """
                cursor.execute(query, company_ids)
            else:
                query = "SELECT vacancy_id FROM vacancies"
                cursor.execute(query)

            results = cursor.fetchall()
            return {str(row[0]) for row in results}

        except psycopg2.Error as e:
            print(f"Ошибка получения ID вакансий: {e}")
            return set()
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_existing_company_ids(self) -> set:
        """
        Получает ID всех существующих компаний в базе данных.

        Returns:
            set: Множество ID существующих компаний
        """
        connection = self._get_connection()
        if not connection:
            return set()

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT company_id FROM companies")
            results = cursor.fetchall()
            return {int(row[0]) for row in results}

        except psycopg2.Error as e:
            print(f"Ошибка получения ID компаний: {e}")
            return set()
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_database_cache(self, company_ids: List[int] = None) -> Dict[str, List[Dict]]:
        """
        Получает все данные из базы для использования в качестве кэша.

        Args:
            company_ids: Список ID компаний для фильтрации (опционально)

        Returns:
            Dict[str, List[Dict]]: Словарь с компаниями и вакансиями из базы
        """
        connection = self._get_connection()
        if not connection:
            return {'companies': [], 'vacancies': []}

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Получаем компании
            if company_ids:
                placeholders = ','.join(['%s'] * len(company_ids))
                companies_query = f"""
                SELECT company_id as id, company_name as name, company_url as alternate_url,
                       description, site_url, vacancies_url, open_vacancies
                FROM companies 
                WHERE company_id IN ({placeholders})
                """
                cursor.execute(companies_query, company_ids)
            else:
                companies_query = """
                SELECT company_id as id, company_name as name, company_url as alternate_url,
                       description, site_url, vacancies_url, open_vacancies
                FROM companies
                """
                cursor.execute(companies_query)
            
            companies = [dict(row) for row in cursor.fetchall()]

            # Получаем вакансии
            if company_ids:
                vacancies_query = f"""
                SELECT vacancy_id as id, company_id, vacancy_name as name,
                       salary_from, salary_to, salary_currency,
                       vacancy_url as alternate_url, requirement, responsibility,
                       experience, schedule, employment, area_name, published_at
                FROM vacancies 
                WHERE company_id IN ({placeholders})
                ORDER BY published_at DESC
                """
                cursor.execute(vacancies_query, company_ids)
            else:
                vacancies_query = """
                SELECT vacancy_id as id, company_id, vacancy_name as name,
                       salary_from, salary_to, salary_currency,
                       vacancy_url as alternate_url, requirement, responsibility,
                       experience, schedule, employment, area_name, published_at
                FROM vacancies 
                ORDER BY published_at DESC
                """
                cursor.execute(vacancies_query)

            vacancies_raw = cursor.fetchall()
            
            # Преобразуем в формат API
            vacancies = []
            for v in vacancies_raw:
                vacancy_dict = dict(v)
                
                # Преобразуем структуру для совместимости с API
                salary = None
                if vacancy_dict.get('salary_from') or vacancy_dict.get('salary_to'):
                    salary = {
                        'from': vacancy_dict.get('salary_from'),
                        'to': vacancy_dict.get('salary_to'),
                        'currency': vacancy_dict.get('salary_currency')
                    }
                
                # Формируем структуру как в API
                formatted_vacancy = {
                    'id': vacancy_dict['id'],
                    'name': vacancy_dict['name'],
                    'salary': salary,
                    'alternate_url': vacancy_dict.get('alternate_url'),
                    'published_at': vacancy_dict.get('published_at'),
                    'employer': {'id': vacancy_dict.get('company_id')},
                    'area': {'name': vacancy_dict.get('area_name')},
                    'experience': {'name': vacancy_dict.get('experience')},
                    'schedule': {'name': vacancy_dict.get('schedule')},
                    'employment': {'name': vacancy_dict.get('employment')},
                    'snippet': {
                        'requirement': vacancy_dict.get('requirement'),
                        'responsibility': vacancy_dict.get('responsibility')
                    }
                }
                vacancies.append(formatted_vacancy)

            cache_data = {
                'companies': companies,
                'vacancies': vacancies
            }
            
            if self.debug_mode:
                print(f"🗃️ Загружено из базы: {len(companies)} компаний, {len(vacancies)} вакансий")
            
            return cache_data

        except psycopg2.Error as e:
            print(f"Ошибка получения кэша из базы: {e}")
            return {'companies': [], 'vacancies': []}
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def insert_companies(self, companies_data: List[Dict]) -> bool:
        """
        Добавляет данные о компаниях в базу данных.

        Args:
            companies_data: Список словарей с данными компаний

        Returns:
            bool: True если данные добавлены успешно
        """
        connection = self._get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            for company in companies_data:
                insert_query = """
                INSERT INTO companies (
                    company_id, company_name, company_url, description,
                    site_url, vacancies_url, open_vacancies
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (company_id) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    company_url = EXCLUDED.company_url,
                    description = EXCLUDED.description,
                    site_url = EXCLUDED.site_url,
                    vacancies_url = EXCLUDED.vacancies_url,
                    open_vacancies = EXCLUDED.open_vacancies;
                """

                cursor.execute(insert_query, (
                    company.get('id'),
                    company.get('name'),
                    company.get('alternate_url'),
                    company.get('description'),
                    company.get('site_url'),
                    company.get('vacancies_url'),
                    company.get('open_vacancies', 0)
                ))

            connection.commit()
            print(f"✓ Добавлено компаний: {len(companies_data)}")
            self._invalidate_cache()  # Инвалидация кэша после добавления компаний
            return True

        except psycopg2.Error as e:
            print(f"✗ Ошибка добавления: {e}")
            connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def insert_vacancies(self, vacancies_data: List[Dict]) -> bool:
        """
        Добавляет данные о вакансиях в базу данных.

        Args:
            vacancies_data: Список словарей с данными вакансий

        Returns:
            bool: True если данные добавлены успешно
        """
        connection = self._get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            for vacancy in vacancies_data:
                # Извлекаем данные
                salary = vacancy.get('salary', {}) or {}
                experience = vacancy.get('experience', {}) or {}
                schedule = vacancy.get('schedule', {}) or {}
                employment = vacancy.get('employment', {}) or {}
                area = vacancy.get('area', {}) or {}
                employer = vacancy.get('employer', {}) or {}

                insert_query = """
                INSERT INTO vacancies (
                    vacancy_id, company_id, vacancy_name, salary_from, salary_to,
                    salary_currency, vacancy_url, requirement, responsibility,
                    experience, schedule, employment, area_name, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO UPDATE SET
                    vacancy_name = EXCLUDED.vacancy_name,
                    salary_from = EXCLUDED.salary_from,
                    salary_to = EXCLUDED.salary_to,
                    salary_currency = EXCLUDED.salary_currency,
                    requirement = EXCLUDED.requirement,
                    responsibility = EXCLUDED.responsibility;
                """

                cursor.execute(insert_query, (
                    vacancy.get('id'),
                    employer.get('id'),
                    vacancy.get('name'),
                    salary.get('from'),
                    salary.get('to'),
                    salary.get('currency'),
                    vacancy.get('alternate_url'),
                    vacancy.get('snippet', {}).get('requirement') if vacancy.get('snippet') else None,
                    vacancy.get('snippet', {}).get('responsibility') if vacancy.get('snippet') else None,
                    experience.get('name'),
                    schedule.get('name'),
                    employment.get('name'),
                    area.get('name'),
                    vacancy.get('published_at')
                ))

            connection.commit()
            print(f"✓ Добавлено вакансий: {len(vacancies_data)}")
            self._invalidate_cache()  # Инвалидация кэша после добавления вакансий
            return True

        except psycopg2.Error as e:
            print(f"✗ Ошибка добавления: {e}")
            connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def _invalidate_cache(self) -> None:
        """
        Инвалидирует кэш в памяти для всех методов чтения данных.
        Вызывается после операций записи/удаления для обеспечения актуальности данных.
        """
        # В данном примере мы предполагаем, что методы чтения данных используют
        # декоратор functools.lru_cache или подобный механизм для кэширования.
        # Для реальной инвалидации кэша, необходимо иметь доступ к объекту кэша.
        # Здесь мы имитируем процесс, вызывая метод clear_cache, если он существует.
        # В реальном приложении этот метод должен быть реализован иначе,
        # например, через прямой доступ к объекту кэша или используя Redis/Memcached.

        # Пример для методов, использующих functools.lru_cache:
        # from functools import lru_cache

        # @lru_cache(maxsize=None)
        # def get_companies_and_vacancies_count(self): ...
        # get_companies_and_vacancies_count.cache_clear() # Пример вызова

        # Так как в предоставленном коде нет явного использования lru_cache
        # или другого механизма кэширования, этот метод является заглушкой
        # и не выполняет реальной инвалидации без дополнительной логики кэширования.
        # Для демонстрации, показываем сообщение только в режиме отладки.
        if self.debug_mode:
            print("🔄 Инвалидация кэша (имитация): Методы чтения данных должны быть очищены.")