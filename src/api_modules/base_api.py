"""
Базовый модуль для работы с API поиска вакансий.

Содержит абстрактный базовый класс, который определяет единый интерфейс
для всех API источников вакансий (HH.ru, SuperJob и т.д.).
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List
import os

logger = logging.getLogger(__name__)


class BaseJobAPI(ABC):
    """
    Базовый абстрактный класс для всех API поиска вакансий.

    Определяет единый интерфейс для работы с различными источниками вакансий,
    включая методы для получения, валидации вакансий.
    """

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение списка вакансий из источника по поисковому запросу.

        Args:
            search_query: Поисковый запрос для поиска вакансий
            **kwargs: Дополнительные параметры поиска (зарплата, опыт и т.д.)

        Returns:
            List[Dict]: Список найденных вакансий в формате словарей
        """

    @abstractmethod
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """
        Валидация структуры данных вакансии.

        Проверяет, что вакансия содержит все необходимые поля
        и соответствует ожидаемой структуре данных.

        Args:
            vacancy: Словарь с данными вакансии для валидации

        Returns:
            bool: True если структура валидна, False иначе
        """

    def _create_dedup_key(self, vacancy: Dict, source: str) -> tuple:
        """
        Создание универсального ключа дедупликации для любого источника

        Args:
            vacancy: Словарь с данными вакансии
            source: Источник вакансии ('hh' или 'sj')

        Returns:
            tuple: Ключ для дедупликации (название, компания, зарплата)
        """
        # Универсальное получение названия вакансии
        if source == "hh":
            title = vacancy.get("name", "").lower().strip()
            company = vacancy.get("employer", {}).get("name", "").lower().strip()

            # Обработка зарплаты для HH.ru
            salary_key = ""
            if "salary" in vacancy and vacancy["salary"]:
                salary = vacancy["salary"]
                salary_from = salary.get("from", 0) or 0
                salary_to = salary.get("to", 0) or 0
                salary_key = f"{salary_from}-{salary_to}"

        elif source == "sj":
            title = vacancy.get("profession", "").lower().strip()
            company = vacancy.get("firm_name", "").lower().strip()

            # Обработка зарплаты для SuperJob
            salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"
        else:
            # Универсальная обработка для неизвестных источников
            title = (vacancy.get("title") or vacancy.get("name") or vacancy.get("profession") or "").lower().strip()

            company = (vacancy.get("employer", {}).get("name") or vacancy.get("firm_name") or "").lower().strip()

            salary_key = "0-0"  # Значение по умолчанию для неизвестных источников

        return title, company, salary_key

    def _deduplicate_vacancies(self, vacancies: List[Dict], source: str = None) -> List[Dict]:
        """
        Удаление дублирующихся вакансий с одновременной фильтрацией по целевым компаниям.
        Использует временную таблицу PostgreSQL для эффективного анализа.

        Args:
            vacancies: Список вакансий для дедупликации
            source: Источник данных (для логирования)

        Returns:
            List[Dict]: Список уникальных вакансий от целевых компаний
        """
        if not vacancies:
            return []

        print("Выполняется дедупликация и фильтрация по целевым компаниям...")
        logger.info(f"Начинаем SQL-дедупликацию с фильтрацией по целевым компаниям для {len(vacancies)} вакансий из источника {source}")

        try:
            # Получаем список целевых компаний
            from src.config.target_companies import TargetCompanies
            TARGET_COMPANIES = TargetCompanies.get_all_companies()

            # Создаем расширенный список альтернативных названий
            target_company_patterns = set()
            for company in TARGET_COMPANIES:
                name = company.name.lower()
                target_company_patterns.add(name)

                # Добавляем известные альтернативы
                alternatives = {
                    "яндекс": ["яндекс"],
                    "тинькофф": ["т-банк", "tinkoff", "тинькофф"],
                    "сбер": ["сбербанк", "сбер", "sberbank"],
                    "wildberries": ["wildberries", "wb"],
                    "ozon": ["ozon"],
                    "vk (вконтакте)": ["vk", "вконтакте", "вк"],
                    "kaspersky": ["kaspersky", "лаборатория касперского"],
                    "авито": ["авито", "avito"],
                    "x5 retail group": ["x5", "x5 retail group"],
                    "ростелеком": ["ростелеком", "rostelecom"],
                    "альфа-банк": ["альфа-банк", "alfa-bank"],
                    "jetbrains": ["jetbrains"],
                    "2gis": ["2гис", "2gis"],
                    "skyeng": ["skyeng"],
                    "delivery club": ["delivery club"]
                }

                if name in alternatives:
                    target_company_patterns.update(alternatives[name])

            # Используем PostgresSaver для SQL-операций
            from src.storage.postgres_saver import PostgresSaver
            postgres_saver = PostgresSaver()

            with postgres_saver._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу для анализа
                    cursor.execute("""
                        CREATE TEMP TABLE temp_dedup_analysis (
                            original_index INTEGER,
                            vacancy_id VARCHAR(50),
                            title_normalized VARCHAR(500),
                            company_normalized VARCHAR(500),
                            salary_key VARCHAR(50),
                            area_normalized VARCHAR(200),
                            dedup_key VARCHAR(1000),
                            source VARCHAR(20),
                            is_target_company BOOLEAN DEFAULT FALSE
                        ) ON COMMIT DROP
                    """)

                    # Подготавливаем данные для анализа
                    analysis_data = []
                    for idx, vacancy in enumerate(vacancies):
                        # Нормализуем данные для сравнения
                        title = self._normalize_text(vacancy.get("name", vacancy.get("profession", "")))

                        # Извлекаем название компании
                        company = ""
                        if "employer" in vacancy and vacancy["employer"]:
                            company = self._normalize_text(vacancy["employer"].get("name", ""))
                        elif "firm_name" in vacancy:
                            company = self._normalize_text(vacancy.get("firm_name", ""))

                        # Проверяем, является ли компания целевой
                        is_target = False
                        if company:
                            company_lower = company.lower()
                            # Проверяем точное совпадение или частичное
                            for pattern in target_company_patterns:
                                if pattern == company_lower or pattern in company_lower or company_lower in pattern:
                                    is_target = True
                                    break

                        # Нормализуем зарплату
                        salary_key = self._get_salary_key(vacancy)

                        # Нормализуем регион
                        area = ""
                        if "area" in vacancy and vacancy["area"]:
                            area = self._normalize_text(vacancy["area"].get("name", ""))
                        elif "town" in vacancy:
                            area = self._normalize_text(vacancy.get("town", {}).get("title", ""))

                        # Создаем ключ дедупликации
                        dedup_key = f"{title}|{company}|{salary_key}|{area}"

                        analysis_data.append((
                            idx,
                            str(vacancy.get("id", "")),
                            title,
                            company,
                            salary_key,
                            area,
                            dedup_key,
                            source or "unknown",
                            is_target
                        ))

                    # Bulk insert данных для анализа
                    from psycopg2.extras import execute_values
                    execute_values(
                        cursor,
                        """INSERT INTO temp_dedup_analysis (
                            original_index, vacancy_id, title_normalized, company_normalized,
                            salary_key, area_normalized, dedup_key, source, is_target_company
                        ) VALUES %s""",
                        analysis_data,
                        template=None,
                        page_size=1000
                    )

                    # SQL-запрос для поиска уникальных вакансий от целевых компаний
                    cursor.execute("""
                        SELECT original_index
                        FROM (
                            SELECT 
                                original_index,
                                ROW_NUMBER() OVER (
                                    PARTITION BY dedup_key 
                                    ORDER BY original_index
                                ) as row_num
                            FROM temp_dedup_analysis
                            WHERE is_target_company = TRUE
                        ) ranked
                        WHERE row_num = 1
                        ORDER BY original_index
                    """)

                    unique_indices = [row[0] for row in cursor.fetchall()]

                    # Получаем подробную статистику
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_vacancies,
                            COUNT(CASE WHEN is_target_company THEN 1 END) as target_company_vacancies,
                            COUNT(DISTINCT CASE WHEN is_target_company THEN dedup_key END) as unique_target_vacancies,
                            COUNT(CASE WHEN is_target_company THEN 1 END) - 
                            COUNT(DISTINCT CASE WHEN is_target_company THEN dedup_key END) as target_duplicates,
                            COUNT(DISTINCT company_normalized) as unique_companies,
                            COUNT(DISTINCT CASE WHEN is_target_company THEN company_normalized END) as target_companies_found
                        FROM temp_dedup_analysis
                    """)

                    stats = cursor.fetchone()
                    total_count = stats[0]
                    target_count = stats[1]
                    unique_target_count = stats[2]
                    target_duplicates = stats[3]
                    unique_companies = stats[4]
                    target_companies_found = stats[5]

                    # Получаем список найденных целевых компаний для логирования
                    cursor.execute("""
                        SELECT DISTINCT company_normalized
                        FROM temp_dedup_analysis
                        WHERE is_target_company = TRUE AND company_normalized != ''
                        ORDER BY company_normalized
                    """)
                    found_companies = [row[0] for row in cursor.fetchall()]

                    # Формируем результат из уникальных вакансий целевых компаний
                    unique_vacancies = [vacancies[idx] for idx in unique_indices]

                    logger.info(f"SQL-дедупликация с фильтрацией завершена:")
                    logger.info(f"  Всего вакансий: {total_count}")
                    logger.info(f"  От целевых компаний: {target_count}")
                    logger.info(f"  Уникальных от целевых: {unique_target_count}")
                    logger.info(f"  Удалено дубликатов: {target_duplicates}")
                    logger.info(f"  Найдено целевых компаний: {target_companies_found}")
                    if found_companies:
                        logger.info(f"  Компании: {', '.join(found_companies[:5])}{'...' if len(found_companies) > 5 else ''}")

                    return unique_vacancies

        except Exception as e:
            logger.error(f"Ошибка при SQL-дедупликации с фильтрацией: {e}")
            # Fallback на простую фильтрацию
            return self._simple_deduplicate_with_filter_fallback(vacancies, source)

    def _normalize_text(self, text: str) -> str:
        """
        Нормализация текста для сравнения

        Args:
            text: Исходный текст

        Returns:
            str: Нормализованный текст
        """
        if not text:
            return ""
        return text.lower().strip()

    def _get_salary_key(self, vacancy: Dict) -> str:
        """
        Получение ключа зарплаты для дедупликации

        Args:
            vacancy: Данные вакансии

        Returns:
            str: Ключ зарплаты в формате "от-до"
        """
        if "salary" in vacancy and vacancy["salary"]:
            salary = vacancy["salary"]
            salary_from = salary.get("from", 0) or 0
            salary_to = salary.get("to", 0) or 0
            return f"{salary_from}-{salary_to}"
        elif "payment_from" in vacancy:
            return f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"
        else:
            return "0-0"

    def _simple_deduplicate_with_filter_fallback(self, vacancies: List[Dict], source: str = None) -> List[Dict]:
        """
        Простая дедупликация с фильтрацией как fallback при ошибках SQL
        """
        from src.config.target_companies import TargetCompanies
        TARGET_COMPANIES = TargetCompanies.get_all_companies()
        target_company_names = [company.name.lower() for company in TARGET_COMPANIES]

        seen = set()
        unique_vacancies = []
        target_vacancies = []

        # Сначала фильтруем по целевым компаниям
        for vacancy in vacancies:
            company = ""
            if "employer" in vacancy and vacancy["employer"]:
                company = vacancy["employer"].get("name", "").lower()
            elif "firm_name" in vacancy:
                company = vacancy.get("firm_name", "").lower()

            # Проверяем, является ли компания целевой
            is_target = False
            for target_name in target_company_names:
                if target_name in company or company in target_name:
                    is_target = True
                    break

            if is_target:
                target_vacancies.append(vacancy)

        # Затем дедуплицируем целевые вакансии
        for vacancy in target_vacancies:
            title = self._normalize_text(vacancy.get("name", vacancy.get("profession", "")))

            company = ""
            if "employer" in vacancy and vacancy["employer"]:
                company = self._normalize_text(vacancy["employer"].get("name", ""))
            elif "firm_name" in vacancy:
                company = self._normalize_text(vacancy.get("firm_name", ""))

            salary_key = self._get_salary_key(vacancy)

            dedup_key = (title, company, salary_key)

            if dedup_key not in seen:
                seen.add(dedup_key)
                unique_vacancies.append(vacancy)

        duplicates_found = len(target_vacancies) - len(unique_vacancies)
        logger.info(f"Fallback дедупликация с фильтрацией: {len(vacancies)} -> {len(target_vacancies)} целевых -> {len(unique_vacancies)} уникальных (удалено {duplicates_found} дубликатов)")

        return unique_vacancies

    def clear_cache(self, source: str) -> None:
        """
        Очистка кэша для конкретного источника

        Args:
            source: Название источника (hh, sj)
        """
        try:
            cache_dir = f"data/cache/{source}"
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                logger.info(f"Кэш {source} очищен")
            else:
                # Создаем папку кэша если её нет
                os.makedirs(cache_dir, exist_ok=True)
                logger.info(f"Создана папка кэша {cache_dir}")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша {source}: {e}")
            raise