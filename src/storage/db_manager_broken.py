"""Модуль управления базой данных PostgreSQL.

Обеспечивает интерфейс для работы с PostgreSQL базой данных,
включая выполнение запросов, управление подключениями и
специализированные методы для работы с вакансиями.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    PSYCOPG2_AVAILABLE = True
    PsycopgError = psycopg2.Error
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None  # type: ignore
    RealDictCursor = None  # type: ignore
    PsycopgError = Exception  # type: ignore
    from .simple_db_adapter import get_db_adapter

    print("psycopg2 недоступен, используется простой DB адаптер")

from src.config.db_config import DatabaseConfig
from src.config.target_companies import TargetCompanies
from src.storage.abstract_db_manager import AbstractDBManager

logger = logging.getLogger(__name__)

# Получаем список целевых компаний из единого источника
TARGET_COMPANIES = TargetCompanies.get_all_companies()


class DBManager(AbstractDBManager):
    """Менеджер базы данных PostgreSQL.

    Предоставляет методы для выполнения запросов к PostgreSQL базе данных,
    управления подключениями и специализированные операции с вакансиями.

    Attributes:
        db_config: Конфигурация подключения к базе данных
    """

    def __init__(self, db_config: Optional[DatabaseConfig] = None) -> None:
        """Инициализация менеджера базы данных.

        Args:
            db_config: Конфигурация базы данных. Если None, используется конфигурация по умолчанию.
        """
        self.db_config = db_config or DatabaseConfig()

    def _get_connection(self) -> Any:
        """Создает подключение к базе данных.

        Returns:
            Подключение к БД (psycopg2.connection или простой адаптер).

        Raises:
            Exception: При ошибке подключения к БД.
        """
        if not PSYCOPG2_AVAILABLE:
            # Возвращаем простой адаптер как "подключение"
            return get_db_adapter()  # type: ignore

        try:
            connection_params = self.db_config.get_connection_params()
            # Добавляем явное указание кодировки UTF-8
            connection_params["client_encoding"] = "utf8"
            connection = psycopg2.connect(**connection_params)  # type: ignore

            # Устанавливаем кодировку для соединения
            connection.set_client_encoding("UTF8")
            return connection
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def _ensure_database_exists(self) -> bool:
        """Создает базу данных если она не существует.

        Подключается к системной БД postgres для создания новой БД.
        """
        if not PSYCOPG2_AVAILABLE:
            logger.warning("psycopg2 недоступен, пропускаем создание базы данных")
            return True

        # Получаем параметры подключения
        connection_params = self.db_config.get_connection_params()
        database_name = connection_params["database"]

        # Создаем параметры для подключения к системной БД postgres
        system_params = connection_params.copy()
        system_params["database"] = "postgres"

        # Подключаемся к системной БД postgres для создания новой БД
        try:
            connection = psycopg2.connect(**system_params)  # type: ignore
            connection.autocommit = True
        except PsycopgError as e:
            error_message = str(e)
            if "database" in error_message and "already exists" in error_message:
                logger.info(f"База данных {database_name} уже существует")
                return True
            logger.error(f"Не удается подключиться к системной БД postgres: {e}")
            logger.info("Пытаемся подключиться к целевой БД напрямую...")
            try:
                # Если не можем подключиться к postgres, пробуем сразу к целевой БД
                test_connection = self._get_connection()
                test_connection.close()
                logger.info(f"✓ База данных {database_name} уже доступна")
                return True
            except PsycopgError:
                logger.error(f"База данных {database_name} недоступна и не может быть создана")
                return False

        try:
            cursor = connection.cursor()

            # Проверяем существование базы данных
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            db_exists = cursor.fetchone() is not None

            if db_exists:
                logger.info(f"✓ База данных {database_name} уже существует")
            else:
                # Создаем новую базу данных только если её нет
                logger.info(f"Создаём базу данных {database_name}...")
                cursor.execute(f'CREATE DATABASE "{database_name}"')
                logger.info(f"✓ База данных {database_name} успешно создана")

        except PsycopgError as e:
            logger.error(f"Ошибка при создании базы данных {database_name}: {e}")
            # Пытаемся подключиться к целевой БД - возможно она уже существует
            try:
                test_connection = self._get_connection()
                test_connection.close()
                logger.info(f"✓ База данных {database_name} доступна (возможно уже существовала)")
            except PsycopgError:
                raise e
        finally:
            if "cursor" in locals() and cursor is not None:
                cursor.close()
            if "connection" in locals() and connection is not None:
                connection.close()

        return True

    def initialize_database(self) -> bool:
        """Единая инициализация БД: создание таблиц и заполнение компаний.
        
        Использует единое соединение с контекстным менеджером для всех операций.
        """
        # Сначала убеждаемся, что база данных существует
        try:
            if not self._ensure_database_exists():
                logger.error("Не удалось создать или подключиться к базе данных")
                return False
        except Exception as db_error:
            logger.error(f"Ошибка при создании базы данных: {db_error}")
            return False
            
        # Единое соединение с контекстным менеджером для всех операций
        try:
            with self._get_connection() as conn:
                # Включаем автокоммит для DDL операций
                conn.autocommit = True
                with conn.cursor() as cursor:
                    print("🔧 Создание структуры базы данных...")
                    # Устанавливаем кодировку сессии
                    cursor.execute("SET client_encoding TO 'UTF8'")

                    # СОЗДАНИЕ ТАБЛИЦ
                    # Создаем таблицу компаний
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
                    print("✅ Таблица companies создана")
                    
                    # Создаем таблицу вакансий
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
                    print("✅ Таблица vacancies создана")
                    
                    # ЗАПОЛНЕНИЕ КОМПАНИЙ
                    print("📊 Заполнение таблицы компаний...")
                    self._fill_companies_table(cursor)
                    
                    print("✅ Инициализация БД завершена")
                    logger.info("✓ База данных инициализирована успешно")
                    
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            logger.error(f"Ошибка при инициализации БД: {e}")
            return False
        return True
        
    def _fill_companies_table(self, cursor) -> None:
        """Заполняет таблицу компаний используя переданный cursor."""
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"ℹ️ Таблица companies уже содержит {count} записей")
            return
            
        # Загружаем целевые компании
        from src.config.target_companies import TARGET_COMPANIES
        
        added = 0
        for company_name, company_data in TARGET_COMPANIES.items():
            try:
                cursor.execute(
                    """
                    INSERT INTO companies (name, hh_id, sj_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (company_name, company_data.get("hh_id"), company_data.get("sj_id"))
                )
                added += 1
            except Exception as e:
                logger.warning(f"Не удалось добавить компанию {company_name}: {e}")
        
        print(f"✅ Добавлено {added} компаний")

    # Оставляем старые методы для обратной совместимости    
    def create_tables(self) -> bool:
        """[УСТАРЕЛО] Используйте initialize_database()."""
        logger.warning("Метод create_tables() устарел. Используйте initialize_database()")
        return self.initialize_database()

    def populate_companies_table(self) -> bool:
        """[УСТАРЕЛО] Используйте initialize_database()."""
        logger.warning("Метод populate_companies_table() устарел. Теперь выполняется в initialize_database()")
        return True  # Метод больше не нужен, все делается в initialize_database()

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
                        RETURNS TEXT AS $$
                        DECLARE
                            result_text TEXT := '';
                            rec RECORD;
                            seq_name TEXT;
                            table_count INT;
                        BEGIN
                            -- Проверяем все таблицы с SERIAL полями
                            FOR rec IN
                                SELECT schemaname, tablename, attname,
                                       pg_get_serial_sequence(schemaname||'.'||tablename, attname) as sequence_name
                                FROM pg_attribute
                                JOIN pg_class ON pg_attribute.attrelid = pg_class.oid
                                JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
                                WHERE atttypid = 'serial'::regtype::oid
                                AND schemaname = 'public'
                                AND tablename IN ('companies', 'vacancies')
                            LOOP
                                IF rec.sequence_name IS NOT NULL THEN
                                    seq_name := rec.sequence_name;

                                    -- Получаем количество записей в таблице
                                    EXECUTE format('SELECT COUNT(*) FROM %I.%I', rec.schemaname, rec.tablename)
                                        INTO table_count;

                                    IF table_count = 0 THEN
                                        -- Таблица пустая - сбрасываем счетчик на 1
                                        EXECUTE format('ALTER SEQUENCE %s RESTART WITH 1', seq_name);
                                        result_text := result_text ||
                                            format('Таблица %s пустая: счетчик %s сброшен на 1',
                                                   rec.tablename, seq_name) || E'\n';
                                    ELSE
                                        -- Таблица не пустая - корректируем счетчик по максимальному ID
                                        EXECUTE format('SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %I.%I), 1), true)',
                                            seq_name, rec.attname, rec.schemaname, rec.tablename);
                                        result_text := result_text ||
                                            format('Таблица %s (%d записей): счетчик %s скорректирован',
                                                   rec.tablename, table_count, seq_name) || E'\n';
                                    END IF;
                                END IF;
                            END LOOP;

                            RETURN result_text;
                        END;
                        $$ LANGUAGE plpgsql;
                    """)

                    # Автоматически сбрасываем счетчики для пустых таблиц и корректируем для заполненных
                    try:
                        cursor.execute("SELECT reset_empty_table_sequences();")
                        reset_result = cursor.fetchone()
                        if reset_result and reset_result[0]:
                            logger.info("✓ Счетчики автоинкремента настроены:")
                            for line in reset_result[0].strip().split("\n"):
                                if line.strip():
                                    logger.info(f"  {line.strip()}")
                    except Exception as e:
                        logger.warning(f"Не удалось настроить счетчики автоинкремента: {e}")
                        # Fallback - сбрасываем вручную для пустых таблиц
                        try:
                            cursor.execute("SELECT COUNT(*) FROM vacancies")
                            if cursor.fetchone()[0] == 0:
                                cursor.execute("ALTER SEQUENCE vacancies_id_seq RESTART WITH 1;")
                                logger.info("✓ Последовательность vacancies_id_seq сброшена на 1 (fallback)")
                        except Exception:
                            pass

                    logger.info("✓ Все таблицы и структуры успешно созданы/проверены")
                    print("💾 Изменения автоматически сохранены (autocommit)")
                    
                    # Проверяем что таблицы действительно созданы
                    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('companies', 'vacancies')")
                    table_count = cursor.fetchone()[0]
                    print(f"✅ Проверка: найдено {table_count} таблиц из 2")
                    
            finally:
                if cursor:
                    cursor.close()
                conn.close()

        except Exception as e:
            print(f"❌ ОШИБКА создания таблиц: {e}")
            logger.error(f"Ошибка при создании таблиц: {e}")
            return False
        return True

    def populate_companies_table(self) -> bool:
        """Заполняет таблицу companies целевыми компаниями.

        Добавляет в таблицу все целевые компании из конфигурации
        с их HH и SuperJob идентификаторами.
        """
        try:
            # Ждем немного чтобы изменения точно зафиксировались
            import time
            time.sleep(0.1)
            
            # Используем контекстный менеджер для безопасной работы с подключением
            with self._get_connection() as connection:
                cursor = connection.cursor()
                # Устанавливаем кодировку сессии
                cursor.execute("SET client_encoding TO 'UTF8'")

                # Проверяем, существует ли таблица companies
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'companies'
                    );
                """
                )

                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    logger.warning("Таблица companies не существует. Таблицы должны быть созданы заранее.")
                    return False

            # Проверяем, есть ли уже данные в таблице
            cursor.execute("SELECT COUNT(*) FROM companies")
            companies_count = cursor.fetchone()[0]

            if companies_count > 0:
                logger.info(f"✓ Таблица companies уже содержит {companies_count} компаний")
                # Для отладки: показываем, какие компании есть в БД
                cursor.execute("SELECT name, hh_id, sj_id FROM companies ORDER BY name LIMIT 5")
                existing_companies = cursor.fetchall()
                logger.info(f"DEBUG: Первые 5 компаний в БД: {existing_companies}")
                return True

            # Добавляем целевые компании с их API идентификаторами
            for company in TARGET_COMPANIES:
                # Сначала проверяем, существует ли компания
                cursor.execute("SELECT id FROM companies WHERE name = %s", (company.name,))
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        INSERT INTO companies (name, hh_id, sj_id)
                        VALUES (%s, %s, %s)
                    """,
                        (company.name, getattr(company, "hh_id", None), getattr(company, "sj_id", None)),
                    )
                    logger.info(f"Добавлена целевая компания: {company.name}")

            # Проверяем результат
            cursor.execute("SELECT COUNT(*) FROM companies")
            final_count = cursor.fetchone()[0]
            logger.info(f"✓ Добавлено компаний в таблицу companies: {final_count}")

        except Exception as e:
            logger.error(f"Ошибка при заполнении таблицы companies: {e}")
            return False
        return True

    def get_target_companies_analysis(self) -> List[Tuple[str, int]]:
        """Получает анализ ТОЛЬКО по целевым компаниям.

        Этот метод специально предназначен для демонстрации п.10.

        Returns:
            Список кортежей (название_целевой_компании, количество_вакансий).
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
        """Получает список всех компаний и количество вакансий у каждой компании.

        ВАЖНО: Метод фильтрует результаты по целевым компаниям из конфигурации.

        Returns:
            Список кортежей (название_компании, количество_вакансий).
        """
        # Проверяем подключение к БД
        if not self.check_connection():
            logger.warning("Нет подключения к базе данных")
            return [(company.name, 0) for company in TARGET_COMPANIES]

        try:
            # Дополнительная проверка подключения перед выполнением запроса
            if not self.check_connection():
                logger.warning("Подключение к БД недоступно при выполнении get_companies_and_vacancies_count")
                return [(company.name, 0) for company in TARGET_COMPANIES]

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Сначала проверяем, существуют ли необходимые таблицы
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'companies'
                        );
                    """)
                    companies_table_exists = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'vacancies'
                        );
                    """)
                    vacancies_table_exists = cursor.fetchone()[0]
                    
                    # Если таблицы не существуют, возвращаем компании с нулевым количеством вакансий
                    if not companies_table_exists or not vacancies_table_exists:
                        logger.info("Таблицы companies или vacancies еще не созданы, возвращаем пустой результат")
                        return [(company.name, 0) for company in TARGET_COMPANIES]

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

                    return [(str(row[0]), int(row[1])) for row in results]

        except Exception as e:
            # Проверяем, является ли это ошибкой отсутствия таблицы
            error_message = str(e).lower()
            if any(keyword in error_message for keyword in ["does not exist", "relation", "не существует"]):
                logger.info("Таблицы базы данных еще не созданы, возвращаем компании с нулевым количеством")
            else:
                logger.error(f"Ошибка при получении списка компаний и количества вакансий: {e}")
            # В случае ошибки возвращаем все целевые компании с нулями
            return [(company.name, 0) for company in TARGET_COMPANIES]

    def _is_target_company_match(self, target_name: str, db_name: str) -> bool:
        """Проверяет, соответствует ли название компании из БД целевой компании.

        Args:
            target_name: Название целевой компании.
            db_name: Название компании из БД.

        Returns:
            True если названия соответствуют.
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
            "Delivery Club": ["delivery club"],
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
                        if row.get("raw_company_id") is not None and row.get("linked_company_id") is None:
                            unlinked_count += 1
                        elif row.get("linked_company_id") is not None:
                            linked_count += 1

                    if unlinked_count > 0:
                        logger.warning(
                            f"Найдено {unlinked_count} вакансий с company_id, но без связи с таблицей companies"
                        )
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

        except Exception as e:
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
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (avg_salary,))
                    results = cursor.fetchall()

                    logger.debug(f"Найдено {len(results)} вакансий с зарплатой выше средней")
                    return [dict(row) for row in results]

        except Exception as e:
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
        WHERE (LOWER(v.title) LIKE LOWER(%s) OR LOWER(v.search_query) LIKE LOWER(%s))
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
                    cursor.execute(query, (search_pattern, search_pattern))
                    results = cursor.fetchall()

                    # Преобразуем результаты в список словарей
                    columns = ["title", "company_name", "salary_info", "url", "description", "vacancy_id"]
                    vacancies = []

                    for row in results:
                        vacancy_dict = {}
                        for i, column in enumerate(columns):
                            vacancy_dict[column] = row[i] if i < len(row) else None
                        vacancies.append(vacancy_dict)

                    logger.debug(f"Поиск по '{keyword}': найдено {len(vacancies)} вакансий")
                    return vacancies

        except Exception as e:
            logger.error(f"Ошибка при выполнении SQL-запроса для поиска вакансий по ключевому слову '{keyword}': {e}")
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
                    cursor.execute(
                        """
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
                    """
                    )

                    main_stats = cursor.fetchone()
                    if main_stats:
                        stats.update(dict(main_stats))

                    # Статистика по компаниям
                    cursor.execute("SELECT COUNT(*) as total_companies FROM companies")
                    company_result = cursor.fetchone()
                    if company_result:
                        stats["total_companies"] = company_result["total_companies"]

                    # Топ работодателей по количеству вакансий
                    cursor.execute(
                        """
                        SELECT c.name as employer, COUNT(*) as vacancy_count
                        FROM vacancies v
                        JOIN companies c ON v.company_id = c.id
                        WHERE c.name IS NOT NULL AND c.name != ''
                        GROUP BY c.name
                        ORDER BY vacancy_count DESC
                        LIMIT 10
                    """
                    )
                    stats["top_employers"] = [dict(row) for row in cursor.fetchall()]

                    # Распределение зарплат по диапазонам
                    cursor.execute(
                        """
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
                    """
                    )
                    stats["salary_distribution"] = [dict(row) for row in cursor.fetchall()]

            return stats

        except Exception as e:
            logger.error(f"Ошибка при выполнении SQL-запросов для получения статистики БД: {e}")
            return {}

    def get_connection(self) -> Any:
        """
        Публичный метод для получения подключения к базе данных

        Returns:
            psycopg2.extensions.connection: Подключение к БД

        Raises:
            Exception: При ошибке подключения к БД
        """
        return self._get_connection()

    def check_connection(self) -> bool:
        """
        Проверяет подключение к базе данных используя простой SQL-запрос

        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            if not PSYCOPG2_AVAILABLE:
                # Используем простой адаптер
                adapter = get_db_adapter()
                return adapter.test_connection()

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Простой SQL-запрос для проверки подключения к БД
                    # SELECT 1 - минимальный запрос, не требующий доступа к таблицам
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке подключения: {e}")
            return False

    def filter_companies_by_targets(self, api_companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует компании из API СТРОГО по ID целевых компаний

        Args:
            api_companies: Список компаний из API

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список целевых компаний
        """
        if not api_companies:
            return []

        # Собираем только hh_id и sj_id из целевых компаний
        # ЗАГЛУШКА: Фильтрация компаний теперь выполняется в PostgresSaver.filter_and_deduplicate_vacancies
        logger.info("Фильтрация компаний должна выполняться через PostgresSaver.filter_and_deduplicate_vacancies")
        return api_companies  # Возвращаем без фильтрации

    def analyze_api_data_with_sql(
        self, api_data: List[Dict[str, Any]], analysis_type: str = "vacancy_stats"
    ) -> Dict[str, Any]:
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
                    cursor.execute(
                        """
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
                    """
                    )

                    # Подготавливаем данные для анализа
                    analysis_data = []
                    for item in api_data:
                        salary = item.get("salary", {}) or {}
                        analysis_data.append(
                            (
                                str(item.get("id", "")),
                                item.get("name", ""),
                                salary.get("from"),
                                salary.get("to"),
                                salary.get("currency"),
                                str(item.get("employer", {}).get("name", "") if item.get("employer") else ""),
                                str(item.get("area", {}).get("name", "") if item.get("area") else ""),
                                (
                                    item.get("experience", {}).get("name", "")
                                    if isinstance(item.get("experience"), dict)
                                    else str(item.get("experience", ""))
                                ),
                                (
                                    item.get("employment", {}).get("name", "")
                                    if isinstance(item.get("employment"), dict)
                                    else str(item.get("employment", ""))
                                ),
                            )
                        )

                    from psycopg2.extras import execute_values

                    execute_values(
                        cursor,
                        """INSERT INTO temp_api_analysis (
                            item_id, title, salary_from, salary_to, salary_currency,
                            employer, area, experience, employment
                        ) VALUES %s""",
                        analysis_data,
                        template=None,
                        page_size=1000,
                    )

                    results = {}

                    if analysis_type == "vacancy_stats":
                        # Статистика по вакансиям
                        cursor.execute(
                            """
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
                        """
                        )

                        stats = cursor.fetchone()
                        results.update(dict(stats))

                        # Топ работодателей
                        cursor.execute(
                            """
                            SELECT employer, COUNT(*) as vacancy_count
                            FROM temp_api_analysis
                            WHERE employer IS NOT NULL AND employer != ''
                            GROUP BY employer
                            ORDER BY vacancy_count DESC
                            LIMIT 10
                        """
                        )
                        results["top_employers"] = [dict(row) for row in cursor.fetchall()]

                    elif analysis_type == "salary_analysis":
                        # Анализ зарплат
                        cursor.execute(
                            """
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
                        """
                        )

                        results.update(dict(cursor.fetchone()))

                    return results

        except Exception as e:
            logger.error(f"Ошибка SQL-анализа данных API: {e}")
            return {}
