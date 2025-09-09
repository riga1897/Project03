"""
Конфигурация целевых компаний для поиска вакансий.

Содержит список из 12 ведущих IT-компаний России с их идентификаторами
для различных источников данных (HH.ru, SuperJob).
Компании выбраны на основе анализа реального кэша SuperJob API.
"""

from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class CompanyInfo:
    """Информация о целевой компании для поиска работы (только ID-based фильтрация)"""

    name: str
    hh_id: Optional[str]
    sj_id: Optional[str] = None
    description: str = ""


class TargetCompanies:
    """Класс для работы с целевыми компаниями"""

    # Список целевых компаний - оптимизированный список из 12 компаний
    COMPANIES = [
        # Компании с обоими API (7 шт.)
        CompanyInfo(
            name="СБЕР",
            hh_id="3529",
            sj_id="16134",
            description="Крупнейший банк России и финтех-экосистема (проверенные ID на обеих платформах)",
        ),
        CompanyInfo(
            name="Тинькофф",
            hh_id="78638",
            sj_id="2324",
            description="Частный российский банк и экосистема финансовых сервисов (проверенные ID)",
        ),
        CompanyInfo(
            name="МТС Финтех",
            hh_id="4496",
            sj_id="4922670",
            description="Финтех-подразделение МТС (проверенные ID на обеих платформах)",
        ),
        CompanyInfo(
            name="КРОК",
            hh_id="2987",
            sj_id="3046437",
            description="IT-консалтинг и системная интеграция (проверенные ID)",
        ),
        CompanyInfo(
            name="Softline",
            hh_id="2381",
            sj_id="4189",
            description="IT-решения и облачные сервисы (проверенные ID)",
        ),
        CompanyInfo(
            name="VK",
            hh_id="15478",
            sj_id="4904563",
            description="Российская IT-компания, соцсети и интернет-сервисы (4 вакансии в кэше)",
        ),
        CompanyInfo(
            name="Социальный фонд России",
            hh_id="3127",
            sj_id="4887815",
            description="Государственное учреждение (4 вакансии в кэше)",
        ),
        # Компании только с SuperJob ID (из реального кэша, 5 шт.)
        CompanyInfo(
            name="Skyeng",
            hh_id=None,
            sj_id="4922082",
            description="Онлайн-школа английского языка (ID из реального кэша SuperJob)",
        ),
        CompanyInfo(
            name="OZON: Старт карьеры",
            hh_id=None,
            sj_id="4905942",
            description="Маркетплейс и интернет-торговля (ID из реального кэша SuperJob)",
        ),
        CompanyInfo(
            name="Кредит Европа Банк",
            hh_id=None,
            sj_id="20194",
            description="Коммерческий банк (ID из реального кэша SuperJob)",
        ),
        CompanyInfo(
            name="Федеральное бюджетное учреждение, ВВУЗ",
            hh_id=None,
            sj_id="2339875",
            description="Государственное образовательное учреждение (1 вакансия в кэше)",
        ),
        CompanyInfo(
            name="Азот-Взрыв",
            hh_id=None,
            sj_id="4440050",
            description="Промышленная компания (ID из реального кэша SuperJob)",
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