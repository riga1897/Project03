"""
Тесты для менеджера источников
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Моковые классы для тестов
class MockAPI:
    """Базовый мок API"""
    def __init__(self, name):
        self.name = name
        self.call_count = 0

    def get_vacancies(self, query, **kwargs):
        self.call_count += 1
        return [
            {
                "id": f"{self.name}_1",
                "title": f"{query} Developer",
                "source": self.name,
                "url": f"https://{self.name}.com/vacancy/1"
            }
        ]

class MockHHAPI(MockAPI):
    def __init__(self):
        super().__init__("hh.ru")

class MockSJAPI(MockAPI):
    def __init__(self):
        super().__init__("superjob.ru")

# Моковый SourceManager для тестов
class SourceManager:
    """Менеджер источников API"""

    def __init__(self):
        self.sources = {}
        self.active_sources = []

    def register_source(self, name: str, api_instance):
        """Регистрация источника API"""
        self.sources[name] = api_instance

    def activate_source(self, name: str):
        """Активация источника"""
        if name in self.sources and name not in self.active_sources:
            self.active_sources.append(name)

    def deactivate_source(self, name: str):
        """Деактивация источника"""
        if name in self.active_sources:
            self.active_sources.remove(name)

    def get_active_sources(self) -> List[str]:
        """Получение списка активных источников"""
        return self.active_sources.copy()

    def get_all_sources(self) -> List[str]:
        """Получение списка всех зарегистрированных источников"""
        return list(self.sources.keys())

    def get_vacancies_from_all_sources(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получение вакансий из всех активных источников"""
        all_vacancies = []

        for source_name in self.active_sources:
            if source_name in self.sources:
                try:
                    api = self.sources[source_name]
                    vacancies = api.get_vacancies(query, **kwargs)
                    all_vacancies.extend(vacancies)
                except Exception:
                    # Пропускаем ошибки отдельных источников
                    continue

        return all_vacancies

