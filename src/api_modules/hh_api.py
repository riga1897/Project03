import logging
from typing import Dict, List, Optional

from src.api_modules.base_api import BaseJobAPI
from src.api_modules.cached_api import CachedAPI
from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig
from src.utils.paginator import Paginator

logger = logging.getLogger(__name__)


class HeadHunterAPI(CachedAPI, BaseJobAPI):
    """
    Расширенный клиент API HeadHunter с надежной обработкой ошибок и кэшированием

    Предоставляет полный набор функций для работы с API hh.ru:
    - Поиск вакансий с пагинацией
    - Многоуровневое кэширование
    - Дедупликация результатов
    - Обработка ошибок и восстановление
    """

    BASE_URL = "https://api.hh.ru/vacancies"
    DEFAULT_CACHE_DIR = "data/cache/hh"
    REQUIRED_VACANCY_FIELDS = {"name", "alternate_url", "salary"}

    def __init__(self, config: Optional[APIConfig] = None):
        """
        Инициализация API клиента HeadHunter

        Args:
            config: Конфигурация API (если None, используется конфигурация по умолчанию)
        """
        super().__init__(self.DEFAULT_CACHE_DIR)  # Инициализируем кэш через родительский класс
        self._config = config or APIConfig()
        self.connector = APIConnector(self._config)
        self._paginator = Paginator()

    def _get_empty_response(self) -> Dict:
        """
        Получить пустую структуру ответа для HH API

        Returns:
            Dict: Пустая структура ответа с полем 'items'
        """
        return {"items": []}

    def _validate_vacancy(self, vacancy: Dict) -> bool:
        """
        Валидация структуры вакансии

        Args:
            vacancy: Словарь с данными вакансии

        Returns:
            bool: True если структура валидна, False иначе
        """
        return (
            isinstance(vacancy, dict)
            and bool(vacancy.get("name"))  # У HH это поле 'name'
            and bool(vacancy.get("alternate_url"))  # У HH это поле 'alternate_url'
        )

    def __connect(self, url: str, params=None) -> Dict:
        """
        Выполнение HTTP-запроса к API HeadHunter

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Dict: Ответ API
        """
        if params is None:
            params = {}
        try:
            # Делаем запрос к HH API
            data = self.__connect(url, params)
            return data
        except Exception as e:
            logger.error(f"Ошибка при подключении к API: {e}")
            return {}

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """
        Получение и валидация одной страницы вакансий

        Args:
            search_query: Поисковый запрос
            page: Номер страницы (начиная с 0)
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список валидных вакансий со страницы
        """
        try:
            params = {"text": search_query, "page": page, **self._config.hh_config.get_params(**kwargs)}

            data = self._CachedAPI__connect_to_api(self.BASE_URL, params, "hh")
            items = data.get("items", [])

            return [item for item in items if self._validate_vacancy(item)]

        except Exception as e:
            logger.error(f"Failed to get vacancies page {page}: {e}")
            return []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение всех вакансий с пагинацией и валидацией

        Выполняет полный цикл получения вакансий:
        1. Получает метаданные о количестве страниц
        2. Обрабатывает все страницы с помощью пагинатора
        3. Валидирует каждую вакансию

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список всех найденных и валидных вакансий
        """
        try:
            # Initial request for metadata
            initial_data = self._CachedAPI__connect_to_api(
                self.BASE_URL, self._config.hh_config.get_params(text=search_query, page=0, per_page=1, **kwargs), "hh"
            )

            if not initial_data.get("found", 0):
                logger.info("No vacancies found for query")
                return []

            total_pages = min(initial_data.get("pages", 1), self._config.get_pagination_params(**kwargs)["max_pages"])

            logger.info(f"Found {initial_data.get('found')} vacancies " f"({total_pages} pages to process)")

            # Process all pages
            results = self._paginator.paginate(
                fetch_func=lambda p: self.get_vacancies_page(search_query, p, **kwargs), total_pages=total_pages
            )

            logger.info(f"Successfully processed {len(results)} vacancies")
            return results

        except KeyboardInterrupt:
            logger.info("Получение вакансий прервано пользователем")
            print("\nПолучение вакансий остановлено.")
            return []
        except Exception as e:
            logger.error(f"Failed to get vacancies: {e}")
            return []

    def _deduplicate_vacancies(self, vacancies: List[Dict], source: str = None) -> List[Dict]:
        """
        Удаление дублирующихся вакансий HH (используется базовая реализация)

        Args:
            vacancies: Список вакансий с HH.ru

        Returns:
            List[Dict]: Список уникальных вакансий
        """
        return super()._deduplicate_vacancies(vacancies, "hh")

    def get_vacancies_with_deduplication(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение вакансий с HH.ru

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры

        Returns:
            List[Dict]: Список уникальных вакансий
        """
        vacancies = self.get_vacancies(search_query, **kwargs)
        return self._deduplicate_vacancies(vacancies)

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очищает кэш API

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросам.
        """
        super().clear_cache("hh")
