import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    PsycopgError = psycopg2.Error
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    PsycopgError = Exception

from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class PostgresSaver(AbstractVacancyStorage):
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
            self.host = db_config.get("host", "localhost")
            self.port = db_config.get("port", "5432")
            self.database = db_config.get("database", "Project03")
            self.username = db_config.get("username", "postgres")
            self.password = db_config.get("password", "")
        else:
            # Используем переменные окружения через EnvLoader (поддерживает .env и Secrets)
            from src.utils.env_loader import EnvLoader

            self.host = EnvLoader.get_env_var("PGHOST", "localhost")
            self.port = EnvLoader.get_env_var("PGPORT", "5432")
            self.database = EnvLoader.get_env_var("PGDATABASE", "Project03")
            self.username = EnvLoader.get_env_var("PGUSER", "postgres")
            self.password = EnvLoader.get_env_var("PGPASSWORD", "")

        # Создание базы данных теперь делегируется DBManager
        # self._ensure_database_exists()  # Удалено - теперь используется DBManager
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
                client_encoding="utf8",
            )
            # Устанавливаем кодировку для соединения
            connection.set_client_encoding("UTF8")
            return connection
        except PsycopgError as e:
            logger.error(f"Ошибка подключения к БД {db_name}: {e}")
            raise


    def _ensure_companies_table_exists(self):
        """Создает таблицу companies если она не существует"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Создаем упрощенную таблицу companies для целевых компаний
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    hh_id VARCHAR(50),
                    sj_id VARCHAR(50)
                );
            """
            )

            # Проверяем и добавляем недостающие поля hh_id и sj_id
            required_fields = [("hh_id", "VARCHAR(50)"), ("sj_id", "VARCHAR(50)")]

            for field_name, field_type in required_fields:
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'companies' AND column_name = %s;
                """,
                    (field_name,),
                )

                if not cursor.fetchone():
                    logger.info(f"Добавляем поле {field_name} в таблицу companies...")
                    cursor.execute(f"ALTER TABLE companies ADD COLUMN {field_name} {field_type};")
                    logger.info(f"✓ Поле {field_name} добавлено")

            # Создаем индексы
            indexes = [
                ("idx_companies_name", "name"),
                ("idx_companies_hh_id", "hh_id"),
                ("idx_companies_sj_id", "sj_id"),
            ]

            for index_name, columns in indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON companies({columns});")
                    logger.info(f"✓ Индекс {index_name} проверен/создан")
                except PsycopgError as e:
                    logger.warn(f"Не удалось создать индекс {index_name}: {e}")

            connection.commit()
            logger.info("✓ Таблица companies успешно создана/проверена")

            # Инициализируем целевые компании
            self._initialize_target_companies()

        except PsycopgError as e:
            logger.error(f"Ошибка создания таблицы companies: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass  # Соединение уже закрыто
            raise
        finally:
            if "cursor" in locals():
                try:
                    cursor.close()
                except Exception:
                    pass
            if not connection.closed:
                try:
                    connection.close()
                except Exception:
                    pass

    def _initialize_target_companies(self):
        """Инициализирует целевые компании в таблице companies"""
        try:
            from src.config.target_companies import TargetCompanies

            TARGET_COMPANIES = TargetCompanies.get_all_companies()

            connection = self._get_connection()
            cursor = connection.cursor()

            for company in TARGET_COMPANIES:
                # Проверяем, есть ли компания в БД
                cursor.execute(
                    """
                    SELECT id FROM companies
                    WHERE hh_id = %s OR sj_id = %s OR name = %s
                    LIMIT 1
                """,
                    (company.hh_id, company.sj_id, company.name),
                )

                if not cursor.fetchone():
                    # Добавляем компанию если её нет
                    cursor.execute(
                        """
                        INSERT INTO companies (name, hh_id, sj_id)
                        VALUES (%s, %s, %s)
                    """,
                        (company.name, company.hh_id, company.sj_id),
                    )
                    logger.info(f"✓ Добавлена целевая компания: {company.name} (HH ID: {company.hh_id})")

            connection.commit()
            logger.info("✓ Целевые компании инициализированы")

        except Exception as e:
            logger.error(f"Ошибка инициализации целевых компаний: {e}")
            if "connection" in locals() and not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass  # Соединение уже закрыто
        finally:
            if "cursor" in locals():
                try:
                    cursor.close()
                except Exception:
                    pass
            if "connection" in locals() and not connection.closed:
                try:
                    connection.close()
                except Exception:
                    pass

    def _ensure_tables_exist(self):
        """Создает таблицы если они не существуют"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Устанавливаем кодировку сессии
            cursor.execute("SET client_encoding TO 'UTF8'")

            # Сначала создаем таблицу companies если её нет
            self._ensure_companies_table_exists()

            # Создаем таблицу для вакансий с базовой структурой
            create_table_query = """
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                vacancy_id VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """

            cursor.execute(create_table_query)
            logger.info("✓ Базовая структура таблицы vacancies проверена")

            # Список всех полей, которые должны быть в таблице vacancies
            required_fields = [
                ("url", "TEXT"),
                ("salary_from", "INTEGER"),
                ("salary_to", "INTEGER"),
                ("salary_currency", "VARCHAR(10)"),
                ("description", "TEXT"),
                ("requirements", "TEXT"),
                ("responsibilities", "TEXT"),
                ("experience", "VARCHAR(200)"),
                ("employment", "VARCHAR(200)"),
                ("schedule", "VARCHAR(200)"),
                ("area", "VARCHAR(200)"),
                ("source", "VARCHAR(50) DEFAULT 'unknown'"),
                ("published_at", "TIMESTAMP"),
            ]

            # Проверяем и добавляем недостающие поля
            for field_name, field_type in required_fields:
                cursor.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'vacancies' AND column_name = %s;
                """,
                    (field_name,),
                )

                field_info = cursor.fetchone()
                if not field_info:
                    logger.info(f"Добавляем поле {field_name} в таблицу vacancies...")
                    cursor.execute(f"ALTER TABLE vacancies ADD COLUMN {field_name} {field_type};")
                    logger.info(f"✓ Поле {field_name} добавлено")

            # Создаем индексы для оптимизации запросов
            indexes_to_create = [
                ("idx_vacancy_id", "vacancy_id"),
                ("idx_title", "title"),
                ("idx_salary", "salary_from, salary_to"),
                ("idx_source", "source"),
                ("idx_published_at", "published_at"),
            ]

            for index_name, columns in indexes_to_create:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON vacancies({columns});")
                    logger.info(f"✓ Индекс {index_name} проверен/создан")
                except PsycopgError as e:
                    logger.warn(f"Не удалось создать индекс {index_name}: {e}")

            # Создаем внешний ключ если его еще нет
            try:
                cursor.execute(
                    """
                    SELECT constraint_name FROM information_schema.table_constraints
                    WHERE table_name = 'vacancies'
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name = 'fk_vacancies_company_id'
                """
                )

                if not cursor.fetchone():
                    cursor.execute(
                        """
                        ALTER TABLE vacancies
                        ADD CONSTRAINT fk_vacancies_company_id
                        FOREIGN KEY (company_id) REFERENCES companies(id)
                        ON DELETE SET NULL
                    """
                    )
                    logger.info("✓ Внешний ключ fk_vacancies_company_id создан")
            except PsycopgError as e:
                logger.warning(f"Не удалось создать внешний ключ: {e}")

            connection.commit()
            logger.info("✓ Таблицы успешно созданы/проверены")

        except PsycopgError as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass  # Соединение уже закрыто
            raise
        finally:
            if "cursor" in locals():
                try:
                    cursor.close()
                except Exception:
                    pass
            if not connection.closed:
                try:
                    connection.close()
                except Exception:
                    pass

    def add_vacancy_batch_optimized(
        self, vacancies: Union[Vacancy, List[Vacancy]], search_query: str = None
    ) -> List[str]:
        """
        Максимально оптимизированное batch-добавление вакансий через временные таблицы.
        Использует SQL для всех операций, минимизирует количество запросов.
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        # Исправляем двойную вложенность списков
        if len(vacancies) == 1 and isinstance(vacancies[0], list):
            vacancies = vacancies[0]
            logger.debug(f"Исправлена двойная вложенность списка: получено {len(vacancies)} вакансий")

        if not vacancies:
            return []

        connection = self._get_connection()
        update_messages: List[str] = []

        try:
            cursor = connection.cursor()

            # Создаем временную таблицу с такой же структурой как основная таблица vacancies
            cursor.execute(
                """
                CREATE TEMP TABLE temp_new_vacancies AS
                SELECT * FROM vacancies WHERE 1=0
            """
            )

            # Получаем сопоставление компаний только по ID
            cursor.execute(
                """
                SELECT id, name, hh_id, sj_id
                FROM companies
            """
            )

            company_id_mapping = {}  # hh_id/sj_id -> company_id

            results = cursor.fetchall()
            for row in results:
                comp_id, name, hh_id, sj_id = row

                # Добавляем только ID-маппинги с приведением к строке
                if hh_id:
                    company_id_mapping[str(hh_id)] = comp_id
                if sj_id:
                    company_id_mapping[str(sj_id)] = comp_id

            # Подготавливаем данные для вставки/обновления (все переданные вакансии)
            insert_data = []
            vacancy_company_mapping = {}  # Словарь для сохранения соответствия vacancy_id -> company_id

            for vacancy in vacancies:
                # Проверяем, что vacancy действительно объект Vacancy
                if not hasattr(vacancy, "employer"):
                    logger.error(f"Объект не является Vacancy: {type(vacancy)} - {vacancy}")
                    continue

                # Определяем company_id для связи с таблицей companies
                mapped_company_id = None
                employer_name = None
                employer_id = None

                if vacancy.employer:
                    if isinstance(vacancy.employer, dict):
                        employer_name = vacancy.employer.get("name", "").strip()
                        employer_id = vacancy.employer.get("id", "").strip()
                    elif hasattr(vacancy.employer, "get_name"):
                        employer_name = vacancy.employer.get_name().strip()
                        employer_id = getattr(vacancy.employer, "id", "").strip()
                    elif hasattr(vacancy.employer, "name"):
                        employer_name = str(getattr(vacancy.employer, "name", "")).strip()
                        employer_id = str(getattr(vacancy.employer, "id", "")).strip()
                    else:
                        employer_name = str(vacancy.employer).strip()
                        employer_id = ""

                # Фильтруем ТОЛЬКО по ID компаний (hh_id и sj_id)
                if employer_id:
                    mapped_company_id = company_id_mapping.get(str(employer_id))

                # Сохраняем соответствие и устанавливаем company_id
                if mapped_company_id:
                    vacancy_company_mapping[vacancy.id] = mapped_company_id
                    vacancy.company_id = mapped_company_id
                    logger.debug(
                        f"Сопоставлено: '{employer_name}' (ID: {employer_id}) -> company_id: {mapped_company_id}"
                    )

            # Обрабатываем ВСЕ переданные вакансии
            for vacancy in vacancies:
                # Проверяем, что vacancy действительно объект Vacancy
                if not hasattr(vacancy, "employer"):
                    logger.error(f"Объект не является Vacancy во втором цикле: {type(vacancy)}")
                    continue

                mapped_company_id = vacancy_company_mapping.get(vacancy.id, None)

                # Безопасная обработка salary
                salary_from = None
                salary_to = None
                salary_currency = None

                if vacancy.salary:
                    if hasattr(vacancy.salary, "salary_from"):
                        salary_from = vacancy.salary.salary_from
                        salary_to = vacancy.salary.salary_to
                        salary_currency = vacancy.salary.currency
                    elif isinstance(vacancy.salary, dict):
                        salary_from = vacancy.salary.get("from")
                        salary_to = vacancy.salary.get("to")
                        salary_currency = vacancy.salary.get("currency")
                    # Если salary - boolean или что-то другое, оставляем None

                # Конвертируем employer в строку для сохранения в БД
                employer_str = None
                if vacancy.employer:
                    if isinstance(vacancy.employer, dict):
                        employer_str = vacancy.employer.get("name", str(vacancy.employer))
                    elif hasattr(vacancy.employer, "get_name"):
                        employer_str = vacancy.employer.get_name()
                    elif hasattr(vacancy.employer, "name"):
                        employer_str = str(getattr(vacancy.employer, "name", ""))
                    else:
                        employer_str = str(vacancy.employer)

                # Унифицированная обработка area для сохранения в БД
                try:
                    from utils.data_normalizers import normalize_area_data
                except ImportError:
                    from src.utils.data_normalizers import normalize_area_data
                area_str = normalize_area_data(vacancy.area)

                # Обработка полей объектов в строки для БД
                experience_str = None
                if vacancy.experience:
                    if hasattr(vacancy.experience, "get_name"):
                        experience_str = vacancy.experience.get_name()
                    else:
                        experience_str = str(vacancy.experience)

                employment_str = None
                if vacancy.employment:
                    if hasattr(vacancy.employment, "get_name"):
                        employment_str = vacancy.employment.get_name()
                    else:
                        employment_str = str(vacancy.employment)

                schedule_str = None
                if vacancy.schedule:
                    if hasattr(vacancy.schedule, "get_name"):
                        schedule_str = vacancy.schedule.get_name()
                    else:
                        schedule_str = str(vacancy.schedule)

                # Обработка даты published_at
                published_date = self._normalize_published_date(vacancy.published_at)

                insert_data.append(
                    (
                        vacancy.id,
                        vacancy.name,
                        vacancy.url,
                        salary_from,
                        salary_to,
                        salary_currency,
                        vacancy.description,
                        vacancy.requirements,
                        vacancy.responsibilities,
                        experience_str,
                        employment_str,
                        schedule_str,
                        area_str,
                        vacancy.source,
                        published_date,
                        mapped_company_id,  # Всегда будет не None для целевых компаний
                        search_query,
                    )
                )

            # Bulk insert во временную таблицу
            from psycopg2.extras import execute_values

            execute_values(
                cursor,
                """INSERT INTO temp_new_vacancies (
                    vacancy_id, name, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, area, source, published_at, company_id, search_query
                ) VALUES %s""",
                insert_data,
                template=None,
                page_size=1000,
            )

            # Находим новые вакансии (которых нет в основной таблице)
            cursor.execute(
                """
                INSERT INTO vacancies (
                    vacancy_id, name, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience,
                    employment, schedule, area, source, published_at, company_id, search_query
                )
                SELECT t.vacancy_id, t.name, t.url, t.salary_from, t.salary_to, t.salary_currency,
                       t.description, t.requirements, t.responsibilities, t.experience,
                       t.employment, t.schedule, t.area, t.source, t.published_at, t.company_id, t.search_query
                FROM temp_new_vacancies t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
                WHERE v.vacancy_id IS NULL
            """
            )

            new_count = cursor.rowcount

            # Находим и обновляем существующие вакансии с изменениями
            cursor.execute(
                """
                UPDATE vacancies v SET
                    name = t.name,
                    url = t.url,
                    description = t.description,
                    experience = t.experience,
                    employment = t.employment,
                    schedule = t.schedule,
                    area = t.area,
                    source = t.source,
                    published_at = t.published_at,
                    company_id = t.company_id,
                    updated_at = CURRENT_TIMESTAMP
                FROM temp_new_vacancies t
                WHERE v.vacancy_id = t.vacancy_id
                AND (
                    v.name != t.name OR
                    v.url != t.url OR
                    v.description != t.description OR
                    COALESCE(v.salary_from, 0) != COALESCE(t.salary_from, 0) OR
                    COALESCE(v.salary_to, 0) != COALESCE(t.salary_to, 0) OR
                    COALESCE(v.salary_currency, '') != COALESCE(t.salary_currency, '') OR
                    COALESCE(v.company_id::text, '') IS DISTINCT FROM COALESCE(t.company_id::text, '') -- Приведение к text для сравнения
                )
            """
            )

            updated_count = cursor.rowcount

            # Получаем информацию о добавленных и обновленных вакансиях для сообщений
            cursor.execute(
                """
                SELECT t.vacancy_id, t.name,
                       CASE WHEN v.vacancy_id IS NULL THEN 'new' ELSE 'updated' END as action
                FROM temp_new_vacancies t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
                ORDER BY action, t.vacancy_id
                LIMIT 10
            """
            )

            results = cursor.fetchall()
            for row in results:
                # Используем индексы вместо ключей для обычного cursor
                vacancy_id, title, action = row[0], row[1], row[2]
                if action == "new":
                    update_messages.append(f"Добавлена новая вакансия ID {vacancy_id}: '{title}'")
                else:
                    update_messages.append(f"Вакансия ID {vacancy_id} обновлена: '{title}'")

            # Добавляем сводку если много операций
            total_processed = len(vacancies)
            if total_processed > 10:
                if new_count > 5:
                    update_messages.append(f"... и еще {new_count - 5} новых вакансий")
                if updated_count > 5:
                    update_messages.append(f"... и еще {updated_count - 5} обновленных вакансий")

            connection.commit()

            total_input = len(vacancies)

            logger.info("Batch операция через временные таблицы:")
            logger.info(f"  Входящих вакансий: {total_input}")
            logger.info(f"  Добавлено в БД: {new_count}")
            logger.info(f"  Обновлено в БД: {updated_count}")

            # Дополнительная проверка количества записей в БД
            cursor.execute("SELECT COUNT(*) FROM vacancies")
            total_in_db = cursor.fetchone()[0]
            logger.info(f"  Итого записей в БД после операции: {total_in_db}")

            # Показываем сводку результатов
            logger.info(
                f"Результат: сохранено {new_count + updated_count} из {total_input} вакансий (новых: {new_count}, обновлено: {updated_count})"
            )

        except PsycopgError as e:
            logger.error(f"Ошибка при batch операции через временные таблицы: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            raise
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

        return update_messages

    def add_vacancy(self, vacancy: Union[Vacancy, List[Vacancy]]) -> Union[bool, List[str]]:
        """
        Добавляет одну вакансию или список вакансий в базу данных

        Args:
            vacancy: Объект вакансии или список вакансий для добавления

        Returns:
            Union[bool, List[str]]: True/False для одной вакансии, список сообщений для множественных
        """
        try:
            if isinstance(vacancy, list):
                # Если передан список, используем batch метод
                return self.add_vacancy_batch_optimized(vacancy)
            else:
                # Если передана одна вакансия, конвертируем в список
                result = self.add_vacancies([vacancy])
                # add_vacancies возвращает список добавленных вакансий
                # Если список не пустой, значит вакансия добавлена
                return len(result) > 0 if isinstance(result, list) else bool(result)
        except Exception as e:
            logger.error(f"Ошибка добавления вакансии: {e}")
            return False if not isinstance(vacancy, list) else []

    def add_vacancies(self, vacancies: List[Vacancy]) -> List[str]:
        """
        Добавляет список вакансий в базу данных.
        Всегда использует batch операции для эффективности.

        Args:
            vacancies: Список объектов вакансий для добавления.

        Returns:
            List[str]: Список сообщений о результатах добавления.
        """
        if not vacancies:
            return []

        try:
            # Используем оптимизированный batch метод
            processed_vacancies = self.add_vacancy_batch_optimized(vacancies)
            successfully_added = []

            # Добавляем успешно обработанные вакансии в результат
            successfully_added.extend(processed_vacancies)

            logger.info(f"Успешно добавлено {len(processed_vacancies)} вакансий")
            return successfully_added
        except Exception as e:
            logger.error(f"Ошибка при пакетном добавлении вакансий: {e}")
            return []

    def save_vacancies(self, vacancies: Union[Vacancy, List[Vacancy]]) -> int:
        """
        Сохраняет вакансии в БД и возвращает количество операций

        Args:
            vacancies: Вакансия или список вакансий

        Returns:
            int: Количество операций (для совместимости)
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        update_messages = self.add_vacancy_batch_optimized(vacancies)
        return len(update_messages)

    def load_vacancies(
        self, limit: Optional[int] = None, offset: int = 0, filters: Optional[Dict[str, Any]] = None
    ) -> List[Vacancy]:
        """
        Загружает вакансии из БД с поддержкой пагинации и фильтров

        Args:
            limit: Максимальное количество вакансий
            offset: Смещение для пагинации
            filters: Словарь с фильтрами (title, salary_from, salary_to, employer)
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Строим базовый запрос с JOIN для получения названия компании
            query = "SELECT v.*, c.name as company_name FROM vacancies v LEFT JOIN companies c ON v.company_id = c.id"
            params = []
            where_conditions = []

            # Добавляем фильтры
            if filters:
                if filters.get("title"):
                    where_conditions.append("LOWER(v.title) LIKE LOWER(%s)")
                    params.append(f"%{filters['title']}%")

                if filters.get("salary_from"):
                    where_conditions.append("v.salary_from >= %s")
                    params.append(filters["salary_from"])

                if filters.get("salary_to"):
                    where_conditions.append("v.salary_to <= %s")
                    params.append(filters["salary_to"])

                if filters.get("employer"):  # Filter by company name from joined table
                    where_conditions.append("LOWER(c.name) LIKE LOWER(%s)")
                    params.append(f"%{filters['employer']}%")

                # Filter by company name directly using the join
                if filters.get("company_name"):
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

        except PsycopgError as e:
            logger.error(f"Ошибка загрузки вакансий: {e}")
            return []
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

    def _convert_rows_to_vacancies(self, rows: List) -> List[Vacancy]:
        """Конвертирует строки БД в объекты Vacancy"""
        vacancies = []
        skipped_count = 0  # Инициализируем счетчик пропущенных записей

        for row in rows:
            try:
                # Порядок полей из SQL запроса: "SELECT v.*, c.name as company_name FROM vacancies v LEFT JOIN companies c ON v.company_id = c.id"
                # Поля таблицы vacancies: id, vacancy_id, title, created_at, updated_at, url, salary_from, salary_to,
                # salary_currency, description, requirements, responsibilities, experience, employment, schedule,
                # area, source, published_at, company_id
                # Последнее поле: company_name из JOIN

                # Извлекаем данные по индексам (row это кортеж)
                vacancy_id = row[1]  # vacancy_id
                title = row[2]  # title
                # row[3] - created_at, row[4] - updated_at
                url = row[5]  # url
                salary_from = row[6]  # salary_from
                salary_to = row[7]  # salary_to
                salary_currency = row[8]  # salary_currency
                description = row[9]  # description
                requirements = row[10]  # requirements
                responsibilities = row[11]  # responsibilities
                experience = row[12]  # experience
                employment = row[13]  # employment
                schedule = row[14]  # schedule
                area = row[15]  # area
                source = row[16]  # source
                published_at_db = row[17]  # published_at
                company_id = row[18]  # company_id
                company_name = row[19] if len(row) > 19 else None  # company_name из JOIN

                # Создаем словарь salary_data для передачи в конструктор Vacancy
                salary_data = None
                if salary_from or salary_to:
                    salary_data = {"from": salary_from, "to": salary_to, "currency": salary_currency}

                # Создаем employer на основе company_name из JOIN или используем заглушку
                employer = None
                if company_name:
                    employer = {"name": company_name}
                else:
                    employer = {"name": "Неизвестная компания"}

                # Convert published_at string back to proper format
                published_at = None
                if published_at_db:
                    # Конвертируем datetime объект в строку ISO формата
                    if hasattr(published_at_db, "isoformat"):
                        published_at = published_at_db.isoformat()
                    else:
                        published_at = str(published_at_db)

                vacancy = Vacancy(
                    title=title,
                    url=url,
                    salary=salary_data,  # Передаем словарь, а не объект Salary
                    description=description,
                    requirements=requirements,
                    responsibilities=responsibilities,
                    experience=experience,
                    employment=employment,
                    schedule=schedule,
                    employer=employer,
                    vacancy_id=vacancy_id,
                    published_at=published_at,
                    source=source or "unknown",
                )

                # Устанавливаем area напрямую
                vacancy.area = area

                # Set company_id if available
                if company_id:
                    vacancy.company_id = company_id

                # Set company name if available from the join
                if company_name:
                    vacancy.company_name = company_name
                    # Для отладки - также сохраняем название компании напрямую
                    vacancy._employer_name = company_name

                vacancies.append(vacancy)

            except Exception as e:
                skipped_count += 1
                logger.error(f"Ошибка создания объекта Vacancy из БД (строка {skipped_count}): {e}")

                # Безопасное извлечение данных из кортежа для диагностики
                try:
                    row_vacancy_id = row[1] if len(row) > 1 else "N/A"
                    row_title = row[2] if len(row) > 2 else "N/A"
                    row_url = row[5] if len(row) > 5 else "N/A"

                    logger.error(f"Данные проблемной строки: vacancy_id={row_vacancy_id}, title={row_title}")
                    logger.debug(f"Полная строка: {row}")

                    # Дополнительная диагностика для выявления конкретных проблем
                    if not row_vacancy_id or row_vacancy_id == "N/A":
                        logger.error("  -> Проблема: отсутствует vacancy_id")
                    if not row_title or row_title == "N/A":
                        logger.error("  -> Проблема: отсутствует title")
                    if not row_url or row_url == "N/A":
                        logger.error("  -> Проблема: отсутствует URL")

                except Exception as diag_error:
                    logger.error(f"  -> Ошибка диагностики: {diag_error}")

                continue

        if skipped_count > 0:
            logger.warning(f"Пропущено {skipped_count} записей при конвертации из БД в объекты Vacancy")

        return vacancies

    def get_vacancies(self) -> List[Vacancy]:
        """Получить все сохраненные вакансии"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT
                            v.*,
                            c.name as company_name
                        FROM vacancies v
                        LEFT JOIN companies c ON v.company_id = c.id
                        ORDER BY v.created_at DESC
                    """
                    )

                    rows = cursor.fetchall()
                    vacancies = []
                    skipped_count = 0

                    for row in rows:
                        try:
                            # Создаем правильную структуру salary
                            salary_dict = None
                            if row["salary_from"] is not None or row["salary_to"] is not None:
                                salary_dict = {
                                    "from": row["salary_from"],
                                    "to": row["salary_to"],
                                    "currency": row["salary_currency"] or "RUR",
                                }

                            # Создаем объект Vacancy напрямую с новой Pydantic структурой
                            vacancy_data = {
                                "id": row["vacancy_id"],
                                "name": row["name"],  # Теперь используем правильное поле name
                                "url": row["url"] or "",  # Теперь url обязательное поле
                                "salary": salary_dict,
                                "snippet": {
                                    "requirement": row["requirements"] or "",
                                    "responsibility": row["responsibilities"] or "",
                                },
                                "employer": {"name": row["company_name"] or "Неизвестная компания"},
                                "area": row["area"] or "",  # Теперь area - это строка, не объект
                                "experience": {"name": row["experience"] or ""},
                                "employment": {"name": row["employment"] or ""},
                                "schedule": {"name": row["schedule"] or ""},
                                "published_at": row["published_at"].isoformat() if row["published_at"] else None,
                                "source": row["source"] or "database",
                            }

                            # Добавляем description если есть
                            if row["description"]:
                                vacancy_data["description"] = row["description"]

                            vacancy = Vacancy.from_dict(vacancy_data)
                            vacancies.append(vacancy)

                        except Exception as e:
                            skipped_count += 1
                            logger.error(f"Ошибка создания объекта Vacancy из БД: {e}")
                            logger.error(f"Данные строки: {dict(row)}")
                            continue

                    if skipped_count > 0:
                        logger.warning(f"Пропущено {skipped_count} записей из БД при создании объектов Vacancy")

                    logger.info(
                        f"Загружено {len(vacancies)} вакансий из БД ({len(rows)} записей в БД, пропущено {skipped_count})"
                    )
                    return vacancies

        except Exception as e:
            logger.error(f"Ошибка при получении вакансий: {e}")
            return []

    def delete_all_vacancies(self) -> bool:
        """Удаляет все вакансии"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM vacancies")
            connection.commit()
            logger.info("Все вакансии удалены")
            return True
        except PsycopgError as e:
            logger.error(f"Ошибка при удалении всех вакансий: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            return False
        finally:
            if "cursor" in locals():
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

        except PsycopgError as e:
            logger.error(f"Ошибка при удалении вакансии {vacancy_id}: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            return False
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

    def delete_vacancies_by_keyword(self, keyword: str) -> int:
        """Удаляет вакансии, содержащие указанное ключевое слово"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM vacancies WHERE LOWER(title) LIKE LOWER(%s)", (f"%{keyword}%",))

            deleted_count = cursor.rowcount
            connection.commit()

            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} вакансий по ключевому слову '{keyword}'")

            return deleted_count

        except PsycopgError as e:
            logger.error(f"Ошибка при удалении вакансий по ключевому слову '{keyword}': {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            return 0
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

    def delete_vacancy(self, vacancy: "AbstractVacancy") -> None:
        """
        Удаляет вакансию из PostgreSQL хранилища
        :param vacancy: Объект вакансии для удаления
        """
        self.delete_vacancy_by_id(vacancy.vacancy_id)

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
            placeholders = ",".join(["%s"] * len(vacancy_ids))
            query = f"DELETE FROM vacancies WHERE vacancy_id IN ({placeholders})"

            cursor.execute(query, vacancy_ids)
            deleted_count = cursor.rowcount
            connection.commit()

            if deleted_count > 0:
                logger.info(f"Batch удалено {deleted_count} вакансий")

            return deleted_count

        except PsycopgError as e:
            logger.error(f"Ошибка при batch удалении вакансий: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            return 0
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

    def is_vacancy_exists(self, vacancy: Vacancy) -> bool:
        """Проверяет, существует ли вакансия в БД"""
        connection = self._get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM vacancies WHERE vacancy_id = %s", (vacancy.vacancy_id,))
            return cursor.fetchone() is not None
        except PsycopgError as e:
            logger.error(f"Ошибка проверки существования вакансии: {e}")
            return False
        finally:
            if "cursor" in locals():
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
            cursor.execute(
                """
                CREATE TEMP TABLE temp_vacancy_check (
                    vacancy_id VARCHAR(50) PRIMARY KEY
                ) ON COMMIT DROP
            """
            )

            # Вставляем все ID для проверки
            vacancy_ids = [(v.vacancy_id,) for v in vacancies]
            from psycopg2.extras import execute_values

            execute_values(
                cursor,
                "INSERT INTO temp_vacancy_check (vacancy_id) VALUES %s",
                vacancy_ids,
                template=None,
                page_size=1000,
            )

            # Находим существующие ID одним запросом
            cursor.execute(
                """
                SELECT t.vacancy_id, (v.vacancy_id IS NOT NULL) as exists
                FROM temp_vacancy_check t
                LEFT JOIN vacancies v ON t.vacancy_id = v.vacancy_id
            """
            )

            result = {row[0]: row[1] for row in cursor.fetchall()}

            connection.commit()
            return result

        except PsycopgError as e:
            logger.error(f"Ошибка batch проверки через временную таблицу: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            # В случае ошибки возвращаем словарь с False для всех
            return {v.id: False for v in vacancies}
        finally:
            if "cursor" in locals():
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
        except PsycopgError as e:
            logger.error(f"Ошибка получения размера БД: {e}")
            return 0
        finally:
            if "cursor" in locals():
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

            query = "SELECT COUNT(*) FROM vacancies v LEFT JOIN companies c ON v.company_id = c.id"
            params = []
            where_conditions = []

            # Добавляем фильтры
            if filters:
                if filters.get("title"):
                    where_conditions.append("LOWER(title) LIKE LOWER(%s)")
                    params.append(f"%{filters['title']}%")

                if filters.get("salary_from"):
                    where_conditions.append("salary_from >= %s")
                    params.append(filters["salary_from"])

                if filters.get("salary_to"):
                    where_conditions.append("salary_to <= %s")
                    params.append(filters["salary_to"])

                if filters.get("employer"):  # Filter by company name from joined table
                    where_conditions.append("LOWER(c.name) LIKE LOWER(%s)")
                    params.append(f"%{filters['employer']}%")

                # Filter by company name directly
                if filters.get("company_name"):
                    where_conditions.append("LOWER(company_name) LIKE LOWER(%s)")
                    params.append(f"%{filters['company_name']}%")

            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            cursor.execute(query, params)
            return cursor.fetchone()[0]

        except PsycopgError as e:
            logger.error(f"Ошибка подсчета вакансий: {e}")
            return 0
        finally:
            if "cursor" in locals():
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
            cursor = connection.cursor()

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

        except PsycopgError as e:
            logger.error(f"Ошибка batch поиска вакансий: {e}")
            return []
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

    def filter_and_deduplicate_vacancies(
        self, vacancies: List[Vacancy], filters: Dict[str, Any] = None
    ) -> List[Vacancy]:
        """
        Единственная точка фильтрации и дедупликации вакансий через SQL временные таблицы.

        Выполняет:
        1. Фильтрацию по целевым компаниям
        2. Дедупликацию
        3. Дополнительные фильтры (если указаны)

        Args:
            vacancies: Список вакансий из API для обработки
            filters: Дополнительные фильтры (опционально)

        Returns:
            List[Vacancy]: Отфильтрованный и дедуплицированный список вакансий
        """
        if not vacancies:
            return []

        if filters is None:
            filters = {}

        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            logger.info(f"Начинаем SQL-фильтрацию и дедупликацию для {len(vacancies)} вакансий")

            # Создаем временную таблицу для всех операций
            cursor.execute(
                """
                CREATE TEMP TABLE temp_processing_vacancies (
                    original_index INTEGER,
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
                    area VARCHAR(200),
                    source VARCHAR(50),
                    published_at TIMESTAMP,
                    company_id INTEGER,
                    employer_name VARCHAR(500),
                    employer_id VARCHAR(50),
                    dedup_key VARCHAR(1000)
                ) ON COMMIT DROP
            """
            )

            # Получаем сопоставление компаний для фильтрации
            cursor.execute(
                """
                SELECT id, name, hh_id, sj_id, LOWER(name) as normalized_name
                FROM companies
            """
            )

            # Только ID-маппинг для фильтрации
            company_id_mapping = {}  # hh_id/sj_id -> company_id

            for row in cursor.fetchall():
                comp_id, name, hh_id, sj_id, normalized_name = row

                # Добавляем только ID-маппинги с приведением к строке
                if hh_id:
                    company_id_mapping[str(hh_id)] = comp_id
                if sj_id:
                    company_id_mapping[str(sj_id)] = comp_id

            # Подготавливаем данные для вставки с фильтрацией по целевым компаниям
            insert_data = []
            filtered_count = 0

            # Счетчик отфильтрованных вакансий
            target_found_count = 0

            for idx, vacancy in enumerate(vacancies):
                # Извлекаем данные работодателя
                employer_name = None
                employer_id = None

                if vacancy.employer:
                    if isinstance(vacancy.employer, dict):
                        employer_name = vacancy.employer.get("name", "").strip()
                        employer_id = vacancy.employer.get("id", "").strip()
                    else:
                        employer_name = str(vacancy.employer).strip()

                # Определяем company_id - ФИЛЬТРАЦИЯ ПО ЦЕЛЕВЫМ КОМПАНИЯМ
                # Фильтруем ТОЛЬКО по ID компаний (hh_id и sj_id)
                mapped_company_id = None
                if employer_id:
                    mapped_company_id = company_id_mapping.get(str(employer_id))

                # Логирование найденных целевых компаний
                if mapped_company_id:
                    logger.info(
                        f"Найдена целевая вакансия: '{vacancy.title}' от '{employer_name}' (ID: {employer_id})"
                    )

                # ФИЛЬТРУЕМ: пропускаем вакансии НЕ от целевых компаний
                if not mapped_company_id:
                    filtered_count += 1
                    continue

                # Создаем ключ дедупликации
                title_norm = self._normalize_text(vacancy.title or "")
                company_norm = self._normalize_text(employer_name or "")
                salary_key = (
                    f"{vacancy.salary.salary_from or 0}-{vacancy.salary.salary_to or 0}" if vacancy.salary else "0-0"
                )
                area_norm = self._normalize_text(str(vacancy.area) if vacancy.area else "")
                dedup_key = f"{title_norm}|{company_norm}|{salary_key}|{area_norm}"

                # Подготавливаем данные для вставки
                # Безопасная обработка salary
                salary_from = None
                salary_to = None
                salary_currency = None

                if vacancy.salary:
                    if hasattr(vacancy.salary, "salary_from"):
                        salary_from = vacancy.salary.salary_from
                        salary_to = vacancy.salary.salary_to
                        salary_currency = vacancy.salary.currency
                    elif isinstance(vacancy.salary, dict):
                        salary_from = vacancy.salary.get("from")
                        salary_to = vacancy.salary.get("to")
                        salary_currency = vacancy.salary.get("currency")
                    # Если salary - boolean или что-то другое, оставляем None

                area_str = str(vacancy.area) if vacancy.area else None
                published_date = self._normalize_published_date(vacancy.published_at)

                insert_data.append(
                    (
                        idx,
                        vacancy.id,
                        vacancy.name,
                        vacancy.url,
                        salary_from,
                        salary_to,
                        salary_currency,
                        vacancy.description,
                        vacancy.requirements,
                        vacancy.responsibilities,
                        experience_str,
                        employment_str,
                        schedule_str,
                        area_str,
                        vacancy.source,
                        published_date,
                        mapped_company_id,
                        employer_name,
                        employer_id,
                        dedup_key,
                    )
                )

            logger.info(
                f"После фильтрации по целевым компаниям: {len(insert_data)} из {len(vacancies)} вакансий (отфильтровано: {filtered_count})"
            )

            logger.info(f"Доступно ID-маппингов для сопоставления: {len(company_id_mapping)}")
            if not company_id_mapping:
                logger.warning("company_id_mapping пустой!")

            if not insert_data:
                return []

            # Bulk insert отфильтрованных данных
            from psycopg2.extras import execute_values

            execute_values(
                cursor,
                """INSERT INTO temp_processing_vacancies (
                    original_index, vacancy_id, title, url, salary_from, salary_to, salary_currency,
                    description, requirements, responsibilities, experience, employment, schedule,
                    area, source, published_at, company_id, employer_name, employer_id, dedup_key
                ) VALUES %s""",
                insert_data,
                template=None,
                page_size=1000,
            )

            # ДЕДУПЛИКАЦИЯ через SQL
            cursor.execute(
                """
                SELECT original_index
                FROM (
                    SELECT original_index,
                           ROW_NUMBER() OVER (
                               PARTITION BY dedup_key
                               ORDER BY original_index
                           ) as row_num
                    FROM temp_processing_vacancies
                ) ranked
                WHERE row_num = 1
                ORDER BY original_index
            """
            )

            unique_indices = [row[0] for row in cursor.fetchall()]

            # Применяем дополнительные фильтры если нужно
            where_conditions = []
            params = []

            if filters.get("salary_from"):
                where_conditions.append("(salary_from >= %s OR salary_to >= %s)")
                params.extend([filters["salary_from"], filters["salary_from"]])

            if filters.get("keywords"):
                keywords = filters["keywords"] if isinstance(filters["keywords"], list) else [filters["keywords"]]
                for keyword in keywords:
                    where_conditions.append("(LOWER(title) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s))")
                    keyword_param = f"%{keyword}%"
                    params.extend([keyword_param, keyword_param])

            if where_conditions:
                # Применяем дополнительные фильтры
                where_clause = " AND ".join(where_conditions)
                placeholders = ",".join(["%s"] * len(unique_indices))

                cursor.execute(
                    f"""
                    SELECT original_index
                    FROM temp_processing_vacancies
                    WHERE original_index IN ({placeholders}) AND {where_clause}
                    ORDER BY original_index
                """,
                    unique_indices + params,
                )

                unique_indices = [row[0] for row in cursor.fetchall()]

            # Формируем результат из исходных объектов
            result_vacancies = [vacancies[idx] for idx in unique_indices]

            logger.info(f"Финальный этап обработки: {len(insert_data)} -> {len(result_vacancies)} вакансий")

            duplicates_removed = len(insert_data) - len(result_vacancies)
            logger.info(f"SQL-обработка завершена: {len(vacancies)} -> {len(result_vacancies)} вакансий")
            logger.info(f"Отфильтровано по компаниям: {filtered_count}, дедуплицировано: {duplicates_removed}")

            connection.commit()
            logger.info(f"Возвращаем отфильтрованные вакансии: {len(result_vacancies)}")
            return result_vacancies

        except Exception as e:
            logger.error(f"Ошибка SQL-фильтрации и дедупликации: {e}")
            if not connection.closed:
                try:
                    connection.rollback()
                except Exception:
                    pass
            return vacancies  # Возвращаем исходный список при ошибке
        finally:
            if "cursor" in locals():
                cursor.close()
            connection.close()

    def _normalize_text(self, text: str) -> str:
        """
        Нормализует текст для дедупликации: приводит к нижнему регистру,
        удаляет лишние пробелы и специальные символы.

        Args:
            text: Исходный текст для нормализации

        Returns:
            str: Нормализованный текст
        """
        if not text:
            return ""

        import re

        # Приводим к нижнему регистру
        normalized = text.lower().strip()

        # Убираем лишние пробелы
        normalized = re.sub(r"\s+", " ", normalized)

        # Убираем специальные символы, оставляем только буквы, цифры и пробелы
        normalized = re.sub(r"[^\w\s]", "", normalized, flags=re.UNICODE)

        return normalized.strip()

    def _normalize_published_date(self, published_at: Any) -> Optional[datetime]:
        """
        Нормализует дату published_at, пытаясь преобразовать ее в объект datetime.
        Поддерживает строки в формате ISO и объекты datetime.
        Если дата не задана или пустая, используется текущая дата.
        """
        if not published_at or (isinstance(published_at, str) and not published_at.strip()):
            # Если дата не указана, используем текущую дату
            return datetime.now()

        if isinstance(published_at, datetime):
            return published_at

        if isinstance(published_at, str):
            try:
                # Пытаемся парсить ISO формат даты
                if "T" in published_at:
                    # Формат: 2025-08-25T18:47:30+0300
                    if "+" in published_at:
                        # Заменяем +0300 на +03:00 для совместимости с Python
                        date_str = published_at
                        if date_str.endswith("+0300"):
                            date_str = date_str.replace("+0300", "+03:00")
                        elif date_str.endswith("+0000"):
                            date_str = date_str.replace("+0000", "+00:00")
                        return datetime.fromisoformat(date_str)
                    else:
                        return datetime.fromisoformat(published_at)
                else:
                    return datetime.fromisoformat(published_at)
            except (ValueError, TypeError) as e:
                logger.warning(f"Не удалось распарсить дату {published_at}: {e}")
                return None
        else:
            # Пытаемся преобразовать в datetime, если это числовой тип или другой формат
            try:
                return datetime.fromisoformat(str(published_at))
            except (ValueError, TypeError):
                logger.warning(f"Не удалось распознать формат даты: {published_at}")
                return None
