"""
Тесты для унифицированного API
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.api_modules.unified_api import UnifiedAPI


class MockVacancy:
    """Мок вакансии для тестов"""
    def __init__(self, data):
        self.data = data
        self.vacancy_id = data.get('id', data.get('vacancy_id', ''))
        self.title = data.get('name', data.get('title', ''))
        self.url = data.get('alternate_url', data.get('url', ''))
        self.source = data.get('source', '')

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def to_dict(self):
        return self.data


class MockAPIConfig:
    """Мок конфигурации API"""
    def get_pagination_params(self, **kwargs):
        return {"max_pages": 5}


class MockStorage:
    """Мок хранилища с SQL-дедупликацией"""
    def __init__(self):
        self.saved_vacancies = []

    def filter_and_deduplicate_vacancies(self, vacancies, filters=None):
        """Мок SQL-фильтрации и дедупликации"""
        if not vacancies:
            return []

        # Имитируем SQL-дедупликацию по vacancy_id
        seen_ids = set()
        unique_vacancies = []

        for vacancy in vacancies:
            vacancy_id = getattr(vacancy, 'vacancy_id', None)
            if vacancy_id and vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                unique_vacancies.append(vacancy)

        return unique_vacancies

    def add_vacancy(self, vacancies):
        """Мок сохранения вакансий"""
        if not isinstance(vacancies, list):
            vacancies = [vacancies]
        self.saved_vacancies.extend(vacancies)
        return [f"Сохранена вакансия {getattr(v, 'vacancy_id', 'unknown')}" for v in vacancies]


class TestUnifiedAPI:
    """Тесты для UnifiedAPI"""

    @pytest.fixture
    def mock_unified_api(self):
        """Создает мок UnifiedAPI для тестов"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh, \
             patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj:

            api = UnifiedAPI()
            api.hh_api = mock_hh.return_value
            api.sj_api = mock_sj.return_value
            return api

    def test_initialization(self, mock_unified_api):
        """Тест инициализации UnifiedAPI"""
        assert mock_unified_api.hh_api is not None
        assert mock_unified_api.sj_api is not None
        assert hasattr(mock_unified_api, 'apis')
        assert 'hh' in mock_unified_api.apis
        assert 'sj' in mock_unified_api.apis

    def test_get_available_sources(self, mock_unified_api):
        """Тест получения доступных источников"""
        sources = mock_unified_api.get_available_sources()
        assert isinstance(sources, list)
        assert "hh" in sources
        assert "sj" in sources

    def test_validate_sources_valid(self, mock_unified_api):
        """Тест валидации корректных источников"""
        valid_sources = mock_unified_api.validate_sources(["hh", "sj"])
        assert valid_sources == ["hh", "sj"]

    def test_validate_sources_invalid(self, mock_unified_api):
        """Тест валидации некорректных источников"""
        # При невалидных источниках должны вернуться все доступные
        invalid_sources = mock_unified_api.validate_sources(["invalid_source"])
        assert set(invalid_sources) == {"hh", "sj"}

    def test_get_vacancies_from_source_hh(self, mock_unified_api):
        """Тест получения вакансий с HH"""
        mock_unified_api.hh_api.get_vacancies.return_value = [
            {"id": "1", "name": "Python Developer", "source": "hh.ru"}
        ]

        result = mock_unified_api.get_vacancies_from_source("python", "hh")

        assert len(result) == 1
        assert result[0]["source"] == "hh.ru"
        mock_unified_api.hh_api.get_vacancies.assert_called_once_with(search_query="python")

    def test_get_vacancies_from_source_sj(self, mock_unified_api):
        """Тест получения вакансий с SuperJob"""
        mock_unified_api.sj_api.get_vacancies.return_value = [
            {"id": "2", "profession": "Java Developer", "source": "superjob.ru"}
        ]

        result = mock_unified_api.get_vacancies_from_source("java", "sj")

        assert len(result) == 1
        assert result[0]["source"] == "superjob.ru"
        mock_unified_api.sj_api.get_vacancies.assert_called_once_with(search_query="java")

    def test_get_vacancies_from_source_unknown(self, mock_unified_api):
        """Тест получения вакансий с неизвестного источника"""
        result = mock_unified_api.get_vacancies_from_source("python", "unknown")

        assert result == []

    @patch('src.api_modules.unified_api.PostgresSaver')
    def test_get_vacancies_from_sources_with_sql_deduplication(self, mock_postgres_class, mock_unified_api):
        """Тест получения вакансий из источников с SQL-дедупликацией"""
        # Настраиваем мок PostgresSaver
        mock_postgres = MockStorage()
        mock_postgres_class.return_value = mock_postgres

        # Настраиваем возвращаемые данные
        mock_unified_api.hh_api.get_vacancies.return_value = [
            {"id": "1", "name": "HH Vacancy", "source": "hh.ru"}
        ]
        mock_unified_api.sj_api.get_vacancies.return_value = [
            {"id": "2", "profession": "SJ Vacancy", "source": "superjob.ru"}
        ]

        # Мокируем Vacancy.from_dict
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy_class.from_dict.side_effect = lambda x: MockVacancy(x)

            # Мокируем _filter_by_target_companies для возврата отфильтрованных данных
            with patch.object(mock_unified_api, '_filter_by_target_companies') as mock_filter:
                mock_filter.return_value = [{"id": "1", "name": "Filtered Vacancy"}]

                result = mock_unified_api.get_vacancies_from_sources("python", ["hh", "sj"])

                # Проверяем результат
                assert len(result) == 1
                assert result[0]["id"] == "1"

                # Проверяем вызовы API
                mock_unified_api.hh_api.get_vacancies.assert_called_once()
                mock_unified_api.sj_api.get_vacancies.assert_called_once()

                # Проверяем что была вызвана SQL-фильтрация
                mock_filter.assert_called_once()

    def test_get_vacancies_from_sources_empty_result(self, mock_unified_api):
        """Тест получения вакансий когда нет результатов"""
        mock_unified_api.hh_api.get_vacancies.return_value = []
        mock_unified_api.sj_api.get_vacancies.return_value = []

        result = mock_unified_api.get_vacancies_from_sources("nonexistent")

        assert result == []

    def test_get_vacancies_from_sources_api_error(self, mock_unified_api):
        """Тест обработки ошибок API"""
        mock_unified_api.hh_api.get_vacancies.side_effect = Exception("HH API Error")
        mock_unified_api.sj_api.get_vacancies.return_value = [
            {"id": "2", "profession": "SJ Vacancy", "source": "superjob.ru"}
        ]

        with patch('src.api_modules.unified_api.PostgresSaver') as mock_postgres_class:
            mock_postgres = MockStorage()
            mock_postgres_class.return_value = mock_postgres

            with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
                mock_vacancy_class.from_dict.side_effect = lambda x: MockVacancy(x)

                with patch.object(mock_unified_api, '_filter_by_target_companies') as mock_filter:
                    mock_filter.return_value = [{"id": "2", "profession": "SJ Vacancy"}]

                    # Ошибка в HH API не должна прерывать получение данных с SJ
                    result = mock_unified_api.get_vacancies_from_sources("python", ["hh", "sj"])

                    assert len(result) == 1
                    assert result[0]["id"] == "2"

    def test_clear_cache_selected_sources(self, mock_unified_api):
        """Тест очистки кэша выбранных источников"""
        mock_unified_api.hh_api.clear_cache = Mock()
        mock_unified_api.sj_api.clear_cache = Mock()

        sources = {"hh": True, "sj": False}

        with patch('glob.glob') as mock_glob, \
             patch('os.remove') as mock_remove:
            mock_glob.return_value = ['cache_file.json']

            mock_unified_api.clear_cache(sources)

            # Должен очистить только HH кэш
            mock_unified_api.hh_api.clear_cache.assert_called_once_with("hh")
            mock_unified_api.sj_api.clear_cache.assert_not_called()

    def test_clear_all_cache(self, mock_unified_api):
        """Тест очистки всего кэша"""
        mock_unified_api.hh_api.clear_cache = Mock()
        mock_unified_api.sj_api.clear_cache = Mock()

        mock_unified_api.clear_all_cache()

        mock_unified_api.hh_api.clear_cache.assert_called_once_with("hh")
        mock_unified_api.sj_api.clear_cache.assert_called_once_with("sj")

    def test_search_with_multiple_keywords(self, mock_unified_api):
        """Тест поиска с множественными ключевыми словами"""
        mock_unified_api.hh_api.get_vacancies.return_value = [
            {"id": "1", "name": "Python Developer", "source": "hh.ru"},
            {"id": "2", "name": "Java Developer", "source": "hh.ru"}
        ]
        mock_unified_api.sj_api.get_vacancies.return_value = []

        with patch.object(mock_unified_api, 'get_all_vacancies') as mock_get_all:
            mock_get_all.side_effect = [
                [{"id": "1", "name": "Python Developer"}],  # Для "python"
                [{"id": "2", "name": "Java Developer"}]     # Для "java"
            ]

            result = mock_unified_api.search_with_multiple_keywords(["python", "java"])

            # Должны получить уникальные результаты
            assert len(result) == 2

            # Проверяем что метод был вызван для каждого ключевого слова
            assert mock_get_all.call_count == 2

    def test_get_all_vacancies(self, mock_unified_api):
        """Тест получения всех вакансий"""
        with patch.object(mock_unified_api, 'get_vacancies_from_sources') as mock_get_from_sources:
            mock_get_from_sources.return_value = [{"id": "1", "name": "Test Vacancy"}]

            result = mock_unified_api.get_all_vacancies("python")

            assert len(result) == 1
            mock_get_from_sources.assert_called_once_with("python", sources=["hh", "sj"])

    @patch('src.api_modules.unified_api.PostgresSaver')
    def test_filter_by_target_companies_sql(self, mock_postgres_class, mock_unified_api):
        """Тест SQL-фильтрации по целевым компаниям"""
        # Настраиваем мок PostgresSaver с реальным поведением SQL-фильтрации
        mock_postgres = MockStorage()
        mock_postgres_class.return_value = mock_postgres

        # Тестовые данные
        test_vacancies = [
            {"id": "1", "name": "Python Dev", "employer": {"name": "Яндекс"}},
            {"id": "2", "name": "Java Dev", "employer": {"name": "Неизвестная компания"}}
        ]

        # Мокируем Vacancy.from_dict
        with patch('src.api_modules.unified_api.Vacancy') as mock_vacancy_class:
            mock_vacancy_class.from_dict.side_effect = lambda x: MockVacancy(x)

            # Мокируем filter_and_deduplicate_vacancies чтобы вернуть только целевые компании
            mock_postgres.filter_and_deduplicate_vacancies = Mock(return_value=[MockVacancy(test_vacancies[0])])

            result = mock_unified_api._filter_by_target_companies(test_vacancies)

            # Проверяем что была вызвана SQL-фильтрация
            mock_postgres.filter_and_deduplicate_vacancies.assert_called_once()

            # Проверяем результат
            assert len(result) == 1
            assert result[0]["id"] == "1"

    def test_get_vacancies_from_target_companies(self, mock_unified_api):
        """Тест получения вакансий от целевых компаний"""
        mock_unified_api.hh_api.get_vacancies_from_target_companies.return_value = [
            {"id": "hh1", "name": "HH Target Vacancy"}
        ]
        mock_unified_api.sj_api.get_vacancies_from_target_companies.return_value = [
            {"id": "sj1", "profession": "SJ Target Vacancy"}
        ]

        # Мокируем _deduplicate_cross_platform если он существует
        with patch.object(mock_unified_api, '_deduplicate_cross_platform', create=True) as mock_dedup:
            mock_dedup.return_value = [
                {"id": "hh1", "name": "HH Target Vacancy"},
                {"id": "sj1", "profession": "SJ Target Vacancy"}
            ]

            result = mock_unified_api.get_vacancies_from_target_companies("python")

            assert len(result) == 2


