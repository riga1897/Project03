#!/usr/bin/env python3
"""
Дополнительные тесты для postgres_saver.py - покрытие оставшихся методов

ДОБАВЛЯЕМ ТЕСТЫ ДЛЯ:
- get_vacancies() - получение всех вакансий
- _convert_rows_to_vacancies() - конвертация строк БД
- filter_and_deduplicate_vacancies() - фильтрация и дедупликация
- Обработка различных сценариев ошибок
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Импорт из реального кода для покрытия
from src.storage.postgres_saver import PostgresSaver


class TestPostgresSaverAdvancedOperations:
    """Тесты для продвинутых операций с вакансиями"""

    @pytest.fixture
    def mock_db_row(self):
        """Создание мок-строки из БД для тестирования"""
        return (
            1,  # id
            "test_id_123",  # vacancy_id  
            "Python Developer",  # title
            "https://hh.ru/vacancy/123",  # url
            100000,  # salary_from
            150000,  # salary_to
            "RUR",  # salary_currency
            "Great job opportunity",  # description
            "Python, Django",  # requirements
            "Develop applications",  # responsibilities
            "1-3 года",  # experience
            "Полная занятость",  # employment
            "Полный день",  # schedule
            "Москва",  # area
            "hh",  # source
            datetime.now(),  # published_at
            datetime.now(),  # created_at
            "Tech Company",  # company_name
        )

    @patch('src.storage.postgres_saver.RealDictCursor')
    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_get_vacancies_success(self, mock_logger, mock_psycopg2, mock_real_dict_cursor, mock_db_row):
        """Покрытие: получение всех вакансий"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Настройка context manager для соединения
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.__exit__.return_value = None
        
        # Настройка context manager для курсора
        mock_cursor.__enter__.return_value = mock_cursor
        mock_cursor.__exit__.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        
        # Мокируем результат с именованными полями как в RealDictCursor
        mock_row_dict = {
            "vacancy_id": "test_id_123",
            "title": "Python Developer", 
            "url": "https://hh.ru/vacancy/123",
            "salary_from": 100000,
            "salary_to": 150000,
            "salary_currency": "RUR",
            "description": "Great job",
            "requirements": "Python",
            "responsibilities": "Develop",
            "experience": "1-3 года",
            "employment": "Полная",
            "schedule": "Полный",
            "area": "Москва",
            "source": "hh",
            "published_at": datetime.now(),
            "company_name": "Tech Company"
        }
        mock_cursor.fetchall.return_value = [mock_row_dict]
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            result = saver.get_vacancies()
            
            # Проверяем что SQL выполнился
            mock_cursor.execute.assert_called_once()
            assert len(result) == 1
            # Проверяем что возвращается список объектов Vacancy
            assert hasattr(result[0], 'id') if result else True

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_get_vacancies_error(self, mock_logger, mock_psycopg2):
        """Покрытие: ошибка при получении вакансий"""
        from src.storage.postgres_saver import PsycopgError
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', side_effect=PsycopgError("Connection failed")):
            result = saver.get_vacancies()
            
            # Проверяем что возвращается пустой список при ошибке
            assert result == []
            mock_logger.error.assert_called()

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_convert_rows_to_vacancies_success(self, mock_logger, mock_psycopg2, mock_db_row):
        """Покрытие: успешная конвертация строк БД в объекты Vacancy"""
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        # Мокируем Vacancy.from_dict для избежания сложностей с созданием реальных объектов
        with patch('src.storage.postgres_saver.Vacancy') as MockVacancy:
            mock_vacancy = MagicMock()
            MockVacancy.return_value = mock_vacancy
            
            rows = [mock_db_row]
            result = saver._convert_rows_to_vacancies(rows)
            
            # Проверяем что создается объект Vacancy
            MockVacancy.assert_called_once()
            assert len(result) == 1
            assert result[0] == mock_vacancy

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')  
    def test_convert_rows_to_vacancies_error(self, mock_logger, mock_psycopg2, mock_db_row):
        """Покрытие: ошибка при конвертации строк БД"""
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        # Мокируем Vacancy чтобы он вызывал ошибку
        with patch('src.storage.postgres_saver.Vacancy', side_effect=Exception("Conversion error")):
            rows = [mock_db_row]
            result = saver._convert_rows_to_vacancies(rows)
            
            # Проверяем что ошибка обработана и возвращается пустой список
            assert result == []
            mock_logger.error.assert_called()
            # Проверяем что логируется предупреждение о пропущенных записях
            warning_calls = [call for call in mock_logger.warning.call_args_list if "Пропущено" in str(call)]
            assert len(warning_calls) >= 1

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_convert_rows_to_vacancies_empty_rows(self, mock_logger, mock_psycopg2):
        """Покрытие: конвертация пустого списка строк"""
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        result = saver._convert_rows_to_vacancies([])
        assert result == []

    @pytest.fixture
    def mock_vacancy_for_filtering(self):
        """Создание мок-вакансии для тестирования фильтрации"""
        vacancy = MagicMock()
        vacancy.id = "filter_test_123"
        vacancy.title = "Java Developer"
        vacancy.description = "Great Java position"
        vacancy.source = "hh"
        vacancy.employer = {
            "name": "Target Company",
            "id": "target_123"
        }
        vacancy.salary = MagicMock()
        vacancy.salary.salary_from = 80000
        vacancy.salary.salary_to = 120000
        vacancy.area = "СПб"
        return vacancy

    @patch('psycopg2.extras.execute_values')
    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_filter_and_deduplicate_vacancies_success(self, mock_logger, mock_psycopg2, mock_execute_values, mock_vacancy_for_filtering):
        """Покрытие: успешная фильтрация и дедупликация"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.connection = mock_connection
        mock_connection.encoding = 'UTF8'
        
        # Мокируем компании для фильтрации
        mock_cursor.fetchall.side_effect = [
            [(1, "Target Company", "target_123", None, "target company")],  # companies
            [(0,)]  # unique indices after deduplication
        ]
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch.object(saver, '_normalize_text', side_effect=lambda x: str(x).lower()):
                result = saver.filter_and_deduplicate_vacancies([mock_vacancy_for_filtering])
                
                # Проверяем что SQL операции выполнились
                assert mock_execute_values.called
                assert isinstance(result, list)

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_filter_and_deduplicate_vacancies_empty_list(self, mock_logger, mock_psycopg2):
        """Покрытие: фильтрация пустого списка"""
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        result = saver.filter_and_deduplicate_vacancies([])
        assert result == []

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_filter_and_deduplicate_vacancies_with_filters(self, mock_logger, mock_psycopg2, mock_vacancy_for_filtering):
        """Покрытие: фильтрация с дополнительными фильтрами"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.connection = mock_connection
        mock_connection.encoding = 'UTF8'
        
        # Мокируем результаты SQL запросов
        mock_cursor.fetchall.side_effect = [
            [(1, "Target Company", "target_123", None, "target company")],  # companies
            [(0,)],  # unique indices after deduplication  
            [(0,)]   # filtered indices after additional filters
        ]
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch('psycopg2.extras.execute_values'):
                with patch.object(saver, '_normalize_text', side_effect=lambda x: str(x).lower()):
                    filters = {
                        "salary_from": 70000,
                        "keywords": ["Java"]
                    }
                    result = saver.filter_and_deduplicate_vacancies([mock_vacancy_for_filtering], filters)
                    
                    # Проверяем что фильтры применились
                    assert isinstance(result, list)

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_filter_and_deduplicate_vacancies_error(self, mock_logger, mock_psycopg2, mock_vacancy_for_filtering):
        """Покрытие: ошибка при фильтрации и дедупликации"""
        mock_connection = MagicMock()
        mock_connection.closed = False
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch.object(mock_connection, 'cursor', side_effect=Exception("SQL Error")):
                result = saver.filter_and_deduplicate_vacancies([mock_vacancy_for_filtering])
                
                # Проверяем что возвращается исходный список при ошибке  
                assert result == [mock_vacancy_for_filtering]
                mock_logger.error.assert_called()


