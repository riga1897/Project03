#!/usr/bin/env python3
"""
Тесты модуля salary для 100% покрытия.

Покрывает все функции в src/utils/salary.py:
- Salary - класс для обработки зарплатных данных
- __init__ - конструктор с различными типами входных данных
- _validate_salary_value - валидация значений зарплаты
- _validate_currency - валидация валюты
- _parse_salary_range_string - парсинг строк с диапазонами зарплат
- Все свойства и публичные методы

Все тесты следуют принципу нулевого I/O.
"""

import pytest

# Импорты из реального кода для покрытия
from src.utils.salary import Salary


class TestSalaryInit:
    """100% покрытие конструктора Salary"""

    def test_init_none_data(self) -> None:
        """Покрытие инициализации с None"""
        salary = Salary(None)

        assert salary.amount_from == 0
        assert salary.amount_to == 0
        assert salary.gross is False
        assert salary.period == "month"
        assert salary.currency == "RUR"

    def test_init_empty_dict(self) -> None:
        """Покрытие инициализации с пустым словарем"""
        salary = Salary({})

        assert salary.amount_from == 0
        assert salary.amount_to == 0
        assert salary.gross is False
        assert salary.period == "month"

    def test_init_string_data(self) -> None:
        """Покрытие инициализации со строкой"""
        salary = Salary("от 50000 до 100000")

        assert salary.salary_from == 50000
        assert salary.salary_to == 100000
        assert salary.currency == "RUR"

    def test_init_dict_with_salary_range(self) -> None:
        """Покрытие инициализации с salary_range в словаре"""
        data = {
            "salary_range": "100000-150000",
            "gross": True
        }
        salary = Salary(data)

        assert salary.salary_from == 100000
        assert salary.salary_to == 150000
        assert salary.gross is True

    def test_init_with_from_to_values(self) -> None:
        """Покрытие инициализации с from/to значениями"""
        data = {
            "from": 75000,
            "to": 125000,
            "currency": "USD",
            "gross": True
        }
        salary = Salary(data)

        assert salary.salary_from == 75000
        assert salary.salary_to == 125000
        assert salary.currency == "USD"
        assert salary.amount_from == 75000
        assert salary.amount_to == 125000
        assert salary.gross is True

    def test_init_with_complex_salary_range_dict(self) -> None:
        """Покрытие инициализации со сложной структурой salary_range"""
        data = {
            "salary_range": {
                "from": 80000,
                "to": 120000,
                "mode": {
                    "id": "year",
                    "name": "год"
                }
            },
            "gross": False
        }
        salary = Salary(data)

        assert salary.amount_from == 80000
        assert salary.amount_to == 120000
        assert salary.period == "year"
        assert salary.gross is False

    def test_init_invalid_currency(self) -> None:
        """Покрытие инициализации с невалидной валютой"""
        data = {
            "currency": None,
            "from": 50000
        }
        salary = Salary(data)

        assert salary.currency == "RUR"  # По умолчанию


class TestSalaryValidateSalaryValue:
    """100% покрытие статического метода _validate_salary_value"""

    def test_validate_salary_value_none(self) -> None:
        """Покрытие None значения"""
        result = Salary._validate_salary_value(None)
        assert result is None

    def test_validate_salary_value_valid_int(self) -> None:
        """Покрытие валидного целого числа"""
        result = Salary._validate_salary_value(100000)
        assert result == 100000

    def test_validate_salary_value_valid_string(self) -> None:
        """Покрытие валидной строки с числом"""
        result = Salary._validate_salary_value("75000")
        assert result == 75000

    def test_validate_salary_value_zero(self) -> None:
        """Покрытие нулевого значения"""
        result = Salary._validate_salary_value(0)
        assert result is None  # Нуль не валидная зарплата

    def test_validate_salary_value_negative(self) -> None:
        """Покрытие отрицательного значения"""
        result = Salary._validate_salary_value(-50000)
        assert result is None

    def test_validate_salary_value_invalid_string(self) -> None:
        """Покрытие невалидной строки"""
        result = Salary._validate_salary_value("not_a_number")
        assert result is None

    def test_validate_salary_value_float(self) -> None:
        """Покрытие float значения"""
        result = Salary._validate_salary_value(75000.5)
        assert result == 75000  # int() обрезает дробную часть

    def test_validate_salary_value_type_error(self) -> None:
        """Покрытие TypeError (например, list)"""
        result = Salary._validate_salary_value([100000])
        assert result is None


