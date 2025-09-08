"""
Сервисы для работы с данными в хранилище.
Включает в себя фильтрацию, дедупликацию и обработку данных
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
