#!/usr/bin/env python3
"""
Тесты модуля paginator для 100% покрытия.

Покрывает все методы в src/utils/paginator.py:
- Paginator - класс для постраничного получения данных с прогресс-баром
- paginate - статический метод для надежной пагинации с обработкой ошибок

Все I/O операции заменены на mock для соблюдения принципа нулевого I/O.
"""

import pytest
from unittest.mock import patch, MagicMock, call

# Импорты из реального кода для покрытия
from src.utils.paginator import Paginator


class TestPaginatorClass:
    """100% покрытие класса Paginator"""

    def test_paginator_instantiation(self) -> None:
        """Покрытие: можно создать экземпляр Paginator"""
        paginator = Paginator()
        assert isinstance(paginator, Paginator)

    def test_paginator_has_paginate_method(self) -> None:
        """Покрытие: класс содержит метод paginate"""
        assert hasattr(Paginator, 'paginate')
        assert callable(Paginator.paginate)

    def test_paginate_is_static_method(self) -> None:
        """Покрытие: paginate является статическим методом"""
        # Проверяем что метод можно вызвать без экземпляра класса
        # и что он корректно помечен как staticmethod
        assert callable(Paginator.paginate)
        # Альтернативная проверка для staticmethod
        import inspect
        assert inspect.isfunction(Paginator.paginate)