class TestSalaryValidateCurrency:
    """100% покрытие статического метода _validate_currency"""

    def test_validate_currency_valid_string(self) -> None:
        """Покрытие валидной строки валюты"""
        result = Salary._validate_currency("usd")
        assert result == "USD"

    def test_validate_currency_none(self) -> None:
        """Покрытие None значения"""
        result = Salary._validate_currency(None)
        assert result == "RUR"

    def test_validate_currency_empty_string(self) -> None:
        """Покрытие пустой строки"""
        result = Salary._validate_currency("")
        assert result == "RUR"

    def test_validate_currency_not_string(self) -> None:
        """Покрытие не-строкового значения"""
        result = Salary._validate_currency(123)
        assert result == "RUR"

    def test_validate_currency_whitespace(self) -> None:
        """Покрытие строки с пробелами"""
        result = Salary._validate_currency("  eur  ")
        assert result == "EUR"

    def test_validate_currency_mixed_case(self) -> None:
        """Покрытие смешанного регистра"""
        result = Salary._validate_currency("RuR")
        assert result == "RUR"


class TestSalaryParseSalaryRangeString:
    """100% покрытие статического метода _parse_salary_range_string"""

    def test_parse_none_or_empty(self) -> None:
        """Покрытие None и пустых значений"""
        assert Salary._parse_salary_range_string(None) == {}
        assert Salary._parse_salary_range_string("") == {}
        assert Salary._parse_salary_range_string("   ") == {}

    def test_parse_not_string(self) -> None:
        """Покрытие не-строкового значения"""
        assert Salary._parse_salary_range_string(123) == {}

    def test_parse_from_to_format(self) -> None:
        """Покрытие формата 'от X до Y'"""
        result = Salary._parse_salary_range_string("от 50000 до 100000")
        expected = {"from": 50000, "to": 100000, "currency": "RUR"}
        assert result == expected

    def test_parse_hyphen_format(self) -> None:
        """Покрытие формата 'X - Y'"""
        result = Salary._parse_salary_range_string("75000 - 125000")
        expected = {"from": 75000, "to": 125000, "currency": "RUR"}
        assert result == expected

    def test_parse_hyphen_no_spaces(self) -> None:
        """Покрытие формата 'X-Y' без пробелов"""
        result = Salary._parse_salary_range_string("60000-90000")
        expected = {"from": 60000, "to": 90000, "currency": "RUR"}
        assert result == expected

    def test_parse_numbers_with_spaces(self) -> None:
        """Покрытие чисел с пробелами (разделители тысяч)"""
        result = Salary._parse_salary_range_string("100 000 - 150 000")
        expected = {"from": 100000, "to": 150000, "currency": "RUR"}
        assert result == expected

    def test_parse_from_only(self) -> None:
        """Покрытие формата 'от X'"""
        result = Salary._parse_salary_range_string("от 80000")
        expected = {"from": 80000, "currency": "RUR"}
        assert result == expected

    def test_parse_to_only(self) -> None:
        """Покрытие формата 'до Y'"""
        result = Salary._parse_salary_range_string("до 120000")
        expected = {"to": 120000, "currency": "RUR"}
        assert result == expected

    def test_parse_single_number(self) -> None:
        """Покрытие простого числа"""
        result = Salary._parse_salary_range_string("95000")
        expected = {"from": 95000, "currency": "RUR"}
        assert result == expected

    def test_parse_single_number_with_spaces(self) -> None:
        """Покрытие простого числа с разделителями тысяч"""
        result = Salary._parse_salary_range_string("95 000")
        expected = {"from": 95000, "currency": "RUR"}
        assert result == expected

    def test_parse_x_do_y_format(self) -> None:
        """Покрытие формата 'X до Y'"""
        result = Salary._parse_salary_range_string("70000 до 110000")
        expected = {"from": 70000, "to": 110000, "currency": "RUR"}
        assert result == expected

    def test_parse_case_insensitive(self) -> None:
        """Покрытие нечувствительности к регистру"""
        result = Salary._parse_salary_range_string("ОТ 60000 ДО 90000")
        expected = {"from": 60000, "to": 90000, "currency": "RUR"}
        assert result == expected

    def test_parse_with_currency_text(self) -> None:
        """Покрытие строк с валютным текстом (игнорируется)"""
        result = Salary._parse_salary_range_string("от 50000 до 100000 рублей")
        expected = {"from": 50000, "to": 100000, "currency": "RUR"}
        assert result == expected

    def test_parse_invalid_format(self) -> None:
        """Покрытие невалидного формата"""
        result = Salary._parse_salary_range_string("договорная")
        assert result == {}

    def test_parse_mixed_valid_invalid(self) -> None:
        """Покрытие смешанного валидного и невалидного текста"""
        result = Salary._parse_salary_range_string("зарплата от 70000 рублей в месяц")
        expected = {"from": 70000, "currency": "RUR"}
        assert result == expected


