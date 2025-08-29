"""
Базовый модуль для работы с API поиска вакансий.

Содержит абстрактный базовый класс, который определяет единый интерфейс
для всех API источников вакансий (HH.ru, SuperJob и т.д.).
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List

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
        Удаление дублирующихся вакансий БЕЗ фильтрации по целевым компаниям.
        Фильтрация должна происходить на более раннем этапе.

        Args:
            vacancies: Список вакансий для дедупликации
            source: Источник данных (для логирования)

        Returns:
            List[Dict]: Список уникальных вакансий
        """
        if not vacancies:
            return []

        print("Выполняется дедупликация вакансий...")
        logger.info(f"Начинаем дедупликацию для {len(vacancies)} вакансий из источника {source}")

        try:
            # Используем PostgresSaver для SQL-операций
            from src.storage.postgres_saver import PostgresSaver

            postgres_saver = PostgresSaver()

            with postgres_saver._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу для анализа
                    cursor.execute(
                        """
                        CREATE TEMP TABLE temp_dedup_analysis (
                            original_index INTEGER,
                            vacancy_id VARCHAR(50),
                            title_normalized VARCHAR(500),
                            company_normalized VARCHAR(500),
                            salary_key VARCHAR(50),
                            area_normalized VARCHAR(200),
                            dedup_key VARCHAR(1000),
                            source VARCHAR(20)
                        ) ON COMMIT DROP
                    """
                    )

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

                        analysis_data.append(
                            (
                                idx,
                                str(vacancy.get("id", "")),
                                title,
                                company,
                                salary_key,
                                area,
                                dedup_key,
                                source or "unknown",
                            )
                        )

                    # Вставляем данные
                    insert_query = """
                        INSERT INTO temp_dedup_analysis (
                            original_index, vacancy_id, title_normalized, company_normalized,
                            salary_key, area_normalized, dedup_key, source
                        ) VALUES %s
                    """

                    from psycopg2.extras import execute_values

                    execute_values(cursor, insert_query, analysis_data, template=None, page_size=1000)

                    # Получаем только уникальные записи
                    cursor.execute(
                        """
                        SELECT original_index
                        FROM (
                            SELECT
                                original_index,
                                ROW_NUMBER() OVER (
                                    PARTITION BY dedup_key
                                    ORDER BY original_index
                                ) as row_num
                            FROM temp_dedup_analysis
                        ) ranked
                        WHERE row_num = 1
                        ORDER BY original_index
                    """
                    )

                    unique_indices = [row[0] for row in cursor.fetchall()]

                    # Формируем результат из уникальных вакансий
                    unique_vacancies = [vacancies[idx] for idx in unique_indices]

                    duplicates_removed = len(vacancies) - len(unique_vacancies)
                    logger.info(f"Дедупликация завершена: {len(vacancies)} -> {len(unique_vacancies)} вакансий (удалено {duplicates_removed} дублей)")

                    return unique_vacancies

        except Exception as e:
            logger.error(f"Ошибка при дедупликации: {e}")
            logger.warning("Используем простую дедупликацию как fallback")
            
            # Простая дедупликация по ID
            seen = set()
            unique_vacancies = []
            for vacancy in vacancies:
                vacancy_id = vacancy.get("id") or vacancy.get("vacancy_id")
                if vacancy_id and vacancy_id not in seen:
                    seen.add(vacancy_id)
                    unique_vacancies.append(vacancy)
            
            return unique_vacancies

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
