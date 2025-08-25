
"""
Тесты для модуля управления источниками данных
"""

import pytest
from unittest.mock import patch, Mock
from src.utils.source_manager import SourceManager


class TestSourceManager:
    """Тесты для класса SourceManager"""

    def test_source_manager_initialization(self):
        """Тест инициализации SourceManager"""
        manager = SourceManager()
        assert manager is not None

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        manager = SourceManager()
        sources = manager.get_available_sources()
        
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "hh.ru" in sources
        assert "superjob.ru" in sources

    def test_get_source_config_hh(self):
        """Тест получения конфигурации для HH.ru"""
        manager = SourceManager()
        config = manager.get_source_config("hh.ru")
        
        assert config is not None
        assert "base_url" in config
        assert config["base_url"] == "https://api.hh.ru/vacancies"

    def test_get_source_config_sj(self):
        """Тест получения конфигурации для SuperJob"""
        manager = SourceManager()
        config = manager.get_source_config("superjob.ru")
        
        assert config is not None
        assert "base_url" in config
        assert config["base_url"] == "https://api.superjob.ru/2.0/vacancies"

    def test_get_source_config_invalid(self):
        """Тест получения конфигурации для несуществующего источника"""
        manager = SourceManager()
        config = manager.get_source_config("invalid_source")
        
        assert config is None

    def test_is_source_available_true(self):
        """Тест проверки доступности существующего источника"""
        manager = SourceManager()
        
        assert manager.is_source_available("hh.ru") is True
        assert manager.is_source_available("superjob.ru") is True

    def test_is_source_available_false(self):
        """Тест проверки доступности несуществующего источника"""
        manager = SourceManager()
        
        assert manager.is_source_available("invalid_source") is False

    def test_get_source_display_name(self):
        """Тест получения отображаемого имени источника"""
        manager = SourceManager()
        
        assert manager.get_source_display_name("hh.ru") == "HeadHunter"
        assert manager.get_source_display_name("superjob.ru") == "SuperJob"
        assert manager.get_source_display_name("invalid") == "invalid"

    def test_get_source_api_limits(self):
        """Тест получения лимитов API для источника"""
        manager = SourceManager()
        
        hh_limits = manager.get_source_api_limits("hh.ru")
        assert hh_limits is not None
        assert "requests_per_minute" in hh_limits
        
        sj_limits = manager.get_source_api_limits("superjob.ru")
        assert sj_limits is not None
        assert "requests_per_minute" in sj_limits

    def test_validate_source_credentials_hh(self):
        """Тест валидации учетных данных для HH (не требуются)"""
        manager = SourceManager()
        
        # HH.ru не требует API ключа
        is_valid = manager.validate_source_credentials("hh.ru", {})
        assert is_valid is True

    @patch.dict('os.environ', {'SUPERJOB_API_KEY': 'test_key'})
    def test_validate_source_credentials_sj_valid(self):
        """Тест валидации учетных данных для SJ (валидные)"""
        manager = SourceManager()
        
        credentials = {"api_key": "test_key"}
        is_valid = manager.validate_source_credentials("superjob.ru", credentials)
        assert is_valid is True

    def test_validate_source_credentials_sj_invalid(self):
        """Тест валидации учетных данных для SJ (невалидные)"""
        manager = SourceManager()
        
        credentials = {}  # Пустые учетные данные
        is_valid = manager.validate_source_credentials("superjob.ru", credentials)
        assert is_valid is False

    def test_get_source_priority(self):
        """Тест получения приоритета источника"""
        manager = SourceManager()
        
        hh_priority = manager.get_source_priority("hh.ru")
        sj_priority = manager.get_source_priority("superjob.ru")
        
        assert isinstance(hh_priority, int)
        assert isinstance(sj_priority, int)
        assert hh_priority != sj_priority

    def test_sort_sources_by_priority(self):
        """Тест сортировки источников по приоритету"""
        manager = SourceManager()
        
        sources = ["superjob.ru", "hh.ru"]
        sorted_sources = manager.sort_sources_by_priority(sources)
        
        assert len(sorted_sources) == 2
        assert sorted_sources[0] in ["hh.ru", "superjob.ru"]
        assert sorted_sources[1] in ["hh.ru", "superjob.ru"]

    def test_get_source_features(self):
        """Тест получения функций источника"""
        manager = SourceManager()
        
        hh_features = manager.get_source_features("hh.ru")
        assert isinstance(hh_features, list)
        assert "free_access" in hh_features
        
        sj_features = manager.get_source_features("superjob.ru")
        assert isinstance(sj_features, list)
        assert "api_key_required" in sj_features