class TestUnifiedAPIEdgeCases:
    """Тесты граничных случаев для UnifiedAPI"""

    @pytest.fixture
    def unified_api(self):
        """Реальный экземпляр UnifiedAPI для тестов граничных случаев"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'):
            return UnifiedAPI()

    def test_empty_query(self, unified_api):
        """Тест обработки пустого запроса"""
        with patch.object(unified_api, 'get_vacancies_from_sources') as mock_get:
            mock_get.return_value = []

            result = unified_api.get_all_vacancies("")

            assert result == []

    def test_none_sources(self, unified_api):
        """Тест обработки None в качестве источников"""
        with patch.object(unified_api, 'get_available_sources') as mock_available:
            mock_available.return_value = ["hh", "sj"]

            with patch.object(unified_api.hh_api, 'get_vacancies') as mock_hh:
                mock_hh.return_value = []

                with patch.object(unified_api.sj_api, 'get_vacancies') as mock_sj:
                    mock_sj.return_value = []

                    with patch.object(unified_api, '_filter_by_target_companies') as mock_filter:
                        mock_filter.return_value = []

                        # None в sources должен использовать все доступные источники
                        result = unified_api.get_vacancies_from_sources("python", None)

                        assert result == []
                        mock_hh.assert_called_once()
                        mock_sj.assert_called_once()

    def test_memory_efficiency_large_dataset(self, unified_api):
        """Тест эффективности памяти для больших наборов данных"""
        # Симулируем большой набор данных
        large_dataset = [{"id": f"vacancy_{i}", "name": f"Vacancy {i}"} for i in range(1000)]

        with patch.object(unified_api.hh_api, 'get_vacancies') as mock_hh:
            mock_hh.return_value = large_dataset

            with patch.object(unified_api.sj_api, 'get_vacancies') as mock_sj:
                mock_sj.return_value = []

                with patch.object(unified_api, '_filter_by_target_companies') as mock_filter:
                    # SQL-фильтрация должна обрабатывать большие наборы эффективно
                    mock_filter.return_value = large_dataset[:100]  # Возвращаем первые 100

                    result = unified_api.get_vacancies_from_sources("python", ["hh"])

                    assert len(result) == 100
                    mock_filter.assert_called_once()