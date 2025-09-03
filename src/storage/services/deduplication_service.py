"""
Сервис дедупликации вакансий на основе SOLID принципов

Реализует эффективную дедупликацию вакансий на уровне базы данных.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

import psycopg2

try:
    from ..abstract_db_manager import AbstractDBManager
except ImportError:
    from src.storage.abstract_db_manager import AbstractDBManager

try:
    from ...vacancies.models import Vacancy
except ImportError:
    from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class DeduplicationStrategy(ABC):
    """
    Абстрактная стратегия дедупликации (принцип Strategy Pattern)
    """

    @abstractmethod
    def deduplicate(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """
        Выполняет дедупликацию вакансий

        Args:
            vacancies: Список вакансий для обработки
            db_manager: Менеджер базы данных

        Returns:
            Список уникальных вакансий
        """
        pass


class SQLDeduplicationStrategy(DeduplicationStrategy):
    """
    SQL-основанная стратегия дедупликации
    Использует мощности PostgreSQL для эффективной обработки
    """

    def deduplicate(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """
        Выполняет дедупликацию через SQL запросы
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем SQL-дедупликацию для {len(vacancies)} вакансий")

        try:
            connection = db_manager._get_connection()
            cursor = connection.cursor()

            # Создаем временную таблицу для вакансий
            cursor.execute(
                """
                CREATE TEMP TABLE temp_vacancies (
                    vacancy_id VARCHAR(255) PRIMARY KEY,
                    title_normalized TEXT,
                    employer_normalized TEXT,
                    original_index INTEGER
                )
            """
            )

            # Подготавливаем данные для вставки
            temp_data = []
            for idx, vacancy in enumerate(vacancies):
                normalized_title = self._normalize_text(vacancy.title or "")
                normalized_employer = self._normalize_employer(vacancy.employer or "")

                temp_data.append((vacancy.vacancy_id, normalized_title, normalized_employer, idx))

            # Вставляем данные
            cursor.executemany(
                """
                INSERT INTO temp_vacancies (vacancy_id, title_normalized, employer_normalized, original_index)
                VALUES (%s, %s, %s, %s)
            """,
                temp_data,
            )

            # Находим уникальные вакансии
            cursor.execute(
                """
                WITH ranked_vacancies AS (
                    SELECT 
                        vacancy_id,
                        original_index,
                        ROW_NUMBER() OVER (
                            PARTITION BY title_normalized, employer_normalized 
                            ORDER BY original_index
                        ) as rn
                    FROM temp_vacancies
                )
                SELECT original_index 
                FROM ranked_vacancies 
                WHERE rn = 1
                ORDER BY original_index
            """
            )

            unique_indices = [row[0] for row in cursor.fetchall()]
            unique_vacancies = [vacancies[idx] for idx in unique_indices]

            cursor.close()
            connection.close()

            duplicates_removed = len(vacancies) - len(unique_vacancies)
            logger.info(
                f"SQL-дедупликация: {len(vacancies)} -> {len(unique_vacancies)} (удалено {duplicates_removed})"
            )

            return unique_vacancies

        except Exception as e:
            logger.error(f"Ошибка SQL-дедупликации: {e}")
            return vacancies  # Возвращаем исходный список

    def _normalize_text(self, text: str) -> str:
        """Нормализует текст для сравнения"""
        if not text:
            return ""

        import re

        # Приводим к нижнему регистру, удаляем лишние пробелы
        normalized = re.sub(r"\s+", " ", text.lower().strip())
        # Удаляем спецсимволы
        normalized = re.sub(r"[^\w\sа-яё]", " ", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    def _normalize_employer(self, employer: Any) -> str:
        """Нормализует информацию о работодателе"""
        if not employer:
            return ""

        if isinstance(employer, dict):
            name = employer.get("name", "")
        else:
            name = str(employer)

        return self._normalize_text(name)


class DeduplicationService:
    """
    Основной сервис дедупликации (принцип Single Responsibility)
    Позволяет легко сменить стратегии дедупликации (принцип Open/Closed)
    """

    def __init__(self, strategy: DeduplicationStrategy):
        """
        Инициализация сервиса

        Args:
            strategy: Стратегия дедупликации
        """
        self.strategy = strategy

    def process(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """
        Выполняет дедупликацию с помощью выбранной стратегии

        Args:
            vacancies: Список вакансий
            db_manager: Менеджер базы данных

        Returns:
            Список уникальных вакансий
        """
        return self.strategy.deduplicate(vacancies, db_manager)

    def set_strategy(self, strategy: DeduplicationStrategy):
        """
        Изменяет стратегию дедупликации

        Args:
            strategy: Новая стратегия
        """
        self.strategy = strategy
