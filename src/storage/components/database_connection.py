"""
Компонент для управления подключениями к базе данных.
Реализует принцип единственной ответственности (SRP).
"""

import logging
from typing import Any, Optional

from src.storage.db_connection_config import get_db_connection_params
from src.storage.db_psycopg2_compat import get_psycopg2, get_psycopg_error, get_real_dict_cursor
from src.storage.db_psycopg2_compat import is_available as psycopg2_available

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Класс для управления подключениями к PostgreSQL базе данных.

    Отвечает только за установку, закрытие и проверку состояния подключений.
    """

    def __init__(self, connection_params: Optional[dict] = None):
        """
        Инициализация подключения к базе данных

        Args:
            connection_params: Параметры подключения или None для использования переменных окружения
        """
        self._connection_params = connection_params or self._get_default_params()
        self._connection = None

    def _get_default_params(self) -> dict:
        """Получение параметров подключения из переменных окружения"""
        # Используем универсальный конфигуратор который поддерживает DATABASE_URL и другие форматы
        return get_db_connection_params()

    def get_connection(self) -> Any:
        """
        Получение подключения к базе данных

        Returns:
            Connection: Активное подключение к PostgreSQL

        Raises:
            ConnectionError: При невозможности подключиться к БД
        """
        if not self._is_connection_valid():
            self._create_new_connection()

        return self._connection

    def _is_connection_valid(self) -> bool:
        """Проверка валидности текущего подключения"""
        if self._connection is None:
            return False

        try:
            # Проверяем подключение простым запросом
            with self._connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:  # Ловим все psycopg2 ошибки
            return False

    def _create_new_connection(self) -> None:
        """Создание нового подключения к базе данных"""
        if not psycopg2_available():
            raise ConnectionError("psycopg2 не установлен или недоступен")

        try:
            psycopg2 = get_psycopg2()
            RealDictCursor = get_real_dict_cursor()
            
            # Фильтруем параметры для psycopg2 - убираем unsupported timeout параметры
            db_params = {k: v for k, v in self._connection_params.items() 
                        if k not in ('connect_timeout', 'command_timeout')}
            
            connection = psycopg2.connect(**db_params, cursor_factory=RealDictCursor)
            self._connection = connection
            if self._connection is not None:
                self._connection.autocommit = False
            logger.debug("Установлено новое подключение к базе данных")

        except get_psycopg_error() as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise ConnectionError(f"Не удалось подключиться к базе данных: {e}")

    def close_connection(self) -> None:
        """Закрытие подключения к базе данных"""
        if self._connection:
            try:
                self._connection.close()
                logger.debug("Подключение к базе данных закрыто")
            except Exception as e:
                logger.warning(f"Ошибка при закрытии подключения: {e}")
            finally:
                self._connection = None

    def __enter__(self) -> Any:
        """Контекстный менеджер - вход"""
        return self.get_connection()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Контекстный менеджер - выход"""
        self.close_connection()
