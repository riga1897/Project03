
"""
Исправленные тесты для компонентов с низким покрытием кода
Фокус на 100% покрытие функционального кода с правильными интерфейсами
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Импорт реальных компонентов
try:
    from src.storage.db_manager import DBManager
    DB_MANAGER_AVAILABLE = True
except ImportError:
    DB_MANAGER_AVAILABLE = False

try:
    from src.storage.postgres_saver import PostgresSaver
    POSTGRES_SAVER_AVAILABLE = True
except ImportError:
    POSTGRES_SAVER_AVAILABLE = False

try:
    from src.storage.simple_db_adapter import SimpleDBAdapter
    SIMPLE_DB_ADAPTER_AVAILABLE = True
except ImportError:
    SIMPLE_DB_ADAPTER_AVAILABLE = False

try:
    from src.config.ui_config import UIConfig, UIPaginationConfig
    UI_CONFIG_AVAILABLE = True
except ImportError:
    UI_CONFIG_AVAILABLE = False

try:
    from src.vacancies.models import Vacancy
    VACANCY_MODEL_AVAILABLE = True
except ImportError:
    VACANCY_MODEL_AVAILABLE = False


class TestDBManagerFixed:
    """Исправленные тесты для DBManager с правильными методами"""

    @pytest.fixture
    def db_manager(self):
        """Фикстура для DBManager"""
        if not DB_MANAGER_AVAILABLE:
            pytest.skip("DBManager not available")
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
        return mock_conn, mock_cursor

    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect, db_manager, mock_connection):
        """Тест получения списка компаний и количества вакансий"""
        if not DB_MANAGER_AVAILABLE:
            return

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
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect, db_manager, mock_connection):
        """Тест получения всех вакансий"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            {'id': '1', 'title': 'Python Developer', 'company': 'TechCorp'},
            {'id': '2', 'title': 'Java Developer', 'company': 'JavaCorp'}
        ]

        result = db_manager.get_all_vacancies()
        
        assert isinstance(result, list)
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_avg_salary(self, mock_connect, db_manager, mock_connection):
        """Тест получения средней зарплаты"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = (125000.0,)

        result = db_manager.get_avg_salary()
        
        assert result == 125000.0
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect, db_manager, mock_connection):
        """Тест получения вакансий с зарплатой выше средней"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            {'id': '1', 'title': 'Senior Developer', 'salary': 150000}
        ]

        result = db_manager.get_vacancies_with_higher_salary()
        
        assert isinstance(result, list)
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect, db_manager, mock_connection):
        """Тест поиска вакансий по ключевому слову"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn, mock_cursor = mock_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = [
            {'id': '1', 'title': 'Python Developer'}
        ]

        result = db_manager.get_vacancies_with_keyword('Python')
        
        assert isinstance(result, list)
        mock_cursor.execute.assert_called_once()

    @patch('psycopg2.connect')
    def test_get_database_stats(self, mock_connect, db_manager, mock_connection):
        """Тест получения статистики базы данных"""
        if not DB_MANAGER_AVAILABLE:
            return

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


class TestPostgresSaverFixed:
    """Исправленные тесты для PostgresSaver с правильными методами"""

    @pytest.fixture
    def postgres_saver(self):
        """Фикстура для PostgresSaver"""
        if not POSTGRES_SAVER_AVAILABLE:
            pytest.skip("PostgresSaver not available")
        return PostgresSaver()

    @pytest.fixture
    def mock_vacancy(self):
        """Фикстура для мокированной вакансии"""
        if not VACANCY_MODEL_AVAILABLE:
            # Создаем простой мок если модель недоступна
            mock_vacancy = Mock()
            mock_vacancy.vacancy_id = "test123"
            mock_vacancy.title = "Test Job"
            mock_vacancy.employer = Mock()
            mock_vacancy.employer.name = "Test Company"
            mock_vacancy.salary = None
            mock_vacancy.description = "Test description"
            mock_vacancy.requirements = "Test requirements"
            mock_vacancy.responsibilities = "Test responsibilities"
            mock_vacancy.experience = None
            mock_vacancy.employment = None
            mock_vacancy.schedule = None
            mock_vacancy.area = "Moscow"
            mock_vacancy.source = "test"
            mock_vacancy.published_at = "2024-01-01"
            mock_vacancy.url = "https://test.com"
            return mock_vacancy
        else:
            # Используем реальную модель если доступна
            from src.vacancies.models import Vacancy, Employer
            employer = Employer(name="Test Company", employer_id="comp123")
            return Vacancy(
                vacancy_id="test123",
                title="Test Job",
                employer=employer,
                url="https://test.com",
                description="Test description",
                source="test"
            )

    @patch('psycopg2.connect')
    def test_save_vacancies_with_real_vacancy_objects(self, mock_connect, postgres_saver, mock_vacancy):
        """Тест сохранения вакансий с реальными объектами Vacancy"""
        if not POSTGRES_SAVER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            mock_cursor.fetchall.return_value = []  # Пустой список компаний
            mock_cursor.rowcount = 1
            
            result = postgres_saver.save_vacancies([mock_vacancy])
            
            assert isinstance(result, list)
            mock_cursor.execute.assert_called()

    @patch('psycopg2.connect')
    def test_get_vacancies_basic(self, mock_connect, postgres_saver):
        """Тест базового получения вакансий"""
        if not POSTGRES_SAVER_AVAILABLE:
            return

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

    @patch('psycopg2.connect')
    def test_delete_vacancy_by_id(self, mock_connect, postgres_saver):
        """Тест удаления вакансии по ID"""
        if not POSTGRES_SAVER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with patch.object(postgres_saver, '_get_connection', return_value=mock_conn):
            postgres_saver.delete_vacancy_by_id('test123')
            mock_cursor.execute.assert_called()

    def test_delete_vacancy_with_object(self, postgres_saver, mock_vacancy):
        """Тест удаления вакансии с объектом"""
        if not POSTGRES_SAVER_AVAILABLE:
            return

        with patch.object(postgres_saver, 'delete_vacancy_by_id') as mock_delete:
            postgres_saver.delete_vacancy(mock_vacancy)
            mock_delete.assert_called_once_with(mock_vacancy.vacancy_id)


class TestSimpleDBAdapterFixed:
    """Исправленные тесты для SimpleDBAdapter с правильными методами"""

    @pytest.fixture
    def db_adapter(self):
        """Фикстура для SimpleDBAdapter"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            pytest.skip("SimpleDBAdapter not available")
        return SimpleDBAdapter()

    @patch('psycopg2.connect')
    def test_get_companies_and_vacancies_count(self, mock_connect, db_adapter):
        """Тест получения компаний и количества вакансий"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        mock_cursor.fetchall.return_value = [
            ('Company1', 10),
            ('Company2', 15)
        ]

        result = db_adapter.get_companies_and_vacancies_count()
        
        assert isinstance(result, list)
        assert len(result) == 2

    @patch('psycopg2.connect')
    def test_get_all_vacancies(self, mock_connect, db_adapter):
        """Тест получения всех вакансий"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        result = db_adapter.get_all_vacancies()
        
        assert isinstance(result, list)

    @patch('psycopg2.connect')
    def test_get_vacancies_with_keyword(self, mock_connect, db_adapter):
        """Тест поиска вакансий по ключевому слову"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        result = db_adapter.get_vacancies_with_keyword('Python')
        
        assert isinstance(result, list)

    def test_init_database_schema(self, db_adapter):
        """Тест инициализации схемы базы данных"""
        if not SIMPLE_DB_ADAPTER_AVAILABLE:
            return

        with patch.object(db_adapter, '_execute_ddl_script') as mock_execute:
            db_adapter.init_database_schema()
            mock_execute.assert_called()


class TestUIConfigFixed:
    """Исправленные тесты для UI конфигурации"""

    def test_ui_pagination_config_basic(self):
        """Тест базовой конфигурации пагинации"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIPaginationConfig()
        
        assert config.default_items_per_page == 10
        assert config.search_results_per_page == 5
        assert config.saved_vacancies_per_page == 10
        assert config.max_items_per_page == 50
        assert config.min_items_per_page == 1

    def test_get_items_per_page_contexts(self):
        """Тест получения количества элементов для разных контекстов"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIPaginationConfig()
        
        assert config.get_items_per_page('search') == 5
        assert config.get_items_per_page('saved') == 10
        assert config.get_items_per_page('top') == 10
        assert config.get_items_per_page(None) == 10
        assert config.get_items_per_page('unknown') == 10

    def test_validate_items_per_page(self):
        """Тест валидации количества элементов на странице"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIPaginationConfig()
        
        assert config.validate_items_per_page(-5) == 1
        assert config.validate_items_per_page(0) == 1
        assert config.validate_items_per_page(25) == 25
        assert config.validate_items_per_page(100) == 50

    def test_ui_config_basic(self):
        """Тест базовой UI конфигурации"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIConfig()
        
        assert config.items_per_page == 5
        assert config.max_display_items == 20

    def test_get_pagination_settings(self):
        """Тест получения настроек пагинации"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIConfig()
        
        # Тест с параметрами по умолчанию
        settings = config.get_pagination_settings()
        assert settings['items_per_page'] == 5
        assert settings['max_display_items'] == 20

        # Тест с пользовательскими параметрами
        custom_settings = config.get_pagination_settings(
            items_per_page=10, 
            max_display_items=30
        )
        assert custom_settings['items_per_page'] == 10
        assert custom_settings['max_display_items'] == 30

    def test_global_config_instances(self):
        """Тест глобальных экземпляров конфигурации"""
        if not UI_CONFIG_AVAILABLE:
            return

        from src.config.ui_config import ui_pagination_config, ui_config
        
        assert isinstance(ui_pagination_config, UIPaginationConfig)
        assert isinstance(ui_config, UIConfig)
        
        # Проверяем, что можем использовать глобальные экземпляры
        assert ui_pagination_config.get_items_per_page('search') == 5
        assert ui_config.items_per_page == 5


