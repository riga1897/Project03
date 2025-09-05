import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseFormatter(ABC):
    """Базовый абстрактный класс для форматирования вакансий"""

    @abstractmethod
    def format_vacancy_info(self, vacancy: Any, number: Optional[int] = None) -> str:
        """Форматирование информации о вакансии в строку"""
        pass

    @abstractmethod
    def format_salary(self, salary: Any) -> str:
        """Форматирование зарплаты"""
        pass

    @abstractmethod
    def format_currency(self, currency: str) -> str:
        """Форматирование валюты"""
        pass

    @abstractmethod
    def format_text(self, text: str, max_length: int = 150) -> str:
        """Форматирование текста с возможностью усечения"""
        pass

    @abstractmethod
    def format_date(self, date_str: str) -> str:
        """Форматирование даты"""
        pass

    @abstractmethod
    def format_experience(self, experience: str) -> str:
        """Форматирование опыта работы"""
        pass

    @abstractmethod
    def format_employment_type(self, employment: str) -> str:
        """Форматирование типа занятости"""
        pass

    @abstractmethod
    def format_schedule(self, schedule: str) -> str:
        """Форматирование графика работы"""
        pass

    @abstractmethod
    def format_company_name(self, company: Any) -> str:
        """Форматирование названия компании"""
        pass

    @abstractmethod
    def clean_html_tags(self, text: str) -> str:
        """Очистка HTML тегов из текста"""
        pass

    @abstractmethod
    def format_number(self, number: int) -> str:
        """Форматирование числа с разделителями тысяч"""
        pass