class TestSourceManager:
    """Тесты для SourceManager"""
    
    def setup_method(self):
        """Подготовка к каждому тесту"""
        self.source_manager = SourceManager()
        self.mock_hh_api = MockHHAPI()
        self.mock_sj_api = MockSJAPI()
    
    def test_register_source(self):
        """Тест регистрации источника"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        
        sources = self.source_manager.get_all_sources()
        assert "hh.ru" in sources
        assert len(sources) == 1
    
    def test_register_multiple_sources(self):
        """Тест регистрации нескольких источников"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.register_source("superjob.ru", self.mock_sj_api)
        
        sources = self.source_manager.get_all_sources()
        assert "hh.ru" in sources
        assert "superjob.ru" in sources
        assert len(sources) == 2
    
    def test_activate_source(self):
        """Тест активации источника"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.activate_source("hh.ru")
        
        active_sources = self.source_manager.get_active_sources()
        assert "hh.ru" in active_sources
        assert len(active_sources) == 1
        assert self.source_manager.is_source_active("hh.ru") is True
    
    def test_activate_nonexistent_source(self):
        """Тест активации несуществующего источника"""
        self.source_manager.activate_source("nonexistent.ru")
        
        active_sources = self.source_manager.get_active_sources()
        assert len(active_sources) == 0
    
    def test_deactivate_source(self):
        """Тест деактивации источника"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.activate_source("hh.ru")
        
        assert self.source_manager.is_source_active("hh.ru") is True
        
        self.source_manager.deactivate_source("hh.ru")
        
        assert self.source_manager.is_source_active("hh.ru") is False
        active_sources = self.source_manager.get_active_sources()
        assert len(active_sources) == 0
    
    def test_deactivate_inactive_source(self):
        """Тест деактивации неактивного источника"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        
        # Источник не активирован, попытка деактивации не должна вызвать ошибку
        self.source_manager.deactivate_source("hh.ru")
        
        active_sources = self.source_manager.get_active_sources()
        assert len(active_sources) == 0
    
    def test_get_active_sources_copy(self):
        """Тест получения копии списка активных источников"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.activate_source("hh.ru")
        
        active_sources = self.source_manager.get_active_sources()
        active_sources.append("fake_source")
        
        # Изменения в полученном списке не должны влиять на оригинал
        original_active = self.source_manager.get_active_sources()
        assert "fake_source" not in original_active
        assert len(original_active) == 1
    
    def test_get_vacancies_from_all_sources(self):
        """Тест получения вакансий из всех активных источников"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.register_source("superjob.ru", self.mock_sj_api)
        
        self.source_manager.activate_source("hh.ru")
        self.source_manager.activate_source("superjob.ru")
        
        vacancies = self.source_manager.get_vacancies_from_all_sources("python")
        
        assert len(vacancies) == 2
        sources_in_results = [v["source"] for v in vacancies]
        assert "hh.ru" in sources_in_results
        assert "superjob.ru" in sources_in_results
    
    def test_get_vacancies_from_all_sources_no_active(self):
        """Тест получения вакансий без активных источников"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        
        # Не активируем источник
        vacancies = self.source_manager.get_vacancies_from_all_sources("python")
        
        assert len(vacancies) == 0
    
    def test_get_vacancies_from_source(self):
        """Тест получения вакансий из конкретного источника"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        
        vacancies = self.source_manager.get_vacancies_from_source("hh.ru", "python")
        
        assert len(vacancies) == 1
        assert vacancies[0]["source"] == "hh.ru"
        assert vacancies[0]["title"] == "python Developer"
    
    def test_get_vacancies_from_nonexistent_source(self):
        """Тест получения вакансий из несуществующего источника"""
        vacancies = self.source_manager.get_vacancies_from_source("nonexistent.ru", "python")
        
        assert len(vacancies) == 0
    
    def test_get_vacancies_with_api_error(self):
        """Тест обработки ошибки API при получении вакансий"""
        # Создаем API, который выбрасывает исключение
        error_api = Mock()
        error_api.get_vacancies.side_effect = Exception("API Error")
        
        self.source_manager.register_source("error.ru", error_api)
        self.source_manager.activate_source("error.ru")
        
        # Должен вернуть пустой список без выброса исключения
        vacancies = self.source_manager.get_vacancies_from_all_sources("python")
        assert len(vacancies) == 0
        
        # Для конкретного источника тоже
        vacancies_specific = self.source_manager.get_vacancies_from_source("error.ru", "python")
        assert len(vacancies_specific) == 0
    
    def test_clear_active_sources(self):
        """Тест очистки активных источников"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.register_source("superjob.ru", self.mock_sj_api)
        
        self.source_manager.activate_source("hh.ru")
        self.source_manager.activate_source("superjob.ru")
        
        assert len(self.source_manager.get_active_sources()) == 2
        
        self.source_manager.clear_active_sources()
        
        assert len(self.source_manager.get_active_sources()) == 0
        assert self.source_manager.is_source_active("hh.ru") is False
        assert self.source_manager.is_source_active("superjob.ru") is False
    
    def test_get_source_stats(self):
        """Тест получения статистики по источникам"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.register_source("superjob.ru", self.mock_sj_api)
        
        self.source_manager.activate_source("hh.ru")
        
        # Делаем несколько запросов
        self.source_manager.get_vacancies_from_source("hh.ru", "python")
        self.source_manager.get_vacancies_from_source("hh.ru", "java")
        
        stats = self.source_manager.get_source_stats()
        
        assert "hh.ru" in stats
        assert "superjob.ru" in stats
        
        assert stats["hh.ru"]["registered"] is True
        assert stats["hh.ru"]["active"] is True
        assert stats["hh.ru"]["call_count"] == 2
        
        assert stats["superjob.ru"]["registered"] is True
        assert stats["superjob.ru"]["active"] is False
        assert stats["superjob.ru"]["call_count"] == 0
    
    def test_duplicate_activation(self):
        """Тест повторной активации источника"""
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        
        self.source_manager.activate_source("hh.ru")
        self.source_manager.activate_source("hh.ru")  # Повторная активация
        
        active_sources = self.source_manager.get_active_sources()
        assert len(active_sources) == 1  # Не должно быть дубликатов
        assert "hh.ru" in active_sources
    
    def test_is_source_active_for_nonexistent(self):
        """Тест проверки активности несуществующего источника"""
        result = self.source_manager.is_source_active("nonexistent.ru")
        assert result is False
    
    def test_integration_workflow(self):
        """Тест интегрированного рабочего процесса"""
        # Регистрация источников
        self.source_manager.register_source("hh.ru", self.mock_hh_api)
        self.source_manager.register_source("superjob.ru", self.mock_sj_api)
        
        # Проверка регистрации
        all_sources = self.source_manager.get_all_sources()
        assert len(all_sources) == 2
        
        # Активация одного источника
        self.source_manager.activate_source("hh.ru")
        
        # Проверка активности
        assert self.source_manager.is_source_active("hh.ru") is True
        assert self.source_manager.is_source_active("superjob.ru") is False
        
        # Получение вакансий
        vacancies = self.source_manager.get_vacancies_from_all_sources("python")
        assert len(vacancies) == 1
        assert vacancies[0]["source"] == "hh.ru"
        
        # Активация второго источника
        self.source_manager.activate_source("superjob.ru")
        
        # Получение вакансий из всех источников
        all_vacancies = self.source_manager.get_vacancies_from_all_sources("java")
        assert len(all_vacancies) == 2
        
        # Проверка статистики
        stats = self.source_manager.get_source_stats()
        assert stats["hh.ru"]["call_count"] == 2  # python + java
        assert stats["superjob.ru"]["call_count"] == 1  # java
        
        # Очистка
        self.source_manager.clear_active_sources()
        assert len(self.source_manager.get_active_sources()) == 0


    def get_vacancies_from_source(self, source_name: str, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получение вакансий из конкретного источника"""
        if source_name not in self.sources:
            return []

        try:
            api = self.sources[source_name]
            return api.get_vacancies(query, **kwargs)
        except Exception:
            return []

    def is_source_active(self, name: str) -> bool:
        """Проверка активности источника"""
        return name in self.active_sources

    def clear_active_sources(self):
        """Очистка списка активных источников"""
        self.active_sources.clear()

    def get_source_stats(self) -> Dict[str, Dict[str, Any]]:
        """Получение статистики по источникам"""
        stats = {}

        for source_name, api in self.sources.items():
            stats[source_name] = {
                'registered': True,
                'active': source_name in self.active_sources,
                'call_count': getattr(api, 'call_count', 0)
            }

        return stats


