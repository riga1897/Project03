import hashlib
import json
import logging
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .env_loader import EnvLoader
from .file_handlers import json_handler
from .decorators import simple_cache


# Configure logger
logger = logging.getLogger(__name__)


class FileCache:
    """Класс для файлового кэширования API-ответов"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self._ensure_dir_exists()

    def _ensure_dir_exists(self) -> None:
        """Создает все необходимые директории"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_params_hash(params: Dict[str, Any]) -> str:
        """
        Генерация хеша параметров
        :param params: Словарь параметров запроса
        :return: Строка с hex-представлением MD5 хеша
        """
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()

    def save_response(self, prefix: str, params: Dict, data: Dict) -> None:
        """
        Сохранение ответа API в кэш

        Args:
            prefix: Префикс для имени файла (hh, sj и т.д.)
            params: Параметры запроса (для создания уникального ключа)
            data: Данные ответа API
        """
        try:
            # Не сохраняем пустые страницы или некорректные данные
            if not self._is_valid_response(data, params):
                logger.debug(f"Пропускаем сохранение некорректного ответа в кэш: {params}")
                return

            cache_key = self._generate_params_hash(params) # Renamed from _generate_cache_key to _generate_params_hash
            file_path = self.cache_dir / f"{prefix}_{cache_key}.json" # Added prefix to filename

            cache_data = {
                "timestamp": time.time(),
                "meta": {
                    "params": params
                },
                "data": data
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Ответ сохранен в кэш: {file_path}")

        except Exception as e:
            logger.error(f"Ошибка сохранения в кэш: {e}")

    def _is_valid_response(self, data: Dict, params: Dict) -> bool:
        """
        Проверка валидности ответа перед сохранением в кэш

        Args:
            data: Данные ответа API
            params: Параметры запроса

        Returns:
            bool: True если ответ валиден для кэширования
        """
        try:
            # Базовая проверка структуры
            if not isinstance(data, dict):
                return False

            # Для HH/SJ API проверяем специфичную логику
            items = data.get("items", [])
            found = data.get("found", 0)
            page = params.get("page", 0)
            pages = data.get("pages", 1)

            # Не сохраняем пустые страницы, если запрашиваем страницу больше доступных
            if page > 0 and not items and page >= pages:
                logger.debug(f"Пропускаем пустую страницу {page} из {pages}")
                return False

            # Не сохраняем страницы без найденных результатов (кроме первой)
            if found == 0 and page > 0:
                logger.debug(f"Пропускаем страницу {page} - нет результатов")
                return False

            return True

        except Exception as e:
            logger.warning(f"Ошибка валидации ответа: {e}")
            return False

    def load_response(self, source: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Загрузка кэшированного ответа"""
        try:
            params_hash = self._generate_params_hash(params)
            filename = f"{source}_{params_hash}.json"
            filepath = self.cache_dir / filename

            if not filepath.exists():
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, Exception):
            # При ошибке декодирования или доступа к файлу, считаем кэш невалидным
            if filepath.exists():
                try:
                    filepath.unlink() # Удаляем некорректный файл
                except OSError as e:
                    logger.error(f"Ошибка удаления некорректного файла кэша {filepath}: {e}")
            return None

    def clear(self, source: Optional[str] = None) -> None:
        """Очистка кэша"""
        pattern = f"{source}_*.json" if source else "*.json"
        for file in self.cache_dir.glob(pattern):
            file.unlink()