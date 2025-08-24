import logging
from typing import List, Optional

from ..vacancies.models import Vacancy
from .base_formatter import BaseFormatter

logger = logging.getLogger(__name__)


class VacancyFormatter(BaseFormatter):
    """Класс для форматирования и отображения вакансий с поддержкой маппинга полей"""

    @staticmethod
    def _extract_responsibilities(vacancy) -> Optional[str]:
        """Извлечение обязанностей (парсеры уже правильно маппят поля)"""
        return getattr(vacancy, "responsibilities", None)

    @staticmethod
    def _extract_requirements(vacancy) -> Optional[str]:
        """Извлечение требований (парсеры уже правильно маппят поля)"""
        return getattr(vacancy, "requirements", None)

    @staticmethod
    def _extract_conditions(vacancy) -> Optional[str]:
        """Извлечение условий с учетом источника"""
        conditions_parts = []

        # График работы
        schedule = getattr(vacancy, "schedule", None)
        if schedule:
            conditions_parts.append(f"График: {schedule}")

        # Можно добавить другие условия специфичные для разных источников
        source = getattr(vacancy, "source", "")

        if source == "hh.ru":
            # Специфичные для HH условия
            pass
        elif source == "superjob.ru":
            # Специфичные для SJ условия
            pass

        return "; ".join(conditions_parts) if conditions_parts else None

    @staticmethod
    def format_vacancy_brief(vacancy: "Vacancy", number: Optional[int] = None) -> str:
        """
        Краткое форматирование информации о вакансии для списков

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер

        Returns:
            Отформатированная строка с краткой информацией
        """
        number_str = f"{number}. " if number else ""

        # Получаем зарплату
        salary_str = "Зарплата не указана"
        if vacancy.salary:
            if hasattr(vacancy.salary, 'salary_from') and hasattr(vacancy.salary, 'salary_to'):
                if vacancy.salary.salary_from and vacancy.salary.salary_to:
                    salary_str = f"{vacancy.salary.salary_from:,} - {vacancy.salary.salary_to:,} ₽"
                elif vacancy.salary.salary_from:
                    salary_str = f"от {vacancy.salary.salary_from:,} ₽"
                elif vacancy.salary.salary_to:
                    salary_str = f"до {vacancy.salary.salary_to:,} ₽"

        # Получаем работодателя
        employer_name = "Не указан"
        if vacancy.employer:
            if isinstance(vacancy.employer, dict):
                employer_name = vacancy.employer.get('name', 'Не указан')
            else:
                employer_name = str(vacancy.employer)

        return (
            f"{number_str}{vacancy.title}\n"
            f"   💰 {salary_str}\n"
            f"   🏢 {employer_name}\n"
            f"   📍 {vacancy.area or 'Не указан'}\n"
            f"   🔗 {vacancy.url}\n"
        )

    @staticmethod
    def format_vacancy_info(vacancy, number=None) -> str:
        """
        Форматирует информацию о вакансии для отображения

        Args:
            vacancy: Объект вакансии или словарь с данными вакансии
            number: Номер вакансии в списке (опционально)

        Returns:
            str: Отформатированная строка с информацией о вакансии
        """
        # Получаем данные о вакансии
        if hasattr(vacancy, 'to_dict'):
            # Если это объект Vacancy
            vacancy_data = vacancy
        else:
            # Если это уже словарь
            vacancy_data = vacancy

        # Извлекаем информацию
        vacancy_id = getattr(vacancy_data, 'vacancy_id', vacancy_data.get('vacancy_id', 'N/A'))

        # Отладка для отслеживания проблемы
        if str(vacancy_id) in ["124403607", "124403580", "124403642"]:
            print(f"DEBUG VacancyFormatter.format_vacancy_info: ID {vacancy_id}")
            print(f"DEBUG VacancyFormatter.format_vacancy_info: type(vacancy_data) = {type(vacancy_data)}")
            if hasattr(vacancy_data, 'employer'):
                print(f"DEBUG VacancyFormatter.format_vacancy_info: vacancy_data.employer = {vacancy_data.employer}")
            elif isinstance(vacancy_data, dict) and 'employer' in vacancy_data:
                print(f"DEBUG VacancyFormatter.format_vacancy_info: vacancy_data['employer'] = {vacancy_data.get('employer')}")

        title = getattr(vacancy_data, 'title', vacancy_data.get('title', 'Название не указано'))
        url = (
            getattr(vacancy_data, 'url', None) or
            vacancy_data.get('url', '') or
            vacancy_data.get('link', '')
        )

        # Получение информации о компании
        company_name = VacancyFormatter._extract_company_name(vacancy_data)

        # Дополнительная отладка для компании
        if str(vacancy_id) in ["124403607", "124403580", "124403642"]:
            print(f"DEBUG VacancyFormatter.format_vacancy_info: извлеченное company_name = '{company_name}'")

        # Получение информации о зарплате
        salary_info = VacancyFormatter._extract_salary_info(vacancy_data)

        # Опыт работы
        experience = (
            getattr(vacancy_data, 'experience', None) or
            vacancy_data.get('experience', 'Не указан')
        )

        # Тип занятости
        employment = (
            getattr(vacancy_data, 'employment', None) or
            vacancy_data.get('employment', 'Не указана')
        )

        # Источник
        source = (
            getattr(vacancy_data, 'source', None) or
            vacancy_data.get('source', 'unknown')
        )

        # Описание (ограничиваем длину)
        description = VacancyFormatter._extract_description(vacancy_data)

        # Формируем итоговую строку
        result_parts = []

        if number is not None:
            result_parts.append(f"{number}.")

        result_parts.extend([
            f"ID: {vacancy_id}",
            f"Название: {title}",
            f"Компания: {company_name}",
            f"Зарплата: {salary_info}",
            f"Опыт: {experience}",
            f"Занятость: {employment}",
            f"Источник: {source}",
            f"Ссылка: {url}",
            f"Описание вакансии: {description}",
        ])

        return "\n".join(result_parts)

    @staticmethod
    def display_vacancy_info(vacancy: Vacancy, number: Optional[int] = None) -> None:
        """
        Отображение информации о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)
        """
        lines = VacancyFormatter._build_vacancy_lines(vacancy, number)

        for line in lines:
            print(line)

        print()  # Один перевод строки между вакансиями

    @staticmethod
    def format_salary(salary_info) -> str:
        """
        Форматирование информации о зарплате

        Args:
            salary_info: Информация о зарплате

        Returns:
            Отформатированная строка с зарплатой
        """
        if not salary_info:
            return "Зарплата не указана"

        if isinstance(salary_info, dict):
            return VacancyFormatter._format_salary_dict(salary_info)

        return str(salary_info)

    @staticmethod
    def _build_vacancy_lines(vacancy: Vacancy, number: Optional[int] = None) -> List[str]:
        """
        Формирование списка строк с информацией о вакансии

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Список строк с информацией о вакансии
            :type vacancy: Vacancy
        """
        lines = []

        # Добавляем номер отдельной строкой
        if number:
            lines.append(f"{number}.")

        # ID
        lines.append(f"ID: {vacancy.vacancy_id}")

        # Название
        title = vacancy.title or getattr(vacancy, "name", None) or "Не указано"
        lines.append(f"Название: {title}")

        # Компания
        company_name = "Не указана"
        if vacancy.employer:
            if isinstance(vacancy.employer, dict):
                company_name = vacancy.employer.get("name", "Не указана")
            elif isinstance(vacancy.employer, str) and vacancy.employer.strip():
                company_name = vacancy.employer
            else:
                company_name = str(vacancy.employer) if vacancy.employer else "Не указана"
        lines.append(f"Компания: {company_name}")

        # Зарплата
        if vacancy.salary:
            lines.append(f"Зарплата: {vacancy.salary}")
        else:
            lines.append("Зарплата: Не указана")

        # Опыт
        if vacancy.experience:
            lines.append(f"Опыт: {vacancy.experience}")

        # Занятость
        if vacancy.employment:
            lines.append(f"Занятость: {vacancy.employment}")

        # Источник
        lines.append(f"Источник: {getattr(vacancy, 'source', 'Не указан')}")

        # Ссылка с преобразованием API-ссылок в веб-ссылки
        url = vacancy.url
        if isinstance(url, str) and url != "Не указана":
            # Преобразуем API-ссылки HH в веб-ссылки
            if "api.hh.ru/vacancies/" in url:
                import re

                match = re.search(r"/vacancies/(\d+)", url)
                if match:
                    vacancy_web_id = match.group(1)
                    url = f"https://hh.ru/vacancy/{vacancy_web_id}"

        lines.append(f"Ссылка: {url}")

        # Описание вакансии (объединенное поле)
        description_parts = []

        # Основное описание - сначала пробуем description, потом detailed_description
        main_description = getattr(vacancy, "description", None)
        if not main_description or not str(main_description).strip():
            main_description = getattr(vacancy, "detailed_description", None)

        if (
            main_description
            and str(main_description).strip()
            and str(main_description).strip() != "Не указано"
            and str(main_description).strip() != ""
        ):
            # Очищаем HTML-теги и ограничиваем длину
            import re

            clean_description = re.sub(r"<[^>]+>", "", str(main_description))
            clean_description = clean_description.strip()
            if clean_description:
                if len(clean_description) > 150:
                    clean_description = clean_description[:150] + "..."
                description_parts.append(clean_description)

        # Обязанности
        responsibilities = VacancyFormatter._extract_responsibilities(vacancy)
        if (
            responsibilities
            and str(responsibilities).strip()
            and str(responsibilities).strip() != "Не указано"
            and str(responsibilities).strip() != ""
        ):
            resp_text = str(responsibilities).strip()
            if len(resp_text) > 150:
                resp_text = resp_text[:150] + "..."
            description_parts.append(f"Обязанности: {resp_text}")

        # Требования
        requirements = VacancyFormatter._extract_requirements(vacancy)
        if (
            requirements
            and str(requirements).strip()
            and str(requirements).strip() != "Не указано"
            and str(requirements).strip() != ""
        ):
            req_text = str(requirements).strip()
            if len(req_text) > 150:
                req_text = req_text[:150] + "..."
            description_parts.append(f"Требования: {req_text}")

        # Условия
        conditions = VacancyFormatter._extract_conditions(vacancy)
        if conditions and str(conditions).strip():
            cond_text = str(conditions).strip()
            if len(cond_text) > 100:
                cond_text = cond_text[:100] + "..."
            description_parts.append(f"Условия: {cond_text}")

        # Если есть хотя бы одна из частей описания, показываем её
        if description_parts:
            combined_description = "; ".join(description_parts)
            # Ограничиваем общую длину описания
            if len(combined_description) > 400:
                combined_description = combined_description[:400] + "..."
            lines.append(f"Описание вакансии: {combined_description}")
        else:
            # Если нет никакого описания, показываем заглушку для отладки
            lines.append("Описание вакансии: Описание отсутствует")

        return lines

    @staticmethod
    def format_company_info(employer_info) -> str:
        """
        Форматирование информации о компании
        Args:
            employer_info: Информация о работодателе
        Returns:
            Отформатированная строка с информацией о компании
        """
        if not employer_info:
            return "Не указана"

        if isinstance(employer_info, dict):
            return employer_info.get("name", "Не указана")

        return str(employer_info)

    @staticmethod
    def _format_salary_dict(salary_info: dict) -> str:
        """
        Форматирование информации о зарплате из словаря
        """
        salary_str = ""
        from_value = salary_info.get("from")
        to_value = salary_info.get("to")
        currency = salary_info.get("currency")

        if from_value:
            salary_str += f"от {from_value} "
        if to_value:
            salary_str += f"до {to_value} "
        if currency:
            salary_str += currency

        return salary_str.strip() if salary_str else "Зарплата не указана"

    @staticmethod
    def _extract_company_name(vacancy_data) -> str:
        """
        Извлекает название компании из объекта или словаря вакансии.
        """
        employer_info = None
        if hasattr(vacancy_data, 'employer'):
            employer_info = vacancy_data.employer
        elif isinstance(vacancy_data, dict) and 'employer' in vacancy_data:
            employer_info = vacancy_data.get('employer')

        if not employer_info:
            return "Не указана"

        if isinstance(employer_info, dict):
            return employer_info.get('name', 'Не указана')
        elif isinstance(employer_info, str) and employer_info.strip():
            return employer_info
        else:
            # Пытаемся преобразовать в строку, если это какой-то другой объект
            return str(employer_info) if employer_info else "Не указана"

    @staticmethod
    def _extract_salary_info(vacancy_data) -> str:
        """
        Извлекает и форматирует информацию о зарплате.
        """
        salary_data = None
        if hasattr(vacancy_data, 'salary'):
            salary_data = vacancy_data.salary
        elif isinstance(vacancy_data, dict) and 'salary' in vacancy_data:
            salary_data = vacancy_data.get('salary')

        if not salary_data:
            return "Не указана"

        if isinstance(salary_data, dict):
            return VacancyFormatter._format_salary_dict(salary_data)
        elif hasattr(salary_data, 'salary_from') and hasattr(salary_data, 'salary_to'):
            # Форматирование, если salary является объектом с атрибутами
            from_value = salary_data.salary_from
            to_value = salary_data.salary_to
            currency = getattr(salary_data, 'currency', '₽') # Используем ₽ по умолчанию, если нет валюты

            salary_parts = []
            if from_value is not None:
                salary_parts.append(f"от {from_value:,}")
            if to_value is not None:
                salary_parts.append(f"до {to_value:,}")
            
            if salary_parts:
                return " ".join(salary_parts) + f" {currency}".strip()
            else:
                return "Не указана"
        else:
            # Если salary_data не словарь и не имеет известных атрибутов, просто возвращаем как строку
            return str(salary_data)

    @staticmethod
    def _extract_description(vacancy_data) -> str:
        """
        Извлекает и форматирует описание вакансии, ограничивая длину.
        """
        description_text = None
        if hasattr(vacancy_data, 'description') and vacancy_data.description:
            description_text = str(vacancy_data.description).strip()
        elif hasattr(vacancy_data, 'detailed_description') and vacancy_data.detailed_description:
            description_text = str(vacancy_data.detailed_description).strip()
        elif isinstance(vacancy_data, dict) and vacancy_data.get('description'):
            description_text = str(vacancy_data.get('description')).strip()
        elif isinstance(vacancy_data, dict) and vacancy_data.get('detailed_description'):
            description_text = str(vacancy_data.get('detailed_description')).strip()

        if not description_text or description_text == "Не указано" or description_text == "":
            return "Описание отсутствует"

        # Очистка HTML-тегов
        import re
        cleaned_description = re.sub(r"<[^>]+>", "", description_text)
        cleaned_description = cleaned_description.strip()

        if not cleaned_description:
            return "Описание отсутствует"

        # Ограничение длины
        if len(cleaned_description) > 150:
            return cleaned_description[:150] + "..."
        return cleaned_description


# Глобальный экземпляр форматтера
vacancy_formatter = VacancyFormatter()