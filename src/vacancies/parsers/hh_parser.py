import json
import logging
from typing import Any, Dict, List, Optional

from src.models import Vacancy
from src.utils.cache import FileCache
from src.utils.salary import Salary
from src.vacancies.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


class HHParser(BaseParser):
    """Парсер для обработки данных вакансий с HeadHunter API"""

    requirements = None
    responsibilities = None

    def __init__(self, cache_dir: str = "data/cache/hh"):
        self.cache = FileCache(cache_dir)
        self.base_url = "https://api.hh.ru/vacancies"

    def parse_vacancies(self, search_params: Dict[str, Any]) -> List[Vacancy]:
        """Парсинг вакансий по параметрам поиска"""
        # Проверка кэша
        cached = self.cache.load_response("hh", search_params)
        if cached:
            return self._parse_items(cached.get("data", []))

        # Запрос к API (заглушка для примера)
        # В реальной реализации здесь будет запрос к API
        vacancies_data = self._fetch_from_api()

        # Сохранение в кэш
        self.cache.save_response("hh", search_params, vacancies_data)
        return self._parse_items(vacancies_data)

    @staticmethod
    def _fetch_from_api() -> List[Dict[str, Any]]:
        """Заглушка для реального запроса к API"""
        # В реальной реализации здесь будет код для работы с API
        return []

    def _parse_items(self, raw_data: List[Dict[str, Any]]) -> List[Vacancy]:
        """Преобразование сырых данных HH в объекты Vacancy"""
        vacancies = []

        for item in raw_data:
            try:
                # Проверяем что есть обязательные поля
                if not item.get("name") or not item.get("alternate_url"):
                    logger.warning(f"Пропуск вакансии без обязательных полей: {item.get('id', 'NO_ID')}")
                    continue

                # Убеждаемся что источник установлен
                if "source" not in item:
                    item["source"] = "hh.ru"

                # Обогащаем данные описанием из snippet если основное описание пустое
                if not item.get("description") and item.get("snippet"):
                    snippet = item.get("snippet", {})
                    desc_parts = []
                    if snippet.get("requirement"):
                        desc_parts.append(f"Требования: {snippet.get('requirement')}")
                    if snippet.get("responsibility"):
                        desc_parts.append(f"Обязанности: {snippet.get('responsibility')}")
                    if desc_parts:
                        item["description"] = " ".join(desc_parts)

                # Создаем объект вакансии напрямую из данных API
                vacancy = Vacancy.from_dict(item)

                # Отладочная информация
                vacancy_id = str(item.get("id", ""))
                if vacancy_id in ["124403607", "124403580", "124403642"]:
                    print(f"DEBUG HH Parser: Обрабатывается вакансия ID {vacancy_id}: {item.get('name')}")
                    print(f"DEBUG HH Parser: item содержит ключи: {list(item.keys())}")
                    print(f"DEBUG HH Parser: item['id'] = {item.get('id')}")
                    print(f"DEBUG HH Parser: Передаем в Vacancy.from_dict...")

                vacancy = Vacancy.from_dict(item)

                if vacancy_id in ["124403607", "124403580", "124403642"]:
                    print(f"DEBUG HH Parser: Созданная вакансия имеет ID: {vacancy.vacancy_id}")
                    print(f"DEBUG HH Parser: Ожидали ID: {vacancy_id}")
                    if vacancy.vacancy_id != vacancy_id:
                        print(f"ОШИБКА: ID изменился с {vacancy_id} на {vacancy.vacancy_id}!")

                vacancies.append(vacancy)

            except Exception as e:
                logger.warning(f"Ошибка парсинга HH вакансии: {e}")
                continue
        logger.info(f"Успешно распарсено {len(vacancies)} вакансий HH из {len(raw_data)}")
        return vacancies

    @staticmethod
    def parse_vacancy(vacancy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг одной вакансии HH в словарь

        Args:
            vacancy_data: Данные вакансии от API HH

        Returns:
            Dict[str, Any]: Словарь с данными вакансии
        """
        try:
            salary_info = vacancy_data.get("salary", {})
            snippet_info = vacancy_data.get("snippet", {})
            employer_info = vacancy_data.get("employer", {})
            area_info = vacancy_data.get("area", {})
            experience_info = vacancy_data.get("experience", {})
            employment_info = vacancy_data.get("employment", {})
            schedule_info = vacancy_data.get("schedule", {})

            return {
                "vacancy_id": str(vacancy_data.get("id", "")),
                "title": vacancy_data.get("name", ""),
                "url": vacancy_data.get("alternate_url", ""),
                "salary_from": salary_info.get("from") if salary_info else None,
                "salary_to": salary_info.get("to") if salary_info else None,
                "salary_currency": salary_info.get("currency") if salary_info else None,
                "requirements": snippet_info.get("requirement", "") if snippet_info else "",
                "responsibilities": snippet_info.get("responsibility", "") if snippet_info else "",
                "employer": employer_info.get("name", "") if employer_info else "",
                "area": area_info.get("name", "") if area_info else "",
                "experience": experience_info.get("name", "") if experience_info else "",
                "employment": employment_info.get("name", "") if employment_info else "",
                "schedule": schedule_info.get("name", "") if schedule_info else "",
                "published_at": vacancy_data.get("published_at", ""),
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге вакансии HH: {e}")
            return {
                "vacancy_id": str(vacancy_data.get("id", "")),
                "title": vacancy_data.get("name", ""),
                "url": "",
                "salary_from": None,
                "salary_to": None,
                "salary_currency": None,
                "requirements": "",
                "responsibilities": "",
                "employer": "",
                "area": "",
                "experience": "",
                "employment": "",
                "schedule": "",
                "published_at": "",
            }

    @staticmethod
    def parse_company(company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг данных компании HH

        Args:
            company_data: Данные компании от API HH

        Returns:
            Dict[str, Any]: Словарь с данными компании
        """
        try:
            return {
                "company_id": str(company_data.get("id", "")),
                "name": company_data.get("name", ""),
                "description": company_data.get("description", ""),
                "url": company_data.get("alternate_url", ""),
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге компании HH: {e}")
            return {
                "company_id": str(company_data.get("id", "")),
                "name": company_data.get("name", ""),
                "description": "",
                "url": "",
            }

    @staticmethod
    def parse_companies(companies_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Парсинг списка компаний HH

        Args:
            companies_data: Данные компаний от API HH

        Returns:
            List[Dict[str, Any]]: Список словарей с данными компаний
        """
        try:
            companies = []
            items = companies_data.get("items", [])

            for company_data in items:
                company = HHParser.parse_company(company_data)
                companies.append(company)

            logger.info(f"Успешно распарсено {len(companies)} компаний HH")
            return companies
        except Exception as e:
            logger.error(f"Ошибка при парсинге списка компаний HH: {e}")
            return []

    @staticmethod
    def convert_to_unified_format(hh_vacancy: Vacancy) -> Vacancy:
        """Конвертация HH вакансии в унифицированный формат"""
        # Для HH: обязанности = responsibility, требования = requirement
        return Vacancy(
            vacancy_id=hh_vacancy.vacancy_id,
            title=hh_vacancy.title,
            url=(
                (hh_vacancy.raw_data.get("alternate_url") if hh_vacancy.raw_data else "")
                or (hh_vacancy.raw_data.get("url") if hh_vacancy.raw_data else "")
                or ""
            ),
            salary=hh_vacancy.salary.to_dict() if hh_vacancy.salary else None,
            description=hh_vacancy.description,
            requirements=hh_vacancy.requirements,  # requirement из snippet
            responsibilities=hh_vacancy.responsibilities,  # responsibility из snippet
            employer=hh_vacancy.employer,
            experience=hh_vacancy.experience,
            employment=hh_vacancy.employment,
            schedule=hh_vacancy.schedule,
            published_at=hh_vacancy.published_at.isoformat() if hh_vacancy.published_at else None,
            skills=hh_vacancy.skills,
            detailed_description=hh_vacancy.detailed_description,
            benefits=hh_vacancy.benefits,
            source=hh_vacancy.source or "hh.ru",
        )
