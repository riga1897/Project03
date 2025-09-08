"""
Интерфейс для обработки только типизированных данных

Заменяет все работы со словарями на объекты классов.
Принцип Interface Segregation - разделяет ответственность обработки данных.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from src.config.target_companies import CompanyInfo
from src.vacancies.models import Vacancy


class TypedDataProcessor(ABC):
    """
    Абстрактный интерфейс для обработки типизированных данных
    Никаких Dict[str, Any] - только строго типизированные объекты
    """

    @abstractmethod
    def process_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Обработка списка вакансий с строгой типизацией

        Args:
            vacancies: Список типизированных объектов Vacancy

        Returns:
            List[Vacancy]: Обработанный список вакансий
        """
        pass

    @abstractmethod
    def validate_vacancy_data(self, vacancy: Vacancy) -> bool:
        """
        Валидация данных вакансии с проверкой типов

        Args:
            vacancy: Объект вакансии для валидации

        Returns:
            bool: True если данные корректны
        """
        pass


class CompanyDataProcessor(ABC):
    """
    Интерфейс для работы с данными компаний
    """

    @abstractmethod
    def process_companies(self, companies: List[CompanyInfo]) -> List[CompanyInfo]:
        """
        Обработка данных компаний

        Args:
            companies: Список компаний

        Returns:
            List[CompanyInfo]: Обработанный список
        """
        pass

    @abstractmethod
    def find_company_by_id(self, company_id: str, source: str) -> Optional[CompanyInfo]:
        """
        Поиск компании по ID

        Args:
            company_id: ID компании
            source: Источник (hh или sj)

        Returns:
            CompanyInfo или None если не найдена
        """
        pass


class SQLDataProcessor(TypedDataProcessor, CompanyDataProcessor):
    """
    Реализация обработки через SQL с типизированными данными
    Принцип Liskov Substitution - может заменить любой из родительских интерфейсов
    """

    def __init__(self, sql_filter_service: Any):
        """
        Инициализация SQL процессора

        Args:
            sql_filter_service: Сервис SQL фильтрации
        """
        self.sql_filter_service = sql_filter_service

    def process_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        SQL обработка вакансий - фильтрация и дедупликация
        """
        return self.sql_filter_service.filter_and_deduplicate_vacancies(vacancies)

    def validate_vacancy_data(self, vacancy: Vacancy) -> bool:
        """
        Валидация типизированной вакансии
        """
        if not vacancy or not isinstance(vacancy, Vacancy):
            return False

        # Проверяем обязательные поля
        if not vacancy.vacancy_id or not vacancy.title:
            return False

        # Проверяем типы данных
        if vacancy.salary and not hasattr(vacancy.salary, "salary_from"):
            return False

        return True

    def process_companies(self, companies: List[CompanyInfo]) -> List[CompanyInfo]:
        """
        Обработка списка компаний через SQL
        """
        # Здесь можно добавить SQL валидацию и обработку компаний
        return [comp for comp in companies if self.validate_company_data(comp)]

    def validate_company_data(self, company: CompanyInfo) -> bool:
        """
        Валидация данных компании
        """
        if not company or not isinstance(company, CompanyInfo):
            return False

        return bool(company.name and (company.hh_id or company.sj_id))

    def find_company_by_id(self, company_id: str, source: str) -> Optional[CompanyInfo]:
        """
        Поиск компании по ID через целевые компании
        """
        from src.config.target_companies import TargetCompanies

        companies = TargetCompanies.get_all_companies()
        for company in companies:
            if source == "hh" and company.hh_id == company_id:
                return company
            elif source == "sj" and company.sj_id == company_id:
                return company

        return None
