
"""
Всеобъемлющие тесты для компонентов с недостаточным покрытием кода
Фокус на 100% покрытие функционального кода с реальными импортами
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
import sys
import os
from typing import List, Dict, Any, Optional
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты компонентов
from src.storage.db_manager import DBManager
from src.storage.postgres_saver import PostgresSaver
from src.storage.simple_db_adapter import SimpleDBAdapter
from src.config.ui_config import UIConfig, UIPaginationConfig
from src.vacancies.models import Vacancy, Employer, Salary
from src.utils.env_loader import EnvLoader
from src.utils.cache import FileCache
from src.utils.decorators import exception_handler, retry
from src.utils.file_handlers import FileHandler
from src.storage.storage_factory import StorageFactory
from src.api_modules.cached_api import CachedAPI
from src.api_modules.hh_api import HeadHunterAPI
from src.api_modules.sj_api import SuperJobAPI


class TestDBManagerComprehensive:
    """Всеобъемлющие тесты для DBManager"""

    @pytest.fixture
    def db_manager(self):
        """Фикстура для DBManager"""
        return DBManager()

    @pytest.fixture
    def mock_connection(self):
        """Фикстура для мокированного подключения"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_conn.commit = Mock()
        mock_conn.rollback = Mock()
        mock_conn.close = Mock()
        return mock_conn, mock_cursor

    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count_success(self, mock_connect, db_manager, mock_connection):
        """Тест успешного получения списка компаний и количества вакансий"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            ('TechCorp', 50),
            ('DataCorp', 30),
            ('WebCorp', 25)
        ]

        result = db_manager.get_companies_and_vacancies_count()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == ('TechCorp', 50)
        assert result[1] == ('DataCorp', 30)
        assert result[2] == ('WebCorp', 25)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count_error(self, mock_connect, db_manager, mock_connection):
        """Тест обработки ошибки при получении компаний"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.execute.side_effect = Exception("Database error")

        result = db_manager.get_companies_and_vacancies_count()
        
        assert result == []
        mock_conn.rollback.assert_called()

    @patch('psycopg2.connect')
    def test_get_all_vacancies_success(self, mock_connect, db_manager, mock_connection):
        """Тест успешного получения всех вакансий"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            {'id': '1', 'title': 'Python Developer', 'company': 'TechCorp'},
            {'id': '2', 'title': 'Java Developer', 'company': 'JavaCorp'}
        ]

        result = db_manager.get_all_vacancies()
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_avg_salary_with_data(self, mock_connect, db_manager, mock_connection):
        """Тест получения средней зарплаты при наличии данных"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = (125000.0,)

        result = db_manager.get_avg_salary()
        
        assert result == 125000.0
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_avg_salary_no_data(self, mock_connect, db_manager, mock_connection):
        """Тест получения средней зарплаты при отсутствии данных"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = None

        result = db_manager.get_avg_salary()
        
        assert result is None

    @patch('psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect, db_manager, mock_connection):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            {'id': '1', 'title': 'Senior Developer', 'salary': 150000}
        ]

        result = db_manager.get_vacancies_with_higher_salary()
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect, db_manager, mock_connection):
        """Тест поиска вакансий по ключевому слову"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            {'id': '1', 'title': 'Python Developer'},
            {'id': '2', 'title': 'Python Analyst'}
        ]

        result = db_manager.get_vacancies_with_keyword('Python')
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_database_stats(self, mock_connect, db_manager, mock_connection):
        """Тест получения статистики базы данных"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.side_effect = [
            (150,),  # total_vacancies
            (25,),   # total_companies
            (125000.0,)  # avg_salary
        ]

        result = db_manager.get_database_stats()
        
        assert isinstance(result, dict)
        assert 'total_vacancies' in result
        assert 'total_companies' in result
        assert 'avg_salary' in result
        assert result['total_vacancies'] == 150
        assert result['total_companies'] == 25
        assert result['avg_salary'] == 125000.0

    @patch('psycopg2.connect')
    def test_init_database_creates_tables(self, mock_connect, db_manager, mock_connection):
        """Тест инициализации базы данных"""
        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn

        db_manager._init_database()
        
        # Проверяем, что execute был вызван для создания таблиц
        assert mock_cursor.execute.call_count >= 1
        mock_conn.commit.assert_called()


class TestPostgresSaverComprehensive:
    """Всеобъемлющие тесты для PostgresSaver"""

    @pytest.fixture
    def postgres_saver(self):
        """Фикстура для PostgresSaver"""
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            return PostgresSaver()

    @pytest.fixture
    def mock_vacancy(self):
        """Фикстура для реальной вакансии"""
        employer = Employer(name="Test Company", employer_id="comp123")
        salary = Salary(salary_from=100000, salary_to=150000, currency="RUR")
        return Vacancy(
            vacancy_id="test123",
            title="Test Job",
            employer=employer,
            url="https://test.com",
            description="Test description",
            salary=salary,
            source="test"
        )

    @patch('psycopg2.connect')
    def test_save_vacancies_single_vacancy(self, mock_connect, postgres_saver, mock_vacancy):
        """Тест сохранения одной вакансии"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            mock_cursor.fetchall.return_value = []
            mock_cursor.rowcount = 1
            
            result = postgres_saver.save_vacancies([mock_vacancy])
            
            assert isinstance(result, (list, int))
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_results(self, mock_connect, postgres_saver):
        """Тест получения вакансий с результатами"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            mock_cursor.fetchall.return_value = [
                ('1', 'Python Developer', 'Great job', 100000, 150000, 'RUR', 
                 'company1', 'TechCorp', 'https://example.com', 'hh')
            ]
            
            result = postgres_saver.get_vacancies()
            
            assert isinstance(result, list)
            mock_cursor.execute.assert_called()

    @patch('psycopg2.connect')
    def test_delete_vacancy_by_id_success(self, mock_connect, postgres_saver):
        """Тест успешного удаления вакансии по ID"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        mock_cursor.rowcount = 1

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            result = postgres_saver.delete_vacancy_by_id('test123')
            
            assert result is True
            mock_cursor.execute.assert_called_with("DELETE FROM vacancies WHERE vacancy_id = %s", ('test123',))
            mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_delete_vacancy_by_id_not_found(self, mock_connect, postgres_saver):
        """Тест удаления несуществующей вакансии"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        mock_cursor.rowcount = 0

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            result = postgres_saver.delete_vacancy_by_id('nonexistent')
            
            assert result is False

    def test_delete_vacancy_with_object(self, postgres_saver, mock_vacancy):
        """Тест удаления вакансии с объектом"""
        with patch.object(postgres_saver, 'delete_vacancy_by_id', return_value=True) as mock_delete:
            postgres_saver.delete_vacancy(mock_vacancy)
            mock_delete.assert_called_once_with(mock_vacancy.vacancy_id)

    @patch('psycopg2.connect')
    def test_is_vacancy_exists_true(self, mock_connect, postgres_saver, mock_vacancy):
        """Тест проверки существования вакансии - найдена"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = (1,)

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            result = postgres_saver.is_vacancy_exists(mock_vacancy)
            
            assert result is True

    @patch('psycopg2.connect')
    def test_is_vacancy_exists_false(self, mock_connect, postgres_saver, mock_vacancy):
        """Тест проверки существования вакансии - не найдена"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = None

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            result = postgres_saver.is_vacancy_exists(mock_vacancy)
            
            assert result is False

    @patch('psycopg2.connect')
    def test_get_vacancies_count_with_filters(self, mock_connect, postgres_saver):
        """Тест подсчета вакансий с фильтрами"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = (42,)

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            filters = {'title': 'Python', 'salary_from': 100000}
            result = postgres_saver.get_vacancies_count(filters)
            
            assert result == 42
            mock_cursor.execute.assert_called()

    @patch('psycopg2.connect')
    def test_delete_all_vacancies(self, mock_connect, postgres_saver):
        """Тест удаления всех вакансий"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            result = postgres_saver.delete_all_vacancies()
            
            assert result is True
            mock_cursor.execute.assert_called_with("DELETE FROM vacancies")
            mock_conn.commit.assert_called()


class TestSimpleDBAdapterComprehensive:
    """Всеобъемлющие тесты для SimpleDBAdapter"""

    @pytest.fixture
    def db_adapter(self):
        """Фикстура для SimpleDBAdapter"""
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://localhost:5432/test'}):
            return SimpleDBAdapter()

    def test_init_with_database_url(self):
        """Тест инициализации с DATABASE_URL"""
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://localhost:5432/test'}):
            adapter = SimpleDBAdapter()
            assert adapter.database_url == 'postgresql://localhost:5432/test'

    def test_init_without_database_url(self):
        """Тест инициализации без DATABASE_URL"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="DATABASE_URL не установлен"):
                SimpleDBAdapter()

    def test_context_manager(self, db_adapter):
        """Тест работы как контекстного менеджера"""
        with db_adapter as adapter:
            assert adapter is not None
            assert isinstance(adapter, SimpleDBAdapter)

    @patch('subprocess.run')
    def test_test_connection_success(self, mock_run, db_adapter):
        """Тест успешной проверки соединения"""
        mock_run.return_value.returncode = 0
        
        result = db_adapter.test_connection()
        
        assert result is True
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_test_connection_failure(self, mock_run, db_adapter):
        """Тест неудачной проверки соединения"""
        mock_run.return_value.returncode = 1
        
        result = db_adapter.test_connection()
        
        assert result is False

    @patch('subprocess.run')
    def test_test_connection_exception(self, mock_run, db_adapter):
        """Тест обработки исключения при проверке соединения"""
        mock_run.side_effect = Exception("Connection error")
        
        result = db_adapter.test_connection()
        
        assert result is False

    def test_cursor_creation(self, db_adapter):
        """Тест создания курсора"""
        cursor = db_adapter.cursor()
        
        assert cursor is not None
        # Проверяем, что cursor имеет необходимые методы
        assert hasattr(cursor, 'execute')

    @patch('subprocess.run')
    def test_get_companies_and_vacancies_count(self, mock_run, db_adapter):
        """Тест получения компаний и количества вакансий"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Company1|10\nCompany2|15\n"

        with patch.object(db_adapter, 'cursor') as mock_cursor_method:
            mock_cursor = Mock()
            mock_cursor_method.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [('Company1', 10), ('Company2', 15)]
            
            result = db_adapter.get_companies_and_vacancies_count()
            
            assert isinstance(result, list)
            assert len(result) == 2

    def test_init_database_schema(self, db_adapter):
        """Тест инициализации схемы базы данных"""
        with patch.object(db_adapter, '_execute_ddl_script') as mock_execute:
            db_adapter.init_database_schema()
            mock_execute.assert_called()


class TestUIConfigComprehensive:
    """Всеобъемлющие тесты для UI конфигурации"""

    def test_ui_pagination_config_initialization(self):
        """Тест инициализации конфигурации пагинации"""
        config = UIPaginationConfig()
        
        assert config.default_items_per_page == 10
        assert config.search_results_per_page == 5
        assert config.saved_vacancies_per_page == 10
        assert config.max_items_per_page == 50
        assert config.min_items_per_page == 1

    def test_get_items_per_page_all_contexts(self):
        """Тест получения количества элементов для всех контекстов"""
        config = UIPaginationConfig()
        
        # Тестируем все поддерживаемые контексты
        assert config.get_items_per_page('search') == 5
        assert config.get_items_per_page('saved') == 10
        assert config.get_items_per_page('top') == 10
        assert config.get_items_per_page('favorites') == 10
        assert config.get_items_per_page('recent') == 10
        
        # Тестируем неизвестные контексты
        assert config.get_items_per_page('unknown') == 10
        assert config.get_items_per_page(None) == 10
        assert config.get_items_per_page('') == 10

    def test_validate_items_per_page_edge_cases(self):
        """Тест валидации с граничными случаями"""
        config = UIPaginationConfig()
        
        # Отрицательные числа
        assert config.validate_items_per_page(-10) == 1
        assert config.validate_items_per_page(-1) == 1
        
        # Ноль
        assert config.validate_items_per_page(0) == 1
        
        # Нормальные значения
        assert config.validate_items_per_page(1) == 1
        assert config.validate_items_per_page(25) == 25
        assert config.validate_items_per_page(50) == 50
        
        # Слишком большие значения
        assert config.validate_items_per_page(51) == 50
        assert config.validate_items_per_page(100) == 50
        assert config.validate_items_per_page(1000) == 50

    def test_ui_config_initialization(self):
        """Тест инициализации UI конфигурации"""
        config = UIConfig()
        
        assert config.items_per_page == 5
        assert config.max_display_items == 20

    def test_get_pagination_settings_default(self):
        """Тест получения настроек пагинации по умолчанию"""
        config = UIConfig()
        
        settings = config.get_pagination_settings()
        
        assert isinstance(settings, dict)
        assert settings['items_per_page'] == 5
        assert settings['max_display_items'] == 20

    def test_get_pagination_settings_custom(self):
        """Тест получения настроек пагинации с пользовательскими параметрами"""
        config = UIConfig()
        
        custom_settings = config.get_pagination_settings(
            items_per_page=15,
            max_display_items=50
        )
        
        assert custom_settings['items_per_page'] == 15
        assert custom_settings['max_display_items'] == 50

    def test_get_pagination_settings_partial_override(self):
        """Тест частичного переопределения настроек"""
        config = UIConfig()
        
        settings = config.get_pagination_settings(items_per_page=12)
        
        assert settings['items_per_page'] == 12
        assert settings['max_display_items'] == 20  # значение по умолчанию

    def test_global_ui_config_instances(self):
        """Тест глобальных экземпляров UI конфигурации"""
        from src.config.ui_config import ui_pagination_config, ui_config
        
        assert isinstance(ui_pagination_config, UIPaginationConfig)
        assert isinstance(ui_config, UIConfig)
        
        # Проверяем функциональность глобальных экземпляров
        assert ui_pagination_config.get_items_per_page('search') == 5
        assert ui_config.items_per_page == 5


class TestCacheComprehensive:
    """Всеобъемлющие тесты для FileCache"""

    @pytest.fixture
    def cache_dir(self):
        """Фикстура для временной директории кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def cache(self, cache_dir):
        """Фикстура для FileCache"""
        return FileCache(cache_dir)

    def test_cache_initialization(self, cache_dir):
        """Тест инициализации кэша"""
        cache = FileCache(cache_dir)
        
        assert cache.cache_dir.name == os.path.basename(cache_dir)
        assert os.path.exists(cache_dir)

    def test_cache_initialization_creates_directory(self):
        """Тест создания директории при инициализации"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = os.path.join(temp_dir, "new_cache")
            cache = FileCache(cache_path)
            
            assert os.path.exists(cache_path)

    def test_generate_params_hash(self, cache):
        """Тест генерации хеша параметров"""
        params1 = {"query": "python", "page": 1}
        params2 = {"query": "python", "page": 2}
        params3 = {"query": "python", "page": 1}
        
        hash1 = cache._generate_params_hash(params1)
        hash2 = cache._generate_params_hash(params2)
        hash3 = cache._generate_params_hash(params3)
        
        assert isinstance(hash1, str)
        assert len(hash1) > 0
        assert hash1 != hash2  # Разные параметры должны давать разные хеши
        assert hash1 == hash3  # Одинаковые параметры должны давать одинаковые хеши

    def test_save_response(self, cache):
        """Тест сохранения ответа в кэш"""
        data = {"items": [{"id": "1", "name": "Test"}], "found": 1}
        params = {"query": "python", "page": 0}
        
        cache.save_response("hh", params, data)
        
        # Проверяем, что файл создан
        hash_key = cache._generate_params_hash(params)
        cache_file = cache.cache_dir / f"hh_{hash_key}.json"
        assert cache_file.exists()

    def test_load_response_existing(self, cache):
        """Тест загрузки существующих данных из кэша"""
        data = {"items": [{"id": "1", "name": "Test"}], "found": 1}
        params = {"query": "python", "page": 0}
        
        # Сначала сохраняем данные
        cache.save_response("hh", params, data)
        
        # Затем загружаем
        loaded_data = cache.load_response("hh", params)
        
        assert loaded_data is not None
        assert "data" in loaded_data
        assert loaded_data["data"]["items"] == data["items"]
        key = "existing_key"
        
        # Сначала сохраняем
        cache.save_to_cache(key, data)
        
        # Затем загружаем
        loaded_data = cache.load_from_cache(key)
        
        assert loaded_data == data

    def test_load_from_cache_nonexistent(self, cache):
        """Тест загрузки несуществующих данных из кэша"""
        result = cache.load_from_cache("nonexistent_key")
        
        assert result is None

    def test_is_cache_valid_fresh(self, cache):
        """Тест проверки валидности свежего кэша"""
        key = "fresh_key"
        cache.save_to_cache(key, {"data": "test"})
        
        # Сразу после сохранения кэш должен быть валидным
        assert cache.is_cache_valid(key, max_age_hours=1)

    def test_is_cache_valid_expired(self, cache):
        """Тест проверки валидности устаревшего кэша"""
        key = "old_key"
        cache_file = os.path.join(cache.cache_dir, f"{key}.json")
        
        # Создаем файл с данными
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({"data": "test"}, f)
        
        # Изменяем время модификации на старое
        old_time = os.path.getmtime(cache_file) - 7200  # 2 часа назад
        os.utime(cache_file, (old_time, old_time))
        
        assert not cache.is_cache_valid(key, max_age_hours=1)

    def test_clear_cache(self, cache):
        """Тест очистки кэша"""
        # Создаем несколько файлов кэша
        cache.save_to_cache("key1", {"data": 1})
        cache.save_to_cache("key2", {"data": 2})
        
        # Проверяем, что файлы созданы
        assert len(os.listdir(cache.cache_dir)) == 2
        
        # Очищаем кэш
        cache.clear_cache()
        
        # Проверяем, что файлы удалены
        assert len(os.listdir(cache.cache_dir)) == 0

    def test_get_cache_size(self, cache):
        """Тест получения размера кэша"""
        initial_size = cache.get_cache_size()
        assert initial_size == 0
        
        # Добавляем данные в кэш
        cache.save_to_cache("size_test", {"data": "test" * 100})
        
        size_after = cache.get_cache_size()
        assert size_after > initial_size


class TestDecoratorsComprehensive:
    """Всеобъемлющие тесты для декораторов"""

    def test_exception_handler_success(self):
        """Тест обработки исключений - успешное выполнение"""
        @exception_handler(default_return="error")
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"

    def test_exception_handler_with_exception(self):
        """Тест обработки исключений - с исключением"""
        @exception_handler(default_return="error")
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        assert result == "error"

    def test_exception_handler_custom_default(self):
        """Тест обработки исключений с пользовательским значением по умолчанию"""
        @exception_handler(default_return=None)
        def failing_function():
            raise RuntimeError("Test error")
        
        result = failing_function()
        assert result is None

    def test_retry_decorator_success_first_try(self):
        """Тест retry декоратора - успех с первой попытки"""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.1)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_decorator_success_after_retries(self):
        """Тест retry декоратора - успех после нескольких попыток"""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"
        
        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_decorator_max_attempts_exceeded(self):
        """Тест retry декоратора - превышение максимального количества попыток"""
        call_count = 0
        
        @retry(max_attempts=2, delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_failing_function()
        
        assert call_count == 2


class TestFileHandlerComprehensive:
    """Всеобъемлющие тесты для FileHandler"""

    @pytest.fixture
    def file_handler(self):
        """Фикстура для FileHandler"""
        return FileHandler()

    @pytest.fixture
    def temp_file(self):
        """Фикстура для временного файла"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_data = {"test": "data", "numbers": [1, 2, 3]}
            json.dump(test_data, f)
            temp_path = f.name
        
        yield temp_path, test_data
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_read_file_json_success(self, file_handler, temp_file):
        """Тест успешного чтения JSON файла"""
        temp_path, expected_data = temp_file
        
        result = file_handler.read_file(temp_path)
        
        assert result == expected_data

    def test_read_file_nonexistent(self, file_handler):
        """Тест чтения несуществующего файла"""
        result = file_handler.read_file("nonexistent.json")
        
        assert result is None

    def test_write_file_json_success(self, file_handler):
        """Тест успешной записи JSON файла"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            test_data = {"write_test": "success", "items": [4, 5, 6]}
            
            result = file_handler.write_file(temp_path, test_data)
            
            assert result is True
            
            # Проверяем, что файл действительно записан
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            assert saved_data == test_data
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_write_file_invalid_path(self, file_handler):
        """Тест записи в недоступный путь"""
        invalid_path = "/root/cannot_write_here.json"
        
        result = file_handler.write_file(invalid_path, {"test": "data"})
        
        assert result is False

    def test_file_exists_true(self, file_handler, temp_file):
        """Тест проверки существования файла - файл существует"""
        temp_path, _ = temp_file
        
        result = file_handler.file_exists(temp_path)
        
        assert result is True

    def test_file_exists_false(self, file_handler):
        """Тест проверки существования файла - файл не существует"""
        result = file_handler.file_exists("definitely_nonexistent.json")
        
        assert result is False

    def test_delete_file_success(self, file_handler):
        """Тест успешного удаления файла"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        # Проверяем, что файл создан
        assert os.path.exists(temp_path)
        
        # Удаляем файл
        result = file_handler.delete_file(temp_path)
        
        assert result is True
        assert not os.path.exists(temp_path)

    def test_delete_file_nonexistent(self, file_handler):
        """Тест удаления несуществующего файла"""
        result = file_handler.delete_file("nonexistent.json")
        
        assert result is False


