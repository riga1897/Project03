
"""
Тесты для менеджера источников
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class SourceManager:
    """Менеджер источников данных"""
    
    def __init__(self):
        """Инициализация менеджера источников"""
        self.available_sources = {
            "hh.ru": {
                "name": "HeadHunter",
                "enabled": True,
                "api_key_required": False
            },
            "superjob.ru": {
                "name": "SuperJob", 
                "enabled": True,
                "api_key_required": True
            }
        }
    
    def get_enabled_sources(self) -> list:
        """
        Получение списка включенных источников
        
        Returns:
            list: Список включенных источников
        """
        enabled = []
        for source_id, config in self.available_sources.items():
            if config.get("enabled", False):
                enabled.append(source_id)
        return enabled
    
    def is_source_available(self, source_id: str) -> bool:
        """
        Проверка доступности источника
        
        Args:
            source_id: Идентификатор источника
            
        Returns:
            bool: True если источник доступен
        """
        config = self.available_sources.get(source_id)
        if not config:
            return False
        
        if not config.get("enabled", False):
            return False
        
        if config.get("api_key_required", False):
            # Проверяем наличие API ключа
            return self._check_api_key(source_id)
        
        return True
    
    def _check_api_key(self, source_id: str) -> bool:
        """
        Проверка наличия API ключа
        
        Args:
            source_id: Идентификатор источника
            
        Returns:
            bool: True если API ключ настроен
        """
        if source_id == "superjob.ru":
            import os
            key = os.getenv("SUPERJOB_API_KEY")
            return key is not None and key != "v3.r.137440105.example.test_tool"
        return True
    
    def get_source_info(self, source_id: str) -> dict:
        """
        Получение информации об источнике
        
        Args:
            source_id: Идентификатор источника
            
        Returns:
            dict: Информация об источнике
        """
        return self.available_sources.get(source_id, {})
    
    def enable_source(self, source_id: str) -> bool:
        """
        Включение источника
        
        Args:
            source_id: Идентификатор источника
            
        Returns:
            bool: True если успешно включен
        """
        if source_id in self.available_sources:
            self.available_sources[source_id]["enabled"] = True
            return True
        return False
    
    def disable_source(self, source_id: str) -> bool:
        """
        Отключение источника
        
        Args:
            source_id: Идентификатор источника
            
        Returns:
            bool: True если успешно отключен
        """
        if source_id in self.available_sources:
            self.available_sources[source_id]["enabled"] = False
            return True
        return False


class TestSourceManager:
    """Тесты для менеджера источников"""
    
    @pytest.fixture
    def source_manager(self):
        """Фикстура менеджера источников"""
        return SourceManager()
    
    def test_initialization(self, source_manager):
        """Тест инициализации менеджера"""
        assert "hh.ru" in source_manager.available_sources
        assert "superjob.ru" in source_manager.available_sources
    
    def test_get_enabled_sources(self, source_manager):
        """Тест получения включенных источников"""
        enabled = source_manager.get_enabled_sources()
        assert isinstance(enabled, list)
        assert "hh.ru" in enabled
        assert "superjob.ru" in enabled
    
    def test_is_source_available_existing(self, source_manager):
        """Тест проверки доступности существующего источника"""
        # HH.ru не требует API ключ
        assert source_manager.is_source_available("hh.ru") is True
    
    def test_is_source_available_non_existing(self, source_manager):
        """Тест проверки доступности несуществующего источника"""
        assert source_manager.is_source_available("unknown.ru") is False
    
    def test_is_source_available_disabled(self, source_manager):
        """Тест проверки доступности отключенного источника"""
        source_manager.disable_source("hh.ru")
        assert source_manager.is_source_available("hh.ru") is False
    
    @patch.dict(os.environ, {"SUPERJOB_API_KEY": "real_api_key"})
    def test_is_source_available_with_api_key(self, source_manager):
        """Тест проверки доступности источника с API ключом"""
        assert source_manager.is_source_available("superjob.ru") is True
    
    @patch.dict(os.environ, {"SUPERJOB_API_KEY": "v3.r.137440105.example.test_tool"})
    def test_is_source_available_with_test_api_key(self, source_manager):
        """Тест проверки доступности источника с тестовым API ключом"""
        assert source_manager.is_source_available("superjob.ru") is False
    
    @patch.dict(os.environ, {}, clear=True)
    def test_is_source_available_without_api_key(self, source_manager):
        """Тест проверки доступности источника без API ключа"""
        assert source_manager.is_source_available("superjob.ru") is False
    
    def test_get_source_info_existing(self, source_manager):
        """Тест получения информации о существующем источнике"""
        info = source_manager.get_source_info("hh.ru")
        assert info["name"] == "HeadHunter"
        assert info["enabled"] is True
        assert info["api_key_required"] is False
    
    def test_get_source_info_non_existing(self, source_manager):
        """Тест получения информации о несуществующем источнике"""
        info = source_manager.get_source_info("unknown.ru")
        assert info == {}
    
    def test_enable_source_existing(self, source_manager):
        """Тест включения существующего источника"""
        source_manager.disable_source("hh.ru")  # Сначала отключаем
        result = source_manager.enable_source("hh.ru")
        assert result is True
        assert source_manager.available_sources["hh.ru"]["enabled"] is True
    
    def test_enable_source_non_existing(self, source_manager):
        """Тест включения несуществующего источника"""
        result = source_manager.enable_source("unknown.ru")
        assert result is False
    
    def test_disable_source_existing(self, source_manager):
        """Тест отключения существующего источника"""
        result = source_manager.disable_source("hh.ru")
        assert result is True
        assert source_manager.available_sources["hh.ru"]["enabled"] is False
    
    def test_disable_source_non_existing(self, source_manager):
        """Тест отключения несуществующего источника"""
        result = source_manager.disable_source("unknown.ru")
        assert result is False
    
    def test_check_api_key_hh(self, source_manager):
        """Тест проверки API ключа для HH.ru"""
        # HH.ru не требует API ключ
        result = source_manager._check_api_key("hh.ru")
        assert result is True
    
    @patch.dict(os.environ, {"SUPERJOB_API_KEY": "real_key"})
    def test_check_api_key_sj_with_key(self, source_manager):
        """Тест проверки API ключа для SuperJob с ключом"""
        result = source_manager._check_api_key("superjob.ru")
        assert result is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_check_api_key_sj_without_key(self, source_manager):
        """Тест проверки API ключа для SuperJob без ключа"""
        result = source_manager._check_api_key("superjob.ru")
        assert result is False
