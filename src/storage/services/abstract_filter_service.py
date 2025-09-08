"""
Абстрактные классы для сервисов обработки вакансий

Определяет единые интерфейсы для фильтрации, дедупликации и координации.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set, Tuple

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class AbstractFilterService(ABC):
    """
    Абстрактный сервис фильтрации вакансий
    Принцип Interface Segregation - специализированный интерфейс для фильтрации
    """

    @abstractmethod
    def filter_by_company_ids(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Фильтрует вакансии по ID компаний

        Args:
            vacancies: Список вакансий для фильтрации

        Returns:
            List[Vacancy]: Отфильтрованные вакансии
        """
        pass

    @abstractmethod
    def get_target_company_stats(self) -> Tuple[Set[str], Set[str]]:
        """
        Возвращает статистику по целевым компаниям

        Returns:
            Tuple[Set[str], Set[str]]: (HH ID, SJ ID) целевых компаний
        """
        pass


class AbstractDeduplicationService(ABC):
    """
    Абстрактный сервис дедупликации вакансий
    Принцип Interface Segregation - специализированный интерфейс для дедупликации
    """

    @abstractmethod
    def deduplicate_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Выполняет дедупликацию вакансий

        Args:
            vacancies: Список вакансий для дедупликации

        Returns:
            List[Vacancy]: Уникальные вакансии
        """
        pass


class AbstractVacancyProcessor(ABC):
    """
    Абстрактный координатор обработки вакансий
    Принцип Interface Segregation - специализированный интерфейс для координации
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def filter_only(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Применяет только фильтрацию по ID компаний (без дедупликации)

        Args:
            vacancies: Список вакансий

        Returns:
            List[Vacancy]: Отфильтрованные вакансии
        """
        pass

    @abstractmethod
    def deduplicate_only(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Применяет только дедупликацию (без фильтрации)

        Args:
            vacancies: Список вакансий

        Returns:
            List[Vacancy]: Дедуплицированные вакансии
        """
        pass

    @abstractmethod
    def get_processing_summary(self, vacancies: List[Vacancy]) -> Dict[str, Any]:
        """
        Получает сводку по обработке без изменения данных

        Args:
            vacancies: Список вакансий для анализа

        Returns:
            Dict[str, Any]: Сводка по обработке
        """
        pass
