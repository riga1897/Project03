import logging
import re
from typing import List, Optional, Any

from ..vacancies.models import Vacancy
from .base_formatter import BaseFormatter

logger = logging.getLogger(__name__)


class VacancyFormatter(BaseFormatter):
    """Форматировщик вакансий - конкретная реализация BaseFormatter"""

    def format_vacancy_info(self, vacancy: Any, number: Optional[int] = None) -> str:
        """
        Форматирование информации о вакансии в строку

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Отформатированная строка с информацией о вакансии
        """
        lines = self._build_vacancy_lines(vacancy, number)
        return '\n'.join(lines)

    def _build_vacancy_lines(self, vacancy: Any, number: Optional[int] = None) -> List[str]:
        """
        Формирование списка строк с информацией о вакансии в едином порядке

        Args:
            vacancy: Объект вакансии
            number: Порядковый номер (опционально)

        Returns:
            Список строк с информацией о вакансии
        """
        lines = []

        # Номер вакансии
        if number:
            lines.append(f"{number}.")

        # ID
        vacancy_id = getattr(vacancy, "vacancy_id", None) or getattr(vacancy, "id", None)
        if vacancy_id:
            lines.append(f"ID: {vacancy_id}")

        # Название
        title = getattr(vacancy, "title", None) or getattr(vacancy, "name", None)
        if title:
            lines.append(f"Название: {title}")

        # Компания
        company_name = self._extract_company_name(vacancy)
        if company_name and company_name != "Не указана":
            lines.append(f"Компания: {company_name}")

        # Зарплата
        salary_info = self._extract_salary_info(vacancy)
        if salary_info and salary_info != "Не указана":
            lines.append(f"Зарплата: {salary_info}")

        # Опыт
        experience = getattr(vacancy, "experience", None)
        if experience:
            lines.append(f"Опыт: {self.format_experience(experience)}")

        # Занятость
        employment = getattr(vacancy, "employment", None)
        if employment:
            lines.append(f"Занятость: {self.format_employment_type(employment)}")

        # Источник
        source = getattr(vacancy, "source", None)
        if source:
            lines.append(f"Источник: {source}")

        # Ссылка
        url = getattr(vacancy, "url", None) or getattr(vacancy, "alternate_url", None)
        if url:
            lines.append(f"Ссылка: {url}")

        # Обязанности
        responsibilities = self._extract_responsibilities(vacancy)
        if responsibilities:
            resp_text = self.format_text(str(responsibilities), 150)
            lines.append(f"Обязанности: {resp_text}")

        # Требования
        requirements = self._extract_requirements(vacancy)
        if requirements:
            req_text = self.format_text(str(requirements), 150)
            lines.append(f"Требования: {req_text}")

        # Условия
        conditions = self._extract_conditions(vacancy)
        if conditions:
            cond_text = self.format_text(str(conditions), 150)
            lines.append(f"Условия: {cond_text}")

        return lines

    def _extract_company_name(self, vacancy: Any) -> Optional[str]:
        """Извлечение названия компании"""
        employer = getattr(vacancy, "employer", None)
        if employer:
            if isinstance(employer, dict):
                name = employer.get("name")
                return name if name and str(name).strip() else "Не указана"
            elif isinstance(employer, str) and employer.strip():
                return employer
            else:
                return str(employer) if employer else "Не указана"
        return "Не указана"

    def _extract_salary_info(self, vacancy: Any) -> Optional[str]:
        """Извлечение информации о зарплате"""
        salary = getattr(vacancy, "salary", None)
        if not salary:
            return None

        return self.format_salary(salary)

    def _extract_responsibilities(self, vacancy: Any) -> Optional[str]:
        """Извлечение обязанностей"""
        return getattr(vacancy, "responsibilities", None)

    def _extract_requirements(self, vacancy: Any) -> Optional[str]:
        """Извлечение требований"""
        return getattr(vacancy, "requirements", None)

    def _extract_conditions(self, vacancy: Any) -> Optional[str]:
        """Извлечение условий"""
        conditions = getattr(vacancy, "conditions", None)
        if not conditions:
            # Также можем использовать график работы как условие
            schedule = getattr(vacancy, "schedule", None)
            if schedule:
                conditions = f"График: {self.format_schedule(schedule)}"
        return conditions

    def format_salary(self, salary: Any) -> str:
        """Форматирование зарплаты"""
        if not salary:
            return "Не указана"

        if isinstance(salary, dict):
            return self._format_salary_dict(salary)
        else:
            return str(salary)

    def _format_salary_dict(self, salary_dict: dict) -> str:
        """Форматирование словаря зарплаты"""
        if not salary_dict:
            return "Не указана"

        from_salary = salary_dict.get("from")
        to_salary = salary_dict.get("to")
        currency = salary_dict.get("currency", "RUR")

        currency_display = self.format_currency(currency)

        if from_salary and to_salary:
            return f"от {self.format_number(from_salary)} до {self.format_number(to_salary)} {currency_display} в месяц"
        elif from_salary:
            return f"от {self.format_number(from_salary)} {currency_display} в месяц"
        elif to_salary:
            return f"до {self.format_number(to_salary)} {currency_display} в месяц"
        else:
            return "Не указана"

    def format_currency(self, currency: str) -> str:
        """Форматирование валюты"""
        currency_map = {"RUR": "руб.", "RUB": "руб.", "USD": "долл.", "EUR": "евро"}
        return currency_map.get(currency, currency)

    def format_text(self, text: str, max_length: int = 150) -> str:
        """Форматирование текста с возможностью усечения"""
        if not text:
            return "Не указано"

        # Очищаем HTML теги
        clean_text = self.clean_html_tags(text)

        if len(clean_text) > max_length:
            return clean_text[:max_length] + "..."

        return clean_text

    def format_date(self, date_str: str) -> str:
        """Форматирование даты"""
        if not date_str:
            return "Не указано"

        try:
            # Пытаемся парсить ISO формат
            if "T" in date_str:
                date_part = date_str.split("T")[0]
                parts = date_part.split("-")
                if len(parts) == 3:
                    return f"{parts[2]}.{parts[1]}.{parts[0]}"
        except:
            pass

        return date_str

    def format_experience(self, experience: str) -> str:
        """Форматирование опыта работы"""
        if not experience:
            return "Не указан"
        return str(experience)

    def format_employment_type(self, employment: str) -> str:
        """Форматирование типа занятости"""
        if not employment:
            return "Не указан"
        return str(employment)

    def format_schedule(self, schedule: str) -> str:
        """Форматирование графика работы"""
        if not schedule:
            return "Не указан"
        return str(schedule)

    def format_company_name(self, company: Any) -> str:
        """Форматирование названия компании"""
        if not company:
            return "Не указана"

        if isinstance(company, dict):
            return company.get("name", "Не указана")

        return str(company)

    def clean_html_tags(self, text: str) -> str:
        """Очистка HTML тегов из текста"""
        if not text:
            return ""

        # Удаляем HTML теги
        clean = re.compile('<.*?>')
        result = re.sub(clean, '', str(text))

        # Заменяем множественные пробелы на одинарные
        result = re.sub(r'\s+', ' ', result)

        return result.strip()

    def format_number(self, number: int) -> str:
        """Форматирование числа с разделителями тысяч"""
        if not isinstance(number, (int, float)):
            return str(number)

        return f"{number:,}".replace(",", " ")

    @staticmethod
    def display_vacancy_info(vacancy: Any, number: Optional[int] = None) -> None:
        """Отображение информации о вакансии"""
        formatter = VacancyFormatter()
        print(formatter.format_vacancy_info(vacancy, number))

    @staticmethod
    def format_vacancy_brief(vacancy: Any, number: Optional[int] = None) -> str:
        """Краткое форматирование вакансии"""
        formatter = VacancyFormatter()

        lines = []

        if number:
            lines.append(f"{number}.")

        # Название
        title = getattr(vacancy, "title", None) or getattr(vacancy, "name", None)
        if title:
            lines.append(title)

        # Компания
        company_name = formatter._extract_company_name(vacancy)
        if company_name and company_name != "Не указана":
            lines.append(f"Компания: {company_name}")

        # Зарплата
        salary_info = formatter._extract_salary_info(vacancy)
        if salary_info and salary_info != "Не указана":
            lines.append(f"Зарплата: {salary_info}")
        else:
            lines.append("Зарплата не указана")

        # Ссылка
        url = getattr(vacancy, "url", None) or getattr(vacancy, "alternate_url", None)
        if url:
            lines.append(f"Ссылка: {url}")

        return ' | '.join(lines)