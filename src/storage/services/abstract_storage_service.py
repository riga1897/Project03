"""
Абстрактный класс для сервиса хранения вакансий

Определяет единый интерфейс для всех операций с хранением вакансий.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class AbstractVacancyStorageService(ABC):
    """
    Абстрактный сервис для работы с хранением вакансий
    Принцип Interface Segregation - единый интерфейс для всех операций хранения
    """

    @abstractmethod
    def filter_and_deduplicate_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Основной метод обработки вакансий

        Args:
            vacancies: Список вакансий для обработки

        Returns:
            List[Vacancy]: Обработанные вакансии (отфильтрованные и без дубликатов)
        """
        pass

    @abstractmethod
    def save_vacancies(self, vacancies: List[Vacancy]) -> int:
        """
        Сохраняет вакансии в хранилище

        Args:
            vacancies: Список вакансий для сохранения

        Returns:
            int: Количество успешно сохраненных вакансий
        """
        pass

    @abstractmethod
    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """
        Получает вакансии из хранилища

        Args:
            filters: Словарь с критериями фильтрации

        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_id: str) -> bool:
        """
        Удаляет вакансию из хранилища

        Args:
            vacancy_id: Идентификатор вакансии

        Returns:
            bool: True если удаление успешно
        """
        pass

    @abstractmethod
    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """
        Получает список компаний и количество их вакансий

        Returns:
            List[tuple]: Список кортежей (компания, количество_вакансий)
        """
        pass

    @abstractmethod
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Получает статистику хранилища

        Returns:
            Dict[str, Any]: Статистика хранилища
        """
        pass
