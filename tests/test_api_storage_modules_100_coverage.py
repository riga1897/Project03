"""
100% покрытие API и storage модулей
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.api_modules.base_api import BaseJobAPI
from src.storage.abstract_db_manager import AbstractDBManager
from src.storage.abstract import AbstractVacancyStorage


class TestBaseJobAPI:
    """100% покрытие BaseJobAPI"""

    def test_cannot_instantiate_abstract_class(self):
        """Тест что абстрактный класс нельзя инстанцировать"""
        with pytest.raises(TypeError):
            BaseJobAPI()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return [{"title": f"Job for {search_query}", "id": "1"}]
            
            def _validate_vacancy(self, vacancy):
                return "title" in vacancy and "id" in vacancy
        
        api = ConcreteJobAPI()
        
        # Тест get_vacancies
        vacancies = api.get_vacancies("Python")
        assert len(vacancies) == 1
        assert vacancies[0]["title"] == "Job for Python"
        
        # Тест _validate_vacancy
        valid_vacancy = {"title": "Python Dev", "id": "123"}
        invalid_vacancy = {"title": "Python Dev"}
        
        assert api._validate_vacancy(valid_vacancy) == True
        assert api._validate_vacancy(invalid_vacancy) == False

    @patch('os.path.exists')
    @patch('shutil.rmtree')
    @patch('os.makedirs')
    def test_clear_cache_existing_directory(self, mock_makedirs, mock_rmtree, mock_exists):
        """Тест очистки существующего кэша"""
        mock_exists.return_value = True
        
        class ConcreteJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return []
            def _validate_vacancy(self, vacancy):
                return True
        
        api = ConcreteJobAPI()
        
        with patch('src.api_modules.base_api.logger') as mock_logger:
            api.clear_cache("hh")
            
        mock_rmtree.assert_called_once_with("data/cache/hh")
        mock_makedirs.assert_called_once_with("data/cache/hh", exist_ok=True)
        mock_logger.info.assert_called_once_with("Кэш hh очищен")

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_clear_cache_nonexistent_directory(self, mock_makedirs, mock_exists):
        """Тест создания нового кэша"""
        mock_exists.return_value = False
        
        class ConcreteJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return []
            def _validate_vacancy(self, vacancy):
                return True
        
        api = ConcreteJobAPI()
        
        with patch('src.api_modules.base_api.logger') as mock_logger:
            api.clear_cache("sj")
            
        mock_makedirs.assert_called_once_with("data/cache/sj", exist_ok=True)
        mock_logger.info.assert_called_once_with("Создана папка кэша data/cache/sj")

    @patch('os.path.exists')
    @patch('shutil.rmtree')
    def test_clear_cache_error_handling(self, mock_rmtree, mock_exists):
        """Тест обработки ошибок при очистке кэша"""
        mock_exists.return_value = True
        mock_rmtree.side_effect = Exception("Permission denied")
        
        class ConcreteJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return []
            def _validate_vacancy(self, vacancy):
                return True
        
        api = ConcreteJobAPI()
        
        with patch('src.api_modules.base_api.logger') as mock_logger:
            with pytest.raises(Exception, match="Permission denied"):
                api.clear_cache("test")
            
            mock_logger.error.assert_called_once()

    def test_clear_cache_different_sources(self):
        """Тест очистки кэша для разных источников"""
        class ConcreteJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return []
            def _validate_vacancy(self, vacancy):
                return True
        
        api = ConcreteJobAPI()
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs:
            
            api.clear_cache("hh")
            api.clear_cache("superjob")
            api.clear_cache("custom_source")
            
            expected_calls = [
                (("data/cache/hh",), {"exist_ok": True}),
                (("data/cache/superjob",), {"exist_ok": True}),
                (("data/cache/custom_source",), {"exist_ok": True})
            ]
            
            assert mock_makedirs.call_count == 3
            for call in expected_calls:
                assert call in mock_makedirs.call_args_list


class TestAbstractDBManager:
    """100% покрытие AbstractDBManager"""

    def test_cannot_instantiate_abstract_class(self):
        """Тест что абстрактный класс нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractDBManager()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteDBManager(AbstractDBManager):
            def get_companies_and_vacancies_count(self):
                return [("Company A", 10), ("Company B", 5)]
            
            def get_all_vacancies(self):
                return [{"id": "1", "title": "Job 1"}, {"id": "2", "title": "Job 2"}]
            
            def get_avg_salary(self):
                return 150000.0
            
            def get_vacancies_with_higher_salary(self):
                return [{"id": "3", "salary": 200000}]
            
            def get_vacancies_with_keyword(self, keyword):
                return [{"id": "4", "title": f"Job with {keyword}"}]
            
            def get_database_stats(self):
                return {
                    "total_vacancies": 100,
                    "total_companies": 20,
                    "avg_salary": 150000.0
                }
        
        db_manager = ConcreteDBManager()
        
        # Тест get_companies_and_vacancies_count
        companies = db_manager.get_companies_and_vacancies_count()
        assert len(companies) == 2
        assert companies[0] == ("Company A", 10)
        assert companies[1] == ("Company B", 5)
        
        # Тест get_all_vacancies
        all_vacancies = db_manager.get_all_vacancies()
        assert len(all_vacancies) == 2
        assert all_vacancies[0]["title"] == "Job 1"
        
        # Тест get_avg_salary
        avg_salary = db_manager.get_avg_salary()
        assert avg_salary == 150000.0
        
        # Тест get_vacancies_with_higher_salary
        high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
        assert len(high_salary_vacancies) == 1
        assert high_salary_vacancies[0]["salary"] == 200000
        
        # Тест get_vacancies_with_keyword
        keyword_vacancies = db_manager.get_vacancies_with_keyword("Python")
        assert len(keyword_vacancies) == 1
        assert "Python" in keyword_vacancies[0]["title"]
        
        # Тест get_database_stats
        stats = db_manager.get_database_stats()
        assert stats["total_vacancies"] == 100
        assert stats["total_companies"] == 20
        assert stats["avg_salary"] == 150000.0

    def test_abstract_methods_signature(self):
        """Тест сигнатур абстрактных методов"""
        # Проверяем что все методы определены правильно
        assert hasattr(AbstractDBManager, 'get_companies_and_vacancies_count')
        assert hasattr(AbstractDBManager, 'get_all_vacancies')
        assert hasattr(AbstractDBManager, 'get_avg_salary')
        assert hasattr(AbstractDBManager, 'get_vacancies_with_higher_salary')
        assert hasattr(AbstractDBManager, 'get_vacancies_with_keyword')
        assert hasattr(AbstractDBManager, 'get_database_stats')


