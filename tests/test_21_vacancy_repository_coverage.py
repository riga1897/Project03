#!/usr/bin/env python3
"""
Тесты модуля vacancy_repository для 100% покрытия.

Покрывает все функции в src/storage/components/vacancy_repository.py:
- VacancyRepository - репозиторий для работы с вакансиями (наследует AbstractVacancyStorage)
- __init__ - инициализация с db_connection и validator
- add_vacancy - добавление вакансии с валидацией
- get_vacancies - получение вакансий с фильтрами
- delete_vacancy - удаление вакансии
- check_vacancies_exist_batch - проверка существования пакета вакансий
- add_vacancy_batch_optimized - оптимизированное пакетное добавление

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from unittest.mock import patch, Mock
from typing import Any, Dict, List


# Импорты из реального кода для покрытия
from src.storage.components.vacancy_repository import VacancyRepository
from src.storage.components.database_connection import DatabaseConnection
from src.storage.components.vacancy_validator import VacancyValidator
from src.vacancies.abstract import AbstractVacancy


class MockAbstractVacancy(AbstractVacancy):
    """Mock объект для AbstractVacancy"""
    def __init__(self, vacancy_id: str, title: str = "Test Job", url: str = "https://test.com"):
        self.id = vacancy_id
        self.vacancy_id = vacancy_id
        self.title = title
        self.url = url
        self.salary = None
        self.description = "Test description"
        self.requirements = "Test requirements"
        self.responsibilities = "Test responsibilities"
        self.experience = "middle"
        self.employment = "full_time"
        self.area = "Moscow"
        self.source = "test"
        self.employer = "Test Company"
        self.published_at = None
        self.company_id = None
        self.schedule = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует вакансию в словарь"""
        return {
            "id": self.id,
            "vacancy_id": self.vacancy_id,
            "title": self.title,
            "url": self.url,
            "salary": self.salary,
            "description": self.description,
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
            "experience": self.experience,
            "employment": self.employment,
            "area": self.area,
            "source": self.source,
            "employer": self.employer,
            "published_at": self.published_at,
            "company_id": self.company_id,
            "schedule": self.schedule
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockAbstractVacancy":
        """Создает объект вакансии из словаря"""
        instance = cls(data.get("vacancy_id", ""), data.get("title", ""), data.get("url", ""))
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


class MockDatabaseConnection(DatabaseConnection):
    """Mock объект для DatabaseConnection"""
    def __init__(self) -> None:
        # Не вызываем super().__init__() чтобы избежать реального подключения к БД
        self._connection_params = {}
        self._connection = None
        # Создаем mock объекты
        self.mock_get_connection = Mock()
        self.mock_connection = Mock()
        self.mock_cursor = Mock()

        # Настройка контекстного менеджера для подключения
        self.mock_connection.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_connection.__exit__ = Mock(return_value=None)

        # Настройка контекстного менеджера для курсора
        self.mock_cursor.__enter__ = Mock(return_value=self.mock_cursor)
        self.mock_cursor.__exit__ = Mock(return_value=None)

        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_get_connection.return_value = self.mock_connection

    def get_connection(self) -> Any:
        """Переопределяем для использования mock"""
        return self.mock_get_connection()

    def close_connection(self) -> None:
        """Переопределяем для использования mock"""
        pass

    def __enter__(self) -> Any:
        """Контекстный менеджер - вход"""
        return self.get_connection()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Контекстный менеджер - выход"""
        self.close_connection()


class MockVacancyValidator(VacancyValidator):
    """Mock объект для VacancyValidator"""
    def __init__(self) -> None:
        super().__init__()
        self.mock_validate_vacancy = Mock(return_value=True)
        self.mock_get_validation_errors = Mock(return_value=[])
        self.mock_validate_batch = Mock(return_value={})

    def validate_vacancy(self, vacancy: AbstractVacancy) -> Any:
        """Переопределяем для использования mock"""
        return self.mock_validate_vacancy(vacancy)

    def get_validation_errors(self) -> Any:
        """Переопределяем для использования mock"""
        return self.mock_get_validation_errors()

    def validate_batch(self, vacancies: List[AbstractVacancy]) -> Any:
        """Переопределяем для использования mock"""
        return self.mock_validate_batch(vacancies)


class TestVacancyRepository:
    """100% покрытие VacancyRepository класса"""

    def test_init_with_dependencies(self) -> None:
        """Покрытие инициализации с зависимостями"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        repo = VacancyRepository(db_connection, validator)

        assert repo._db_connection == db_connection
        assert repo._validator == validator

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_success(self, mock_logger: Any) -> None:
        """Покрытие успешного добавления вакансии"""
        # Настройка mock объектов
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()
        validator.mock_validate_vacancy.return_value = True

        vacancy = MockAbstractVacancy("test_id_1")

        repo = VacancyRepository(db_connection, validator)
        repo.add_vacancy(vacancy)

        # Проверяем, что валидация была вызвана
        validator.mock_validate_vacancy.assert_called_once_with(vacancy)

        # Проверяем, что execute был вызван
        db_connection.mock_cursor.execute.assert_called_once()

        # Проверяем, что commit был вызван
        db_connection.mock_connection.commit.assert_called_once()

        # Проверяем логирование
        mock_logger.debug.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_validation_failure(self, mock_logger: Any) -> None:
        """Покрытие неудачной валидации при добавлении"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()
        validator.mock_validate_vacancy.return_value = False
        validator.mock_get_validation_errors.return_value = ["Ошибка 1", "Ошибка 2"]

        vacancy = MockAbstractVacancy("test_id_1")

        repo = VacancyRepository(db_connection, validator)

        with pytest.raises(ValueError, match="Вакансия не прошла валидацию"):
            repo.add_vacancy(vacancy)

        # Проверяем, что валидация была вызвана
        validator.mock_validate_vacancy.assert_called_once_with(vacancy)
        validator.mock_get_validation_errors.assert_called_once()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_database_error(self, mock_logger: Any) -> None:
        """Покрытие ошибки базы данных при добавлении"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()
        validator.mock_validate_vacancy.return_value = True

        # Имитируем ошибку базы данных
        db_connection.mock_cursor.execute.side_effect = Exception("Database error")

        vacancy = MockAbstractVacancy("test_id_1")

        repo = VacancyRepository(db_connection, validator)

        with pytest.raises(Exception, match="Database error"):
            repo.add_vacancy(vacancy)

        mock_logger.error.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_with_salary(self, mock_logger: Any) -> None:
        """Покрытие добавления вакансии с зарплатой"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()
        validator.mock_validate_vacancy.return_value = True

        vacancy = MockAbstractVacancy("test_id_1")
        # Добавляем объект зарплаты
        salary_mock = Mock()
        salary_mock.salary_from = 100000
        salary_mock.salary_to = 150000
        salary_mock.currency = "RUB"
        vacancy.salary = salary_mock

        repo = VacancyRepository(db_connection, validator)
        repo.add_vacancy(vacancy)

        # Проверяем, что данные зарплаты были переданы в execute
        db_connection.mock_cursor.execute.assert_called_once()
        call_args = db_connection.mock_cursor.execute.call_args[0]
        assert len(call_args) == 2  # query, params
        params = call_args[1]
        assert 100000 in params  # salary_from
        assert 150000 in params  # salary_to
        assert "RUB" in params    # currency

    @patch('src.vacancies.models.Vacancy')
    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_vacancies_no_filters(self, mock_logger: Any, mock_vacancy_class: Any) -> None:
        """Покрытие получения вакансий без фильтров"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Настройка mock для результата базы данных
        mock_rows = [
            {'vacancy_id': '1', 'title': 'Job 1'},
            {'vacancy_id': '2', 'title': 'Job 2'}
        ]
        db_connection.mock_cursor.fetchall.return_value = mock_rows

        # Настройка mock для Vacancy.from_dict
        mock_vacancy_instance = Mock()
        mock_vacancy_class.from_dict.return_value = mock_vacancy_instance

        repo = VacancyRepository(db_connection, validator)
        result = repo.get_vacancies()

        assert len(result) == 2
        db_connection.mock_cursor.execute.assert_called_once()
        # Проверяем, что базовый запрос был выполнен
        call_args = db_connection.mock_cursor.execute.call_args[0]
        assert "SELECT * FROM vacancies" in call_args[0]
        assert "ORDER BY created_at DESC" in call_args[0]

    @patch('src.vacancies.models.Vacancy')
    def test_get_vacancies_with_filters(self, mock_vacancy_class: Any) -> None:
        """Покрытие получения вакансий с фильтрами"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Настройка mock для результата базы данных
        mock_rows = [{'vacancy_id': '1', 'title': 'Job 1'}]
        db_connection.mock_cursor.fetchall.return_value = mock_rows

        mock_vacancy_instance = Mock()
        mock_vacancy_class.from_dict.return_value = mock_vacancy_instance

        filters = {
            "company_id": 123,
            "min_salary": 100000,
            "source": "hh.ru"
        }

        repo = VacancyRepository(db_connection, validator)
        result = repo.get_vacancies(filters)

        assert len(result) == 1
        db_connection.mock_cursor.execute.assert_called_once()

        # Проверяем, что фильтры были применены
        call_args = db_connection.mock_cursor.execute.call_args[0]
        query = call_args[0]
        params = call_args[1]

        assert "WHERE" in query
        assert "company_id = %s" in query
        assert "salary_from >= %s OR salary_to >= %s" in query
        assert "source = %s" in query
        assert 123 in params
        assert 100000 in params
        assert "hh.ru" in params

    @patch('src.storage.components.vacancy_repository.logger')
    def test_get_vacancies_database_error(self, mock_logger: Any) -> None:
        """Покрытие ошибки базы данных при получении вакансий"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Имитируем ошибку базы данных
        db_connection.mock_cursor.execute.side_effect = Exception("Database error")

        repo = VacancyRepository(db_connection, validator)

        with pytest.raises(Exception, match="Database error"):
            repo.get_vacancies()

        mock_logger.error.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_delete_vacancy_success(self, mock_logger: Any) -> None:
        """Покрытие успешного удаления вакансии"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Имитируем успешное удаление (1 строка затронута)
        db_connection.mock_cursor.rowcount = 1

        vacancy = MockAbstractVacancy("test_id_1")

        repo = VacancyRepository(db_connection, validator)
        repo.delete_vacancy(vacancy)

        db_connection.mock_cursor.execute.assert_called_once()
        call_args = db_connection.mock_cursor.execute.call_args[0]
        assert "DELETE FROM vacancies WHERE vacancy_id = %s" in call_args[0]
        assert "test_id_1" in call_args[1]

        db_connection.mock_connection.commit.assert_called_once()
        mock_logger.debug.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_delete_vacancy_not_found(self, mock_logger: Any) -> None:
        """Покрытие удаления несуществующей вакансии"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Имитируем неуспешное удаление (0 строк затронуто)
        db_connection.mock_cursor.rowcount = 0

        vacancy = MockAbstractVacancy("nonexistent_id")

        repo = VacancyRepository(db_connection, validator)
        repo.delete_vacancy(vacancy)

        db_connection.mock_cursor.execute.assert_called_once()
        db_connection.mock_connection.commit.assert_called_once()
        mock_logger.warning.assert_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_delete_vacancy_database_error(self, mock_logger: Any) -> None:
        """Покрытие ошибки базы данных при удалении"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Имитируем ошибку базы данных
        db_connection.mock_cursor.execute.side_effect = Exception("Database error")

        vacancy = MockAbstractVacancy("test_id_1")

        repo = VacancyRepository(db_connection, validator)

        with pytest.raises(Exception, match="Database error"):
            repo.delete_vacancy(vacancy)

        mock_logger.error.assert_called()

    def test_check_vacancies_exist_batch_empty_list(self) -> None:
        """Покрытие проверки существования пустого списка"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        repo = VacancyRepository(db_connection, validator)
        result = repo.check_vacancies_exist_batch([])

        assert result == {}
        # Убеждаемся, что база данных не вызывалась
        db_connection.mock_cursor.execute.assert_not_called()

    def test_check_vacancies_exist_batch_success(self) -> None:
        """Покрытие успешной проверки существования вакансий"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Настройка mock для результата базы данных
        mock_rows = [
            {'vacancy_id': 'id_1'},
            {'vacancy_id': 'id_3'}
        ]
        db_connection.mock_cursor.fetchall.return_value = mock_rows

        vacancies = [
            MockAbstractVacancy("id_1"),
            MockAbstractVacancy("id_2"),
            MockAbstractVacancy("id_3")
        ]

        repo = VacancyRepository(db_connection, validator)
        result = repo.check_vacancies_exist_batch(vacancies)  # type: ignore

        expected = {
            "id_1": True,
            "id_2": False,
            "id_3": True
        }
        assert result == expected

        db_connection.mock_cursor.execute.assert_called_once()
        call_args = db_connection.mock_cursor.execute.call_args[0]
        assert "SELECT vacancy_id FROM vacancies WHERE vacancy_id IN" in call_args[0]
        assert "id_1" in call_args[1]
        assert "id_2" in call_args[1]
        assert "id_3" in call_args[1]

    @patch('src.storage.components.vacancy_repository.logger')
    def test_check_vacancies_exist_batch_database_error(self, mock_logger: Any) -> None:
        """Покрытие ошибки базы данных при проверке существования"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Имитируем ошибку базы данных
        db_connection.mock_cursor.execute.side_effect = Exception("Database error")

        vacancies = [MockAbstractVacancy("id_1")]

        repo = VacancyRepository(db_connection, validator)

        with pytest.raises(Exception, match="Database error"):
            repo.check_vacancies_exist_batch(vacancies)  # type: ignore

        mock_logger.error.assert_called()

    def test_add_vacancy_batch_optimized_empty_list(self) -> None:
        """Покрытие пакетного добавления пустого списка"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        repo = VacancyRepository(db_connection, validator)
        result = repo.add_vacancy_batch_optimized([])

        assert result == []
        # Убеждаемся, что валидация не вызывалась
        validator.mock_validate_batch.assert_not_called()

    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_batch_optimized_no_valid_vacancies(self, mock_logger: Any) -> None:
        """Покрытие пакетного добавления без валидных вакансий"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Все вакансии невалидны
        validator.mock_validate_batch.return_value = {
            "id_1": False,
            "id_2": False
        }

        vacancies = [
            MockAbstractVacancy("id_1"),
            MockAbstractVacancy("id_2")
        ]

        repo = VacancyRepository(db_connection, validator)
        result = repo.add_vacancy_batch_optimized(vacancies)  # type: ignore

        assert result == []
        validator.mock_validate_batch.assert_called_once_with(vacancies)
        mock_logger.warning.assert_called()

    @patch('psycopg2.extras.execute_values')
    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_batch_optimized_success(self, mock_logger: Any, mock_execute_values: Any) -> None:
        """Покрытие успешного пакетного добавления"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Часть вакансий валидна
        validator.mock_validate_batch.return_value = {
            "id_1": True,
            "id_2": False,
            "id_3": True
        }

        vacancies = [
            MockAbstractVacancy("id_1"),
            MockAbstractVacancy("id_2"),
            MockAbstractVacancy("id_3")
        ]

        repo = VacancyRepository(db_connection, validator)
        result = repo.add_vacancy_batch_optimized(vacancies)  # type: ignore

        assert result == ["id_1", "id_3"]
        validator.mock_validate_batch.assert_called_once_with(vacancies)
        mock_execute_values.assert_called_once()
        db_connection.mock_connection.commit.assert_called_once()
        mock_logger.info.assert_called()

    @patch('psycopg2.extras.execute_values')
    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_batch_optimized_with_salary(self, mock_logger: Any, mock_execute_values: Any) -> None:
        """Покрытие пакетного добавления с зарплатой"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        validator.mock_validate_batch.return_value = {"id_1": True}

        vacancy = MockAbstractVacancy("id_1")
        # Добавляем объект зарплаты
        salary_mock = Mock()
        salary_mock.salary_from = 80000
        salary_mock.salary_to = 120000
        salary_mock.currency = "USD"
        vacancy.salary = salary_mock

        repo = VacancyRepository(db_connection, validator)
        result = repo.add_vacancy_batch_optimized([vacancy])

        assert result == ["id_1"]
        mock_execute_values.assert_called_once()

        # Проверяем, что данные зарплаты были переданы
        call_args = mock_execute_values.call_args[0]
        insert_data = call_args[2]  # Третий аргумент - данные для вставки
        assert len(insert_data) == 1
        vacancy_data = insert_data[0]
        assert 80000 in vacancy_data   # salary_from
        assert 120000 in vacancy_data  # salary_to
        assert "USD" in vacancy_data   # currency

    @patch('psycopg2.extras.execute_values')
    @patch('src.storage.components.vacancy_repository.logger')
    def test_add_vacancy_batch_optimized_database_error(self, mock_logger: Any, mock_execute_values: Any) -> None:
        """Покрытие ошибки базы данных при пакетном добавлении"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        validator.mock_validate_batch.return_value = {"id_1": True}

        # Имитируем ошибку базы данных
        mock_execute_values.side_effect = Exception("Database error")

        vacancies = [MockAbstractVacancy("id_1")]

        repo = VacancyRepository(db_connection, validator)

        with pytest.raises(Exception, match="Database error"):
            repo.add_vacancy_batch_optimized(vacancies)  # type: ignore

        mock_logger.error.assert_called()


class TestVacancyRepositoryEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    def test_vacancy_with_none_salary(self) -> None:
        """Покрытие обработки вакансии без зарплаты"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()
        validator.mock_validate_vacancy.return_value = True

        vacancy = MockAbstractVacancy("test_id_1")
        vacancy.salary = None  # Явно устанавливаем None

        repo = VacancyRepository(db_connection, validator)
        repo.add_vacancy(vacancy)

        # Проверяем, что вызов прошел без ошибок
        db_connection.mock_cursor.execute.assert_called_once()
        call_args = db_connection.mock_cursor.execute.call_args[0]
        params = call_args[1]
        # Salary поля должны быть None
        assert None in params

    def test_vacancy_with_missing_attributes(self) -> None:
        """Покрытие обработки вакансии с отсутствующими атрибутами"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()
        validator.mock_validate_vacancy.return_value = True

        # Создаем минимальную вакансию
        vacancy = Mock()
        vacancy.vacancy_id = "minimal_id"
        vacancy.title = "Minimal Job"
        vacancy.url = "https://minimal.com"
        vacancy.salary = None
        # Не устанавливаем остальные атрибуты

        repo = VacancyRepository(db_connection, validator)
        repo.add_vacancy(vacancy)

        # Проверяем, что getattr с None по умолчанию работает
        db_connection.mock_cursor.execute.assert_called_once()

    def test_get_vacancies_empty_result(self) -> None:
        """Покрытие получения пустого результата"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Пустой результат из базы данных
        db_connection.mock_cursor.fetchall.return_value = []

        repo = VacancyRepository(db_connection, validator)
        result = repo.get_vacancies()

        assert result == []
        db_connection.mock_cursor.execute.assert_called_once()

    def test_get_vacancies_filters_with_none_values(self) -> None:
        """Покрытие фильтров с None значениями"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        db_connection.mock_cursor.fetchall.return_value = []

        filters = {
            "company_id": None,    # Должен игнорироваться
            "min_salary": 0,       # Должен игнорироваться (falsy)
            "source": "",          # Должен игнорироваться (falsy)
            "other_filter": "value"  # Должен игнорироваться (не обрабатывается)
        }

        repo = VacancyRepository(db_connection, validator)
        result = repo.get_vacancies(filters)

        # Проверяем, что WHERE условий нет
        call_args = db_connection.mock_cursor.execute.call_args[0]
        query = call_args[0]
        assert "WHERE" not in query
        assert result == []


class TestVacancyRepositoryIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.vacancies.models.Vacancy')
    def test_complete_workflow(self, mock_vacancy_class: Any) -> None:
        """Покрытие полного рабочего процесса"""
        db_connection = MockDatabaseConnection()
        validator = MockVacancyValidator()

        # Настройка для различных операций
        validator.mock_validate_vacancy.return_value = True
        validator.mock_validate_batch.return_value = {"id_1": True, "id_2": True}

        # Настройка для get_vacancies
        mock_rows = [{'vacancy_id': '1', 'title': 'Job 1'}]
        db_connection.mock_cursor.fetchall.return_value = mock_rows
        mock_vacancy_instance = Mock()
        mock_vacancy_class.from_dict.return_value = mock_vacancy_instance

        # Настройка для check_vacancies_exist_batch
        def cursor_execute_side_effect(query: Any, params: None = None) -> None:
            if "SELECT vacancy_id FROM vacancies WHERE vacancy_id IN" in query:
                db_connection.mock_cursor.fetchall.return_value = [{'vacancy_id': 'id_1'}]

        db_connection.mock_cursor.execute.side_effect = cursor_execute_side_effect
        db_connection.mock_cursor.rowcount = 1

        repo = VacancyRepository(db_connection, validator)

        # 1. Добавление одной вакансии
        vacancy = MockAbstractVacancy("id_1")
        repo.add_vacancy(vacancy)

        # 2. Получение вакансий
        vacancies = repo.get_vacancies()
        assert len(vacancies) == 1

        # 3. Проверка существования
        exists_result = repo.check_vacancies_exist_batch([vacancy])
        assert exists_result["id_1"] is True

        # 4. Пакетное добавление
        batch_vacancies = [MockAbstractVacancy("id_1"), MockAbstractVacancy("id_2")]
        with patch('psycopg2.extras.execute_values'):
            added_ids = repo.add_vacancy_batch_optimized(batch_vacancies)  # type: ignore
            assert added_ids == ["id_1", "id_2"]

        # 5. Удаление
        repo.delete_vacancy(vacancy)

        # Проверяем, что все операции были выполнены
        assert db_connection.mock_cursor.execute.call_count >= 4
        assert db_connection.mock_connection.commit.call_count >= 2
