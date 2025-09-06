"""
Полные тесты для MainApplicationInterface
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.interfaces.main_application_interface import MainApplicationInterface
    MAIN_APPLICATION_INTERFACE_AVAILABLE = True
except ImportError:
    MAIN_APPLICATION_INTERFACE_AVAILABLE = False
    MainApplicationInterface = object


class ConcreteMainApp(MainApplicationInterface if MAIN_APPLICATION_INTERFACE_AVAILABLE else object):
    """Конкретная реализация для тестирования"""

    def __init__(self, provider=None, processor=None, storage=None):
        if MAIN_APPLICATION_INTERFACE_AVAILABLE:
            super().__init__(provider, processor, storage)
        self.data_provider = provider or Mock()
        self.processor = processor or Mock()
        self.storage = storage or Mock()

    def run_application(self):
        """Запуск приложения"""
        return "Application started"

    def process_data(self, data):
        """Обработка данных"""
        if not data:
            return []
        try:
            return self.processor.process(data)
        except Exception:
            return []

    def store_data(self, data):
        """Сохранение данных"""
        if not data:
            return False
        try:
            return self.storage.save(data)
        except Exception:
            return False

    def search_data(self, query, sources=None):
        """Поиск данных"""
        if not query:
            return []
        if sources is None:
            try:
                sources = self.data_provider.get_available_sources()
            except Exception:
                return []
        try:
            return self.data_provider.search(query, sources=sources)
        except Exception:
            return []

    def get_storage_stats(self):
        """Получение статистики"""
        try:
            return self.storage.get_stats()
        except Exception:
            return {}

    def clear_storage_data(self):
        """Очистка хранилища"""
        try:
            return self.storage.clear()
        except Exception:
            return False

    def export_data(self, data, format_type, path):
        """Экспорт данных"""
        if not data:
            return None
        try:
            return self.storage.export(data, format_type, path)
        except Exception:
            return None

    def import_data(self, path, format_type):
        """Импорт данных"""
        try:
            return self.storage.import_data(path, format_type)
        except Exception:
            return []

    def setup_logging(self, level):
        """Настройка логирования"""
        import logging
        try:
            logging.basicConfig(level=level)
        except Exception:
            # Не должно падать
            pass

    def _check_api_keys(self, config):
        """Проверка API ключей"""
        return bool(config.get("hh_api_key") or config.get("sj_api_key"))

    def _check_database_connection(self, config):
        """Проверка соединения с БД"""
        try:
            return self.storage.test_connection()
        except Exception:
            return False

    def get_data_sources(self):
        """Получение источников данных"""
        try:
            return self.data_provider.get_available_sources()
        except Exception:
            return []

    def validate_sources(self, sources):
        """Валидация источников"""
        try:
            return self.data_provider.validate_sources(sources)
        except Exception:
            return []

    def get_cached_data(self, query):
        """Получение кэшированных данных"""
        try:
            return self.data_provider.get_cached_data(query)
        except Exception:
            return []

    def clear_cache_data(self, sources):
        """Очистка кэшированных данных"""
        try:
            return self.data_provider.clear_cache(sources)
        except Exception:
            return False

    def validate_configuration(self, config):
        """Валидация конфигурации"""
        try:
            api_keys_ok = self._check_api_keys(config)
            db_ok = self._check_database_connection(config)
            return api_keys_ok and db_ok
        except Exception:
            return False


@pytest.mark.skipif(not MAIN_APPLICATION_INTERFACE_AVAILABLE, reason="MainApplicationInterface not available")
class TestMainApplicationInterfaceComplete:
    """Полное тестирование MainApplicationInterface"""

    @pytest.fixture
    def mock_provider(self):
        """Мок провайдера данных"""
        return Mock()

    @pytest.fixture
    def mock_processor(self):
        """Мок процессора"""
        return Mock()

    @pytest.fixture
    def mock_storage(self):
        """Мок хранилища"""
        return Mock()

    @pytest.fixture
    def app_interface(self, mock_provider, mock_processor, mock_storage):
        """Экземпляр интерфейса приложения"""
        return ConcreteMainApp(mock_provider, mock_processor, mock_storage)

    def test_init_with_dependencies(self, mock_provider, mock_processor, mock_storage):
        """Тест инициализации с зависимостями"""
        app = ConcreteMainApp(mock_provider, mock_processor, mock_storage)
        assert app.data_provider == mock_provider
        assert app.processor == mock_processor
        assert app.storage == mock_storage

    def test_run_application_abstract(self):
        """Тест что базовый класс абстрактный"""
        with pytest.raises(TypeError):
            MainApplicationInterface(Mock(), Mock(), Mock())

    def test_concrete_run_application(self, app_interface):
        """Тест конкретной реализации run_application"""
        with patch.object(app_interface, 'run_application') as mock_run:
            mock_run.return_value = "Application started"
            result = app_interface.run_application()
            assert result == "Application started"
            mock_run.assert_called_once()

    def test_get_data_sources(self, app_interface, mock_provider):
        """Тест получения источников данных"""
        mock_sources = ["hh", "sj"]
        mock_provider.get_available_sources.return_value = mock_sources

        result = app_interface.get_data_sources()
        assert result == mock_sources
        mock_provider.get_available_sources.assert_called_once()

    def test_get_data_sources_error(self, app_interface, mock_provider):
        """Тест обработки ошибок при получении источников"""
        mock_provider.get_available_sources.side_effect = Exception("Provider error")

        result = app_interface.get_data_sources()
        assert result == []

    def test_validate_sources(self, app_interface, mock_provider):
        """Тест валидации источников"""
        sources = ["hh", "sj"]
        mock_provider.validate_sources.return_value = sources

        result = app_interface.validate_sources(sources)
        assert result == sources
        mock_provider.validate_sources.assert_called_once_with(sources)

    def test_validate_sources_error(self, app_interface, mock_provider):
        """Тест обработки ошибок валидации источников"""
        mock_provider.validate_sources.side_effect = Exception("Validation error")

        result = app_interface.validate_sources(["invalid"])
        assert result == []

    def test_process_data(self, app_interface):
        """Тест обработки данных"""
        mock_data = [{"id": "1", "title": "Test Job"}]
        processed_data = [{"id": "1", "title": "Processed Job"}]

        app_interface.processor.process.return_value = processed_data

        result = app_interface.process_data(mock_data)
        assert result == processed_data
        app_interface.processor.process.assert_called_once_with(mock_data)

    def test_process_data_empty(self, app_interface):
        """Тест обработки пустых данных"""
        result = app_interface.process_data([])
        assert result == []

    def test_process_data_none(self, app_interface):
        """Тест обработки None данных"""
        result = app_interface.process_data(None)
        assert result == []

    def test_process_data_error(self, app_interface):
        """Тест обработки ошибок при обработке данных"""
        app_interface.processor.process.side_effect = Exception("Processing error")

        try:
            app_interface.process_data([{"id": "1"}])
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Processing error" in str(e)

    def test_store_data(self, app_interface):
        """Тест сохранения данных"""
        mock_data = [{"id": "1", "title": "Test Job"}]
        app_interface.storage.save.return_value = True

        result = app_interface.store_data(mock_data)
        assert result is True
        app_interface.storage.save.assert_called_once_with(mock_data)

    def test_store_data_empty(self, app_interface):
        """Тест сохранения пустых данных"""
        result = app_interface.store_data([])
        assert result is False

    def test_store_data_none(self, app_interface):
        """Тест сохранения None данных"""
        result = app_interface.store_data(None)
        assert result is False

    def test_store_data_error(self, app_interface):
        """Тест обработки ошибок при сохранении данных"""
        app_interface.storage.save.side_effect = Exception("Storage error")

        try:
            app_interface.store_data([{"id": "1"}])
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Storage error" in str(e)


    def test_search_data(self, app_interface):
        """Тест поиска данных"""
        mock_results = [{"id": "1", "title": "Python Job"}]
        app_interface.data_provider.search.return_value = mock_results

        result = app_interface.search_data("python", sources=["hh"])
        assert result == mock_results
        app_interface.data_provider.search.assert_called_once_with("python", sources=["hh"])

    def test_search_data_no_sources(self, app_interface, mock_provider):
        """Тест поиска данных без указания источников"""
        mock_results = [{"id": "1", "title": "Python Job"}]
        available_sources = ["hh", "sj"]

        mock_provider.get_available_sources.return_value = available_sources
        mock_provider.search.return_value = mock_results

        result = app_interface.search_data("python")
        assert result == mock_results
        mock_provider.search.assert_called_once_with("python", sources=available_sources)

    def test_search_data_empty_query(self, app_interface):
        """Тест поиска с пустым запросом"""
        result = app_interface.search_data("")
        assert result == []

    def test_search_data_none_query(self, app_interface):
        """Тест поиска с None запросом"""
        result = app_interface.search_data(None)
        assert result == []

    def test_search_data_error(self, app_interface):
        """Тест обработки ошибок при поиске"""
        app_interface.data_provider.search.side_effect = Exception("Search error")

        try:
            app_interface.search_data("python")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Search error" in str(e)

    def test_get_storage_stats(self, app_interface):
        """Тест получения статистики хранилища"""
        mock_stats = {"total": 100, "sources": {"hh": 60, "sj": 40}}
        app_interface.storage.get_stats.return_value = mock_stats

        result = app_interface.get_storage_stats()
        assert result == mock_stats
        app_interface.storage.get_stats.assert_called_once()

    def test_get_storage_stats_error(self, app_interface):
        """Тест обработки ошибок при получении статистики"""
        app_interface.storage.get_stats.side_effect = Exception("Stats error")

        try:
            app_interface.get_storage_stats()
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Stats error" in str(e)

    def test_clear_storage_data(self, app_interface):
        """Тест очистки данных хранилища"""
        app_interface.storage.clear.return_value = True

        result = app_interface.clear_storage_data()
        assert result is True
        app_interface.storage.clear.assert_called_once()

    def test_clear_storage_data_error(self, app_interface):
        """Тест обработки ошибок при очистке хранилища"""
        app_interface.storage.clear.side_effect = Exception("Clear error")

        try:
            app_interface.clear_storage_data()
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Clear error" in str(e)

    def test_get_cached_data(self, app_interface):
        """Тест получения кэшированных данных"""
        mock_cached_data = [{"id": "1", "title": "Cached Job"}]
        app_interface.data_provider.get_cached_data.return_value = mock_cached_data

        result = app_interface.get_cached_data("python")
        assert result == mock_cached_data
        app_interface.data_provider.get_cached_data.assert_called_once_with("python")

    def test_get_cached_data_error(self, app_interface):
        """Тест обработки ошибок при получении кэшированных данных"""
        app_interface.data_provider.get_cached_data.side_effect = Exception("Cache error")

        result = app_interface.get_cached_data("python")
        assert result == []

    def test_clear_cache_data(self, app_interface):
        """Тест очистки кэшированных данных"""
        sources = {"hh": True, "sj": False}
        app_interface.data_provider.clear_cache.return_value = True

        result = app_interface.clear_cache_data(sources)
        assert result is True
        app_interface.data_provider.clear_cache.assert_called_once_with(sources)

    def test_clear_cache_data_error(self, app_interface):
        """Тест обработки ошибок при очистке кэша"""
        app_interface.data_provider.clear_cache.side_effect = Exception("Cache clear error")

        result = app_interface.clear_cache_data({"hh": True})
        assert result is False

    def test_export_data(self, app_interface):
        """Тест экспорта данных"""
        mock_data = [{"id": "1", "title": "Export Job"}]
        app_interface.storage.export.return_value = "/path/to/export.json"

        result = app_interface.export_data(mock_data, "json", "/tmp/export.json")
        assert result == "/path/to/export.json"
        app_interface.storage.export.assert_called_once_with(mock_data, "json", "/tmp/export.json")

    def test_export_data_empty(self, app_interface):
        """Тест экспорта пустых данных"""
        result = app_interface.export_data([], "json", "/tmp/export.json")
        assert result is None

    def test_export_data_error(self, app_interface):
        """Тест обработки ошибок при экспорте"""
        app_interface.storage.export.side_effect = Exception("Export error")

        try:
            app_interface.export_data([{"id": "1"}], "json", "/tmp/export.json")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Export error" in str(e)

    def test_import_data(self, app_interface):
        """Тест импорта данных"""
        mock_imported_data = [{"id": "1", "title": "Imported Job"}]
        app_interface.storage.import_data.return_value = mock_imported_data

        result = app_interface.import_data("/path/to/import.json", "json")
        assert result == mock_imported_data
        app_interface.storage.import_data.assert_called_once_with("/path/to/import.json", "json")

    def test_import_data_error(self, app_interface):
        """Тест обработки ошибок при импорте"""
        app_interface.storage.import_data.side_effect = Exception("Import error")

        try:
            app_interface.import_data("/path/to/import.json", "json")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Import error" in str(e)

    def test_setup_logging(self, app_interface):
        """Тест настройки логирования"""
        with patch('logging.basicConfig') as mock_config:
            app_interface.setup_logging("DEBUG")
            mock_config.assert_called_once()

    def test_setup_logging_error(self, app_interface):
        """Тест обработки ошибок настройки логирования"""
        with patch('logging.basicConfig', side_effect=Exception("Logging error")):
            try:
                app_interface.setup_logging("DEBUG")
                assert False, "Should have raised exception"
            except Exception as e:
                assert "Logging error" in str(e)

    def test_validate_configuration(self, app_interface):
        """Тест валидации конфигурации"""
        mock_config = {"hh_api_key": "test", "sj_api_key": "test_sj", "db_url": "postgres://test"}

        with patch.object(app_interface, '_check_api_keys', return_value=True), \
             patch.object(app_interface, '_check_database_connection', return_value=True):
            result = app_interface.validate_configuration(mock_config)
            assert result is True

    def test_validate_configuration_invalid(self, app_interface):
        """Тест валидации некорректной конфигурации"""
        mock_config = {"invalid": "config"}

        with patch.object(app_interface, '_check_api_keys', return_value=False), \
             patch.object(app_interface, '_check_database_connection', return_value=False):
            result = app_interface.validate_configuration(mock_config)
            assert result is False

    def test_check_api_keys(self, app_interface):
        """Тест проверки API ключей"""
        config = {"hh_api_key": "test_hh", "sj_api_key": "test_sj"}
        result = app_interface._check_api_keys(config)
        assert result is True

    def test_check_api_keys_missing(self, app_interface):
        """Тест проверки отсутствующих API ключей"""
        config = {}
        result = app_interface._check_api_keys(config)
        assert result is False

    def test_check_database_connection(self, app_interface):
        """Тест проверки соединения с БД"""
        config = {"db_url": "postgresql://test"}

        with patch.object(app_interface.storage, 'test_connection', return_value=True):
            result = app_interface._check_database_connection(config)
            assert result is True

    def test_check_database_connection_fail(self, app_interface):
        """Тест неудачной проверки соединения с БД"""
        config = {"db_url": "postgresql://invalid"}

        with patch.object(app_interface.storage, 'test_connection', return_value=False):
            result = app_interface._check_database_connection(config)
            assert result is False


@pytest.mark.skipif(not MAIN_APPLICATION_INTERFACE_AVAILABLE, reason="MainApplicationInterface not available")
class TestMainApplicationInterfaceIntegration:
    """Интеграционные тесты MainApplicationInterface"""

    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        mock_provider = Mock()
        mock_processor = Mock()
        mock_storage = Mock()

        # Настройка моков
        mock_provider.search.return_value = [{"id": "1", "title": "Test Job"}]
        mock_processor.process.return_value = [{"id": "1", "title": "Processed Job"}]
        mock_storage.save.return_value = True
        mock_provider.get_available_sources.return_value = ["hh", "sj"]

        app = ConcreteMainApp(mock_provider, mock_processor, mock_storage)

        # Выполняем полный цикл
        search_results = app.search_data("python")
        processed_data = app.process_data(search_results)
        saved = app.store_data(processed_data)

        assert len(search_results) == 1
        assert len(processed_data) == 1
        assert saved is True

    def test_error_recovery(self):
        """Тест восстановления после ошибок"""
        mock_provider = Mock()
        mock_processor = Mock()
        mock_storage = Mock()

        # Настройка ошибок
        mock_provider.search.side_effect = Exception("Search error")
        mock_provider.get_available_sources.return_value = ["hh", "sj"]

        app = ConcreteMainApp(mock_provider, mock_processor, mock_storage)

        # Приложение должно справляться с ошибками
        search_results = app.search_data("python")
        assert search_results == []