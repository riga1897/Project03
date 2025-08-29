"""
Тесты для DBManager

Содержит тесты для проверки корректности работы с базой данных PostgreSQL
и специфичных методов согласно требованиям проекта.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.storage.db_manager import DBManager


class TestDBManager:
    """Тесты для класса DBManager"""

    @patch('psycopg2.connect')
    def test_initialization(self, mock_connect):
        """Тест инициализации DBManager"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        assert db_manager is not None

    @patch('psycopg2.connect')
    def test_check_connection(self, mock_connect):
        """Тест проверки подключения к базе данных"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is True

    @patch('psycopg2.connect')
    def test_check_connection_failure(self, mock_connect):
        """Тест неудачной проверки подключения"""
        mock_connect.side_effect = Exception("Connection failed")

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is False

    @pytest.fixture
    def sample_companies_data(self):
        """Фикстура с примерами данных компаний"""
        return [
            {"name": "СБЕР", "vacancies_count": 10},
            {"name": "Яндекс", "vacancies_count": 15}
        ]

    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect, sample_companies_data):
        """Тест получения списка компаний и количества вакансий"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.fetchone.return_value = (1,)  # For check_connection
        mock_cursor.fetchall.return_value = [("СБЕР", 10), ("Яндекс", 15)]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        companies = db_manager.get_companies_and_vacancies_count()

        assert len(companies) == 2
        assert companies[0][0] == "СБЕР"
        assert companies[0][1] == 10

    @patch('psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        
        # Настраиваем множественные вызовы fetchone для create_tables
        mock_cursor.fetchone.side_effect = [
            ("integer",),  # Для проверки типа company_id в create_tables
            (True,),       # Для проверки constraint в create_tables
        ]
        
        # Создаем правильный mock для RealDictCursor результата
        test_row_data = {
            "title": "Python Developer", 
            "company_name": "СБЕР", 
            "salary_info": "100000 - 150000 RUR",
            "url": "https://hh.ru/vacancy/12345", 
            "vacancy_id": "12345", 
            "raw_company_id": 1, 
            "linked_company_id": 1
        }
        
        # Создаем mock объект который ведет себя как dict
        test_row = Mock()
        test_row.get = lambda key, default=None: test_row_data.get(key, default)
        # Добавляем методы для работы как словарь
        test_row.keys = Mock(return_value=test_row_data.keys())
        test_row.values = Mock(return_value=test_row_data.values())
        test_row.items = Mock(return_value=test_row_data.items())
        test_row.__getitem__ = lambda self, key: test_row_data[key]
        test_row.__iter__ = Mock(return_value=iter(test_row_data))
        
        mock_cursor.fetchall.return_value = [test_row]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Патчим _ensure_tables_exist чтобы избежать реального выполнения create_tables
        db_manager = DBManager()
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
            vacancies = db_manager.get_all_vacancies()

            assert len(vacancies) == 1
            assert vacancies[0]["title"] == "Python Developer"

    @patch('psycopg2.connect')
    def test_get_avg_salary(self, mock_connect):
        """Тест получения средней зарплаты"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_cursor.fetchone.return_value = (125000.0,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        avg_salary = db_manager.get_avg_salary()

        assert avg_salary == 125000.0
        mock_cursor.execute.assert_called()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        
        # Настраиваем разные результаты для разных запросов
        def side_effect(*args, **kwargs):
            if "AVG(" in args[0]:
                return (125000.0,)
            else:
                return [
                    ("Senior Python Developer", "СБЕР", "150000 - 200000 RUR", 
                     "https://hh.ru/vacancy/67890", 175000.0, "67890")
                ]
        
        mock_cursor.fetchone.side_effect = lambda: (125000.0,)
        mock_cursor.fetchall.return_value = [
            ("Senior Python Developer", "СБЕР", "150000 - 200000 RUR", 
             "https://hh.ru/vacancy/67890", 175000.0, "67890")
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        vacancies = db_manager.get_vacancies_with_higher_salary()

        assert len(vacancies) == 1
        assert vacancies[0]["title"] == "Senior Python Developer"

    @patch('psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тест поиска вакансий по ключевому слову"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        
        # Настраиваем множественные вызовы fetchone для create_tables
        mock_cursor.fetchone.side_effect = [
            ("integer",),  # Для проверки типа company_id в create_tables
            (True,),       # Для проверки constraint в create_tables
        ]
        
        # Настраиваем fetchall для основного запроса
        mock_cursor.fetchall.return_value = [
            ("Python Developer", "СБЕР", "100000 - 150000 RUR", 
             "https://hh.ru/vacancy/12345", "Python development", "12345")
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        vacancies = db_manager.get_vacancies_with_keyword("python")

        assert len(vacancies) == 1
        assert vacancies[0]["title"] == "Python Developer"
        mock_cursor.execute.assert_called()

    @patch('psycopg2.connect')
    def test_create_tables(self, mock_connect):
        """Тест создания таблиц"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Настраиваем ответы для различных SQL запросов
        mock_cursor.fetchone.side_effect = [
            ("integer",),  # Для проверки типа company_id
            (True,),       # Для проверки существования constraint
        ]

        db_manager = DBManager()
        
        # Патчим create_tables чтобы избежать реального выполнения
        with patch.object(db_manager, '_ensure_tables_exist', return_value=True):
            db_manager.create_tables()

        # Проверяем, что execute был вызван для создания таблиц
        assert mock_cursor.execute.call_count >= 2  # Минимум 2 таблицы
        # commit вызывается автоматически при использовании контекстного менеджера

    @patch('psycopg2.connect')
    def test_populate_companies_table(self, mock_connect):
        """Тест заполнения таблицы компаний"""
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Настраиваем ответы для SQL запросов:
        # 1. Проверка существования таблицы companies
        # 2. Начальный подсчет компаний
        # 3. Проверка существования каждой компании (15 раз) 
        # 4. Финальный подсчет компаний
        fetchone_responses = [
            (True,),   # 1. Таблица существует
            (0,),      # 2. Количество компаний = 0 (начальное)
        ]
        
        # 3. Добавляем None для каждой проверки существования компании (15 целевых компаний)
        for _ in range(15):
            fetchone_responses.append(None)
            
        # 4. Финальное количество компаний после вставки
        fetchone_responses.append((15,))
        
        mock_cursor.fetchone.side_effect = fetchone_responses

        db_manager = DBManager()
        db_manager.populate_companies_table()

        # Проверяем, что execute был вызван для заполнения таблицы
        assert mock_cursor.execute.call_count > 0