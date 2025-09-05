import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.utils.salary import Salary

from .abstract import AbstractVacancy
from .abstract_models import AbstractEmployer, AbstractEmployment, AbstractExperience, AbstractSalary

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Employer(AbstractEmployer):
    """Конкретная реализация работодателя"""

    def __init__(
        self,
        name: str,
        employer_id: Optional[str] = None,
        trusted: Optional[bool] = None,
        alternate_url: Optional[str] = None,
    ):
        self._name = name
        self._id = employer_id
        self._trusted = trusted
        self._alternate_url = alternate_url

    def get_name(self) -> str:
        """Получить название компании"""
        return self._name or "Не указана"

    def get_id(self) -> Optional[str]:
        """Получить ID работодателя"""
        return self._id

    def is_trusted(self) -> Optional[bool]:
        """Проверить, является ли работодатель проверенным"""
        return self._trusted

    def get_url(self) -> Optional[str]:
        """Получить URL работодателя"""
        return self._alternate_url

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта Employer в словарь"""
        return {"name": self._name, "id": self._id, "trusted": self._trusted, "alternate_url": self._alternate_url}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Employer":
        """Создание объекта Employer из словаря"""
        return cls(
            name=data.get("name", "Не указана"),
            employer_id=data.get("id"),
            trusted=data.get("trusted"),
            alternate_url=data.get("alternate_url"),
        )

    def __str__(self) -> str:
        return self.get_name()

    def __repr__(self) -> str:
        return f"Employer(name='{self._name}', id='{self._id}')"

    # Свойства для обратной совместимости
    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def id(self) -> Optional[str]:
        return self.get_id()

    @property
    def trusted(self) -> Optional[bool]:
        return self._trusted

    @property
    def alternate_url(self) -> Optional[str]:
        return self._alternate_url

    # Метод get для совместимости со словарями
    def get(self, key: str, default=None):
        """Dictionary-like access for backward compatibility"""
        if key == "name":
            return self._name
        elif key == "id":
            return self._id
        elif key == "trusted":
            return self._trusted
        elif key == "alternate_url":
            return self._alternate_url
        return default

    def __eq__(self, other):
        """Comparison with dictionaries for test compatibility"""
        if isinstance(other, dict):
            return self.get("name") == other.get("name") and self.get("id") == other.get("id")
        elif isinstance(other, Employer):
            return self._name == other._name and self._id == other._id
        return False

    def __hash__(self):
        """Hash for sets and dict keys"""
        return hash((self._name, self._id))


class Experience(AbstractExperience):
    """Конкретная реализация опыта работы"""

    def __init__(self, name: str, experience_id: Optional[str] = None):
        self._name = name
        self._id = experience_id

    def get_name(self) -> str:
        """Получить описание опыта"""
        return self._name or "Не указан"

    def get_id(self) -> Optional[str]:
        """Получить ID опыта"""
        return self._id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {"name": self._name, "id": self._id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experience":
        """Создание объекта Experience из словаря"""
        if isinstance(data, str):
            return cls(name=data)
        return cls(name=data.get("name", "Не указан"), experience_id=data.get("id"))

    @classmethod
    def from_string(cls, data: str) -> "Experience":
        """Создание объекта Experience из строки"""
        return cls(name=data or "Не указан")

    def __str__(self) -> str:
        return self.get_name()

    def __repr__(self) -> str:
        return f"Experience(name='{self._name}')"

    # Свойства для обратной совместимости
    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def id(self) -> Optional[str]:
        return self.get_id()


class Employment(AbstractEmployment):
    """Конкретная реализация типа занятости"""

    def __init__(self, name: str, employment_id: Optional[str] = None):
        self._name = name
        self._id = employment_id

    def get_name(self) -> str:
        """Получить тип занятости"""
        return self._name or "Не указан"

    def get_id(self) -> Optional[str]:
        """Получить ID типа занятости"""
        return self._id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {"name": self._name, "id": self._id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Employment":
        """Создание объекта Employment из словаря"""
        if isinstance(data, str):
            return cls(name=data)
        return cls(name=data.get("name", "Не указан"), employment_id=data.get("id"))

    @classmethod
    def from_string(cls, data: str) -> "Employment":
        """Создание объекта Employment из строки"""
        return cls(name=data or "Не указан")

    def __str__(self) -> str:
        return self.get_name()

    def __repr__(self) -> str:
        return f"Employment(name='{self._name}')"

    # Свойства для обратной совместимости
    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def id(self) -> Optional[str]:
        return self.get_id()


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
        salary: Optional[Union[Salary, AbstractSalary, Dict[str, Any]]] = None,
        description: str = "",
        requirements: Optional[str] = None,
        responsibilities: Optional[str] = None,
        employer: Optional[Union[Employer, AbstractEmployer, Dict[str, Any]]] = None,
        employer_id: Optional[str] = None,
        experience: Optional[Union[Experience, AbstractExperience, str, Dict[str, Any]]] = None,
        employment: Optional[Union[Employment, AbstractEmployment, str, Dict[str, Any]]] = None,
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

        # Преобразуем employer в объект
        self.employer = self._validate_employer(employer)
        self.employer_id = employer_id

        # Преобразуем experience в объект
        self.experience = self._validate_experience(experience)

        # Преобразуем employment в объект
        self.employment = self._validate_employment(employment)
        self.schedule = schedule
        self.published_at = self._parse_datetime(published_at) if published_at else None
        self.skills = skills or []
        self.detailed_description = detailed_description or description
        self.benefits = benefits
        self.source = source

        # Унифицированная обработка area
        try:
            from utils.data_normalizers import normalize_area_data
        except ImportError:
            from src.utils.data_normalizers import normalize_area_data
        self.area = normalize_area_data(area)

    @staticmethod
    def _validate_salary(salary_data: Optional[Union[Salary, AbstractSalary, Dict[str, Any]]]) -> Salary:
        """Приватный метод валидации данных о зарплате"""
        # Если уже объект Salary, возвращаем как есть
        if isinstance(salary_data, Salary):
            return salary_data
        # Если AbstractSalary, создаем Salary на основе его данных
        if isinstance(salary_data, AbstractSalary):
            return Salary(salary_data.to_dict())
        # Если словарь, создаем новый объект Salary
        return Salary(salary_data) if salary_data else Salary()

    @staticmethod
    def _validate_employer(
        employer_data: Optional[Union[Employer, AbstractEmployer, Dict[str, Any]]],
    ) -> Optional[Employer]:
        """Приватный метод валидации данных о работодателе"""
        if not employer_data:
            return None

        # Если уже объект Employer, возвращаем как есть
        if isinstance(employer_data, Employer):
            return employer_data

        # Если AbstractEmployer, создаем Employer
        if isinstance(employer_data, AbstractEmployer):
            return Employer(
                name=employer_data.get_name(),
                employer_id=employer_data.get_id(),
                trusted=employer_data.is_trusted(),
                alternate_url=employer_data.get_url(),
            )

        # Если словарь, создаем объект Employer
        if isinstance(employer_data, dict):
            return Employer.from_dict(employer_data)

        # Если строка, создаем объект с именем
        if isinstance(employer_data, str):
            return Employer(name=employer_data)

        return None

    @staticmethod
    def _validate_experience(
        experience_data: Optional[Union[Experience, AbstractExperience, str, Dict[str, Any]]],
    ) -> Optional[Experience]:
        """Приватный метод валидации данных об опыте"""
        if not experience_data:
            return None

        # Если уже объект Experience, возвращаем как есть
        if isinstance(experience_data, Experience):
            return experience_data

        # Если AbstractExperience, создаем Experience
        if isinstance(experience_data, AbstractExperience):
            return Experience(name=experience_data.get_name(), experience_id=experience_data.get_id())

        # Если словарь, создаем объект Experience
        if isinstance(experience_data, dict):
            return Experience.from_dict(experience_data)

        # Если строка, создаем объект из строки
        if isinstance(experience_data, str):
            return Experience.from_string(experience_data)

        return None

    @staticmethod
    def _validate_employment(
        employment_data: Optional[Union[Employment, AbstractEmployment, str, Dict[str, Any]]],
    ) -> Optional[Employment]:
        """Приватный метод валидации данных о занятости"""
        if not employment_data:
            return None

        # Если уже объект Employment, возвращаем как есть
        if isinstance(employment_data, Employment):
            return employment_data

        # Если AbstractEmployment, создаем Employment
        if isinstance(employment_data, AbstractEmployment):
            return Employment(name=employment_data.get_name(), employment_id=employment_data.get_id())

        # Если словарь, создаем объект Employment
        if isinstance(employment_data, dict):
            return Employment.from_dict(employment_data)

        # Если строка, создаем объект из строки
        if isinstance(employment_data, str):
            return Employment.from_string(employment_data)

        return None

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
                or data.get("url")  # API-ссылка
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

            # Унифицированная обработка опыта работы
            try:
                from utils.data_normalizers import normalize_experience_data
            except ImportError:
                from src.utils.data_normalizers import normalize_experience_data
            experience = normalize_experience_data(data.get("experience"))

            # Унифицированная обработка типа занятости
            try:
                from utils.data_normalizers import normalize_employment_data
            except ImportError:
                from src.utils.data_normalizers import normalize_employment_data
            employment_raw = data.get("employment") or data.get("type_of_work")
            employment = normalize_employment_data(employment_raw)

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

            # Для HH (snippet)
            requirements = ""
            responsibilities = ""
            snippet = data.get("snippet", {})
            if isinstance(snippet, dict):
                requirements = snippet.get("requirement") or ""
                responsibilities = snippet.get("responsibility") or ""

            # Для SuperJob (прямые поля)
            if not requirements:
                requirements = data.get("candidat") or ""
            if not responsibilities:
                responsibilities = data.get("work") or ""

            # Извлекаем структурированные требования и обязанности из описания
            # если они все еще пустые после обработки всех источников
            try:
                from src.utils.description_parser import DescriptionParser

                # Если поля пустые, пытаемся извлечь из description
                if (not requirements or not requirements.strip()) or (
                    not responsibilities or not responsibilities.strip()
                ):
                    extracted_req, extracted_resp = DescriptionParser.extract_requirements_and_responsibilities(
                        description
                    )

                    if (not requirements or not requirements.strip()) and extracted_req:
                        requirements = extracted_req
                    if (not responsibilities or not responsibilities.strip()) and extracted_resp:
                        responsibilities = extracted_resp

            except ImportError:
                logger.warning("DescriptionParser не найден, пропускаем извлечение структурированных данных")
            except Exception as e:
                logger.warning(f"Ошибка извлечения структурированных данных: {e}")

            # Определяем источник на основе структуры данных
            source = data.get("source", "unknown")
            # Определение источника по структуре данных
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
                area=data.get("area"),  # Передаем area как есть
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
        """Преобразование вакансии в словарь"""
        result = {
            "vacancy_id": self.vacancy_id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "area": self.area,
            "experience": self.experience,
            "employment": self.employment,
            "description": self.description,
            "published_at": self.published_at,
        }

        if self.salary:
            # Обработка salary как словаря или объекта
            if isinstance(self.salary, dict):
                result["salary"] = {
                    "from_amount": self.salary.get("salary_from", self.salary.get("amount_from")),
                    "to_amount": self.salary.get("salary_to", self.salary.get("amount_to")),
                    "currency": self.salary.get("currency", ""),
                }
            else:
                # Если это объект Salary
                result["salary"] = {
                    "from_amount": getattr(self.salary, "amount_from", getattr(self.salary, "salary_from", None)),
                    "to_amount": getattr(self.salary, "amount_to", getattr(self.salary, "salary_to", None)),
                    "currency": getattr(self.salary, "currency", ""),
                }

        if self.employer:
            # Обработка employer как словаря или объекта
            if isinstance(self.employer, dict):
                result["employer"] = {"name": self.employer.get("name", ""), "url": self.employer.get("url", "")}
            else:
                # Если это объект Employer
                result["employer"] = {
                    "name": getattr(self.employer, "name", str(self.employer)),
                    "url": getattr(self.employer, "url", ""),
                }

        return result

    def __str__(self) -> str:
        """Строковое представление унифицированной вакансии"""
        # Правильное извлечение имени компании
        company_name = "Не указана"
        if self.employer:
            if isinstance(self.employer, dict):
                company_name = self.employer.get("name", "Не указана")
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
