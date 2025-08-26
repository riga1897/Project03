import logging
from typing import Dict, List, Optional

from src.api_modules.base_api import BaseJobAPI
from src.api_modules.cached_api import CachedAPI
from src.api_modules.get_api import APIConnector
from src.config.api_config import APIConfig
from src.config.target_companies import get_target_company_ids
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
            # Приводим поисковый запрос к нижнему регистру для регистронезависимого поиска
            search_query_lower = search_query.lower() if search_query else search_query
            params = self._config.hh_config.get_params(text=search_query_lower, page=page, **kwargs)

            data = self._CachedAPI__connect_to_api(self.BASE_URL, params, "hh")
            items = data.get("items", [])

            # Добавляем источник к каждой вакансии и валидируем
            validated_items = []
            for item in items:
                # Устанавливаем источник сразу при получении данных
                item["source"] = "hh.ru"
                if self._validate_vacancy(item):
                    validated_items.append(item)

            return validated_items

        except Exception as e:
            logger.error(f"Failed to get vacancies page {page}: {e}")
            return []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение вакансий с HH.ru с многоуровневым кэшированием

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список вакансий
        """
        try:
            logger.info(f"Начинаем поиск вакансий по запросу: '{search_query}' с параметрами: {kwargs}")

            # Используем кэшированный API для получения данных
            vacancies = self._cached_api.get_vacancies(search_query, **kwargs)

            if not vacancies:
                logger.warning(f"Вакансии по запросу '{search_query}' не найдены")
                return []

            logger.info(f"Получено {len(vacancies)} вакансий по запросу '{search_query}'")
            return vacancies

        except KeyboardInterrupt:
            logger.info("Получение вакансий прервано пользователем")
            print("\nПолучение вакансий остановлено.")
            return []
        except Exception as e:
            logger.error(f"Ошибка получения вакансий: {e}")
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

    def get_vacancies_from_target_companies(self, search_query: str = "", **kwargs) -> List[Dict]:
        """
        Получение вакансий только от целевых компаний

        Args:
            search_query: Поисковый запрос (опционально)
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список вакансий от целевых компаний
        """
        target_company_ids = get_target_company_ids()
        all_vacancies = []

        logger.info(f"Получение вакансий от {len(target_company_ids)} целевых компаний")

        for company_id in target_company_ids:
            try:
                # Получаем вакансии конкретной компании
                company_vacancies = self.get_vacancies_by_company(company_id, search_query, **kwargs)
                if company_vacancies:
                    all_vacancies.extend(company_vacancies)
                    logger.debug(f"Получено {len(company_vacancies)} вакансий от компании {company_id}")
            except Exception as e:
                logger.warning(f"Ошибка получения вакансий от компании {company_id}: {e}")
                continue

        logger.info(f"Всего получено {len(all_vacancies)} вакансий от целевых компаний")

        # Показываем статистику по компаниям (используем сырые данные)
        if all_vacancies:
            from src.utils.vacancy_stats import VacancyStats
            VacancyStats.display_company_stats(all_vacancies, "HH.ru - Целевые компании")

        return self._deduplicate_vacancies(all_vacancies)

    def get_vacancies_by_company(self, company_id: str, search_query: str = "", **kwargs) -> List[Dict]:
        """
        Получение вакансий конкретной компании

        Args:
            company_id: ID компании на HH.ru
            search_query: Поисковый запрос (опционально)
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список вакансий компании
        """
        try:
            # Добавляем фильтр по компании в параметры
            kwargs['employer_id'] = company_id

            if search_query:
                search_query_lower = search_query.lower()
            else:
                search_query_lower = ""

            # Получаем метаданные для определения количества страниц
            initial_params = self._config.hh_config.get_params(
                text=search_query_lower, page=0, per_page=1, **kwargs
            )
            initial_data = self._CachedAPI__connect_to_api(self.BASE_URL, initial_params, "hh")

            found_vacancies = initial_data.get("found", 0)
            if not found_vacancies:
                logger.debug(f"Компания {company_id}: вакансий не найдено")
                return []

            # Правильно рассчитываем количество страниц
            actual_pages = initial_data.get("pages", 1)
            max_pages = self._config.get_pagination_params(**kwargs)["max_pages"]
            per_page = self._config.hh_config.get_params(**kwargs).get("per_page", 50)

            # Если вакансий меньше чем per_page, то страница только одна
            if found_vacancies <= per_page:
                total_pages = 1
            else:
                total_pages = min(actual_pages, max_pages)

            logger.debug(f"Компания {company_id}: найдено {found_vacancies} вакансий, обрабатываем {total_pages} страниц")

            # Получаем все страницы только если есть что обрабатывать
            if total_pages > 0:
                results = self._paginator.paginate(
                    fetch_func=lambda p: self.get_vacancies_page_by_company(company_id, search_query, p, **kwargs),
                    total_pages=total_pages
                )
            else:
                results = []

            return results

        except Exception as e:
            logger.error(f"Ошибка получения вакансий компании {company_id}: {e}")
            return []

    def get_vacancies_page_by_company(self, company_id: str, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """
        Получение одной страницы вакансий конкретной компании

        Args:
            company_id: ID компании на HH.ru
            search_query: Поисковый запрос
            page: Номер страницы
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список валидных вакансий со страницы
        """
        try:
            # Добавляем фильтр по компании
            kwargs['employer_id'] = company_id

            search_query_lower = search_query.lower() if search_query else ""
            params = self._config.hh_config.get_params(text=search_query_lower, page=page, **kwargs)

            data = self._CachedAPI__connect_to_api(self.BASE_URL, params, "hh")
            items = data.get("items", [])

            # Добавляем источник к каждой вакансии и валидируем
            validated_items = []
            for item in items:
                item["source"] = "hh.ru"
                if self._validate_vacancy(item):
                    validated_items.append(item)

            return validated_items

        except Exception as e:
            logger.error(f"Ошибка получения страницы {page} для компании {company_id}: {e}")
            return []

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очищает кэш API

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросам.
        """
        super().clear_cache("hh")