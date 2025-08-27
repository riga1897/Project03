
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class AbstractDBManager(ABC):
    """Абстрактный класс для менеджеров базы данных"""

    @abstractmethod
    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получить список всех компаний и количество вакансий у каждой компании
        
        Returns:
            List[Tuple[str, int]]: Список кортежей (название_компании, количество_вакансий)
        """
        pass

    @abstractmethod
    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получить список всех вакансий
        
        Returns:
            List[Dict[str, Any]]: Список всех вакансий
        """
        pass

    @abstractmethod
    def get_avg_salary(self) -> Optional[float]:
        """
        Получить среднюю зарплату по всем вакансиям
        
        Returns:
            Optional[float]: Средняя зарплата или None если данных нет
        """
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получить список вакансий с зарплатой выше средней
        
        Returns:
            List[Dict[str, Any]]: Список вакансий с зарплатой выше средней
        """
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получить список вакансий, в названии которых содержится переданное слово
        
        Args:
            keyword: Ключевое слово для поиска
            
        Returns:
            List[Dict[str, Any]]: Список найденных вакансий
        """
        pass

    @abstractmethod
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Получить статистику базы данных
        
        Returns:
            Dict[str, Any]: Статистика базы данных
        """
        pass