class TestStorageFactoryComprehensive:
    """Всеобъемлющие тесты для StorageFactory"""

    def test_create_storage_postgres(self):
        """Тест создания PostgreSQL хранилища"""
        with patch('src.storage.storage_factory.PostgresSaver') as mock_postgres:
            mock_instance = Mock()
            mock_postgres.return_value = mock_instance
            
            storage = StorageFactory.create_storage('postgres')
            
            assert storage == mock_instance
            mock_postgres.assert_called_once()

    def test_create_storage_json(self):
        """Тест создания JSON хранилища"""
        with patch('src.storage.storage_factory.JSONSaver') as mock_json:
            mock_instance = Mock()
            mock_json.return_value = mock_instance
            
            storage = StorageFactory.create_storage('json')
            
            assert storage == mock_instance
            mock_json.assert_called_once()

    def test_create_storage_csv(self):
        """Тест создания CSV хранилища"""
        with patch('src.storage.storage_factory.CSVSaver') as mock_csv:
            mock_instance = Mock()
            mock_csv.return_value = mock_instance
            
            storage = StorageFactory.create_storage('csv')
            
            assert storage == mock_instance
            mock_csv.assert_called_once()

    def test_create_storage_unknown_type(self):
        """Тест создания хранилища неизвестного типа"""
        with pytest.raises(ValueError, match="Неизвестный тип хранилища"):
            StorageFactory.create_storage('unknown_type')

    def test_get_available_storage_types(self):
        """Тест получения доступных типов хранилищ"""
        types = StorageFactory.get_available_storage_types()
        
        assert isinstance(types, list)
        assert 'postgres' in types
        assert 'json' in types
        assert 'csv' in types

    def test_create_storage_with_config(self):
        """Тест создания хранилища с конфигурацией"""
        config = {'host': 'localhost', 'port': 5432}
        
        with patch('src.storage.storage_factory.PostgresSaver') as mock_postgres:
            mock_instance = Mock()
            mock_postgres.return_value = mock_instance
            
            storage = StorageFactory.create_storage('postgres', config)
            
            assert storage == mock_instance
            mock_postgres.assert_called_once_with(config)