class TestSalaryValidateAndSet:
    """100% покрытие приватного метода _validate_and_set"""

    def test_validate_and_set_not_dict(self) -> None:
        """Покрытие не-словарных данных"""
        salary = Salary()
        salary._validate_and_set("not a dict")

        # Должны остаться значения по умолчанию
        assert salary.amount_from == 0
        assert salary.amount_to == 0

    def test_validate_and_set_basic_values(self) -> None:
        """Покрытие базовых значений from/to"""
        salary = Salary()
        data = {
            "from": 60000,
            "to": 90000,
            "gross": True
        }
        salary._validate_and_set(data)

        assert salary.amount_from == 60000
        assert salary.amount_to == 90000
        assert salary.gross is True

    def test_validate_and_set_none_values(self) -> None:
        """Покрытие None значений (должны стать 0)"""
        salary = Salary()
        data = {
            "from": None,
            "to": None
        }
        salary._validate_and_set(data)

        assert salary.amount_from == 0
        assert salary.amount_to == 0

    def test_validate_and_set_salary_range_dict(self) -> None:
        """Покрытие salary_range как словаря"""
        salary = Salary()
        data = {
            "salary_range": {
                "from": 70000,
                "to": 100000,
                "mode": {
                    "id": "year"
                }
            }
        }
        salary._validate_and_set(data)

        assert salary.amount_from == 70000
        assert salary.amount_to == 100000
        assert salary.period == "year"

    def test_validate_and_set_salary_range_no_mode(self) -> None:
        """Покрытие salary_range без mode"""
        salary = Salary()
        data = {
            "salary_range": {
                "from": 80000,
                "to": 120000
            }
        }
        salary._validate_and_set(data)

        assert salary.amount_from == 80000
        assert salary.amount_to == 120000
        assert salary.period == "month"  # По умолчанию

    def test_validate_and_set_salary_range_invalid_mode(self) -> None:
        """Покрытие salary_range с невалидным mode"""
        salary = Salary()
        data = {
            "salary_range": {
                "from": 50000,
                "mode": "not a dict"
            }
        }
        salary._validate_and_set(data)

        assert salary.amount_from == 50000
        assert salary.period == "month"  # По умолчанию

    def test_validate_and_set_salary_range_empty_mode_id(self) -> None:
        """Покрытие salary_range с пустым mode id"""
        salary = Salary()
        data = {
            "salary_range": {
                "from": 55000,
                "mode": {
                    "id": ""
                }
            }
        }
        salary._validate_and_set(data)

        assert salary.amount_from == 55000
        assert salary.period == "month"  # Остается по умолчанию


