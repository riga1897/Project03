import logging
from typing import Dict, List, Any

from src.vacancies.models import Vacancy
from src.vacancies.parsers.sj_parser import SuperJobParser

from .hh_api import HeadHunterAPI
from .sj_api import SuperJobAPI

from tqdm import tqdm


logger = logging.getLogger(__name__)


class UnifiedAPI:
    """Унифицированный API для работы с несколькими источниками вакансий"""

    def __init__(self):
        self.hh_api = HeadHunterAPI()
        self.sj_api = SuperJobAPI()
        self.parser = SuperJobParser()

    @staticmethod
    def _deduplicate_cross_platform(all_vacancies: List[Dict]) -> List[Dict]:
        """
        Межплатформенная дедупликация вакансий из разных источников

        Args:
            all_vacancies: Список всех вакансий из разных источников

        Returns:
            List[Dict]: Список вакансий без дублей между платформами
        """
        if not all_vacancies:
            return []



        seen = set()
        unique_vacancies = []

        print("Выполняется поиск дубликатов между платформами...")
        with tqdm(total=len(all_vacancies), desc="Поиск дубликатов", unit="вакансия") as pbar:
            for vacancy in all_vacancies:
                # Универсальная логика для дедупликации между источниками
                title = vacancy.get("name", vacancy.get("profession", "")).lower().strip()
                company = vacancy.get("employer", {}).get("name", vacancy.get("firm_name", "")).lower().strip()

                # Нормализуем зарплату для межплатформенного сравнения
                salary_key = ""
                if "salary" in vacancy and vacancy["salary"]:
                    salary = vacancy["salary"]
                    salary_from = salary.get("from", 0) or 0
                    salary_to = salary.get("to", 0) or 0
                    salary_key = f"{salary_from}-{salary_to}"
                elif "payment_from" in vacancy:
                    salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"

                dedup_key = (title, company, salary_key)

                if dedup_key not in seen:
                    seen.add(dedup_key)
                    unique_vacancies.append(vacancy)
                else:
                    logger.debug(f"Межплатформенный дубль отфильтрован: {title} в {company}")

                pbar.update(1)

        duplicates_found = len(all_vacancies) - len(unique_vacancies)
        if duplicates_found > 0:
            print(f"Найдено и удалено {duplicates_found} дубликатов между платформами")

        logger.info(f"Межплатформенная дедупликация: {len(all_vacancies)} -> {len(unique_vacancies)} вакансий")
        return unique_vacancies

    def get_vacancies_from_sources(self, search_query: str, sources: List[str] = None, **kwargs: dict[str, Any]) -> List[Dict]:
        """
        Получение вакансий из выбранных источников с дедупликацией

        Args:
            search_query: Поисковый запрос
            sources: Список источников ['hh', 'sj']
            **kwargs: Дополнительные параметры для API

        Returns:
            List[Dict]: Список всех уникальных вакансий
        """
        if sources is None:
            sources = self.get_available_sources()
        else:
            sources = self.validate_sources(sources)

        all_vacancies = []
        hh_vacancies = []
        sj_vacancies = []

        # Получение из HeadHunter
        if "hh" in sources:
            try:
                logger.info(f"Получение вакансий с HH.ru по запросу: '{search_query}'")
                hh_data = self.hh_api.get_vacancies(search_query, **kwargs)
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

        # SQL-дедупликация с фильтрацией по целевым компаниям
        if all_vacancies:
            logger.info(f"Всего получено {len(all_vacancies)} вакансий, применяем SQL-дедупликацию с фильтрацией")
            
            try:
                # Используем SQL для эффективной дедупликации с фильтрацией
                from src.api_modules.base_api import BaseJobAPI
                
                # Создаем временную реализацию BaseJobAPI для доступа к методу
                class TempAPI(BaseJobAPI):
                    def get_vacancies(self, search_query: str, **kwargs):
                        return []
                    def _validate_vacancy(self, vacancy):
                        return True
                
                base_api = TempAPI()
                all_vacancies = base_api._deduplicate_vacancies(all_vacancies, "unified")
                
                if all_vacancies:
                    print(f"✅ Найдено {len(all_vacancies)} уникальных вакансий от целевых компаний")
                else:
                    print("⚠️ Не найдено вакансий от целевых компаний")

            except Exception as e:
                logger.error(f"Ошибка SQL-дедупликации: {e}")
                print("⚠️ Переходим к простой дедупликации...")

                # Fallback: простая дедупликация с фильтрацией
                from src.config.target_companies import TargetCompanies
                TARGET_COMPANIES = TargetCompanies.get_all_companies()
                target_company_names = [company['name'].lower() for company in TARGET_COMPANIES]

                seen = set()
                unique_vacancies = []

                for vacancy in all_vacancies:
                    # Проверяем, является ли компания целевой
                    company = vacancy.get("employer", {}).get("name", vacancy.get("firm_name", "")).lower().strip()
                    
                    is_target = False
                    for target_name in target_company_names:
                        if target_name in company or company in target_name:
                            is_target = True
                            break

                    if is_target:
                        # Создаем ключ дедупликации
                        title = vacancy.get("name", vacancy.get("profession", "")).lower().strip()
                        
                        salary_key = ""
                        if "salary" in vacancy and vacancy["salary"]:
                            salary = vacancy["salary"]
                            salary_from = salary.get("from", 0) or 0
                            salary_to = salary.get("to", 0) or 0
                            salary_key = f"{salary_from}-{salary_to}"
                        elif "payment_from" in vacancy:
                            salary_key = f"{vacancy.get('payment_from', 0)}-{vacancy.get('payment_to', 0)}"

                        dedup_key = (title, company, salary_key)

                        if dedup_key not in seen:
                            seen.add(dedup_key)
                            unique_vacancies.append(vacancy)

                all_vacancies = unique_vacancies
                print(f"✅ Найдено {len(all_vacancies)} уникальных вакансий от целевых компаний (простая дедупликация)")

            return all_vacancies
        else:
            logger.info("Вакансии не найдены")
            return []

    def get_hh_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
        """Получение вакансий только с HH.ru с дедупликацией"""
        try:
            hh_data = self.hh_api.get_vacancies_with_deduplication(query, **kwargs)
            return [Vacancy.from_dict(item) for item in hh_data]
        except Exception as e:
            logger.error(f"Ошибка получения вакансий HH: {e}")
            return []

    def get_sj_vacancies(self, query: str, **kwargs) -> List[Vacancy]:
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
                from tqdm import tqdm

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
                import os
                import glob
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
                print(f"✅ Кэш HH.ru очищен (удалено {removed_count} файлов)")
                cleared_sources.append("HH.ru")

            if sources.get("sj", False):
                # Очищаем через API
                self.sj_api.clear_cache("sj")

                # Принудительно удаляем файлы кэша
                import os
                import glob
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
                print(f"✅ Кэш SuperJob очищен (удалено {removed_count} файлов)")
                cleared_sources.append("SuperJob")

            if cleared_sources:
                print(f"🎯 Кэш успешно очищен для источников: {', '.join(cleared_sources)}")
            else:
                print("⚠️ Не выбраны источники для очистки кэша")

        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")
            print(f"❌ Ошибка при очистке кэша: {e}")
            raise

    def get_vacancies_from_target_companies(self, search_query: str = "", sources: List[str] = None, **kwargs) -> List[Dict]:
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

        # Дедупликация только если есть вакансии
        if all_vacancies:
            unique_vacancies = self._deduplicate_cross_platform(all_vacancies)
            logger.info(f"Всего найдено {len(unique_vacancies)} уникальных вакансий от целевых компаний")
            return unique_vacancies
        else:
            logger.info("Вакансии от целевых компаний не найдены")
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
        sources = self.get_available_sources()
        return self.get_vacancies_from_sources(query, sources=sources, **kwargs)

    def get_vacancies_from_all_sources(self, query: str, **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение вакансий из всех источников"""
        return self.get_all_vacancies(query, sources=["hh", "sj"], **kwargs)

    def get_vacancies_from_source(self, query: str, source: str, **kwargs: dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение вакансий из определенного источника"""
        if source.lower() == "hh":
            return self.get_hh_vacancies(query, **kwargs)
        elif source.lower() in ["sj", "superjob"]:
            return self.get_sj_vacancies(query, **kwargs)
        else:
            logger.warning(f"Неизвестный источник: {source}")
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
            vacancy_id = result.get('id') or result.get('vacancy_id')
            if vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                unique_results.append(result)

        logger.info(f"Найдено {len(unique_results)} уникальных вакансий по {len(keywords)} ключевым словам")
        return unique_results