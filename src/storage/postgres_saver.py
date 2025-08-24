
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Union, Optional
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
            self.database = db_config.get('database', 'postgres')
            self.username = db_config.get('username', 'postgres')
            self.password = db_config.get('password', '')
        else:
            # Используем переменные окружения из Replit Database
            self.host = os.getenv('PGHOST', 'localhost')
            self.port = os.getenv('PGPORT', '5432')
            self.database = os.getenv('PGDATABASE', 'postgres')
            self.username = os.getenv('PGUSER', 'postgres')
            self.password = os.getenv('PGPASSWORD', '')
        
        self._ensure_tables_exist()

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
                published_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_query)
            
            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacancy_id ON vacancies_storage(vacancy_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON vacancies_storage(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salary ON vacancies_storage(salary_from, salary_to);")
            
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
        Добавляет вакансии в БД с выводом информационных сообщений об изменениях.
        Возвращает список сообщений об обновлениях.
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        connection = self._get_connection()
        update_messages: List[str] = []
        
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            for new_vac in vacancies:
                # Проверяем существование вакансии
                cursor.execute("SELECT * FROM vacancies_storage WHERE vacancy_id = %s", (new_vac.vacancy_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Обновляем существующую вакансию
                    changed_fields = []
                    
                    # Проверяем изменения
                    if existing['title'] != new_vac.title:
                        changed_fields.append('title')
                    if existing['url'] != new_vac.url:
                        changed_fields.append('url')
                    if existing['description'] != new_vac.description:
                        changed_fields.append('description')
                    
                    # Проверяем зарплату
                    salary_from = new_vac.salary.salary_from if new_vac.salary else None
                    salary_to = new_vac.salary.salary_to if new_vac.salary else None
                    salary_currency = new_vac.salary.currency if new_vac.salary else None
                    
                    if (existing['salary_from'] != salary_from or 
                        existing['salary_to'] != salary_to or 
                        existing['salary_currency'] != salary_currency):
                        changed_fields.append('salary')
                    
                    if changed_fields:
                        update_query = """
                        UPDATE vacancies_storage SET
                            title = %s, url = %s, salary_from = %s, salary_to = %s,
                            salary_currency = %s, description = %s, requirements = %s,
                            responsibilities = %s, experience = %s, employment = %s,
                            schedule = %s, employer = %s, area = %s, published_at = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE vacancy_id = %s
                        """
                        
                        cursor.execute(update_query, (
                            new_vac.title, new_vac.url, salary_from, salary_to,
                            salary_currency, new_vac.description, new_vac.requirements,
                            new_vac.responsibilities, new_vac.experience, new_vac.employment,
                            new_vac.schedule, new_vac.employer, new_vac.area,
                            new_vac.published_at, new_vac.vacancy_id
                        ))
                        
                        message = (
                            f"Вакансия ID {new_vac.vacancy_id} обновлена. "
                            f"Измененные поля: {', '.join(changed_fields)}. "
                            f"Название: '{new_vac.title}'"
                        )
                        update_messages.append(message)
                else:
                    # Добавляем новую вакансию
                    insert_query = """
                    INSERT INTO vacancies_storage (
                        vacancy_id, title, url, salary_from, salary_to, salary_currency,
                        description, requirements, responsibilities, experience,
                        employment, schedule, employer, area, published_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    salary_from = new_vac.salary.salary_from if new_vac.salary else None
                    salary_to = new_vac.salary.salary_to if new_vac.salary else None
                    salary_currency = new_vac.salary.currency if new_vac.salary else None
                    
                    cursor.execute(insert_query, (
                        new_vac.vacancy_id, new_vac.title, new_vac.url,
                        salary_from, salary_to, salary_currency,
                        new_vac.description, new_vac.requirements, new_vac.responsibilities,
                        new_vac.experience, new_vac.employment, new_vac.schedule,
                        new_vac.employer, new_vac.area, new_vac.published_at
                    ))
                    
                    message = f"Добавлена новая вакансия ID {new_vac.vacancy_id}: '{new_vac.title}'"
                    update_messages.append(message)
            
            connection.commit()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка при добавлении вакансий: {e}")
            connection.rollback()
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
            
        return update_messages

    def load_vacancies(self) -> List[Vacancy]:
        """Загружает все вакансии из БД"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM vacancies_storage ORDER BY created_at DESC")
            results = cursor.fetchall()
            
            vacancies = []
            for row in results:
                # Создаем объект Salary если есть данные о зарплате
                salary = None
                if row['salary_from'] or row['salary_to']:
                    from src.utils.salary import Salary
                    salary = Salary(
                        salary_from=row['salary_from'],
                        salary_to=row['salary_to'],
                        currency=row['salary_currency']
                    )
                
                vacancy = Vacancy(
                    title=row['title'],
                    url=row['url'],
                    salary=salary,
                    description=row['description'],
                    requirements=row['requirements'],
                    responsibilities=row['responsibilities'],
                    experience=row['experience'],
                    employment=row['employment'],
                    schedule=row['schedule'],
                    employer=row['employer'],
                    area=row['area'],
                    vacancy_id=row['vacancy_id'],
                    published_at=row['published_at']
                )
                vacancies.append(vacancy)
                
            return vacancies
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка загрузки вакансий: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()

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

    @property
    def filename(self) -> str:
        """Возвращает информацию о БД (для совместимости)"""
        return f"PostgreSQL://{self.host}:{self.port}/{self.database}"
