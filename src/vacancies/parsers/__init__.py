"""
Абстрактные классы и базовые модели для работы с вакансиями.
"""

import abc
from typing import List

# Импортируем каноническую версию AbstractVacancy
from src.vacancies.abstract import AbstractVacancy
# Импортируем основную модель Vacancy
from src.vacancies.models import Vacancy


class BaseJobAPI(abc.ABC):
    """Базовый класс для работы с API поиска работы."""

    @abc.abstractmethod
    def get_jobs(self, search_query: str) -> List[Vacancy]:
        """Получить список вакансий по поисковому запросу."""
        pass


class BaseParser(abc.ABC):
    """Базовый класс для парсинга вакансий."""

    @abc.abstractmethod
    def parse(self, html_content: str) -> List[Vacancy]:
        """Распарсить HTML контент и извлечь вакансии."""
        pass


class BaseDBManager(abc.ABC):
    """Базовый класс для работы с базой данных."""

    @abc.abstractmethod
    def save_vacancy(self, vacancy: AbstractVacancy) -> None:
        """Сохранить вакансию в базе данных."""
        pass

    @abc.abstractmethod
    def get_vacancies(self, search_params: dict) -> List[AbstractVacancy]:
        """Получить вакансии из базы данных по параметрам поиска."""
        pass

    @abc.abstractmethod
    def delete_vacancy(self, vacancy_id: int) -> None:
        """Удалить вакансию из базы данных."""
        pass

    @abc.abstractmethod
    def count_vacancies(self) -> int:
        """Получить количество вакансий в базе данных."""
        pass