class TestSalaryProperties:
    """100% покрытие всех свойств"""

    def test_salary_from_property(self) -> None:
        """Покрытие свойства salary_from"""
        data = {"from": 70000}
        salary = Salary(data)
        assert salary.salary_from == 70000

    def test_salary_to_property(self) -> None:
        """Покрытие свойства salary_to"""
        data = {"to": 90000}
        salary = Salary(data)
        assert salary.salary_to == 90000

    def test_currency_property(self) -> None:
        """Покрытие свойства currency"""
        data = {"currency": "USD"}
        salary = Salary(data)
        assert salary.currency == "USD"

    def test_from_amount_alias(self) -> None:
        """Покрытие алиаса from_amount"""
        data = {"from": 65000}
        salary = Salary(data)
        assert salary.from_amount == 65000

    def test_to_amount_alias(self) -> None:
        """Покрытие алиаса to_amount"""
        data = {"to": 85000}
        salary = Salary(data)
        assert salary.to_amount == 85000

    def test_average_both_values(self) -> None:
        """Покрытие average с обеими границами"""
        data = {"from": 80000, "to": 120000}
        salary = Salary(data)
        assert salary.average == 100000

    def test_average_from_only(self) -> None:
        """Покрытие average только с from"""
        data = {"from": 75000}
        salary = Salary(data)
        assert salary.average == 75000

    def test_average_to_only(self) -> None:
        """Покрытие average только с to"""
        data = {"to": 95000}
        salary = Salary(data)
        assert salary.average == 95000

    def test_average_no_values(self) -> None:
        """Покрытие average без значений"""
        salary = Salary({})
        assert salary.average == 0


class TestSalaryPublicMethods:
    """100% покрытие публичных методов"""

    def test_to_dict(self) -> None:
        """Покрытие to_dict метода"""
        data = {
            "from": 60000,
            "to": 90000,
            "currency": "EUR",
            "gross": True
        }
        salary = Salary(data)
        result = salary.to_dict()

        expected = {
            "from": 60000,
            "to": 90000,
            "currency": "EUR",
            "gross": True,
            "period": "month"
        }
        assert result == expected

    def test_get_max_salary_with_to(self) -> None:
        """Покрытие get_max_salary с to значением"""
        data = {"from": 70000, "to": 100000}
        salary = Salary(data)
        assert salary.get_max_salary() == 100000

    def test_get_max_salary_from_only(self) -> None:
        """Покрытие get_max_salary только с from"""
        data = {"from": 80000}
        salary = Salary(data)
        assert salary.get_max_salary() == 80000

    def test_get_max_salary_no_values(self) -> None:
        """Покрытие get_max_salary без значений"""
        salary = Salary({})
        assert salary.get_max_salary() == 0


class TestSalaryStringRepresentation:
    """100% покрытие строкового представления"""

    def test_str_no_values(self) -> None:
        """Покрытие __str__ без значений"""
        salary = Salary({})
        assert str(salary) == "Не указана"

    def test_str_from_only(self) -> None:
        """Покрытие __str__ только с from"""
        data = {"from": 75000}
        salary = Salary(data)
        result = str(salary)
        assert "от 75,000" in result
        assert "руб." in result

    def test_str_to_only(self) -> None:
        """Покрытие __str__ только с to"""
        data = {"to": 95000}
        salary = Salary(data)
        result = str(salary)
        assert "до 95,000" in result
        assert "руб." in result

    def test_str_both_values(self) -> None:
        """Покрытие __str__ с обеими границами"""
        data = {"from": 60000, "to": 90000}
        salary = Salary(data)
        result = str(salary)
        assert "от 60,000" in result
        assert "до 90,000" in result
        assert "руб." in result

    def test_str_usd_currency(self) -> None:
        """Покрытие __str__ с USD валютой"""
        data = {"from": 1000, "currency": "USD"}
        salary = Salary(data)
        result = str(salary)
        assert "$" in result

    def test_str_eur_currency(self) -> None:
        """Покрытие __str__ с EUR валютой"""
        data = {"from": 1000, "currency": "EUR"}
        salary = Salary(data)
        result = str(salary)
        assert "€" in result

    def test_str_unknown_currency(self) -> None:
        """Покрытие __str__ с неизвестной валютой"""
        data = {"from": 1000, "currency": "GBP"}
        salary = Salary(data)
        result = str(salary)
        assert "GBP" in result

    def test_str_with_gross(self) -> None:
        """Покрытие __str__ с gross флагом"""
        data = {"from": 80000, "gross": True}
        salary = Salary(data)
        result = str(salary)
        assert "до вычета налогов" in result

    def test_str_without_gross(self) -> None:
        """Покрытие __str__ без gross флага"""
        data = {"from": 80000, "gross": False}
        salary = Salary(data)
        result = str(salary)
        assert "до вычета налогов" not in result

    def test_str_month_period(self) -> None:
        """Покрытие __str__ с периодом месяц"""
        data = {"from": 70000}
        salary = Salary(data)
        salary.period = "month"
        result = str(salary)
        assert "в месяц" in result

    def test_str_month_russian_period(self) -> None:
        """Покрытие __str__ с русским периодом месяц"""
        data = {"from": 70000}
        salary = Salary(data)
        salary.period = "месяц"
        result = str(salary)
        assert "в месяц" in result

    def test_str_year_period(self) -> None:
        """Покрытие __str__ с периодом год"""
        data = {"from": 800000}
        salary = Salary(data)
        salary.period = "year"
        result = str(salary)
        assert "в year" in result

    def test_str_no_period(self) -> None:
        """Покрытие __str__ без периода"""
        data = {"from": 70000}
        salary = Salary(data)
        salary.period = ""
        result = str(salary)
        # Не должно содержать информацию о периоде
        assert "в" not in result.split()[-1]  # Последнее слово не должно быть "в"


