"""
Абстрактные базовые классы, совместимые с Pydantic архитектурой.

Эти классы определяют контракты для всех моделей системы,
но теперь работают совместно с Pydantic BaseModel.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class AbstractEmployerMixin(ABC):
    """Миксин для определения интерфейса работодателя"""

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


class AbstractExperienceMixin(ABC):
    """Миксин для определения интерфейса опыта работы"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить описание опыта"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID опыта"""
        pass


class AbstractEmploymentMixin(ABC):
    """Миксин для определения интерфейса типа занятости"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить тип занятости"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID типа занятости"""
        pass


class AbstractScheduleMixin(ABC):
    """Миксин для определения интерфейса графика работы"""

    @abstractmethod
    def get_name(self) -> str:
        """Получить название графика"""
        pass

    @abstractmethod
    def get_id(self) -> Optional[str]:
        """Получить ID графика"""
        pass


class AbstractSalaryMixin(ABC):
    """Миксин для определения интерфейса зарплаты"""

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


# Совместимые с Pydantic базовые классы
class AbstractEmployer(BaseModel, AbstractEmployerMixin):
    """Абстрактный базовый класс для работодателя, совместимый с Pydantic"""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractEmployer":
        """Создать из словаря"""
        return cls(**data)


class AbstractExperience(BaseModel, AbstractExperienceMixin):
    """Абстрактный базовый класс для опыта работы, совместимый с Pydantic"""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractExperience":
        """Создать из словаря"""
        return cls(**data)

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> "AbstractExperience":
        """Создать из строки"""
        pass


class AbstractEmployment(BaseModel, AbstractEmploymentMixin):
    """Абстрактный базовый класс для типа занятости, совместимый с Pydantic"""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractEmployment":
        """Создать из словаря"""
        return cls(**data)

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> "AbstractEmployment":
        """Создать из строки"""
        pass


class AbstractSchedule(BaseModel, AbstractScheduleMixin):
    """Абстрактный базовый класс для графика работы, совместимый с Pydantic"""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractSchedule":
        """Создать из словаря"""
        return cls(**data)

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> "AbstractSchedule":
        """Создать из строки"""
        pass


class AbstractSalary(BaseModel, AbstractSalaryMixin):
    """Абстрактный базовый класс для зарплаты, совместимый с Pydantic"""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractSalary":
        """Создать из словаря"""
        return cls(**data)


# Экспортируемые типы
__all__ = [
    "AbstractEmployerMixin",
    "AbstractExperienceMixin",
    "AbstractEmploymentMixin",
    "AbstractScheduleMixin",
    "AbstractSalaryMixin",
    "AbstractEmployer",
    "AbstractExperience",
    "AbstractEmployment",
    "AbstractSchedule",
    "AbstractSalary",
]
