"""
Конфигурация целевых компаний для поиска вакансий.

Содержит список из 15 ведущих IT-компаний России с их идентификаторами
для различных источников данных (HH.ru, SuperJob).
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass


@dataclass
class CompanyInfo:
    """Информация о компании"""
    name: str
    hh_id: str
    sj_id: Optional[str] = None
    description: str = ""
    aliases: List[str] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class TargetCompanies:
    """Класс для работы с целевыми компаниями"""

    # Основной список целевых компаний
    COMPANIES = [
        CompanyInfo(
            name="Яндекс",
            hh_id="1740",
            sj_id="19421",
            description="Российская IT-компания, разработчик поисковой системы",
            aliases=["Yandex", "яндекс"]
        ),
        CompanyInfo(
            name="Тинькофф",
            hh_id="78638",
            sj_id="2324",
            description="Частный российский банк и экосистема финансовых сервисов",
            aliases=["Т-Банк", "Tinkoff", "T-Bank", "TCS", "тинькофф", "т-банк"]
        ),
        CompanyInfo(
            name="СБЕР",
            hh_id="3529",
            sj_id="16134",
            description="Крупнейший банк России и финтех-экосистема",
            aliases=["Сбербанк", "Sber", "Sberbank", "сбер", "сбербанк"]
        ),
        CompanyInfo(
            name="Wildberries",
            hh_id="64174",
            sj_id="49357",
            description="Крупнейший российский интернет-ритейлер",
            aliases=["WB", "Вайлдберриз", "вайлдберриз", "wildberries"]
        ),
        CompanyInfo(
            name="OZON",
            hh_id="2180",
            sj_id="38292",
            description="Российская e-commerce площадка и экосистема сервисов",
            aliases=["Ozon", "Озон", "озон"]
        ),
        CompanyInfo(
            name="VK",
            hh_id="15478",
            sj_id="15618",
            description="Российская IT-компания, социальные сети и интернет-сервисы",
            aliases=["ВКонтакте", "ВК", "Mail.ru Group", "VK Group", "вк", "вконтакте"]
        ),
        CompanyInfo(
            name="Лаборатория Касперского",
            hh_id="1057",
            sj_id="1165",
            description="Российская компания по разработке систем защиты информации",
            aliases=["Kaspersky", "Касперский", "касперского"]
        ),
        CompanyInfo(
            name="Авито",
            hh_id="84585",
            sj_id="12258",
            description="Российский сервис объявлений и маркетплейс",
            aliases=["Avito", "авито"]
        ),
        CompanyInfo(
            name="X5 Retail Group",
            hh_id="4934",
            sj_id="2664",
            description="Российская продуктовая розничная сеть",
            aliases=["X5", "Пятёрочка", "Карусель", "Перекрёсток"]
        ),
        CompanyInfo(
            name="Ростелеком",
            hh_id="2748",
            sj_id="1145",
            description="Крупнейший российский провайдер телекоммуникационных услуг",
            aliases=["Rostelecom", "ростелеком"]
        ),
        CompanyInfo(
            name="Альфа-Банк",
            hh_id="80",
            sj_id="1390",
            description="Частный российский банк",
            aliases=["Alfa-Bank", "Alfabank", "альфа"]
        ),
        CompanyInfo(
            name="JetBrains",
            hh_id="1122",
            sj_id="1237",
            description="Чешская компания по разработке ПО с российскими корнями",
            aliases=["Джетбрейнс", "jetbrains"]
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
    def get_all_names_and_aliases(cls) -> Set[str]:
        """Возвращает множество всех названий и псевдонимов компаний (в нижнем регистре)"""
        names = set()
        for company in cls.COMPANIES:
            names.add(company.name.lower())
            names.update(alias.lower() for alias in company.aliases)
        return names

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
    def find_company_by_name(cls, name: str) -> Optional[CompanyInfo]:
        """
        Поиск компании по названию или псевдониму (регистронезависимо)

        Args:
            name: Название для поиска

        Returns:
            CompanyInfo или None если не найдено
        """
        search_name = name.lower().strip()

        for company in cls.COMPANIES:
            # Проверяем основное название
            if company.name.lower() == search_name:
                return company

            # Проверяем псевдонимы
            if search_name in (alias.lower() for alias in company.aliases):
                return company

            # Проверяем частичное вхождение
            if search_name in company.name.lower() or company.name.lower() in search_name:
                return company

            # Проверяем частичное вхождение в псевдонимах
            for alias in company.aliases:
                if search_name in alias.lower() or alias.lower() in search_name:
                    return company

        return None

    @classmethod
    def is_target_company(cls, name: str) -> bool:
        """Проверяет, является ли компания целевой"""
        return cls.find_company_by_name(name) is not None

    @classmethod
    def get_search_patterns_for_sql(cls) -> List[str]:
        """
        Возвращает список паттернов для SQL LIKE запросов

        Returns:
            Список строк для использования в SQL запросах с LIKE
        """
        patterns = []
        for company in cls.COMPANIES:
            # Основное название
            patterns.append(f"%{company.name.lower()}%")

            # Псевдонимы
            for alias in company.aliases:
                patterns.append(f"%{alias.lower()}%")

        return patterns

    @classmethod
    def get_company_count(cls) -> int:
        """Возвращает количество целевых компаний"""
        return len(cls.COMPANIES)


def get_target_company_ids() -> List[str]:
    """
    Возвращает список ID целевых компаний для HH.ru

    Returns:
        List[str]: Список ID компаний для HH.ru
    """
    return TargetCompanies.get_hh_ids()


def get_target_company_names() -> List[str]:
    """
    Возвращает список названий целевых компаний

    Returns:
        List[str]: Список названий компаний
    """
    return TargetCompanies.get_company_names()


# Для обратной совместимости - список словарей
TARGET_COMPANIES = [
    {
        "name": company.name,
        "hh_id": company.hh_id,
        "sj_id": company.sj_id,
        "description": company.description,
        "aliases": company.aliases
    }
    for company in TargetCompanies.COMPANIES
]