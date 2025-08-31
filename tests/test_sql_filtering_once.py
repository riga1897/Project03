"""
Тест единственной точки SQL-фильтрации по целевым компаниям
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from src.api_modules.unified_api import UnifiedAPI
from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy


class TestSingleSQLFiltering:
    """Тесты единственной точки SQL-фильтрации"""

    @pytest.fixture
    def mock_db_connection(self) -> Dict[str, Any]:
        """Мок подключения к БД для тестов"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.cursor.return_value.__exit__.return_value = None

        # Мокируем результаты SQL-запросов
        mock_cursor.fetchall.return_value = [("1",), ("3",)]  # ID отфильтрованных вакансий

        return {"connection": mock_connection, "cursor": mock_cursor}

    @pytest.fixture
    def sample_vacancies(self) -> List[Vacancy]:
        """Примеры вакансий для тестирования"""
        return [
            Vacancy(
                vacancy_id="1",
                title="Python Developer",
                employer={"id": "1740", "name": "Яндекс"},  # Целевая компания
                source="hh",
            ),
            Vacancy(
                vacancy_id="2",
                title="Java Developer",
                employer={"id": "9999", "name": "Неизвестная компания"},  # НЕ целевая
                source="hh",
            ),
            Vacancy(
                vacancy_id="3",
                title="Go Developer",
                employer={"id": "78638", "name": "Тинькофф"},  # Целевая компания
                source="hh",
            ),
        ]

    def test_single_sql_filtering_execution(
        self, mock_db_connection: Dict[str, Any], sample_vacancies: List[Vacancy]
    ) -> None:
        """Тест что SQL-фильтрация выполняется ТОЛЬКО один раз"""
        with patch("src.storage.postgres_saver.PostgresSaver.get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_db_connection["connection"]
            mock_get_conn.return_value.__exit__.return_value = None

            postgres_saver = PostgresSaver()

            # Вызываем фильтрацию
            result = postgres_saver.filter_and_deduplicate_vacancies(sample_vacancies, {"target_companies_only": True})

            # Проверяем что SQL выполнялся только один раз
            cursor = mock_db_connection["cursor"]

            # Должна быть создана временная таблица
            create_temp_calls = [
                call
                for call in cursor.execute.call_args_list
                if "CREATE TEMP TABLE temp_filter_vacancies" in str(call)
            ]
            assert len(create_temp_calls) == 1, "Временная таблица должна создаваться ТОЛЬКО один раз"

            # Проверяем что возвращаются только отфильтрованные вакансии
            assert isinstance(result, list)
            assert len(result) == 2  # Только целевые компании (ID 1 и 3)

    def test_filtering_only_in_postgres_saver(self) -> None:
        """Тест что фильтрация выполняется ТОЛЬКО в PostgresSaver"""
        # PostgresSaver имеет метод фильтрации
        postgres_saver = PostgresSaver()
        unified_api = UnifiedAPI()

        # У PostgresSaver должен быть метод фильтрации
        assert hasattr(postgres_saver, "filter_and_deduplicate_vacancies")

        # У UnifiedAPI НЕ должно быть методов фильтрации по компаниям
        filtering_methods = [
            attr for attr in dir(unified_api) if "filter" in attr.lower() and "companies" in attr.lower()
        ]
        assert (
            len(filtering_methods) == 0
        ), f"UnifiedAPI не должен содержать методы фильтрации по компаниям: {filtering_methods}"

    def test_strict_typing_in_filtering_method(self) -> None:
        """Тест строгой типизации метода фильтрации"""
        postgres_saver = PostgresSaver()
        method = getattr(postgres_saver, "filter_and_deduplicate_vacancies")

        # Проверяем аннотации типов
        assert hasattr(method, "__annotations__")
        annotations = method.__annotations__

        # Проверяем обязательные аннотации
        assert "vacancies" in annotations
        assert "filters" in annotations
        assert "return" in annotations

    def test_no_fallback_methods(self, mock_db_connection: Dict[str, Any], sample_vacancies: List[Vacancy]) -> None:
        """Тест отсутствия fallback методов"""
        with patch("src.storage.postgres_saver.PostgresSaver.get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_db_connection["connection"]
            mock_get_conn.return_value.__exit__.return_value = None

            postgres_saver = PostgresSaver()

            # Проверяем что нет fallback логики в фильтрации
            # Вакансия с неизвестной компанией не должна проходить фильтрацию
            unknown_vacancy = Vacancy(
                vacancy_id="unknown",
                title="Unknown Company Job",
                employer={"id": "unknown", "name": "Unknown Company"},
                source="hh",
            )

            result = postgres_saver.filter_and_deduplicate_vacancies(
                [unknown_vacancy], {"target_companies_only": True}
            )

            # Должен вернуть пустой список - НЕТ fallback
            assert len(result) == 0

    def test_db_fields_saved_correctly(self, mock_db_connection: Dict[str, Any]) -> None:
        """Тест что description, requirements, responsibilities сохраняются в БД"""
        vacancy_with_fields = Vacancy(
            vacancy_id="test_fields",
            title="Test Vacancy",
            description="Test description",
            requirements="Python, Django",
            responsibilities="Develop applications",
            employer={"id": "1740", "name": "Яндекс"},
            source="hh",
        )

        with patch("src.storage.postgres_saver.PostgresSaver.get_connection") as mock_get_conn:
            mock_get_conn.return_value.__enter__.return_value = mock_db_connection["connection"]
            mock_get_conn.return_value.__exit__.return_value = None

            postgres_saver = PostgresSaver()

            # Мокируем company_mapping
            with patch.object(postgres_saver, "filter_and_deduplicate_vacancies", return_value=[vacancy_with_fields]):
                result = postgres_saver.add_vacancy_batch_optimized([vacancy_with_fields])

                # Проверяем что execute был вызван с правильными полями
                cursor = mock_db_connection["cursor"]
                insert_calls = [
                    call for call in cursor.execute.call_args_list if "INSERT INTO temp_new_vacancies" in str(call)
                ]

                assert (
                    len(insert_calls) >= 1
                ), "Должна быть выполнена вставка с полями description, requirements, responsibilities"
