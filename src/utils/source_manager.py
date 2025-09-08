"""
Модуль для управления источниками данных о вакансиях
"""

from typing import Any, Dict, List, Optional

from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig


class SourceManager:
    """Менеджер для управления источниками данных"""

    def __init__(self) -> None:
        """Инициализация менеджера источников с конфигурациями API."""
        self._sources_config = {
            "hh.ru": {
                "name": "HeadHunter",
                "display_name": "HeadHunter",
                "priority": 1,
                "api_limits": {"requests_per_second": 5, "max_pages": 20, "max_per_page": 100},
                "features": ["free_access", "large_database", "detailed_info"],
                "config_class": HHAPIConfig,
            },
            "superjob.ru": {
                "name": "SuperJob",
                "display_name": "SuperJob",
                "priority": 2,
                "api_limits": {"requests_per_second": 3, "max_pages": 50, "max_per_page": 100},
                "features": ["api_key_required", "salary_details", "contact_info"],
                "config_class": SJAPIConfig,
            },
        }

    def get_available_sources(self) -> List[str]:
        """
        Получить список доступных источников

        Returns:
            Список идентификаторов источников
        """
        return list(self._sources_config.keys())

    def get_source_config(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Получить конфигурацию источника

        Args:
            source: Идентификатор источника

        Returns:
            Словарь с конфигурацией или None
        """
        return self._sources_config.get(source)

    def is_source_available(self, source: str) -> bool:
        """
        Проверить доступность источника

        Args:
            source: Идентификатор источника

        Returns:
            True если источник доступен
        """
        return source in self._sources_config

    def get_source_display_name(self, source: str) -> str:
        """
        Получить отображаемое название источника

        Args:
            source: Идентификатор источника

        Returns:
            Отображаемое название
        """
        config = self.get_source_config(source)
        if config:
            return config.get("display_name", source)
        return source

    def get_source_api_limits(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Получить лимиты API для источника

        Args:
            source: Идентификатор источника

        Returns:
            Словарь с лимитами API
        """
        config = self.get_source_config(source)
        if config:
            return config.get("api_limits")
        return None

    def validate_source_credentials(self, source: str, credentials: Dict[str, Any]) -> bool:
        """
        Валидация учетных данных для источника

        Args:
            source: Идентификатор источника
            credentials: Словарь с учетными данными

        Returns:
            True если учетные данные валидны
        """
        if source == "hh.ru":
            # HH.ru не требует API ключа
            return True
        elif source == "superjob.ru":
            # SuperJob требует API ключ
            api_key = credentials.get("api_key")
            if not api_key:
                # Проверяем в переменных окружения
                config = SJAPIConfig()
                return config.is_configured()
            return bool(api_key)
        return False

    def get_source_priority(self, source: str) -> int:
        """
        Получить приоритет источника

        Args:
            source: Идентификатор источника

        Returns:
            Приоритет (меньше = выше приоритет)
        """
        config = self.get_source_config(source)
        if config:
            return config.get("priority", 999)
        return 999

    def sort_sources_by_priority(self, sources: List[str]) -> List[str]:
        """
        Сортировка источников по приоритету

        Args:
            sources: Список идентификаторов источников

        Returns:
            Отсортированный список источников
        """
        return sorted(sources, key=self.get_source_priority)

    def get_source_features(self, source: str) -> List[str]:
        """
        Получить список функций источника

        Args:
            source: Идентификатор источника

        Returns:
            Список функций
        """
        config = self.get_source_config(source)
        if config:
            return config.get("features", [])
        return []

    def get_source_config_class(self, source: str) -> Optional[type]:
        """
        Получить класс конфигурации для источника

        Args:
            source: Идентификатор источника

        Returns:
            Класс конфигурации
        """
        config = self.get_source_config(source)
        if config:
            return config.get("config_class")
        return None

    def create_source_instance(self, source: str) -> Optional[Any]:
        """
        Создать экземпляр API для источника

        Args:
            source: Идентификатор источника

        Returns:
            Экземпляр API класса
        """
        config_class = self.get_source_config_class(source)
        if config_class:
            return config_class()
        return None


class DataSource:
    """Класс для представления источника данных"""

    def __init__(self, key: str, name: str, display_name: str):
        """Инициализация источника данных с основными параметрами."""
        self.key = key
        self.name = name
        self.display_name = display_name


# Глобальный экземпляр менеджера источников
source_manager = SourceManager()
