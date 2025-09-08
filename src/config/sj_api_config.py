import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.env_loader import EnvLoader
from src.utils.file_handlers import json_handler

logger = logging.getLogger(__name__)


@dataclass
class SJAPIConfig:
    """Конфигурация специфичных параметров SuperJob API"""

    count: int = 500  # Максимальное количество элементов на странице (до 500 по API)
    published: int = 15  # Период публикации в днях (по умолчанию 15 дней)
    only_with_salary: bool = False  # Будет загружено из .env
    custom_params: Optional[Dict[str, Any]] = None

    # Дополнительные настройки
    per_page = 100
    max_total_pages = 20

    # Настройка фильтрации данных через SQL
    filter_by_target_companies = True  # Фильтровать по целевым компаниям через SQL

    def __init__(self, token_file: Path = Path("token.json"), **kwargs):
        """Инициализация конфигурации SuperJob API с загрузкой настроек."""
        self.token_file = token_file
        # Инициализация APIConfig, если он нужен (в данном случае не используется напрямую в SJAPIConfig)
        # self.api_config = APIConfig()

        # Загружаем настройку фильтрации по зарплате из .env
        env_value = EnvLoader.get_env_var("FILTER_ONLY_WITH_SALARY", "false")
        self.only_with_salary = str(env_value).lower() in ("true", "1", "yes", "on")

        # Обновляем параметры из kwargs, если они переданы
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "count": kwargs.get("count", self.count),
            "order_field": kwargs.get("order_field", "date"),  # Сортировка по дате
            "order_direction": kwargs.get("order_direction", "desc"),  # Сначала новые
            "published": kwargs.get("published", self.published),  # Период публикации (15 дней по умолчанию)
            "no_agreement": (
                1 if kwargs.get("only_with_salary", self.only_with_salary) else 0
            ),  # Только с указанной зарплатой
        }

        # Обрабатываем пагинацию (SuperJob использует page, начиная с 0)
        if "page" in kwargs:
            params["page"] = kwargs["page"]

        # Город добавляем только если указан явно (по умолчанию поиск по всей России)
        if "town" in kwargs:
            params["town"] = kwargs["town"]

        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params

    def save_token(self, token: str) -> None:
        """Сохранить токен в файл"""
        try:
            token_data = [{"superjob_api_key": token}]
            json_handler.write_json(self.token_file, token_data)
            logger.info(f"Токен SuperJob сохранен в {self.token_file}")

        except Exception as e:
            logger.error(f"Ошибка сохранения токена: {e}")
            raise

    def load_token(self) -> Optional[str]:
        """Загрузить токен из файла"""
        try:
            token_data = json_handler.read_json(self.token_file)
            if token_data and len(token_data) > 0:
                return token_data[0].get("superjob_api_key")
            return None

        except Exception as e:
            logger.error(f"Ошибка загрузки токена: {e}")
            return None
