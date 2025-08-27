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

    # Mapping for std company names, based on the intention of the provided snippet.
    COMPANY_NAME_STANDARDIZATION = {
        'яндекс': 'Яндекс',
        'сбер': 'Сбер',
        'сбербанк': 'Сбер',
        'тинькофф': 'Тинькофф',
        'т-банк': 'Тинькофф',
        'tinkoff': 'Тинькофф',
        'vk': 'VK',
        'вконтакте': 'VK',
        'вк': 'VK',
        'ozon': 'Ozon',
        'озон': 'Ozon',
        'wildberries': 'Wildberries',
        'wb': 'Wildberries',
        'альфа-банк': 'Альфа-Банк',
        'alfa-bank': 'Альфа-Банк'
    }

    def _standardize_employer_name(self, employer_name: Optional[str]) -> Optional[str]:
        """
        Standardizes employer name using a predefined mapping.
        This is an interpretation of the provided snippet's intention to improve company handling.
        """
        if not employer_name:
            return None

        lower_name = employer_name.lower()
        for pattern, standardized_name in self.COMPANY_NAME_STANDARDIZATION.items():
            if pattern in lower_name:
                return standardized_name
        return employer_name # Return original if no pattern matches

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
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=db_name,
                user=self.username,
                password=self.password,
                client_encoding='utf8'
            )
            # Устанавливаем кодировку для соединения
            connection.set_client_encoding('UTF8')
            return connection
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

            # Устанавливаем кодировку сессии
            cursor.execute("SET client_encoding TO 'UTF8'")

            # Сначала создаем таблицу companies если её нет
            self._ensure_companies_table_exists()

            # Проверяем, есть ли внешний ключ, который может вызывать проблемы
            cursor.execute("""
                SELECT constraint_name FROM information_schema.table_constraints
                WHERE table_name = 'vacancies' 
                AND constraint_type = 'FOREIGN KEY'
                AND constraint_name = 'vacancies_company_id_fkey'
            """)
            
            if cursor.fetchone():
                logger.info("Удаляем проблемный внешний ключ...")
                try:
                    cursor.execute("ALTER TABLE vacancies DROP CONSTRAINT IF EXISTS vacancies_company_id_fkey")
                    logger.info("✓ Внешний ключ vacancies_company_id_fkey удален")
                except psycopg2.Error as e:
                    logger.warning(f"Не удалось удалить внешний ключ: {e}")

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER -- Ссылка на компанию (используем внутренний id из companies)
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

            # Проверяем существование поля company_id и его тип
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'vacancies' AND column_name = 'company_id';
            """)

            company_id_info = cursor.fetchone()
            if not company_id_info:
                logger.info("Добавляем поле company_id в существующую таблицу...")
                cursor.execute("ALTER TABLE vacancies ADD COLUMN company_id INTEGER;")
                logger.info("✓ Поле company_id добавлено")
            elif company_id_info[1] != 'integer':
                logger.warning(f"Поле company_id имеет тип {company_id_info[1]}, но должен быть INTEGER.")
                logger.info("Пересоздаем поле company_id с правильным типом...")
                try:
                    # Удаляем старое поле и создаем новое
                    cursor.execute("ALTER TABLE vacancies DROP COLUMN IF EXISTS company_id CASCADE")
                    cursor.execute("ALTER TABLE vacancies ADD COLUMN company_id INTEGER")
                    logger.info("✓ Поле company_id пересоздано с типом INTEGER")
                except psycopg2.Error as e:
                    logger.error(f"Не удалось пересоздать поле company_id: {e}")

            # Создаем индексы
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacancy_id ON vacancies(vacancy_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON vacancies(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_salary ON vacancies(salary_from, salary_to);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON vacancies(source);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_id ON vacancies(company_id);")

            # Теперь можем создать правильный внешний ключ (опционально, так как это может вызывать проблемы)
            # cursor.execute("""
            #     ALTER TABLE vacancies 
            #     ADD CONSTRAINT fk_vacancies_company_id 
            #     FOREIGN KEY (company_id) REFERENCES companies(id)
            #     ON DELETE SET NULL
            # """)

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
                    published_at TIMESTAMP,
                    company_id INTEGER
                ) ON COMMIT DROP
            """)

            # Получаем соответствие employer -> company_id из таблицы companies
            company_mapping = {}
            try:
                # Ensure companies table exists before querying
                self._ensure_companies_table_exists()

                cursor.execute("SELECT id, hh_id, sj_id, company_id, name, source FROM companies")
                companies = cursor.fetchall()

                for company in companies:
                    id, hh_id, sj_id, company_id, name, source = company

                    # Добавляем маппинг по внешним ID
                    if hh_id:
                        company_mapping[str(hh_id)] = id
                    if sj_id:
                        company_mapping[str(sj_id)] = id

                    # Добавляем маппинг по названию
                    company_mapping[name.lower()] = id

            except Exception as e:
                logger.error(f"Ошибка при получении соответствия компаний: {e}")

            # Подготавливаем данные для вставки/обновления И сохраняем company_id в объектах
            insert_data = []
            vacancy_company_mapping = {}  # Словарь для сохранения соответствия vacancy_id -> company_id

            for vacancy in vacancies:
                # Определяем company_id на основе employer
                mapped_company_id = None
                employer_name = None
                employer_id = None

                if vacancy.employer:
                    # Правильно извлекаем имя работодателя и ID
                    if isinstance(vacancy.employer, dict):
                        employer_name = vacancy.employer.get('name')
                        employer_id = vacancy.employer.get('id')
                    elif isinstance(vacancy.employer, str):
                        employer_name = vacancy.employer
                    else:
                        employer_name = str(vacancy.employer)

                # Также проверяем специфичные поля для SJ
                if hasattr(vacancy, 'source') and vacancy.source == 'superjob.ru':
                    # Для SuperJob проверяем firm_id или client_id в исходных данных
                    if hasattr(vacancy, '_raw_data') and vacancy._raw_data:
                        sj_firm_id = vacancy._raw_data.get('firm_id') or vacancy._raw_data.get('client_id')
                        if sj_firm_id:
                            mapped_company_id = company_mapping.get(str(sj_firm_id))

                # Если ID не найден по внешнему ID, ищем по имени
                if not mapped_company_id and employer_name and employer_name.strip():
                    employer_lower = employer_name.lower().strip()

                    # 1. Поиск по внешнему ID (для HH)
                    if employer_id and not mapped_company_id:
                        mapped_company_id = company_mapping.get(str(employer_id))

                    # 2. Прямое соответствие по названию
                    if not mapped_company_id:
                        mapped_company_id = company_mapping.get(employer_lower)

                    # 3. Поиск частичного соответствия (улучшенный)
                    if not mapped_company_id:
                        # Сначала ищем точные вхождения
                        for alt_name, comp_id in company_mapping.items():
                            if isinstance(alt_name, str) and alt_name == employer_lower:
                                mapped_company_id = comp_id
                                break

                    # 4. Поиск частичного соответствия
                    if not mapped_company_id:
                        for alt_name, comp_id in company_mapping.items():
                            if isinstance(alt_name, str) and len(alt_name) > 2 and (alt_name in employer_lower or employer_lower in alt_name):
                                mapped_company_id = comp_id
                                break

                    # 5. Логирование для отладки
                    if not mapped_company_id and employer_name:
                        source_info = f" (source: {getattr(vacancy, 'source', 'unknown')})"
                        logger.debug(f"Company_id не найден для работодателя: '{employer_name}'{source_info} (vacancy_id: {vacancy.vacancy_id})")

                # Сохраняем соответствие для дальнейшего использования
                vacancy_company_mapping[vacancy.vacancy_id] = mapped_company_id

                # Устанавливаем company_id напрямую в объект вакансии
                vacancy.company_id = mapped_company_id

                salary_from = vacancy.salary.salary_from if vacancy.salary else None
                salary_to = vacancy.salary.salary_to if vacancy.salary else None
                salary_currency = vacancy.salary.currency if vacancy.salary else None

                # Standardize employer name before storing
                raw_employer_name = None
                if isinstance(vacancy.employer, dict):
                    raw_employer_name = vacancy.employer.get('name')
                elif vacancy.employer:
                    raw_employer_name = str(vacancy.employer)

                employer_str = self._standardize_employer_name(raw_employer_name)

                area_str = (
                    vacancy.area.get('name') if isinstance(vacancy.area, dict)
                    else str(vacancy.area) if vacancy.area else None
                )

                # Обработка даты published_at
                published_date = None
                if vacancy.published_at:
                    if isinstance(vacancy.published_at, str):
                        try:
                            # Пытаемся парсить ISO формат даты
                            from datetime import datetime
                            if 'T' in vacancy.published_at:
                                # Формат: 2025-08-25T18:47:30+0300
                                if '+' in vacancy.published_at:
                                    # Заменяем +0300 на +03:00 для совместимости с Python
                                    date_str = vacancy.published_at
                                    if date_str.endswith('+0300'):
                                        date_str = date_str.replace('+0300', '+03:00')
                                    elif date_str.endswith('+0000'):
                                        date_str = date_str.replace('+0000', '+00:00')
                                    published_date = datetime.fromisoformat(date_str)
                                else:
                                    published_date = datetime.fromisoformat(vacancy.published_at)
                            else:
                                published_date = datetime.fromisoformat(vacancy.published_at)
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Не удалось распарсить дату {vacancy.published_at}: {e}")
                            # Пытаемся использовать текущую дату как fallback
                            from datetime import datetime
                            published_date = datetime.now()
                    elif hasattr(vacancy.published_at, 'isoformat'):
                        # Это уже datetime объект
                        published_date = vacancy.published_at
                    else:
                        # Пытаемся преобразовать в datetime
                        try:
                            from datetime import datetime
                            published_date = datetime.fromisoformat(str(vacancy.published_at))
                        except:
                            published_date = datetime.now()

                # Валидация описания
                final_description = vacancy.description
                if not final_description or not final_description.strip():
                    # Если описание пустое, формируем его из доступных данных
                    desc_parts = []
                    if vacancy.requirements:
                        desc_parts.append(f"Требования: {vacancy.requirements}")
                    if vacancy.responsibilities:
                        desc_parts.append(f"Обязанности: {vacancy.responsibilities}")
                    if desc_parts:
                        final_description = " ".join(desc_parts)
                    else:
                        final_description = f"Вакансия: {vacancy.title}"

                    logger.debug(f"Сформировано описание для вакансии {vacancy.vacancy_id}: {final_description[:100]}...")

                insert_data.append((
                    vacancy.vacancy_id, vacancy.title, vacancy.url,
                    salary_from, salary_to, salary_currency,
                    final_description, vacancy.requirements, vacancy.responsibilities,
                    vacancy.experience, vacancy.employment, vacancy.schedule,
                    employer_str, area_str, vacancy.source, published_date,
                    mapped_company_id  # Оставляем как integer
                ))

            # Bulk insert во временную таблицу
            from psycopg2.extras import execute_values
            execute_values(
                cursor,
                """INSERT INTO temp_new_vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at, company_id
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
                    employment, schedule, employer, area, source, published_at, company_id
                )
                SELECT t.vacancy_id, t.title, t.url, t.salary_from, t.salary_to, t.salary_currency,
                       t.description, t.requirements, t.responsibilities, t.experience,
                       t.employment, t.schedule, t.employer, t.area, t.source, t.published_at, t.company_id
                FROM temp_new_vacancies t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
                WHERE v.vacancy_id IS NULL
            """)

            new_count = cursor.rowcount

            # Находим и обновляем существующие вакансии с изменениями
            cursor.execute("""
                UPDATE vacancies v SET
                    title = t.title,
                    url = t.url,
                    description = t.description,
                    experience = t.experience,
                    employment = t.employment,
                    schedule = t.schedule,
                    employer = t.employer,
                    area = t.area,
                    source = t.source,
                    published_at = t.published_at,
                    company_id = t.company_id,
                    updated_at = CURRENT_TIMESTAMP
                FROM temp_new_vacancies t
                WHERE v.vacancy_id = t.vacancy_id
                AND (
                    v.title != t.title OR
                    v.url != t.url OR
                    v.description != t.description OR
                    COALESCE(v.salary_from, 0) != COALESCE(t.salary_from, 0) OR
                    COALESCE(v.salary_to, 0) != COALESCE(t.salary_to, 0) OR
                    COALESCE(v.salary_currency, '') != COALESCE(t.salary_currency, '') OR
                    COALESCE(v.company_id::text, '') IS DISTINCT FROM COALESCE(t.company_id::text, '') -- Приведение к text для сравнения
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

            # Получаем соответствие employer -> company_id из таблицы companies
            company_mapping = {}
            try:
                # Ensure companies table exists before querying
                self._ensure_companies_table_exists()

                cursor.execute("SELECT id, hh_id, sj_id, company_id, name, source FROM companies")
                companies = cursor.fetchall()

                for company in companies:
                    id, hh_id, sj_id, company_id, name, source = company

                    # Добавляем маппинг по внешним ID
                    if hh_id:
                        company_mapping[str(hh_id)] = id
                    if sj_id:
                        company_mapping[str(sj_id)] = id

                    # Добавляем маппинг по названию
                    company_mapping[name.lower()] = id

            except Exception as e:
                logger.error(f"Ошибка при получении соответствия компаний: {e}")


            # Batch проверка существования вакансий
            vacancy_ids = [v.vacancy_id for v in vacancies]
            placeholders = ','.join(['%s'] * len(vacancy_ids))

            cursor.execute(
                f"SELECT vacancy_id, title, url, description, salary_from, salary_to, salary_currency, company_id FROM vacancies WHERE vacancy_id IN ({placeholders})",
                vacancy_ids
            )

            existing_map = {row['vacancy_id']: row for row in cursor.fetchall()}

            # Разделяем на новые и обновляемые вакансии
            new_vacancies = []
            update_vacancies = []

            for vacancy in vacancies:
                if vacancy.vacancy_id in existing_map:
                    existing = existing_map[vacancy.vacancy_id]

                    # Проверяем изменения
                    salary_from = vacancy.salary.salary_from if vacancy.salary else None
                    salary_to = vacancy.salary.salary_to if vacancy.salary else None
                    salary_currency = vacancy.salary.currency if vacancy.salary else None

                    # Определяем company_id на основе employer
                    mapped_company_id = None
                    employer_name = None
                    employer_id = None

                    if vacancy.employer:
                        # Правильно извлекаем имя работодателя и ID
                        if isinstance(vacancy.employer, dict):
                            employer_name = vacancy.employer.get('name')
                            employer_id = vacancy.employer.get('id')
                        elif isinstance(vacancy.employer, str):
                            employer_name = vacancy.employer
                        else:
                            employer_name = str(vacancy.employer)

                    # Также проверяем специфичные поля для SJ
                    if hasattr(vacancy, 'source') and vacancy.source == 'superjob.ru':
                        # Для SuperJob проверяем firm_id или client_id в исходных данных
                        if hasattr(vacancy, '_raw_data') and vacancy._raw_data:
                            sj_firm_id = vacancy._raw_data.get('firm_id') or vacancy._raw_data.get('client_id')
                            if sj_firm_id:
                                mapped_company_id = company_mapping.get(str(sj_firm_id))

                    # Если ID не найден по внешнему ID, ищем по имени
                    if not mapped_company_id and employer_name and employer_name.strip():
                        employer_lower = employer_name.lower().strip()

                        # 1. Поиск по внешнему ID (для HH)
                        if employer_id and not mapped_company_id:
                            mapped_company_id = company_mapping.get(str(employer_id))

                        # 2. Прямое соответствие по названию
                        if not mapped_company_id:
                            mapped_company_id = company_mapping.get(employer_lower)

                        # 3. Поиск частичного соответствия (улучшенный)
                        if not mapped_company_id:
                            # Сначала ищем точные вхождения
                            for alt_name, comp_id in company_mapping.items():
                                if isinstance(alt_name, str) and alt_name == employer_lower:
                                    mapped_company_id = comp_id
                                    break

                        # 4. Поиск частичного соответствия
                        if not mapped_company_id:
                            for alt_name, comp_id in company_mapping.items():
                                if isinstance(alt_name, str) and len(alt_name) > 2 and (alt_name in employer_lower or employer_lower in alt_name):
                                    mapped_company_id = comp_id
                                    break

                        # 5. Логирование для отладки
                        if not mapped_company_id and employer_name:
                            source_info = f" (source: {getattr(vacancy, 'source', 'unknown')})"
                            logger.debug(f"Company_id не найден для работодателя: '{employer_name}'{source_info} (vacancy_id: {vacancy.vacancy_id})")

                    has_changes = (
                        existing['title'] != vacancy.title or
                        existing['url'] != vacancy.url or
                        existing['description'] != vacancy.description or
                        existing['salary_from'] != salary_from or
                        existing['salary_to'] != salary_to or
                        existing['salary_currency'] != salary_currency or
                        existing['company_id'] != mapped_company_id # Сравнение company_id
                    )

                    if has_changes:
                        update_vacancies.append(vacancy)
                        update_messages.append(f"Вакансия ID {vacancy.vacancy_id} обновлена: '{vacancy.title}'")
                else:
                    new_vacancies.append(vacancy)
                    update_messages.append(f"Добавлена новая вакансия ID {vacancy.vacancy_id}: '{vacancy.title}'")

            # Batch insert новых вакансий
            if new_vacancies:
                insert_data = []
                for vacancy in new_vacancies:
                    salary_from = vacancy.salary.salary_from if vacancy.salary else None
                    salary_to = vacancy.salary.salary_to if vacancy.salary else None
                    salary_currency = vacancy.salary.currency if vacancy.salary else None

                    # Определяем company_id на основе employer
                    mapped_company_id = None
                    employer_name = None
                    employer_id = None

                    if vacancy.employer:
                        # Правильно извлекаем имя работодателя и ID
                        if isinstance(vacancy.employer, dict):
                            employer_name = vacancy.employer.get('name')
                            employer_id = vacancy.employer.get('id')
                        elif isinstance(vacancy.employer, str):
                            employer_name = vacancy.employer
                        else:
                            employer_name = str(vacancy.employer)

                    # Также проверяем специфичные поля для SJ
                    if hasattr(vacancy, 'source') and vacancy.source == 'superjob.ru':
                        # Для SuperJob проверяем firm_id или client_id в исходных данных
                        if hasattr(vacancy, '_raw_data') and vacancy._raw_data:
                            sj_firm_id = vacancy._raw_data.get('firm_id') or vacancy._raw_data.get('client_id')
                            if sj_firm_id:
                                mapped_company_id = company_mapping.get(str(sj_firm_id))

                    # Если ID не найден по внешнему ID, ищем по имени
                    if not mapped_company_id and employer_name and employer_name.strip():
                        employer_lower = employer_name.lower().strip()

                        # 1. Поиск по внешнему ID (для HH)
                        if employer_id and not mapped_company_id:
                            mapped_company_id = company_mapping.get(str(employer_id))

                        # 2. Прямое соответствие по названию
                        if not mapped_company_id:
                            mapped_company_id = company_mapping.get(employer_lower)

                        # 3. Поиск частичного соответствия (улучшенный)
                        if not mapped_company_id:
                            # Сначала ищем точные вхождения
                            for alt_name, comp_id in company_mapping.items():
                                if isinstance(alt_name, str) and alt_name == employer_lower:
                                    mapped_company_id = comp_id
                                    break

                        # 4. Поиск частичного соответствия
                        if not mapped_company_id:
                            for alt_name, comp_id in company_mapping.items():
                                if isinstance(alt_name, str) and len(alt_name) > 2 and (alt_name in employer_lower or employer_lower in alt_name):
                                    mapped_company_id = comp_id
                                    break

                        # 5. Логирование для отладки
                        if not mapped_company_id and employer_name:
                            source_info = f" (source: {getattr(vacancy, 'source', 'unknown')})"
                            logger.debug(f"Company_id не найден для работодателя: '{employer_name}'{source_info} (vacancy_id: {vacancy.vacancy_id})")


                    # Standardize employer name before storing
                    raw_employer_name = None
                    if isinstance(vacancy.employer, dict):
                        raw_employer_name = vacancy.employer.get('name')
                    elif vacancy.employer:
                        raw_employer_name = str(vacancy.employer)

                    employer_str = self._standardize_employer_name(raw_employer_name)

                    area_str = (
                        vacancy.area.get('name') if isinstance(vacancy.area, dict)
                        else str(vacancy.area) if vacancy.area else None
                    )

                    # Обработка даты published_at
                    published_date = None
                    if vacancy.published_at:
                        if isinstance(vacancy.published_at, str):
                            try:
                                # Пытаемся парсить ISO формат даты
                                from datetime import datetime
                                if 'T' in vacancy.published_at:
                                    # Формат: 2025-08-25T18:47:30+0300
                                    if '+' in vacancy.published_at:
                                        # Заменяем +0300 на +03:00 для совместимости с Python
                                        date_str = vacancy.published_at
                                        if date_str.endswith('+0300'):
                                            date_str = date_str.replace('+0300', '+03:00')
                                        elif date_str.endswith('+0000'):
                                            date_str = date_str.replace('+0000', '+00:00')
                                        published_date = datetime.fromisoformat(date_str)
                                    else:
                                        published_date = datetime.fromisoformat(vacancy.published_at)
                                else:
                                    published_date = datetime.fromisoformat(vacancy.published_at)
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Не удалось распарсить дату {vacancy.published_at}: {e}")
                                # Пытаемся использовать текущую дату как fallback
                                from datetime import datetime
                                published_date = datetime.now()
                        elif hasattr(vacancy.published_at, 'isoformat'):
                            # Это уже datetime объект
                            published_date = vacancy.published_at
                        else:
                            # Пытаемся преобразовать в datetime
                            try:
                                from datetime import datetime
                                published_date = datetime.fromisoformat(str(vacancy.published_at))
                            except:
                                published_date = datetime.now()

                    # Валидация описания
                    final_description = vacancy.description
                    if not final_description or not final_description.strip():
                        # Если описание пустое, формируем его из доступных данных
                        desc_parts = []
                        if vacancy.requirements:
                            desc_parts.append(f"Требования: {vacancy.requirements}")
                        if vacancy.responsibilities:
                            desc_parts.append(f"Обязанности: {vacancy.responsibilities}")
                        if desc_parts:
                            final_description = " ".join(desc_parts)
                        else:
                            final_description = f"Вакансия: {vacancy.title}"

                        logger.debug(f"Сформировано описание для вакансии {vacancy.vacancy_id}: {final_description[:100]}...")


                    insert_data.append((
                        vacancy.vacancy_id, vacancy.title, vacancy.url,
                        salary_from, salary_to, salary_currency,
                        final_description, vacancy.requirements, vacancy.responsibilities,
                        vacancy.experience, vacancy.employment, vacancy.schedule,
                        employer_str, area_str, vacancy.source, published_date,
                        mapped_company_id  # Оставляем как integer
                    ))

                insert_query = """
                INSERT INTO vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at, company_id
                ) VALUES %s
                """

                from psycopg2.extras import execute_values
                execute_values(cursor, insert_query, insert_data, template=None, page_size=100)

            # Batch update существующих вакансий
            if update_vacancies:
                for vacancy in update_vacancies:
                    salary_from = vacancy.salary.salary_from if vacancy.salary else None
                    salary_to = vacancy.salary.salary_to if vacancy.salary else None
                    salary_currency = vacancy.salary.currency if vacancy.salary else None

                    # Определяем company_id на основе employer
                    mapped_company_id = None
                    employer_name = None
                    employer_id = None

                    if vacancy.employer:
                        # Правильно извлекаем имя работодателя и ID
                        if isinstance(vacancy.employer, dict):
                            employer_name = vacancy.employer.get('name')
                            employer_id = vacancy.employer.get('id')
                        elif isinstance(vacancy.employer, str):
                            employer_name = vacancy.employer
                        else:
                            employer_name = str(vacancy.employer)

                    # Также проверяем специфичные поля для SJ
                    if hasattr(vacancy, 'source') and vacancy.source == 'superjob.ru':
                        # Для SuperJob проверяем firm_id или client_id в исходных данных
                        if hasattr(vacancy, '_raw_data') and vacancy._raw_data:
                            sj_firm_id = vacancy._raw_data.get('firm_id') or vacancy._raw_data.get('client_id')
                            if sj_firm_id:
                                mapped_company_id = company_mapping.get(str(sj_firm_id))

                    # Если ID не найден по внешнему ID, ищем по имени
                    if not mapped_company_id and employer_name and employer_name.strip():
                        employer_lower = employer_name.lower().strip()

                        # 1. Поиск по внешнему ID (для HH)
                        if employer_id and not mapped_company_id:
                            mapped_company_id = company_mapping.get(str(employer_id))

                        # 2. Прямое соответствие по названию
                        if not mapped_company_id:
                            mapped_company_id = company_mapping.get(employer_lower)

                        # 3. Поиск частичного соответствия (улучшенный)
                        if not mapped_company_id:
                            # Сначала ищем точные вхождения
                            for alt_name, comp_id in company_mapping.items():
                                if isinstance(alt_name, str) and alt_name == employer_lower:
                                    mapped_company_id = comp_id
                                    break

                        # 4. Поиск частичного соответствия
                        if not mapped_company_id:
                            for alt_name, comp_id in company_mapping.items():
                                if isinstance(alt_name, str) and len(alt_name) > 2 and (alt_name in employer_lower or employer_lower in alt_name):
                                    mapped_company_id = comp_id
                                    break

                        # 5. Логирование для отладки
                        if not mapped_company_id and employer_name:
                            source_info = f" (source: {getattr(vacancy, 'source', 'unknown')})"
                            logger.debug(f"Company_id не найден для работодателя: '{employer_name}'{source_info} (vacancy_id: {vacancy.vacancy_id})")


                    # Standardize employer name before storing
                    raw_employer_name = None
                    if isinstance(vacancy.employer, dict):
                        raw_employer_name = vacancy.employer.get('name')
                    elif vacancy.employer:
                        raw_employer_name = str(vacancy.employer)

                    employer_str = self._standardize_employer_name(raw_employer_name)

                    area_str = (
                        vacancy.area.get('name') if isinstance(vacancy.area, dict)
                        else str(vacancy.area) if vacancy.area else None
                    )

                    # Обработка даты published_at
                    published_date = None
                    if vacancy.published_at:
                        if isinstance(vacancy.published_at, str):
                            try:
                                # Пытаемся парсить ISO формат даты
                                from datetime import datetime
                                if 'T' in vacancy.published_at:
                                    # Формат: 2025-08-25T18:47:30+0300
                                    if '+' in vacancy.published_at:
                                        # Заменяем +0300 на +03:00 для совместимости с Python
                                        date_str = vacancy.published_at
                                        if date_str.endswith('+0300'):
                                            date_str = date_str.replace('+0300', '+03:00')
                                        elif date_str.endswith('+0000'):
                                            date_str = date_str.replace('+0000', '+00:00')
                                        published_date = datetime.fromisoformat(date_str)
                                    else:
                                        published_date = datetime.fromisoformat(vacancy.published_at)
                                else:
                                    published_date = datetime.fromisoformat(vacancy.published_at)
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Не удалось распарсить дату {vacancy.published_at}: {e}")
                                # Пытаемся использовать текущую дату как fallback
                                from datetime import datetime
                                published_date = datetime.now()
                        elif hasattr(vacancy.published_at, 'isoformat'):
                            # Это уже datetime объект
                            published_date = vacancy.published_at
                        else:
                            # Пытаемся преобразовать в datetime
                            try:
                                from datetime import datetime
                                published_date = datetime.fromisoformat(str(vacancy.published_at))
                            except:
                                published_date = datetime.now()


                    update_query = """
                    UPDATE vacancies SET
                        title = %s, url = %s, salary_from = %s, salary_to = %s,
                        salary_currency = %s, description = %s, requirements = %s,
                        responsibilities = %s, experience = %s, employment = %s,
                        schedule = %s, employer = %s, area = %s, source = %s, published_at = %s,
                        company_id = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE vacancy_id = %s
                    """

                    cursor.execute(update_query, (
                        vacancy.title, vacancy.url, salary_from, salary_to,
                        salary_currency, vacancy.description, vacancy.requirements,
                        vacancy.responsibilities, vacancy.experience, vacancy.employment,
                        vacancy.schedule, employer_str, area_str, vacancy.source,
                        published_date, mapped_company_id, vacancy.vacancy_id
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
            # Join with companies to get company name for filtering and display
            query = "SELECT v.*, c.name as company_name FROM vacancies v LEFT JOIN companies c ON v.company_id = c.id"
            params = []
            where_conditions = []

            # Добавляем фильтры
            if filters:
                if filters.get('title'):
                    where_conditions.append("LOWER(v.title) LIKE LOWER(%s)")
                    params.append(f"%{filters['title']}%")

                if filters.get('salary_from'):
                    where_conditions.append("v.salary_from >= %s")
                    params.append(filters['salary_from'])

                if filters.get('salary_to'):
                    where_conditions.append("v.salary_to <= %s")
                    params.append(filters['salary_to'])

                if filters.get('employer'): # Filter by standardized employer name
                    standardized_employer = self._standardize_employer_name(filters['employer'])
                    if standardized_employer:
                        where_conditions.append("LOWER(v.employer) LIKE LOWER(%s)")
                        params.append(f"%{standardized_employer}%")

                # Filter by company name directly using the join
                if filters.get('company_name'):
                    where_conditions.append("LOWER(c.name) LIKE LOWER(%s)")
                    params.append(f"%{filters['company_name']}%")


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

                # Set company_id if available
                if row.get('company_id'):
                    vacancy.company_id = row['company_id']

                # Set company name if available from the join
                if row.get('company_name'):
                    vacancy.company_name = row['company_name']


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

                if filters.get('employer'): # Filter by standardized employer name
                    standardized_employer = self._standardize_employer_name(filters['employer'])
                    if standardized_employer:
                        where_conditions.append("LOWER(employer) LIKE LOWER(%s)")
                        params.append(f"%{standardized_employer}%")

                # Filter by company name directly
                if filters.get('company_name'):
                    where_conditions.append("LOWER(company_name) LIKE LOWER(%s)")
                    params.append(f"%{filters['company_name']}%")


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
            SELECT v.*, c.name as company_name FROM vacancies v LEFT JOIN companies c ON v.company_id = c.id
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
                    published_at TIMESTAMP,
                    company_id INTEGER
                ) ON COMMIT DROP
            """)

            # Получаем соответствие employer -> company_id из таблицы companies
            company_mapping = {}
            try:
                # Ensure companies table exists before querying
                self._ensure_companies_table_exists()

                cursor.execute("SELECT id, hh_id, sj_id, company_id, name, source FROM companies")
                companies = cursor.fetchall()

                for company in companies:
                    id, hh_id, sj_id, company_id, name, source = company

                    # Добавляем маппинг по внешним ID
                    if hh_id:
                        company_mapping[str(hh_id)] = id
                    if sj_id:
                        company_mapping[str(sj_id)] = id

                    # Добавляем маппинг по названию
                    company_mapping[name.lower()] = id

            except Exception as e:
                logger.error(f"Ошибка при получении соответствия компаний: {e}")


            # Подготавливаем данные для вставки
            insert_data = []
            for vacancy in vacancies:
                salary_from = vacancy.salary.salary_from if vacancy.salary else None
                salary_to = vacancy.salary.salary_to if vacancy.salary else None
                salary_currency = vacancy.salary.currency if vacancy.salary else None

                # Определяем company_id на основе employer
                mapped_company_id = None
                employer_name = None
                employer_id = None

                if vacancy.employer:
                    # Правильно извлекаем имя работодателя и ID
                    if isinstance(vacancy.employer, dict):
                        employer_name = vacancy.employer.get('name')
                        employer_id = vacancy.employer.get('id')
                    elif isinstance(vacancy.employer, str):
                        employer_name = vacancy.employer
                    else:
                        employer_name = str(vacancy.employer)

                # Также проверяем специфичные поля для SJ
                if hasattr(vacancy, 'source') and vacancy.source == 'superjob.ru':
                    # Для SuperJob проверяем firm_id или client_id в исходных данных
                    if hasattr(vacancy, '_raw_data') and vacancy._raw_data:
                        sj_firm_id = vacancy._raw_data.get('firm_id') or vacancy._raw_data.get('client_id')
                        if sj_firm_id:
                            mapped_company_id = company_mapping.get(str(sj_firm_id))

                # Если ID не найден по внешнему ID, ищем по имени
                if not mapped_company_id and employer_name and employer_name.strip():
                    employer_lower = employer_name.lower().strip()

                    # 1. Поиск по внешнему ID (для HH)
                    if employer_id and not mapped_company_id:
                        mapped_company_id = company_mapping.get(str(employer_id))

                    # 2. Прямое соответствие по названию
                    if not mapped_company_id:
                        mapped_company_id = company_mapping.get(employer_lower)

                    # 3. Поиск частичного соответствия (улучшенный)
                    if not mapped_company_id:
                        # Сначала ищем точные вхождения
                        for alt_name, comp_id in company_mapping.items():
                            if isinstance(alt_name, str) and alt_name == employer_lower:
                                mapped_company_id = comp_id
                                break

                    # 4. Поиск частичного соответствия
                    if not mapped_company_id:
                        for alt_name, comp_id in company_mapping.items():
                            if isinstance(alt_name, str) and len(alt_name) > 2 and (alt_name in employer_lower or employer_lower in alt_name):
                                mapped_company_id = comp_id
                                break

                    # 5. Логирование для отладки
                    if not mapped_company_id and employer_name:
                        source_info = f" (source: {getattr(vacancy, 'source', 'unknown')})"
                        logger.debug(f"Company_id не найден для работодателя: '{employer_name}'{source_info} (vacancy_id: {vacancy.vacancy_id})")


                # Standardize employer name before storing
                raw_employer_name = None
                if isinstance(vacancy.employer, dict):
                    raw_employer_name = vacancy.employer.get('name')
                elif vacancy.employer:
                    raw_employer_name = str(vacancy.employer)

                employer_str = self._standardize_employer_name(raw_employer_name)

                area_str = (
                    vacancy.area.get('name') if isinstance(vacancy.area, dict)
                    else str(vacancy.area) if vacancy.area else None
                )

                # Обработка даты published_at
                published_date = None
                if vacancy.published_at:
                    if isinstance(vacancy.published_at, str):
                        try:
                            # Пытаемся парсить ISO формат даты
                            from datetime import datetime
                            if 'T' in vacancy.published_at:
                                # Формат: 2025-08-25T18:47:30+0300
                                if '+' in vacancy.published_at:
                                    # Заменяем +0300 на +03:00 для совместимости с Python
                                    date_str = vacancy.published_at
                                    if date_str.endswith('+0300'):
                                        date_str = date_str.replace('+0300', '+03:00')
                                    elif date_str.endswith('+0000'):
                                        date_str = date_str.replace('+0000', '+00:00')
                                    published_date = datetime.fromisoformat(date_str)
                                else:
                                    published_date = datetime.fromisoformat(vacancy.published_at)
                            else:
                                published_date = datetime.fromisoformat(vacancy.published_at)
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Не удалось распарсить дату {vacancy.published_at}: {e}")
                            # Пытаемся использовать текущую дату как fallback
                            from datetime import datetime
                            published_date = datetime.now()
                    elif hasattr(vacancy.published_at, 'isoformat'):
                        # Это уже datetime объект
                        published_date = vacancy.published_at
                    else:
                        # Пытаемся преобразовать в datetime
                        try:
                            from datetime import datetime
                            published_date = datetime.fromisoformat(str(vacancy.published_at))
                        except:
                            published_date = datetime.now()

                insert_data.append((
                    vacancy.vacancy_id, vacancy.title, vacancy.url,
                    salary_from, salary_to, salary_currency,
                    vacancy.description, vacancy.requirements, vacancy.responsibilities,
                    vacancy.experience, vacancy.employment, vacancy.schedule,
                    employer_str, area_str, vacancy.source, published_date,
                    mapped_company_id  # Оставляем как integer
                ))

            # Bulk insert во временную таблицу
            from psycopg2.extras import execute_values
            execute_values(
                cursor,
                """INSERT INTO temp_api_vacancies (
                    vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, employer, area, source, published_at, company_id
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
                    # Standardize employer name for filtering as well
                    standardized_employer = self._standardize_employer_name(employer)
                    if standardized_employer:
                        employer_conditions.append("LOWER(employer) LIKE LOWER(%s)")
                        params.append(f"%{standardized_employer}%")

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

            # Фильтр по company_id
            if filters.get('company_id'):
                where_conditions.append("company_id = %s")
                params.append(filters['company_id'])

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
                        # Update company_id in the original vacancy object
                        original_vacancy.company_id = row['company_id']
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

        if filters.get('employer'): # Filter by standardized employer name
            standardized_employer = self._standardize_employer_name(filters['employer'])
            if standardized_employer:
                conditions.append("LOWER(employer) LIKE LOWER(%s)")
                params.append(f"%{standardized_employer}%")

        if filters.get('company_id'): # Filter by company_id
            conditions.append("company_id = %s")
            params.append(filters['company_id'])

        if filters.get('experience'):
            conditions.append("LOWER(experience) LIKE LOWER(%s)")
            params.append(f"%{filters['experience']}%")

        if filters.get('employment'):
            conditions.append("LOWER(employment) LIKE LOWER(%s)")
            params.append(f"%{filters['employment']}%")

        return {'conditions': conditions, 'params': params}

    def _ensure_companies_table_exists(self):
        """Создает таблицу companies если она не существует"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                hh_id VARCHAR(50),
                sj_id VARCHAR(50),
                company_id VARCHAR(255) UNIQUE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                url TEXT,
                logo_url TEXT,
                site_url TEXT,
                source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)

            # Проверяем и обновляем типы полей при необходимости
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'companies' AND column_name IN ('hh_id', 'sj_id');
            """)
            
            columns_info = cursor.fetchall()
            for col_name, data_type in columns_info:
                if data_type == 'integer':
                    logger.info(f"Изменяем тип поля {col_name} с INTEGER на VARCHAR...")
                    try:
                        cursor.execute(f"ALTER TABLE companies ALTER COLUMN {col_name} TYPE VARCHAR(50) USING {col_name}::VARCHAR(50)")
                        logger.info(f"✓ Тип поля {col_name} изменен на VARCHAR(50)")
                    except psycopg2.Error as e:
                        logger.warning(f"Не удалось изменить тип поля {col_name}: {e}")

            # Add indexes if they don't exist
            indexes_to_create = [
                ("idx_companies_hh_id", "hh_id"),
                ("idx_companies_sj_id", "sj_id"),
                ("idx_companies_company_id", "company_id"),
                ("idx_companies_name", "name"),
                ("idx_companies_source", "source")
            ]

            for index_name, column_name in indexes_to_create:
                cursor.execute(f"SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'companies' AND indexname = '{index_name}';")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"CREATE INDEX {index_name} ON companies({column_name});")

            connection.commit()
            logger.info("✓ Таблица 'companies' успешно создана/проверена")

        except psycopg2.Error as e:
            logger.error(f"Ошибка создания таблицы 'companies': {e}")
            connection.rollback()
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            connection.close()