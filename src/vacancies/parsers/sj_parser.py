"""
Парсер для обработки данных вакансий с SuperJob API.

Модуль содержит класс SuperJobParser для преобразования сырых данных
из API SuperJob в структурированные объекты Vacancy.
Поддерживает различные форматы ответов API.
"""

import logging
from typing import Any, Dict, List

from src.vacancies.parsers.base_parser import BaseParser

from ..models import Vacancy

logger = logging.getLogger(__name__)


class SuperJobParser(BaseParser):
    """Парсер для обработки данных вакансий SuperJob"""

    def _extract_vacancies_from_response(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Извлекает список вакансий из ответа SuperJob API с поддержкой разных форматов

        SuperJob API может возвращать данные в разных форматах:
        - Обычный список: [vacancy1, vacancy2, ...]
        - Обернутые в objects: {data: {objects: [vacancy1, vacancy2, ...]}}
        - Обернутые в items: {data: {items: [vacancy1, vacancy2, ...]}}

        Args:
            raw_data: Ответ от SuperJob API

        Returns:
            List[Dict[str, Any]]: Список данных вакансий
        """
        try:
            # Если это уже список вакансий
            if isinstance(raw_data, list):
                return raw_data

            # Если это обернутые данные
            if isinstance(raw_data, dict):
                # Проверяем есть ли data.objects
                if "data" in raw_data and isinstance(raw_data["data"], dict):
                    data_section = raw_data["data"]
                    if "objects" in data_section and isinstance(data_section["objects"], list):
                        logger.info(f"Извлечено {len(data_section['objects'])} вакансий из data.objects")
                        return data_section["objects"]
                    elif "items" in data_section and isinstance(data_section["items"], list):
                        logger.info(f"Извлечено {len(data_section['items'])} вакансий из data.items")
                        return data_section["items"]

            logger.warning(f"Неизвестный формат ответа SuperJob API: {type(raw_data)}")
            return []

        except Exception as e:
            logger.error(f"Ошибка извлечения вакансий из ответа SuperJob: {e}")
            return []

    def parse_vacancies(self, raw_vacancies: Any) -> List[Vacancy]:
        """
        Парсинг данных вакансий SuperJob - возвращает объекты Vacancy

        ИСПРАВЛЕНО: Поддерживает разные форматы API ответов

        Args:
            raw_vacancies: Данные от SuperJob API (список или обернутые данные)

        Returns:
            List[Vacancy]: Список объектов вакансий
        """
        # ИСПРАВЛЕНИЕ: Сначала извлекаем правильный список вакансий
        vacancies_list = self._extract_vacancies_from_response(raw_vacancies)

        if not vacancies_list:
            logger.warning("Не удалось извлечь вакансии из ответа SuperJob")
            return []

        parsed_vacancies = []

        for vacancy_data in vacancies_list:
            try:
                # ИСПРАВЛЕНИЕ: Преобразуем сырые данные SuperJob в формат Vacancy
                processed_data = self.parse_vacancy(vacancy_data)

                # Сохраняем сырые данные API для статистики и анализа
                processed_data["raw_data"] = vacancy_data.copy()  # сохраняем полную копию сырых данных

                # Создаем объект вакансии из обработанных данных
                vacancy = Vacancy.from_dict(processed_data)
                parsed_vacancies.append(vacancy)
            except ValueError as e:
                logger.warning(f"Пропуск вакансии SuperJob из-за ошибки валидации: {e}")
                continue
            except Exception as e:
                logger.error(f"Неожиданная ошибка при парсинге вакансии SuperJob: {e}")
                continue

        logger.info(f"Успешно распарсено {len(parsed_vacancies)} вакансий SuperJob из {len(raw_vacancies)}")
        return parsed_vacancies

    @staticmethod
    def convert_to_unified_format(sj_vacancy: Vacancy) -> Dict[str, Any]:
        """
        Конвертация SuperJob вакансии в унифицированный формат

        Args:
            sj_vacancy: Объект вакансии SuperJob

        Returns:
            Dict[str, Any]: Унифицированный словарь вакансии
        """
        # Обрабатываем зарплату для корректного отображения
        salary_dict = None
        if sj_vacancy.salary:
            if hasattr(sj_vacancy.salary, "to_dict") and callable(getattr(sj_vacancy.salary, "to_dict", None)):
                salary_dict = sj_vacancy.salary.to_dict()  # type: ignore
            elif hasattr(sj_vacancy.salary, "model_dump") and callable(getattr(sj_vacancy.salary, "model_dump", None)):
                salary_dict = sj_vacancy.salary.model_dump()  # type: ignore
            else:
                salary_dict = sj_vacancy.salary
            # Исправляем период для SuperJob
            if salary_dict and "period" in salary_dict:
                if salary_dict["period"] in ["месяц", "month"]:
                    salary_dict["period"] = "месяц"

        return {
            "id": sj_vacancy.vacancy_id,
            "name": sj_vacancy.title,
            "title": sj_vacancy.title,
            "url": sj_vacancy.url,
            "alternate_url": sj_vacancy.url,
            "salary": salary_dict,
            "description": sj_vacancy.description,
            # Для SJ: обязанности = vacancyRichText (description), требования = candidat (requirements)
            "requirements": sj_vacancy.requirements,  # candidat
            "responsibilities": sj_vacancy.description,  # vacancyRichText
            "employer": sj_vacancy.employer,
            "experience": sj_vacancy.experience,
            "employment": sj_vacancy.employment,
            "schedule": sj_vacancy.schedule,
            "published_at": (
                sj_vacancy.published_at.isoformat()
                if sj_vacancy.published_at and hasattr(sj_vacancy.published_at, "isoformat")
                else (str(sj_vacancy.published_at) if sj_vacancy.published_at else None)
            ),
            "skills": [],
            "keywords": [],
            "detailed_description": sj_vacancy.detailed_description,
            "benefits": sj_vacancy.benefits,
            "source": sj_vacancy.source or "superjob.ru",
        }

    def parse_vacancy(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсинг одной вакансии SJ в словарь

        Args:
            vacancy_data: Данные вакансии от API SJ

        Returns:
            Dict[str, Any]: Словарь с данными вакансии
        """
        try:
            town_info = raw_data.get("town", {})
            experience_info = raw_data.get("experience", {})
            type_of_work_info = raw_data.get("type_of_work", {})
            place_of_work_info = raw_data.get("place_of_work", {})

            # Обработка описания - объединяем vacancyRichText и work
            description_parts = []
            if raw_data.get("vacancyRichText"):
                description_parts.append(raw_data.get("vacancyRichText"))
            if raw_data.get("work"):
                description_parts.append(raw_data.get("work"))
            description = " ".join(filter(None, description_parts))

            # Обработка зарплаты - разбираем диапазон
            payment_from = raw_data.get("payment_from")
            payment_to = raw_data.get("payment_to")

            # Если зарплата задана одним числом без диапазона, используем его как salary_from
            if payment_from and not payment_to:
                salary_from = payment_from
                salary_to = None
            elif payment_to and not payment_from:
                salary_from = None
                salary_to = payment_to
            else:
                salary_from = payment_from
                salary_to = payment_to

            # Извлекаем ID компании (название берется из БД)
            company_id = self._extract_company_id(raw_data)

            return {
                "vacancy_id": str(raw_data.get("id", "")),
                "name": raw_data.get("profession", ""),  # ИСПРАВЛЕНО: name вместо title
                "title": raw_data.get("profession", ""),
                "url": raw_data.get("link", ""),
                "alternate_url": raw_data.get("link", ""),  # ИСПРАВЛЕНО: добавлено обязательное поле
                "salary_from": salary_from,
                "salary_to": salary_to,
                "salary_currency": raw_data.get("currency"),
                "description": description or "",
                "requirements": raw_data.get("candidat", ""),
                "responsibilities": raw_data.get("work", ""),
                # ИСПРАВЛЕНО: ID + название компании (из client.title или БД)
                "employer": self._build_employer_info(raw_data, company_id) if company_id else None,
                "area": {"name": town_info.get("title", "")} if town_info else None,
                # ИСПРАВЛЕНО: Создаем объекты вместо строк для валидации Pydantic
                "experience": {"name": experience_info.get("title", "")} if experience_info else None,
                "employment": {"name": type_of_work_info.get("title", "")} if type_of_work_info else None,
                "schedule": {"name": place_of_work_info.get("title", "")} if place_of_work_info else None,
                "published_at": raw_data.get("date_pub_timestamp", ""),
                "source": "superjob.ru",
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге вакансии SJ: {e}")
            return {
                "vacancy_id": str(raw_data.get("id", "")),
                "title": raw_data.get("profession", ""),
                "url": "",
                "salary_from": None,
                "salary_to": None,
                "salary_currency": None,
                "description": "",
                "requirements": "",
                "responsibilities": "",
                "employer": None,
                "area": "",
                "experience": "",
                "employment": "",
                "schedule": "",
                "published_at": "",
                "source": "superjob.ru",
            }

    def _build_employer_info(self, raw_data: Dict[str, Any], company_id: str) -> Dict[str, str]:
        """
        Создает информацию о работодателе с ID и названием

        Args:
            raw_data: Сырые данные вакансии от SuperJob API
            company_id: ID компании

        Returns:
            Dict[str, str]: Словарь с id и name работодателя
        """
        try:
            # Приоритет 1: Название из client.title
            client = raw_data.get("client", {})
            if isinstance(client, dict) and client.get("title"):
                company_name = client.get("title", "").strip()
                if company_name:
                    return {"id": company_id, "name": company_name}

            # Приоритет 2: Название из firm_name
            firm_name = raw_data.get("firm_name", "").strip()
            if firm_name:
                return {"id": company_id, "name": firm_name}

            # Приоритет 3: Ищем название в БД по ID
            company_name = self._get_company_name_by_id(company_id)
            if company_name != "Неизвестная компания":
                return {"id": company_id, "name": company_name}

            # Fallback: ID + заглушка названия
            return {"id": company_id, "name": f"Компания {company_id}"}

        except Exception as e:
            logger.warning(f"Ошибка создания информации о работодателе: {e}")
            return {"id": company_id, "name": f"Компания {company_id}"}

    def _get_company_name_by_id(self, company_id: str) -> str:
        """
        Получает название компании по ID из конфигурации

        Args:
            company_id: ID компании

        Returns:
            str: Название компании или "Неизвестная компания"
        """
        try:
            from src.config.target_companies import TargetCompanies

            # Ищем по SuperJob ID
            company = TargetCompanies.get_company_by_sj_id(company_id)
            if company:
                return company.name

            return "Неизвестная компания"
        except Exception:
            return "Неизвестная компания"

    def _extract_company_id(self, raw_data: Dict[str, Any]) -> str:
        """
        Извлекает ID компании из данных SuperJob
        Приоритет: client.id -> id_client (fallback)

        Args:
            raw_data: Сырые данные вакансии от SuperJob API

        Returns:
            str: ID компании или пустая строка
        """
        try:
            # Приоритет 1: client.id (основной источник)
            client = raw_data.get("client", {})
            if isinstance(client, dict):
                client_id = client.get("id")
                if client_id is not None and str(client_id) != "0":
                    return str(client_id)

            # Приоритет 2: id_client (fallback)
            id_client = raw_data.get("id_client")
            if id_client is not None and str(id_client) != "0":
                return str(id_client)

            return ""
        except Exception:
            return ""
