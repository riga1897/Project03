"""
Класс DBManager для работы с данными в БД PostgreSQL

Реализует специфические методы согласно требованиям проекта по работе с БД.
Использует библиотеку psycopg2 для подключения к PostgreSQL.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

from src.storage.abstract_db_manager import AbstractDBManager
from src.config.db_config import DatabaseConfig
from src.config.target_companies import TargetCompanies

logger = logging.getLogger(__name__)

# Получаем список целевых компаний из единого источника
TARGET_COMPANIES = TargetCompanies.get_all_companies()


class DBManager(AbstractDBManager):
    """
    Класс для работы с базой данных PostgreSQL.
    Предоставляет методы для выполнения специфических запросов к базе данных.
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
            connection_params = self.db_config.get_connection_params()
            # Добавляем явное указание кодировки UTF-8
            connection_params['client_encoding'] = 'utf8'
            connection = psycopg2.connect(**connection_params)

            # Устанавливаем кодировку для соединения
            connection.set_client_encoding('UTF8')
            return connection
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def create_tables(self):
        """
        Создает таблицы компаний и вакансий в базе данных, если они не существуют
        Автоматически добавляет недостающие поля в существующие таблицы
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Устанавливаем кодировку сессии
                    cursor.execute("SET client_encoding TO 'UTF8'")

                    # Создаем упрощенную таблицу компаний для целевых компаний
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS companies (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL UNIQUE,
                            hh_id VARCHAR(50),
                            sj_id VARCHAR(50)
                        );
                    """)
                    logger.info("✓ Таблица companies создана/проверена")

                    # Создаем полную таблицу вакансий сразу с правильными типами
                    cursor.execute("""
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
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    
                    # Проверяем и исправляем тип company_id если нужно
                    cursor.execute("""
                        SELECT data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'vacancies' AND column_name = 'company_id'
                    """)
                    
                    result = cursor.fetchone()
                    if result and result[0] not in ('integer', 'bigint'):
                        logger.warning(f"Поле company_id имеет неправильный тип {result[0]}, исправляем...")
                        try:
                            # Сохраняем данные
                            cursor.execute("ALTER TABLE vacancies RENAME COLUMN company_id TO company_id_old")
                            # Создаем новое поле с правильным типом
                            cursor.execute("ALTER TABLE vacancies ADD COLUMN company_id INTEGER")
                            # Пытаемся скопировать данные с приведением типа
                            cursor.execute("""
                                UPDATE vacancies SET company_id = 
                                CASE 
                                    WHEN company_id_old ~ '^[0-9]+$' THEN company_id_old::INTEGER 
                                    ELSE NULL 
                                END
                            """)
                            # Удаляем старое поле
                            cursor.execute("ALTER TABLE vacancies DROP COLUMN company_id_old")
                            logger.info("✓ Поле company_id исправлено на INTEGER")
                        except Exception as e:
                            logger.warning(f"Не удалось исправить тип company_id: {e}")
                            # Откатываемся
                            try:
                                cursor.execute("ALTER TABLE vacancies DROP COLUMN IF EXISTS company_id")
                                cursor.execute("ALTER TABLE vacancies RENAME COLUMN company_id_old TO company_id")
                            except:
                                pass
                    
                    logger.info("✓ Таблица vacancies создана/проверена")

                    # Создаем индексы
                    indexes = [
                        ("idx_companies_name", "companies", "name"),
                        ("idx_vacancies_vacancy_id", "vacancies", "vacancy_id"),
                        ("idx_vacancies_title", "vacancies", "title"),
                        ("idx_vacancies_company_id", "vacancies", "company_id"),
                        ("idx_vacancies_salary", "vacancies", "salary_from, salary_to")
                    ]

                    for index_name, table_name, columns in indexes:
                        try:
                            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns});")
                            logger.info(f"✓ Индекс {index_name} проверен/создан")
                        except Exception as e:
                            logger.warning(f"Не удалось создать индекс {index_name}: {e}")

                    # Создаем внешний ключ
                    try:
                        cursor.execute("""
                            SELECT constraint_name
                            FROM information_schema.table_constraints
                            WHERE table_name = 'vacancies'
                            AND constraint_type = 'FOREIGN KEY'
                            AND constraint_name = 'fk_vacancies_company_id';
                        """)

                        if not cursor.fetchone():
                            cursor.execute("""
                                ALTER TABLE vacancies
                                ADD CONSTRAINT fk_vacancies_company_id
                                FOREIGN KEY (company_id) REFERENCES companies(id)
                                ON DELETE SET NULL;
                            """)
                            logger.info("✓ Внешний ключ fk_vacancies_company_id создан")
                    except Exception as e:
                        logger.warning(f"Не удалось создать внешний ключ: {e}")

                    logger.info("✓ Все таблицы и структуры успешно созданы/проверены")

        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

    def populate_companies_table(self):
        """Заполняет таблицу companies целевыми компаниями"""
        try:
            # Используем контекстный менеджер для безопасной работы с подключением
            with self._get_connection() as connection:
                with connection.cursor() as cursor:
                    # Устанавливаем кодировку сессии
                    cursor.execute("SET client_encoding TO 'UTF8'")

                    # Проверяем, существует ли таблица companies
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = 'companies'
                        );
                    """)

                    table_exists = cursor.fetchone()[0]
                    if not table_exists:
                        logger.warning("Таблица companies не существует. Таблицы должны быть созданы заранее.")
                        return

                    # Проверяем, есть ли уже данные в таблице
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    companies_count = cursor.fetchone()[0]

                    if companies_count > 0:
                        logger.info(f"✓ Таблица companies уже содержит {companies_count} компаний")
                        return

                    # Добавляем целевые компании с их API идентификаторами
                    for company in TARGET_COMPANIES:
                        # Сначала проверяем, существует ли компания
                        cursor.execute("SELECT id FROM companies WHERE name = %s", (company.name,))
                        if not cursor.fetchone():
                            cursor.execute("""
                                INSERT INTO companies (name, hh_id, sj_id)
                                VALUES (%s, %s, %s)
                            """, (
                                company.name,
                                getattr(company, 'hh_id', None),
                                getattr(company, 'sj_id', None)
                            ))
                            logger.info(f"Добавлена целевая компания: {company.name}")

                    # Проверяем результат
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    final_count = cursor.fetchone()[0]
                    logger.info(f"✓ Добавлено компаний в таблицу companies: {final_count}")

        except Exception as e:
            logger.error(f"Ошибка при заполнении таблицы companies: {e}")
            raise

    def get_target_companies_analysis(self) -> List[Tuple[str, int]]:
        """
        Получает анализ ТОЛЬКО по целевым компаниям
        Этот метод специально предназначен для демонстрации п.10

        Returns:
            List[Tuple[str, int]]: Список кортежей (название_целевой_компании, количество_вакансий)
        """
        try:
            # Сначала получаем все данные
            all_data = self.get_companies_and_vacancies_count()

            # Если нет данных, возвращаем все целевые компании с нулями
            if not all_data:
                return [(company.name, 0) for company in TARGET_COMPANIES]

            return all_data  # Метод уже возвращает данные по целевым компаниям

        except Exception as e:
            logger.error(f"Ошибка при анализе целевых компаний: {e}")
            # В случае ошибки возвращаем все целевые компании с нулями
            return [(company.name, 0) for company in TARGET_COMPANIES]

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании
        ВАЖНО: Метод фильтрует результаты по целевым компаниям из конфигурации

        Returns:
            List[Tuple[str, int]]: Список кортежей (название_компании, количество_вакансий)
        """
        # Проверяем подключение к БД
        if not self.check_connection():
            logger.warning("Нет подключения к базе данных")
            return [(company.name, 0) for company in TARGET_COMPANIES]

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Основной SQL-запрос с использованием LEFT JOIN для получения статистики по компаниям
                    query = """
                    -- Получение списка всех компаний и количества вакансий у каждой компании
                    -- Использует LEFT JOIN для связи вакансий с компаниями и CASE для форматирования данных
                    SELECT
                        c.name as company_name,                    -- Название компании из справочника
                        COUNT(v.id) as vacancy_count               -- Подсчет количества вакансий для каждой компании
                    FROM companies c                               -- Основная таблица компаний
                    LEFT JOIN vacancies v ON c.id = v.company_id  -- Левое соединение с таблицей вакансий
                    GROUP BY c.name, c.id                  -- Группировка по компании для агрегации COUNT()
                    ORDER BY vacancy_count DESC, company_name      -- Сортировка: сначала по количеству (убывание), затем по имени
                    """

                    cursor.execute(query)
                    results = cursor.fetchall()

                    # Если есть результаты с вакансиями, возвращаем их
                    if any(count > 0 for _, count in results):
                        return results

                    # Если нет связанных данных, работаем напрямую с таблицей vacancies
                    logger.info("Нет данных в основной схеме, переходим к fallback")

                    # Создаем результат для всех целевых компаний
                    company_results = []

                    for target_company in TARGET_COMPANIES:
                        company_name = target_company.name

                        # Сначала пытаемся найти компанию по ID в таблице companies
                        cursor.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
                        company_record = cursor.fetchone()

                        vacancy_count = 0

                        if company_record:
                            # Если компания найдена в таблице companies, ищем по company_id
                            company_db_id = company_record[0]
                            cursor.execute("""
                                SELECT COUNT(*) FROM vacancies 
                                WHERE company_id = %s
                            """, (company_db_id,))
                            count_result = cursor.fetchone()
                            vacancy_count = count_result[0] if count_result else 0

                        

                        company_results.append((company_name, vacancy_count))

                    # Сортируем по количеству вакансий (убывание), затем по названию
                    company_results.sort(key=lambda x: (-x[1], x[0]))
                    return company_results

        except Exception as e:
            logger.error(f"Ошибка при получении списка компаний и количества вакансий: {e}")
            # В случае ошибки возвращаем все целевые компании с нулями
            return [(company.name, 0) for company in TARGET_COMPANIES]

    def _is_target_company_match(self, target_name: str, db_name: str) -> bool:
        """
        Проверяет, соответствует ли название компании из БД целевой компании

        Args:
            target_name: Название целевой компании
            db_name: Название компании из БД

        Returns:
            bool: True если названия соответствуют
        """
        # Словарь сопоставлений
        mappings = {
            "Яндекс": ["яндекс"],
            "Тинькофф": ["т-банк", "tinkoff", "тинькофф"],
            "СБЕР": ["сбербанк", "сбер", "sberbank"],
            "Wildberries": ["wildberries", "wb"],
            "OZON": ["ozon"],
            "VK (ВКонтакте)": ["vk", "вконтакте", "вк"],
            "Kaspersky": ["kaspersky", "лаборатория касперского"],
            "Авито": ["авито", "avito"],
            "X5 Retail Group": ["x5", "x5 retail group"],
            "Ростелеком": ["ростелеком", "rostelecom", "билайн"],
            "Альфа-Банк": ["альфа-банк", "alfa-bank"],
            "JetBrains": ["jetbrains"],
            "2GIS": ["2гис", "2gis"],
            "Skyeng": ["skyeng"],
            "Delivery Club": ["delivery club"]
        }

        target_lower = target_name.lower()
        db_lower = db_name.lower()

        # Проверяем точное совпадение
        if target_lower == db_lower:
            return True

        # Проверяем сопоставления
        possible_names = mappings.get(target_name, [target_lower])

        for possible_name in possible_names:
            if possible_name in db_lower or db_lower in possible_name:
                return True

        return False

    def _ensure_tables_exist(self) -> bool:
        """
        Убеждается, что таблицы созданы

        Returns:
            bool: True если таблицы созданы, False иначе
        """
        try:
            self.create_tables()
            return True
        except Exception as e:
            logger.warning(f"Не удалось создать таблицы: {e}")
            return False

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию
        Использует SQL-запрос с CASE для форматирования зарплаты

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о вакансиях
        """
        if not self._ensure_tables_exist():
            return []

        query = """
        -- Получение списка всех вакансий с названием компании, зарплатой и ссылкой
        -- Использует LEFT JOIN для связи вакансий с компаниями и CASE для форматирования данных
        SELECT
            v.title,                                       -- Название вакансии
            -- Название компании берется только из таблицы companies
            COALESCE(c.name, 'Неизвестная компания') as company_name,
            -- CASE для форматирования информации о зарплате:
            -- Объединяет salary_from, salary_to и currency в читаемый формат
            CASE
                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                    CONCAT(v.salary_from, ' - ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))  -- Диапазон зарплаты
                WHEN v.salary_from IS NOT NULL THEN
                    CONCAT('от ', v.salary_from, ' ', COALESCE(v.salary_currency, 'RUR'))              -- Только минимум
                WHEN v.salary_to IS NOT NULL THEN
                    CONCAT('до ', v.salary_to, ' ', COALESCE(v.salary_currency, 'RUR'))                -- Только максимум
                ELSE 'Не указана'                                                                     -- Зарплата не указана
            END as salary_info,
            v.url,                                         -- Ссылка на вакансию
            v.vacancy_id,                                  -- ID вакансии
            v.company_id as raw_company_id,                -- Raw company_id из вакансии для диагностики
            c.id as linked_company_id                      -- ID компании из справочника
        FROM vacancies v                                   -- Основная таблица вакансий
        LEFT JOIN companies c ON v.company_id = c.id  -- Левое соединение для получения названия компании
        -- Сортировка по названию компании, затем по названию вакансии
        ORDER BY
            COALESCE(c.name, 'Неизвестная компания'),     -- Сортировка по названию компании
            v.title                                        -- Вторичная сортировка по названию вакансии
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()

                    # Диагностика связей company_id
                    unlinked_count = 0
                    linked_count = 0
                    for row in results:
                        if row.get('raw_company_id') is not None and row.get('linked_company_id') is None:
                            unlinked_count += 1
                        elif row.get('linked_company_id') is not None:
                            linked_count += 1
                    
                    if unlinked_count > 0:
                        logger.warning(f"Найдено {unlinked_count} вакансий с company_id, но без связи с таблицей companies")
                        logger.info(f"Связанных вакансий: {linked_count}")

                    # Возвращаем список словарей без вывода
                    return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Ошибка при получении всех вакансий: {e}")
            return []

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям
        Использует SQL-функцию AVG() для вычисления средней зарплаты

        Returns:
            Optional[float]: Средняя зарплата или None если данных нет
        """
        if not self._ensure_tables_exist():
            return None

        query = """
        -- Расчет средней зарплаты по всем вакансиям с использованием функции AVG()
        -- Учитывает различные варианты указания зарплаты и нормализует их к единому значению
        SELECT AVG(
            -- CASE для вычисления единого значения зарплаты из диапазона или отдельных значений
            CASE
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN
                    (salary_from + salary_to) / 2                     -- Среднее арифметическое диапазона
                WHEN salary_from IS NOT NULL THEN salary_from          -- Используем минимум, если нет максимума
                WHEN salary_to IS NOT NULL THEN salary_to              -- Используем максимум, если нет минимума
                ELSE NULL                                             -- Исключаем вакансии без зарплаты
            END
        ) as avg_salary                                               -- Применяем AVG() к нормализованным значениям
        FROM vacancies                                                -- Таблица вакансий
        -- Фильтрация: включаем только вакансии с указанной зарплатой
        WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)      -- Есть хотя бы одно значение зарплаты
        AND salary_currency IN ('RUR', 'RUB', 'руб.', NULL)          -- Только российские рубли или без валюты
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
        if not self._ensure_tables_exist():
            return []

        # Сначала получаем среднюю зарплату
        avg_salary = self.get_avg_salary()

        if avg_salary is None:
            logger.warning("Не удалось рассчитать среднюю зарплату")
            return []

        # SQL-запрос для получения вакансий с зарплатой выше средней
        query = """
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
            CASE
                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                    (v.salary_from + v.salary_to) / 2
                WHEN v.salary_from IS NOT NULL THEN v.salary_from
                WHEN v.salary_to IS NOT NULL THEN v.salary_to
                ELSE NULL
            END as calculated_salary,
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
        AND (v.salary_currency IN ('RUR', 'RUB', 'руб.') OR v.salary_currency IS NULL)
        -- Сортировка аналогично get_all_vacancies(): по зарплате (убывание), компании, названию вакансии
        ORDER BY calculated_salary DESC,
            COALESCE(c.name, 'Неизвестная компания'),
            v.title                                        -- Вторичная сортировка по названию вакансии
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (avg_salary,))
                    results = cursor.fetchall()

                    # Преобразуем результаты в список словарей
                    columns = ['title', 'company_name', 'salary_info', 'url', 'calculated_salary', 'vacancy_id']
                    vacancies = []

                    for row in results:
                        vacancy_dict = {}
                        for i, column in enumerate(columns):
                            vacancy_dict[column] = row[i] if i < len(row) else None
                        vacancies.append(vacancy_dict)

                    logger.debug(f"Найдено {len(vacancies)} вакансий с зарплатой выше средней")
                    return vacancies

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для получения вакансий с высокой зарплатой: {e}")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка в get_vacancies_with_higher_salary: {e}")
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

        if not self._ensure_tables_exist():
            return []

        # SQL-запрос для поиска вакансий по ключевому слову в названии
        query = """
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
            v.description,
            v.vacancy_id
        FROM vacancies v
        LEFT JOIN companies c ON v.company_id = c.id
        WHERE LOWER(v.title) LIKE LOWER(%s)
        -- Сортировка: сначала по зарплате (убывание), затем по названию вакансии (возрастание)
        ORDER BY
            CASE
                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN
                    (v.salary_from + v.salary_to) / 2      -- Среднее арифметическое диапазона
                WHEN v.salary_from IS NOT NULL THEN v.salary_from          -- Используем минимум
                WHEN v.salary_to IS NOT NULL THEN v.salary_to              -- Используем максимум
                ELSE 0                                     -- Вакансии без зарплаты в конце
            END DESC,                                      -- Сортировка по зарплате по убыванию
            v.title ASC                                    -- Вторичная сортировка по названию по возрастанию
        """

        try:
            search_pattern = f"%{keyword.strip()}%"

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (search_pattern,))
                    results = cursor.fetchall()

                    # Преобразуем результаты в список словарей
                    columns = ['title', 'company_name', 'salary_info', 'url', 'description', 'vacancy_id']
                    vacancies = []

                    for row in results:
                        vacancy_dict = {}
                        for i, column in enumerate(columns):
                            vacancy_dict[column] = row[i] if i < len(row) else None
                        vacancies.append(vacancy_dict)

                    logger.debug(f"Поиск по '{keyword}': найдено {len(vacancies)} вакансий")
                    return vacancies

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для поиска вакансий по ключевому слову '{keyword}': {e}")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка в get_vacancies_with_keyword: {e}")
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Получает расширенную статистику базы данных используя различные SQL-запросы

        Returns:
            Dict[str, Any]: Словарь со статистикой
        """
        stats = {}

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Основная статистика одним запросом
                    cursor.execute("""
                        SELECT
                            COUNT(*) as total_vacancies,
                            COUNT(CASE WHEN salary_from IS NOT NULL OR salary_to IS NOT NULL THEN 1 END) as vacancies_with_salary,
                            COUNT(DISTINCT CASE WHEN company_id IS NOT NULL THEN company_id END) as unique_employers,
                            AVG(CASE
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2
                                WHEN salary_from IS NOT NULL THEN salary_from
                                WHEN salary_to IS NOT NULL THEN salary_to
                            END) as avg_salary,
                            -- Улучшенная обработка дат с проверкой на валидность
                            MAX(CASE WHEN published_at IS NOT NULL THEN published_at END) as latest_vacancy_date,
                            MIN(CASE WHEN published_at IS NOT NULL THEN published_at END) as earliest_vacancy_date,
                            COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as vacancies_last_week,
                            COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as vacancies_last_month,
                            -- Дополнительная статистика по заполненности полей
                            COUNT(CASE WHEN description IS NOT NULL AND description != '' THEN 1 END) as vacancies_with_description,
                            COUNT(CASE WHEN requirements IS NOT NULL AND requirements != '' THEN 1 END) as vacancies_with_requirements,
                            COUNT(CASE WHEN area IS NOT NULL AND area != '' THEN 1 END) as vacancies_with_area,
                            COUNT(CASE WHEN published_at IS NOT NULL THEN 1 END) as vacancies_with_published_date
                        FROM vacancies
                    """)

                    main_stats = cursor.fetchone()
                    if main_stats:
                        stats.update(dict(main_stats))

                    # Статистика по компаниям
                    cursor.execute("SELECT COUNT(*) as total_companies FROM companies")
                    company_result = cursor.fetchone()
                    if company_result:
                        stats['total_companies'] = company_result['total_companies']

                    # Топ работодателей по количеству вакансий
                    cursor.execute("""
                        SELECT c.name as employer, COUNT(*) as vacancy_count
                        FROM vacancies v
                        JOIN companies c ON v.company_id = c.id
                        WHERE c.name IS NOT NULL AND c.name != ''
                        GROUP BY c.name
                        ORDER BY vacancy_count DESC
                        LIMIT 10
                    """)
                    stats['top_employers'] = [dict(row) for row in cursor.fetchall()]

                    # Распределение зарплат по диапазонам
                    cursor.execute("""
                        SELECT
                            CASE
                                WHEN COALESCE(salary_from, salary_to, 0) < 50000 THEN 'до 50k'
                                WHEN COALESCE(salary_from, salary_to, 0) < 100000 THEN '50k-100k'
                                WHEN COALESCE(salary_from, salary_to, 0) < 150000 THEN '100k-150k'
                                WHEN COALESCE(salary_from, salary_to, 0) < 200000 THEN '150k-200k'
                                ELSE 'свыше 200k'
                            END as salary_range,
                            COUNT(*) as count
                        FROM vacancies
                        WHERE (salary_from IS NOT NULL OR salary_to IS NOT NULL)
                        AND (salary_currency IN ('RUR', 'RUB', 'руб.') OR salary_currency IS NULL)
                        GROUP BY salary_range
                        ORDER BY MIN(COALESCE(salary_from, salary_to, 0))
                    """)
                    stats['salary_distribution'] = [dict(row) for row in cursor.fetchall()]

            return stats

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении SQL-запросов для получения статистики БД: {e}")
            return {}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении статистики БД: {e}")
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
                    # Простой SQL-запрос для проверки подключения к БД
                    # SELECT 1 - минимальный запрос, не требующий доступа к таблицам
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None and result[0] == 1
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке подключения: {e}")
            return False

    def filter_companies_by_targets(self, api_companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует компании из API по целевым компаниям используя SQL-запрос

        Args:
            api_companies: Список компаний из API

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список целевых компаний
        """
        if not api_companies:
            return []

        # Создаем список названий целевых компаний для SQL-поиска
        target_company_names = [company.name.lower() for company in TARGET_COMPANIES]

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