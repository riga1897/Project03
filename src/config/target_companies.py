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

    # Список целевых компаний - 12 ведущих IT-компаний России
    COMPANIES = [
        CompanyInfo(
            name="Яндекс",
            hh_id="1740",
            sj_id="19421",
            description="Российская IT-компания, разработчик поисковой системы",
        ),
        CompanyInfo(
            name="Тинькофф",
            hh_id="78638",
            sj_id="2324",
            description="Частный российский банк и экосистема финансовых сервисов",
        ),
        CompanyInfo(
            name="СБЕР",
            hh_id="3529",
            sj_id="16134",
            description="Крупнейший банк России и финтех-экосистема",
        ),
        CompanyInfo(
            name="Wildberries",
            hh_id="64174",
            sj_id="49357",
            description="Крупнейший российский интернет-ритейлер",
        ),
        CompanyInfo(
            name="OZON",
            hh_id="2180",
            sj_id="38292",
            description="Российская e-commerce площадка и экосистема сервисов",
        ),
        CompanyInfo(
            name="VK",
            hh_id="15478",
            sj_id="15618",
            description="Российская IT-компания, социальные сети и интернет-сервисы",
        ),
        CompanyInfo(
            name="Лаборатория Касперского",
            hh_id="1057",
            sj_id="1165",
            description="Российская компания по разработке систем защиты информации",
        ),
        CompanyInfo(
            name="Авито",
            hh_id="84585",
            sj_id="12258",
            description="Российский сервис объявлений и маркетплейс",
        ),
        CompanyInfo(
            name="X5 Retail Group",
            hh_id="4934",
            sj_id="2664",
            description="Российская продуктовая розничная сеть",
        ),
        CompanyInfo(
            name="Ростелеком",
            hh_id="2748",
            sj_id="1145",
            description="Крупнейший российский провайдер телекоммуникационных услуг",
        ),
        CompanyInfo(
            name="Альфа-Банк",
            hh_id="80",
            sj_id="1390",
            description="Частный российский банк",
        ),
        CompanyInfo(
            name="JetBrains",
            hh_id="1122",
            sj_id="1237",
            description="Чешская компания по разработке ПО с российскими корнями",
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