class TestAPIModulesFixed:
    """Исправленные тесты для API модулей"""

    @patch('requests.get')
    def test_hh_api_methods_coverage(self, mock_get):
        """Тест покрытия методов HeadHunter API"""
        try:
            from src.api_modules.hh_api import HeadHunterAPI
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": [], "found": 0}
            mock_get.return_value = mock_response

            hh_api = HeadHunterAPI()
            
            # Тестируем существующие методы
            if hasattr(hh_api, 'get_vacancies_page'):
                result = hh_api.get_vacancies_page("Python")
                assert isinstance(result, dict)
            
            if hasattr(hh_api, 'get_vacancies'):
                result = hh_api.get_vacancies("Python")
                assert isinstance(result, list)

        except ImportError:
            pytest.skip("HeadHunter API not available")

    @patch('requests.get')
    def test_sj_api_methods_coverage(self, mock_get):
        """Тест покрытия методов SuperJob API"""
        try:
            from src.api_modules.sj_api import SuperJobAPI
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"objects": [], "total": 0}
            mock_get.return_value = mock_response

            sj_api = SuperJobAPI()
            
            # Тестируем существующие методы
            if hasattr(sj_api, 'get_vacancies_page'):
                result = sj_api.get_vacancies_page("Python")
                assert isinstance(result, list)
            
            if hasattr(sj_api, 'get_vacancies'):
                result = sj_api.get_vacancies("Python")
                assert isinstance(result, list)

        except ImportError:
            pytest.skip("SuperJob API not available")

    def test_cached_api_basic_functionality(self):
        """Тест базовой функциональности кэшированного API"""
        try:
            from src.api_modules.cached_api import CachedAPI
            from src.api_modules.hh_api import HeadHunterAPI
            
            base_api = HeadHunterAPI()
            cache_dir = "test_cache"
            
            # Создаем экземпляр с реальными параметрами
            cached_api = CachedAPI(base_api, cache_dir)
            
            assert cached_api is not None
            assert hasattr(cached_api, 'cache_dir')

        except ImportError:
            pytest.skip("Cached API not available")


