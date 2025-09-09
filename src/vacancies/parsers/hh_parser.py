"""
Парсер для обработки данных вакансий с HeadHunter API.

Модуль содержит класс HHParser для преобразования сырых данных
из API HeadHunter в структурированные объекты Vacancy.
"""

import logging
from typing import Any, Dict, List

from src.utils.cache import FileCache
from src.vacancies.models import Vacancy
from src.vacancies.parsers.base_parser import BaseParser

logger = logging.getLogger(__name__)


class HHParser(BaseParser):
    """Парсер для обработки данных вакансий с HeadHunter API"""

    def __init__(self, cache_dir: str = "data/cache/hh"):
        """Инициализация парсера HeadHunter с настройкой кэша."""
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

                # ИСПРАВЛЕНО: Правильно извлекаем requirements и responsibilities из snippet
                snippet = item.get("snippet", {})
                if snippet:
                    # Устанавливаем отдельные поля requirements и responsibilities
                    requirement = snippet.get("requirement")
                    responsibility = snippet.get("responsibility")

                    if requirement:
                        item["requirements"] = requirement
                        logger.debug(f"Установлены требования для вакансии {item.get('id')}: {requirement[:50]}...")

                    if responsibility:
                        item["responsibilities"] = responsibility
                        logger.debug(
                            f"Установлены обязанности для вакансии {item.get('id')}: {responsibility[:50]}..."
                        )

                    # Обогащаем description только если его нет
                    if not item.get("description"):
                        desc_parts = []
                        if snippet.get("requirement"):
                            desc_parts.append(f"Требования: {snippet.get('requirement')}")
                        if snippet.get("responsibility"):
                            desc_parts.append(f"Обязанности: {snippet.get('responsibility')}")
                        if desc_parts:
                            item["description"] = " ".join(desc_parts)
                else:
                    # НОВОЕ: Если нет snippet, пытаемся извлечь из описания
                    logger.debug(f"Нет snippet для вакансии {item.get('id')}, пытаемся извлечь из description")
                    description = item.get("description", "")
                    if description:
                        # Используем DescriptionParser для извлечения из полного описания
                        try:
                            from src.utils.description_parser import DescriptionParser

                            parser = DescriptionParser()
                            requirements, responsibilities = parser.extract_requirements_and_responsibilities(
                                description
                            )

                            if requirements:
                                item["requirements"] = requirements
                                logger.debug(
                                    f"Извлечены требования из description для {item.get('id')}: {requirements[:50]}..."
                                )
                            if responsibilities:
                                item["responsibilities"] = responsibilities
                                logger.debug(
                                    f"Извлечены обязанности из description для {item.get('id')}: {responsibilities[:50]}..."
                                )
                        except Exception as e:
                            logger.warning(f"Ошибка извлечения из description для {item.get('id')}: {e}")

                # ИСПРАВЛЕНО: Маппинг полей для совместимости с моделью Vacancy
                # Преобразуем поля API в поля модели с учетом alias
                if "alternate_url" in item:
                    item["url"] = item["alternate_url"]
                if "id" in item:
                    item["vacancy_id"] = item["id"]
                if "name" in item:
                    item["title"] = item["name"]

                # Сохраняем сырые данные API для статистики и анализа
                item["raw_data"] = item.copy()  # сохраняем полную копию сырых данных

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
        # Просто возвращаем исходную вакансию, так как она уже в правильном формате
        return hh_vacancy
