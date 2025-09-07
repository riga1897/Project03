#!/usr/bin/env python3
"""
Тесты модуля vacancy_validator для 100% покрытия.

Покрывает все функции в src/storage/components/vacancy_validator.py:
- VacancyValidator - валидатор для вакансий
- validate_vacancy - валидация одной вакансии
- _validate_required_fields - проверка обязательных полей
- _validate_data_types - проверка типов данных
- _validate_business_rules - проверка бизнес-правил
- get_validation_errors - получение ошибок валидации
- validate_batch - пакетная валидация

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from typing import Optional, Dict, Any, List
from unittest.mock import patch, MagicMock, Mock

# Импорты из реального кода для покрытия
from src.storage.components.vacancy_validator import VacancyValidator


class MockAbstractVacancy:
    """Mock объект для AbstractVacancy"""
    def __init__(self, vacancy_id: str = "test_id", title: str = "Test Job", url: str = "https://example.com/job"):
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


class TestVacancyValidator:
    """100% покрытие VacancyValidator класса"""

    def test_init(self):
        """Покрытие инициализации валидатора"""
        validator = VacancyValidator()
        
        # Проверяем константы класса
        assert validator.REQUIRED_FIELDS == {"vacancy_id": str, "title": str, "url": str}
        assert "salary" in validator.OPTIONAL_FIELDS
        assert "description" in validator.OPTIONAL_FIELDS
        assert validator._validation_errors == []

    def test_validate_vacancy_success(self):
        """Покрытие успешной валидации вакансии"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True
        assert validator._validation_errors == []

    def test_validate_vacancy_missing_required_field(self):
        """Покрытие валидации с отсутствующим обязательным полем"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        delattr(vacancy, 'title')  # Удаляем обязательное поле
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("title" in error for error in errors)

    def test_validate_vacancy_empty_required_field(self):
        """Покрытие валидации с пустым обязательным полем"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.vacancy_id = ""  # Пустое обязательное поле
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("vacancy_id" in error for error in errors)

    def test_validate_vacancy_whitespace_only_field(self):
        """Покрытие валидации с полем содержащим только пробелы"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = "   "  # Только пробелы
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("title" in error for error in errors)

    def test_validate_vacancy_wrong_type_required_field(self):
        """Покрытие валидации с неверным типом обязательного поля"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = 123  # Число вместо строки
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("title" in error and "тип" in error for error in errors)

    def test_validate_vacancy_wrong_type_optional_field(self):
        """Покрытие валидации с неверным типом опционального поля"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.description = 123  # Число вместо строки
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("description" in error and "тип" in error for error in errors)

    def test_validate_vacancy_none_optional_field(self):
        """Покрытие валидации с None в опциональном поле"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.description = None  # None разрешен в опциональных полях
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True
        assert validator._validation_errors == []

    def test_validate_vacancy_missing_optional_field(self):
        """Покрытие валидации с отсутствующим опциональным полем"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        delattr(vacancy, 'description')  # Удаляем опциональное поле
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True  # Отсутствие опциональных полей допустимо
        assert validator._validation_errors == []

    def test_validate_vacancy_invalid_url_no_protocol(self):
        """Покрытие валидации с URL без протокола"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.url = "example.com/job"  # Без http/https
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("URL" in error and ("http://" in error or "https://" in error) for error in errors)

    def test_validate_vacancy_valid_http_url(self):
        """Покрытие валидации с корректным HTTP URL"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.url = "http://example.com/job"
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True
        assert validator._validation_errors == []

    def test_validate_vacancy_valid_https_url(self):
        """Покрытие валидации с корректным HTTPS URL"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.url = "https://example.com/job"
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True
        assert validator._validation_errors == []

    def test_validate_vacancy_too_long_id(self):
        """Покрытие валидации со слишком длинным ID"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.vacancy_id = "x" * 101  # Превышает лимит в 100 символов
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("ID" in error and "длинный" in error for error in errors)

    def test_validate_vacancy_max_length_id(self):
        """Покрытие валидации с ID максимальной длины"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.vacancy_id = "x" * 100  # Ровно на границе лимита
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True
        assert validator._validation_errors == []

    def test_validate_vacancy_too_long_title(self):
        """Покрытие валидации со слишком длинным заголовком"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = "x" * 501  # Превышает лимит в 500 символов
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert any("Название" in error and "длинное" in error for error in errors)

    def test_validate_vacancy_max_length_title(self):
        """Покрытие валидации с заголовком максимальной длины"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = "x" * 500  # Ровно на границе лимита
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is True
        assert validator._validation_errors == []

    def test_get_validation_errors_empty(self):
        """Покрытие получения пустого списка ошибок"""
        validator = VacancyValidator()
        
        errors = validator.get_validation_errors()
        
        assert errors == []
        assert isinstance(errors, list)

    def test_get_validation_errors_with_errors(self):
        """Покрытие получения списка ошибок"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = None  # Вызовет ошибку
        
        validator.validate_vacancy(vacancy)
        errors = validator.get_validation_errors()
        
        assert len(errors) > 0
        assert isinstance(errors, list)
        assert all(isinstance(error, str) for error in errors)

    def test_get_validation_errors_returns_copy(self):
        """Покрытие того, что get_validation_errors возвращает копию"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = None  # Вызовет ошибку
        
        validator.validate_vacancy(vacancy)
        errors1 = validator.get_validation_errors()
        errors2 = validator.get_validation_errors()
        
        # Должны быть разными объектами (копии)
        assert errors1 is not errors2
        assert errors1 == errors2

    def test_validate_vacancy_errors_cleared_on_new_validation(self):
        """Покрытие сброса ошибок при новой валидации"""
        validator = VacancyValidator()
        
        # Первая валидация с ошибкой
        invalid_vacancy = MockAbstractVacancy()
        invalid_vacancy.title = None
        
        result1 = validator.validate_vacancy(invalid_vacancy)
        assert result1 is False
        assert len(validator.get_validation_errors()) > 0
        
        # Вторая валидация успешная
        valid_vacancy = MockAbstractVacancy()
        
        result2 = validator.validate_vacancy(valid_vacancy)
        assert result2 is True
        assert len(validator.get_validation_errors()) == 0

    def test_validate_batch_empty_list(self):
        """Покрытие пакетной валидации пустого списка"""
        validator = VacancyValidator()
        
        result = validator.validate_batch([])
        
        assert result == {}

    @patch('src.storage.components.vacancy_validator.logger')
    def test_validate_batch_success(self, mock_logger):
        """Покрытие успешной пакетной валидации"""
        validator = VacancyValidator()
        vacancies = [
            MockAbstractVacancy("id_1", "Job 1"),
            MockAbstractVacancy("id_2", "Job 2"),
            MockAbstractVacancy("id_3", "Job 3")
        ]
        
        result = validator.validate_batch(vacancies)
        
        expected = {
            "id_1": True,
            "id_2": True,
            "id_3": True
        }
        assert result == expected
        # Не должно быть предупреждений для валидных вакансий
        mock_logger.warning.assert_not_called()

    @patch('src.storage.components.vacancy_validator.logger')
    def test_validate_batch_mixed_results(self, mock_logger):
        """Покрытие пакетной валидации со смешанными результатами"""
        validator = VacancyValidator()
        
        # Валидная вакансия
        valid_vacancy = MockAbstractVacancy("valid_id", "Valid Job")
        
        # Невалидная вакансия (неверный URL)
        invalid_vacancy = MockAbstractVacancy("invalid_id", "Invalid Job")
        invalid_vacancy.url = "invalid-url"
        
        # Невалидная вакансия (отсутствует заголовок)
        missing_title_vacancy = MockAbstractVacancy("missing_title_id")
        missing_title_vacancy.title = None
        
        vacancies = [valid_vacancy, invalid_vacancy, missing_title_vacancy]
        
        result = validator.validate_batch(vacancies)
        
        expected = {
            "valid_id": True,
            "invalid_id": False,
            "missing_title_id": False
        }
        assert result == expected
        
        # Должны быть предупреждения для невалидных вакансий
        assert mock_logger.warning.call_count == 2

    @patch('src.storage.components.vacancy_validator.logger')
    def test_validate_batch_exception_handling(self, mock_logger):
        """Покрытие обработки исключений в пакетной валидации"""
        validator = VacancyValidator()
        
        # Создаем объект, который вызовет исключение при доступе к атрибуту
        class ProblematicVacancy:
            @property
            def vacancy_id(self):
                raise Exception("Test exception")
        
        problematic_vacancy = ProblematicVacancy()
        
        result = validator.validate_batch([problematic_vacancy])
        
        assert result == {"unknown": False}
        mock_logger.error.assert_called_once()

    def test_validate_batch_unknown_vacancy_id(self):
        """Покрытие пакетной валидации с отсутствующим vacancy_id"""
        validator = VacancyValidator()
        
        # Создаем объект без атрибута vacancy_id
        class VacancyWithoutId:
            pass
        
        vacancy_without_id = VacancyWithoutId()
        
        result = validator.validate_batch([vacancy_without_id])
        
        assert "unknown" in result
        assert result["unknown"] is False

    def test_validate_batch_with_duplicates(self):
        """Покрытие пакетной валидации с дубликатами ID"""
        validator = VacancyValidator()
        
        # Две вакансии с одинаковыми ID, но разной валидностью
        valid_vacancy = MockAbstractVacancy("duplicate_id", "Valid Job")
        invalid_vacancy = MockAbstractVacancy("duplicate_id", "Invalid Job")
        invalid_vacancy.url = "invalid-url"
        
        vacancies = [valid_vacancy, invalid_vacancy]
        
        result = validator.validate_batch(vacancies)
        
        # Последняя вакансия должна перезаписать результат
        assert "duplicate_id" in result
        assert result["duplicate_id"] is False


