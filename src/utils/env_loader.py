import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class EnvLoader:
    """Класс для загрузки переменных окружения из .env файла"""

    _loaded = False

    @classmethod
    def load_env_file(cls, env_file_path: str = ".env") -> None:
        """
        Загружает переменные окружения из .env файла

        Args:
            env_file_path: Путь к .env файлу
        """
        if cls._loaded:
            return

        # Ищем .env файл в нескольких местах
        possible_paths = [
            env_file_path,  # Относительный путь
            os.path.abspath(env_file_path),  # Абсолютный путь
            os.path.join(os.getcwd(), env_file_path),  # В текущей рабочей директории
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", env_file_path),  # В корне проекта
        ]

        env_file_found = None
        for path in possible_paths:
            if os.path.exists(path):
                env_file_found = path
                break

        if not env_file_found:
            logger.warning(f"Файл .env не найден в следующих местах: {possible_paths}")
            logger.warning("Используются переменные окружения системы.")
            cls._loaded = True
            return

        env_file_path = env_file_found

        try:
            with open(env_file_path, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()

                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith("#"):
                        continue

                    # Парсим строку формата KEY=VALUE
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Убираем кавычки если они есть
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        # Устанавливаем переменную окружения только если она еще не задана
                        if key not in os.environ:
                            os.environ[key] = value
                            logger.debug(f"Загружена переменная окружения: {key}")
                    else:
                        logger.warning(f"Неверный формат строки {line_num} в {env_file_path}: {line}")

            logger.info(f"Переменные окружения загружены из {env_file_path}")
            cls._loaded = True

        except Exception as e:
            logger.error(f"Ошибка при загрузке {env_file_path}: {e}")
            cls._loaded = True

    @staticmethod
    def get_env_var(key: str, default: Optional[str] = "") -> Optional[str]:
        """
        Получает переменную окружения с возможностью указать значение по умолчанию

        Args:
            key: Название переменной
            default: Значение по умолчанию

        Returns:
            Значение переменной или значение по умолчанию
        """
        return os.getenv(key, default)

    @staticmethod
    def get_env_var_int(key: str, default: int = 0) -> int:
        """
        Получает переменную окружения как целое число

        Args:
            key: Название переменной
            default: Значение по умолчанию

        Returns:
            Значение переменной как int или значение по умолчанию
        """
        try:
            value = os.getenv(key)
            if value is not None:
                return int(value)
            return default
        except ValueError:
            logger.warning(f"Не удалось преобразовать {key} в int, используется значение по умолчанию: {default}")
            return default


# Автоматическая загрузка .env при импорте модуля
EnvLoader.load_env_file()
