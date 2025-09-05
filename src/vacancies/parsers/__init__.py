
"""Абстрактные классы и базовые модели для работы с вакансиями."""

import abc


class AbstractVacancy(abc.ABC):
    """Абстрактный класс для представления вакансии."""

    @abc.abstractmethod
    def get_title(self) -> str:
        """Получить название вакансии."""
        pass

    @abc.abstractmethod
    def get_salary(self) -> str:
        """Получить информацию о зарплате."""
        pass

    @abc.abstractmethod
    def get_url(self) -> str:
        """Получить ссылку на вакансию."""
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        """Получить описание вакансии."""
        pass

    @abc.abstractmethod
    def get_city(self) -> str:
        """Получить город размещения вакансии."""
        pass


class Vacancy(AbstractVacancy):
    """Конкретная реализация вакансии."""

    def __init__(self, title: str, salary: str, url: str, description: str,
                 city: str):
        """
        Инициализировать вакансию.
        
        Args:
            title: Название вакансии
            salary: Информация о зарплате
            url: Ссылка на вакансию
            description: Описание вакансии
            city: Город размещения
        """
        self.title = title
        self.salary = salary
        self.url = url
        self.description = description
        self.city = city

    def get_title(self) -> str:
        """Получить название вакансии."""
        return self.title

    def get_salary(self) -> str:
        """Получить информацию о зарплате."""
        return self.salary

    def get_url(self) -> str:
        """Получить ссылку на вакансию."""
        return self.url

    def get_description(self) -> str:
        """Получить описание вакансии."""
        return self.description

    def get_city(self) -> str:
        """Получить город размещения вакансии."""
        return self.city


class BaseJobAPI(abc.ABC):
    """Базовый класс для работы с API поиска работы."""

    @abc.abstractmethod
    def get_jobs(self, search_query: str) -> list[AbstractVacancy]:
        """Получить список вакансий по поисковому запросу."""
        pass


class BaseParser(abc.ABC):
    """Базовый класс для парсинга вакансий."""

    @abc.abstractmethod
    def parse(self, html_content: str) -> list[AbstractVacancy]:
        """Распарсить HTML контент и извлечь вакансии."""
        pass


class BaseDBManager(abc.ABC):
    """Базовый класс для работы с базой данных."""

    @abc.abstractmethod
    def save_vacancy(self, vacancy: AbstractVacancy) -> None:
        """Сохранить вакансию в базе данных."""
        pass

    @abc.abstractmethod
    def get_vacancies(self, search_params: dict) -> list[AbstractVacancy]:
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
