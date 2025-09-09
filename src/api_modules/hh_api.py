import logging
from typing import Any, Dict, List, Optional

from src.api_modules.base_api import BaseJobAPI
from src.api_modules.cached_api import CachedAPI
from src.api_modules.get_api import APIConnector
from src.config.hh_api_config import HHAPIConfig
from src.config.target_companies import TargetCompanies
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

    def __init__(self, config: Optional[HHAPIConfig] = None):
        """
        Инициализация API клиента HeadHunter

        Args:
            config: Конфигурация HH API (если None, используется конфигурация по умолчанию)
        """
        super().__init__(self.DEFAULT_CACHE_DIR)  # Инициализируем кэш через родительский класс
        self.config = config or HHAPIConfig()
        # Создаем APIConfig для APIConnector
        from src.config.api_config import APIConfig
        api_config = APIConfig()
        self.connector = APIConnector(api_config)
        self._paginator = Paginator()
        # Централизованное управление целевыми компаниями
        self._target_company_ids = TargetCompanies.get_hh_ids()

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

    def _connect(self, url: str, params: Optional[Dict] = None) -> Dict:
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
            # Делаем запрос к HH API через CachedAPI
            data = self._connect_to_api(url, params, "hh")
            return data
        except Exception as e:
            logger.error(f"Ошибка при подключении к API: {e}")
            return self._get_empty_response()

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs: Any) -> List[Dict]:
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
            params = self.config.get_params(text=search_query_lower, page=page, **kwargs)

            data = self._connect_to_api(self.BASE_URL, params, "hh")
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

    def get_vacancies_by_employer_id(self, employer_id: str, **kwargs: Any) -> List[Dict]:
        """
        Получение вакансий по ID работодателя (только для HH API)
        
        Args:
            employer_id: ID работодателя в системе HH.ru
            **kwargs: Дополнительные параметры поиска
            
        Returns:
            List[Dict]: Список вакансий работодателя
            
        Note:
            Эта функция доступна только для HH API.
            SuperJob API не поддерживает поиск по ID организации.
        """
        try:
            params = self.config.get_params(employer_id=employer_id, **kwargs)
            
            all_vacancies = []
            page = 0
            max_pages = self.config.get_pagination_params(**kwargs)["max_pages"]
            
            while page < max_pages:
                params['page'] = page
                data = self._connect_to_api(self.BASE_URL, params, "hh")
                
                if not data or 'items' not in data:
                    break
                    
                items = data.get('items', [])
                if not items:
                    break
                
                # Добавляем источник и валидируем
                validated_items = []
                for item in items:
                    item["source"] = "hh.ru"
                    if self._validate_vacancy(item):
                        validated_items.append(item)
                
                all_vacancies.extend(validated_items)
                
                # Проверяем, есть ли еще страницы
                if len(items) < params.get('per_page', 50):
                    break
                    
                page += 1
            
            logger.info(f"Получено {len(all_vacancies)} вакансий для работодателя {employer_id}")
            return all_vacancies
            
        except Exception as e:
            logger.error(f"Ошибка получения вакансий по ID работодателя {employer_id}: {e}")
            return []

    def get_companies(self, **kwargs: Any) -> List[Dict]:
        """
        Получение списка компаний с HeadHunter

        Args:
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список компаний
        """
        try:
            # HH API не предоставляет прямой метод для получения компаний
            # Используем целевые компании из конфигурации
            target_companies = TargetCompanies()
            companies = []
            for company_info in target_companies.get_all_companies():
                companies.append({"id": company_info.hh_id, "name": company_info.name, "source": "hh.ru"})
            return companies
        except Exception as e:
            logger.error(f"Ошибка получения компаний с HH: {e}")
            return []

    def get_vacancies(
        self, search_query: Optional[str] = None, per_page: int = 100, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Получает вакансии с HeadHunter API

        Args:
            search_query: Поисковый запрос
            per_page: Количество вакансий на странице (по умолчанию 100)
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict[str, Any]]: Список словарей с данными вакансий
        """
        try:
            # Получаем базовые параметры от конфигурации
            params = self.config.get_params(text=search_query, **kwargs)
            # Устанавливаем per_page отдельно, чтобы избежать дублирования
            params["per_page"] = per_page

            # Получаем метаданные для определения количества страниц
            initial_params = self.config.get_params(
                text=search_query.lower() if search_query else "", page=0, per_page=1, **kwargs
            )
            initial_data = self._connect_to_api(self.BASE_URL, initial_params, "hh")

            found_vacancies = initial_data.get("found", 0)
            if not found_vacancies:
                logger.warning(f"Вакансии по запросу '{search_query}' не найдены")
                return []

            # Рассчитываем количество страниц
            actual_pages = initial_data.get("pages", 1)
            max_pages = self.config.get_pagination_params(**kwargs)["max_pages"]

            per_page_from_params = params.get("per_page", 50)

            if found_vacancies <= per_page_from_params:
                total_pages = 1
            else:
                total_pages = min(actual_pages, max_pages)

            logger.info(f"Найдено {found_vacancies} вакансий, обрабатываем {total_pages} страниц")

            # Получаем все страницы
            if total_pages > 0:
                results = self._paginator.paginate(
                    fetch_func=lambda p: self.get_vacancies_page(search_query or "", p, **kwargs),
                    total_pages=total_pages,
                )
            else:
                results = []

            logger.info(f"Получено {len(results)} вакансий по запросу '{search_query}'")
            return results

        except KeyboardInterrupt:
            logger.info("Получение вакансий прервано пользователем")
            print("\nПолучение вакансий остановлено.")
            return []
        except Exception as e:
            logger.error(f"Ошибка получения вакансий: {e}")
            return []

    def get_vacancies_with_deduplication(self, search_query: str, **kwargs: Any) -> List[Dict]:
        """
        Получение вакансий с HH.ru БЕЗ дедупликации.
        Дедупликация выполняется централизованно в PostgresSaver.

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры

        Returns:
            List[Dict]: Список вакансий (дедупликация будет выполнена позже)
        """
        return self.get_vacancies(search_query, **kwargs)

    def get_vacancies_from_target_companies(self, search_query: str = "", **kwargs: Any) -> List[Dict]:
        """
        Получение вакансий только от целевых компаний

        Args:
            search_query: Поисковый запрос (опционально)
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список вакансий от целевых компаний
        """
        all_vacancies = []

        logger.info(f"Получение вакансий от {len(self._target_company_ids)} целевых компаний")

        for company_id in self._target_company_ids:
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

            stats = VacancyStats()
            stats.display_company_stats(all_vacancies, "HH.ru - Целевые компании")
            logger.info(f"Возвращаем {len(all_vacancies)} вакансий от целевых компаний")
        else:
            logger.warning("Получен пустой список вакансий от целевых компаний")

        return all_vacancies

    def get_vacancies_by_company(self, company_id: str, search_query: str = "", **kwargs: Any) -> List[Dict]:
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
            kwargs["employer_id"] = company_id

            if search_query:
                search_query_lower = search_query.lower()
            else:
                search_query_lower = ""

            # Получаем метаданные для определения количества страниц
            initial_params = self.config.get_params(text=search_query_lower, page=0, per_page=1, **kwargs)
            initial_data = self._connect_to_api(self.BASE_URL, initial_params, "hh")

            found_vacancies = initial_data.get("found", 0)
            if not found_vacancies:
                logger.debug(f"Компания {company_id}: вакансий не найдено")
                return []

            # Правильно рассчитываем количество страниц
            actual_pages = initial_data.get("pages", 1)
            max_pages = self.config.get_pagination_params(**kwargs)["max_pages"]
            per_page = self.config.get_params(**kwargs).get("per_page", 50)

            # Если вакансий меньше чем per_page, то страница только одна
            if found_vacancies <= per_page:
                total_pages = 1
            else:
                total_pages = min(actual_pages, max_pages)

            logger.debug(
                f"Компания {company_id}: найдено {found_vacancies} вакансий, обрабатываем {total_pages} страниц"
            )

            # Получаем все страницы только если есть что обрабатывать
            if total_pages > 0:
                results = self._paginator.paginate(
                    fetch_func=lambda p: self.get_vacancies_page_by_company(company_id, search_query, p, **kwargs),
                    total_pages=total_pages,
                )
            else:
                results = []

            return results

        except Exception as e:
            logger.error(f"Ошибка получения вакансий компании {company_id}: {e}")
            return []

    def get_vacancies_page_by_company(
        self, company_id: str, search_query: str, page: int = 0, **kwargs: Any
    ) -> List[Dict]:
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
            kwargs["employer_id"] = company_id

            search_query_lower = search_query.lower() if search_query else ""
            params = self.config.get_params(text=search_query_lower, page=page, **kwargs)

            data = self._connect_to_api(self.BASE_URL, params, "hh")
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

    def is_target_company(self, company_id: str) -> bool:
        """
        Проверяет, является ли компания целевой
        
        Args:
            company_id: ID компании для проверки
            
        Returns:
            bool: True если компания целевая, False иначе
        """
        return company_id in self._target_company_ids

    def get_target_company_ids(self) -> List[str]:
        """
        Возвращает список ID целевых компаний
        
        Returns:
            List[str]: Список ID целевых компаний
        """
        return self._target_company_ids.copy()

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очищает кэш API

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросам.
        """
        super().clear_cache("hh")