class TestAbstractVacancyStorage:
    """100% покрытие AbstractVacancyStorage"""

    def test_cannot_instantiate_abstract_class(self):
        """Тест что абстрактный класс нельзя инстанцировать"""
        with pytest.raises(TypeError):
            AbstractVacancyStorage()

    def test_concrete_implementation_all_methods(self):
        """Тест конкретной реализации всех методов"""
        class ConcreteVacancyStorage(AbstractVacancyStorage):
            def __init__(self):
                self.vacancies = []
            
            def add_vacancy(self, vacancy):
                self.vacancies.append(vacancy)
            
            def get_vacancies(self, filters=None):
                if filters:
                    # Простая фильтрация для теста
                    return [v for v in self.vacancies if filters.get("keyword", "") in v.get("title", "")]
                return self.vacancies
            
            def delete_vacancy(self, vacancy):
                if vacancy in self.vacancies:
                    self.vacancies.remove(vacancy)
            
            def check_vacancies_exist_batch(self, vacancies):
                existing = {}
                for vacancy in vacancies:
                    existing[vacancy.get("id")] = vacancy in self.vacancies
                return existing
            
            def add_vacancy_batch_optimized(self, vacancies, search_query=None):
                added = []
                for vacancy in vacancies:
                    if vacancy not in self.vacancies:
                        self.vacancies.append(vacancy)
                        added.append(vacancy)
                return added
        
        storage = ConcreteVacancyStorage()
        
        # Тест add_vacancy
        vacancy1 = {"id": "1", "title": "Python Developer"}
        storage.add_vacancy(vacancy1)
        assert len(storage.vacancies) == 1
        
        # Тест get_vacancies без фильтров
        all_vacancies = storage.get_vacancies()
        assert len(all_vacancies) == 1
        assert all_vacancies[0] == vacancy1
        
        # Тест get_vacancies с фильтрами
        vacancy2 = {"id": "2", "title": "Java Developer"}
        storage.add_vacancy(vacancy2)
        
        python_vacancies = storage.get_vacancies({"keyword": "Python"})
        assert len(python_vacancies) == 1
        assert python_vacancies[0] == vacancy1
        
        # Тест delete_vacancy
        storage.delete_vacancy(vacancy1)
        assert len(storage.vacancies) == 1
        assert vacancy1 not in storage.vacancies
        
        # Тест check_vacancies_exist_batch
        test_vacancies = [vacancy1, vacancy2, {"id": "3", "title": "C++ Dev"}]
        exists_check = storage.check_vacancies_exist_batch(test_vacancies)
        assert exists_check["1"] == False  # vacancy1 был удален
        assert exists_check["2"] == True   # vacancy2 существует
        assert exists_check["3"] == False  # vacancy3 не существует
        
        # Тест add_vacancy_batch_optimized
        new_vacancies = [
            {"id": "3", "title": "C++ Developer"},
            {"id": "4", "title": "Go Developer"},
            vacancy2  # уже существует
        ]
        added = storage.add_vacancy_batch_optimized(new_vacancies)
        assert len(added) == 2  # vacancy2 уже был, поэтому добавлено только 2
        assert len(storage.vacancies) == 3  # всего стало 3


