#!/usr/bin/env python3
"""
Тесты модуля src/storage/abstract.py - 100% покрытие кода.

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- НУЛЕВЫХ реальных I/O операций
- ТОЛЬКО мокированные данные
- 100% покрытие всех строк кода
- Импорт из реального кода для покрытия

Модуль содержит:
- 1 абстрактный класс: AbstractVacancyStorage (ABC)
- 5 абстрактных методов: add_vacancy, get_vacancies, delete_vacancy, check_vacancies_exist_batch, add_vacancy_batch_optimized
- 48 строк кода, только определения интерфейсов без I/O
"""

import pytest
from abc import ABC
from typing import Any, Dict, List, Optional

# Импорт из реального кода для покрытия
from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy


class TestAbstractVacancyStorage:
    """100% покрытие класса AbstractVacancyStorage"""

    def test_class_exists(self) -> None:
        """Покрытие: существование класса"""
        assert AbstractVacancyStorage is not None
        assert issubclass(AbstractVacancyStorage, ABC)

    def test_class_is_abstract(self) -> None:
        """Покрытие: класс является абстрактным"""
        assert getattr(AbstractVacancyStorage, '__abstractmethods__') is not None
        # Должно быть 5 абстрактных методов
        abstract_methods = AbstractVacancyStorage.__abstractmethods__
        assert len(abstract_methods) == 5
        expected_methods = {
            'add_vacancy',
            'get_vacancies',
            'delete_vacancy',
            'check_vacancies_exist_batch',
            'add_vacancy_batch_optimized'
        }
        assert abstract_methods == expected_methods

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Покрытие: нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError) as exc_info:
            AbstractVacancyStorage()

        error_message = str(exc_info.value)
        assert "Can't instantiate abstract class AbstractVacancyStorage" in error_message

    def test_abstract_method_signatures(self) -> None:
        """Покрытие: сигнатуры всех абстрактных методов"""

        # add_vacancy
        assert hasattr(AbstractVacancyStorage, 'add_vacancy')
        assert callable(AbstractVacancyStorage.add_vacancy)
        assert AbstractVacancyStorage.add_vacancy.__isabstractmethod__ is True

        # get_vacancies
        assert hasattr(AbstractVacancyStorage, 'get_vacancies')
        assert callable(AbstractVacancyStorage.get_vacancies)
        assert AbstractVacancyStorage.get_vacancies.__isabstractmethod__ is True

        # delete_vacancy
        assert hasattr(AbstractVacancyStorage, 'delete_vacancy')
        assert callable(AbstractVacancyStorage.delete_vacancy)
        assert AbstractVacancyStorage.delete_vacancy.__isabstractmethod__ is True

        # check_vacancies_exist_batch
        assert hasattr(AbstractVacancyStorage, 'check_vacancies_exist_batch')
        assert callable(AbstractVacancyStorage.check_vacancies_exist_batch)
        assert AbstractVacancyStorage.check_vacancies_exist_batch.__isabstractmethod__ is True

        # add_vacancy_batch_optimized
        assert hasattr(AbstractVacancyStorage, 'add_vacancy_batch_optimized')
        assert callable(AbstractVacancyStorage.add_vacancy_batch_optimized)
        assert AbstractVacancyStorage.add_vacancy_batch_optimized.__isabstractmethod__ is True

    def test_abstract_methods_docstrings(self) -> None:
        """Покрытие: проверка документации абстрактных методов"""

        # add_vacancy docstring
        add_vacancy_doc = AbstractVacancyStorage.add_vacancy.__doc__
        assert add_vacancy_doc is not None
        assert "Добавляет вакансию в PostgreSQL хранилище" in add_vacancy_doc
        assert ":param vacancy: Объект вакансии для добавления" in add_vacancy_doc

        # get_vacancies docstring
        get_vacancies_doc = AbstractVacancyStorage.get_vacancies.__doc__
        assert get_vacancies_doc is not None
        assert "Возвращает список вакансий из PostgreSQL с учетом фильтров" in get_vacancies_doc
        assert ":param filters: Словарь с критериями фильтрации" in get_vacancies_doc
        assert ":return: Список вакансий" in get_vacancies_doc

        # delete_vacancy docstring
        delete_vacancy_doc = AbstractVacancyStorage.delete_vacancy.__doc__
        assert delete_vacancy_doc is not None
        assert "Удаляет вакансию из PostgreSQL хранилища" in delete_vacancy_doc
        assert ":param vacancy: Объект вакансии для удаления" in delete_vacancy_doc

        # check_vacancies_exist_batch docstring
        batch_check_doc = AbstractVacancyStorage.check_vacancies_exist_batch.__doc__
        assert batch_check_doc is not None
        assert "Проверяет существование множества вакансий одним запросом" in batch_check_doc
        assert ":param vacancies: Список вакансий для проверки" in batch_check_doc
        assert ":return: Словарь {vacancy_id: exists}" in batch_check_doc

        # add_vacancy_batch_optimized docstring
        batch_add_doc = AbstractVacancyStorage.add_vacancy_batch_optimized.__doc__
        assert batch_add_doc is not None
        assert "Оптимизированное batch-добавление вакансий" in batch_add_doc
        assert ":param vacancies: Список вакансий для добавления" in batch_add_doc
        assert ":param search_query: Поисковый запрос, по которому найдены вакансии" in batch_add_doc
        assert ":return: Список сообщений об операциях" in batch_add_doc


