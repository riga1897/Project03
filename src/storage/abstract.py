from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from src.vacancies.abstract import AbstractVacancy


class AbstractVacancyStorage(ABC):
    """Абстрактный класс для работы с хранилищем вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: AbstractVacancy) -> None:
        """
        Добавляет вакансию в хранилище
        :param vacancy: Объект вакансии для добавления
        """

    @abstractmethod
    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
        """
        Возвращает список вакансий с учетом фильтров
        :param filters: Словарь с критериями фильтрации
        :return: Список вакансий
        """

    @abstractmethod
    def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
        """
        Удаляет вакансию из хранилища
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
    def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy]) -> List[str]:
        """
        Оптимизированное batch-добавление вакансий
        :param vacancies: Список вакансий для добавления
        :return: Список сообщений об операциях
        """

    # Новые методы для бизнес-логики
    @abstractmethod
    def get_vacancies_paginated(self, page: int = 1, page_size: int = 10, 
                              filters: Optional[Dict[str, Any]] = None,
                              sort_by: str = "created_at", sort_desc: bool = True) -> Tuple[List[AbstractVacancy], int]:
        """
        Возвращает вакансии с пагинацией и сортировкой
        :param page: Номер страницы (начиная с 1)
        :param page_size: Количество вакансий на странице
        :param filters: Фильтры для поиска
        :param sort_by: Поле для сортировки
        :param sort_desc: Сортировка по убыванию
        :return: Кортеж (список вакансий, общее количество)
        """

    @abstractmethod
    def search_vacancies_advanced(self, keywords: List[str], salary_range: Optional[Tuple[int, int]] = None,
                                experience_levels: Optional[List[str]] = None,
                                employment_types: Optional[List[str]] = None,
                                page: int = 1, page_size: int = 10) -> Tuple[List[AbstractVacancy], int]:
        """
        Расширенный поиск вакансий
        :param keywords: Список ключевых слов для поиска
        :param salary_range: Диапазон зарплат (от, до)
        :param experience_levels: Уровни опыта
        :param employment_types: Типы занятости
        :param page: Номер страницы
        :param page_size: Размер страницы
        :return: Кортеж (список вакансий, общее количество)
        """

    @abstractmethod
    def get_salary_statistics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Получение статистики по зарплатам
        :param filters: Фильтры для выборки
        :return: Словарь со статистикой (мин, макс, среднее, медиана)
        """

    @abstractmethod
    def get_top_employers(self, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Получение топа работодателей по количеству вакансий
        :param limit: Количество работодателей в топе
        :param filters: Фильтры для выборки
        :return: Список словарей с информацией о работодателях
        """

    @abstractmethod
    def get_popular_keywords(self, limit: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Получение популярных ключевых слов из требований
        :param limit: Количество ключевых слов
        :param filters: Фильтры для выборки
        :return: Список словарей с ключевыми словами и их частотой
        """
