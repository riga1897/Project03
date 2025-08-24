"""
Модуль для создания и настройки базы данных PostgreSQL
"""

import psycopg2
import os
from typing import Optional


class DatabaseSetup:
    """
    Класс для создания и настройки структуры базы данных.
    
    Отвечает за автоматическое создание БД и таблиц для хранения данных 
    о компаниях и вакансиях с HeadHunter.
    """
    
    def __init__(self) -> None:
        """Инициализация с параметрами подключения из переменных окружения."""
        self.host: str = os.getenv('PGHOST', 'localhost')
        self.port: str = os.getenv('PGPORT', '5432')
        self.database: str = os.getenv('PGDATABASE', 'postgres')
        self.username: str = os.getenv('PGUSER', 'postgres')
        self.password: str = os.getenv('PGPASSWORD', '')
        
    def get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """
        Создает подключение к базе данных PostgreSQL.
        
        Returns:
            Optional[psycopg2.extensions.connection]: Объект подключения или None
        """
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            return connection
        except psycopg2.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return None
    
    def create_tables(self) -> bool:
        """
        Создает таблицы для хранения данных.
        
        Создаются две таблицы:
        - companies: для хранения информации о компаниях
        - vacancies: для хранения информации о вакансиях с FK на companies
        
        Returns:
            bool: True если таблицы созданы успешно
        """
        connection = self.get_connection()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            
            # Удаляем таблицы если существуют
            cursor.execute("DROP TABLE IF EXISTS vacancies CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS companies CASCADE;")
            
            # Создаем таблицу компаний
            create_companies = """
            CREATE TABLE companies (
                company_id INTEGER PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                company_url VARCHAR(500),
                description TEXT,
                site_url VARCHAR(500),
                vacancies_url VARCHAR(500),
                open_vacancies INTEGER DEFAULT 0
            );
            """
            cursor.execute(create_companies)
            
            # Создаем таблицу вакансий с FK на companies
            create_vacancies = """
            CREATE TABLE vacancies (
                vacancy_id INTEGER PRIMARY KEY,
                company_id INTEGER REFERENCES companies(company_id),
                vacancy_name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                salary_currency VARCHAR(10),
                vacancy_url VARCHAR(500),
                requirement TEXT,
                responsibility TEXT,
                experience VARCHAR(100),
                schedule VARCHAR(100),
                employment VARCHAR(100),
                area_name VARCHAR(100),
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_vacancies)
            
            # Создаем индексы для оптимизации
            cursor.execute("CREATE INDEX idx_vacancies_company ON vacancies(company_id);")
            cursor.execute("CREATE INDEX idx_vacancies_salary ON vacancies(salary_from, salary_to);")
            cursor.execute("CREATE INDEX idx_vacancies_name ON vacancies(vacancy_name);")
            
            connection.commit()
            print("✓ Таблицы успешно созданы")
            return True
            
        except psycopg2.Error as e:
            print(f"✗ Ошибка создания таблиц: {e}")
            connection.rollback()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()
    
    def test_connection(self) -> bool:
        """
        Проверяет подключение к базе данных.
        
        Returns:
            bool: True если подключение успешно
        """
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                if version:
                    print(f"✓ PostgreSQL подключен: {version[0][:30]}...")
                cursor.close()
                connection.close()
                return True
            except psycopg2.Error as e:
                print(f"✗ Ошибка подключения: {e}")
                return False
        return False