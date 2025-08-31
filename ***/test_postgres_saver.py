"""
Оптимизированные тесты для PostgresSaver с единым подключением к БД
"""

from unittest.mock import Mock, patch

import pytest

from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy


class TestPostgresSaverOptimized:
    """Оптимизированные тесты для PostgresSaver"""

    def test_postgres_saver_initialization(self, global_external_resource_isolation):
        """Тест инициализации PostgresSaver"""
        # Мокируем методы инициализации
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ):

            storage = PostgresSaver()
            assert storage is not None

    def test_vacancy_save_operations(self, global_external_resource_isolation, sample_vacancy):
        """Тест операций сохранения вакансий"""
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "add_vacancy_batch_optimized", return_value=["Success"]):

            storage = PostgresSaver()

            # Тестируем сохранение одной вакансии
            result = storage.add_vacancy(sample_vacancy)
            assert isinstance(result, bool)

            # Тестируем сохранение списка вакансий
            batch_result = storage.add_vacancies([sample_vacancy])
            assert isinstance(batch_result, list)

            # Тестируем метод save_vacancies
            save_result = storage.save_vacancies([sample_vacancy])
            assert isinstance(save_result, int)

    def test_vacancy_retrieval_operations(self, global_external_resource_isolation):
        """Тест операций получения вакансий"""
        mock_vacancy_data = [
            {
                "vacancy_id": "test_1",
                "title": "Test Vacancy",
                "url": "https://test.com/vacancy/1",
                "salary_from": 100000,
                "salary_to": 150000,
                "salary_currency": "RUR",
                "description": "Test description",
                "company_name": "Test Company",
            }
        ]

        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "_get_connection") as mock_get_conn:

            # Настраиваем мок подключения и курсора
            mock_conn = global_external_resource_isolation["db_connection"]
            mock_get_conn.return_value = mock_conn

            # Мокируем результат запроса
            mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = mock_vacancy_data

            storage = PostgresSaver()
            vacancies = storage.get_vacancies()

            assert isinstance(vacancies, list)

    def test_vacancy_deletion_operations(self, global_external_resource_isolation):
        """Тест операций удаления вакансий"""
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "_get_connection") as mock_get_conn:

            # Настраиваем мок для успешного удаления
            mock_conn = global_external_resource_isolation["db_connection"]
            mock_conn.cursor.return_value.rowcount = 1
            mock_get_conn.return_value = mock_conn

            storage = PostgresSaver()

            # Тестируем удаление по ID
            delete_result = storage.delete_vacancy_by_id("test_1")
            assert isinstance(delete_result, bool)

    def test_vacancy_count_operations(self, global_external_resource_isolation):
        """Тест операций подсчета вакансий"""
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "_get_connection") as mock_get_conn:

            # Настраиваем мок для возврата количества
            mock_conn = global_external_resource_isolation["db_connection"]
            mock_conn.cursor.return_value.fetchone.return_value = (42,)
            mock_get_conn.return_value = mock_conn

            storage = PostgresSaver()
            count = storage.get_vacancies_count()

            assert isinstance(count, int)

    def test_vacancy_existence_check(self, global_external_resource_isolation, sample_vacancy):
        """Тест проверки существования вакансии"""
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "_get_connection") as mock_get_conn:

            # Настраиваем мок для проверки существования
            mock_conn = global_external_resource_isolation["db_connection"]
            mock_conn.cursor.return_value.fetchone.return_value = (1,)
            mock_get_conn.return_value = mock_conn

            storage = PostgresSaver()
            exists = storage.is_vacancy_exists(sample_vacancy)

            assert isinstance(exists, bool)

    def test_batch_operations_optimization(self, global_external_resource_isolation, sample_vacancy):
        """Тест оптимизированных batch операций"""
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "_get_connection") as mock_get_conn:

            # Настраиваем мок для batch операций
            mock_conn = global_external_resource_isolation["db_connection"]
            mock_conn.cursor.return_value.rowcount = 5
            mock_get_conn.return_value = mock_conn

            storage = PostgresSaver()

            # Тестируем batch операции
            batch_vacancies = [sample_vacancy] * 5
            result = storage.add_vacancy_batch_optimized(batch_vacancies)

            assert isinstance(result, list)

    def test_error_handling_in_storage_operations(self, global_external_resource_isolation):
        """Тест обработки ошибок в операциях хранилища"""
        with patch.object(PostgresSaver, "_ensure_database_exists"), patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ), patch.object(PostgresSaver, "_get_connection", side_effect=Exception("Connection error")):

            storage = PostgresSaver()

            # Тестируем обработку ошибок при получении вакансий
            vacancies = storage.get_vacancies()
            assert isinstance(vacancies, list)
            assert len(vacancies) == 0  # При ошибке должен возвращать пустой список

    def test_database_table_management(self, global_external_resource_isolation):
        """Тест управления таблицами БД"""
        with patch.object(PostgresSaver, "_ensure_database_exists") as mock_ensure_db, patch.object(
            PostgresSaver, "_ensure_tables_exist"
        ) as mock_ensure_tables:

            storage = PostgresSaver()

            # Проверяем что методы инициализации были вызваны
            mock_ensure_db.assert_called_once()
            mock_ensure_tables.assert_called_once()
