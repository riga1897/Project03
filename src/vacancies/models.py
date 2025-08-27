import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.utils.salary import Salary

from .abstract import AbstractVacancy

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Vacancy(AbstractVacancy):
    """
    Модуль моделей данных для работы с вакансиями.

    Содержит основную модель Vacancy и вспомогательные классы для представления
    структурированных данных о вакансиях из различных источников (HH.ru, SuperJob).
    Обеспечивает унификацию данных и их валидацию.
    """

    __slots__ = (
        "vacancy_id",
        "title",
        "url",
        "salary",
        "description",
        "requirements",
        "responsibilities",
        "employer",
        "employer_id",  # Новое поле для ID работодателя
        "experience",
        "employment",
        "schedule",
        "published_at",
        "skills",
        "detailed_description",
        "benefits",
        "source",
        "area",
        "company_id",
    )

    def __init__(
        self,
        title: str,
        url: str,
        salary: Optional[Dict[str, Any]] = None,
        description: str = "",
        requirements: Optional[str] = None,
        responsibilities: Optional[str] = None,
        employer: Optional[Dict[str, Any]] = None,
        employer_id: Optional[str] = None,  # Новый параметр для ID работодателя
        experience: Optional[str] = None,
        employment: Optional[str] = None,
        schedule: Optional[str] = None,
        published_at: Optional[str] = None,
        skills: Optional[List[Dict[str, str]]] = None,
        detailed_description: Optional[str] = None,
        benefits: Optional[str] = None,
        vacancy_id: Optional[str] = None,
        source: str = "unknown",
        area: Optional[str] = None,
    ):
        self.company_id = ""  # Инициализируем как строку
        # Используем переданный ID, если есть, иначе генерируем UUID
        if vacancy_id and str(vacancy_id).strip() and str(vacancy_id) != "":
            self.vacancy_id = str(vacancy_id)
        else:
            self.vacancy_id = str(uuid.uuid4())
        self.title = title
        self.url = url
        self.salary = self._validate_salary(salary)
        self.description = description
        self.requirements = self._clean_html(requirements) if requirements else None
        self.responsibilities = self._clean_html(responsibilities) if responsibilities else None

        self.employer = employer
        self.employer_id = employer_id  # Инициализируем новое поле

        self.experience = experience
        self.employment = employment
        self.schedule = schedule
        self.published_at = self._parse_datetime(published_at) if published_at else None
        self.skills = skills or []
        self.detailed_description = detailed_description or description
        self.benefits = benefits
        self.source = source

        # Обработка area - может приходить как строка или словарь
        if isinstance(area, dict):
            self.area = area.get('name', str(area))
        else:
            self.area = area

    @staticmethod
    def _validate_salary(salary_data: Optional[Dict[str, Any]]) -> Salary:
        """Приватный метод валидации данных о зарплате"""
        return Salary(salary_data) if salary_data else Salary()

    @staticmethod
    def _clean_html(text: str) -> str:
        """Очистка HTML-тегов из текста"""
        import re

        return re.sub(r"<[^>]+>", "", text)

    @staticmethod
    def _parse_datetime(date_str: Union[str, int, None]) -> Optional[datetime]:
        """
        Универсальный парсер дат для разных форматов API

        Args:
            date_str: Строка с датой в различных форматах или timestamp

        Returns:
            datetime object или None при ошибке
        """
        if not date_str:
            return None

        try:
            # Если это timestamp (для SuperJob)
            if isinstance(date_str, (int, float)):
                return datetime.fromtimestamp(date_str)

            # Если это строка
            if isinstance(date_str, str):
                # Сначала попробуем как timestamp
                try:
                    timestamp = float(date_str)
                    return datetime.fromtimestamp(timestamp)
                except (ValueError, TypeError):
                    pass

                # Попробуем разные форматы строк
                formats = [
                    "%Y-%m-%dT%H:%M:%S%z",  # ISO with timezone
                    "%Y-%m-%dT%H:%M:%S",  # ISO without timezone
                    "%Y-%m-%d %H:%M:%S",  # Standard format
                    "%Y-%m-%d",  # Date only
                ]

                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

        except Exception as e:
            logger.error(f"Ошибка парсинга даты '{date_str}': {e}")

        return None

    @classmethod
    def cast_to_object_list(cls, data):
        """Преобразование списка словарей в список объектов Vacancy"""
        vacancies = []
        for i, item in enumerate(data):
            try:
                vacancy = cls.from_dict(item)
                vacancies.append(vacancy)
            except ValueError as e:
                logging.warning(f"Пропуск элемента из-за ошибки валидации: {e}")
                continue
        return vacancies

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vacancy":
        """Создает унифицированный объект Vacancy из словаря"""
        try:
            if not isinstance(data, dict):
                raise ValueError("Данные должны быть словарем")

            # Универсальная обработка полей из разных источников
            title = data.get("title") or data.get("name") or data.get("profession") or "Без названия"

            url = (
                data.get("alternate_url")  # Веб-версия для HH
                or data.get("link")  # Веб-версия для SuperJob
                or data.get("url")  # Fallback на API-ссылку
                or ""
            )

            # Получаем ID из API данных
            # Ищем ID в разных полях (из API и из UnifiedAPI)
            vacancy_id = data.get("id") or data.get("vacancy_id")
            if vacancy_id:
                vacancy_id = str(vacancy_id)
            else:
                vacancy_id = ""

            # Обработка зарплаты (универсальная для всех источников)
            salary = data.get("salary")

            # Если salary не найден, но есть поле salary_range как строка - парсим его
            if not salary and data.get("salary_range") and isinstance(data.get("salary_range"), str):
                salary = data.get("salary_range")

            # Обработка работодателя - сохраняем исходную структуру
            employer = data.get("employer")
            company_id = ""
            employer_id = None  # Новое поле для сохранения ID работодателя

            if employer:
                if isinstance(employer, dict):
                    company_id = str(employer.get("id", "")) if employer.get("id") else ""
                    employer_id = employer.get("id")  # Сохраняем ID работодателя отдельно
                    # Сохраняем employer как есть
                elif isinstance(employer, str):
                    # Если employer - строка, преобразуем в словарь
                    employer = {"name": employer}
                    company_id = ""
                    employer_id = None
            elif data.get("firm_name"):
                # Для SuperJob создаем структуру employer с ID если есть
                firm_id = data.get("firm_id") or data.get("client_id")
                employer = {"name": data.get("firm_name")}
                if firm_id:
                    employer["id"] = str(firm_id)
                    employer_id = str(firm_id)
                    company_id = str(firm_id)
                else:
                    employer_id = None
                    company_id = ""

            # Если employer все еще None, но есть данные от SuperJob
            if not employer and data.get("firm_name"):
                firm_id = data.get("firm_id") or data.get("client_id")
                employer = {"name": data.get("firm_name")}
                if firm_id:
                    employer["id"] = str(firm_id)
                    employer_id = str(firm_id)
                    company_id = str(firm_id)
                else:
                    employer_id = None

            # Обработка опыта работы
            experience = None
            experience_data = data.get("experience")
            if isinstance(experience_data, dict):
                experience = experience_data.get("name") or experience_data.get("title")
            elif isinstance(experience_data, str):
                experience = experience_data

            # Обработка типа занятости
            employment = None
            employment_data = data.get("employment") or data.get("type_of_work")
            if isinstance(employment_data, dict):
                employment = employment_data.get("name") or employment_data.get("title")
            elif isinstance(employment_data, str):
                employment = employment_data

            # Обработка описания и требований
            description = data.get("description") or data.get("vacancyRichText") or ""

            # Для HH API также проверяем snippet
            snippet = data.get("snippet", {})
            if not description.strip() and isinstance(snippet, dict):
                snippet_parts = []
                if snippet.get("requirement"):
                    snippet_parts.append(f"Требования: {snippet.get('requirement')}")
                if snippet.get("responsibility"):
                    snippet_parts.append(f"Обязанности: {snippet.get('responsibility')}")
                if snippet_parts:
                    description = " ".join(snippet_parts)

            # Если описание все еще пустое, но есть requirements или responsibilities - объединяем их
            if not description.strip():
                desc_parts = []
                if data.get("requirements"):
                    desc_parts.append(f"Требования: {data.get('requirements')}")
                if data.get("responsibilities"):
                    desc_parts.append(f"Обязанности: {data.get('responsibilities')}")
                if data.get("candidat"):  # Для SuperJob
                    desc_parts.append(f"Требования: {data.get('candidat')}")
                if data.get("work"):  # Для SuperJob
                    desc_parts.append(f"Обязанности: {data.get('work')}")
                if desc_parts:
                    description = " ".join(desc_parts)

            # Если описание все еще пустое, используем название вакансии
            if not description.strip():
                description = f"Вакансия: {title}"

            requirements = None
            responsibilities = None

            # Для HH (snippet)
            snippet = data.get("snippet", {})
            if isinstance(snippet, dict):
                requirements = snippet.get("requirement")
                responsibilities = snippet.get("responsibility")

            # Для SuperJob (прямые поля)
            if not requirements:
                requirements = data.get("candidat")
            if not responsibilities:
                responsibilities = data.get("work")

            # Определяем источник на основе структуры данных
            source = data.get("source", "unknown")
            # Fallback логика только если источник не установлен
            if source == "unknown":
                if "alternate_url" in data and "hh.ru" in str(data.get("alternate_url", "")):
                    source = "hh.ru"
                elif "hh.ru" in url:
                    source = "hh.ru"
                elif "superjob.ru" in url or "sj.ru" in url:
                    source = "superjob.ru"
                elif "payment_to" in data or "payment_from" in data:
                    source = "superjob.ru"
                elif "name" in data and "snippet" in data:
                    source = "hh.ru"

            vacancy = cls(
                vacancy_id=vacancy_id,
                title=title,
                url=url,
                salary=salary,
                description=description,
                requirements=requirements,
                responsibilities=responsibilities,
                employer=employer,  # Используем исходную структуру employer
                employer_id=employer_id,  # Передаем ID работодателя отдельно
                experience=experience,
                employment=employment,
                schedule=data.get("schedule", {}).get("name") if isinstance(data.get("schedule"), dict) else None,
                published_at=data.get("published_at") or data.get("date_published"),
                detailed_description=data.get("detailed_description"),
                benefits=data.get("benefits"),
                source=source,
                area=data.get("area")  # Передаем area как есть
            )

            # Устанавливаем company_id после создания объекта
            vacancy.company_id = company_id
            # Устанавливаем источник данных
            vacancy.source = source or "unknown"

            return vacancy

        except Exception as e:
            logger.error(f"Ошибка создания унифицированной вакансии из данных: {data}\nОшибка: {e}")
            raise ValueError(f"Невозможно создать унифицированную вакансию: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование объекта в словарь для сериализации

        Returns:
            Dict[str, Any]: Словарь с данными вакансии
        """
        # Безопасная обработка поля company
        company_value = None
        if self.employer: # Используем self.employer, так как он был заполнен обработанной компанией
            if isinstance(self.employer, str):
                company_value = self.employer.lower()
            elif isinstance(self.employer, dict):
                # Если company - словарь, извлекаем имя компании
                company_value = self.employer.get("name", str(self.employer)).lower() if self.employer.get("name") else str(self.employer).lower()
            else:
                company_value = str(self.employer).lower()

        return {
            "vacancy_id": self.vacancy_id,
            "title": self.title,
            "link": self.url, # Использовать self.url вместо self.link
            "salary": self.salary.to_dict() if self.salary else None,
            "description": self.description,
            "company": company_value,
            "employer": self.employer,  # Сохраняем полную структуру employer
            "employer_id": self.employer_id,  # Сохраняем ID работодателя отдельно
            "location": self.area, # Использовать self.area вместо self.location
            "source": self.source,
            "published_date": self.published_at.isoformat() if self.published_at else None, # Использовать self.published_at
            "experience": self.experience,
            "employment": self.employment,
            "schedule": self.schedule,
        }

    def __str__(self) -> str:
        """Строковое представление унифицированной вакансии"""
        # Правильное извлечение имени компании
        company_name = "Не указана"
        if self.employer:
            if isinstance(self.employer, dict):
                company_name = self.employer.get('name', 'Не указана')
            elif isinstance(self.employer, str):
                company_name = self.employer
            else:
                company_name = str(self.employer)

        parts = [
            f"[{self.source.upper()}] Должность: {self.title}",
            f"Компания: {company_name}",
            f"Зарплата: {self.salary}",
            f"Требования: {self.requirements[:100] + '...' if self.requirements else 'Не указаны'}",
            f"Ссылка: {self.url}",
        ]
        return "\n".join(parts)

    def __eq__(self, other) -> bool:
        """Сравнение вакансий по ID"""
        if not isinstance(other, Vacancy):
            return False
        return self.vacancy_id == other.vacancy_id

    def __lt__(self, other) -> bool:
        """Сравнение по зарплате для сортировки"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average < other.salary.average

    def __le__(self, other) -> bool:
        """Сравнение по зарплате (меньше или равно)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average <= other.salary.average

    def __gt__(self, other) -> bool:
        """Сравнение по зарплате (больше)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average > other.salary.average

    def __ge__(self, other) -> bool:
        """Сравнение по зарплате (больше или равно)"""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary.average >= other.salary.average

    def __hash__(self) -> int:
        """Хеш для использования в множествах и словарях"""
        return hash(self.vacancy_id)