class TestConcreteStorageImplementation:
    """Тестирование через конкретную реализацию для покрытия абстрактных методов"""

    def test_concrete_implementation_works(self) -> None:
        """Покрытие: конкретная реализация должна работать"""

        # Создаем мок-вакансию для тестирования
        class MockVacancy(AbstractVacancy):
            def __init__(self) -> None:
                self.id = "test_vacancy_1"
                self.title = "Python Developer"

            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id, "title": self.title}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "MockVacancy":
                vacancy = cls()
                vacancy.id = data.get("id", "default")
                vacancy.title = data.get("title", "Default Title")
                return vacancy

        # Создаем конкретную реализацию хранилища для тестирования
        class ConcreteStorage(AbstractVacancyStorage):
            """Конкретная реализация для тестирования"""

            def __init__(self) -> None:
                self.vacancies = []
                self.deleted_count = 0

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                """Конкретная реализация добавления"""
                self.vacancies.append(vacancy)

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                """Конкретная реализация получения"""
                if not filters:
                    return self.vacancies
                # Простая фильтрация для теста
                filtered = []
                for vacancy in self.vacancies:
                    if hasattr(vacancy, 'title') and filters.get('title') in vacancy.title:
                        filtered.append(vacancy)
                return filtered

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                """Конкретная реализация удаления"""
                if vacancy in self.vacancies:
                    self.vacancies.remove(vacancy)
                    self.deleted_count += 1

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                """Конкретная реализация батчевой проверки"""
                result = {}
                for vacancy in vacancies:
                    result[vacancy.id] = vacancy in self.vacancies
                return result

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                """Конкретная реализация батчевого добавления"""
                messages = []
                for vacancy in vacancies:
                    self.add_vacancy(vacancy)
                    message = f"Added vacancy {vacancy.id}"
                    if search_query:
                        message += f" (search: {search_query})"
                    messages.append(message)
                return messages

        # Тестируем конкретную реализацию
        storage = ConcreteStorage()
        vacancy = MockVacancy()

        # Проверяем что это экземпляр абстрактного класса
        assert isinstance(storage, AbstractVacancyStorage)

        # Тестируем add_vacancy
        storage.add_vacancy(vacancy)
        assert len(storage.vacancies) == 1
        assert vacancy in storage.vacancies

        # Тестируем get_vacancies без фильтров
        all_vacancies = storage.get_vacancies()
        assert len(all_vacancies) == 1
        assert vacancy in all_vacancies

        # Тестируем get_vacancies с фильтрами
        filtered = storage.get_vacancies({"title": "Python"})
        assert len(filtered) == 1
        assert vacancy in filtered

        empty_filtered = storage.get_vacancies({"title": "Java"})
        assert len(empty_filtered) == 0

        # Тестируем delete_vacancy
        storage.delete_vacancy(vacancy)
        assert len(storage.vacancies) == 0
        assert storage.deleted_count == 1

    def test_batch_operations(self) -> None:
        """Покрытие: батчевые операции"""

        class MockVacancy(AbstractVacancy):
            def __init__(self, vacancy_id: str = "test", title: str = "Test") -> None:
                self.id = vacancy_id
                self.title = title

            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id, "title": self.title}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "MockVacancy":
                return cls(data.get("id", "test"), data.get("title", "Test"))

        class ConcreteStorage(AbstractVacancyStorage):
            def __init__(self) -> None:
                self.vacancies = []

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.vacancies.append(vacancy)

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return self.vacancies

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                if vacancy in self.vacancies:
                    self.vacancies.remove(vacancy)

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                result = {}
                for vacancy in vacancies:
                    result[vacancy.id] = any(v.id == vacancy.id for v in self.vacancies)
                return result

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                messages = []
                for vacancy in vacancies:
                    self.add_vacancy(vacancy)
                    msg = f"Processed {vacancy.id}"
                    if search_query:
                        msg += f" from '{search_query}'"
                    messages.append(msg)
                return messages

        storage = ConcreteStorage()

        # Создаем тестовые вакансии
        vacancy1 = MockVacancy("v1", "Developer")
        vacancy2 = MockVacancy("v2", "Designer")
        vacancy3 = MockVacancy("v3", "Manager")

        test_vacancies = [vacancy1, vacancy2, vacancy3]

        # Тестируем check_vacancies_exist_batch с пустым хранилищем
        exist_results = storage.check_vacancies_exist_batch(test_vacancies)
        assert len(exist_results) == 3
        assert exist_results["v1"] is False
        assert exist_results["v2"] is False
        assert exist_results["v3"] is False

        # Тестируем add_vacancy_batch_optimized без search_query
        messages = storage.add_vacancy_batch_optimized(test_vacancies[:2])
        assert len(messages) == 2
        assert "Processed v1" in messages[0]
        assert "Processed v2" in messages[1]
        assert len(storage.vacancies) == 2

        # Тестируем add_vacancy_batch_optimized с search_query
        messages_with_query = storage.add_vacancy_batch_optimized([vacancy3], "python jobs")
        assert len(messages_with_query) == 1
        assert "Processed v3" in messages_with_query[0]
        assert "from 'python jobs'" in messages_with_query[0]

        # Тестируем check_vacancies_exist_batch с заполненным хранилищем
        exist_results_filled = storage.check_vacancies_exist_batch(test_vacancies)
        assert exist_results_filled["v1"] is True
        assert exist_results_filled["v2"] is True
        assert exist_results_filled["v3"] is True


