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

# Константы для быстрого доступа  
TARGET_COMPANY_IDS = get_target_company_ids()
TARGET_COMPANY_NAMES = get_target_company_names()