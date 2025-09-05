from typing import Any, Dict, Optional


class Salary:
    """
    Класс для обработки зарплатных данных

    Предоставляет функциональность для:
    - Парсинга зарплатных данных из различных форматов
    - Валидации и нормализации зарплатных значений
    - Форматирования зарплаты для отображения
    - Вычисления средних и максимальных значений

    Поддерживает форматы:
    - "от X до Y" / "X - Y" / "X-Y"
    - "от X" / "до Y"
    - Простые числовые значения
    """

    __slots__ = ("_salary_from", "_salary_to", "_currency", "gross", "period", "amount_from", "amount_to")

    def __init__(self, salary_data: Optional[Dict[str, Any]] = None):
        if salary_data is None:
            salary_data = {}

        self.amount_from = 0
        self.amount_to = 0
        self.gross = False
        self.period = "month"

        # Сначала проверяем, есть ли строковый диапазон для парсинга
        if isinstance(salary_data, str):
            salary_data = self._parse_salary_range_string(salary_data)
        elif isinstance(salary_data, dict) and salary_data.get("salary_range"):
            range_data = self._parse_salary_range_string(salary_data["salary_range"])
            salary_data.update(range_data)

        self._salary_from = self._validate_salary_value(salary_data.get("from"))
        self._salary_to = self._validate_salary_value(salary_data.get("to"))
        self._currency = self._validate_currency(salary_data.get("currency", "RUR"))

        if salary_data:
            self._validate_and_set(salary_data)

    def _validate_and_set(self, data: Dict[str, Any]) -> None:
        """Приватный метод валидации данных"""
        if not isinstance(data, dict):
            return

        self.amount_from = data.get("from") or 0
        self.amount_to = data.get("to") or 0
        self.gross = data.get("gross", False)

        if "salary_range" in data and isinstance(data["salary_range"], dict):
            salary_range = data["salary_range"]
            self.amount_from = salary_range.get("from") or self.amount_from
            self.amount_to = salary_range.get("to") or self.amount_to
            if salary_range.get("mode") and isinstance(salary_range["mode"], dict):
                mode_id = salary_range["mode"].get("id", "").lower()
                if mode_id:
                    self.period = mode_id

    @staticmethod
    def _validate_salary_value(value: Any) -> Optional[int]:
        """Валидация значения зарплаты"""
        if value is None:
            return None
        try:
            salary_val = int(value)
            return salary_val if salary_val > 0 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _validate_currency(value: Any) -> str:
        """Валидация валюты"""
        if not value or not isinstance(value, str):
            return "RUR"
        return value.upper().strip()

    @staticmethod
    def _parse_salary_range_string(salary_range: str) -> Dict[str, Any]:
        """
        Парсинг строки с диапазоном зарплаты

        Поддерживаемые форматы:
        - "100000 - 150000"
        - "от 100000 до 150000"
        - "100000-150000"
        - "от 100000"
        - "до 150000"
        """
        if not salary_range or not isinstance(salary_range, str):
            return {}

        import re

        # Очищаем строку от лишних символов и приводим к нижнему регистру
        clean_range = salary_range.strip().lower()

        # Паттерны для разных форматов
        patterns = [
            # "от X до Y", "от X до Y руб", "от X до Y рублей"
            r"от\s*(\d+(?:\s?\d{3})*)\s*до\s*(\d+(?:\s?\d{3})*)",
            # "X - Y", "X-Y"
            r"(\d+(?:\s?\d{3})*)\s*-\s*(\d+(?:\s?\d{3})*)",
            # "X до Y"
            r"(\d+(?:\s?\d{3})*)\s*до\s*(\d+(?:\s?\d{3})*)",
        ]

        # Пытаемся найти диапазон
        for pattern in patterns:
            match = re.search(pattern, clean_range)
            if match:
                from_salary = int(re.sub(r"\s", "", match.group(1)))
                to_salary = int(re.sub(r"\s", "", match.group(2)))
                return {"from": from_salary, "to": to_salary, "currency": "RUR"}  # По умолчанию рубли

        # Паттерны для одиночных значений
        single_patterns = [
            # "от X"
            (r"от\s*(\d+(?:\s?\d{3})*)", "from"),
            # "до Y"
            (r"до\s*(\d+(?:\s?\d{3})*)", "to"),
            # просто число
            (r"^(\d+(?:\s?\d{3})*)$", "from"),
        ]

        for pattern, field in single_patterns:
            match = re.search(pattern, clean_range)
            if match:
                salary_value = int(re.sub(r"\s", "", match.group(1)))
                return {field: salary_value, "currency": "RUR"}

        return {}

    @property
    def salary_from(self) -> Optional[int]:
        return self._salary_from

    @property
    def salary_to(self) -> Optional[int]:
        return self._salary_to

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def from_amount(self) -> Optional[int]:
        """Alias for amount_from for backwards compatibility"""
        return self.amount_from

    @property
    def to_amount(self) -> Optional[int]:
        """Alias for amount_to for backwards compatibility"""
        return self.amount_to

    @property
    def average(self) -> int:
        """Среднее значение зарплаты"""
        if self.amount_from and self.amount_to:
            return (self.amount_from + self.amount_to) // 2
        return self.amount_from or self.amount_to or 0

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "from": self.amount_from,
            "to": self.amount_to,
            "currency": self.currency,
            "gross": self.gross,
            "period": self.period,
        }

    def get_max_salary(self) -> Optional[int]:
        """Возвращает максимальную зарплату из диапазона"""
        if self.salary_to is not None:
            return self.salary_to
        elif self.salary_from is not None:
            return self.salary_from
        else:
            return 0

    CURRENCY_SYMBOLS = {"RUR": "руб.", "USD": "$", "EUR": "€"}

    def __str__(self) -> str:
        """Строковое представление зарплаты"""
        if not self.amount_from and not self.amount_to:
            return "Не указана"

        components = []
        if self.amount_from:
            components.append(f"от {self.amount_from:,}")
        if self.amount_to:
            components.append(f"до {self.amount_to:,}")

        currency = self.CURRENCY_SYMBOLS.get(self.currency, self.currency)

        # Добавляем период если указан
        period_str = ""
        if self.period:
            # Исправляем формат периода для SuperJob
            if self.period in ["месяц", "month"]:
                period_str = "в месяц"
            else:
                period_str = f"в {self.period}"

        gross = " до вычета налогов" if self.gross else ""

        return f"{' '.join(components)} {currency} {period_str}{gross}".strip()
