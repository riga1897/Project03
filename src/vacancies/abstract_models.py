"""
Абстрактные базовые классы для объектно-ориентированной архитектуры системы поиска вакансий.

В соответствии с принципами SOLID и ООП, все компоненты системы должны наследоваться
от соответствующих абстрактных классов без конкретной реализации.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AbstractEmployer(ABC):
    """Абстрактный базовый класс для работодателя"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить название компании"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID работодателя"""
        pass

    @abstractmethod
    def is_trusted(self) -> Optional[bool]:
        """Проверить, является ли работодатель проверенным"""
        pass

    @abstractmethod
    def get_url(self) -> Optional[str]:
        """Получить URL работодателя"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractEmployer":
        """Создать из словаря"""
        pass


class AbstractExperience(ABC):
    """Абстрактный базовый класс для опыта работы"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить описание опыта"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID опыта"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractExperience":
        """Создать из словаря"""
        pass

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> "AbstractExperience":
        """Создать из строки"""
        pass


class AbstractEmployment(ABC):
    """Абстрактный базовый класс для типа занятости"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить тип занятости"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID типа занятости"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractEmployment":
        """Создать из словаря"""
        pass

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> "AbstractEmployment":
        """Создать из строки"""
        pass


class AbstractSalary(ABC):
    """Абстрактный базовый класс для зарплаты"""

    @abstractmethod
    def get_from_amount(self) -> Optional[int]:
        """Получить минимальную зарплату"""
        pass

    @abstractmethod
    def get_to_amount(self) -> Optional[int]:
        """Получить максимальную зарплату"""
        pass

    @abstractmethod
    def get_currency(self) -> str:
        """Получить валюту"""
        pass

    @abstractmethod
    def get_average(self) -> float:
        """Получить среднюю зарплату"""
        pass

    @abstractmethod
    def is_specified(self) -> bool:
        """Проверить, указана ли зарплата"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractSalary":
        """Создать из словаря"""
        pass


class AbstractSchedule(ABC):
    """Абстрактный базовый класс для графика работы"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить название графика"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID графика"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractSchedule":
        """Создать из словаря"""
        pass

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> "AbstractSchedule":
        """Создать из строки"""
        pass