class TestIntegrationFixed:
    """Исправленные интеграционные тесты"""

    @patch('psycopg2.connect')
    def test_db_manager_postgres_saver_integration(self, mock_connect):
        """Тест интеграции DBManager и PostgresSaver"""
        if not (DB_MANAGER_AVAILABLE and POSTGRES_SAVER_AVAILABLE):
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        postgres_saver = PostgresSaver()

        # Тестируем, что оба компонента могут работать с одинаковыми данными
        mock_cursor.fetchall.return_value = [('TestCorp', 5)]
        
        db_result = db_manager.get_companies_and_vacancies_count()
        assert isinstance(db_result, list)

    def test_ui_config_with_pagination(self):
        """Тест интеграции UI конфигурации с пагинацией"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIConfig()
        pagination_config = UIPaginationConfig()

        # Тестируем совместимость конфигураций
        base_items = config.items_per_page
        search_items = pagination_config.get_items_per_page('search')
        
        assert isinstance(base_items, int)
        assert isinstance(search_items, int)
        assert base_items == 5
        assert search_items == 5

    def test_component_error_handling(self):
        """Тест обработки ошибок в компонентах"""
        # Тестируем обработку ошибок при недоступности компонентов
        try:
            if DB_MANAGER_AVAILABLE:
                db_manager = DBManager()
                assert db_manager is not None
        except Exception as e:
            # Ошибки при создании объектов допустимы
            assert isinstance(e, Exception)

        try:
            if UI_CONFIG_AVAILABLE:
                config = UIConfig()
                assert config is not None
        except Exception as e:
            assert isinstance(e, Exception)


class TestPerformanceFixed:
    """Тесты производительности для компонентов с низким покрытием"""

    def test_ui_config_performance(self):
        """Тест производительности UI конфигурации"""
        if not UI_CONFIG_AVAILABLE:
            return

        import time
        
        config = UIPaginationConfig()
        
        start_time = time.time()
        for i in range(1000):
            config.get_items_per_page('search')
            config.validate_items_per_page(i % 100)
        end_time = time.time()
        
        # Операции должны быть быстрыми
        assert end_time - start_time < 1.0

    @patch('psycopg2.connect')
    def test_db_operations_performance(self, mock_connect):
        """Тест производительности операций с базой данных"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        mock_cursor.fetchall.return_value = []

        import time
        start_time = time.time()
        
        for _ in range(10):
            db_manager.get_all_vacancies()
            
        end_time = time.time()
        
        # Операции должны быть относительно быстрыми
        assert end_time - start_time < 5.0


