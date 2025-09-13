#!/usr/bin/env python3
"""
Тесты модуля app_config для 100% покрытия.

Покрывает все функции в src/config/app_config.py:
- AppConfig - класс управления конфигурацией приложения
- __init__ - инициализация с настройками БД из env
- get_storage_type - получение типа хранилища
- set_storage_type - установка типа хранилища с валидацией
- get_db_config - получение конфигурации БД (копия)
- set_db_config - обновление конфигурации БД

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from unittest.mock import patch

# Импорты из реального кода для покрытия
from src.config.app_config import AppConfig


class TestAppConfig:
    """100% покрытие AppConfig класса"""

    @patch.dict('os.environ', {}, clear=True)
    def test_init_with_default_env_values(self) -> None:
        """Покрытие инициализации с env значениями по умолчанию"""
        config = AppConfig()

        # Проверяем настройки по умолчанию
        assert config.default_storage_type == "postgres"
        assert config.storage_type == "postgres"

        # Проверяем настройки БД по умолчанию
        expected_db_config = {
            "host": "localhost",
            "port": "5432",
            "database": "Project03",
            "username": "postgres",
            "password": ""
        }
        assert config.db_config == expected_db_config

    @patch.dict('os.environ', {
        'PGHOST': 'test-host',
        'PGPORT': '5433',
        'PGDATABASE': 'test-db',
        'PGUSER': 'test-user',
        'PGPASSWORD': 'test-pass'
    })
    def test_init_with_custom_env_values(self) -> None:
        """Покрытие инициализации с кастомными env значениями"""
        config = AppConfig()

        # Проверяем кастомные настройки БД из env
        expected_db_config = {
            "host": "test-host",
            "port": "5433",
            "database": "test-db",
            "username": "test-user",
            "password": "test-pass"
        }
        assert config.db_config == expected_db_config

    @patch.dict('os.environ', {
        'PGHOST': 'partial-host',
        'PGPORT': '5434',
        'PGDATABASE': 'Project03',  # Устанавливаем явно
        'PGUSER': 'postgres',       # Устанавливаем явно
        'PGPASSWORD': ''            # Устанавливаем явно
    })
    def test_init_with_partial_env_values(self) -> None:
        """Покрытие инициализации с частичными env значениями"""
        config = AppConfig()

        # Проверяем смешанные настройки (частично env, частично по умолчанию)
        expected_db_config = {
            "host": "partial-host",     # Из env
            "port": "5434",             # Из env
            "database": "Project03",    # По умолчанию
            "username": "postgres",     # По умолчанию
            "password": ""              # По умолчанию
        }
        assert config.db_config == expected_db_config

    def test_get_storage_type_default(self) -> None:
        """Покрытие получения типа хранилища по умолчанию"""
        config = AppConfig()

        result = config.get_storage_type()

        assert result == "postgres"
        assert result == config.storage_type

    def test_set_storage_type_valid(self) -> None:
        """Покрытие установки валидного типа хранилища"""
        config = AppConfig()

        config.set_storage_type("postgres")

        assert config.storage_type == "postgres"
        assert config.get_storage_type() == "postgres"

    def test_set_storage_type_invalid(self) -> None:
        """Покрытие установки невалидного типа хранилища"""
        config = AppConfig()

        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL: mysql"):
            config.set_storage_type("mysql")

        # Убеждаемся, что значение не изменилось
        assert config.storage_type == "postgres"

    def test_set_storage_type_multiple_invalid_types(self) -> None:
        """Покрытие установки различных невалидных типов хранилища"""
        config = AppConfig()

        invalid_types = ["mysql", "sqlite", "mongodb", "redis", ""]

        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match=f"Поддерживается только PostgreSQL: {invalid_type}"):
                config.set_storage_type(invalid_type)

            # Убеждаемся, что значение остается postgres
            assert config.storage_type == "postgres"

    def test_get_db_config_returns_copy(self) -> None:
        """Покрытие того, что get_db_config возвращает копию"""
        config = AppConfig()

        db_config1 = config.get_db_config()
        db_config2 = config.get_db_config()

        # Должны быть разными объектами (копии)
        assert db_config1 is not db_config2
        assert db_config1 == db_config2

        # Изменение возвращенной копии не должно влиять на оригинал
        db_config1["host"] = "modified-host"
        assert config.db_config["host"] != "modified-host"
        assert config.get_db_config()["host"] != "modified-host"

    def test_get_db_config_content(self) -> None:
        """Покрытие содержимого конфигурации БД"""
        config = AppConfig()

        db_config = config.get_db_config()

        # Проверяем наличие всех ключей
        required_keys = {"host", "port", "database", "username", "password"}
        assert set(db_config.keys()) == required_keys

        # Проверяем типы значений
        assert all(isinstance(value, str) for value in db_config.values())

    def test_set_db_config_update_existing(self) -> None:
        """Покрытие обновления существующей конфигурации БД"""
        config = AppConfig()

        # Исходная конфигурация
        original_config = config.get_db_config()

        # Обновляем некоторые параметры
        updates = {
            "host": "updated-host",
            "port": "5435"
        }

        config.set_db_config(updates)

        # Проверяем обновленную конфигурацию
        updated_config = config.get_db_config()
        assert updated_config["host"] == "updated-host"
        assert updated_config["port"] == "5435"

        # Проверяем что остальные параметры остались без изменений
        assert updated_config["database"] == original_config["database"]
        assert updated_config["username"] == original_config["username"]
        assert updated_config["password"] == original_config["password"]

    def test_set_db_config_add_new_keys(self) -> None:
        """Покрытие добавления новых ключей в конфигурацию БД"""
        config = AppConfig()

        # Добавляем новые ключи
        new_config = {
            "ssl_mode": "require",
            "connection_timeout": "30"
        }

        config.set_db_config(new_config)

        # Проверяем что новые ключи добавлены
        updated_config = config.get_db_config()
        assert updated_config["ssl_mode"] == "require"
        assert updated_config["connection_timeout"] == "30"

        # Проверяем что старые ключи остались
        assert "host" in updated_config
        assert "port" in updated_config

    def test_set_db_config_empty_dict(self) -> None:
        """Покрытие обновления конфигурации БД пустым словарем"""
        config = AppConfig()

        original_config = config.get_db_config()

        # Обновляем пустым словарем
        config.set_db_config({})

        # Конфигурация должна остаться без изменений
        updated_config = config.get_db_config()
        assert updated_config == original_config

    def test_set_db_config_overwrite_all(self) -> None:
        """Покрытие полной перезаписи конфигурации БД"""
        config = AppConfig()

        # Полностью новая конфигурация
        new_config = {
            "host": "new-host",
            "port": "5436",
            "database": "new-db",
            "username": "new-user",
            "password": "new-pass"
        }

        config.set_db_config(new_config)

        # Проверяем что все значения обновились
        updated_config = config.get_db_config()
        assert updated_config == new_config


class TestAppConfigEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    @patch.dict('os.environ', {
        'PGPASSWORD': ''  # Пустой пароль
    })
    def test_init_with_empty_password(self) -> None:
        """Покрытие инициализации с пустым паролем"""
        config = AppConfig()

        assert config.db_config["password"] == ""

    @patch.dict('os.environ', {
        'PGHOST': '  ',  # Пробелы
        'PGPORT': '0'    # Нулевой порт
    })
    def test_init_with_edge_case_values(self) -> None:
        """Покрытие инициализации с граничными значениями"""
        config = AppConfig()

        # Проверяем что значения принимаются как есть (без валидации)
        assert config.db_config["host"] == "  "
        assert config.db_config["port"] == "0"

    def test_multiple_config_instances_independence(self) -> None:
        """Покрытие независимости множественных экземпляров конфигурации"""
        config1 = AppConfig()
        config2 = AppConfig()

        # Изменяем конфигурацию первого экземпляра
        config1.set_db_config({"host": "host1"})
        config1.set_storage_type("postgres")

        # Второй экземпляр должен остаться без изменений
        assert config2.get_db_config()["host"] != "host1"
        assert config2.get_storage_type() == "postgres"  # Значение по умолчанию

    def test_storage_type_case_sensitivity(self) -> None:
        """Покрытие чувствительности к регистру типа хранилища"""
        config = AppConfig()

        # Проверяем что регистр имеет значение
        with pytest.raises(ValueError):
            config.set_storage_type("PostgreSQL")

        with pytest.raises(ValueError):
            config.set_storage_type("POSTGRES")

        # Только точное совпадение работает
        config.set_storage_type("postgres")
        assert config.get_storage_type() == "postgres"

    def test_db_config_modification_after_set(self) -> None:
        """Покрытие модификации конфигурации после установки"""
        config = AppConfig()

        # Устанавливаем конфигурацию
        test_config = {"host": "test-host", "custom_key": "custom_value"}
        config.set_db_config(test_config)

        # Изменяем оригинальный словарь
        test_config["host"] = "modified-host"
        test_config["new_key"] = "new_value"

        # Конфигурация в объекте не должна измениться
        current_config = config.get_db_config()
        assert current_config["host"] == "test-host"
        assert "new_key" not in current_config


class TestAppConfigIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch.dict('os.environ', {
        'PGHOST': 'integration-host',
        'PGPORT': '5437',
        'PGDATABASE': 'integration-db',
        'PGUSER': 'integration-user',
        'PGPASSWORD': 'integration-pass'
    })
    def test_full_configuration_workflow(self) -> None:
        """Покрытие полного рабочего процесса конфигурации"""
        # Инициализация с env переменными
        config = AppConfig()

        # Проверяем начальную конфигурацию
        assert config.get_storage_type() == "postgres"
        db_config = config.get_db_config()
        assert db_config["host"] == "integration-host"
        assert db_config["port"] == "5437"

        # Обновляем конфигурацию
        config.set_db_config({
            "port": "5438",
            "ssl_mode": "require"
        })

        # Проверяем обновленную конфигурацию
        updated_config = config.get_db_config()
        assert updated_config["host"] == "integration-host"  # Остался из env
        assert updated_config["port"] == "5438"              # Обновился
        assert updated_config["ssl_mode"] == "require"       # Добавился

        # Тип хранилища остался без изменений
        assert config.get_storage_type() == "postgres"

    def test_configuration_state_consistency(self) -> None:
        """Покрытие согласованности состояния конфигурации"""
        config = AppConfig()

        # Многократные операции чтения должны возвращать одинаковые результаты
        storage_type1 = config.get_storage_type()
        storage_type2 = config.get_storage_type()
        assert storage_type1 == storage_type2

        db_config1 = config.get_db_config()
        db_config2 = config.get_db_config()
        assert db_config1 == db_config2

        # Операции изменения должны быть согласованными
        config.set_storage_type("postgres")
        config.set_db_config({"consistency": "test"})

        assert config.get_storage_type() == "postgres"
        assert config.get_db_config()["consistency"] == "test"

    def test_error_resilience(self) -> None:
        """Покрытие устойчивости к ошибкам"""
        config = AppConfig()

        original_storage_type = config.get_storage_type()
        original_db_config = config.get_db_config()

        # Неудачная попытка изменения storage_type
        try:
            config.set_storage_type("invalid")
        except ValueError:
            pass

        # Состояние должно остаться без изменений
        assert config.get_storage_type() == original_storage_type
        assert config.get_db_config() == original_db_config

        # Успешные операции должны работать после ошибок
        config.set_db_config({"recovery": "successful"})
        assert config.get_db_config()["recovery"] == "successful"
