from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class AbstractVacancy(ABC):
    """Абстрактный базовый класс для представления вакансии
    
    Определяет минимальный интерфейс для всех типов вакансий.
    Конкретные реализации должны предоставить все необходимые атрибуты
    как обычные поля или свойства.
    """

    # Основные атрибуты интерфейса
    id: str
    vacancy_id: str
    title: str
    url: str
    description: Optional[str]
    requirements: Optional[str]
    responsibilities: Optional[str]
    
    # Связанные объекты
    employer: Optional[Any]
    salary: Optional[Any]
    experience: Optional[Any]
    employment: Optional[Any]
    schedule: Optional[Any]
    
    # Метаинформация
    area: Optional[str]
    source: Optional[str]
    published_at: Optional[datetime]
    company_id: Optional[int]

    @abstractmethod
    def __init__(self) -> None:
        """
        Инициализация вакансии
        """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует вакансию в словарь"""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AbstractVacancy":
        """
        Создает объект вакансии из словаря
        :param data: Словарь с данными вакансии
        :return: Объект вакансии
        """