class TestStorageFactory:
    """100% покрытие storage_factory"""

    def test_storage_factory_imports(self):
        """Тест импорта StorageFactory"""
        from src.storage.storage_factory import StorageFactory
        assert StorageFactory is not None

    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.postgres_saver.PostgresSaver')
    def test_create_storage_success(self, mock_postgres_saver, mock_app_config):
        """Тест успешного создания хранилища"""
        from src.storage.storage_factory import StorageFactory
        
        # Настраиваем моки
        mock_config_instance = Mock()
        mock_config_instance.get_db_config.return_value = {
            "host": "localhost",
            "port": "5432",
            "database": "test_db"
        }
        mock_app_config.return_value = mock_config_instance
        
        mock_storage_instance = Mock()
        mock_postgres_saver.return_value = mock_storage_instance
        
        # Вызываем метод
        result = StorageFactory.create_storage("postgres")
        
        # Проверяем результат
        assert result == mock_storage_instance
        mock_app_config.assert_called_once()
        mock_postgres_saver.assert_called_once()

    def test_create_storage_invalid_type(self):
        """Тест создания хранилища с невалидным типом"""
        from src.storage.storage_factory import StorageFactory
        
        with pytest.raises(ValueError, match="Поддерживается только PostgreSQL хранилище"):
            StorageFactory.create_storage("mysql")

    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.postgres_saver.PostgresSaver')
    def test_create_storage_default_type(self, mock_postgres_saver, mock_app_config):
        """Тест создания хранилища с дефолтным типом"""
        from src.storage.storage_factory import StorageFactory
        
        # Настраиваем моки
        mock_config_instance = Mock()
        mock_config_instance.get_db_config.return_value = {"host": "localhost"}
        mock_app_config.return_value = mock_config_instance
        
        mock_storage_instance = Mock()
        mock_postgres_saver.return_value = mock_storage_instance
        
        # Вызываем метод без параметров (должен использовать дефолт "postgres")
        result = StorageFactory.create_storage()
        
        assert result == mock_storage_instance
        mock_postgres_saver.assert_called_once()

    @patch('src.storage.storage_factory.StorageFactory.create_storage')
    def test_get_default_storage(self, mock_create_storage):
        """Тест получения дефолтного хранилища"""
        from src.storage.storage_factory import StorageFactory
        
        mock_storage = Mock()
        mock_create_storage.return_value = mock_storage
        
        result = StorageFactory.get_default_storage()
        
        assert result == mock_storage
        mock_create_storage.assert_called_once_with("postgres")

    @patch('src.config.app_config.AppConfig')
    def test_create_storage_config_error(self, mock_app_config):
        """Тест обработки ошибки конфигурации"""
        from src.storage.storage_factory import StorageFactory
        
        mock_app_config.side_effect = Exception("Config error")
        
        with pytest.raises(Exception, match="Config error"):
            StorageFactory.create_storage("postgres")

    @patch('src.config.app_config.AppConfig')
    @patch('src.storage.postgres_saver.PostgresSaver')
    def test_create_storage_postgres_error(self, mock_postgres_saver, mock_app_config):
        """Тест обработки ошибки создания PostgresSaver"""
        from src.storage.storage_factory import StorageFactory
        
        # Настраиваем успешную конфигурацию
        mock_config_instance = Mock()
        mock_config_instance.get_db_config.return_value = {"host": "localhost"}
        mock_app_config.return_value = mock_config_instance
        
        # Мокируем ошибку PostgresSaver
        mock_postgres_saver.side_effect = Exception("DB connection failed")
        
        with pytest.raises(Exception, match="DB connection failed"):
            StorageFactory.create_storage("postgres")


