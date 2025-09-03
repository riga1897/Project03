import logging
from typing import Any, Dict, List

from src.utils.cache import FileCache
from src.vacancies.models import Vacancy
from src.vacancies.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


class HHParser(BaseParser):
    """Парсер для обработки данных вакансий с HeadHunter API"""

    def __init__(self, cache_dir: str = "data/cache/hh"):
        self.cache = FileCache(cache_dir)
        self.base_url = "https://api.hh.ru/vacancies"

    def parse_vacancies(self, raw_vacancies: List[Dict[str, Any]]) -> List[Vacancy]:
        """Парсинг вакансий по предоставленным сырым данным - возвращает объекты Vacancy"""
        if not raw_vacancies:
            return []
        return self._parse_items(raw_vacancies)

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

                # Создаем объект вакансии из данных API
                vacancy = Vacancy.from_dict(item)

                vacancies.append(vacancy)

            except Exception as e:
                logger.warning(f"Ошибка парсинга HH вакансии: {e}")
                continue
        logger.info(f"Успешно распарсено {len(vacancies)} вакансий HH из {len(raw_data)}")
        return vacancies

    def parse_vacancy(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг одной вакансии HH в словарь

        Args:
            vacancy_data: Данные вакансии от API HH

        Returns:
            Dict[str, Any]: Словарь с данными вакансии
        """
        try:
            salary_info = raw_data.get("salary", {})
            snippet_info = raw_data.get("snippet", {})
            employer_info = raw_data.get("employer", {})
            area_info = raw_data.get("area", {})
            experience_info = raw_data.get("experience", {})
            employment_info = raw_data.get("employment", {})
            schedule_info = raw_data.get("schedule", {})

            return {
                "vacancy_id": str(raw_data.get("id", "")),
                "title": raw_data.get("name", ""),
                "url": raw_data.get("alternate_url", ""),
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
                "published_at": raw_data.get("published_at", ""),
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге вакансии HH: {e}")
            return {
                "vacancy_id": str(raw_data.get("id", "")),
                "title": raw_data.get("name", ""),
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
    def convert_to_unified_format(hh_vacancy: Vacancy) -> Vacancy:
        """Конвертация HH вакансии в унифицированный формат"""
        # Для HH: обязанности = responsibility, требования = requirement
        return Vacancy(
            vacancy_id=hh_vacancy.vacancy_id,
            title=hh_vacancy.title,
            url=hh_vacancy.url,
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