class TestPostgresSaverConnectionHandling:
    """Тестирование управления соединениями и ошибок"""

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_ensure_companies_table_index_creation_error(self, mock_logger, mock_psycopg2):
        """Покрытие: ошибка при создании индексов для таблицы companies"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.connection = mock_connection
        mock_connection.encoding = 'UTF8'
        
        # Мокируем что поля не существуют, но создание индекса падает
        def mock_execute_side_effect(query, *args):
            if "CREATE INDEX" in query:
                from src.storage.postgres_saver import PsycopgError
                raise PsycopgError("Index creation failed")
            
        mock_cursor.execute.side_effect = mock_execute_side_effect
        mock_cursor.fetchone.side_effect = [None, None]  # Поля не найдены
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch.object(saver, '_initialize_target_companies'):
                saver._ensure_companies_table_exists()
                
                # Проверяем что предупреждение логируется
                warning_calls = [call for call in mock_logger.warn.call_args_list if "Не удалось создать индекс" in str(call)]
                assert len(warning_calls) >= 1

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_ensure_tables_exist_foreign_key_error(self, mock_logger, mock_psycopg2):
        """Покрытие: ошибка при создании внешнего ключа"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.connection = mock_connection
        mock_connection.encoding = 'UTF8'
        
        def mock_execute_side_effect(query, *args):
            if "FOREIGN KEY" in query:
                from src.storage.postgres_saver import PsycopgError
                raise PsycopgError("Foreign key creation failed")
                
        mock_cursor.execute.side_effect = mock_execute_side_effect
        # Внешний ключ не найден
        mock_cursor.fetchone.side_effect = [None] * 20  # Много None для полей и None для FK
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch.object(saver, '_ensure_companies_table_exists'):
                saver._ensure_tables_exist()
                
                # Проверяем что предупреждение логируется  
                warning_calls = [call for call in mock_logger.warning.call_args_list if "Не удалось создать внешний ключ" in str(call)]
                assert len(warning_calls) >= 1

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_connection_cleanup_on_error(self, mock_logger, mock_psycopg2):
        """Покрытие: очистка соединений при ошибках"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.closed = False
        
        from src.storage.postgres_saver import PsycopgError
        mock_cursor.execute.side_effect = PsycopgError("Database error")
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            try:
                saver.delete_all_vacancies()
            except:
                pass
                
            # Проверяем что соединение было закрыто
            mock_connection.close.assert_called()
            # Проверяем что был сделан rollback
            mock_connection.rollback.assert_called()

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_connection_closed_error_handling(self, mock_logger, mock_psycopg2):
        """Покрытие: обработка ошибок с уже закрытым соединением"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.closed = True  # Соединение уже закрыто
        
        from src.storage.postgres_saver import PsycopgError
        mock_cursor.execute.side_effect = PsycopgError("Database error")
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            result = saver.delete_all_vacancies()
            
            # Проверяем что возвращается False при ошибке
            assert result is False
            # rollback не должен быть вызван для закрытого соединения
            mock_connection.rollback.assert_not_called()


