"""
Pydantic модели для вакансий с автоматической валидацией и сериализацией.

Эти модели работают параллельно с существующими классами и предоставляют:
- Автоматическую валидацию данных
- Типобезопасность
- Простую сериализацию/десериализацию
- Интеграцию с JSON
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
import uuid

from ..utils.salary import Salary


class EmployerModel(BaseModel):
    """Pydantic модель для работодателя"""
    
    name: str = Field(..., min_length=1, description="Название компании")
    id: Optional[str] = Field(None, description="ID работодателя")
    trusted: Optional[bool] = Field(None, description="Проверенный работодатель")
    alternate_url: Optional[str] = Field(None, description="URL работодателя")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or v.strip() == "":
            return "Не указана"
        return v.strip()
    
    @validator('alternate_url')
    def validate_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f"https://{v}"
        return v
    
    class Config:
        json_encoders = {
            # Кастомные энкодеры для специальных типов
        }
        
    def to_legacy_employer(self):
        """Конвертация в существующий класс Employer для обратной совместимости"""
        from .models import Employer
        return Employer(
            name=self.name,
            employer_id=self.id,
            trusted=self.trusted,
            alternate_url=self.alternate_url
        )


class ExperienceModel(BaseModel):
    """Pydantic модель для опыта работы"""
    
    name: str = Field(..., description="Описание требуемого опыта")
    id: Optional[str] = Field(None, description="ID опыта")
    
    @validator('name')
    def validate_experience_name(cls, v):
        if not v:
            return "Не указан"
        return v.strip()
    
    def to_legacy_experience(self):
        """Конвертация в существующий класс Experience"""
        from .models import Experience
        return Experience(name=self.name, experience_id=self.id)


class EmploymentModel(BaseModel):
    """Pydantic модель для типа занятости"""
    
    name: str = Field(..., description="Тип занятости")
    id: Optional[str] = Field(None, description="ID типа занятости")
    
    @validator('name')
    def validate_employment_name(cls, v):
        if not v:
            return "Не указан"
        return v.strip()
    
    def to_legacy_employment(self):
        """Конвертация в существующий класс Employment"""
        from .models import Employment
        return Employment(name=self.name, employment_id=self.id)


class SalaryModel(BaseModel):
    """Pydantic модель для зарплаты"""
    
    amount_from: Optional[int] = Field(None, ge=0, description="Зарплата от")
    amount_to: Optional[int] = Field(None, ge=0, description="Зарплата до") 
    currency: str = Field("RUR", description="Валюта")
    gross: bool = Field(False, description="До вычета налогов")
    period: str = Field("month", description="Период выплаты")
    
    @validator('amount_to')
    def validate_salary_range(cls, v, values):
        if 'amount_from' in values and values['amount_from'] is not None and v is not None:
            if v < values['amount_from']:
                raise ValueError('amount_to должно быть больше или равно amount_from')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ['RUR', 'USD', 'EUR', 'KZT', 'UZS', 'BYR']
        if v not in allowed_currencies:
            return 'RUR'
        return v
    
    @property
    def average(self) -> Optional[int]:
        """Среднее значение зарплаты"""
        if self.amount_from and self.amount_to:
            return (self.amount_from + self.amount_to) // 2
        return self.amount_from or self.amount_to
    
    @property
    def max_value(self) -> Optional[int]:
        """Максимальное значение зарплаты"""
        return self.amount_to or self.amount_from
    
    def to_legacy_salary(self) -> Salary:
        """Конвертация в существующий класс Salary"""
        salary_data = {
            'from': self.amount_from,
            'to': self.amount_to,
            'currency': self.currency,
            'gross': self.gross
        }
        return Salary(salary_data)
    
    def format_salary(self) -> str:
        """Форматированное представление зарплаты"""
        if not self.amount_from and not self.amount_to:
            return "Не указана"
        
        components = []
        if self.amount_from:
            components.append(f"от {self.amount_from:,}")
        if self.amount_to:
            components.append(f"до {self.amount_to:,}")
        
        currency_symbols = {"RUR": "руб.", "USD": "$", "EUR": "€", "KZT": "₸"}
        currency = currency_symbols.get(self.currency, self.currency)
        
        period_str = ""
        if self.period in ["месяц", "month"]:
            period_str = "в месяц"
        elif self.period:
            period_str = f"в {self.period}"
        
        gross = " до вычета налогов" if self.gross else ""
        
        return f"{' '.join(components)} {currency} {period_str}{gross}".strip()


class VacancyModel(BaseModel):
    """Pydantic модель для вакансии"""
    
    id: str = Field(..., description="Уникальный ID вакансии")
    name: str = Field(..., min_length=1, description="Название вакансии")
    url: str = Field(..., description="URL вакансии")
    
    employer: Optional[EmployerModel] = Field(None, description="Работодатель")
    salary: Optional[SalaryModel] = Field(None, description="Зарплата")
    experience: Optional[ExperienceModel] = Field(None, description="Требуемый опыт")
    employment: Optional[EmploymentModel] = Field(None, description="Тип занятости")
    
    area: Optional[str] = Field(None, description="Город/регион")
    schedule: Optional[str] = Field(None, description="График работы")
    requirements: Optional[str] = Field(None, description="Требования")
    responsibilities: Optional[str] = Field(None, description="Обязанности")
    description: Optional[str] = Field(None, description="Описание вакансии")
    
    published_at: Optional[Union[datetime, str]] = Field(None, description="Дата публикации")
    source: Optional[str] = Field(None, description="Источник вакансии")
    
    # Внутренние поля
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Дата создания записи")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления записи")
    
    @validator('id', pre=True)
    def validate_id(cls, v):
        if not v:
            return str(uuid.uuid4())
        return str(v)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Название вакансии не может быть пустым')
        return v.strip()
    
    @validator('url')
    def validate_url(cls, v):
        if not v:
            raise ValueError('URL вакансии обязателен')
        if not (v.startswith('http://') or v.startswith('https://')):
            return f"https://{v}"
        return v
    
    @validator('published_at', pre=True)
    def validate_published_at(cls, v):
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
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return None
        return v
    
    @root_validator
    def validate_vacancy_data(cls, values):
        """Комплексная валидация данных вакансии"""
        # Проверяем что ID и URL совместимы с источником
        if values.get('source') == 'hh.ru' and values.get('id'):
            if not str(values['id']).isdigit():
                # Для HeadHunter ID должен быть числовым
                pass
        
        return values
    
    def to_legacy_vacancy(self):
        """Конвертация в существующий класс Vacancy"""
        from .models import Vacancy
        
        # Создаем legacy объекты для связанных сущностей
        legacy_employer = self.employer.to_legacy_employer() if self.employer else None
        legacy_experience = self.experience.to_legacy_experience() if self.experience else None
        legacy_employment = self.employment.to_legacy_employment() if self.employment else None
        legacy_salary = self.salary.to_legacy_salary() if self.salary else None
        
        return Vacancy(
            vacancy_id=self.id,
            name=self.name,
            url=self.url,
            employer=legacy_employer,
            salary=legacy_salary,
            experience=legacy_experience,
            employment=legacy_employment,
            area=self.area,
            schedule=self.schedule,
            requirements=self.requirements,
            responsibilities=self.responsibilities,
            description=self.description,
            published_at=self.published_at,
            source=self.source
        )
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None,
        }
        # Позволяем дополнительные поля для гибкости
        extra = "ignore"
        # Используем enum значения
        use_enum_values = True


# Утилиты для работы с моделями
class VacancyFactory:
    """Фабрика для создания вакансий из различных источников"""
    
    @staticmethod
    def from_hh_api(data: Dict[str, Any]) -> VacancyModel:
        """Создание вакансии из данных HeadHunter API"""
        employer_data = data.get('employer', {})
        salary_data = data.get('salary', {})
        experience_data = data.get('experience', {})
        employment_data = data.get('employment', {})
        
        return VacancyModel(
            id=str(data.get('id', str(uuid.uuid4()))),
            name=data.get('name', ''),
            url=data.get('alternate_url', ''),
            employer=EmployerModel(**employer_data) if employer_data else None,
            salary=SalaryModel(
                amount_from=salary_data.get('from'),
                amount_to=salary_data.get('to'),
                currency=salary_data.get('currency', 'RUR'),
                gross=salary_data.get('gross', False)
            ) if salary_data else None,
            experience=ExperienceModel(
                name=experience_data.get('name', 'Не указан'),
                id=experience_data.get('id')
            ) if experience_data else None,
            employment=EmploymentModel(
                name=employment_data.get('name', 'Не указан'),
                id=employment_data.get('id')
            ) if employment_data else None,
            area=data.get('area', {}).get('name'),
            schedule=data.get('schedule', {}).get('name'),
            requirements=data.get('snippet', {}).get('requirement'),
            responsibilities=data.get('snippet', {}).get('responsibility'),
            published_at=data.get('published_at'),
            source='hh.ru'
        )
    
    @staticmethod
    def from_superjob_api(data: Dict[str, Any]) -> VacancyModel:
        """Создание вакансии из данных SuperJob API"""
        return VacancyModel(
            id=str(data.get('id', str(uuid.uuid4()))),
            name=data.get('profession', ''),
            url=data.get('link', ''),
            employer=EmployerModel(
                name=data.get('firm_name', 'Не указана'),
                id=str(data.get('id_client', ''))
            ) if data.get('firm_name') else None,
            salary=SalaryModel(
                amount_from=data.get('payment_from') if data.get('payment_from', 0) > 0 else None,
                amount_to=data.get('payment_to') if data.get('payment_to', 0) > 0 else None,
                currency='RUR',  # SuperJob использует только рубли
                gross=False
            ) if (data.get('payment_from', 0) > 0 or data.get('payment_to', 0) > 0) else None,
            area=data.get('town', {}).get('title') if isinstance(data.get('town'), dict) else data.get('town'),
            requirements=data.get('candidat'),
            responsibilities=data.get('work'),
            published_at=data.get('date_published'),
            source='superjob.ru'
        )


class VacancyListModel(BaseModel):
    """Модель для списка вакансий с метаданными"""
    
    vacancies: List[VacancyModel] = Field(default_factory=list, description="Список вакансий")
    total_count: Optional[int] = Field(None, description="Общее количество вакансий")
    page: Optional[int] = Field(None, description="Текущая страница")
    per_page: Optional[int] = Field(None, description="Вакансий на странице")
    pages: Optional[int] = Field(None, description="Всего страниц")
    
    def add_vacancy(self, vacancy: VacancyModel) -> None:
        """Добавить вакансию в список"""
        self.vacancies.append(vacancy)
    
    def filter_by_salary(self, min_salary: Optional[int] = None) -> "VacancyListModel":
        """Фильтровать вакансии по зарплате"""
        if min_salary is None:
            return self
        
        filtered_vacancies = []
        for vacancy in self.vacancies:
            if vacancy.salary and (
                (vacancy.salary.amount_from and vacancy.salary.amount_from >= min_salary) or
                (vacancy.salary.amount_to and vacancy.salary.amount_to >= min_salary)
            ):
                filtered_vacancies.append(vacancy)
        
        return VacancyListModel(
            vacancies=filtered_vacancies,
            total_count=len(filtered_vacancies)
        )
    
    def get_unique_employers(self) -> List[str]:
        """Получить список уникальных работодателей"""
        employers = set()
        for vacancy in self.vacancies:
            if vacancy.employer:
                employers.add(vacancy.employer.name)
        return sorted(list(employers))