"""
Базовый модуль для работы с API поиска вакансий.

Содержит абстрактный базовый класс, который определяет единый интерфейс
для всех API источников вакансий (HH.ru, SuperJob и т.д.).
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List

logger = logging.getLogger(__name__)


class BaseJobAPI(ABC):
    """
    Базовый абстрактный класс для всех API поиска вакансий.

    Определяет единый интерфейс для работы с различными источниками вакансий,
    включая методы для получения, валидации вакансий.
    """

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение списка вакансий из источника по поисковому запросу.

        Args:
            search_query: Поисковый запрос для поиска вакансий
            **kwargs: Дополнительные параметры поиска (зарплата, опыт и т.д.)

        Returns:
            List[Dict]: Список найденных вакансий в формате словарей
        """

    @abstractmethod
    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """
        Валидация структуры данных вакансии.

        Проверяет, что вакансия содержит все необходимые поля
        и соответствует ожидаемой структуре данных.

        Args:
            vacancy: Словарь с данными вакансии для валидации

        Returns:
            bool: True если структура валидна, False иначе
        """

    def clear_cache(self, source: str) -> None:
        """
        Очистка кэша для конкретного источника

        Args:
            source: Название источника (hh, sj)
        """
        try:
            cache_dir = f"data/cache/{source}"
            if os.path.exists(cache_dir):
                import shutil

                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                logger.info(f"Кэш {source} очищен")
            else:
                # Создаем папку кэша если её нет
                os.makedirs(cache_dir, exist_ok=True)
                logger.info(f"Создана папка кэша {cache_dir}")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша {source}: {e}")
            raise
