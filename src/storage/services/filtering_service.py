"""
Сервис фильтрации вакансий по целевым компаниям на основе SOLID принципов

Реализует строгую ID-основанную фильтрацию без фолбэк-методов.
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

try:
    from ...config.target_companies import TargetCompanies
except ImportError:
    from src.config.target_companies import TargetCompanies

logger = logging.getLogger(__name__)


class FilteringStrategy(ABC):
    """
    Абстрактная стратегия фильтрации (принцип Strategy Pattern)
    """

    @abstractmethod
    def filter(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """
        Выполняет фильтрацию вакансий

        Args:
            vacancies: Список вакансий для фильтрации
            db_manager: Менеджер базы данных

        Returns:
            Отфильтрованные вакансии
        """
        pass


class TargetCompanyFilterStrategy(FilteringStrategy):
    """
    Стратегия фильтрации по целевым компаниям
    Использует ТОЛЬКО ID-основанную фильтрацию (без фолбэков)
    """

    def __init__(self):
        """Инициализация стратегии"""
        self.target_companies = TargetCompanies.get_all_companies()
        # Получаем все валидные ID целевых компаний
        self.target_hh_ids = set()
        self.target_sj_ids = set()

        for company in self.target_companies:
            if hasattr(company, "hh_id") and company.hh_id:
                self.target_hh_ids.add(str(company.hh_id))
            if hasattr(company, "sj_id") and company.sj_id:
                self.target_sj_ids.add(str(company.sj_id))

        logger.info(f"Инициализирована фильтрация: {len(self.target_hh_ids)} HH ID, {len(self.target_sj_ids)} SJ ID")

    def filter(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """
        Фильтрует вакансии по целевым компаниям через ID
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем фильтрацию по целевым компаниям: {len(vacancies)} вакансий")

        filtered_vacancies = []

        for vacancy in vacancies:
            if self._is_target_company_vacancy(vacancy):
                filtered_vacancies.append(vacancy)

        logger.info(f"Фильтрация завершена: {len(vacancies)} -> {len(filtered_vacancies)} вакансий")
        return filtered_vacancies

    def _is_target_company_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Проверяет, относится ли вакансия к целевой компании
        ТОЛЬКО по ID - никаких фолбэков по названиям!
        """
        if not vacancy.employer:
            return False

        # Извлекаем ID работодателя из разных источников
        employer_id = None

        if isinstance(vacancy.employer, dict):
            employer_id = vacancy.employer.get("id")
        elif hasattr(vacancy.employer, "id"):
            employer_id = vacancy.employer.id
        elif hasattr(vacancy.employer, "employer_id"):
            employer_id = vacancy.employer.employer_id

        # Дополнительно проверяем поле employer_id на уровне вакансии
        if not employer_id and hasattr(vacancy, "employer_id"):
            employer_id = vacancy.employer_id

        if not employer_id:
            return False

        employer_id_str = str(employer_id)

        # Проверяем по спискам ID (учитываем источник вакансии)
        source = getattr(vacancy, "source", "").lower()

        # Для HH вакансий проверяем HH ID
        if "hh" in source and employer_id_str in self.target_hh_ids:
            return True

        # Для SuperJob вакансий проверяем SJ ID
        if ("sj" in source or "superjob" in source) and employer_id_str in self.target_sj_ids:
            return True

        # Если источник неизвестен, проверяем оба списка
        if employer_id_str in self.target_hh_ids or employer_id_str in self.target_sj_ids:
            return True

        return False


class SalaryFilterStrategy(FilteringStrategy):
    """
    Стратегия фильтрации по зарплате
    Оставляет только вакансии с указанной зарплатой
    """

    def filter(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """Фильтрует вакансии с указанной зарплатой"""
        if not vacancies:
            return []

        logger.info(f"Начинаем фильтрацию по зарплате: {len(vacancies)} вакансий")

        filtered_vacancies = []

        for vacancy in vacancies:
            if self._has_salary(vacancy):
                filtered_vacancies.append(vacancy)

        logger.info(f"Фильтрация по зарплате: {len(vacancies)} -> {len(filtered_vacancies)} вакансий")
        return filtered_vacancies

    def _has_salary(self, vacancy: Vacancy) -> bool:
        """Проверяет, есть ли у вакансии указанная зарплата"""
        if not vacancy.salary:
            return False

        # Проверяем различные форматы зарплаты
        if isinstance(vacancy.salary, dict):
            salary_from = vacancy.salary.get("from")
            salary_to = vacancy.salary.get("to")
            return bool(salary_from or salary_to)
        elif hasattr(vacancy.salary, "salary_from") or hasattr(vacancy.salary, "salary_to"):
            return bool(vacancy.salary.salary_from or vacancy.salary.salary_to)

        return False


class CompositeFilterStrategy(FilteringStrategy):
    """
    Композитная стратегия для применения нескольких фильтров (принцип Composite Pattern)
    """

    def __init__(self, strategies: List[FilteringStrategy]):
        """
        Инициализация композитной стратегии

        Args:
            strategies: Список стратегий для последовательного применения
        """
        self.strategies = strategies

    def filter(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """Последовательно применяет все стратегии"""
        result = vacancies

        for i, strategy in enumerate(self.strategies, 1):
            logger.info(f"Применяем стратегию {i}/{len(self.strategies)}: {strategy.__class__.__name__}")
            result = strategy.filter(result, db_manager)

            if not result:
                logger.warning(f"Стратегия {strategy.__class__.__name__} не оставила вакансий")
                break

        return result


class FilteringService:
    """
    Основной сервис фильтрации (принцип Single Responsibility)
    Позволяет легко сменить стратегии фильтрации (принцип Open/Closed)
    """

    def __init__(self, strategy: FilteringStrategy):
        """
        Инициализация сервиса

        Args:
            strategy: Стратегия фильтрации
        """
        self.strategy = strategy

    def process(self, vacancies: List[Vacancy], db_manager: AbstractDBManager) -> List[Vacancy]:
        """
        Выполняет фильтрацию с помощью выбранной стратегии

        Args:
            vacancies: Список вакансий
            db_manager: Менеджер базы данных

        Returns:
            Отфильтрованные вакансии
        """
        return self.strategy.filter(vacancies, db_manager)

    def set_strategy(self, strategy: FilteringStrategy) -> None:
        """
        Изменяет стратегию фильтрации

        Args:
            strategy: Новая стратегия
        """
        self.strategy = strategy
