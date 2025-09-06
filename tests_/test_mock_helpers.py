
"""
Вспомогательные классы и функции для правильного мокирования в тестах
"""

from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class IterableMock(Mock):
    """Мок который можно безопасно итерировать"""
    
    def __init__(self, iterable_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._iterable_data = iterable_data or []
        self.__iter__ = Mock(return_value=iter(self._iterable_data))
    
    def __getitem__(self, index):
        return self._iterable_data[index]
    
    def __len__(self):
        return len(self._iterable_data)


class DatabaseMockHelper:
    """Помощник для создания моков базы данных"""
    
    @staticmethod
    def create_connection_mock(cursor_results=None):
        """Создает мок подключения к БД с правильными context managers"""
        mock_conn = Mock()
        mock_cursor = Mock()
        
        # Context managers
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        
        # Cursor configuration
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)
        
        # Results configuration
        if cursor_results:
            if isinstance(cursor_results, list):
                mock_cursor.fetchall.return_value = IterableMock(cursor_results)
            else:
                mock_cursor.fetchone.return_value = cursor_results
        else:
            mock_cursor.fetchall.return_value = IterableMock([])
            mock_cursor.fetchone.return_value = None
        
        mock_cursor.rowcount = 0
        
        return mock_conn, mock_cursor
    
    @staticmethod
    def create_postgres_saver_mock():
        """Создает мок PostgresSaver с безопасными методами"""
        mock_saver = Mock()
        
        # Основные методы
        mock_saver.save_vacancies.return_value = 0
        mock_saver.get_vacancies.return_value = []
        mock_saver.delete_vacancy_by_id.return_value = True
        mock_saver.is_vacancy_exists.return_value = False
        
        # Методы подключения
        mock_saver._get_connection.return_value = None
        
        return mock_saver


