"""
Класс DBManager для работы с данными в БД PostgreSQL

Реализует специфические методы согласно требованиям проекта по работе с БД.
Использует библиотеку psycopg2 для подключения к PostgreSQL.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import psycopg2
from psycopg2.extras import RealDictCursor

from src.config.db_config import DatabaseConfig

logger = logging.getLogger(__name__)


class DBManager:
    """
    Класс для работы с данными в БД PostgreSQL согласно требованиям проекта

    Предоставляет методы согласно требованиям проекта:
    - get_companies_and_vacancies_count() — получает список всех компаний и количество вакансий у каждой компании
    - get_all_vacancies() — получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию
    - get_avg_salary() — получает среднюю зарплату по вакансиям
    - get_vacancies_with_higher_salary() — получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
    - get_vacancies_with_keyword() — получает список всех вакансий, в названии которых содержатся переданные слова

    Использует библиотеку psycopg2 и SQL-запросы для работы с PostgreSQL.
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
        """
        # SQL для создания таблиц с явным указанием кодировки
        create_companies_table = """
        -- Создание таблицы компаний для хранения информации о работодателях
        -- Используется IF NOT EXISTS для безопасного создания таблицы
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,                          -- Автоинкрементный первичный ключ
            company_id VARCHAR(255) UNIQUE NOT NULL,        -- Уникальный идентификатор компании из API
            name VARCHAR(255) NOT NULL,                     -- Название компании
            description TEXT,                               -- Описание компании
            hh_id VARCHAR(255),                            -- ID компании в системе HeadHunter
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Время создания записи
        );
        """

        create_vacancies_table = """
        -- Создание таблицы вакансий для хранения всей информации о вакансиях
        -- Связана с таблицей companies через внешний ключ company_id
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,                          -- Автоинкрементный первичный ключ
            vacancy_id VARCHAR(255) UNIQUE NOT NULL,        -- Уникальный идентификатор вакансии из API
            title TEXT NOT NULL,                           -- Название вакансии (обязательное поле)
            url TEXT,                                      -- Ссылка на вакансию
            salary_from INTEGER,                           -- Минимальная зарплата (может быть NULL)
            salary_to INTEGER,                             -- Максимальная зарплата (может быть NULL)
            salary_currency VARCHAR(10),                   -- Валюта зарплаты (RUR, USD, EUR и т.д.)
            description TEXT,                              -- Полное описание вакансии
            requirements TEXT,                             -- Требования к кандидату
            responsibilities TEXT,                         -- Обязанности на позиции
            experience VARCHAR(100),                       -- Требуемый опыт работы
            employment VARCHAR(100),                       -- Тип занятости (полная, частичная и т.д.)
            schedule VARCHAR(100),                         -- График работы (полный день, удаленка и т.д.)
            employer TEXT,                                 -- Название работодателя (дублирование для совместимости)
            area TEXT,                                     -- Регион/город размещения вакансии
            source VARCHAR(50),                            -- Источник данных (hh.ru, superjob.ru)
            published_at TIMESTAMP,                        -- Дата публикации вакансии
            company_id VARCHAR(255),                       -- Связь с таблицей компаний (внешний ключ)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время создания записи в БД
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время последнего обновления записи
            -- Внешний ключ для связи с таблицей компаний
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Устанавливаем кодировку сессии
                    cursor.execute("SET client_encoding TO 'UTF8'")

                    # Сначала создаем таблицу компаний
                    cursor.execute(create_companies_table)
                    logger.info("Таблица компаний создана успешно")

                    # Затем создаем таблицу вакансий с FK
                    cursor.execute(create_vacancies_table)
                    logger.info("Таблица вакансий создана успешно")

        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

    def populate_companies_table(self):
        """
        Заполняет таблицу компаний данными из конфигурации
        """
        from src.config.target_companies import TARGET_COMPANIES

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Проверяем, есть ли уже данные
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    count = cursor.fetchone()[0]

                    if count == 0:
                        # Вставляем данные о компаниях
                        insert_sql = """
                        INSERT INTO companies (company_id, name, description, hh_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (company_id) DO NOTHING
                        """

                        for company in TARGET_COMPANIES:
                            cursor.execute(insert_sql, (
                                company["hh_id"],
                                company["name"],
                                company["description"],
                                company["hh_id"]
                            ))

                        logger.info(f"Добавлено {len(TARGET_COMPANIES)} компаний в базу данных")
                    else:
                        logger.info(f"Таблица компаний уже содержит {count} записей")

        except Exception as e:
            logger.error(f"Ошибка при заполнении таблицы компаний: {e}")
            raise



    def get_target_companies_analysis(self) -> List[Tuple[str, int]]:
        """
        Получает анализ ТОЛЬКО по целевым компаниям
        Этот метод специально предназначен для демонстрации п.10

        Returns:
            List[Tuple[str, int]]: Список кортежей (название_целевой_компании, количество_вакансий)
        """
        from src.config.target_companies import TARGET_COMPANIES

        try:
            # Сначала получаем все данные
            all_data = self.get_companies_and_vacancies_count()

            # Если нет данных, возвращаем все целевые компании с нулями
            if not all_data:
                return [(company['name'], 0) for company in TARGET_COMPANIES]

            return all_data  # Метод уже возвращает данные по целевым компаниям

        except Exception as e:
            logger.error(f"Ошибка при анализе целевых компаний: {e}")
            # В случае ошибки возвращаем все целевые компании с нулями
            return [(company['name'], 0) for company in TARGET_COMPANIES]

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании
        ВАЖНО: Метод фильтрует результаты по целевым компаниям из конфигурации

        Returns:
            List[Tuple[str, int]]: Список кортежей (название_компании, количество_вакансий)
        """
        from src.config.target_companies import TARGET_COMPANIES

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
                    LEFT JOIN vacancies v ON c.company_id = v.company_id  -- Левое соединение с таблицей вакансий
                    GROUP BY c.name, c.company_id                  -- Группировка по компании для агрегации COUNT()
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
                        company_name = target_company['name']

                        # Fallback SQL-запрос для поиска вакансий по названию компании в поле employer
                        # Используется когда нет связанных данных через внешний ключ company_id
                        fallback_query = """
                        -- Подсчет вакансий по частичному совпадению названия компании
                        -- Использует LIKE для нечеткого поиска и LOWER() для регистронезависимого поиска
                        SELECT COUNT(*) as vacancy_count              -- Количество найденных вакансий
                        FROM vacancies                               -- Таблица вакансий
                        WHERE LOWER(employer) LIKE LOWER(%s)         -- Поиск по полю employer с игнорированием регистра
                        """

                        cursor.execute(fallback_query, (f"%{company_name}%",))
                        count_result = cursor.fetchone()
                        vacancy_count = count_result[0] if count_result else 0

                        # Дополнительные проверки для известных альтернативных названий
                        if vacancy_count == 0:
                            # Альтернативные названия компаний
                            alternatives = {
                                "Тинькофф": ["т-банк", "tinkoff"],
                                "СБЕР": ["сбербанк", "сбер"],
                                "VK (ВКонтакте)": ["vk", "вконтакте"],
                                "OZON": ["ozon"],
                                "Wildberries": ["wildberries"]
                            }

                            if company_name in alternatives:
                                for alt_name in alternatives[company_name]:
                                    cursor.execute(fallback_query, (f"%{alt_name}%",))
                                    count_result = cursor.fetchone()
                                    if count_result and count_result[0] > 0:
                                        vacancy_count = count_result[0]
                                        break

                        company_results.append((company_name, vacancy_count))

                    # Сортируем по количеству вакансий (убывание), затем по названию
                    company_results.sort(key=lambda x: (-x[1], x[0]))
                    return company_results

        except Exception as e:
            logger.error(f"Ошибка при получении списка компаний и количества вакансий: {e}")
            # В случае ошибки возвращаем все целевые компании с нулями
            return [(company['name'], 0) for company in TARGET_COMPANIES]

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

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию
        Использует SQL-запрос с CASE для форматирования зарплаты

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о вакансиях
        """
        query = """
        -- Получение списка всех вакансий с названием компании, зарплатой и ссылкой
        -- Использует LEFT JOIN для связи вакансий с компаниями и CASE для форматирования данных
        SELECT
            v.title,                                       -- Название вакансии
            -- CASE для определения названия компании с приоритетом:
            -- 1. Название из справочника companies (если есть связь по company_id)
            -- 2. Название из поля employer вакансии (если заполнено)  
            -- 3. Значение по умолчанию "Неизвестная компания"
            CASE
                WHEN c.name IS NOT NULL THEN c.name                           -- Приоритет: справочник компаний
                WHEN v.employer IS NOT NULL AND v.employer != '' THEN v.employer  -- Fallback: поле employer
                ELSE 'Неизвестная компания'                                   -- По умолчанию
            END as company_name,
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
            v.employer,                                    -- Оригинальное поле employer для совместимости
            c.company_id                                   -- ID компании из справочника
        FROM vacancies v                                   -- Основная таблица вакансий
        LEFT JOIN companies c ON v.company_id = c.company_id  -- Левое соединение для получения названия компании
        -- Сортировка по названию компании, затем по названию вакансии
        ORDER BY
            CASE
                WHEN c.name IS NOT NULL THEN c.name        -- Сортировка по названию из справочника
                WHEN v.employer IS NOT NULL AND v.employer != '' THEN v.employer  -- или по полю employer
                ELSE 'Неизвестная компания'               -- или по значению по умолчанию
            END,
            v.title                                        -- Вторичная сортировка по названию вакансии
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()

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
        # Сначала получаем среднюю зарплату
        avg_salary = self.get_avg_salary()

        if avg_salary is None:
            logger.warning("Не удалось рассчитать среднюю зарплату")
            return []

        # SQL-запрос для получения вакансий с зарплатой выше средней
        query = """
        SELECT
            v.title,
            COALESCE(c.name, v.employer, 'Неизвестная компания') as company_name,
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
            v.vacancy_id,
            v.employer
        FROM vacancies v
        LEFT JOIN companies c ON v.company_id = c.company_id
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
            CASE
                WHEN c.name IS NOT NULL THEN c.name        -- Сортировка по названию из справочника
                WHEN v.employer IS NOT NULL AND v.employer != '' THEN v.employer  -- или по полю employer
                ELSE 'Неизвестная компания'               -- или по значению по умолчанию
            END,
            v.title                                        -- Вторичная сортировка по названию вакансии
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (avg_salary,))
                    results = cursor.fetchall()

                    # Преобразуем результаты в список словарей
                    columns = ['title', 'company_name', 'salary_info', 'url', 'calculated_salary', 'vacancy_id', 'employer']
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

        # SQL-запрос для поиска вакансий по ключевому слову в названии
        query = """
        SELECT
            v.title,
            COALESCE(c.name, v.employer, 'Неизвестная компания') as company_name,
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
            v.vacancy_id,
            v.employer
        FROM vacancies v
        LEFT JOIN companies c ON v.company_id = c.company_id
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
                    columns = ['title', 'company_name', 'salary_info', 'url', 'description', 'vacancy_id', 'employer']
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
                            COUNT(DISTINCT CASE WHEN employer IS NOT NULL AND employer != '' THEN employer END) as unique_employers,
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
                        SELECT employer, COUNT(*) as vacancy_count
                        FROM vacancies
                        WHERE employer IS NOT NULL AND employer != ''
                        GROUP BY employer
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
                    return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False

    def filter_companies_by_targets(self, api_companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует компании из API по целевым компаниям используя SQL-запрос

        Args:
            api_companies: Список компаний из API

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список целевых компаний
        """
        from src.config.target_companies import TARGET_COMPANIES

        if not api_companies:
            return []

        # Создаем список названий целевых компаний для SQL-поиска
        target_company_names = [company['name'].lower() for company in TARGET_COMPANIES]

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