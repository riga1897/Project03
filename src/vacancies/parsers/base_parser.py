from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseParser(ABC):
    """Базовый абстрактный класс для парсеров вакансий"""

    @abstractmethod
    def parse_vacancy(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг одной вакансии из сырых данных API

        Args:
            raw_data: Сырые данные вакансии от API

        Returns:
            Dict[str, Any]: Унифицированные данные вакансии
        """
        pass

    @abstractmethod
    def parse_vacancies(self, raw_vacancies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Парсинг списка вакансий из сырых данных API

        Args:
            raw_vacancies: Список сырых данных вакансий от API

        Returns:
            List[Dict[str, Any]]: Список унифицированных данных вакансий
        """
        pass