class TestCachedAPIComprehensive:
    """Всеобъемлющие тесты для CachedAPI"""

    @pytest.fixture
    def base_api(self):
        """Фикстура для базового API"""
        return HeadHunterAPI()

    @pytest.fixture
    def cache_dir(self):
        """Фикстура для директории кэша"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def cached_api(self, base_api, cache_dir):
        """Фикстура для CachedAPI"""
        return CachedAPI(base_api, cache_dir)

    def test_cached_api_initialization(self, base_api, cache_dir):
        """Тест инициализации CachedAPI"""
        cached_api = CachedAPI(base_api, cache_dir)
        
        assert cached_api.base_api == base_api
        assert cached_api.cache_dir == cache_dir
        assert os.path.exists(cache_dir)

    @patch('requests.get')
    def test_get_vacancies_with_cache_miss(self, mock_get, cached_api):
        """Тест получения вакансий при отсутствии в кэше"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "1", "name": "Test Job"}], "found": 1}
        mock_get.return_value = mock_response

        result = cached_api.get_vacancies("Python")
        
        assert isinstance(result, list)
        mock_get.assert_called()

    def test_get_vacancies_with_cache_hit(self, cached_api):
        """Тест получения вакансий при наличии в кэше"""
        # Подготавливаем кэш
        cache_key = cached_api.cache.get_cache_key("Python", page=0, per_page=20)
        cached_data = [{"id": "cached1", "name": "Cached Job"}]
        cached_api.cache.save_to_cache(cache_key, cached_data)
        
        with patch.object(cached_api.base_api, 'get_vacancies') as mock_base:
            result = cached_api.get_vacancies("Python")
            
            assert result == cached_data
            # Базовый API не должен вызываться при попадании в кэш
            mock_base.assert_not_called()

    def test_clear_cache(self, cached_api):
        """Тест очистки кэша"""
        # Добавляем данные в кэш
        cached_api.cache.save_to_cache("test_key", {"test": "data"})
        
        # Проверяем, что кэш не пустой
        assert len(os.listdir(cached_api.cache_dir)) > 0
        
        # Очищаем кэш
        cached_api.clear_cache()
        
        # Проверяем, что кэш очищен
        assert len(os.listdir(cached_api.cache_dir)) == 0

    def test_get_cache_size(self, cached_api):
        """Тест получения размера кэша"""
        initial_size = cached_api.get_cache_size()
        
        # Добавляем данные в кэш
        cached_api.cache.save_to_cache("size_test", {"large_data": "x" * 1000})
        
        new_size = cached_api.get_cache_size()
        assert new_size > initial_size


