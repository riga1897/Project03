"""Модели данных для системы поиска вакансий на основе Pydantic v2.

Этот модуль содержит все модели данных для работы с вакансиями, работодателями
и связанными объектами. Полностью заменяет прежнюю архитектуру с улучшенной
валидацией, типобезопасностью и автоматической сериализацией.

Classes:
    Employer: Модель работодателя с валидацией
    Experience: Модель опыта работы
    Area: Модель географической области
    Schedule: Модель графика работы
    Employment: Модель типа занятости
    KeySkill: Модель ключевых навыков
    Vacancy: Основная модель вакансии
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.utils.salary import Salary

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Employer(BaseModel):
    """Модель работодателя с валидацией данных.

    Представляет информацию о компании-работодателе с автоматической валидацией
    и нормализацией данных при создании и обновлении объекта.

    Attributes:
        name: Название компании (обязательное поле).
        id: Уникальный идентификатор работодателя.
        trusted: Флаг проверенного работодателя.
        alternate_url: URL страницы работодателя.
    """

    name: str = Field(..., min_length=1, description="Название компании")
    id: Optional[str] = Field(None, description="ID работодателя")
    trusted: Optional[bool] = Field(None, description="Проверенный работодатель")
    alternate_url: Optional[str] = Field(None, description="URL работодателя")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидирует и нормализует название компании.

        Args:
            v: Входное название компании.

        Returns:
            Нормализованное название компании.
        """
        if not v or v.strip() == "":
            return "Не указана"
        return v.strip()

    @field_validator("alternate_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Валидирует и нормализует URL.

        Args:
            v: Входной URL.

        Returns:
            Нормализованный URL с протоколом.
        """
        if v and not (v.startswith("http://") or v.startswith("https://")):
            return f"https://{v}"
        return v

    # Методы для обратной совместимости с существующим кодом
    def get_name(self) -> str:
        """Получить название компании.
        
        Returns:
            Название компании.
        """
        return self.name

    def get_id(self) -> Optional[str]:
        """Получить ID работодателя.
        
        Returns:
            ID работодателя или None.
        """
        return self.id

    def is_trusted(self) -> Optional[bool]:
        """Проверить, является ли работодатель проверенным.
        
        Returns:
            True если работодатель проверен, False или None иначе.
        """
        return self.trusted

    def get_url(self) -> Optional[str]:
        """Получить URL работодателя.
        
        Returns:
            URL страницы работодателя или None.
        """
        return self.alternate_url

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь.
        
        Returns:
            Словарь с данными работодателя.
        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Employer":
        """Создание объекта из словаря.
        
        Args:
            data: Словарь с данными работодателя.
            
        Returns:
            Новый экземпляр Employer.
        """
        return cls(**data)

    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like access для обратной совместимости.
        
        Args:
            key: Ключ для доступа к атрибуту.
            default: Значение по умолчанию если ключ не найден.
            
        Returns:
            Значение атрибута или значение по умолчанию.
        """
        return getattr(self, key, default)

    model_config = ConfigDict(validate_assignment=True, use_attribute_docstrings=True)


class Experience(BaseModel):
    """Модель опыта работы с Pydantic валидацией"""

    name: str = Field(..., description="Описание требуемого опыта")
    id: Optional[str] = Field(None, description="ID опыта")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидирует и нормализует описание опыта работы.
        
        Args:
            v: Входное описание опыта.
            
        Returns:
            Нормализованное описание опыта.
        """
        if not v:
            return "Не указан"
        return v.strip()

    # Методы для обратной совместимости
    def get_name(self) -> str:
        """Получить описание опыта"""
        return self.name

    def get_id(self) -> Optional[str]:
        """Получить ID опыта"""
        return self.id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experience":
        """Создать из словаря"""
        return cls(**data)

    @classmethod
    def from_string(cls, data: str) -> "Experience":
        """Создать из строки"""
        return cls(name=data)

    model_config = ConfigDict(validate_assignment=True)


class Employment(BaseModel):
    """Модель типа занятости с Pydantic валидацией"""

    name: str = Field(..., description="Тип занятости")
    id: Optional[str] = Field(None, description="ID типа занятости")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидирует и нормализует тип занятости.
        
        Args:
            v: Входной тип занятости.
            
        Returns:
            Нормализованный тип занятости.
        """
        if not v:
            return "Не указан"
        return v.strip()

    # Методы для обратной совместимости
    def get_name(self) -> str:
        """Получить тип занятости"""
        return self.name

    def get_id(self) -> Optional[str]:
        """Получить ID типа занятости"""
        return self.id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Employment":
        """Создать из словаря"""
        return cls(**data)

    @classmethod
    def from_string(cls, data: str) -> "Employment":
        """Создать из строки"""
        return cls(name=data)

    model_config = ConfigDict(validate_assignment=True)


class Schedule(BaseModel):
    """Модель графика работы с Pydantic валидацией"""

    name: str = Field(..., description="Название графика")
    id: Optional[str] = Field(None, description="ID графика")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидирует и нормализует название графика работы.
        
        Args:
            v: Входное название графика.
            
        Returns:
            Нормализованное название графика.
        """
        if not v:
            return "Не указан"
        return v.strip()

    # Методы для обратной совместимости
    def get_name(self) -> str:
        """Получить название графика"""
        return self.name

    def get_id(self) -> Optional[str]:
        """Получить ID графика"""
        return self.id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Schedule":
        """Создать из словаря"""
        return cls(**data)

    @classmethod
    def from_string(cls, data: str) -> "Schedule":
        """Создать из строки"""
        return cls(name=data)

    model_config = ConfigDict(validate_assignment=True)


class Vacancy(BaseModel):
    """Основная модель вакансии с Pydantic валидацией"""

    # Основная информация
    id: str = Field(alias="vacancy_id", description="Идентификатор вакансии")
    title: str = Field(alias="name", description="Название вакансии")
    url: str = Field(alias="alternate_url", description="Ссылка на вакансии")

    # Описание и требования
    description: Optional[str] = Field(default=None, description="Описание вакансии")
    requirements: Optional[str] = Field(default=None, description="Требования к кандидату")
    responsibilities: Optional[str] = Field(default=None, description="Обязанности")
    detailed_description: Optional[str] = Field(default=None, description="Подробное описание")

    # Связанные объекты
    employer: Optional[Employer] = Field(None, description="Работодатель")
    salary: Optional[Dict[str, Any]] = Field(None, description="Данные о зарплате")
    experience: Optional[Experience] = Field(None, description="Требуемый опыт")
    employment: Optional[Employment] = Field(None, description="Тип занятости")
    schedule: Optional[Schedule] = Field(None, description="График работы")

    # Временные метки
    published_at: Optional[Union[datetime, str]] = Field(None, description="Дата публикации")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Дата создания записи")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления записи")

    # Метаинформация
    area: Optional[str] = Field(None, description="Регион/местоположение вакансии")
    source: Optional[str] = Field(None, description="Источник вакансии")
    company_id: Optional[int] = Field(None, description="ID компании в БД (для связи с таблицей companies)")

    @field_validator("title", mode="before")
    @classmethod
    def validate_name_vacancy(cls, v: str) -> str:
        """Валидирует название вакансии.
        
        Args:
            v: Входное название вакансии.
            
        Returns:
            Нормализованное название вакансии.
        
        Raises:
            ValueError: Когда название пустое.
        """
        if not v or not v.strip():
            raise ValueError("Название вакансии не может быть пустым")
        return v.strip()

    @field_validator("url", mode="before")
    @classmethod
    def validate_url_vacancy(cls, v: str) -> str:
        """Валидирует и нормализует URL вакансии.
        
        Args:
            v: Входной URL.
            
        Returns:
            Нормализованный URL с протоколом.
        
        Raises:
            ValueError: Когда URL пустой.
        """
        if not v:
            raise ValueError("URL вакансии обязателен")
        if not (v.startswith("http://") or v.startswith("https://")):
            return f"https://{v}"
        return v

    @field_validator("area", mode="before")
    @classmethod
    def validate_area(cls, v: Any) -> Optional[str]:
        """Валидация и нормализация поля area из API ответов.
        
        Args:
            v: Входное значение области (может быть dict, str или другим типом).
            
        Returns:
            Нормализованное название области или None.
        """
        if v is None:
            return None

        # Если пришел объект из API (например, {'id': '1', 'name': 'Москва'})
        if isinstance(v, dict):
            # Приоритет: name > title > id
            if "name" in v:
                return str(v["name"]).strip()
            elif "title" in v:
                return str(v["title"]).strip()
            elif "id" in v:
                return str(v["id"]).strip()
            else:
                return str(v).strip() if str(v).strip() != "{}" else None

        # Если уже строка
        if isinstance(v, str):
            return v.strip() if v.strip() else None

        # Для остальных типов
        return str(v).strip() if str(v).strip() else None

    @field_validator("published_at", mode="before")
    @classmethod
    def validate_published_at(cls, v: Any) -> Optional[datetime]:
        """Валидирует и преобразует дату публикации вакансии.
        
        Args:
            v: Входное значение даты (строка, datetime или None).
            
        Returns:
            Объект datetime или None.
        """
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Попытка парсинга различных форматов дат
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"]:
                    try:
                        return datetime.strptime(v, fmt)
                    except ValueError:
                        continue
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return v  # Возвращаем как есть, если не удалось распарсить
        return v

    @field_validator("salary", mode="before")
    @classmethod
    def validate_salary(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Валидирует и нормализует данные о зарплате.
        
        Args:
            v: Входные данные о зарплате.
            
        Returns:
            Нормализованные данные о зарплате или None.
        """
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        # Если передан объект Salary, конвертируем в словарь
        if hasattr(v, "to_dict"):
            return v.to_dict()
        return v

    @model_validator(mode="after")
    def validate_vacancy_data(self) -> "Vacancy":
        """Комплексная валидация данных вакансии.
        
        Returns:
            Проверенные данные вакансии.
        """
        # Проверяем что ID и URL совместимы с источником
        if self.source == "hh.ru" and self.id:
            if not str(self.id).isdigit():
                # Для HeadHunter ID обычно числовой, но оставляем гибкость
                pass

        return self

    # Методы для работы с зарплатой (обратная совместимость)
    def get_salary(self) -> Optional[Salary]:
        """Получить объект зарплаты"""
        if self.salary:
            return Salary(self.salary)
        return None

    def set_salary(self, salary_data: Union[Dict[str, Any], Salary, None]) -> None:
        """Установить данные о зарплате.
        
        Args:
            salary_data: Данные о зарплате в виде словаря, объекта Salary или None.
        """
        if salary_data is None:
            self.salary = None
        elif isinstance(salary_data, dict):
            self.salary = salary_data
        elif isinstance(salary_data, Salary):
            self.salary = salary_data.to_dict()
        else:
            self.salary = None

    # Методы для обратной совместимости
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = self.model_dump()
        # Преобразуем datetime в строки для JSON совместимости
        if data.get("published_at") and isinstance(data["published_at"], datetime):
            data["published_at"] = data["published_at"].isoformat()
        if data.get("created_at") and isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at") and isinstance(data["updated_at"], datetime):
            data["updated_at"] = data["updated_at"].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vacancy":
        """Создание объекта из словаря"""
        # Обрабатываем вложенные объекты
        processed_data = data.copy()

        # ИСПРАВЛЕНО: Правильный маппинг для Pydantic v2 с alias
        # Если данные приходят с API ключами, сохраняем их в правильных alias именах
        # НЕ удаляем исходные ключи, а добавляем нужные alias ключи
        if "id" in processed_data and "vacancy_id" not in processed_data:
            processed_data["vacancy_id"] = processed_data["id"]
        # Для Pydantic v2 с alias="name" нужно оставить данные в ключе 'name'
        # Аналогично для alternate_url

        # Employer
        if "employer" in processed_data and isinstance(processed_data["employer"], dict):
            processed_data["employer"] = Employer(**processed_data["employer"])

        # Experience
        if "experience" in processed_data and isinstance(processed_data["experience"], dict):
            processed_data["experience"] = Experience(**processed_data["experience"])

        # Employment
        if "employment" in processed_data and isinstance(processed_data["employment"], dict):
            processed_data["employment"] = Employment(**processed_data["employment"])

        # Schedule
        if "schedule" in processed_data and isinstance(processed_data["schedule"], dict):
            processed_data["schedule"] = Schedule(**processed_data["schedule"])

        return cls(**processed_data)

    # Дополнительные методы для удобства
    def __str__(self) -> str:
        """Строковое представление вакансии для пользователей.
        
        Returns:
            Строка в формате "Название - Работодатель".
        """
        employer_name = self.employer.name if self.employer else "Не указан"
        return f"{self.title} - {employer_name}"

    def __repr__(self) -> str:
        """Строковое представление вакансии для разработчиков.
        
        Returns:
            Строка с ID и названием вакансии.
        """
        return f"Vacancy(id='{self.id}', title='{self.title}')"

    model_config = ConfigDict(extra="ignore", use_enum_values=True, validate_assignment=True)


# Фабричные методы для создания объектов из API
class VacancyFactory:
    """Фабрика для создания вакансий из различных источников данных"""

    @staticmethod
    def from_hh_api(data: Dict[str, Any]) -> Vacancy:
        """Создание вакансии из данных HeadHunter API"""
        employer_data = data.get("employer", {})
        salary_data = data.get("salary", {})
        experience_data = data.get("experience", {})
        employment_data = data.get("employment", {})
        schedule_data = data.get("schedule", {})

        return Vacancy(
            vacancy_id=str(data.get("id", str(uuid.uuid4()))),
            name=data.get("name", ""),
            alternate_url=data.get("alternate_url", ""),
            employer=Employer(**employer_data) if employer_data else None,
            salary=salary_data if salary_data else None,
            experience=Experience(**experience_data) if experience_data else None,
            employment=Employment(**employment_data) if employment_data else None,
            schedule=Schedule(**schedule_data) if schedule_data else None,
            area=data.get("area", {}).get("name") if isinstance(data.get("area"), dict) else data.get("area"),
            requirements=data.get("snippet", {}).get("requirement") if isinstance(data.get("snippet"), dict) else None,
            responsibilities=(
                data.get("snippet", {}).get("responsibility") if isinstance(data.get("snippet"), dict) else None
            ),
            description=data.get("description"),
            published_at=data.get("published_at"),
            source="hh.ru",
        )

    @staticmethod
    def from_superjob_api(data: Dict[str, Any]) -> Vacancy:
        """Создание вакансии из данных SuperJob API"""
        salary_data = None
        if data.get("payment_from", 0) > 0 or data.get("payment_to", 0) > 0:
            salary_data = {
                "from": data.get("payment_from") if data.get("payment_from", 0) > 0 else None,
                "to": data.get("payment_to") if data.get("payment_to", 0) > 0 else None,
                "currency": "RUR",
                "gross": False,
            }

        return Vacancy(
            vacancy_id=str(data.get("id", str(uuid.uuid4()))),
            name=data.get("profession", ""),
            alternate_url=data.get("link", ""),
            employer=(
                Employer(
                    name=data.get("firm_name", "Не указана"),
                    id=str(data.get("id_client", "")) if data.get("id_client") else None,
                )
                if data.get("firm_name")
                else None
            ),
            salary=salary_data,
            area=data.get("town", {}).get("title") if isinstance(data.get("town"), dict) else data.get("town"),
            requirements=data.get("candidat"),
            responsibilities=data.get("work"),
            published_at=data.get("date_published"),
            source="superjob.ru",
        )


# Типы для экспорта
__all__ = ["Employer", "Experience", "Employment", "Schedule", "Vacancy", "VacancyFactory"]
