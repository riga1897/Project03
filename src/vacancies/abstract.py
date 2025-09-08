from abc import ABC, abstractmethod
from typing import Any, Dict


class AbstractVacancy(ABC):
    """Абстрактный базовый класс для представления вакансии
    
    Определяет минимальный интерфейс для всех типов вакансий.
    Конкретные реализации должны предоставить все необходимые атрибуты
    как обычные поля или свойства.
    """

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