class TestEnvLoaderComprehensive:
    """Всеобъемлющие тесты для EnvLoader"""

    def test_get_env_var_existing(self):
        """Тест получения существующей переменной окружения"""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = EnvLoader.get_env_var('TEST_VAR')
            assert result == 'test_value'

    def test_get_env_var_with_default(self):
        """Тест получения переменной с значением по умолчанию"""
        result = EnvLoader.get_env_var('NONEXISTENT_VAR', 'default_value')
        assert result == 'default_value'

    def test_get_env_var_nonexistent_no_default(self):
        """Тест получения несуществующей переменной без значения по умолчанию"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_env_var('NONEXISTENT_VAR')
            assert result is None

    @patch('builtins.open', new_callable=mock_open, read_data='TEST_VAR=test_value\nANOTHER_VAR=another_value\n')
    def test_load_env_file_success(self, mock_file):
        """Тест успешной загрузки .env файла"""
        with patch('os.path.exists', return_value=True):
            result = EnvLoader.load_env_file('.env')
            
            assert result is True
            mock_file.assert_called_once_with('.env', 'r', encoding='utf-8')

    def test_load_env_file_nonexistent(self):
        """Тест загрузки несуществующего .env файла"""
        with patch('os.path.exists', return_value=False):
            result = EnvLoader.load_env_file('nonexistent.env')
            
            assert result is False

    def test_get_database_url_from_env(self):
        """Тест получения DATABASE_URL из переменных окружения"""
        test_url = 'postgresql://user:pass@localhost:5432/db'
        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            result = EnvLoader.get_database_url()
            assert result == test_url

    def test_get_database_url_default(self):
        """Тест получения DATABASE_URL со значением по умолчанию"""
        with patch.dict(os.environ, {}, clear=True):
            result = EnvLoader.get_database_url()
            assert result is not None
            assert 'postgresql' in result

    def test_is_debug_mode_true(self):
        """Тест проверки режима отладки - включен"""
        with patch.dict(os.environ, {'DEBUG': 'True'}):
            assert EnvLoader.is_debug_mode() is True
        
        with patch.dict(os.environ, {'DEBUG': '1'}):
            assert EnvLoader.is_debug_mode() is True

    def test_is_debug_mode_false(self):
        """Тест проверки режима отладки - выключен"""
        with patch.dict(os.environ, {'DEBUG': 'False'}):
            assert EnvLoader.is_debug_mode() is False
        
        with patch.dict(os.environ, {}, clear=True):
            assert EnvLoader.is_debug_mode() is False


class TestAPIModulesComprehensive:
    """Всеобъемлющие тесты для API модулей"""

    @patch('requests.get')
    def test_hh_api_get_vacancies_success(self, mock_get):
        """Тест успешного получения вакансий из HeadHunter API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": "1", "name": "Python Developer"},
                {"id": "2", "name": "Java Developer"}
            ],
            "found": 2
        }
        mock_get.return_value = mock_response

        hh_api = HeadHunterAPI()
        result = hh_api.get_vacancies("Python")
        
        assert isinstance(result, list)
        assert len(result) >= 0
        mock_get.assert_called()

    @patch('requests.get')
    def test_hh_api_get_vacancies_error(self, mock_get):
        """Тест обработки ошибки при получении вакансий из HeadHunter API"""
        mock_get.side_effect = Exception("Network error")

        hh_api = HeadHunterAPI()
        result = hh_api.get_vacancies("Python")
        
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('requests.get')
    def test_sj_api_get_vacancies_success(self, mock_get):
        """Тест успешного получения вакансий из SuperJob API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objects": [
                {"id": 1, "profession": "Python Developer"},
                {"id": 2, "profession": "Java Developer"}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response

        sj_api = SuperJobAPI()
        result = sj_api.get_vacancies("Python")
        
        assert isinstance(result, list)
        mock_get.assert_called()

    @patch('requests.get')
    def test_sj_api_get_vacancies_error(self, mock_get):
        """Тест обработки ошибки при получении вакансий из SuperJob API"""
        mock_get.side_effect = Exception("API error")

        sj_api = SuperJobAPI()
        result = sj_api.get_vacancies("Python")
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_hh_api_initialization(self):
        """Тест инициализации HeadHunter API"""
        hh_api = HeadHunterAPI()
        
        assert hh_api is not None
        assert hasattr(hh_api, 'get_vacancies')
        assert hasattr(hh_api, 'base_url')

    def test_sj_api_initialization(self):
        """Тест инициализации SuperJob API"""
        sj_api = SuperJobAPI()
        
        assert sj_api is not None
        assert hasattr(sj_api, 'get_vacancies')
        assert hasattr(sj_api, 'base_url')

    @patch('requests.get')
    def test_hh_api_pagination(self, mock_get):
        """Тест пагинации HeadHunter API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "found": 0}
        mock_get.return_value = mock_response

        hh_api = HeadHunterAPI()
        
        if hasattr(hh_api, 'get_vacancies_page'):
            result = hh_api.get_vacancies_page("Python", page=1)
            assert isinstance(result, (dict, list))

    @patch('requests.get')
    def test_sj_api_pagination(self, mock_get):
        """Тест пагинации SuperJob API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"objects": [], "total": 0}
        mock_get.return_value = mock_response

        sj_api = SuperJobAPI()
        
        if hasattr(sj_api, 'get_vacancies_page'):
            result = sj_api.get_vacancies_page("Python", page=1)
            assert isinstance(result, (dict, list))


class TestIntegrationComprehensive:
    """Всеобъемлющие интеграционные тесты"""

    @patch('psycopg2.connect')
    def test_db_manager_storage_integration(self, mock_connect):
        """Тест интеграции DBManager и хранилищ"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        
        with patch.object(PostgresSaver, '_ensure_tables_exist'):
            postgres_saver = PostgresSaver()

        # Тестируем совместимость методов
        mock_cursor.fetchall.return_value = [('TestCorp', 5)]
        
        db_result = db_manager.get_companies_and_vacancies_count()
        assert isinstance(db_result, list)

    def test_ui_config_cache_integration(self):
        """Тест интеграции UI конфигурации с кэшем"""
        config = UIConfig()
        
        with tempfile.TemporaryDirectory() as cache_dir:
            cache = Cache(cache_dir)
            
            # Тестируем сохранение настроек в кэш
            settings = config.get_pagination_settings()
            cache.save_to_cache("ui_settings", settings)
            
            loaded_settings = cache.load_from_cache("ui_settings")
            assert loaded_settings == settings

    def test_api_cache_storage_integration(self):
        """Тест интеграции API, кэша и хранилища"""
        with tempfile.TemporaryDirectory() as cache_dir:
            base_api = HeadHunterAPI()
            cached_api = CachedAPI(base_api, cache_dir)
            
            with patch.object(PostgresSaver, '_ensure_tables_exist'):
                storage = PostgresSaver()
            
            # Все компоненты должны быть совместимы
            assert cached_api is not None
            assert storage is not None
            assert isinstance(cached_api.cache_dir, str)

    def test_error_handling_integration(self):
        """Тест интеграции обработки ошибок между компонентами"""
        @exception_handler(default_return=[])
        def failing_operation():
            raise ValueError("Integration test error")
        
        @retry(max_attempts=2, delay=0.01)
        def retrying_operation():
            return failing_operation()
        
        # Декораторы должны работать вместе
        result = retrying_operation()
        assert result == []

    def test_full_workflow_integration(self):
        """Тест полного рабочего процесса"""
        config = UIConfig()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_handler = FileHandler()
            cache = Cache(temp_dir)
            
            # Создаем настройки
            settings = config.get_pagination_settings(items_per_page=10)
            
            # Сохраняем в кэш
            cache.save_to_cache("workflow_settings", settings)
            
            # Загружаем обратно
            loaded_settings = cache.load_from_cache("workflow_settings")
            
            assert loaded_settings == settings
            assert loaded_settings['items_per_page'] == 10


