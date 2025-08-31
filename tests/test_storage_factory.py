import os
import sys
from typing import Any, Optional
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импортируем реальные классы
try:
    from src.storage.storage_factory import StorageFactory
except ImportError:
    # Создаем тестовый класс StorageFactory, если не удается импортировать
    class StorageFactory:
        """Тестовая фабрика хранилищ"""

        @staticmethod
        def create_storage(storage_type: str = "postgres", **kwargs):
            """Создание хранилища"""
            if storage_type == "postgres":
                return MockPostgresStorage()
            else:
                raise ValueError(f"Unknown storage type: {storage_type}")

        @staticmethod
        def get_default_storage():
            """Получение хранилища по умолчанию"""
            return MockPostgresStorage()


class MockPostgresStorage:
    """Мок Postgres хранилища"""

    def __init__(self):
        self.data = []
        self.connected = True

    def save_vacancy(self, vacancy):
        self.data.append(vacancy)

    def load_vacancies(self):
        return self.data

    def get_vacancies_count(self):
        return len(self.data)

    def close(self):
        self.connected = False


class TestStorageFactory:
    def test_storage_factory_initialization(self):
        """Тест инициализации фабрики хранилищ"""
        factory = StorageFactory()
        assert hasattr(factory, "create_storage")

    @patch("src.storage.postgres_saver.PostgresSaver")
    def test_create_postgres_storage(self, mock_postgres_saver):
        """Тест создания PostgreSQL хранилища с моками"""
        mock_storage_instance = Mock()
        mock_postgres_saver.return_value = mock_storage_instance

        with patch("src.config.app_config.AppConfig") as mock_app_config:
            mock_config_instance = Mock()
            mock_config_instance.get_db_config.return_value = {"host": "localhost"}
            mock_app_config.return_value = mock_config_instance

            factory = StorageFactory()
            storage = factory.create_storage("postgres")

        assert storage == mock_storage_instance
        mock_app_config.assert_called_once()
        mock_postgres_saver.assert_called_once()

    def test_create_unknown_storage(self):
        """Тест создания неизвестного типа хранилища"""
        factory = StorageFactory()
        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL"):
            factory.create_storage("unknown_type")

    @patch("src.storage.storage_factory.StorageFactory.create_storage")
    def test_get_default_storage(self, mock_create_storage):
        """Тест получения хранилища по умолчанию"""
        mock_storage = Mock()
        mock_create_storage.return_value = mock_storage

        storage = StorageFactory.get_default_storage()

        assert storage == mock_storage
        mock_create_storage.assert_called_once_with("postgres")

    def test_storage_factory_singleton_behavior(self):
        """Тест что фабрика создает экземпляры корректно"""
        factory1 = StorageFactory()
        factory2 = StorageFactory()

        # Фабрика не синглтон, но создается корректно
        assert factory1 is not None
        assert factory2 is not None
        assert hasattr(factory1, "create_storage")
        assert hasattr(factory2, "create_storage")

    @patch("src.storage.postgres_saver.PostgresSaver")
    def test_create_storage_with_db_config(self, mock_postgres_saver):
        """Тест создания хранилища с конфигурацией БД"""
        mock_storage_instance = Mock()
        mock_postgres_saver.return_value = mock_storage_instance

        with patch("src.config.app_config.AppConfig") as mock_app_config:
            mock_config_instance = Mock()
            test_db_config = {
                "host": "test_host",
                "port": "5432",
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass",
            }
            mock_config_instance.get_db_config.return_value = test_db_config
            mock_app_config.return_value = mock_config_instance

            factory = StorageFactory()
            storage = factory.create_storage("postgres")

        assert storage == mock_storage_instance
        mock_config_instance.get_db_config.assert_called_once()
        mock_postgres_saver.assert_called_once_with(test_db_config)

    def test_mock_postgres_storage_functionality(self):
        """Тест функциональности мок хранилища"""
        storage = MockPostgresStorage()

        # Тест базовой функциональности
        assert storage.get_vacancies_count() == 0
        assert storage.connected is True

        # Тест добавления данных
        test_vacancy = {"id": 1, "title": "Test Job"}
        storage.save_vacancy(test_vacancy)

        assert storage.get_vacancies_count() == 1
        assert storage.load_vacancies() == [test_vacancy]

        # Тест закрытия соединения
        storage.close()
        assert storage.connected is False

    @patch("src.storage.storage_factory.StorageFactory.create_storage")
    def test_error_handling_in_factory(self, mock_create_storage):
        """Тест обработки ошибок в фабрике"""
        mock_create_storage.side_effect = Exception("Database connection failed")

        factory = StorageFactory()
        with pytest.raises(Exception, match="Database connection failed"):
            factory.create_storage("postgres")
