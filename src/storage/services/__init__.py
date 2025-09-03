"""
Модуль сервисов для работы с вакансиями на основе SOLID принципов

Содержит:
- DeduplicationService: Сервис дедупликации вакансий
- FilteringService: Сервис фильтрации по целевым компаниям
- VacancyStorageService: Основной сервис (замена postgres_saver)
"""

from .deduplication_service import DeduplicationService, SQLDeduplicationStrategy
from .filtering_service import (CompositeFilterStrategy, FilteringService, SalaryFilterStrategy,
                                TargetCompanyFilterStrategy)
from .vacancy_storage_service import VacancyStorageService

__all__ = [
    "DeduplicationService",
    "SQLDeduplicationStrategy",
    "FilteringService",
    "TargetCompanyFilterStrategy",
    "SalaryFilterStrategy",
    "CompositeFilterStrategy",
    "VacancyStorageService",
]
