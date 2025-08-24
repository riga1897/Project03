
"""
Конфигурация целевых компаний для получения вакансий.

Содержит список из 15 интересных IT-компаний России,
от которых будут получаться данные о вакансиях через API HH.ru.
"""

from typing import List, Dict

# Список из 15 целевых компаний с их ID на HH.ru
TARGET_COMPANIES: List[Dict[str, str]] = [
    {
        "name": "Яндекс",
        "hh_id": "1740",
        "description": "Российская IT-компания, разработчик поисковой системы"
    },
    {
        "name": "Тинькофф",
        "hh_id": "78638",
        "description": "Частный российский банк и экосистема финансовых сервисов"
    },
    {
        "name": "СБЕР",
        "hh_id": "3529",
        "description": "Крупнейший банк России и финтех-экосистема"
    },
    {
        "name": "Wildberries",
        "hh_id": "64174",
        "description": "Крупнейший российский интернет-ритейлер"
    },
    {
        "name": "OZON",
        "hh_id": "2180",
        "description": "Российская e-commerce площадка и экосистема сервисов"
    },
    {
        "name": "VK (ВКонтакте)",
        "hh_id": "15478",
        "description": "Российская IT-компания, социальные сети и интернет-сервисы"
    },
    {
        "name": "Kaspersky",
        "hh_id": "1057",
        "description": "Российская компания по разработке систем защиты информации"
    },
    {
        "name": "Авито",
        "hh_id": "84585",
        "description": "Российский сервис объявлений и маркетплейс"
    },
    {
        "name": "X5 Retail Group",
        "hh_id": "4934",
        "description": "Российская продуктовая розничная сеть"
    },
    {
        "name": "Ростелеком",
        "hh_id": "2748",
        "description": "Крупнейший российский провайдер телекоммуникационных услуг"
    },
    {
        "name": "Альфа-Банк",
        "hh_id": "80",
        "description": "Частный российский банк"
    },
    {
        "name": "JetBrains",
        "hh_id": "1122",
        "description": "Чешская компания по разработке ПО с российскими корнями"
    },
    {
        "name": "2GIS",
        "hh_id": "64356",
        "description": "Российская IT-компания, справочно-навигационные сервисы"
    },
    {
        "name": "Skyeng",
        "hh_id": "1201321",
        "description": "Российская EdTech-компания, онлайн-образование"
    },
    {
        "name": "Delivery Club",
        "hh_id": "633442",
        "description": "Российский сервис доставки еды"
    }
]

def get_target_company_ids() -> List[str]:
    """
    Возвращает список ID целевых компаний для API запросов.
    
    Returns:
        List[str]: Список ID компаний на HH.ru
    """
    return [company["hh_id"] for company in TARGET_COMPANIES]

def get_target_company_names() -> List[str]:
    """
    Возвращает список названий целевых компаний.
    
    Returns:
        List[str]: Список названий компаний
    """
    return [company["name"] for company in TARGET_COMPANIES]

def get_company_by_id(hh_id: str) -> Dict[str, str]:
    """
    Возвращает информацию о компании по её ID на HH.ru.
    
    Args:
        hh_id: ID компании на HH.ru
        
    Returns:
        Dict[str, str]: Информация о компании или пустой словарь
    """
    for company in TARGET_COMPANIES:
        if company["hh_id"] == hh_id:
            return company
    return {}

def get_company_by_name(name: str) -> Dict[str, str]:
    """
    Возвращает информацию о компании по её названию.
    
    Args:
        name: Название компании
        
    Returns:
        Dict[str, str]: Информация о компании или пустой словарь
    """
    for company in TARGET_COMPANIES:
        if company["name"].lower() == name.lower():
            return company
    return {}
"""
Конфигурация целевых компаний для поиска вакансий

Содержит список из 12-15 интересных компаний, от которых будут получены 
данные о вакансиях через API HH.ru согласно требованиям проекта.
"""

from typing import Dict, List


class TargetCompanies:
    """
    Класс для управления списком целевых компаний
    
    Содержит ID компаний на HH.ru и их названия для поиска вакансий.
    Список включает технологические компании, банки, интернет-компании и другие.
    """
    
    # Словарь с ID компаний на HH.ru и их названиями
    COMPANIES: Dict[str, str] = {
        "1740": "Яндекс",
        "15478": "VK (ВКонтакте)",
        "78638": "Тинькофф",
        "3529": "Сбербанк",
        "80": "Альфа-Банк", 
        "2748": "Росбанк",
        "1455": "HeadHunter",
        "893": "Авито",
        "4934": "Озон",
        "561508": "Wildberries",
        "2180": "Лаборатория Касперского",
        "64174": "2ГИС",
        "3776": "MTS (МТС)",
        "4181": "Ростелеком",
        "9498": "JetBrains"
    }
    
    @classmethod
    def get_company_ids(cls) -> List[str]:
        """
        Возвращает список ID компаний
        
        Returns:
            List[str]: Список ID компаний на HH.ru
        """
        return list(cls.COMPANIES.keys())
    
    @classmethod
    def get_company_names(cls) -> List[str]:
        """
        Возвращает список названий компаний
        
        Returns:
            List[str]: Список названий компаний
        """
        return list(cls.COMPANIES.values())
    
    @classmethod
    def get_company_name_by_id(cls, company_id: str) -> str:
        """
        Возвращает название компании по ID
        
        Args:
            company_id: ID компании на HH.ru
            
        Returns:
            str: Название компании или "Неизвестная компания"
        """
        return cls.COMPANIES.get(company_id, "Неизвестная компания")
    
    @classmethod
    def get_companies_dict(cls) -> Dict[str, str]:
        """
        Возвращает полный словарь компаний
        
        Returns:
            Dict[str, str]: Словарь {id: название}
        """
        return cls.COMPANIES.copy()
    
    @classmethod
    def is_target_company(cls, company_id: str) -> bool:
        """
        Проверяет, является ли компания целевой
        
        Args:
            company_id: ID компании на HH.ru
            
        Returns:
            bool: True если компания в списке целевых
        """
        return company_id in cls.COMPANIES
    
    @classmethod
    def get_companies_info(cls) -> str:
        """
        Возвращает информацию о целевых компаниях в виде строки
        
        Returns:
            str: Форматированная строка с информацией о компаниях
        """
        info_lines = [
            "Целевые компании для поиска вакансий:",
            "=" * 40
        ]
        
        for i, (company_id, company_name) in enumerate(cls.COMPANIES.items(), 1):
            info_lines.append(f"{i:2d}. {company_name} (ID: {company_id})")
        
        info_lines.extend([
            "=" * 40,
            f"Всего компаний: {len(cls.COMPANIES)}"
        ])
        
        return "\n".join(info_lines)


# Константы для быстрого доступа
TARGET_COMPANY_IDS = TargetCompanies.get_company_ids()
TARGET_COMPANY_NAMES = TargetCompanies.get_company_names()
