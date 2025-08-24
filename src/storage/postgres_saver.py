import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Union, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import json

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class PostgresSaver:
    """
    Класс для работы с PostgreSQL хранилищем вакансий.

    Обеспечивает сохранение, загрузку, обновление и удаление вакансий
    в PostgreSQL базе данных с валидацией данных и обработкой ошибок.
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
            # Используем переменные окружения через EnvLoader (поддерживает .env и Secrets)
            from src.utils.env_loader import EnvLoader
            self.host = EnvLoader.get_env_var('PGHOST', 'localhost')
            self.port = EnvLoader.get_env_var('PGPORT', '5432')
            self.database = EnvLoader.get_env_var('PGDATABASE', 'Project03')
            self.username = EnvLoader.get_env_var('PGUSER', 'postgres')
            self.password = EnvLoader.get_env_var('PGPASSWORD', '')

        self._ensure_database_exists()
        self._ensure_tables_exist()

    def _get_connection(self, database=None):
        """Создает подключение к базе данных"""
        db_name = database or self.database
        try:
            return psycopg2.connect(
                host=self.host,
                port=self.port,
                database=db_name,
                user=self.username,
                password=self.password
            )
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к БД {db_name}: {e}")
            raise

    def _ensure_database_exists(self):
        """Создает базу данных Project03 если она не существует"""
        # Подключаемся к системной БД postgres для создания новой БД
        connection = self._get_connection('postgres')
        connection.autocommit = True

        try:
            cursor = connection.cursor()

            # Проверяем существование базы данных Project03
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.database,)
            )

            db_exists = cursor.fetchone() is not None

            if db_exists:
                logger.info(f"✓ База данных {self.database} уже существует")
            else:
                # Создаем новую базу данных только если её нет
                cursor.execute(f'CREATE DATABASE "{self.database}"')
                logger.info(f"✓ База данных {self.database} создана")

        except psycopg2.Error as e:
            logger.error(f"Ошибка при создании базы данных {self.database}: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def _ensure_tables_exist(self):
        """Создает таблицы если они не существуют"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Создаем таблицу для вакансий
            create_table_query = """
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                vacancy_id VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                url TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                salary_currency VARCHAR(10),
                description TEXT,
                requirements TEXT,
                responsibilities TEXT,
                experience VARCHAR(200),
                employment VARCHAR(200),
                schedule VARCHAR(200),
                employer VARCHAR(500),
                area VARCHAR(200),
                source VARCHAR(50) DEFAULT 'unknown',
                published_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            cursor.execute(create_table_query)

            # Проверяем существование поля source и добавляем если его нет
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'vacancies' AND column_name = 'source';
            """)

            if not cursor.fetchone():
                logger.info("Добавляем поле source в существующую таблицу...")
                cursor.execute("ALTER TABLE vacancies ADD COLUMN source VARCHAR(50) DEFAULT 'unknown';")
                logger.info("✓ Поле source добавлено")

            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacancy_id ON vacancies(vacancy_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON vacancies(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salary ON vacancies(salary_from, salary_to);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON vacancies(source);")

            connection.commit()
            logger.info("✓ Таблицы успешно созданы/проверены")

        except psycopg2.Error as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            connection.rollback()
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def add_vacancy_batch_optimized(self, vacancies: Union[Vacancy, List[Vacancy]]) -> List[str]:
        """
        Максимально оптимизированное batch-добавление вакансий через временные таблицы.
        Использует SQL для всех операций, минимизирует количество запросов.
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        if not vacancies:
            return []

        connection = self._get_connection()
        update_messages: List[str] = []

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Создаем временную таблицу для новых вакансий
            cursor.execute("""
                CREATE TEMP TABLE temp_new_vacancies (
                    vacancy_id VARCHAR(50),
                    title VARCHAR(500),
                    url TEXT,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    salary_currency VARCHAR(10),
                    description TEXT,
                    requirements TEXT,
                    responsibilities TEXT,
                    experience VARCHAR(200),
                    employment VARCHAR(200),
                    schedule VARCHAR(200),
                    employer VARCHAR(500),
                    area VARCHAR(200),
                    source VARCHAR(50),
                    published_at TIMESTAMP
                ) ON COMMIT DROP
            """)

            # Подготавливаем данные для вставки
            insert_data = []
            for vac in vacancies:
                salary_from = vac.salary.salary_from if vac.salary else None
                salary_to = vac.salary.salary_to if vac.salary else None
                salary_currency = vac.salary.currency if vac.salary else None

                employer_str = (
                    vac.employer.get('name') if isinstance(vac.employer, dict) 
                    else str(vac.employer) if vac.employer else None
                )
                area_str = (
                    vac.area.get('name') if isinstance(vac.area, dict)
                    else str(vac.area) if vac.area else None
                )

                insert_data.append((
                    vac.vacancy_id, vac.title, vac.url,
                    salary_from, salary_to, salary_currency,
                    vac.description, vac.requirements, vac.responsibilities,
                    vac.experience, vac.employment, vac.schedule,
                    employer_str, area_str, vac.source, vac.published_at
                ))

            # Bulk insert во временную таблицу
            from psycopg2.extras import execute_values
            execute_values(
                cursor,
                """INSERT INTO temp_new_vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at
                ) VALUES %s""",
                insert_data,
                template=None,
                page_size=1000
            )

            # Находим новые вакансии (которых нет в основной таблице)
            cursor.execute("""
                INSERT INTO vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at
                )
                SELECT t.* FROM temp_new_vacancies t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
                WHERE v.vacancy_id IS NULL
            """)

            new_count = cursor.rowcount

            # Находим и обновляем существующие вакансии с изменениями
            cursor.execute("""
                UPDATE vacancies v SET
                    title = t.title,
                    url = t.url,
                    salary_from = t.salary_from,
                    salary_to = t.salary_to,
                    salary_currency = t.salary_currency,
                    description = t.description,
                    requirements = t.requirements,
                    responsibilities = t.responsibilities,
                    experience = t.experience,
                    employment = t.employment,
                    schedule = t.schedule,
                    employer = t.employer,
                    area = t.area,
                    source = t.source,
                    published_at = t.published_at,
                    updated_at = CURRENT_TIMESTAMP
                FROM temp_new_vacancies t
                WHERE v.vacancy_id = t.vacancy_id
                AND (
                    v.title != t.title OR
                    v.url != t.url OR
                    v.description != t.description OR
                    COALESCE(v.salary_from, 0) != COALESCE(t.salary_from, 0) OR
                    COALESCE(v.salary_to, 0) != COALESCE(t.salary_to, 0) OR
                    COALESCE(v.salary_currency, '') != COALESCE(t.salary_currency, '')
                )
            """)

            updated_count = cursor.rowcount

            # Получаем информацию о добавленных и обновленных вакансиях для сообщений
            cursor.execute("""
                SELECT t.vacancy_id, t.title, 
                       CASE WHEN v.vacancy_id IS NULL THEN 'new' ELSE 'updated' END as action
                FROM temp_new_vacancies t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
                ORDER BY action, t.vacancy_id
                LIMIT 10
            """)

            results = cursor.fetchall()
            for row in results:
                if row['action'] == 'new':
                    update_messages.append(f"Добавлена новая вакансия ID {row['vacancy_id']}: '{row['title']}'")
                else:
                    update_messages.append(f"Вакансия ID {row['vacancy_id']} обновлена: '{row['title']}'")

            # Добавляем сводку если много операций
            total_processed = len(vacancies)
            if total_processed > 10:
                if new_count > 5:
                    update_messages.append(f"... и еще {new_count - 5} новых вакансий")
                if updated_count > 5:
                    update_messages.append(f"... и еще {updated_count - 5} обновленных вакансий")

            connection.commit()
            logger.info(f"Batch операция через временные таблицы: добавлено {new_count}, обновлено {updated_count} вакансий")

        except psycopg2.Error as e:
            logger.error(f"Ошибка при batch операции через временные таблицы: {e}")
            connection.rollback()
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

        return update_messages

    def add_vacancy(self, vacancies: Union[Vacancy, List[Vacancy]]) -> List[str]:
        """
        Добавляет вакансии в БД. Использует оптимизированный метод для больших объемов.
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        # Для небольших объемов используем старый алгоритм, для больших - оптимизированный
        if len(vacancies) <= 50:
            return self._add_vacancy_small_batch(vacancies)
        else:
            return self.add_vacancy_batch_optimized(vacancies)

    def _add_vacancy_small_batch(self, vacancies: List[Vacancy]) -> List[str]:
        """Оригинальный алгоритм для небольших batch-операций"""
        if not vacancies:
            return []

        connection = self._get_connection()
        update_messages: List[str] = []

        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Batch проверка существования вакансий
            vacancy_ids = [v.vacancy_id for v in vacancies]
            placeholders = ','.join(['%s'] * len(vacancy_ids))

            cursor.execute(
                f"SELECT vacancy_id, title, url, description, salary_from, salary_to, salary_currency FROM vacancies WHERE vacancy_id IN ({placeholders})",
                vacancy_ids
            )

            existing_map = {row['vacancy_id']: row for row in cursor.fetchall()}

            # Разделяем на новые и обновляемые вакансии
            new_vacancies = []
            update_vacancies = []

            for vac in vacancies:
                if vac.vacancy_id in existing_map:
                    existing = existing_map[vac.vacancy_id]

                    # Проверяем изменения
                    salary_from = vac.salary.salary_from if vac.salary else None
                    salary_to = vac.salary.salary_to if vac.salary else None
                    salary_currency = vac.salary.currency if vac.salary else None

                    has_changes = (
                        existing['title'] != vac.title or
                        existing['url'] != vac.url or
                        existing['description'] != vac.description or
                        existing['salary_from'] != salary_from or
                        existing['salary_to'] != salary_to or
                        existing['salary_currency'] != salary_currency
                    )

                    if has_changes:
                        update_vacancies.append(vac)
                        update_messages.append(f"Вакансия ID {vac.vacancy_id} обновлена: '{vac.title}'")
                else:
                    new_vacancies.append(vac)
                    update_messages.append(f"Добавлена новая вакансия ID {vac.vacancy_id}: '{vac.title}'")

            # Batch insert новых вакансий
            if new_vacancies:
                insert_data = []
                for vac in new_vacancies:
                    salary_from = vac.salary.salary_from if vac.salary else None
                    salary_to = vac.salary.salary_to if vac.salary else None
                    salary_currency = vac.salary.currency if vac.salary else None

                    employer_str = (
                        vac.employer.get('name') if isinstance(vac.employer, dict) 
                        else str(vac.employer) if vac.employer else None
                    )
                    area_str = (
                        vac.area.get('name') if isinstance(vac.area, dict)
                        else str(vac.area) if vac.area else None
                    )

                    insert_data.append((
                        vac.vacancy_id, vac.title, vac.url,
                        salary_from, salary_to, salary_currency,
                        vac.description, vac.requirements, vac.responsibilities,
                        vac.experience, vac.employment, vac.schedule,
                        employer_str, area_str, vac.source, vac.published_at
                    ))

                insert_query = """
                INSERT INTO vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at
                ) VALUES %s
                """

                from psycopg2.extras import execute_values
                execute_values(cursor, insert_query, insert_data, template=None, page_size=100)

            # Batch update существующих вакансий
            if update_vacancies:
                for vac in update_vacancies:
                    salary_from = vac.salary.salary_from if vac.salary else None
                    salary_to = vac.salary.salary_to if vac.salary else None
                    salary_currency = vac.salary.currency if vac.salary else None

                    employer_str = (
                        vac.employer.get('name') if isinstance(vac.employer, dict) 
                        else str(vac.employer) if vac.employer else None
                    )
                    area_str = (
                        vac.area.get('name') if isinstance(vac.area, dict)
                        else str(vac.area) if vac.area else None
                    )

                    update_query = """
                    UPDATE vacancies SET
                        title = %s, url = %s, salary_from = %s, salary_to = %s,
                        salary_currency = %s, description = %s, requirements = %s,
                        responsibilities = %s, experience = %s, employment = %s,
                        schedule = %s, employer = %s, area = %s, source = %s, published_at = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE vacancy_id = %s
                    """

                    cursor.execute(update_query, (
                        vac.title, vac.url, salary_from, salary_to,
                        salary_currency, vac.description, vac.requirements,
                        vac.responsibilities, vac.experience, vac.employment,
                        vac.schedule, employer_str, area_str, vac.source,
                        vac.published_at, vac.vacancy_id
                    ))

            connection.commit()
            logger.info(f"Малый batch: добавлено {len(new_vacancies)}, обновлено {len(update_vacancies)} вакансий")

        except psycopg2.Error as e:
            logger.error(f"Ошибка при малом batch добавлении вакансий: {e}")
            connection.rollback()
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

        return update_messages

    def load_vacancies(self, limit: Optional[int] = None, offset: int = 0, filters: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """
        Загружает вакансии из БД с поддержкой пагинации и фильтров

        Args:
            limit: Максимальное количество вакансий
            offset: Смещение для пагинации
            filters: Словарь с фильтрами (title, salary_from, salary_to, employer)
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Строим базовый запрос
            query = "SELECT * FROM vacancies"
            params = []
            where_conditions = []

            # Добавляем фильтры
            if filters:
                if filters.get('title'):
                    where_conditions.append("LOWER(title) LIKE LOWER(%s)")
                    params.append(f"%{filters['title']}%")

                if filters.get('salary_from'):
                    where_conditions.append("salary_from >= %s")
                    params.append(filters['salary_from'])

                if filters.get('salary_to'):
                    where_conditions.append("salary_to <= %s")
                    params.append(filters['salary_to'])

                if filters.get('employer'):
                    where_conditions.append("LOWER(employer) LIKE LOWER(%s)")
                    params.append(f"%{filters['employer']}%")

            # Добавляем WHERE если есть условия
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            # Добавляем сортировку и пагинацию
            query += " ORDER BY created_at DESC"

            if limit:
                query += " LIMIT %s"
                params.append(limit)

            if offset > 0:
                query += " OFFSET %s"
                params.append(offset)

            cursor.execute(query, params)
            results = cursor.fetchall()

            return self._convert_rows_to_vacancies(results)

        except psycopg2.Error as e:
            logger.error(f"Ошибка загрузки вакансий: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def _convert_rows_to_vacancies(self, rows: List[Dict]) -> List[Vacancy]:
        """Конвертирует строки БД в объекты Vacancy"""
        vacancies = []
        for row in rows:
            try:
                # Создаем словарь salary_data для передачи в конструктор Vacancy
                salary_data = None
                if row['salary_from'] or row['salary_to']:
                    salary_data = {
                        'from': row['salary_from'],
                        'to': row['salary_to'],
                        'currency': row['salary_currency']
                    }

                # Convert employer string back to dict format for consistency
                employer = None
                if row['employer']:
                    employer = {'name': row['employer']}

                # Convert published_at string back to proper format
                published_at = None
                if row['published_at']:
                    # Конвертируем datetime объект в строку ISO формата
                    if hasattr(row['published_at'], 'isoformat'):
                        published_at = row['published_at'].isoformat()
                    else:
                        published_at = str(row['published_at'])

                vacancy = Vacancy(
                    title=row['title'],
                    url=row['url'],
                    salary=salary_data,  # Передаем словарь, а не объект Salary
                    description=row['description'],
                    requirements=row['requirements'],
                    responsibilities=row['responsibilities'],
                    experience=row['experience'],
                    employment=row['employment'],
                    schedule=row['schedule'],
                    employer=employer,
                    vacancy_id=row['vacancy_id'],
                    published_at=published_at,
                    source=row.get('source', 'unknown')
                )

                # Устанавливаем area напрямую
                vacancy.area = row['area']
                
                # Для отладки - также сохраняем название компании напрямую
                if row['employer']:
                    vacancy._employer_name = row['employer']
                
                vacancies.append(vacancy)

            except Exception as e:
                logger.error(f"Ошибка конвертации строки в Vacancy: {e}")
                continue

        return vacancies

    def get_vacancies(self) -> List[Vacancy]:
        """Возвращает список вакансий"""
        return self.load_vacancies()

    def delete_all_vacancies(self) -> bool:
        """Удаляет все вакансии"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM vacancies")
            connection.commit()
            logger.info("Все вакансии удалены")
            return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка при удалении всех вакансий: {e}")
            connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def delete_vacancy_by_id(self, vacancy_id: str) -> bool:
        """Удаляет вакансию по ID"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM vacancies WHERE vacancy_id = %s", (vacancy_id,))

            if cursor.rowcount > 0:
                connection.commit()
                logger.info(f"Вакансия с ID {vacancy_id} удалена")
                return True
            else:
                logger.warning(f"Вакансия с ID {vacancy_id} не найдена")
                return False

        except psycopg2.Error as e:
            logger.error(f"Ошибка при удалении вакансии {vacancy_id}: {e}")
            connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def delete_vacancies_by_keyword(self, keyword: str) -> int:
        """Удаляет вакансии, содержащие указанное ключевое слово"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM vacancies WHERE LOWER(title) LIKE LOWER(%s)",
                (f"%{keyword}%",)
            )

            deleted_count = cursor.rowcount
            connection.commit()

            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} вакансий по ключевому слову '{keyword}'")

            return deleted_count

        except psycopg2.Error as e:
            logger.error(f"Ошибка при удалении вакансий по ключевому слову '{keyword}': {e}")
            connection.rollback()
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def delete_vacancies_batch(self, vacancy_ids: List[str]) -> int:
        """
        Batch удаление вакансий по списку ID

        Args:
            vacancy_ids: Список ID вакансий для удаления

        Returns:
            int: Количество удаленных вакансий
        """
        if not vacancy_ids:
            return 0

        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Создаем плейсхолдеры для IN запроса
            placeholders = ','.join(['%s'] * len(vacancy_ids))
            query = f"DELETE FROM vacancies WHERE vacancy_id IN ({placeholders})"

            cursor.execute(query, vacancy_ids)
            deleted_count = cursor.rowcount
            connection.commit()

            if deleted_count > 0:
                logger.info(f"Batch удалено {deleted_count} вакансий")

            return deleted_count

        except psycopg2.Error as e:
            logger.error(f"Ошибка при batch удалении вакансий: {e}")
            connection.rollback()
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def is_vacancy_exists(self, vacancy: Vacancy) -> bool:
        """Проверяет, существует ли вакансия в БД"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM vacancies WHERE vacancy_id = %s", (vacancy.vacancy_id,))
            return cursor.fetchone() is not None
        except psycopg2.Error as e:
            logger.error(f"Ошибка проверки существования вакансии: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def check_vacancies_exist_batch(self, vacancies: List[Vacancy]) -> Dict[str, bool]:
        """
        Проверяет существование множества вакансий через временную таблицу

        Args:
            vacancies: Список вакансий для проверки

        Returns:
            Dict[str, bool]: Словарь {vacancy_id: exists}
        """
        if not vacancies:
            return {}

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            # Создаем временную таблицу для batch-проверки
            cursor.execute("""
                CREATE TEMP TABLE temp_vacancy_check (
                    vacancy_id VARCHAR(50) PRIMARY KEY
                ) ON COMMIT DROP
            """)

            # Вставляем все ID для проверки
            vacancy_ids = [(v.vacancy_id,) for v in vacancies]
            from psycopg2.extras import execute_values
            execute_values(
                cursor, 
                "INSERT INTO temp_vacancy_check (vacancy_id) VALUES %s",
                vacancy_ids,
                template=None,
                page_size=1000
            )

            # Находим существующие ID одним запросом
            cursor.execute("""
                SELECT t.vacancy_id, (v.vacancy_id IS NOT NULL) as exists
                FROM temp_vacancy_check t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
            """)

            result = {row[0]: row[1] for row in cursor.fetchall()}

            connection.commit()
            return result

        except psycopg2.Error as e:
            logger.error(f"Ошибка batch проверки через временную таблицу: {e}")
            connection.rollback()
            # В случае ошибки возвращаем словарь с False для всех
            return {v.vacancy_id: False for v in vacancies}
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_file_size(self) -> int:
        """Возвращает количество записей в БД (аналог размера файла)"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM vacancies")
            count = cursor.fetchone()[0]
            return count * 1024  # Примерный размер в байтах
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения размера БД: {e}")
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_vacancies_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Возвращает количество вакансий с учетом фильтров

        Args:
            filters: Словарь с фильтрами

        Returns:
            int: Количество вакансий
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            query = "SELECT COUNT(*) FROM vacancies"
            params = []
            where_conditions = []

            # Добавляем фильтры
            if filters:
                if filters.get('title'):
                    where_conditions.append("LOWER(title) LIKE LOWER(%s)")
                    params.append(f"%{filters['title']}%")

                if filters.get('salary_from'):
                    where_conditions.append("salary_from >= %s")
                    params.append(filters['salary_from'])

                if filters.get('salary_to'):
                    where_conditions.append("salary_to <= %s")
                    params.append(filters['salary_to'])

                if filters.get('employer'):
                    where_conditions.append("LOWER(employer) LIKE LOWER(%s)")
                    params.append(f"%{filters['employer']}%")

            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            cursor.execute(query, params)
            return cursor.fetchone()[0]

        except psycopg2.Error as e:
            logger.error(f"Ошибка подсчета вакансий: {e}")
            return 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def search_vacancies_batch(self, keywords: List[str], limit: Optional[int] = None) -> List[Vacancy]:
        """
        Batch поиск вакансий по множественным ключевым словам

        Args:
            keywords: Список ключевых слов для поиска
            limit: Максимальное количество результатов

        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        if not keywords:
            return []

        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Строим условия поиска
            search_conditions = []
            params = []

            for keyword in keywords:
                search_conditions.append(
                    "(LOWER(title) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s) OR LOWER(requirements) LIKE LOWER(%s))"
                )
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param])

            query = f"""
            SELECT * FROM vacancies 
            WHERE {' AND '.join(search_conditions)}
            ORDER BY created_at DESC
            """

            if limit:
                query += " LIMIT %s"
                params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()

            return self._convert_rows_to_vacancies(results)

        except psycopg2.Error as e:
            logger.error(f"Ошибка batch поиска вакансий: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def filter_api_vacancies_via_temp_table(self, vacancies: List[Vacancy], filters: Dict[str, Any]) -> List[Vacancy]:
        """
        Фильтрация вакансий из API через временную таблицу средствами SQL

        Args:
            vacancies: Список вакансий из API для фильтрации
            filters: Словарь с фильтрами (salary_from, salary_to, keywords, employers, etc.)

        Returns:
            List[Vacancy]: Отфильтрованный список вакансий
        """
        if not vacancies:
            return []

        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)

            # Создаем временную таблицу для вакансий из API
            cursor.execute("""
                CREATE TEMP TABLE temp_api_vacancies (
                    vacancy_id VARCHAR(50),
                    title VARCHAR(500),
                    url TEXT,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    salary_currency VARCHAR(10),
                    description TEXT,
                    requirements TEXT,
                    responsibilities TEXT,
                    experience VARCHAR(200),
                    employment VARCHAR(200),
                    schedule VARCHAR(200),
                    employer VARCHAR(500),
                    area VARCHAR(200),
                    source VARCHAR(50),
                    published_at TIMESTAMP
                ) ON COMMIT DROP
            """)

            # Подготавливаем данные для вставки
            insert_data = []
            for vac in vacancies:
                salary_from = vac.salary.salary_from if vac.salary else None
                salary_to = vac.salary.salary_to if vac.salary else None
                salary_currency = vac.salary.currency if vac.salary else None

                employer_str = (
                    vac.employer.get('name') if isinstance(vac.employer, dict) 
                    else str(vac.employer) if vac.employer else None
                )
                area_str = (
                    vac.area.get('name') if isinstance(vac.area, dict)
                    else str(vac.area) if vac.area else None
                )

                insert_data.append((
                    vac.vacancy_id, vac.title, vac.url,
                    salary_from, salary_to, salary_currency,
                    vac.description, vac.requirements, vac.responsibilities,
                    vac.experience, vac.employment, vac.schedule,
                    employer_str, area_str, vac.source, vac.published_at
                ))

            # Bulk insert во временную таблицу
            from psycopg2.extras import execute_values
            execute_values(
                cursor,
                """INSERT INTO temp_api_vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at
                ) VALUES %s""",
                insert_data,
                template=None,
                page_size=1000
            )

            # Строим SQL-запрос с фильтрами
            where_conditions = []
            params = []

            # Фильтр по зарплате от
            if filters.get('salary_from'):
                where_conditions.append("(salary_from >= %s OR salary_to >= %s)")
                params.extend([filters['salary_from'], filters['salary_from']])

            # Фильтр по зарплате до
            if filters.get('salary_to'):
                where_conditions.append("(salary_from <= %s OR salary_to <= %s)")
                params.extend([filters['salary_to'], filters['salary_to']])

            # Фильтр по ключевым словам в названии/описании
            if filters.get('keywords'):
                keywords = filters['keywords'] if isinstance(filters['keywords'], list) else [filters['keywords']]
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append(
                        "(LOWER(title) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s) OR LOWER(requirements) LIKE LOWER(%s))"
                    )
                    keyword_param = f"%{keyword}%"
                    params.extend([keyword_param, keyword_param, keyword_param])

                if keyword_conditions:
                    where_conditions.append(f"({' OR '.join(keyword_conditions)})")

            # Фильтр по работодателям (целевые компании)
            if filters.get('target_employers'):
                employers = filters['target_employers']
                employer_conditions = []
                for employer in employers:
                    employer_conditions.append("LOWER(employer) LIKE LOWER(%s)")
                    params.append(f"%{employer}%")

                if employer_conditions:
                    where_conditions.append(f"({' OR '.join(employer_conditions)})")

            # Фильтр по опыту работы
            if filters.get('experience'):
                where_conditions.append("LOWER(experience) LIKE LOWER(%s)")
                params.append(f"%{filters['experience']}%")

            # Фильтр по типу занятости
            if filters.get('employment'):
                where_conditions.append("LOWER(employment) LIKE LOWER(%s)")
                params.append(f"%{filters['employment']}%")

            # Фильтр по графику работы
            if filters.get('schedule'):
                where_conditions.append("LOWER(schedule) LIKE LOWER(%s)")
                params.append(f"%{filters['schedule']}%")

            # Фильтр по региону
            if filters.get('area'):
                where_conditions.append("LOWER(area) LIKE LOWER(%s)")
                params.append(f"%{filters['area']}%")

            # Исключение уже существующих вакансий (опционально)
            if filters.get('exclude_existing', False):
                where_conditions.append("""
                    NOT EXISTS (
                        SELECT 1 FROM vacancies v 
                        WHERE v.vacancy_id = temp_api_vacancies.vacancy_id
                    )
                """)

            # Формируем итоговый запрос
            query = "SELECT * FROM temp_api_vacancies"
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            # Добавляем сортировку
            if filters.get('sort_by_salary', False):
                query += " ORDER BY COALESCE(salary_from, salary_to, 0) DESC"
            else:
                query += " ORDER BY published_at DESC"

            # Ограничение количества результатов
            if filters.get('limit'):
                query += " LIMIT %s"
                params.append(filters['limit'])

            cursor.execute(query, params)
            results = cursor.fetchall()

            # Конвертируем результаты обратно в объекты Vacancy
            filtered_vacancies = []
            for row in results:
                try:
                    # Находим оригинальную вакансию из списка по ID
                    original_vacancy = next((v for v in vacancies if v.vacancy_id == row['vacancy_id']), None)
                    if original_vacancy:
                        filtered_vacancies.append(original_vacancy)
                except Exception as e:
                    logger.error(f"Ошибка при восстановлении вакансии {row['vacancy_id']}: {e}")
                    continue

            connection.commit()
            logger.info(f"SQL-фильтрация через временную таблицу: отобрано {len(filtered_vacancies)} из {len(vacancies)} вакансий")

            return filtered_vacancies

        except psycopg2.Error as e:
            logger.error(f"Ошибка SQL-фильтрации через временную таблицу: {e}")
            connection.rollback()
            return vacancies  # Возвращаем исходный список при ошибке
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    @property
    def filename(self) -> str:
        """Возвращает информацию о БД (для совместимости)"""
        return f"PostgreSQL://{self.host}:{self.port}/{self.database}"

    def _build_where_conditions(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Вспомогательный метод для построения WHERE условий"""
        conditions = []
        params = []

        if not filters:
            return {'conditions': conditions, 'params': params}

        if filters.get('title'):
            conditions.append("LOWER(title) LIKE LOWER(%s)")
            params.append(f"%{filters['title']}%")

        if filters.get('salary_from'):
            conditions.append("(salary_from >= %s OR salary_to >= %s)")
            params.extend([filters['salary_from'], filters['salary_from']])

        if filters.get('salary_to'):
            conditions.append("(salary_from <= %s OR salary_to <= %s)")
            params.extend([filters['salary_to'], filters['salary_to']])

        if filters.get('employer'):
            conditions.append("LOWER(employer) LIKE LOWER(%s)")
            params.append(f"%{filters['employer']}%")

        if filters.get('experience'):
            conditions.append("LOWER(experience) LIKE LOWER(%s)")
            params.append(f"%{filters['experience']}%")

        if filters.get('employment'):
            conditions.append("LOWER(employment) LIKE LOWER(%s)")
            params.append(f"%{filters['employment']}%")

        return {'conditions': conditions, 'params': params}