class TestAPIStorageIntegration:
    """Интеграционные тесты API и storage модулей"""

    def test_api_storage_workflow_simulation(self):
        """Тест симуляции полного рабочего процесса"""
        # Создаем конкретные реализации
        class TestJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return [
                    {"id": "1", "title": f"{search_query} Developer", "company": "Tech Corp"},
                    {"id": "2", "title": f"Senior {search_query} Engineer", "company": "Startup Inc"}
                ]
            
            def _validate_vacancy(self, vacancy):
                return all(key in vacancy for key in ["id", "title", "company"])
        
        class TestVacancyStorage(AbstractVacancyStorage):
            def __init__(self):
                self.data = []
            
            def add_vacancy(self, vacancy):
                self.data.append(vacancy)
            
            def get_vacancies(self, filters=None):
                return self.data
            
            def delete_vacancy(self, vacancy):
                if vacancy in self.data:
                    self.data.remove(vacancy)
            
            def check_vacancies_exist_batch(self, vacancies):
                return {v.get("id"): v in self.data for v in vacancies}
            
            def add_vacancy_batch_optimized(self, vacancies, search_query=None):
                added = []
                for v in vacancies:
                    if v not in self.data:
                        self.data.append(v)
                        added.append(v)
                return added
        
        # Симулируем рабочий процесс
        api = TestJobAPI()
        storage = TestVacancyStorage()
        
        # 1. Получаем вакансии из API
        vacancies = api.get_vacancies("Python")
        assert len(vacancies) == 2
        
        # 2. Валидируем вакансии
        valid_vacancies = [v for v in vacancies if api._validate_vacancy(v)]
        assert len(valid_vacancies) == 2
        
        # 3. Сохраняем в хранилище
        added = storage.add_vacancy_batch_optimized(valid_vacancies)
        assert len(added) == 2
        
        # 4. Получаем из хранилища
        stored_vacancies = storage.get_vacancies()
        assert len(stored_vacancies) == 2
        assert stored_vacancies[0]["title"] == "Python Developer"

    def test_error_handling_comprehensive(self):
        """Комплексное тестирование обработки ошибок"""
        # Тест API с ошибками
        class ErrorJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                if search_query == "error":
                    raise Exception("API Error")
                return []
            
            def _validate_vacancy(self, vacancy):
                return vacancy.get("valid", False)
        
        api = ErrorJobAPI()
        
        # Тест обработки ошибки в get_vacancies
        with pytest.raises(Exception, match="API Error"):
            api.get_vacancies("error")
        
        # Тест валидации
        valid_vacancy = {"valid": True}
        invalid_vacancy = {"valid": False}
        
        assert api._validate_vacancy(valid_vacancy) == True
        assert api._validate_vacancy(invalid_vacancy) == False

    def test_logging_integration(self):
        """Тест интеграции с системой логирования"""
        class LoggingJobAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                logging.getLogger(__name__).info(f"Searching for: {search_query}")
                return []
            
            def _validate_vacancy(self, vacancy):
                return True
        
        api = LoggingJobAPI()
        
        with patch('src.api_modules.base_api.logger') as mock_logger:
            # Очистка кэша вызовет логирование
            with patch('os.path.exists', return_value=False), \
                 patch('os.makedirs'):
                api.clear_cache("test")
                
            mock_logger.info.assert_called_once()

    def test_inheritance_and_polymorphism(self):
        """Тест наследования и полиморфизма"""
        apis = []
        storages = []
        
        # Создаем разные реализации API
        class HHAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return [{"source": "hh", "query": search_query}]
            def _validate_vacancy(self, vacancy):
                return "source" in vacancy
        
        class SJAPI(BaseJobAPI):
            def get_vacancies(self, search_query, **kwargs):
                return [{"source": "sj", "query": search_query}]
            def _validate_vacancy(self, vacancy):
                return "source" in vacancy
        
        apis.extend([HHAPI(), SJAPI()])
        
        # Тест полиморфного поведения
        results = []
        for api in apis:
            vacancies = api.get_vacancies("test")
            results.extend(vacancies)
        
        assert len(results) == 2
        assert results[0]["source"] == "hh"
        assert results[1]["source"] == "sj"