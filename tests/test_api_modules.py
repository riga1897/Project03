from unittest.mock import MagicMock, Mock, patch

import pytest

from src.api_modules.base_api import BaseJobAPI
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI
from src.api_modules.unified_api import UnifiedAPI
from src.config.api_config import APIConfig


class MockVacancy:
    """Мок для тестирования"""

    def __init__(self, data):
        self.data = data
        self.vacancy_id = data.get("id", data.get("vacancy_id"))
        self.title = data.get("name", data.get("title", ""))
        self.url = data.get("alternate_url", data.get("url", ""))

    @classmethod
    def from_dict(cls, data):
        return cls(data)

    def to_dict(self):
        return self.data


class MockPostgresSaver:
    """Мок для PostgresSaver с SQL-дедупликацией"""

    def __init__(self):
        self.saved_vacancies = []

    def filter_and_deduplicate_vacancies(self, vacancies, filters=None):
        """Мок SQL-дедупликации"""
        if not vacancies:
            return []

        # Простая дедупликация по vacancy_id для тестов
        seen_ids = set()
        unique_vacancies = []

        for vacancy in vacancies:
            vacancy_id = getattr(vacancy, "vacancy_id", None)
            if vacancy_id and vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                unique_vacancies.append(vacancy)

        return unique_vacancies

    def add_vacancy(self, vacancies):
        if not isinstance(vacancies, list):
            vacancies = [vacancies]
        self.saved_vacancies.extend(vacancies)
        return [f"Сохранена вакансия {v.vacancy_id}" for v in vacancies]


class TestHeadHunterAPI:
    """Тесты для HeadHunterAPI"""

    @pytest.fixture
    def hh_api(self):
        """Создает экземпляр HeadHunterAPI для тестов"""
        with patch("src.api_modules.hh_api.APIConnector"):
            return HeadHunterAPI()

    def test_api_initialization(self, hh_api):
        """Тест инициализации API"""
        assert hh_api is not None
        assert hasattr(hh_api, "BASE_URL")
        assert hasattr(hh_api, "connector")

    def test_validate_vacancy_valid(self, hh_api):
        """Тест валидации корректной вакансии"""
        valid_vacancy = {"name": "Python Developer", "alternate_url": "https://hh.ru/vacancy/123"}
        assert hh_api._validate_vacancy(valid_vacancy) is True

    def test_validate_vacancy_invalid(self, hh_api):
        """Тест валидации некорректной вакансии"""
        invalid_vacancy = {"id": "123"}  # Нет обязательных полей
        assert hh_api._validate_vacancy(invalid_vacancy) is False

    @patch("src.api_modules.hh_api.CachedAPI._CachedAPI__connect_to_api")
    def test_get_vacancies_page(self, mock_connect, hh_api):
        """Тест получения одной страницы вакансий"""
        mock_connect.return_value = {
            "items": [{"id": "1", "name": "Test Vacancy", "alternate_url": "https://test.com"}]
        }

        result = hh_api.get_vacancies_page("python", 0)

        assert len(result) == 1
        assert result[0]["source"] == "hh.ru"

    @patch("src.api_modules.hh_api.CachedAPI._CachedAPI__connect_to_api")
    def test_get_vacancies(self, mock_connect, hh_api):
        """Тест получения вакансий"""
        # Мокируем ответы API
        mock_connect.side_effect = [
            {"found": 50, "pages": 1, "items": []},  # Первый запрос для метаданных
            {
                "items": [
                    {"id": "1", "name": "Python Dev", "alternate_url": "https://test1.com"},
                    {"id": "2", "name": "Java Dev", "alternate_url": "https://test2.com"},
                ]
            },
        ]

        with patch.object(hh_api, "get_vacancies_page") as mock_page:
            mock_page.return_value = [
                {"id": "1", "name": "Python Dev", "alternate_url": "https://test1.com", "source": "hh.ru"},
                {"id": "2", "name": "Java Dev", "alternate_url": "https://test2.com", "source": "hh.ru"},
            ]

            result = hh_api.get_vacancies("python")

            assert len(result) == 2
            assert all(v["source"] == "hh.ru" for v in result)


class TestSuperJobAPI:
    """Тесты для SuperJobAPI"""

    @pytest.fixture
    def sj_api(self):
        """Создает экземпляр SuperJobAPI для тестов"""
        with patch("src.api_modules.sj_api.APIConnector"):
            return SuperJobAPI()

    def test_api_initialization(self, sj_api):
        """Тест инициализации API"""
        assert sj_api is not None
        assert hasattr(sj_api, "BASE_URL")

    def test_validate_vacancy_valid(self, sj_api):
        """Тест валидации корректной вакансии"""
        valid_vacancy = {"profession": "Python Developer", "link": "https://superjob.ru/vacancy/123"}
        assert sj_api._validate_vacancy(valid_vacancy) is True

    def test_validate_vacancy_invalid(self, sj_api):
        """Тест валидации некорректной вакансии"""
        invalid_vacancy = {"id": "123"}
        assert sj_api._validate_vacancy(invalid_vacancy) is False


