
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
            # Используем переменные окружения из Replit Database
            self.host = os.getenv('PGHOST', 'localhost')
            self.port = os.getenv('PGPORT', '5432')
            self.database = os.getenv('PGDATABASE', 'Project03')
            self.username = os.getenv('PGUSER', 'postgres')
            self.password = os.getenv('PGPASSWORD', '')
        
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
            CREATE TABLE IF NOT EXISTS vacancies_storage (
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
                WHERE table_name = 'vacancies_storage' AND column_name = 'source';
            """)
            
            if not cursor.fetchone():
                logger.info("Добавляем поле source в существующую таблицу...")
                cursor.execute("ALTER TABLE vacancies_storage ADD COLUMN source VARCHAR(50) DEFAULT 'unknown';")
                logger.info("✓ Поле source добавлено")
            
            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacancy_id ON vacancies_storage(vacancy_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON vacancies_storage(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salary ON vacancies_storage(salary_from, salary_to);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON vacancies_storage(source);")
            
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

    def add_vacancy(self, vacancies: Union[Vacancy, List[Vacancy]]) -> List[str]:
        """
        Добавляет вакансии в БД с batch-операциями для максимальной производительности.
        Возвращает список сообщений об обновлениях.
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

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
                f"SELECT vacancy_id, title, url, description, salary_from, salary_to, salary_currency FROM vacancies_storage WHERE vacancy_id IN ({placeholders})",
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
                INSERT INTO vacancies_storage (
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
                    UPDATE vacancies_storage SET
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
            logger.info(f"Batch операция: добавлено {len(new_vacancies)}, обновлено {len(update_vacancies)} вакансий")
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка при batch добавлении вакансий: {e}")
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
            query = "SELECT * FROM vacancies_storage"
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
            cursor.execute("DELETE FROM vacancies_storage")
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
            cursor.execute("DELETE FROM vacancies_storage WHERE vacancy_id = %s", (vacancy_id,))
            
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
                "DELETE FROM vacancies_storage WHERE LOWER(title) LIKE LOWER(%s)",
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
            query = f"DELETE FROM vacancies_storage WHERE vacancy_id IN ({placeholders})"
            
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
            cursor.execute("SELECT 1 FROM vacancies_storage WHERE vacancy_id = %s", (vacancy.vacancy_id,))
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
        Проверяет существование множества вакансий одним запросом
        
        Args:
            vacancies: Список вакансий для проверки
            
        Returns:
            Dict[str, bool]: Словарь {vacancy_id: exists}
        """
        if not vacancies:
            return {}
            
        vacancy_ids = [v.vacancy_id for v in vacancies]
        connection = self._get_connection()
        
        try:
            cursor = connection.cursor()
            
            # Создаем плейсхолдеры для IN запроса
            placeholders = ','.join(['%s'] * len(vacancy_ids))
            query = f"SELECT vacancy_id FROM vacancies_storage WHERE vacancy_id IN ({placeholders})"
            
            cursor.execute(query, vacancy_ids)
            existing_ids = {row[0] for row in cursor.fetchall()}
            
            # Создаем результат для всех проверяемых ID
            result = {}
            for vacancy_id in vacancy_ids:
                result[vacancy_id] = vacancy_id in existing_ids
                
            return result
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка пакетной проверки вакансий: {e}")
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
            cursor.execute("SELECT COUNT(*) FROM vacancies_storage")
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
            
            query = "SELECT COUNT(*) FROM vacancies_storage"
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
            SELECT * FROM vacancies_storage 
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

    @property
    def filename(self) -> str:
        """Возвращает информацию о БД (для совместимости)"""
        return f"PostgreSQL://{self.host}:{self.port}/{self.database}"

    # Новые методы бизнес-логики на SQL
    def get_vacancies_paginated(self, page: int = 1, page_size: int = 10, 
                              filters: Optional[Dict[str, Any]] = None,
                              sort_by: str = "created_at", sort_desc: bool = True) -> Tuple[List[Vacancy], int]:
        """SQL-оптимизированная пагинация с сортировкой"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            # Получаем общее количество
            count_query = "SELECT COUNT(*) FROM vacancies_storage"
            count_params = []
            where_conditions = self._build_where_conditions(filters)
            
            if where_conditions['conditions']:
                count_query += " WHERE " + " AND ".join(where_conditions['conditions'])
                count_params = where_conditions['params']
            
            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]
            
            # Получаем данные с пагинацией
            valid_sort_fields = ['created_at', 'updated_at', 'title', 'salary_from', 'salary_to', 'published_at']
            sort_field = sort_by if sort_by in valid_sort_fields else 'created_at'
            sort_order = 'DESC' if sort_desc else 'ASC'
            
            query = f"SELECT * FROM vacancies_storage"
            params = []
            
            if where_conditions['conditions']:
                query += " WHERE " + " AND ".join(where_conditions['conditions'])
                params = where_conditions['params']
            
            query += f" ORDER BY {sort_field} {sort_order}"
            
            # Добавляем LIMIT и OFFSET
            offset = (page - 1) * page_size
            query += " LIMIT %s OFFSET %s"
            params.extend([page_size, offset])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            vacancies = self._convert_rows_to_vacancies(results)
            return vacancies, total_count
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка пагинации вакансий: {e}")
            return [], 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def search_vacancies_advanced(self, keywords: List[str], salary_range: Optional[Tuple[int, int]] = None,
                                experience_levels: Optional[List[str]] = None,
                                employment_types: Optional[List[str]] = None,
                                page: int = 1, page_size: int = 10) -> Tuple[List[Vacancy], int]:
        """SQL-оптимизированный расширенный поиск"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            # Строим условия поиска
            where_conditions = []
            params = []
            
            # Поиск по ключевым словам
            if keywords:
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append(
                        "(LOWER(title) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s) OR LOWER(requirements) LIKE LOWER(%s))"
                    )
                    keyword_param = f"%{keyword}%"
                    params.extend([keyword_param, keyword_param, keyword_param])
                
                where_conditions.append(f"({' AND '.join(keyword_conditions)})")
            
            # Фильтр по зарплате
            if salary_range:
                min_salary, max_salary = salary_range
                where_conditions.append("(salary_from >= %s OR salary_to >= %s)")
                where_conditions.append("(salary_from <= %s OR salary_to <= %s)")
                params.extend([min_salary, min_salary, max_salary, max_salary])
            
            # Фильтр по опыту
            if experience_levels:
                exp_placeholders = ','.join(['%s'] * len(experience_levels))
                where_conditions.append(f"LOWER(experience) IN ({exp_placeholders})")
                params.extend([exp.lower() for exp in experience_levels])
            
            # Фильтр по типу занятости
            if employment_types:
                emp_placeholders = ','.join(['%s'] * len(employment_types))
                where_conditions.append(f"LOWER(employment) IN ({emp_placeholders})")
                params.extend([emp.lower() for emp in employment_types])
            
            base_where = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Получаем количество
            count_query = f"SELECT COUNT(*) FROM vacancies_storage{base_where}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # Получаем данные с пагинацией
            offset = (page - 1) * page_size
            query = f"""
            SELECT * FROM vacancies_storage{base_where}
            ORDER BY 
                CASE WHEN salary_from IS NOT NULL OR salary_to IS NOT NULL THEN 0 ELSE 1 END,
                GREATEST(COALESCE(salary_from, 0), COALESCE(salary_to, 0)) DESC,
                created_at DESC
            LIMIT %s OFFSET %s
            """
            
            params.extend([page_size, offset])
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            vacancies = self._convert_rows_to_vacancies(results)
            return vacancies, total_count
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка расширенного поиска: {e}")
            return [], 0
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_salary_statistics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """SQL-агрегация статистики по зарплатам"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            
            where_conditions = self._build_where_conditions(filters)
            base_where = ""
            params = []
            
            if where_conditions['conditions']:
                base_where = " WHERE " + " AND ".join(where_conditions['conditions'])
                params = where_conditions['params']
            
            # Статистика по зарплатам с фильтрацией NULL значений
            query = f"""
            SELECT 
                COUNT(*) as total_vacancies,
                COUNT(CASE WHEN salary_from IS NOT NULL OR salary_to IS NOT NULL THEN 1 END) as with_salary,
                MIN(GREATEST(COALESCE(salary_from, 0), COALESCE(salary_to, 0))) as min_salary,
                MAX(GREATEST(COALESCE(salary_from, 0), COALESCE(salary_to, 0))) as max_salary,
                AVG(GREATEST(COALESCE(salary_from, 0), COALESCE(salary_to, 0))) as avg_salary,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY GREATEST(COALESCE(salary_from, 0), COALESCE(salary_to, 0))) as median_salary
            FROM vacancies_storage{base_where}
            """
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            return {
                'total_vacancies': result[0],
                'vacancies_with_salary': result[1],
                'min_salary': result[2] if result[2] else 0,
                'max_salary': result[3] if result[3] else 0,
                'avg_salary': round(result[4], 2) if result[4] else 0,
                'median_salary': round(result[5], 2) if result[5] else 0,
                'salary_coverage': round((result[1] / result[0] * 100), 2) if result[0] > 0 else 0
            }
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения статистики зарплат: {e}")
            return {}
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_top_employers(self, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """SQL-агрегация топа работодателей"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            
            where_conditions = self._build_where_conditions(filters)
            base_where = ""
            params = []
            
            if where_conditions['conditions']:
                base_where = " WHERE " + " AND ".join(where_conditions['conditions'])
                params = where_conditions['params']
            
            query = f"""
            SELECT 
                employer,
                COUNT(*) as vacancy_count,
                AVG(GREATEST(COALESCE(salary_from, 0), COALESCE(salary_to, 0))) as avg_salary,
                COUNT(CASE WHEN salary_from IS NOT NULL OR salary_to IS NOT NULL THEN 1 END) as vacancies_with_salary
            FROM vacancies_storage{base_where}
            WHERE employer IS NOT NULL AND employer != ''
            GROUP BY employer
            ORDER BY vacancy_count DESC
            LIMIT %s
            """
            
            params.append(limit)
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [
                {
                    'employer': row[0],
                    'vacancy_count': row[1],
                    'avg_salary': round(row[2], 2) if row[2] else 0,
                    'vacancies_with_salary': row[3]
                }
                for row in results
            ]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения топа работодателей: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

    def get_popular_keywords(self, limit: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """SQL-анализ популярных ключевых слов"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            
            where_conditions = self._build_where_conditions(filters)
            base_where = ""
            params = []
            
            if where_conditions['conditions']:
                base_where = " WHERE " + " AND ".join(where_conditions['conditions'])
                params = where_conditions['params']
            
            # Используем простой подход с разделением по словам
            query = f"""
            WITH keywords AS (
                SELECT 
                    LOWER(TRIM(unnest(string_to_array(requirements, ' ')))) as keyword
                FROM vacancies_storage{base_where}
                WHERE requirements IS NOT NULL
            ),
            filtered_keywords AS (
                SELECT keyword
                FROM keywords
                WHERE LENGTH(keyword) > 3 
                AND keyword NOT IN ('для', 'что', 'как', 'все', 'вас', 'мы', 'наш', 'ваш', 'это', 'или', 'так', 'может', 'быть', 'его', 'ее', 'их')
                AND keyword ~ '^[а-яё]+$|^[a-z]+$'
            )
            SELECT 
                keyword,
                COUNT(*) as frequency
            FROM filtered_keywords
            GROUP BY keyword
            ORDER BY frequency DESC
            LIMIT %s
            """
            
            params.append(limit)
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [
                {
                    'keyword': row[0],
                    'frequency': row[1]
                }
                for row in results
            ]
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка анализа ключевых слов: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

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
