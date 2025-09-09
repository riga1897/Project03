import logging
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from src.vacancies.models import Vacancy
from src.vacancies.parsers.sj_parser import SuperJobParser

from .hh_api import HeadHunterAPI
from .sj_api import SuperJobAPI

logger = logging.getLogger(__name__)


class UnifiedAPI:
    """Унифицированный API для работы с несколькими источниками вакансий"""

    def __init__(self) -> None:
        """Инициализация унифицированного API.

        Создает экземпляры HeadHunter и SuperJob API, а также настраивает
        парсер и словарь источников для удобного доступа к API.
        """
        self.hh_api = HeadHunterAPI()
        self.sj_api = SuperJobAPI()
        self.parser = SuperJobParser()
        # Добавляем словарь для хранения API по источникам
        self.apis = {
            "hh": self.hh_api,
            "sj": self.sj_api,
        }

    def get_vacancies_from_sources(
        self, search_query: str, sources: Optional[List[str]] = None, **kwargs: dict[str, Any]
    ) -> List[Dict]:
        """
        Получение вакансий из выбранных источников с фильтрацией по целевым компаниям и дедупликацией

        Args:
            search_query: Поисковый запрос
            sources: Список источников ['hh', 'sj']
            **kwargs: Дополнительные параметры для API

        Returns:
            List[Dict]: Список всех уникальных вакансий от целевых компаний
        """
        if sources is None:
            sources = self.get_available_sources()
        else:
            sources = self.validate_sources(sources)

        all_vacancies = []

        # Получение из HeadHunter
        if "hh" in sources:
            try:
                logger.info(f"Получение вакансий с HH.ru по запросу: '{search_query}'")
                # Передаем только поддерживаемые параметры к HH API
                hh_data = self.hh_api.get_vacancies(search_query)
                if hh_data:
                    all_vacancies.extend(hh_data)
                    logger.info(f"HH.ru: получено {len(hh_data)} вакансий")
            except Exception as e:
                logger.error(f"Ошибка получения вакансий с HH.ru: {e}")

        # Получение от SuperJob
        if "sj" in sources:
            try:
                # Синхронизируем параметры периода между API
                sj_kwargs = kwargs.copy()
                if "period" in kwargs:
                    sj_kwargs["published"] = kwargs["period"]
                    sj_kwargs.pop("period", None)

                sj_data = self.sj_api.get_vacancies(search_query, **sj_kwargs)
                if sj_data:
                    all_vacancies.extend(sj_data)
                    logger.info(f"SuperJob: получено {len(sj_data)} вакансий")
            except Exception as e:
                logger.error(f"Ошибка получения вакансий с SuperJob: {e}")

        if not all_vacancies:
            logger.info("Вакансии не найдены")
            return []

        # УНИФИЦИРОВАННАЯ фильтрация и дедупликация
        logger.info(f"Унифицированная обработка: получено {len(all_vacancies)} вакансий всего")

        # 1. Фильтрация по целевым компаниям (едина для всех источников)
        filtered_vacancies = self._unified_filter_by_target_companies(all_vacancies)

        # 2. Единая дедупликация для всех источников
        unique_vacancies = self._unified_deduplicate(filtered_vacancies)

        if unique_vacancies:
            logger.info(f"Финальный результат: {len(unique_vacancies)} уникальных вакансий от целевых компаний")
            return unique_vacancies
        else:
            logger.warning(f"После обработки не найдено вакансий от целевых компаний из {len(all_vacancies)} исходных")
            return []

    def _unified_filter_by_target_companies(self, vacancies: List[Dict]) -> List[Dict]:
        """
        УНИФИЦИРОВАННАЯ фильтрация вакансий по целевым компаниям для ВСЕХ источников

        Логика:
        - HH.ru: проверяем employer.id в hh_ids
        - SuperJob: проверяем client.id/id_client в sj_ids
        - Другие источники: можно добавить в будущем

        Args:
            vacancies: Список всех вакансий от разных источников

        Returns:
            List[Dict]: Отфильтрованный список вакансий от целевых компаний
        """
        if not vacancies:
            return []

        try:
            # Получаем списки ID целевых компаний для разных источников
            from src.config.target_companies import TargetCompanies

            target_hh_ids = set(TargetCompanies.get_hh_ids())
            target_sj_ids = set(TargetCompanies.get_sj_ids())

            filtered_vacancies = []

            for vacancy in vacancies:
                try:
                    is_target_company = False

                    # 1. HH.ru формат: employer.id
                    if "employer" in vacancy and vacancy["employer"]:
                        employer_id = str(vacancy["employer"].get("id", ""))
                        if employer_id in target_hh_ids:
                            is_target_company = True

                    # 2. SuperJob формат: client.id или id_client
                    if not is_target_company:
                        # Используем SuperJob парсер для надежного извлечения ID
                        from src.vacancies.parsers.sj_parser import SuperJobParser

                        parser = SuperJobParser()
                        try:
                            company_id = parser._extract_company_id(vacancy)
                            if company_id and company_id in target_sj_ids:
                                is_target_company = True
                        except BaseException:
                            pass

                    if is_target_company:
                        filtered_vacancies.append(vacancy)

                except Exception as e:
                    logger.warning(f"Ошибка при проверке вакансии на целевую компанию: {e}")
                    continue

            logger.info(
                f"Унифицированная фильтрация: найдено {len(filtered_vacancies)} вакансий от целевых компаний из {len(vacancies)} исходных"
            )
            return filtered_vacancies

        except Exception as e:
            logger.error(f"Критическая ошибка при фильтрации по целевым компаниям: {e}")
            return []

    def _unified_deduplicate(self, vacancies: List[Dict]) -> List[Dict]:
        """
        ЕДИНАЯ дедупликация вакансий со всех источников

        Логика:
        - Используем ID вакансий как ключи уникальности
        - HH.ru: используем поле 'id'
        - SuperJob: используем поле 'id'

        Args:
            vacancies: Отфильтрованные вакансии от целевых компаний

        Returns:
            List[Dict]: Дедуплицированный список вакансий
        """
        if not vacancies:
            return []

        try:
            seen_ids = set()
            unique_vacancies = []

            for vacancy in vacancies:
                try:
                    # Извлекаем ID вакансии
                    vacancy_id = vacancy.get("id")
                    if not vacancy_id:
                        continue

                    # Создаем уникальный ключ с префиксом источника
                    # Это позволяет иметь одинаковые ID у разных источников
                    source_prefix = "hh" if "employer" in vacancy else "sj"
                    unique_key = f"{source_prefix}_{vacancy_id}"

                    if unique_key not in seen_ids:
                        seen_ids.add(unique_key)
                        unique_vacancies.append(vacancy)

                except Exception as e:
                    logger.warning(f"Ошибка при дедупликации вакансии: {e}")
                    continue

            logger.info(
                f"Единая дедупликация: осталось {len(unique_vacancies)} уникальных вакансий из {len(vacancies)} отфильтрованных"
            )
            return unique_vacancies

        except Exception as e:
            logger.error(f"Критическая ошибка при дедупликации: {e}")
            return vacancies  # Возвращаем исходный список при ошибке

    def get_hh_vacancies(self, query: str, **kwargs: Any) -> List[Vacancy]:
        """Получение вакансий только с HH.ru с дедупликацией"""
        try:
            hh_data = self.hh_api.get_vacancies_with_deduplication(query, **kwargs)
            return [Vacancy.from_dict(item) for item in hh_data]
        except Exception as e:
            logger.error(f"Ошибка получения вакансий HH: {e}")
            return []

    def get_sj_vacancies(self, query: str, **kwargs: Any) -> List[Vacancy]:
        """Получение вакансий только с SuperJob с дедупликацией"""
        try:
            # Синхронизируем параметры периода
            sj_kwargs = kwargs.copy()
            if "period" in kwargs:
                # HH использует 'period', SuperJob использует 'published'
                sj_kwargs["published"] = kwargs["period"]
                sj_kwargs.pop("period", None)  # Удаляем исходный параметр

            sj_data = self.sj_api.get_vacancies_with_deduplication(query, **sj_kwargs)

            # Парсим данные SuperJob в объекты SuperJobVacancy
            if sj_data:

                print(f"Парсинг {len(sj_data)} вакансий SuperJob...")
                sj_vacancies_raw = self.parser.parse_vacancies(sj_data)

                # Конвертируем SuperJobVacancy в унифицированный формат
                sj_vacancies = []
                print("Конвертация вакансий SuperJob в унифицированный формат...")

                with tqdm(total=len(sj_vacancies_raw), desc="Конвертация SJ", unit="вакансия") as pbar:
                    for sj_vac in sj_vacancies_raw:
                        try:
                            unified_data = self.parser.convert_to_unified_format(sj_vac)
                            vacancy = Vacancy.from_dict(unified_data)
                            sj_vacancies.append(vacancy)
                        except Exception as e:
                            logger.warning(f"Ошибка конвертации вакансии SuperJob: {e}")
                        finally:
                            pbar.update(1)

                return sj_vacancies
            return []
        except Exception as e:
            logger.error(f"Ошибка получения вакансий SJ: {e}")
            return []

    def clear_cache(self, sources: Dict[str, bool]) -> None:
        """
        Очистка кэша для выбранных источников

        Args:
            sources: Словарь с источниками для очистки
        """
        cleared_sources = []

        try:
            if sources.get("hh", False):
                # Очищаем через API
                self.hh_api.clear_cache("hh")

                # Принудительно удаляем файлы кэша
                import glob
                import os

                cache_dir = "data/cache/hh"
                hh_files = glob.glob(f"{cache_dir}/hh_*.json")
                removed_count = 0

                for file in hh_files:
                    try:
                        os.remove(file)
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Не удалось удалить файл {file}: {e}")

                logger.info("Кэш HH.ru очищен")
                print(f"Кэш HH.ru очищен (удалено {removed_count} файлов)")
                cleared_sources.append("HH.ru")

            if sources.get("sj", False):
                # Очищаем через API
                self.sj_api.clear_cache("sj")

                # Принудительно удаляем файлы кэша
                import glob
                import os

                cache_dir = "data/cache/sj"
                sj_files = glob.glob(f"{cache_dir}/sj_*.json")
                removed_count = 0

                for file in sj_files:
                    try:
                        os.remove(file)
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Не удалось удалить файл {file}: {e}")

                logger.info("Кэш SuperJob очищен")
                print(f"Кэш SuperJob очищен (удалено {removed_count} файлов)")
                cleared_sources.append("SuperJob")

            if cleared_sources:
                print(f"Кэш успешно очищен для источников: {', '.join(cleared_sources)}")
            else:
                print("Не выбраны источники для очистки кэша")

        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")
            print(f"Ошибка при очистке кэша: {e}")
            raise

    def get_vacancies_from_target_companies(
        self, search_query: str = "", sources: Optional[List[str]] = None, **kwargs: Any
    ) -> List[Dict]:
        """
        Получение вакансий от целевых компаний из указанных источников

        Args:
            search_query: Поисковый запрос
            sources: Список источников (hh, sj). Если None - используются все доступные
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Dict]: Объединенный список вакансий от всех источников
        """
        all_vacancies = []

        # Определяем какие источники использовать
        if sources is None:
            sources = ["hh", "sj"]

        # Нормализуем названия источников
        normalized_sources = []
        for source in sources:
            if source.lower() in ["hh", "hh.ru", "headhunter"]:
                normalized_sources.append("hh")
            elif source.lower() in ["sj", "superjob", "superjob.ru"]:
                normalized_sources.append("sj")

        logger.info(f"Получение вакансий от целевых компаний из источников: {normalized_sources}")

        # HH.ru
        if "hh" in normalized_sources:
            try:
                logger.info("Поиск через HH.ru API...")
                hh_vacancies = self.hh_api.get_vacancies_from_target_companies(search_query, **kwargs)
                if hh_vacancies:
                    all_vacancies.extend(hh_vacancies)
                    logger.info(f"HH.ru: найдено {len(hh_vacancies)} вакансий")
                else:
                    logger.info("HH.ru: вакансий не найдено")
            except Exception as e:
                logger.error(f"Ошибка получения вакансий от HH.ru: {e}")

        # SuperJob - только если явно указан в источниках
        if "sj" in normalized_sources:
            try:
                logger.info("Поиск через SuperJob API...")
                sj_vacancies = self.sj_api.get_vacancies_from_target_companies(search_query, **kwargs)
                if sj_vacancies:
                    all_vacancies.extend(sj_vacancies)
                    logger.info(f"SuperJob: найдено {len(sj_vacancies)} вакансий")
                else:
                    logger.info("SuperJob: вакансий не найдено")
            except Exception as e:
                logger.error(f"Ошибка получения вакансий от SuperJob: {e}")

        # УНИФИЦИРОВАННАЯ фильтрация и дедупликация
        if all_vacancies:
            logger.info(f"Унифицированная обработка: получено {len(all_vacancies)} вакансий всего")

            # 1. Фильтрация по целевым компаниям (едина для всех источников)
            filtered_vacancies = self._unified_filter_by_target_companies(all_vacancies)

            # 2. Единая дедупликация для всех источников
            unique_vacancies = self._unified_deduplicate(filtered_vacancies)

            if unique_vacancies:
                logger.info(f"Финальный результат: {len(unique_vacancies)} уникальных вакансий от целевых компаний")

                # НЕ показываем статистику здесь - она будет после создания объектов Vacancy
                return unique_vacancies
            else:
                logger.warning(
                    f"После обработки не найдено вакансий от целевых компаний из {len(all_vacancies)} исходных"
                )
                return []
        else:
            logger.info("Вакансии не найдены")
            return []

    def clear_all_cache(self) -> None:
        """Очистка кэша всех API"""
        # Очищаем кэш каждого API отдельно, чтобы ошибка в одном не влияла на другой
        try:
            self.hh_api.clear_cache("hh")
            logger.info("Кэш HH.ru очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша HH.ru: {e}")

        try:
            self.sj_api.clear_cache("sj")
            logger.info("Кэш SuperJob очищен")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша SuperJob: {e}")

    def _display_unified_stats(self, vacancies: List[Dict], sources: List[str]) -> None:
        """
        Показывает статистику вакансий ПОСЛЕ правильной фильтрации

        Args:
            vacancies: Отфильтрованные вакансии от целевых компаний
            sources: Источники данных
        """
        try:
            from src.utils.vacancy_stats import VacancyStats

            # Определяем название для статистики
            if len(sources) == 1:
                if sources[0] == "hh":
                    source_name = "HH.ru - Целевые компании"
                elif sources[0] == "sj":
                    source_name = "SuperJob - Целевые компании"
                else:
                    source_name = f"{sources[0].upper()} - Целевые компании"
            else:
                source_name = "Все источники - Целевые компании"

            stats = VacancyStats()
            stats.display_company_stats(vacancies, source_name)

        except Exception as e:
            logger.warning(f"Ошибка при отображении унифицированной статистики: {e}")

    @staticmethod
    def get_available_sources() -> List[str]:
        """Получение списка доступных источников"""
        return ["hh", "sj"]

    def validate_sources(self, sources: List[str]) -> List[str]:
        """Валидация списка источников"""
        available = self.get_available_sources()
        valid_sources = [s for s in sources if s in available]

        if not valid_sources:
            logger.warning(f"Нет валидных источников в {sources}, используем все доступные")
            return available

        return valid_sources

    def get_all_vacancies(self, query: str, **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение всех вакансий из всех доступных источников"""
        # Используем переданные sources или все доступные по умолчанию
        sources_input = kwargs.pop("sources", None)
        if sources_input is None:
            validated_sources = self.get_available_sources()
        elif isinstance(sources_input, list):
            validated_sources = sources_input
        elif isinstance(sources_input, str):
            validated_sources = [sources_input]
        else:
            validated_sources = self.get_available_sources()
        return self.get_vacancies_from_sources(query, sources=validated_sources, **kwargs)

    def get_vacancies_from_all_sources(self, query: str, **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение вакансий из всех источников"""
        return self.get_vacancies_from_sources(query, sources=["hh", "sj"], **kwargs)

    def get_vacancies_from_source(
        self, search_query: str, source: str, **kwargs: dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Получает вакансии из указанного источника

        Args:
            search_query: Поисковый запрос
            source: Источник данных ('hh', 'sj')
            **kwargs: Дополнительные параметры

        Returns:
            List[Dict[str, Any]]: Список вакансий
        """
        # Нормализуем название источника
        source_mapping = {"hh.ru": "hh", "superjob.ru": "sj", "hh": "hh", "sj": "sj"}

        normalized_source = source_mapping.get(source, source)

        if normalized_source not in self.get_available_sources():
            logger.warning(f"Неизвестный источник: {source}")
            return []

        api = self.apis.get(normalized_source)
        if not api:
            logger.error(f"API для источника {normalized_source} не найден")
            return []

        try:
            return api.get_vacancies(search_query=search_query, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка получения вакансий из {normalized_source}: {e}")
            return []

    def get_companies_from_all_sources(self, **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение компаний из всех источников"""
        companies = []

        try:
            # Получаем компании с HH
            hh_companies = self.hh_api.get_companies(**kwargs)
            if hh_companies:
                companies.extend(hh_companies)

            # Получаем компании с SJ
            sj_companies = self.sj_api.get_companies(**kwargs)
            if sj_companies:
                companies.extend(sj_companies)

            logger.info(f"Получено {len(companies)} компаний из всех источников")
            return companies
        except Exception as e:
            logger.error(f"Ошибка при получении компаний из всех источников: {e}")
            return []

    def get_companies_from_source(self, source: str, **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение компаний из определенного источника"""
        try:
            if source.lower() == "hh":
                return self.hh_api.get_companies(**kwargs)
            elif source.lower() in ["sj", "superjob"]:
                return self.sj_api.get_companies(**kwargs)
            else:
                logger.warning(f"Неизвестный источник: {source}")
                return []
        except Exception as e:
            logger.error(f"Ошибка при получении компаний из источника {source}: {e}")
            return []

    def search_with_multiple_keywords(self, keywords: List[str], **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Поиск с несколькими ключевыми словами"""
        all_results = []

        for keyword in keywords:
            try:
                results = self.get_all_vacancies(keyword, **kwargs)
                if results:
                    all_results.extend(results)
            except Exception as e:
                logger.error(f"Ошибка при поиске по ключевому слову '{keyword}': {e}")
                continue

        # Дедуплицируем результаты по ID
        seen_ids = set()
        unique_results = []

        for result in all_results:
            vacancy_id = result.get("id") or result.get("vacancy_id")
            if vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                unique_results.append(result)

        logger.info(f"Найдено {len(unique_results)} уникальных вакансий по {len(keywords)} ключевым словам")
        return unique_results