class TestInheritanceAndPolymorphism:
    """Тестирование наследования и полиморфизма"""

    def test_multiple_storage_implementations(self) -> None:
        """Покрытие: несколько реализаций хранилища"""

        class MockVacancy(AbstractVacancy):
            def __init__(self, vacancy_id: str = "test") -> None:
                self.id = vacancy_id

            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "MockVacancy":
                return cls(data.get("id", "test"))

        class InMemoryStorage(AbstractVacancyStorage):
            def __init__(self) -> None:
                self.data = []

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.data.append(vacancy)

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return self.data

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                if vacancy in self.data:
                    self.data.remove(vacancy)

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                return {v.id: v in self.data for v in vacancies}

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                for v in vacancies:
                    self.data.append(v)
                return [f"InMemory: added {v.id}" for v in vacancies]

        class CachedStorage(AbstractVacancyStorage):
            def __init__(self) -> None:
                self.cache = {}
                self.counter = 0

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.cache[vacancy.id] = vacancy
                self.counter += 1

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return list(self.cache.values())

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.cache.pop(vacancy.id, None)

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                return {v.id: v.id in self.cache for v in vacancies}

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                for v in vacancies:
                    self.cache[v.id] = v
                    self.counter += 1
                return [f"Cached: added {v.id}" for v in vacancies]

        # Создаем разные реализации
        in_memory = InMemoryStorage()
        cached = CachedStorage()
        vacancy = MockVacancy("test_v")

        # Проверяем полиморфизм
        storages = [in_memory, cached]
        for storage in storages:
            assert isinstance(storage, AbstractVacancyStorage)
            storage.add_vacancy(vacancy)
            retrieved = storage.get_vacancies()
            assert len(retrieved) == 1

        # Проверяем различное поведение
        assert len(in_memory.data) == 1
        assert len(cached.cache) == 1
        assert cached.counter == 1


