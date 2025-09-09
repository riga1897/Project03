import logging
from typing import Any, Dict, List, Optional

from src.config.sj_api_config import SJAPIConfig
from src.config.target_companies import TargetCompanies
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

    BASE_URL = "https://api.superjob.ru/2.0/vacancies/"
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
        from src.config.api_config import APIConfig
        api_config = APIConfig()
        self.connector = APIConnector(api_config)

        # Настраиваем специфичные для SJ заголовки
        api_key = (
            EnvLoader.get_env_var("SUPERJOB_API_KEY", "v3.r.137440105.example.test_tool")
            or "v3.r.137440105.example.test_tool"
        )
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
        return {"objects": [], "total": 0, "more": False}

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

    def _connect(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        Выполнение HTTP-запроса к API SuperJob через CachedAPI (аналогично HH API)

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Dict: Ответ API или пустой ответ в случае ошибки
        """
        if params is None:
            params = {}
        try:
            # Делаем запрос к SuperJob API через CachedAPI (аналогично HH)
            data = self._connect_to_api(url, params, "sj")
            return data
        except Exception as e:
            logger.error(f"Ошибка при подключении к API: {e}")
            return self._get_empty_response()

    def get_vacancies_page(self, search_query: str, page: int = 0, **kwargs: Any) -> List[Dict]:
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

            data = self._connect(self.BASE_URL, params)
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

    def get_vacancies(self, search_query: str, **kwargs: Any) -> List[Dict]:
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
            # Проверяем API ключ
            api_key = EnvLoader.get_env_var("SUPERJOB_API_KEY", "")
            if not api_key or api_key == "v3.r.137440105.example.test_tool":
                logger.warning("SuperJob API ключ не настроен или используется тестовый ключ")
                logger.info(
                    "Для полной функциональности настройте реальный API ключ через пункт меню '9. Настройка SuperJob API'"
                )
                return []

            # Приводим поисковый запрос к нижнему регистру для регистронезависимого поиска
            search_query_lower = search_query.lower() if search_query else search_query

            # Получаем первую страницу для метаданных
            first_page_params = self.config.get_params(keyword=search_query_lower, page=0, **kwargs)

            initial_data = self._connect(self.BASE_URL, first_page_params)

            if not initial_data or not initial_data.get("total", 0):
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
            logger.error(f"Failed to get vacancies from SuperJob: {e}")
            if "403" in str(e) or "401" in str(e):
                logger.warning("Возможно, проблема с API ключом SuperJob")
            return []

    def get_companies(self, **kwargs: Any) -> List[Dict]:
        """
        Получение списка компаний с SuperJob

        Note:
            SuperJob API НЕ поддерживает поиск по ID организации.
            Используется список целевых компаний из конфигурации.
            Для поиска по ID организации используйте HeadHunter API.

        Args:
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Список компаний
        """
        try:
            # SJ API не предоставляет прямой метод для получения компаний
            # Используем целевые компании из конфигурации
            target_companies_list = TargetCompanies.get_all_companies()
            companies = []
            for company_info in target_companies_list:
                companies.append({"id": company_info.sj_id, "name": company_info.name, "source": "superjob.ru"})
            return companies
        except Exception as e:
            logger.error(f"Ошибка получения компаний с SuperJob: {str(e)}")
            return []

    def _deduplicate_vacancies(self, vacancies: List[Dict], source: Optional[str] = None) -> List[Dict]:
        """
        Удаление дублирующихся вакансий SJ с фильтрацией по целевым компаниям

        Args:
            vacancies: Список вакансий с SuperJob

        Returns:
            List[Dict]: Список уникальных вакансий от целевых компаний
        """
        # Базовая дедупликация без использования родительского метода
        seen_ids = set()
        unique_vacancies = []
        for vacancy in vacancies:
            vacancy_id = vacancy.get("id") or vacancy.get("link", "")
            if vacancy_id and vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                unique_vacancies.append(vacancy)
        return unique_vacancies

    def get_vacancies_with_deduplication(self, search_query: str, **kwargs: Any) -> List[Dict]:
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

    def get_vacancies_from_target_companies(self, search_query: str = "", **kwargs: Any) -> List[Dict]:
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
            api_key = EnvLoader.get_env_var("SUPERJOB_API_KEY", "")
            if not api_key or api_key == "v3.r.137440105.example.test_tool":
                logger.warning("SuperJob API ключ не настроен, пропускаем")
                return []

            # SuperJob не имеет прямого фильтра по ID компаний в API
            # Используем строгую фильтрацию только по ID целевых компаний
            logger.info("SuperJob: получение всех вакансий для строгой ID-based фильтрации")

            all_vacancies = self.get_vacancies(search_query, **kwargs)

            if not all_vacancies:
                logger.info("SuperJob: не найдено вакансий для фильтрации")
                return []

            # Строгая фильтрация только по SuperJob ID целевых компаний
            try:
                target_sj_ids = TargetCompanies.get_sj_ids()
                target_vacancies = []

                # Используем парсер для извлечения ID компании
                from src.vacancies.parsers.sj_parser import SuperJobParser
                parser = SuperJobParser()
                
                for vacancy in all_vacancies:
                    try:
                        # Используем метод парсера для извлечения ID компании
                        company_id = parser._extract_company_id(vacancy)
                        
                        # Отладочная информация для первых нескольких вакансий
                        if len(target_vacancies) < 3:
                            logger.debug(f"Вакансия {vacancy.get('id')}: company_id='{company_id}', в целевых: {company_id in target_sj_ids if company_id else False}")
                            logger.debug(f"client: {vacancy.get('client', {})}")
                            logger.debug(f"id_client: {vacancy.get('id_client')}")
                        
                        # Проверяем строгое совпадение с целевыми ID
                        if company_id and company_id in target_sj_ids:
                            target_vacancies.append(vacancy)
                    except Exception as e:
                        logger.warning(f"Ошибка при обработке вакансии: {e}")
                        continue

                logger.info(
                    f"SuperJob: отфильтровано {len(target_vacancies)} вакансий от целевых компаний по строгому ID-matching"
                )

                # Показываем статистику
                if target_vacancies:
                    try:
                        from src.utils.vacancy_stats import VacancyStats

                        stats = VacancyStats()
                        stats.display_company_stats(target_vacancies)
                    except Exception as e:
                        logger.warning(f"Ошибка при отображении статистики: {e}")

                return target_vacancies

            except Exception as e:
                logger.error(f"Ошибка при фильтрации по целевым компаниям: {e}")
                return all_vacancies  # Возвращаем все вакансии если фильтрация не удалась

        except Exception as e:
            if "403" in str(e) or "ключ" in str(e).lower():
                logger.warning(f"SuperJob API ключ недействителен или не настроен: {e}")
                logger.info(
                    "Для использования SuperJob настройте API ключ через пункт меню '9. Настройка SuperJob API'"
                )
            else:
                logger.error(f"Ошибка SuperJob API: {e}")
            return []

    def clear_cache(self, source: str) -> None:
        """
        Очищает кэш API (используя общий механизм как в HH API)

        Удаляет все сохраненные ответы API из кэша для освобождения места
        и обеспечения получения актуальных данных при следующих запросах.
        """
        super().clear_cache(source)