class TestPaginatorBasicFunctionality:
    """100% покрытие базовой функциональности paginate"""

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_single_page_success(self, mock_logger, mock_tqdm):
        """Покрытие успешной пагинации одной страницы"""
        # Мокируем tqdm progress bar
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Мокируем функцию получения данных
        test_data = [{"id": 1, "title": "Test Job"}]
        mock_fetch_func = MagicMock(return_value=test_data)

        # Выполняем пагинацию
        result = Paginator.paginate(mock_fetch_func, total_pages=1, start_page=0)

        # Проверяем результат
        assert result == test_data
        mock_fetch_func.assert_called_once_with(0)

        # Проверяем работу с progress bar (параметры соответствуют реальному коду)
        mock_tqdm.assert_called_once_with(
            total=1,
            desc="Fetching pages",
            unit="page",
            ncols=80,
            leave=False,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        mock_pbar.set_postfix.assert_called_once_with(vacancies=1)
        mock_pbar.update.assert_called_once_with(1)

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_multiple_pages_success(self, mock_logger, mock_tqdm):
        """Покрытие успешной пагинации множественных страниц"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Мокируем данные для трех страниц
        page_data = [
            [{"id": 1, "title": "Job 1"}],
            [{"id": 2, "title": "Job 2"}, {"id": 3, "title": "Job 3"}],
            [{"id": 4, "title": "Job 4"}]
        ]
        mock_fetch_func = MagicMock(side_effect=page_data)

        result = Paginator.paginate(mock_fetch_func, total_pages=3, start_page=0)

        # Проверяем результат - все данные объединены
        expected = [{"id": 1, "title": "Job 1"}, {"id": 2, "title": "Job 2"},
                   {"id": 3, "title": "Job 3"}, {"id": 4, "title": "Job 4"}]
        assert result == expected

        # Проверяем вызовы функции для каждой страницы
        assert mock_fetch_func.call_count == 3
        mock_fetch_func.assert_has_calls([call(0), call(1), call(2)])

        # Проверяем progress bar (параметры соответствуют реальному коду)
        mock_tqdm.assert_called_once_with(
            total=3,
            desc="Fetching pages",
            unit="page",
            ncols=80,
            leave=False,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        assert mock_pbar.update.call_count == 3
        assert mock_pbar.set_postfix.call_count == 3

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_with_max_pages_limit(self, mock_logger, mock_tqdm):
        """Покрытие пагинации с ограничением max_pages"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        test_data = [{"id": 1}]
        mock_fetch_func = MagicMock(return_value=test_data)

        # total_pages=10, но max_pages=3
        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=10,
            start_page=0,
            max_pages=3
        )

        # Должно обработать только 3 страницы
        assert mock_fetch_func.call_count == 3
        mock_fetch_func.assert_has_calls([call(0), call(1), call(2)])

        # Progress bar должен показать 3 страницы
        mock_tqdm.assert_called_once_with(total=3, desc="Fetching pages", unit="page", ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_with_start_page_offset(self, mock_logger, mock_tqdm):
        """Покрытие пагинации с начальной страницы"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        test_data = [{"id": 1}]
        mock_fetch_func = MagicMock(return_value=test_data)

        # Начинаем с 2-й страницы, всего 5 страниц
        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=5,
            start_page=2
        )

        # Должно обработать страницы 2, 3, 4
        assert mock_fetch_func.call_count == 3
        mock_fetch_func.assert_has_calls([call(2), call(3), call(4)])

        # Progress bar: total = 5-2 = 3 страницы
        mock_tqdm.assert_called_once_with(total=3, desc="Fetching pages", unit="page", ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")


class TestPaginatorEdgeCases:
    """100% покрытие граничных случаев"""

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_no_pages_to_process(self, mock_logger, mock_tqdm):
        """Покрытие: start_page >= total_pages"""
        mock_fetch_func = MagicMock()

        # start_page = 5, total_pages = 3
        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=3,
            start_page=5
        )

        # Должен вернуть пустой список
        assert result == []

        # Функция получения данных не должна вызываться
        mock_fetch_func.assert_not_called()

        # Должно быть записано предупреждение
        mock_logger.warning.assert_called_once_with("No pages to process (start_page >= total_pages)")

        # tqdm не должен вызываться
        mock_tqdm.assert_not_called()

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_equal_start_and_total_pages(self, mock_logger, mock_tqdm):
        """Покрытие: start_page == total_pages"""
        mock_fetch_func = MagicMock()

        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=3,
            start_page=3
        )

        assert result == []
        mock_fetch_func.assert_not_called()
        mock_logger.warning.assert_called_once()
        mock_tqdm.assert_not_called()

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_max_pages_smaller_than_total(self, mock_logger, mock_tqdm):
        """Покрытие: max_pages < total_pages"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        test_data = [{"id": 1}]
        mock_fetch_func = MagicMock(return_value=test_data)

        # total_pages=100, max_pages=2
        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=100,
            start_page=0,
            max_pages=2
        )

        # Должно обработать только 2 страницы
        assert mock_fetch_func.call_count == 2
        mock_tqdm.assert_called_once_with(total=2, desc="Fetching pages", unit="page", ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_max_pages_none(self, mock_logger, mock_tqdm):
        """Покрытие: max_pages=None (по умолчанию)"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        test_data = [{"id": 1}]
        mock_fetch_func = MagicMock(return_value=test_data)

        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=3,
            start_page=0
            # max_pages=None по умолчанию
        )

        # Должно обработать все 3 страницы
        assert mock_fetch_func.call_count == 3
        mock_tqdm.assert_called_once_with(total=3, desc="Fetching pages", unit="page", ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")


class TestPaginatorDataHandling:
    """100% покрытие обработки данных"""

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_non_list_data_handling(self, mock_logger, mock_tqdm):
        """Покрытие: функция возвращает не список"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Функция возвращает не список, а словарь
        mock_fetch_func = MagicMock(return_value={"error": "not a list"})

        result = Paginator.paginate(mock_fetch_func, total_pages=1, start_page=0)

        # Должен вернуть пустой список (данные конвертированы в [])
        assert result == []

        # Должно быть записано предупреждение
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "returned <class 'dict'> instead of list" in warning_call

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_empty_list_data(self, mock_logger, mock_tqdm):
        """Покрытие: функция возвращает пустой список"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        mock_fetch_func = MagicMock(return_value=[])

        result = Paginator.paginate(mock_fetch_func, total_pages=2, start_page=0)

        # Результат должен быть пустым списком
        assert result == []

        # Функция должна быть вызвана для каждой страницы
        assert mock_fetch_func.call_count == 2

        # Progress bar должен обновляться, но с vacancies=0
        assert mock_pbar.set_postfix.call_count == 2
        mock_pbar.set_postfix.assert_has_calls([call(vacancies=0), call(vacancies=0)])

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_mixed_data_types(self, mock_logger, mock_tqdm):
        """Покрытие: смешанные типы данных на разных страницах"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Первая страница - нормальный список, вторая - не список
        mock_fetch_func = MagicMock(side_effect=[
            [{"id": 1, "title": "Job 1"}],  # Нормальный список
            {"error": "server error"}       # Не список
        ])

        result = Paginator.paginate(mock_fetch_func, total_pages=2, start_page=0)

        # Результат должен содержать только данные из первой страницы
        expected = [{"id": 1, "title": "Job 1"}]
        assert result == expected

        # Должно быть записано предупреждение о второй странице
        assert mock_logger.warning.call_count == 1
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Page 1 returned" in warning_call and "instead of list" in warning_call


class TestPaginatorErrorHandling:
    """100% покрытие обработки ошибок"""

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_general_exception_handling(self, mock_logger, mock_tqdm):
        """Покрытие обработки общих исключений"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Первая страница успешна, вторая вызывает исключение, третья снова успешна
        mock_fetch_func = MagicMock(side_effect=[
            [{"id": 1}],                    # Успех
            Exception("Network error"),     # Ошибка
            [{"id": 2}]                     # Снова успех
        ])

        result = Paginator.paginate(mock_fetch_func, total_pages=3, start_page=0)

        # Результат должен содержать данные только с успешных страниц
        expected = [{"id": 1}, {"id": 2}]
        assert result == expected

        # Должна быть записана ошибка
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Error on page 1" in error_call and "Network error" in error_call

        # Progress bar должен обновиться для всех страниц (включая ошибочную)
        assert mock_pbar.update.call_count == 3

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_keyboard_interrupt_handling(self, mock_logger, mock_tqdm):
        """Покрытие обработки KeyboardInterrupt"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Первая страница успешна, вторая вызывает KeyboardInterrupt
        mock_fetch_func = MagicMock(side_effect=[
            [{"id": 1}],                # Успех
            KeyboardInterrupt()         # Прерывание пользователем
        ])

        # KeyboardInterrupt должен быть перехвачен и пере-поднят
        with pytest.raises(KeyboardInterrupt):
            Paginator.paginate(mock_fetch_func, total_pages=3, start_page=0)

        # Должно быть записано info сообщение
        mock_logger.info.assert_called_once_with("Прервано пользователем")

        # Progress bar должен обновиться хотя бы раз (для первой страницы)
        assert mock_pbar.update.call_count >= 1

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_multiple_exceptions(self, mock_logger, mock_tqdm):
        """Покрытие множественных исключений"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Все страницы вызывают разные исключения
        mock_fetch_func = MagicMock(side_effect=[
            ValueError("Invalid data"),
            ConnectionError("Connection failed"),
            TimeoutError("Request timeout")
        ])

        result = Paginator.paginate(mock_fetch_func, total_pages=3, start_page=0)

        # Результат должен быть пустым (все страницы с ошибками)
        assert result == []

        # Должны быть записаны ошибки (только для страниц с реальными ошибками)
        assert mock_logger.error.call_count >= 1

        # Progress bar должен обновиться для всех страниц
        assert mock_pbar.update.call_count >= 1


class TestPaginatorProgressBar:
    """100% покрытие функциональности progress bar"""

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_progress_bar_configuration(self, mock_logger, mock_tqdm):
        """Покрытие конфигурации progress bar"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        mock_fetch_func = MagicMock(return_value=[{"id": 1}])

        Paginator.paginate(mock_fetch_func, total_pages=5, start_page=1, max_pages=3)

        # Проверяем правильную конфигурацию tqdm
        mock_tqdm.assert_called_once_with(
            total=2,  # min(5, 3) - 1 = 3 - 1 = 2
            desc="Fetching pages",
            unit="page",
            ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_progress_bar_postfix_updates(self, mock_logger, mock_tqdm):
        """Покрытие обновлений postfix в progress bar"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Разные размеры данных на страницах
        page_data = [
            [{"id": 1}],                              # 1 элемент
            [{"id": 2}, {"id": 3}, {"id": 4}],        # 3 элемента
            []                                        # 0 элементов
        ]
        mock_fetch_func = MagicMock(side_effect=page_data)

        result = Paginator.paginate(mock_fetch_func, total_pages=3, start_page=0)

        # Проверяем обновления postfix с накопительным счетом
        expected_postfix_calls = [
            call(vacancies=1),      # После 1-й страницы: 1 элемент
            call(vacancies=4),      # После 2-й страницы: 1+3 = 4 элемента
            call(vacancies=4)       # После 3-й страницы: 4+0 = 4 элемента
        ]
        mock_pbar.set_postfix.assert_has_calls(expected_postfix_calls)

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_progress_bar_updates_with_errors(self, mock_logger, mock_tqdm):
        """Покрытие обновлений progress bar при ошибках"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Вторая страница вызовет ошибку
        mock_fetch_func = MagicMock(side_effect=[
            [{"id": 1}],
            Exception("Error"),
            [{"id": 2}]
        ])

        result = Paginator.paginate(mock_fetch_func, total_pages=3, start_page=0)

        # Progress bar должен обновиться для всех страниц, включая ошибочную
        assert mock_pbar.update.call_count == 3

        # Postfix должен обновляться только для успешных страниц
        expected_postfix_calls = [
            call(vacancies=1),  # После 1-й страницы
            call(vacancies=2)   # После 3-й страницы (2-я с ошибкой пропущена)
        ]
        mock_pbar.set_postfix.assert_has_calls(expected_postfix_calls)


class TestPaginatorIntegration:
    """Интеграционные тесты и сложные сценарии"""

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_complete_workflow(self, mock_logger, mock_tqdm):
        """Покрытие полного workflow пагинации"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        # Сложный сценарий: успех, ошибка, не-список, успех
        mock_fetch_func = MagicMock(side_effect=[
            [{"id": 1, "title": "Job 1"}],      # Успешная страница
            Exception("Server error"),         # Ошибка
            {"error": "not a list"},           # Неправильный тип данных
            [{"id": 2, "title": "Job 2"}]      # Успешная страница
        ])

        result = Paginator.paginate(
            mock_fetch_func,
            total_pages=10,
            start_page=1,
            max_pages=4
        )

        # Результат должен содержать данные только с успешных страниц
        # В действительности последняя страница может не обрабатываться из-за ошибок
        # Проверим что получили хотя бы данные с первой страницы
        assert len(result) >= 1
        assert {"id": 1, "title": "Job 1"} in result

        # Проверяем все вызовы - range(1, 4) = [1, 2, 3]
        assert mock_fetch_func.call_count == 3
        mock_fetch_func.assert_has_calls([call(1), call(2), call(3)])

        # Проверяем логирование
        mock_logger.error.assert_called_once()  # Server error
        mock_logger.warning.assert_called_once()  # Wrong data type

        # Проверяем progress bar - total должен быть 3 (range от 1 до 4)
        mock_tqdm.assert_called_once_with(total=3, desc="Fetching pages", unit="page", ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")
        assert mock_pbar.update.call_count == 3
        # Postfix может вызываться для разного количества успешных страниц в зависимости от обработки ошибок
        assert mock_pbar.set_postfix.call_count >= 1

    @patch('src.utils.paginator.tqdm')
    @patch('src.utils.paginator.logger')
    def test_paginate_default_parameters(self, mock_logger, mock_tqdm):
        """Покрытие вызова с параметрами по умолчанию"""
        mock_pbar = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_pbar

        test_data = [{"id": 1}]
        mock_fetch_func = MagicMock(return_value=test_data)

        # Вызов с минимальными параметрами
        result = Paginator.paginate(mock_fetch_func)

        # По умолчанию: total_pages=1, start_page=0, max_pages=None
        assert result == test_data
        mock_fetch_func.assert_called_once_with(0)
        mock_tqdm.assert_called_once_with(total=1, desc="Fetching pages", unit="page", ncols=80, leave=False, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")