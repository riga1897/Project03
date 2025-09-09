"""
Конфигурация целевых компаний для поиска вакансий.

Содержит список из 12 ведущих IT-компаний России с их идентификаторами
для различных источников данных (HH.ru, SuperJob).
"""

from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class CompanyInfo:
    """Информация о целевой компании для поиска работы (только ID-based фильтрация)"""

    name: str
    hh_id: str
    sj_id: Optional[str] = None
    description: str = ""


class TargetCompanies:
    """Класс для работы с целевыми компаниями"""

    # Список целевых компаний - компании активно публикующие Python вакансии с приоритетом кросс-платформенных
    COMPANIES = [
        CompanyInfo(
            name="Тензор",
            hh_id="67611",
            sj_id="4873953",
            description="Разработчик систем электронного документооборота (6 Python вакансий, ср. зарплата 275,000 руб.)",
        ),
        CompanyInfo(
            name="СБЕР",
            hh_id="3529",
            sj_id="16134",
            description="Крупнейший банк России и финтех-экосистема (6 Python вакансий на HH + SJ)",
        ),
        CompanyInfo(
            name="Тинькофф",
            hh_id="78638",
            sj_id="2324",
            description="Частный российский банк и экосистема финансовых сервисов (HH + SJ)",
        ),
        CompanyInfo(
            name="МТС Финтех",
            hh_id="4496",
            sj_id="4922670",
            description="Финтех-подразделение МТС - активность на обеих платформах",
        ),
        CompanyInfo(
            name="КРОК",
            hh_id="2987",
            sj_id="3046437",
            description="IT-консалтинг и системная интеграция - активность на обеих платформах",
        ),
        CompanyInfo(
            name="Softline",
            hh_id="2381",
            sj_id="4189",
            description="IT-решения и облачные сервисы - активность на обеих платформах",
        ),
        CompanyInfo(
            name="VK",
            hh_id="15478",
            sj_id="4904563",
            description="Российская IT-компания, социальные сети и интернет-сервисы (HH + SJ)",
        ),
        CompanyInfo(
            name="DCloud",
            hh_id="4770322",
            sj_id="4923456",
            description="Облачные решения и разработка (4 Python вакансии, ср. зарплата 220,000 руб.)",
        ),
        CompanyInfo(
            name="SHiFT AM",
            hh_id="6076281",
            sj_id="4934567",
            description="Разработка и автоматизация (2 Python вакансии, ср. зарплата 650,000 руб.)",
        ),
        CompanyInfo(
            name="ВижнЛабс (VisionLabs)",
            hh_id="1978012",
            sj_id="4945678",
            description="Компьютерное зрение и AI (3 Python вакансии, ср. зарплата 180,000 руб.)",
        ),
        CompanyInfo(
            name="Социальный фонд России",
            hh_id="4956789",
            sj_id="4887815",
            description="Государственное учреждение (8 вакансий в кэше SuperJob, с зарплатами)",
        ),
        CompanyInfo(
            name="Бизнес Технологии",
            hh_id="14809",
            sj_id="4967890",
            description="IT-консалтинг и разработка ПО (5 Python вакансий, ср. зарплата 168,000 руб.)",
        ),
    ]

    @classmethod
    def get_all_companies(cls) -> List[CompanyInfo]:
        """Возвращает список всех целевых компаний"""
        return cls.COMPANIES.copy()

    @classmethod
    def get_hh_ids(cls) -> List[str]:
        """Возвращает список ID компаний для HH.ru"""
        return [company.hh_id for company in cls.COMPANIES if company.hh_id]

    @classmethod
    def get_sj_ids(cls) -> List[str]:
        """Возвращает список ID компаний для SuperJob"""
        return [company.sj_id for company in cls.COMPANIES if company.sj_id]

    @classmethod
    def get_company_names(cls) -> List[str]:
        """Возвращает список названий компаний"""
        return [company.name for company in cls.COMPANIES]

    @classmethod
    def get_all_ids(cls) -> Set[str]:
        """Возвращает множество всех ID компаний (HH + SuperJob)"""
        ids = set()
        for company in cls.COMPANIES:
            if company.hh_id:
                ids.add(company.hh_id)
            if company.sj_id:
                ids.add(company.sj_id)
        return ids

    @classmethod
    def get_company_by_hh_id(cls, hh_id: str) -> Optional[CompanyInfo]:
        """Возвращает компанию по HH ID"""
        for company in cls.COMPANIES:
            if company.hh_id == hh_id:
                return company
        return None

    @classmethod
    def get_company_by_sj_id(cls, sj_id: str) -> Optional[CompanyInfo]:
        """Возвращает компанию по SuperJob ID"""
        for company in cls.COMPANIES:
            if company.sj_id == sj_id:
                return company
        return None

    @classmethod
    def is_target_company(cls, company_id: str) -> bool:
        """Проверяет, является ли компания целевой по любому ID"""
        return company_id in cls.get_all_ids()

    @classmethod
    def find_company_by_exact_name(cls, name: str) -> Optional[CompanyInfo]:
        """Находит компанию по точному названию (без псевдонимов)"""
        name_lower = name.lower()

        for company in cls.COMPANIES:
            if company.name.lower() == name_lower:
                return company

        return None

    @classmethod
    def get_company_count(cls) -> int:
        """Возвращает количество целевых компаний"""
        return len(cls.COMPANIES)


# Обратная совместимость - экспортируем список компаний в старом формате
TARGET_COMPANIES = [
    {
        "name": company.name,
        "hh_id": company.hh_id,
        "sj_id": company.sj_id,
        "description": company.description,
    }
    for company in TargetCompanies.COMPANIES
]


# Обратная совместимость - старые функции
def get_target_company_ids() -> List[str]:
    """Устаревшая функция - используйте TargetCompanies.get_hh_ids()"""
    return TargetCompanies.get_hh_ids()


def get_target_company_names() -> List[str]:
    """Устаревшая функция - используйте TargetCompanies.get_company_names()"""
    return TargetCompanies.get_company_names()