class APIMockHelper:
    """Помощник для создания моков API"""
    
    @staticmethod
    def create_response_mock(status_code=200, json_data=None):
        """Создает мок HTTP ответа"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {"items": [], "found": 0}
        return mock_response
    
    @staticmethod
    def create_api_mock(response_data=None):
        """Создает мок API с методами"""
        mock_api = Mock()
        
        default_response = response_data or []
        
        # API методы
        mock_api.get_vacancies.return_value = default_response
        mock_api.get_vacancies_page.return_value = default_response
        mock_api.search_vacancies.return_value = default_response
        
        # Методы валидации
        mock_api._validate_vacancy.return_value = True
        mock_api._get_empty_response.return_value = {"items": [], "found": 0}
        
        return mock_api


class CacheMockHelper:
    """Помощник для создания моков кэша"""
    
    @staticmethod
    def create_cache_mock():
        """Создает мок кэша с методами"""
        mock_cache = Mock()
        
        # Основные методы
        mock_cache.save_response.return_value = None
        mock_cache.load_response.return_value = None
        mock_cache.clear.return_value = None
        mock_cache.exists.return_value = False
        
        # Методы валидации
        mock_cache.is_valid_response.return_value = True
        mock_cache._is_valid.return_value = True
        
        return mock_cache
    
    @staticmethod
    def create_file_cache_mock(cache_dir="/tmp/test"):
        """Создает мок FileCache"""
        mock_cache = CacheMockHelper.create_cache_mock()
        mock_cache.cache_dir = cache_dir
        return mock_cache


class ModelMockHelper:
    """Помощник для создания моков моделей"""
    
    @staticmethod
    def create_vacancy_mock(vacancy_id="test123", title="Test Job"):
        """Создает мок вакансии"""
        mock_vacancy = Mock()
        
        # Основные атрибуты
        mock_vacancy.vacancy_id = vacancy_id
        mock_vacancy.id = vacancy_id
        mock_vacancy.title = title
        mock_vacancy.name = title
        mock_vacancy.url = f"https://example.com/vacancy/{vacancy_id}"
        mock_vacancy.alternate_url = mock_vacancy.url
        
        # Работодатель
        mock_vacancy.employer = Mock()
        mock_vacancy.employer.name = "Test Company"
        mock_vacancy.employer.id = "comp123"
        mock_vacancy.employer.employer_id = "comp123"
        
        # Зарплата
        mock_vacancy.salary = Mock()
        mock_vacancy.salary.salary_from = 100000
        mock_vacancy.salary.salary_to = 150000
        mock_vacancy.salary.currency = "RUR"
        
        # Дополнительные поля
        mock_vacancy.description = "Test description"
        mock_vacancy.requirements = "Test requirements"
        mock_vacancy.area = Mock()
        mock_vacancy.area.name = "Москва"
        mock_vacancy.published_at = "2025-01-01T00:00:00+0300"
        mock_vacancy.source = "test"
        
        # Методы
        mock_vacancy.to_dict.return_value = {
            'id': vacancy_id,
            'title': title,
            'url': mock_vacancy.url
        }
        
        return mock_vacancy
    
    @staticmethod
    def create_employer_mock(name="Test Company", employer_id="comp123"):
        """Создает мок работодателя"""
        mock_employer = Mock()
        mock_employer.name = name
        mock_employer.id = employer_id
        mock_employer.employer_id = employer_id
        return mock_employer
    
    @staticmethod
    def create_salary_mock(salary_from=100000, salary_to=150000, currency="RUR"):
        """Создает мок зарплаты"""
        mock_salary = Mock()
        mock_salary.salary_from = salary_from
        mock_salary.salary_to = salary_to
        mock_salary.currency = currency
        return mock_salary


class UIComponentsMockHelper:
    """Помощник для создания моков UI компонентов"""
    
    @staticmethod
    def create_display_handler_mock():
        """Создает мок обработчика отображения"""
        mock_handler = Mock()
        mock_handler.display_vacancies.return_value = None
        mock_handler.display_vacancy_details.return_value = None
        mock_handler.show_vacancies.return_value = None
        return mock_handler
    
    @staticmethod
    def create_search_handler_mock():
        """Создает мок обработчика поиска"""
        mock_handler = Mock()
        mock_handler.search_vacancies.return_value = []
        mock_handler.handle_search.return_value = None
        return mock_handler
    
    @staticmethod
    def create_menu_manager_mock():
        """Создает мок менеджера меню"""
        mock_manager = Mock()
        mock_manager.display_menu.return_value = None
        mock_manager.show_menu.return_value = None
        mock_manager.get_user_choice.return_value = "0"
        return mock_manager
    
    @staticmethod
    def create_paginator_mock(page_size=10):
        """Создает мок пагинатора"""
        mock_paginator = Mock()
        mock_paginator.page_size = page_size
        mock_paginator.current_page = 0
        mock_paginator.total_pages = 0
        
        mock_paginator.get_page.return_value = []
        mock_paginator.next_page.return_value = True
        mock_paginator.previous_page.return_value = True
        mock_paginator.has_next_page.return_value = False
        mock_paginator.has_previous_page.return_value = False
        
        return mock_paginator


class ConfigMockHelper:
    """Помощник для создания моков конфигурации"""
    
    @staticmethod
    def create_app_config_mock():
        """Создает мок конфигурации приложения"""
        mock_config = Mock()
        
        # Основные настройки
        mock_config.database_url = "postgresql://localhost/test"
        mock_config.api_timeout = 30
        mock_config.cache_ttl = 3600
        mock_config.debug = False
        
        # Методы
        mock_config.get_setting.return_value = "default_value"
        mock_config.update_setting.return_value = None
        mock_config.load_config.return_value = {}
        
        return mock_config
    
    @staticmethod
    def create_db_config_mock():
        """Создает мок конфигурации БД"""
        mock_config = Mock()
        
        mock_config.host = "localhost"
        mock_config.port = 5432
        mock_config.database = "test_db"
        mock_config.user = "test_user"
        mock_config.password = "test_pass"
        
        mock_config.get_connection_params.return_value = {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass"
        }
        
        mock_config.get_database_url.return_value = "postgresql://test_user:test_pass@localhost:5432/test_db"
        
        return mock_config


class ServiceMockHelper:
    """Помощник для создания моков сервисов"""
    
    @staticmethod
    def create_filtering_service_mock():
        """Создает мок сервиса фильтрации"""
        mock_service = Mock()
        mock_strategy = Mock()
        mock_strategy.filter.return_value = []
        
        mock_service.strategy = mock_strategy
        mock_service.filter.return_value = []
        mock_service.filter_by_salary.return_value = []
        mock_service.filter_by_keyword.return_value = []
        
        return mock_service
    
    @staticmethod
    def create_deduplication_service_mock():
        """Создает мок сервиса дедупликации"""
        mock_service = Mock()
        mock_strategy = Mock()
        mock_strategy.deduplicate.return_value = []
        
        mock_service.strategy = mock_strategy
        mock_service.deduplicate.return_value = []
        mock_service.deduplicate_by_id.return_value = []
        
        return mock_service
    
    @staticmethod
    def create_storage_service_mock():
        """Создает мок сервиса хранения"""
        mock_service = Mock()
        
        mock_service.get_vacancies.return_value = []
        mock_service.save_vacancies.return_value = 0
        mock_service.delete_vacancy.return_value = True
        mock_service.get_storage_stats.return_value = {"total": 0}
        
        return mock_service


# Функции-утилиты для быстрого создания моков
def quick_db_mock():
    """Быстрое создание мока БД"""
    return DatabaseMockHelper.create_connection_mock()

def quick_api_mock():
    """Быстрое создание мока API"""
    return APIMockHelper.create_api_mock()

def quick_cache_mock():
    """Быстрое создание мока кэша"""
    return CacheMockHelper.create_cache_mock()

def quick_vacancy_mock():
    """Быстрое создание мока вакансии"""
    return ModelMockHelper.create_vacancy_mock()