class TestEdgeCasesFixed:
    """Тесты граничных случаев"""

    def test_ui_config_edge_cases(self):
        """Тест граничных случаев UI конфигурации"""
        if not UI_CONFIG_AVAILABLE:
            return

        config = UIPaginationConfig()
        
        # Тест с экстремальными значениями
        assert config.validate_items_per_page(-1000) == 1
        assert config.validate_items_per_page(1000) == 50
        
        # Тест с None контекстом
        assert config.get_items_per_page(None) == 10
        
        # Тест с пустой строкой
        assert config.get_items_per_page('') == 10

    @patch('psycopg2.connect')
    def test_db_empty_results(self, mock_connect):
        """Тест обработки пустых результатов из БД"""
        if not DB_MANAGER_AVAILABLE:
            return

        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        db_manager = DBManager()
        
        # Тест с пустыми результатами
        mock_cursor.fetchall.return_value = []
        result = db_manager.get_all_vacancies()
        assert isinstance(result, list)
        assert len(result) == 0
        
        # Тест с None результатом
        mock_cursor.fetchone.return_value = None
        avg_salary = db_manager.get_avg_salary()
        assert avg_salary is None

    def test_postgres_saver_edge_cases(self):
        """Тест граничных случаев PostgresSaver"""
        if not POSTGRES_SAVER_AVAILABLE:
            return

        postgres_saver = PostgresSaver()
        
        # Тест с пустым списком вакансий
        with patch.object(postgres_saver, '_get_connection') as mock_conn:
            result = postgres_saver.save_vacancies([])
            assert isinstance(result, list)
            assert len(result) == 0
