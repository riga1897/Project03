"""
Валидатор данных вакансий.
Реализует принцип единственной ответственности (SRP).
"""

import logging
from typing import Any, Dict, List, Tuple, Type, Union

from src.vacancies.abstract import AbstractVacancy

logger = logging.getLogger(__name__)


class VacancyValidator:
    """
    Класс для валидации данных вакансий.

    Отвечает только за проверку корректности и полноты данных вакансий.
    Реализует принцип единственной ответственности (SRP).

    Поддерживает валидацию:
    - Обязательных полей (vacancy_id, title, url)
    - Типов данных для всех полей
    - Бизнес-правил (формат URL, длина полей)
    - Пакетную валидацию списка вакансий
    """

    REQUIRED_FIELDS = {"vacancy_id": str, "title": str, "url": str}

    OPTIONAL_FIELDS = {
        "salary": Any,
        "description": str,
        "requirements": (str, type(None)),
        "responsibilities": (str, type(None)),
        "employer": Any,
        "experience": (str, type(None)),
        "employment": (str, type(None)),
        "area": (str, type(None)),
        "source": (str, type(None)),
    }

    def __init__(self) -> None:
        """Инициализация валидатора"""
        self._validation_errors: List[str] = []

    def validate_vacancy(self, vacancy: AbstractVacancy) -> bool:
        """
        Полная валидация объекта вакансии

        Args:
            vacancy: Объект вакансии для валидации

        Returns:
            bool: True если вакансия валидна, False иначе
        """
        self._validation_errors.clear()

        if not self._validate_required_fields(vacancy):
            return False

        if not self._validate_data_types(vacancy):
            return False

        if not self._validate_business_rules(vacancy):
            return False

        return True

    def _validate_required_fields(self, vacancy: AbstractVacancy) -> bool:
        """Валидация обязательных полей"""
        for field_name, expected_type in self.REQUIRED_FIELDS.items():
            if not hasattr(vacancy, field_name):
                self._validation_errors.append(f"Отсутствует обязательное поле: {field_name}")
                continue

            value = getattr(vacancy, field_name)
            if not value or (isinstance(value, str) and not value.strip()):
                self._validation_errors.append(f"Обязательное поле пустое: {field_name}")
                continue

            if not isinstance(value, expected_type):
                self._validation_errors.append(
                    f"Неверный тип поля {field_name}: ожидался {expected_type}, получен {type(value)}"
                )

        return len(self._validation_errors) == 0

    def _validate_data_types(self, vacancy: AbstractVacancy) -> bool:
        """Валидация типов данных опциональных полей"""
        for field_name, expected_types in self.OPTIONAL_FIELDS.items():
            if not hasattr(vacancy, field_name):
                continue

            value = getattr(vacancy, field_name)
            if value is None:
                continue

            if not isinstance(value, expected_types):
                self._validation_errors.append(
                    f"Неверный тип поля {field_name}: ожидался {expected_types}, получен {type(value)}"
                )

        return len(self._validation_errors) == 0

    def _validate_business_rules(self, vacancy: AbstractVacancy) -> bool:
        """Валидация бизнес-правил"""
        # Проверка URL
        url_value = getattr(vacancy, "url", None)
        if url_value:
            if not str(url_value).startswith(("http://", "https://")):
                self._validation_errors.append("URL вакансии должен начинаться с http:// или https://")

        # Проверка ID
        vacancy_id_value = getattr(vacancy, "vacancy_id", None)
        if vacancy_id_value:
            if len(str(vacancy_id_value)) > 100:  # Разумное ограничение
                self._validation_errors.append("ID вакансии слишком длинный")

        # Проверка названия
        title_value = getattr(vacancy, "title", None)
        if title_value:
            if len(str(title_value)) > 500:  # Разумное ограничение
                self._validation_errors.append("Название вакансии слишком длинное")

        return len(self._validation_errors) == 0

    def get_validation_errors(self) -> List[str]:
        """Получение списка ошибок валидации"""
        return self._validation_errors.copy()

    def validate_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
        """
        Валидация списка вакансий

        Args:
            vacancies: Список вакансий для валидации

        Returns:
            Dict[str, bool]: Словарь {vacancy_id: is_valid}
        """
        results = {}

        for vacancy in vacancies:
            try:
                vacancy_id = getattr(vacancy, "vacancy_id", "unknown")
                results[vacancy_id] = self.validate_vacancy(vacancy)

                if not results[vacancy_id]:
                    logger.warning(f"Вакансия {vacancy_id} не прошла валидацию: {self.get_validation_errors()}")

            except Exception as e:
                logger.error(f"Ошибка валидации вакансии: {e}")
                results[getattr(vacancy, "vacancy_id", "unknown")] = False

        return results