class TestAbstractMethodsEnforcement:
    """Тестирование принуждения реализации абстрактных методов"""

    def test_missing_add_vacancy_fails(self) -> None:
        """Покрытие: отсутствие add_vacancy вызывает ошибку"""

        with pytest.raises(TypeError) as exc_info:
            class IncompleteStorage1(AbstractVacancyStorage):
                def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                    return []

                def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                    pass

                def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                    return {}

                def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                    return []

            IncompleteStorage1()

        error_message = str(exc_info.value)
        assert "add_vacancy" in error_message

    def test_missing_multiple_methods_fails(self) -> None:
        """Покрытие: отсутствие нескольких методов"""

        with pytest.raises(TypeError) as exc_info:
            class IncompleteStorage2(AbstractVacancyStorage):
                def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                    pass
                # Остальные методы не реализованы

            IncompleteStorage2()

        error_message = str(exc_info.value)
        # Должны быть упомянуты все нереализованные методы
        missing_methods = ["get_vacancies", "delete_vacancy", "check_vacancies_exist_batch", "add_vacancy_batch_optimized"]
        for method in missing_methods:
            assert method in error_message or f"abstract method {method}" in error_message

    def test_all_methods_must_be_implemented(self) -> None:
        """Покрытие: все методы должны быть реализованы"""

        with pytest.raises(TypeError) as exc_info:
            class EmptyStorage(AbstractVacancyStorage):
                pass

            EmptyStorage()

        error_message = str(exc_info.value)
        assert "abstract methods" in error_message or "abstract method" in error_message
        # Должны быть упомянуты все 5 методов
        expected_methods = ["add_vacancy", "get_vacancies", "delete_vacancy", "check_vacancies_exist_batch", "add_vacancy_batch_optimized"]
        for method in expected_methods:
            assert method in error_message

    def test_complete_implementation_works(self) -> None:
        """Покрытие: полная реализация должна работать"""

        class MockVacancy(AbstractVacancy):
            def __init__(self) -> None:
                self.id = "test"

            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "MockVacancy":
                return cls()

        class CompleteStorage(AbstractVacancyStorage):
            def __init__(self) -> None:
                self.storage = []

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                self.storage.append(vacancy)

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return self.storage

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                if vacancy in self.storage:
                    self.storage.remove(vacancy)

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                return {v.id: v in self.storage for v in vacancies}

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                for v in vacancies:
                    self.storage.append(v)
                return [f"Added {v.id}" for v in vacancies]

        # Должно работать без ошибок
        storage = CompleteStorage()
        assert isinstance(storage, AbstractVacancyStorage)

        vacancy = MockVacancy()
        storage.add_vacancy(vacancy)
        assert len(storage.storage) == 1

        retrieved = storage.get_vacancies()
        assert len(retrieved) == 1
        assert vacancy in retrieved


class TestEdgeCases:
    """Тестирование граничных случаев"""

    def test_empty_filters_handling(self) -> None:
        """Покрытие: обработка пустых фильтров"""

        class MockVacancy(AbstractVacancy):
            def __init__(self, vacancy_id: str = "test") -> None:
                self.id = vacancy_id

            def to_dict(self) -> Dict[str, Any]:
                return {"id": self.id}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "MockVacancy":
                return cls()

        class TestStorage(AbstractVacancyStorage):
            def __init__(self) -> None:
                self.data = [MockVacancy("v1"), MockVacancy("v2")]

            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                # Тестируем разные варианты фильтров
                if filters is None:
                    return self.data
                if not filters:  # Пустой словарь
                    return self.data
                return []

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                return {}

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                return []

        storage = TestStorage()

        # Тестируем None фильтр
        result1 = storage.get_vacancies(None)
        assert len(result1) == 2

        # Тестируем пустой словарь
        result2 = storage.get_vacancies({})
        assert len(result2) == 2

        # Тестируем непустой фильтр
        result3 = storage.get_vacancies({"test": "value"})
        assert len(result3) == 0

    def test_empty_batch_operations(self) -> None:
        """Покрытие: пустые батчевые операции"""

        class MockVacancy(AbstractVacancy):
            def to_dict(self) -> Dict[str, Any]:
                return {}

            @classmethod
            def from_dict(cls, data: Dict[str, Any]) -> "MockVacancy":
                return cls()

        class TestStorage(AbstractVacancyStorage):
            def add_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass

            def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
                return []

            def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
                pass

            def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
                # Тестируем пустой список
                return {v.id: False for v in vacancies}

            def add_vacancy_batch_optimized(self, vacancies: List[AbstractVacancy], search_query: str = None) -> List[str]:
                # Тестируем с search_query и без
                if search_query:
                    return [f"Query: {search_query}, processed {len(vacancies)} items"]
                return [f"Processed {len(vacancies)} items"]

        storage = TestStorage()

        # Тестируем пустые батчи
        empty_check = storage.check_vacancies_exist_batch([])
        assert len(empty_check) == 0

        empty_add = storage.add_vacancy_batch_optimized([])
        assert len(empty_add) == 1
        assert "Processed 0 items" in empty_add[0]

        # Тестируем с query
        empty_add_with_query = storage.add_vacancy_batch_optimized([], "test query")
        assert len(empty_add_with_query) == 1
        assert "Query: test query" in empty_add_with_query[0]