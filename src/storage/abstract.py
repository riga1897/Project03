from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.vacancies.abstract import AbstractVacancy

if TYPE_CHECKING:
    from src.vacancies.models import Vacancy


class AbstractVacancyStorage(ABC):
    """Абстрактный класс для работы с хранилищем вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: AbstractVacancy) -> bool:
        """
        Добавляет вакансию в PostgreSQL хранилище
        :param vacancy: Объект вакансии для добавления
        :return: True если вакансия успешно добавлена, False иначе
        """

    @abstractmethod
    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List["Vacancy"]:
        """
        Возвращает список вакансий из PostgreSQL с учетом фильтров
        :param filters: Словарь с критериями фильтрации
        :return: Список вакансий
        """

    @abstractmethod
    def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
        """
        Удаляет вакансию из PostgreSQL хранилища
        :param vacancy: Объект вакансии для удаления
        """

    # Batch методы для эффективной работы с большими объемами данных
    @abstractmethod
    def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
        """
        Проверяет существование множества вакансий одним запросом
        :param vacancies: Список вакансий для проверки
        :return: Словарь {vacancy_id: exists}
        """

    @abstractmethod
    def add_vacancy_batch_optimized(
        self, vacancies: List[AbstractVacancy], search_query: Optional[str] = None
    ) -> List[str]:
        """
        Оптимизированное batch-добавление вакансий
        :param vacancies: Список вакансий для добавления
        :param search_query: Поисковый запрос, по которому найдены вакансии
        :return: Список сообщений об операциях
        """
