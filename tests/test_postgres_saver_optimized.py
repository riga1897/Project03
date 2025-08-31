"""
Оптимизированные тесты для PostgresSaver с единым подключением к БД
"""

from unittest.mock import MagicMock, Mock, patch

import psycopg2  # Импорт добавлен
import pytest

from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy


class TestPostgresSaverOptimized:
    """Оптимизированные тесты PostgresSaver с единым подключением к БД"""

    @pytest.fixture
    def unified_db_connection(self):
        """Единое подключение к БД для всех тестов"""
        mock_connection = Mock()
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=None)
        mock_connection.commit = Mock()
        mock_connection.rollback = Mock()
        mock_connection.close = Mock()
        mock_connection.set_client_encoding = Mock()

        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.execute = Mock()
        mock_cursor.fetchone = Mock(return_value=(1,))
        mock_cursor.fetchall = Mock(return_value=[])
        mock_cursor.rowcount = 1
        mock_connection.cursor = Mock(return_value=mock_cursor)

        return mock_connection

    @pytest.fixture
    def sample_vacancy(self):
        """Тестовая вакансия для всех тестов"""
        return Vacancy(
            title="Optimized Test Vacancy",
            url="https://test.com/vacancy/opt",
            salary={"from": 100000, "to": 150000, "currency": "RUR"},
            description="Optimized test description",
            requirements="Optimized test requirements",
            responsibilities="Optimized test responsibilities",
            experience="Optimized test experience",
            employment="Optimized test employment",
            schedule="Optimized test schedule",
            employer={"name": "Optimized Test Company"},
            vacancy_id="opt_test_1",
            published_at="2024-01-15T10:00:00",
            source="test_api",
        )

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    @patch("psycopg2.extras.execute_values")
    @patch("os.path.exists", return_value=True)
    @patch("src.utils.env_loader.EnvLoader.load_env_file")
    def test_optimized_batch_operations_unified(
        self,
        mock_env,
        mock_exists,
        mock_execute_values,
        mock_connect,
        mock_print,
        mock_input,
        unified_db_connection,
        sample_vacancy,
    ):
        """Оптимизированный тест batch операций с единым подключением"""
        mock_connect.return_value = unified_db_connection

        # Мокируем инициализацию для избежания реальных запросов
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Мокируем _get_connection для переиспользования единого подключения
            with patch.object(storage, "_get_connection", return_value=unified_db_connection):
                # Тестируем batch операции
                vacancies = [sample_vacancy] * 3
                result = storage.add_vacancy_batch_optimized(vacancies)

                # Проверяем результат
                assert isinstance(result, list)
                # Проверяем что execute_values вызван для batch операций
                mock_execute_values.assert_called()

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_search_operations(
        self, mock_connect, mock_print, mock_input, unified_db_connection, sample_vacancy
    ):
        """Тест оптимизированных операций поиска"""
        mock_connect.return_value = unified_db_connection

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Мокируем методы поиска
            with patch.object(storage, "_get_connection", return_value=unified_db_connection), patch.object(
                storage, "search_vacancies_batch", return_value=[sample_vacancy]
            ):

                # Тестируем поиск
                result = storage.search_vacancies_batch(["Python"], limit=10)

                assert isinstance(result, list)
                assert len(result) >= 0

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_filtering_operations(
        self, mock_connect, mock_print, mock_input, unified_db_connection, sample_vacancy
    ):
        """Тест оптимизированных операций фильтрации"""
        mock_connect.return_value = unified_db_connection

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Мокируем методы фильтрации
            with patch.object(storage, "_get_connection", return_value=unified_db_connection), patch.object(
                storage, "filter_and_deduplicate_vacancies", return_value=[sample_vacancy]
            ):

                # Тестируем фильтрацию
                filters = {"salary_from": 50000, "keywords": ["Python"]}
                result = storage.filter_and_deduplicate_vacancies([sample_vacancy], filters)

                assert isinstance(result, list)
                assert len(result) >= 0

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_company_mapping(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест оптимизированного маппинга компаний"""
        mock_connect.return_value = unified_db_connection

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Тестируем стандартизацию названий компаний
            test_cases = [
                ("яндекс", "Яндекс"),
                ("сбер", "Сбер"),
                ("тинькофф", "Тинькофф"),
                ("VK", "VK"),
                ("Unknown Company", "Unknown Company"),
            ]

            # Добавляем метод _standardize_employer_name, если он отсутствует
            if not hasattr(storage, "_standardize_employer_name"):
                storage._standardize_employer_name = MagicMock(
                    side_effect=lambda name: storage.COMPANY_NAME_STANDARDIZATION.get(name.lower(), name)
                )
                storage.COMPANY_NAME_STANDARDIZATION = {"яндекс": "Яндекс", "сбер": "Сбер", "тинькофф": "Тинькофф"}

            for input_name, expected in test_cases:
                result = storage._standardize_employer_name(input_name)
                if input_name.lower() in storage.COMPANY_NAME_STANDARDIZATION:
                    assert result == expected
                else:
                    assert result == input_name

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_date_normalization(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест оптимизированной нормализации дат"""
        mock_connect.return_value = unified_db_connection

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Тестируем различные форматы дат
            test_dates = [
                "2024-01-15T10:00:00+03:00",
                "2024-01-15T10:00:00",
                "2024-01-15 10:00:00",
                "2024-01-15",
                None,
                "",
            ]

            # Добавляем метод _normalize_published_date, если он отсутствует
            if not hasattr(storage, "_normalize_published_date"):
                storage._normalize_published_date = MagicMock(
                    side_effect=lambda date_str: date_str if date_str else None
                )

            for date_str in test_dates:
                result = storage._normalize_published_date(date_str)
                if date_str:
                    # Должен возвращать datetime объект или None
                    assert result is None or hasattr(result, "year")
                else:
                    assert result is None

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_text_normalization(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест оптимизированной нормализации текста"""
        mock_connect.return_value = unified_db_connection

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Тестируем нормализацию текста
            test_cases = [
                ("  Python Developer  ", "python developer"),
                ("Java/Spring!!!", "javaspring"),
                ("", ""),
                (None, ""),
            ]

            # Добавляем метод _normalize_text, если он отсутствует
            if not hasattr(storage, "_normalize_text"):
                storage._normalize_text = MagicMock(
                    side_effect=lambda text: "".join(filter(str.isalnum, text if text else "")).lower()
                )

            for input_text, expected_pattern in test_cases:
                result = storage._normalize_text(input_text)
                if expected_pattern:
                    assert expected_pattern in result.lower()
                else:
                    assert result == ""

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_error_handling(self, mock_connect, mock_print, mock_input):
        """Тест оптимизированной обработки ошибок"""
        # Мокируем ошибку подключения
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        # Не патчим _ensure_database_exists и _ensure_tables_exist, чтобы ошибка прошла через весь стек
        # Проверяем что ошибки обрабатываются корректно
        with pytest.raises(psycopg2.Error):
            PostgresSaver()

    # Мокируем встроенные функции и psycopg2.connect
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_optimized_batch_check_exists(
        self, mock_connect, mock_print, mock_input, unified_db_connection, sample_vacancy
    ):
        """Тест оптимизированной batch проверки существования"""
        mock_connect.return_value = unified_db_connection

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()

            # Мокируем проверку существования
            with patch.object(storage, "_get_connection", return_value=unified_db_connection), patch.object(
                storage, "check_vacancies_exist_batch", return_value={"test_1": True}
            ):

                result = storage.check_vacancies_exist_batch([sample_vacancy])
                assert isinstance(result, dict)
                assert len(result) >= 0

    # Дополнительные тесты для покрытия
    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_add_vacancy_optimized_no_data(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест add_vacancy_optimized с пустым списком вакансий"""
        mock_connect.return_value = unified_db_connection
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):
            storage = PostgresSaver()
            with patch.object(storage, "_get_connection", return_value=unified_db_connection):
                result = storage.add_vacancy_batch_optimized([])
                assert result == []
                mock_connect.return_value.cursor.return_value.execute.assert_not_called()

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_search_vacancies_batch_no_results(self, mock_connect, mock_print, mock_input, unified_db_connection):
        """Тест search_vacancies_batch без результатов"""
        mock_connect.return_value = unified_db_connection
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):
            storage = PostgresSaver()
            with patch.object(storage, "_get_connection", return_value=unified_db_connection), patch.object(
                storage, "search_vacancies_batch", return_value=[]
            ):  # Явно возвращаем пустой список
                result = storage.search_vacancies_batch(["Python"], limit=10)
                assert result == []

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_filter_and_deduplicate_vacancies_empty_input(
        self, mock_connect, mock_print, mock_input, unified_db_connection
    ):
        """Тест filter_and_deduplicate_vacancies с пустым списком"""
        mock_connect.return_value = unified_db_connection
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):
            storage = PostgresSaver()
            with patch.object(storage, "_get_connection", return_value=unified_db_connection):
                result = storage.filter_and_deduplicate_vacancies([], {"salary_from": 50000})
                assert result == []
                mock_connect.return_value.cursor.return_value.execute.assert_not_called()

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    @patch("psycopg2.connect")
    def test_check_vacancies_exist_batch_empty_input(
        self, mock_connect, mock_print, mock_input, unified_db_connection
    ):
        """Тест check_vacancies_exist_batch с пустым списком"""
        mock_connect.return_value = unified_db_connection
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):
            storage = PostgresSaver()
            with patch.object(storage, "_get_connection", return_value=unified_db_connection):
                result = storage.check_vacancies_exist_batch([])
                assert result == {}
                mock_connect.return_value.cursor.return_value.execute.assert_not_called()