class TestVacancyValidatorHelperMethods:
    """Покрытие вспомогательных методов валидатора"""

    def test_validate_required_fields_all_present_and_valid(self):
        """Покрытие проверки всех присутствующих и валидных обязательных полей"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Вызываем validate_vacancy, который внутри вызовет _validate_required_fields
        result = validator.validate_vacancy(vacancy)
        assert result is True

    def test_validate_data_types_valid_optional_fields(self):
        """Покрытие валидации типов данных для корректных опциональных полей"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Устанавливаем корректные типы для опциональных полей
        vacancy.description = "Valid description"
        vacancy.requirements = "Valid requirements"
        vacancy.responsibilities = None  # None разрешен
        
        result = validator.validate_vacancy(vacancy)
        assert result is True

    def test_validate_business_rules_all_valid(self):
        """Покрытие валидации бизнес-правил для корректных данных"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Устанавливаем корректные значения для всех проверяемых полей
        vacancy.url = "https://example.com/job"
        vacancy.vacancy_id = "valid_id_123"
        vacancy.title = "Valid Job Title"
        
        result = validator.validate_vacancy(vacancy)
        assert result is True

    def test_validate_business_rules_empty_url(self):
        """Покрытие валидации с пустым URL"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.url = ""  # Пустой URL
        
        # Пустой URL не должен вызывать ошибку бизнес-правил (только required fields)
        # Но вызовет ошибку обязательного поля
        result = validator.validate_vacancy(vacancy)
        assert result is False

    def test_validate_business_rules_empty_id(self):
        """Покрытие валидации с пустым ID"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.vacancy_id = ""  # Пустой ID
        
        # Пустой ID вызовет ошибку обязательного поля
        result = validator.validate_vacancy(vacancy)
        assert result is False

    def test_validate_business_rules_empty_title(self):
        """Покрытие валидации с пустым заголовком"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.title = ""  # Пустой заголовок
        
        # Пустой заголовок вызовет ошибку обязательного поля
        result = validator.validate_vacancy(vacancy)
        assert result is False


