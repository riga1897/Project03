"""
Абстрактный базовый класс для фильтров данных.
Реализует интерфейс для различных типов фильтрации.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AbstractDataFilter(ABC):
    """
    Абстрактный базовый класс для фильтров данных.

    Определяет единый интерфейс для всех типов фильтров,
    обеспечивая соблюдение принципа открытости/закрытости (OCP).
    """

    @abstractmethod
    def filter_by_company(self, data: List[Dict[str, Any]], companies: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация данных по компаниям

        Args:
            data: Список данных для фильтрации
            companies: Список названий компаний для фильтрации

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список данных
        """
        pass

    @abstractmethod
    def filter_by_salary(
        self, data: List[Dict[str, Any]], min_salary: Optional[int] = None, max_salary: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Фильтрация данных по зарплате

        Args:
            data: Список данных для фильтрации
            min_salary: Минимальная зарплата
            max_salary: Максимальная зарплата

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список данных
        """
        pass

    @abstractmethod
    def filter_by_location(self, data: List[Dict[str, Any]], locations: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация данных по местоположению

        Args:
            data: Список данных для фильтрации
            locations: Список местоположений для фильтрации

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список данных
        """
        pass

    @abstractmethod
    def filter_by_experience(self, data: List[Dict[str, Any]], experience_levels: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация данных по опыту работы

        Args:
            data: Список данных для фильтрации
            experience_levels: Список уровней опыта для фильтрации

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список данных
        """
        pass

    def filter_by_multiple_criteria(self, data: List[Dict[str, Any]], **filters: Any) -> List[Dict[str, Any]]:
        """
        Фильтрация по множественным критериям

        Args:
            data: Список данных для фильтрации
            **filters: Именованные параметры фильтрации

        Returns:
            List[Dict[str, Any]]: Отфильтрованный список данных
        """
        result = data

        if "companies" in filters and filters["companies"]:
            result = self.filter_by_company(result, filters["companies"])

        if "min_salary" in filters or "max_salary" in filters:
            result = self.filter_by_salary(result, filters.get("min_salary"), filters.get("max_salary"))

        if "locations" in filters and filters["locations"]:
            result = self.filter_by_location(result, filters["locations"])

        if "experience_levels" in filters and filters["experience_levels"]:
            result = self.filter_by_experience(result, filters["experience_levels"])

        return result