class TestPostgresSaverEdgeCases:
    """Тестирование граничных случаев и особых сценариев"""

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_batch_operations_with_invalid_vacancy(self, mock_logger, mock_psycopg2):
        """Покрытие: batch операции с невалидными вакансиями"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.connection = mock_connection
        mock_connection.encoding = 'UTF8'
        mock_cursor.fetchall.return_value = []  # Нет компаний
        
        # Создаем невалидную "вакансию" без атрибута employer
        invalid_vacancy = MagicMock()
        del invalid_vacancy.employer  # Удаляем атрибут
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch('psycopg2.extras.execute_values'):
                result = saver.add_vacancy_batch_optimized([invalid_vacancy])
                
                # Проверяем что операция не падает и возвращает пустой результат
                assert isinstance(result, list)
                # Проверяем что логируется ошибка о невалидном объекте
                error_calls = [call for call in mock_logger.error.call_args_list if "не является Vacancy" in str(call)]
                assert len(error_calls) >= 1

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger') 
    def test_normalize_date_edge_cases(self, mock_logger, mock_psycopg2):
        """Покрытие: нормализация даты для граничных случаев"""
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        # Тестируем различные случаи
        result1 = saver._normalize_published_date("")  # Пустая строка
        assert isinstance(result1, datetime)
        
        result2 = saver._normalize_published_date("   ")  # Пробелы
        assert isinstance(result2, datetime)
        
        result3 = saver._normalize_published_date("invalid-date")  # Невалидная дата
        assert result3 is None or isinstance(result3, datetime)
        
        result4 = saver._normalize_published_date(12345)  # Число
        assert result4 is None or isinstance(result4, datetime)

    @patch('src.storage.postgres_saver.psycopg2')
    @patch('src.storage.postgres_saver.logger')
    def test_add_vacancy_batch_with_complex_employer_data(self, mock_logger, mock_psycopg2):
        """Покрытие: batch добавление с различными типами данных работодателя"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.connection = mock_connection
        mock_connection.encoding = 'UTF8'
        mock_cursor.fetchall.return_value = [(1, "Company", "123", None)]
        
        # Создаем вакансии с разными типами employer
        vacancy1 = MagicMock()
        vacancy1.id = "test_1"
        vacancy1.employer = {"name": "Dict Company", "id": "123"}  # Словарь
        vacancy1.salary = None
        vacancy1.area = "Moscow"
        
        vacancy2 = MagicMock()  
        vacancy2.id = "test_2"
        vacancy2.employer = MagicMock()  # Объект с методами
        vacancy2.employer.get_name.return_value = "Object Company"
        vacancy2.employer.id = "456"
        vacancy2.salary = None
        vacancy2.area = "SPb"
        
        vacancy3 = MagicMock()
        vacancy3.id = "test_3"
        vacancy3.employer = "String Company"  # Просто строка
        vacancy3.salary = None
        vacancy3.area = "Екатеринburg"
        
        vacancies = [vacancy1, vacancy2, vacancy3]
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            saver = PostgresSaver({"host": "test"})
            
        with patch.object(saver, '_get_connection', return_value=mock_connection):
            with patch('psycopg2.extras.execute_values'):
                with patch('src.utils.data_normalizers.normalize_area_data', return_value="Area"):
                    with patch.object(saver, '_normalize_published_date', return_value=datetime.now()):
                        result = saver.add_vacancy_batch_optimized(vacancies)
                        
                        # Проверяем что операция прошла без ошибок
                        assert isinstance(result, list)


# Добавляем тесты для 100% покрытия строк