class TestUnifiedAPI:
    """Тесты для UnifiedAPI"""

    @pytest.fixture
    def unified_api(self):
        """Создает экземпляр UnifiedAPI для тестов"""
        with patch("src.api_modules.unified_api.HeadHunterAPI") as mock_hh, patch(
            "src.api_modules.unified_api.SuperJobAPI"
        ) as mock_sj:

            api = UnifiedAPI()
            api.hh_api = mock_hh.return_value
            api.sj_api = mock_sj.return_value
            return api

    def test_get_available_sources(self, unified_api):
        """Тест получения доступных источников"""
        sources = unified_api.get_available_sources()
        assert "hh" in sources
        assert "sj" in sources

    def test_validate_sources(self, unified_api):
        """Тест валидации источников"""
        valid_sources = unified_api.validate_sources(["hh", "sj"])
        assert valid_sources == ["hh", "sj"]

        invalid_sources = unified_api.validate_sources(["invalid"])
        assert invalid_sources == ["hh", "sj"]  # Возвращает все доступные

    def test_get_vacancies_from_sources(self, unified_api):
        """Тест получения вакансий из источников с мокированием методов API"""
        # Мокируем результаты API
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "name": "HH Vacancy", "source": "hh.ru"}]
        unified_api.sj_api.get_vacancies.return_value = [
            {"id": "2", "profession": "SJ Vacancy", "source": "superjob.ru"}
        ]

        # Мокируем _filter_by_target_companies для возврата отфильтрованных данных
        with patch.object(unified_api, "_filter_by_target_companies") as mock_filter:
            mock_filter.return_value = [{"id": "1", "name": "Filtered Vacancy"}]

            result = unified_api.get_vacancies_from_sources("python", ["hh", "sj"])

            assert len(result) == 1
            assert result[0]["id"] == "1"

            # Проверяем вызовы API
            unified_api.hh_api.get_vacancies.assert_called_once()
            unified_api.sj_api.get_vacancies.assert_called_once()

            # Проверяем что была вызвана фильтрация
            mock_filter.assert_called_once()

    def test_get_vacancies_from_source(self, unified_api):
        """Тест получения вакансий из конкретного источника"""
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "name": "Test Vacancy"}]

        result = unified_api.get_vacancies_from_source("python", "hh")

        assert len(result) == 1
        unified_api.hh_api.get_vacancies.assert_called_once_with(search_query="python")

    def test_clear_cache(self, unified_api):
        """Тест очистки кэша"""
        sources = {"hh": True, "sj": False}

        # Мокируем методы очистки кэша
        unified_api.hh_api.clear_cache = Mock()
        unified_api.sj_api.clear_cache = Mock()

        with patch("glob.glob") as mock_glob, patch("os.remove") as mock_remove:
            mock_glob.return_value = ["cache_file1.json", "cache_file2.json"]

            unified_api.clear_cache(sources)

            unified_api.hh_api.clear_cache.assert_called_once_with("hh")
            unified_api.sj_api.clear_cache.assert_not_called()


class TestBaseJobAPI:
    """Тесты для BaseJobAPI"""

    def test_abstract_class(self):
        """Тест что BaseJobAPI является абстрактным классом"""
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_clear_cache_method(self):
        """Тест метода очистки кэша"""

        class ConcreteAPI(BaseJobAPI):
            def get_vacancies(self, search_query: str, **kwargs):
                return []

            def _validate_vacancy(self, vacancy):
                return True

        api = ConcreteAPI()

        with patch("os.path.exists") as mock_exists, patch("shutil.rmtree") as mock_rmtree, patch(
            "os.makedirs"
        ) as mock_makedirs:

            mock_exists.return_value = True

            api.clear_cache("test")

            mock_rmtree.assert_called_once()
            mock_makedirs.assert_called_once()


class TestAPIIntegration:
    """Интеграционные тесты для API модулей"""

    def test_end_to_end_workflow(self):
        """Тест полного workflow получения и обработки вакансий"""
        with patch("src.api_modules.unified_api.HeadHunterAPI") as mock_hh, patch(
            "src.api_modules.unified_api.SuperJobAPI"
        ) as mock_sj:

            # Настраиваем моки API
            mock_hh_instance = Mock()
            mock_sj_instance = Mock()
            mock_hh.return_value = mock_hh_instance
            mock_sj.return_value = mock_sj_instance

            mock_hh_instance.get_vacancies.return_value = [
                {"id": "hh1", "name": "Python Dev", "source": "hh.ru"},
                {"id": "hh2", "name": "Java Dev", "source": "hh.ru"},
            ]

            mock_sj_instance.get_vacancies.return_value = [
                {"id": "sj1", "profession": "Python Dev", "source": "superjob.ru"}
            ]

            # Создаем UnifiedAPI
            unified_api = UnifiedAPI()

            # Мокируем фильтрацию
            with patch.object(unified_api, "_filter_by_target_companies") as mock_filter:
                mock_filter.return_value = [{"id": "hh1", "name": "Python Dev", "filtered": True}]

                # Выполняем тест
                result = unified_api.get_vacancies_from_sources("python")

                # Проверяем результат
                assert len(result) == 1
                assert result[0]["filtered"] is True

                # Проверяем что вызвались правильные методы
                mock_hh_instance.get_vacancies.assert_called_once()
                mock_sj_instance.get_vacancies.assert_called_once()
                mock_filter.assert_called_once()

    def test_error_handling(self):
        """Тест обработки ошибок"""
        with patch("src.api_modules.unified_api.HeadHunterAPI") as mock_hh:
            mock_hh_instance = Mock()
            mock_hh.return_value = mock_hh_instance
            mock_hh_instance.get_vacancies.side_effect = Exception("API Error")

            unified_api = UnifiedAPI()

            # Ошибка API не должна прерывать выполнение
            result = unified_api.get_vacancies_from_sources("python", ["hh"])

            # Должен вернуть пустой список при ошибке
            assert result == []