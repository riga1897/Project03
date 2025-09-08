"""
Координатор обработки вакансий

Координирует работу отдельных сервисов фильтрации и дедупликации.
Принцип Single Responsibility - только координация процесса.
"""

import logging
from typing import List

from src.storage.abstract_db_manager import AbstractDBManager
from src.vacancies.models import Vacancy

from .abstract_filter_service import AbstractVacancyProcessor
from .company_id_filter_service import CompanyIDFilterService
from .sql_deduplication_service import SQLDeduplicationService

logger = logging.getLogger(__name__)


class VacancyProcessingCoordinator(AbstractVacancyProcessor):
    """
    Координатор обработки вакансий
    Принцип Single Responsibility - координация отдельных операций
    """

    def __init__(self, db_manager: AbstractDBManager):
        """
        Инициализация координатора

        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        self.id_filter_service = CompanyIDFilterService(db_manager)
        self.deduplication_service = SQLDeduplicationService(db_manager)

        logger.info("Vacancy Processing Coordinator инициализирован")

    def process_vacancies(
        self, vacancies: List[Vacancy], apply_company_filter: bool = True, apply_deduplication: bool = True
    ) -> List[Vacancy]:
        """
        Обрабатывает вакансии через отдельные сервисы

        Args:
            vacancies: Список вакансий для обработки
            apply_company_filter: Применять ли фильтрацию по ID компаний
            apply_deduplication: Применять ли дедупликацию

        Returns:
            List[Vacancy]: Обработанные вакансии
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем обработку {len(vacancies)} вакансий")
        logger.info(f"Параметры: ID фильтр={apply_company_filter}, дедупликация={apply_deduplication}")

        result = vacancies

        # Шаг 1: Фильтрация по ID целевых компаний
        if apply_company_filter:
            logger.info("Шаг 1: Фильтрация по ID целевых компаний")
            result = self.id_filter_service.filter_by_company_ids(result)

            if not result:
                logger.warning("После фильтрации по ID компаний не осталось вакансий")
                return []

        # Шаг 2: Дедупликация
        if apply_deduplication:
            logger.info("Шаг 2: SQL-дедупликация")
            result = self.deduplication_service.deduplicate_vacancies(result)

        logger.info(f"Обработка завершена: {len(vacancies)} -> {len(result)} вакансий")
        return result

    def filter_only(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Применяет только фильтрацию по ID компаний (без дедупликации)

        Args:
            vacancies: Список вакансий

        Returns:
            List[Vacancy]: Отфильтрованные вакансии
        """
        return self.process_vacancies(vacancies, apply_company_filter=True, apply_deduplication=False)

    def deduplicate_only(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Применяет только дедупликацию (без фильтрации)

        Args:
            vacancies: Список вакансий

        Returns:
            List[Vacancy]: Дедуплицированные вакансии
        """
        return self.process_vacancies(vacancies, apply_company_filter=False, apply_deduplication=True)

    def get_target_company_stats(self) -> tuple:
        """Получает статистику по целевым компаниям"""
        return self.id_filter_service.get_target_company_stats()

    def get_processing_summary(self, vacancies: List[Vacancy]) -> dict:
        """
        Получает сводку по обработке без изменения данных

        Args:
            vacancies: Список вакансий для анализа

        Returns:
            dict: Сводка по обработке
        """
        if not vacancies:
            return {
                "total_vacancies": 0,
                "after_company_filter": 0,
                "after_deduplication": 0,
                "target_hh_ids": 0,
                "target_sj_ids": 0,
            }

        hh_ids, sj_ids = self.get_target_company_stats()

        # Применяем только фильтр для статистики
        filtered = self.filter_only(vacancies)

        # Применяем дедупликацию к отфильтрованным
        deduplicated = self.deduplication_service.deduplicate_vacancies(filtered) if filtered else []

        return {
            "total_vacancies": len(vacancies),
            "after_company_filter": len(filtered),
            "after_deduplication": len(deduplicated),
            "target_hh_ids": len(hh_ids),
            "target_sj_ids": len(sj_ids),
        }