class TestSourceManager:
    """Тесты для класса SourceManager"""

    def test_source_manager_initialization(self):
        """Тест инициализации SourceManager"""
        manager = SourceManager()
        assert manager is not None

    def test_register_and_activate_source(self):
        """Тест регистрации и активации источника"""
        manager = SourceManager()
        mock_api = MockHHAPI()
        manager.register_source("hh.ru", mock_api)
        manager.activate_source("hh.ru")
        assert "hh.ru" in manager.get_all_sources()
        assert "hh.ru" in manager.get_active_sources()
        assert manager.is_source_active("hh.ru") is True

    def test_deactivate_source(self):
        """Тест деактивации источника"""
        manager = SourceManager()
        mock_api = MockHHAPI()
        manager.register_source("hh.ru", mock_api)
        manager.activate_source("hh.ru")
        manager.deactivate_source("hh.ru")
        assert "hh.ru" not in manager.get_active_sources()
        assert manager.is_source_active("hh.ru") is False

    def test_get_vacancies_from_all_sources(self):
        """Тест получения вакансий из всех активных источников"""
        manager = SourceManager()
        mock_hh_api = MockHHAPI()
        mock_sj_api = MockSJAPI()

        manager.register_source("hh.ru", mock_hh_api)
        manager.register_source("superjob.ru", mock_sj_api)

        manager.activate_source("hh.ru")
        manager.activate_source("superjob.ru")

        vacancies = manager.get_vacancies_from_all_sources("python developer")

        assert len(vacancies) == 2
        assert vacancies[0]["source"] == "hh.ru"
        assert vacancies[1]["source"] == "superjob.ru"
        assert mock_hh_api.call_count == 1
        assert mock_sj_api.call_count == 1

    def test_get_vacancies_from_source(self):
        """Тест получения вакансий из конкретного источника"""
        manager = SourceManager()
        mock_hh_api = MockHHAPI()
        mock_sj_api = MockSJAPI()

        manager.register_source("hh.ru", mock_hh_api)
        manager.register_source("superjob.ru", mock_sj_api)

        hh_vacancies = manager.get_vacancies_from_source("hh.ru", "python developer")
        sj_vacancies = manager.get_vacancies_from_source("superjob.ru", "python developer")
        invalid_vacancies = manager.get_vacancies_from_source("invalid.ru", "python developer")

        assert len(hh_vacancies) == 1
        assert hh_vacancies[0]["source"] == "hh.ru"
        assert mock_hh_api.call_count == 1
        assert mock_sj_api.call_count == 0

        assert len(sj_vacancies) == 1
        assert sj_vacancies[0]["source"] == "superjob.ru"
        assert mock_hh_api.call_count == 1
        assert mock_sj_api.call_count == 1

        assert len(invalid_vacancies) == 0

    def test_get_source_stats(self):
        """Тест получения статистики по источникам"""
        manager = SourceManager()
        mock_hh_api = MockHHAPI()
        mock_sj_api = MockSJAPI()

        manager.register_source("hh.ru", mock_hh_api)
        manager.register_source("superjob.ru", mock_sj_api)
        manager.activate_source("hh.ru")

        stats = manager.get_source_stats()

        assert "hh.ru" in stats
        assert stats["hh.ru"]["registered"] is True
        assert stats["hh.ru"]["active"] is True
        assert stats["hh.ru"]["call_count"] == 0

        assert "superjob.ru" in stats
        assert stats["superjob.ru"]["registered"] is True
        assert stats["superjob.ru"]["active"] is False
        assert stats["superjob.ru"]["call_count"] == 0

    def test_clear_active_sources(self):
        """Тест очистки списка активных источников"""
        manager = SourceManager()
        mock_api = MockHHAPI()
        manager.register_source("hh.ru", mock_api)
        manager.activate_source("hh.ru")
        manager.clear_active_sources()
        assert len(manager.get_active_sources()) == 0
        assert manager.is_source_active("hh.ru") is False

    def test_get_vacancies_with_error_handling(self):
        """Тест получения вакансий с обработкой ошибок"""
        manager = SourceManager()
        mock_api = Mock()
        mock_api.get_vacancies.side_effect = Exception("API error")
        manager.register_source("error_source", mock_api)
        manager.activate_source("error_source")

        vacancies = manager.get_vacancies_from_all_sources("test")

        assert len(vacancies) == 0
        assert mock_api.get_vacancies.call_count == 1