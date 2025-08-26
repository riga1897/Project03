import logging
from typing import Dict, List, Optional

from src.config.api_config import APIConfig
from src.config.sj_api_config import SJAPIConfig
from src.config.target_companies import get_target_company_names
from src.utils.env_loader import EnvLoader
from src.utils.paginator import Paginator

from .base_api import BaseJobAPI
from .cached_api import CachedAPI
from .get_api import APIConnector

logger = logging.getLogger(__name__)


class SuperJobAPI(CachedAPI, BaseJobAPI):
    """
    API SuperJob для поиска вакансий с использованием общих механизмов

    Предоставляет полный набор функций для работы с API superjob.ru:
    - Поиск вакансий с пагинацией
    - Многоуровневое кэширование
    - Дедупликация результатов
    - Автоматическая обработка API ключей
    """

    BASE_URL = "https://api.superjob.ru/2.0/vacancies"
    DEFAULT_CACHE_DIR = "data/cache/sj"
    REQUIRED_VACANCY_FIELDS = {"profession", "link"}

    def __init__(self, config: Optional[SJAPIConfig] = None):
        """
        Инициализация SuperJob API

        Args:
            config: Конфигурация SuperJob API
        """
        super().__init__(self.DEFAULT_CACHE_DIR)  # Инициализируем кэш через родительский класс
        self.config = config or SJAPIConfig()

        # Используем общий APIConnector как в HH API
        api_config = APIConfig()
        self.connector = APIConnector(api_config)

        # Настраиваем специфичные для SJ заголовки
        api_key = EnvLoader.get_env_var("SUPERJOB_API_KEY", "v3.r.137440105.example.test_tool")
        self.connector.headers.update({"X-Api-App-Id": api_key, "User-Agent": "VacancySearchApp/1.0"})

        # Инициализируем общие компоненты как в HH API
        self._paginator = Paginator()

        # Логируем, какой ключ используется
        if api_key == "v3.r.137440105.example.test_tool":
            logger.warning(
                "Используется тестовый API ключ SuperJob. \
                Для полной функциональности добавьте реальный ключ \
                в переменную окружения SUPERJOB_API_KEY"
            )
        else:
            logger.info("Используется пользовательский API ключ SuperJob")

    def _get_empty_response(self) -> Dict:
        """
        Получить пустую структуру ответа для SJ API

        Returns:
            Dict: Пустая структура ответа с полем 'objects'
        """
        return {"objects": []}

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
            and bool(vacancy.get("profession"))  # У SJ это поле 'profession'
            and bool(vacancy.get("link"))  # У SJ это поле 'link'
        )

    def __connect(self, url: str, params: Dict = None) -> Dict:
        """
        Выполнение HTTP-запроса к API SuperJob

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Dict: Ответ API или пустой ответ в случае ошибки
        """
        try:
            # Делаем запрос к SuperJob API
            data = self.connector.connect(url, params)
            return data

        except Exception as e:
            logger.error(f"Ошибка при подключении к API: {e}")
            return self._get_empty_response()

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs) -> List[Dict]:
        """
        Получение одной страницы вакансий (адаптировано под паттерн HH API)

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
            params = self.config.get_params(keyword=search_query_lower, page=page, **kwargs)

            data = self._CachedAPI__connect_to_api(self.BASE_URL, params, "sj")
            items = data.get("objects", [])

            # Добавляем источник и валидируем как в HH API
            validated_items = []
            for item in items:
                # Устанавливаем источник сразу при получении данных
                item["source"] = "superjob.ru"
                if self._validate_vacancy(item):
                    validated_items.append(item)

            return validated_items

        except Exception as e:
            logger.error(f"Failed to get vacancies page {page}: {e}")
            return []

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение всех вакансий с пагинацией и валидацией (адаптировано под паттерн HH API)

        Выполняет полный цикл получения вакансий:
        1. Получает метаданные о количестве результатов
        2. Рассчитывает необходимое количество страниц
        3. Обрабатывает все страницы с помощью унифицированного пагинатора
        4. Возвращает дедуплицированный список вакансий

        Args:
            search_query: Поисковый запрос
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список всех найденных вакансий
        """
        try:
            # Приводим поисковый запрос к нижнему регистру для регистронезависимого поиска
            search_query_lower = search_query.lower() if search_query else search_query

            # Получаем первую страницу для метаданных
            first_page_params = self.config.get_params(keyword=search_query_lower, page=0, **kwargs)

            initial_data = self._CachedAPI__connect_to_api(
                self.BASE_URL,
                first_page_params,  # Минимальные данные сначала
                "sj",
            )

            if not initial_data.get("total", 0):
                logger.info("No vacancies found for query")
                return []

            total_found = initial_data.get("total", 0)

            # Используем общую логику пагинации как в HH API
            per_page = kwargs.get("count", 100)
            max_pages = kwargs.get("max_pages", 20)
            total_pages = min(max_pages, (total_found + per_page - 1) // per_page if total_found > 0 else 1)

            logger.info(f"Found {total_found} vacancies " f"({total_pages} pages to process)")

            # Process all pages using unified paginator (как в HH API)
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
        Удаление дублирующихся вакансий SJ с фильтрацией по целевым компаниям

        Args:
            vacancies: Список вакансий с SuperJob

        Returns:
            List[Dict]: Список уникальных вакансий от целевых компаний
        """
        return super()._deduplicate_vacancies(vacancies, "sj")

    def get_vacancies_with_deduplication(self, search_query: str, **kwargs) -> List[Dict]:
        """
        Получение вакансий с SuperJob с дедупликацией

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
        try:
            # Проверяем наличие API ключа
            if not self.config.sj_config.secret_key:
                logger.warning("SuperJob API ключ не настроен, пропускаем")
                return []

            # SuperJob не имеет фильтра по конкретным компаниям в API
            # Получаем все вакансии и фильтруем по целевым компаниям
            logger.info("SuperJob: получение всех вакансий для фильтрации по целевым компаниям")

            all_vacancies = self.get_vacancies(search_query, **kwargs)

            if not all_vacancies:
                return []

            # Фильтруем по целевым компаниям
            target_companies = get_target_company_names()
            target_vacancies = []

            for vacancy in all_vacancies:
                company_name = vacancy.get('firm_name', '').lower()
                # Проверяем совпадение с целевыми компаниями (нечеткое сравнение)
                for target_company in target_companies:
                    if target_company.lower() in company_name or company_name in target_company.lower():
                        target_vacancies.append(vacancy)
                        break

            logger.info(f"SuperJob: отфильтровано {len(target_vacancies)} вакансий от целевых компаний")

            # Показываем статистику
            if target_vacancies:
                from src.utils.vacancy_stats import VacancyStats
                VacancyStats.display_company_stats(target_vacancies, "SuperJob - Целевые компании")

            return target_vacancies

        except Exception as e:
            if "403" in str(e) or "ключ" in str(e).lower():
                logger.warning(f"SuperJob API ключ недействителен или не настроен: {e}")
                logger.info("Для использования SuperJob настройте API ключ через пункт меню '9. Настройка SuperJob API'")
            else:
                logger.error(f"Ошибка SuperJob API: {e}")
            return []

    def clear_cache(self, api_prefix: str) -> None:
        """
        Очищает кэш API (используя общий механизм как в HH API)

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросах.
        """
        super().clear_cache("sj")