class TestVacancyValidatorEdgeCases:
    """Покрытие граничных случаев и особых сценариев"""

    def test_validate_vacancy_multiple_errors(self):
        """Покрытие валидации с множественными ошибками"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Устанавливаем ошибки, которые будут проверены в разных методах
        vacancy.title = None  # Отсутствует обязательное поле (остановит _validate_required_fields)
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert len(errors) >= 1  # Будет минимум 1 ошибка из-за остановки на первом методе

    def test_validate_vacancy_multiple_type_errors(self):
        """Покрытие множественных ошибок типов данных"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Ошибки типов данных в опциональных полях
        vacancy.description = 123  # Неверный тип
        vacancy.requirements = 456  # Неверный тип
        
        result = validator.validate_vacancy(vacancy)
        
        assert result is False
        errors = validator.get_validation_errors()
        assert len(errors) >= 2  # Должно быть минимум 2 ошибки типов

    def test_validate_vacancy_with_special_characters(self):
        """Покрытие валидации с специальными символами"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Устанавливаем специальные символы
        vacancy.vacancy_id = "job_123-456.789"
        vacancy.title = "Senior Python Developer (Remote) №1 ★★★"
        vacancy.description = "Job with émojis 🚀 and special chars: ®™©\nNew line\tTab"
        
        result = validator.validate_vacancy(vacancy)
        assert result is True  # Специальные символы должны быть разрешены

    def test_validate_vacancy_numeric_id(self):
        """Покрытие валидации с числовым ID"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        vacancy.vacancy_id = 12345  # Числовой ID (будет преобразован в строку)
        
        result = validator.validate_vacancy(vacancy)
        assert result is False  # Числовой тип недопустим для ID

    def test_validate_vacancy_with_complex_url(self):
        """Покрытие валидации со сложным URL"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        complex_url = "https://subdomain.example.com:8080/path/to/job?id=123&ref=search&utm_source=test#section"
        vacancy.url = complex_url
        
        result = validator.validate_vacancy(vacancy)
        assert result is True  # Сложный но корректный URL должен быть принят

    def test_optional_fields_tuple_types(self):
        """Покрытие опциональных полей с кортежами типов"""
        validator = VacancyValidator()
        vacancy = MockAbstractVacancy()
        
        # Проверяем поля, которые могут быть str или None
        vacancy.requirements = None  # Первый тип из кортежа (str, type(None))
        vacancy.responsibilities = "Valid responsibilities"  # Второй тип
        
        result = validator.validate_vacancy(vacancy)
        assert result is True

    def test_missing_attributes_in_business_rules(self):
        """Покрытие отсутствующих атрибутов в бизнес-правилах"""
        validator = VacancyValidator()
        
        # Создаем минимальную вакансию только с обязательными полями
        minimal_vacancy = Mock()
        minimal_vacancy.vacancy_id = "test_id"
        minimal_vacancy.title = "Test Job"
        minimal_vacancy.url = "https://example.com"
        
        # Удаляем все остальные атрибуты
        for attr in ['salary', 'description', 'requirements', 'responsibilities', 
                     'employer', 'experience', 'employment', 'area', 'source']:
            if hasattr(minimal_vacancy, attr):
                delattr(minimal_vacancy, attr)
        
        result = validator.validate_vacancy(minimal_vacancy)
        assert result is True  # Должно быть валидным с минимальным набором полей


class TestVacancyValidatorIntegration:
    """Интеграционные тесты и комплексные сценарии"""

    @patch('src.storage.components.vacancy_validator.logger')
    def test_comprehensive_validation_workflow(self, mock_logger):
        """Покрытие комплексного рабочего процесса валидации"""
        validator = VacancyValidator()
        
        # Создаем набор разнообразных вакансий
        vacancies = []
        
        # 1. Полностью валидная вакансия
        perfect_vacancy = MockAbstractVacancy("perfect_1", "Software Engineer")
        perfect_vacancy.description = "Great job opportunity"
        perfect_vacancy.requirements = "Python, Django"
        vacancies.append(perfect_vacancy)
        
        # 2. Валидная минималистичная вакансия
        minimal_vacancy = MockAbstractVacancy("minimal_1", "Simple Job")
        minimal_vacancy.description = None
        minimal_vacancy.requirements = None
        vacancies.append(minimal_vacancy)
        
        # 3. Вакансия с ошибками в обязательных полях
        missing_title = MockAbstractVacancy("error_1")
        missing_title.title = None
        vacancies.append(missing_title)
        
        # 4. Вакансия с ошибками в бизнес-правилах
        bad_url = MockAbstractVacancy("error_2")
        bad_url.url = "ftp://invalid-protocol.com"
        vacancies.append(bad_url)
        
        # 5. Вакансия с ошибками типов данных
        wrong_types = MockAbstractVacancy("error_3")
        wrong_types.description = 123  # Неверный тип
        vacancies.append(wrong_types)
        
        # Пакетная валидация
        batch_results = validator.validate_batch(vacancies)
        
        expected_results = {
            "perfect_1": True,
            "minimal_1": True,
            "error_1": False,
            "error_2": False,
            "error_3": False
        }
        
        assert batch_results == expected_results
        
        # Проверяем логирование
        assert mock_logger.warning.call_count == 3  # 3 невалидные вакансии

    def test_validator_state_independence(self):
        """Покрытие независимости состояния валидатора"""
        validator = VacancyValidator()
        
        # Множественные валидации должны быть независимыми
        for i in range(5):
            if i % 2 == 0:
                # Валидная вакансия
                vacancy = MockAbstractVacancy(f"valid_{i}", f"Job {i}")
                result = validator.validate_vacancy(vacancy)
                assert result is True
                assert len(validator.get_validation_errors()) == 0
            else:
                # Невалидная вакансия
                vacancy = MockAbstractVacancy(f"invalid_{i}")
                vacancy.title = None
                result = validator.validate_vacancy(vacancy)
                assert result is False
                assert len(validator.get_validation_errors()) > 0

    def test_concurrent_usage_simulation(self):
        """Покрытие имитации конкурентного использования"""
        # Создаем несколько независимых валидаторов
        validators = [VacancyValidator() for _ in range(3)]
        
        for i, validator in enumerate(validators):
            # Каждый валидатор обрабатывает свою вакансию
            vacancy = MockAbstractVacancy(f"concurrent_{i}", f"Concurrent Job {i}")
            
            if i == 1:
                vacancy.title = None  # Делаем одну невалидной
            
            result = validator.validate_vacancy(vacancy)
            
            if i == 1:
                assert result is False
                assert len(validator.get_validation_errors()) > 0
            else:
                assert result is True
                assert len(validator.get_validation_errors()) == 0
        
        # Убеждаемся, что валидаторы независимы
        assert len(validators[0].get_validation_errors()) == 0
        assert len(validators[1].get_validation_errors()) > 0
        assert len(validators[2].get_validation_errors()) == 0