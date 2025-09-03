from dataclasses import dataclass, field
from typing import Any, Dict
from src.utils.env_loader import EnvLoader


@dataclass
class HHAPIConfig:
    """Конфигурация специфичных параметров HH API"""

    area: int = 113  # Россия по умолчанию
    per_page: int = 50  # Количество элементов на странице
    only_with_salary: bool = False  # Будет загружено из .env
    period: int = 15  # Период 15 дней по умолчанию
    custom_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Загружаем настройку фильтрации по зарплате из .env
        env_value = EnvLoader.get_env_var("FILTER_ONLY_WITH_SALARY", "false")
        self.only_with_salary = str(env_value).lower() in ("true", "1", "yes", "on")

    def get_params(self, **kwargs) -> Dict[str, Any]:
        """Генерация параметров запроса с учетом переопределений"""
        params = {
            "area": kwargs.get("area", self.area),
            "per_page": kwargs.get("per_page", self.per_page),
            "only_with_salary": kwargs.get("only_with_salary", self.only_with_salary),
            "period": kwargs.get("period", self.period),
        }
        if self.custom_params:
            params.update(self.custom_params)
        params.update(kwargs)
        return params

    def get_hh_params(self, **kwargs) -> Dict[str, Any]:
        """Get HH API params with overrides (для совместимости со старым интерфейсом)."""
        return self.get_params(**kwargs)
