"""
Тесты для классов хранения данных
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from src.storage.json_saver import JSONSaver
from src.storage.postgres_saver import PostgresSaver
from src.vacancies.models import Vacancy


class TestJSONSaver:
    """Тесты для JSONSaver"""

    def test_add_vacancy_to_empty_file(self, temp_json_file, sample_vacancy):
        """Тест добавления вакансии в пустой файл"""
        saver = JSONSaver(temp_json_file)
        messages = saver.add_vacancy(sample_vacancy)

        assert len(messages) == 1
        assert "Добавлена новая вакансия" in messages[0]

        # Проверяем, что файл содержит вакансию
        with open(temp_json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['vacancy_id'] == '12345'

    def test_add_duplicate_vacancy(self, temp_json_file, sample_vacancy):
        """Тест добавления дублирующейся вакансии"""
        saver = JSONSaver(temp_json_file)

        # Добавляем вакансию первый раз
        saver.add_vacancy(sample_vacancy)

        # Добавляем ту же вакансию снова
        messages = saver.add_vacancy(sample_vacancy)

        # Должно быть сообщение об обновлении
        assert any("обновлена" in msg for msg in messages)

        # В файле должна быть только одна вакансия
        vacancies = saver.get_vacancies()
        assert len(vacancies) == 1

    def test_get_vacancies_empty_file(self, temp_json_file):
        """Тест получения вакансий из пустого файла"""
        saver = JSONSaver(temp_json_file)
        vacancies = saver.get_vacancies()

        assert vacancies == []

    def test_delete_vacancy_by_id(self, temp_json_file, sample_vacancies):
        """Тест удаления вакансии по ID"""
        saver = JSONSaver(temp_json_file)
        saver.add_vacancy(sample_vacancies)

        # Удаляем первую вакансию
        result = saver.delete_vacancy_by_id("12345")

        assert result is True

        remaining_vacancies = saver.get_vacancies()
        assert len(remaining_vacancies) == 1
        assert remaining_vacancies[0].vacancy_id == "67890"

    def test_delete_nonexistent_vacancy(self, temp_json_file, sample_vacancy):
        """Тест удаления несуществующей вакансии"""
        saver = JSONSaver(temp_json_file)
        saver.add_vacancy(sample_vacancy)

        result = saver.delete_vacancy_by_id("nonexistent")

        assert result is False
        assert len(saver.get_vacancies()) == 1

    def test_delete_all_vacancies(self, temp_json_file, sample_vacancies):
        """Тест удаления всех вакансий"""
        saver = JSONSaver(temp_json_file)
        saver.add_vacancy(sample_vacancies)

        result = saver.delete_all_vacancies()

        assert result is True
        assert len(saver.get_vacancies()) == 0

    def test_file_size_calculation(self, temp_json_file, sample_vacancy):
        """Тест вычисления размера файла"""
        saver = JSONSaver(temp_json_file)

        # Пустой файл
        size_empty = saver.get_file_size()
        assert size_empty >= 0

        # Файл с вакансией
        saver.add_vacancy(sample_vacancy)
        size_with_data = saver.get_file_size()
        assert size_with_data > size_empty


class TestPostgresSaver:
    """Тесты для PostgresSaver"""

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_connection_creation(self, mock_connect):
        """Тест создания подключения к БД"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver(config)
            connection = saver._get_connection()

        assert connection == mock_connection

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_add_vacancy_success(self, mock_connect, sample_vacancy):
        """Тест успешного добавления вакансии"""
        # Настраиваем мок-объекты
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  # Нет существующих вакансий

        # Создаем PostgresSaver с мок-конфигурацией
        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({'host': 'localhost', 'database': 'test'})

        messages = saver.add_vacancy(sample_vacancy)

        assert len(messages) == 1
        assert "Добавлена новая вакансия" in messages[0]
        mock_connection.commit.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_get_vacancies_count(self, mock_connect):
        """Тест подсчета количества вакансий"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [42]

        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({'host': 'localhost', 'database': 'test'})

        count = saver.get_vacancies_count()

        assert count == 42

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_delete_vacancy_by_id_success(self, mock_connect):
        """Тест успешного удаления вакансии по ID"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Одна строка удалена

        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({'host': 'localhost', 'database': 'test'})

        result = saver.delete_vacancy_by_id("12345")

        assert result is True
        mock_connection.commit.assert_called()

    @patch('src.storage.postgres_saver.psycopg2.connect')
    def test_delete_vacancy_by_id_not_found(self, mock_connect):
        """Тест удаления несуществующей вакансии"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0  # Ничего не удалено

        with patch.object(PostgresSaver, '_ensure_database_exists'), \
             patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({'host': 'localhost', 'database': 'test'})

        result = saver.delete_vacancy_by_id("nonexistent")

        assert result is False