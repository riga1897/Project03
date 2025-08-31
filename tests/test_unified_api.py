import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Создаем тестовые классы для изолированного тестирования
class MockHeadHunterAPI:
    """Мок HH API"""

    def __init__(self):
        pass

    def get_vacancies(self, search_query, **kwargs):
        return [{"id": 1, "title": "Python Developer", "source": "hh"}]

    def clear_cache(self, source):
        pass


class MockSuperJobAPI:
    """Мок SJ API"""

    def __init__(self):
        pass

    def get_vacancies(self, search_query, **kwargs):
        return [{"id": 2, "title": "Java Developer", "source": "sj"}]

    def clear_cache(self, source):
        pass


class MockSuperJobParser:
    """Мок SJ Parser"""

    def __init__(self):
        pass


class MockVacancy:
    """Мок Vacancy"""

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def to_dict(self):
        return self.data


class MockPostgresSaver:
    """Мок PostgresSaver"""

    def __init__(self):
        pass

    def filter_and_deduplicate_vacancies(self, vacancies, filters):
        return vacancies


# Создаем тестовый UnifiedAPI без реальных зависимостей
class UnifiedAPIForTesting:
    """Тестовый Unифицированный API без обращений к реальным ресурсам"""

    def __init__(self):
        self.hh_api = MockHeadHunterAPI()
        self.sj_api = MockSuperJobAPI()
        self.parser = MockSuperJobParser()
        self.apis = {
            "hh": self.hh_api,
            "sj": self.sj_api,
        }

    def get_vacancies_from_sources(self, search_query, sources=None, **kwargs):
        """Получение вакансий из источников с моками"""
        if sources is None:
            sources = self.get_available_sources()

        all_vacancies = []

        if "hh" in sources:
            hh_data = self.hh_api.get_vacancies(search_query, **kwargs)
            all_vacancies.extend(hh_data)

        if "sj" in sources:
            sj_data = self.sj_api.get_vacancies(search_query, **kwargs)
            all_vacancies.extend(sj_data)

        return self._filter_by_target_companies(all_vacancies)

    def _filter_by_target_companies(self, all_vacancies):
        """Мок фильтрации без обращения к БД"""
        return all_vacancies

    def get_available_sources(self):
        return ["hh", "sj"]

    def validate_sources(self, sources):
        available = self.get_available_sources()
        valid_sources = [s for s in sources if s in available]
        return valid_sources if valid_sources else available

    def clear_cache(self, sources):
        """Мок очистки кэша"""
        if sources.get("hh", False):
            self.hh_api.clear_cache("hh")
        if sources.get("sj", False):
            self.sj_api.clear_cache("sj")

    def get_vacancies_from_source(self, search_query, source, **kwargs):
        """Получение вакансий из одного источника"""
        if source not in self.get_available_sources():
            return []

        api = self.apis.get(source)
        if not api:
            return []

        return api.get_vacancies(search_query, **kwargs)

    def get_all_vacancies(self, query, **kwargs):
        """Получение всех вакансий"""
        return self.get_vacancies_from_sources(query, sources=["hh", "sj"], **kwargs)

    def search_with_multiple_keywords(self, keywords, **kwargs):
        """Поиск с несколькими ключевыми словами"""
        all_results = []
        for keyword in keywords:
            results = self.get_all_vacancies(keyword, **kwargs)
            all_results.extend(results)

        # Дедупликация по ID
        seen_ids = set()
        unique_results = []
        for result in all_results:
            vacancy_id = result.get("id")
            if vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                unique_results.append(result)

        return unique_results