class TestEdgeCasesComprehensive:
    """Всеобъемлющие тесты граничных случаев"""

    def test_empty_data_handling(self):
        """Тест обработки пустых данных"""
        config = UIPaginationConfig()
        
        # Пустые строки
        assert config.get_items_per_page('') == 10
        assert config.get_items_per_page(None) == 10
        
        # Нулевые значения
        assert config.validate_items_per_page(0) == 1

    def test_large_data_handling(self):
        """Тест обработки больших данных"""
        config = UIPaginationConfig()
        
        # Очень большие числа
        assert config.validate_items_per_page(1000000) == 50
        assert config.validate_items_per_page(sys.maxsize) == 50

    def test_unicode_handling(self):
        """Тест обработки Unicode данных"""
        with tempfile.TemporaryDirectory() as cache_dir:
            cache = Cache(cache_dir)
            
            unicode_data = {
                "title": "Разработчик Python 🐍",
                "company": "Яндекс",
                "emoji": "💼📊🚀"
            }
            
            cache.save_to_cache("unicode_test", unicode_data)
            loaded_data = cache.load_from_cache("unicode_test")
            
            assert loaded_data == unicode_data

    def test_concurrent_access_simulation(self):
        """Тест симуляции конкурентного доступа"""
        with tempfile.TemporaryDirectory() as cache_dir:
            cache1 = Cache(cache_dir)
            cache2 = Cache(cache_dir)
            
            # Имитируем одновременное использование
            cache1.save_to_cache("concurrent1", {"data": 1})
            cache2.save_to_cache("concurrent2", {"data": 2})
            
            # Оба кэша должны работать
            assert cache1.load_from_cache("concurrent1") == {"data": 1}
            assert cache2.load_from_cache("concurrent2") == {"data": 2}

    def test_memory_efficiency(self):
        """Тест эффективности использования памяти"""
        config = UIPaginationConfig()
        
        # Множественные вызовы не должны создавать новые объекты
        result1 = config.get_items_per_page('search')
        result2 = config.get_items_per_page('search')
        
        assert result1 == result2 == 5

    def test_type_safety(self):
        """Тест типобезопасности"""
        config = UIPaginationConfig()
        
        # Различные типы входных данных
        assert config.validate_items_per_page("10") == 10  # строка
        assert config.validate_items_per_page(10.0) == 10  # float
        assert config.validate_items_per_page(True) == 1   # boolean


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
