import logging
from typing import Any, Dict, List

from src.utils.cache import FileCache

from ..models import Vacancy

logger = logging.getLogger(__name__)


class HHParser:
    """Парсер вакансий с HeadHunter API"""

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
                        print(f"❌ ОШИБКА: ID изменился с {vacancy_id} на {vacancy.vacancy_id}!")

                vacancies.append(vacancy)

            except Exception as e:
                logger.warning(f"Ошибка парсинга HH вакансии: {e}")
                continue
        return vacancies

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