class TestSalaryIntegration:
    """Интеграционные тесты и сложные сценарии"""

    def test_complex_initialization_flow(self) -> None:
        """Покрытие сложного потока инициализации"""
        # Тест с максимальным количеством данных
        data = {
            "from": 70000,
            "to": 120000,
            "currency": "usd",
            "gross": True,
            "salary_range": {
                "from": 75000,  # Должно перезаписать основное значение
                "to": 125000,   # Должно перезаписать основное значение
                "mode": {
                    "id": "YEAR",
                    "name": "В год"
                }
            }
        }

        salary = Salary(data)

        # Проверяем что salary_range перезаписал основные значения
        assert salary.amount_from == 75000
        assert salary.amount_to == 125000
        assert salary.currency == "USD"  # Приведено к верхнему регистру
        assert salary.gross is True
        assert salary.period == "year"  # Приведено к нижнему регистру

    def test_string_parsing_priority(self) -> None:
        """Покрытие приоритета парсинга строк"""
        # Если передается строка, она должна парситься независимо от других данных
        salary = Salary("от 50000 до 80000")

        assert salary.salary_from == 50000
        assert salary.salary_to == 80000
        assert salary.currency == "RUR"

    def test_edge_case_large_numbers(self) -> None:
        """Покрытие граничных случаев с большими числами"""
        data = {"from": 999999999, "to": 1000000000}
        salary = Salary(data)

        assert salary.average == 999999999  # Целочисленное деление
        assert salary.get_max_salary() == 1000000000

        # Проверяем форматирование больших чисел
        str_repr = str(salary)
        assert "999,999,999" in str_repr
        assert "1,000,000,000" in str_repr

    def test_currency_symbols_coverage(self) -> None:
        """Покрытие всех символов валют"""
        for currency, symbol in Salary.CURRENCY_SYMBOLS.items():
            data = {"from": 1000, "currency": currency}
            salary = Salary(data)
            result = str(salary)
            assert symbol in result

    def test_slots_attribute_access(self) -> None:
        """Покрытие ограничений __slots__"""
        salary = Salary({"from": 50000})

        # Эти атрибуты должны быть доступны
        assert hasattr(salary, 'amount_from')
        assert hasattr(salary, 'amount_to')
        assert hasattr(salary, 'gross')
        assert hasattr(salary, 'period')

        # Попытка добавить новый атрибут должна вызвать ошибку
        with pytest.raises(AttributeError):
            salary.new_attribute = "test"

    def test_regex_patterns_comprehensive(self) -> None:
        """Покрытие всех regex паттернов парсинга"""
        test_cases = [
            # Основные паттерны диапазонов
            ("от 100000 до 150000", {"from": 100000, "to": 150000}),
            ("100000 - 150000", {"from": 100000, "to": 150000}),
            ("100000-150000", {"from": 100000, "to": 150000}),
            ("100000 до 150000", {"from": 100000, "to": 150000}),

            # Одиночные значения
            ("от 80000", {"from": 80000}),
            ("до 120000", {"to": 120000}),
            ("95000", {"from": 95000}),

            # С разделителями тысяч
            ("100 000 - 150 000", {"from": 100000, "to": 150000}),
            ("95 000", {"from": 95000}),
        ]

        for test_string, expected in test_cases:
            result = Salary._parse_salary_range_string(test_string)
            for key, value in expected.items():
                assert result.get(key) == value
            assert result.get("currency") == "RUR"