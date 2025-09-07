"""
Сервис SQL-дедупликации вакансий

Реализует дедупликацию через SQL без фильтрации.
Принцип Single Responsibility - только дедупликация.
"""

import logging
from typing import List

from src.storage.abstract_db_manager import AbstractDBManager
from src.vacancies.models import Vacancy

from .abstract_filter_service import AbstractDeduplicationService

logger = logging.getLogger(__name__)


class SQLDeduplicationService(AbstractDeduplicationService):
    """
    Сервис SQL-дедупликации вакансий
    Принцип Single Responsibility - только дедупликация
    """

    def __init__(self, db_manager: AbstractDBManager):
        """
        Инициализация сервиса

        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager

    def deduplicate_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Выполняет дедупликацию вакансий через SQL

        Args:
            vacancies: Список вакансий для дедупликации

        Returns:
            List[Vacancy]: Уникальные вакансии
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем SQL-дедупликацию: {len(vacancies)} вакансий")

        try:
            with self.db_manager._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу для дедупликации
                    self._create_temp_table(cursor, vacancies)

                    # Выполняем SQL запрос для поиска уникальных вакансий
                    unique_vacancy_ids = self._execute_deduplication_query(cursor)

                    # Возвращаем уникальные вакансии
                    return self._build_unique_vacancies(vacancies, unique_vacancy_ids)

        except Exception as e:
            logger.error(f"Ошибка SQL-дедупликации: {e}")
            # В случае ошибки возвращаем оригинальный список
            return vacancies

    def _create_temp_table(self, cursor, vacancies: List[Vacancy]) -> None:
        """Создает временную таблицу для дедупликации"""
        cursor.execute(
            """
            CREATE TEMP TABLE temp_deduplication (
                vacancy_id VARCHAR(255) PRIMARY KEY,
                title_normalized TEXT,
                employer_normalized TEXT,
                employer_id VARCHAR(50),
                original_index INTEGER
            )
        """
        )

        # Подготавливаем данные для вставки
        dedup_data = []
        for idx, vacancy in enumerate(vacancies):
            # Нормализуем данные для дедупликации
            title_normalized = self._normalize_text(vacancy.title or "")

            # Извлекаем и нормализуем имя работодателя
            employer_name = "неизвестный"
            employer_id = None
            
            if vacancy.employer:
                if hasattr(vacancy.employer, "get_name"):
                    employer_name = vacancy.employer.get_name()
                elif hasattr(vacancy.employer, "name"):
                    employer_name = vacancy.employer.name
                elif isinstance(vacancy.employer, dict):
                    employer_name = vacancy.employer.get("name", "неизвестный")
                else:
                    employer_name = str(vacancy.employer)
                    
                # Извлекаем employer.id (hh_id или sj_id)
                if hasattr(vacancy.employer, "get_id"):
                    employer_id = vacancy.employer.get_id()
                elif hasattr(vacancy.employer, "id"):
                    employer_id = vacancy.employer.id
                elif isinstance(vacancy.employer, dict):
                    employer_id = vacancy.employer.get("id")

            employer_normalized = self._normalize_text(employer_name)
            
            dedup_data.append((vacancy.vacancy_id, title_normalized, employer_normalized, employer_id, idx))

        # Вставляем данные
        cursor.executemany(
            """
            INSERT INTO temp_deduplication 
            (vacancy_id, title_normalized, employer_normalized, employer_id, original_index)
            VALUES (%s, %s, %s, %s, %s)
        """,
            dedup_data,
        )

        logger.info(f"Создана временная таблица для дедупликации: {len(dedup_data)} записей")

    def _execute_deduplication_query(self, cursor) -> List[str]:
        """Выполняет SQL запрос для поиска уникальных вакансий"""

        query = """
        WITH ranked_vacancies AS (
            SELECT 
                vacancy_id,
                original_index,
                ROW_NUMBER() OVER (
                    PARTITION BY title_normalized, employer_normalized, COALESCE(employer_id, 'unknown')
                    ORDER BY original_index
                ) as row_num
            FROM temp_deduplication
        )
        SELECT vacancy_id 
        FROM ranked_vacancies 
        WHERE row_num = 1
        ORDER BY original_index
        """

        cursor.execute(query)
        results = cursor.fetchall()

        unique_ids = [row[0] for row in results]

        duplicates_count = (
            len([row for row in cursor.execute("SELECT COUNT(*) FROM temp_deduplication").fetchall()[0]])
            - len(unique_ids)
            if cursor.rowcount
            else 0
        )
        logger.info(
            f"SQL-дедупликация: найдено {len(unique_ids)} уникальных вакансий, удалено {duplicates_count} дубликатов"
        )

        return unique_ids

    def _build_unique_vacancies(self, original_vacancies: List[Vacancy], unique_ids: List[str]) -> List[Vacancy]:
        """Строит итоговый список уникальных вакансий"""
        vacancy_map = {v.vacancy_id: v for v in original_vacancies}

        unique_vacancies = []
        for vacancy_id in unique_ids:
            if vacancy_id in vacancy_map:
                unique_vacancies.append(vacancy_map[vacancy_id])

        logger.info(f"Дедупликация завершена: {len(original_vacancies)} -> {len(unique_vacancies)} вакансий")
        return unique_vacancies

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Нормализует текст для сравнения при дедупликации

        Args:
            text: Исходный текст

        Returns:
            str: Нормализованный текст
        """
        if not text:
            return ""

        import re

        # Приводим к нижнему регистру, удаляем лишние пробелы
        normalized = re.sub(r"\s+", " ", text.lower().strip())
        # Удаляем специальные символы, оставляем буквы, цифры и пробелы
        normalized = re.sub(r"[^\w\sа-яё]", " ", normalized)
        return re.sub(r"\s+", " ", normalized).strip()
