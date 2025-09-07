"""Сервис SQL-дедупликации вакансий с использованием временных таблиц PostgreSQL.

Этот модуль предоставляет высокопроизводительный механизм дедупликации вакансий
с использованием SQL-запросов и временных таблиц. Поддерживает межплатформенную 
дедупликацию с приоритетом HeadHunter над SuperJob.

Features:
    - Создание временных таблиц в PostgreSQL для изоляции операций
    - Нормализация данных для точного сравнения
    - Приоритизация источников (HH > SJ > другие)
    - Группировка по: название + компания + зарплата + город
    - Автоматическая очистка временных таблиц

Classes:
    SQLDeduplicationService: Основной сервис дедупликации
"""

import logging
from typing import Any, List

from src.storage.abstract_db_manager import AbstractDBManager
from src.vacancies.models import Vacancy

from .abstract_filter_service import AbstractDeduplicationService

logger = logging.getLogger(__name__)


class SQLDeduplicationService(AbstractDeduplicationService):
    """Сервис SQL-дедупликации вакансий с межплатформенным приоритетом.
    
    Реализует высокопроизводительную дедупликацию через SQL с использованием 
    временных таблиц PostgreSQL. Поддерживает приоритизацию источников для
    межплатформенной дедупликации.
    
    Attributes:
        db_manager: Менеджер базы данных для выполнения SQL операций.
    """

    def __init__(self, db_manager: AbstractDBManager) -> None:
        """Инициализация сервиса дедупликации.

        Args:
            db_manager: Менеджер базы данных для выполнения SQL операций.
        """
        self.db_manager = db_manager

    def deduplicate_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """Выполняет межплатформенную дедупликацию вакансий через SQL.

        Создает временную таблицу в PostgreSQL, нормализует данные вакансий
        и применяет алгоритм дедупликации с приоритетом HeadHunter над SuperJob.

        Args:
            vacancies: Список вакансий для дедупликации.

        Returns:
            Список уникальных вакансий с применением межплатформенного приоритета.
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем SQL-дедупликацию: {len(vacancies)} вакансий")

        try:
            conn = self.db_manager._get_connection()
            cursor = conn.cursor()
            
            try:
                # Создаем временную таблицу для дедупликации
                self._create_temp_table(cursor, vacancies)

                # Выполняем SQL запрос для поиска уникальных вакансий
                unique_vacancy_ids = self._execute_deduplication_query(cursor)

                # Возвращаем уникальные вакансии
                return self._build_unique_vacancies(vacancies, unique_vacancy_ids)
            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            logger.error(f"Ошибка SQL-дедупликации: {e}")
            # В случае ошибки возвращаем оригинальный список
            return vacancies

    def _create_temp_table(self, cursor: Any, vacancies: List[Vacancy]) -> None:
        """Создает временную таблицу PostgreSQL для дедупликации.
        
        Создает таблицу temp_deduplication с нормализованными данными вакансий
        включая приоритеты источников для межплатформенной дедупликации.
        
        Args:
            cursor: Курсор базы данных PostgreSQL.
            vacancies: Список вакансий для обработки.
        """
        cursor.execute(
            """
            CREATE TEMP TABLE temp_deduplication (
                vacancy_id VARCHAR(255) PRIMARY KEY,
                title_normalized TEXT,
                employer_normalized TEXT,
                employer_id VARCHAR(50),
                salary_normalized TEXT,
                area_normalized TEXT,
                source_priority INTEGER,
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
            
            # Извлекаем и нормализуем зарплату
            salary_normalized = "не_указана"
            if vacancy.salary:
                if isinstance(vacancy.salary, dict):
                    salary_from = vacancy.salary.get("from") or 0
                    salary_to = vacancy.salary.get("to") or 0
                    currency = vacancy.salary.get("currency", "RUR")
                    # Создаем ключ для группировки похожих зарплат
                    if salary_from or salary_to:
                        salary_normalized = f"{salary_from}-{salary_to}_{currency}"
                else:
                    salary_normalized = self._normalize_text(str(vacancy.salary))
            
            # Извлекаем и нормализуем город/регион
            area_normalized = "не_указан"
            if vacancy.area:
                area_normalized = self._normalize_text(str(vacancy.area))
            
            # Определяем приоритет источника (HH = 1, SJ = 2, остальные = 3)
            source = getattr(vacancy, "source", "").lower()
            if "hh" in source:
                source_priority = 1  # HH имеет высший приоритет
            elif "sj" in source or "superjob" in source:
                source_priority = 2  # SJ второй приоритет
            else:
                source_priority = 3  # Остальные источники
            
            dedup_data.append((
                vacancy.id,  # Исправлено: vacancy.id вместо vacancy.vacancy_id
                title_normalized, 
                employer_normalized, 
                employer_id, 
                salary_normalized,
                area_normalized,
                source_priority,
                idx
            ))

        # Вставляем данные
        cursor.executemany(
            """
            INSERT INTO temp_deduplication 
            (vacancy_id, title_normalized, employer_normalized, employer_id, salary_normalized, area_normalized, source_priority, original_index)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                    PARTITION BY title_normalized, employer_normalized, salary_normalized, area_normalized  
                    ORDER BY source_priority ASC, original_index ASC
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
        
        if results is None:
            logger.error("SQL запрос вернул None - проблема с курсором")
            return []

        unique_ids = [row[0] for row in results]

        # Подсчет дубликатов
        try:
            cursor.execute("SELECT COUNT(*) FROM temp_deduplication")
            total_count = cursor.fetchone()
            duplicates_count = (total_count[0] if total_count else 0) - len(unique_ids)
        except Exception:
            duplicates_count = 0
        logger.info(
            f"SQL-дедупликация: найдено {len(unique_ids)} уникальных вакансий, удалено {duplicates_count} дубликатов"
        )

        return unique_ids

    def _build_unique_vacancies(self, original_vacancies: List[Vacancy], unique_ids: List[str]) -> List[Vacancy]:
        """Строит итоговый список уникальных вакансий"""
        vacancy_map = {v.id: v for v in original_vacancies}  # Исправлено: v.id вместо v.vacancy_id

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