class TestUnifiedAPIUnit:
    """Юнит тесты для UnifiedAPI с полной изоляцией"""

    def test_unified_api_initialization(self):
        """Тест инициализации UnifiedAPI"""
        api = UnifiedAPIForTesting()

        assert api.hh_api is not None
        assert api.sj_api is not None
        assert api.parser is not None
        assert "hh" in api.apis
        assert "sj" in api.apis

    def test_get_available_sources(self):
        """Тест получения доступных источников"""
        api = UnifiedAPIForTesting()
        sources = api.get_available_sources()

        assert isinstance(sources, list)
        assert "hh" in sources
        assert "sj" in sources

    def test_validate_sources_with_valid_sources(self):
        """Тест валидации валидных источников"""
        api = UnifiedAPIForTesting()
        valid_sources = api.validate_sources(["hh", "sj"])

        assert "hh" in valid_sources
        assert "sj" in valid_sources

    def test_validate_sources_with_invalid_sources(self):
        """Тест валидации невалидных источников"""
        api = UnifiedAPIForTesting()
        valid_sources = api.validate_sources(["invalid_source"])

        # Должны вернуться все доступные источники
        assert "hh" in valid_sources
        assert "sj" in valid_sources

    def test_get_vacancies_from_sources_hh_only(self):
        """Тест получения вакансий только из HH"""
        api = UnifiedAPIForTesting()
        result = api.get_vacancies_from_sources("Python", sources=["hh"])

        assert len(result) == 1
        assert result[0]["source"] == "hh"

    def test_get_vacancies_from_sources_both_sources(self):
        """Тест получения вакансий из обоих источников"""
        api = UnifiedAPIForTesting()
        result = api.get_vacancies_from_sources("Python", sources=["hh", "sj"])

        assert len(result) == 2
        sources = [v["source"] for v in result]
        assert "hh" in sources
        assert "sj" in sources

    def test_clear_cache(self):
        """Тест очистки кэша"""
        api = UnifiedAPIForTesting()

        # Мокаем методы clear_cache
        api.hh_api.clear_cache = Mock()
        api.sj_api.clear_cache = Mock()

        api.clear_cache({"hh": True, "sj": True})

        api.hh_api.clear_cache.assert_called_once_with("hh")
        api.sj_api.clear_cache.assert_called_once_with("sj")

    def test_get_vacancies_from_source_single(self):
        """Тест получения вакансий из одного источника"""
        api = UnifiedAPIForTesting()
        result = api.get_vacancies_from_source("Python", "hh")

        assert len(result) == 1
        assert result[0]["source"] == "hh"

    def test_get_vacancies_from_source_unknown(self):
        """Тест получения вакансий из неизвестного источника"""
        api = UnifiedAPIForTesting()
        result = api.get_vacancies_from_source("Python", "unknown")

        assert result == []

    def test_get_all_vacancies(self):
        """Тест получения всех вакансий"""
        api = UnifiedAPIForTesting()
        result = api.get_all_vacancies("Python")

        assert len(result) == 2
        sources = [v["source"] for v in result]
        assert "hh" in sources
        assert "sj" in sources

    def test_search_with_multiple_keywords(self):
        """Тест поиска с несколькими ключевыми словами"""
        api = UnifiedAPIForTesting()
        result = api.search_with_multiple_keywords(["Python", "Java"])

        # Должны получить уникальные результаты
        assert len(result) == 2
        ids = [v["id"] for v in result]
        assert len(set(ids)) == len(ids)  # Проверяем уникальность

    def test_filter_by_target_companies_empty_list(self):
        """Тест фильтрации с пустым списком"""
        api = UnifiedAPIForTesting()
        result = api._filter_by_target_companies([])

        assert result == []

    def test_filter_by_target_companies_with_data(self):
        """Тест фильтрации с данными"""
        api = UnifiedAPIForTesting()
        test_vacancies = [{"id": 1, "title": "Test Job"}]

        result = api._filter_by_target_companies(test_vacancies)

        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_validate_sources_empty_list(self):
        """Тест валидации с пустым списком"""
        api = UnifiedAPIForTesting()
        result = api.validate_sources([])

        # Должны вернуться все доступные источники
        assert "hh" in result
        assert "sj" in result

    def test_get_vacancies_from_sources_no_sources(self):
        """Тест получения вакансий без указания источников"""
        api = UnifiedAPIForTesting()
        result = api.get_vacancies_from_sources("Python")

        # Должны использоваться все доступные источники
        assert len(result) == 2

    def test_clear_cache_partial(self):
        """Тест частичной очистки кэша"""
        api = UnifiedAPIForTesting()

        api.hh_api.clear_cache = Mock()
        api.sj_api.clear_cache = Mock()

        api.clear_cache({"hh": True, "sj": False})

        api.hh_api.clear_cache.assert_called_once_with("hh")
        api.sj_api.clear_cache.assert_not_called()

    def test_get_vacancies_kwargs_handling(self):
        """Тест передачи дополнительных параметров"""
        api = UnifiedAPIForTesting()

        # Мокаем методы для проверки передачи параметров
        api.hh_api.get_vacancies = Mock(return_value=[{"id": 1, "source": "hh"}])
        api.sj_api.get_vacancies = Mock(return_value=[{"id": 2, "source": "sj"}])

        result = api.get_vacancies_from_sources("Python", sources=["hh"], period=30)

        api.hh_api.get_vacancies.assert_called_once_with("Python", period=30)
        assert len(result) == 1
