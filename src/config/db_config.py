from typing import Dict, Optional, Union

from src.utils.env_loader import EnvLoader


class DatabaseConfig:
    """Конфигурация подключения к базе данных"""

    def __init__(self) -> None:
        """Инициализация конфигурации базы данных.

        Загружает конфигурацию подключения к БД из переменных окружения
        или устанавливает значения по умолчанию.
        """
        self.default_config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Union[str, None]]:
        """Получает конфигурацию по умолчанию из переменных окружения"""
        # EnvLoader автоматически загружает переменные из .env при импорте

        # Проверяем, есть ли DATABASE_URL (имеет приоритет над отдельными параметрами)
        database_url = EnvLoader.get_env_var("DATABASE_URL")

        if database_url:
            # Парсим DATABASE_URL формата: postgresql://username:password@hostname:port/database
            return self._parse_database_url(database_url)

        # Используем отдельные переменные окружения
        return {
            "host": EnvLoader.get_env_var("PGHOST", "localhost"),
            "port": EnvLoader.get_env_var("PGPORT", "5432"),
            "database": EnvLoader.get_env_var("PGDATABASE", "job_search_app"),
            "username": EnvLoader.get_env_var("PGUSER", "postgres"),
            "password": EnvLoader.get_env_var("PGPASSWORD", ""),
            "connect_timeout": EnvLoader.get_env_var("PGCONNECT_TIMEOUT", "10"),
            "command_timeout": EnvLoader.get_env_var("PGCOMMAND_TIMEOUT", "30"),
        }

    def get_config(self, custom_config: Optional[Dict[str, str]] = None) -> Dict[str, Union[str, None]]:
        """
        Возвращает конфигурацию БД

        Args:
            custom_config: Пользовательская конфигурация (опционально)

        Returns:
            Dict[str, str]: Конфигурация подключения к БД
        """
        if custom_config:
            config = self.default_config.copy()
            config.update(custom_config)
            return config
        return self.default_config

    def get_connection_params(self) -> Dict[str, str]:
        """
        Возвращает параметры подключения в формате для psycopg2

        Returns:
            Dict[str, str]: Параметры подключения
        """
        params = {
            "host": self.default_config["host"] or "localhost",
            "port": self.default_config["port"] or "5432",
            "database": self.default_config["database"] or "job_search_app",
            "user": self.default_config["username"] or "postgres",
            "password": self.default_config["password"] or "",
        }

        # Добавляем SSL параметры если они есть в конфигурации
        if "sslmode" in self.default_config and self.default_config["sslmode"]:
            params["sslmode"] = self.default_config["sslmode"]

        return params

    def _parse_database_url(self, database_url: str) -> Dict[str, str]:
        """
        Парсит DATABASE_URL в формате postgresql://username:password@hostname:port/database

        Args:
            database_url: URL подключения к базе данных

        Returns:
            Dict[str, str]: Распарсенная конфигурация
        """
        try:
            # Убираем префикс схемы
            if database_url.startswith("postgresql://"):
                url = database_url[13:]  # убираем "postgresql://"
            elif database_url.startswith("postgres://"):
                url = database_url[11:]  # убираем "postgres://"
            else:
                raise ValueError("Неподдерживаемая схема URL базы данных")

            # Парсим username:password@host:port/database
            if "@" in url:
                auth_part, host_part = url.split("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                else:
                    username, password = auth_part, ""
            else:
                username, password = "", ""
                host_part = url

            if "/" in host_part:
                host_port_part, database_part = host_part.split("/", 1)
            else:
                host_port_part, database_part = host_part, ""

            if ":" in host_port_part:
                host, port = host_port_part.split(":", 1)
            else:
                host, port = host_port_part, "5432"

            # Разделяем название базы данных и параметры
            if "?" in database_part:
                database, params = database_part.split("?", 1)
            else:
                database, params = database_part, ""

            config = {
                "host": host,
                "port": port,
                "database": database,
                "username": username,
                "password": password,
                "connect_timeout": EnvLoader.get_env_var("PGCONNECT_TIMEOUT", "10"),
                "command_timeout": EnvLoader.get_env_var("PGCOMMAND_TIMEOUT", "30"),
            }

            # Добавляем SSL параметры если они есть
            if "sslmode" in params:
                config["sslmode"] = "require"

            return config

        except Exception as e:
            # Если парсинг не удался, используем значения по умолчанию
            print(f"Ошибка парсинга DATABASE_URL: {e}. Используются значения по умолчанию.")
            return {
                "host": "localhost",
                "port": "5432",
                "database": "job_search_app",
                "username": "postgres",
                "password": "",
                "connect_timeout": "10",
                "command_timeout": "30",
            }

    def test_connection(self, config: Optional[Dict[str, str]] = None) -> bool:
        """
        Тестирует подключение к БД

        Args:
            config: Конфигурация для тестирования (опционально)

        Returns:
            bool: True если подключение успешно
        """
        test_config = config or self.default_config

        try:
            import psycopg2

            connection = psycopg2.connect(
                host=test_config["host"],
                port=test_config["port"],
                database=test_config["database"],
                user=test_config["username"],
                password=test_config["password"],
            )
            connection.close()
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
