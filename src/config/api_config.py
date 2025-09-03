from typing import Any, Dict, Optional

from src.config.hh_api_config import HHAPIConfig
from src.config.sj_api_config import SJAPIConfig


class APIConfig:
    """
    Основная конфигурация API

    Центральная точка конфигурации для всех API-модулей.
    Содержит общие настройки подключения, таймауты и лимиты.
    """

    def __init__(
        self,
        user_agent: str = "MyVacancyApp/1.0",
        timeout: int = 15,
        request_delay: float = 0.5,
        hh_config: Optional[HHAPIConfig] = None,
        max_pages: int = 20,
    ):
        """
        Инициализация конфигурации API

        Args:
            user_agent: User-Agent для HTTP запросов
            timeout: Таймаут запросов в секундах
            request_delay: Задержка между запросами в секундах
            hh_config: Специфичная конфигурация для HH API
            max_pages: Максимальное количество страниц для обработки
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.request_delay = request_delay
        self.hh_config = hh_config or HHAPIConfig()
        self.sj_config = SJAPIConfig()
        self.max_pages = max_pages

    def get_pagination_params(self, **kwargs) -> Dict[str, Any]:
        """
        Получение параметров пагинации

        Args:
            **kwargs: Параметры для переопределения значений по умолчанию

        Returns:
            Dict[str, Any]: Словарь параметров пагинации
        """
        return {"max_pages": kwargs.get("max_pages", self.max_pages)}
