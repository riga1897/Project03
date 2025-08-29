"""
Тесты для модуля Paginator
"""

import pytest

from src.utils.paginator import Paginator


class TestPaginator:
    """Тесты для класса Paginator"""

    @pytest.fixture
    def sample_data(self):
        """Фикстура с тестовыми данными"""
        return list(range(1, 51))  # 50 элементов

    def test_paginator_initialization(self, sample_data):
        """Тест инициализации пагинатора"""
        paginator = Paginator(sample_data, page_size=10)
        assert paginator.total_items == 50
        assert paginator.page_size == 10
        assert paginator.total_pages == 5
        assert paginator.current_page == 1

    def test_get_current_page_data(self, sample_data):
        """Тест получения данных текущей страницы"""
        paginator = Paginator(sample_data, page_size=10)
        page_data = paginator.get_current_page_data()
        assert len(page_data) == 10
        assert page_data == list(range(1, 11))

    def test_next_page(self, sample_data):
        """Тест перехода к следующей странице"""
        paginator = Paginator(sample_data, page_size=10)
        assert paginator.next_page() is True
        assert paginator.current_page == 2
        page_data = paginator.get_current_page_data()
        assert page_data == list(range(11, 21))

    def test_next_page_at_end(self, sample_data):
        """Тест перехода к следующей странице на последней странице"""
        paginator = Paginator(sample_data, page_size=10)
        paginator.current_page = 5  # Последняя страница
        assert paginator.next_page() is False
        assert paginator.current_page == 5

    def test_previous_page(self, sample_data):
        """Тест перехода к предыдущей странице"""
        paginator = Paginator(sample_data, page_size=10)
        paginator.current_page = 2
        assert paginator.previous_page() is True
        assert paginator.current_page == 1

    def test_previous_page_at_start(self, sample_data):
        """Тест перехода к предыдущей странице на первой странице"""
        paginator = Paginator(sample_data, page_size=10)
        assert paginator.previous_page() is False
        assert paginator.current_page == 1

    def test_go_to_page_valid(self, sample_data):
        """Тест перехода к корректной странице"""
        paginator = Paginator(sample_data, page_size=10)
        assert paginator.go_to_page(3) is True
        assert paginator.current_page == 3

    def test_go_to_page_invalid(self, sample_data):
        """Тест перехода к некорректной странице"""
        paginator = Paginator(sample_data, page_size=10)
        assert paginator.go_to_page(10) is False
        assert paginator.current_page == 1

    def test_empty_data(self):
        """Тест пагинации с пустыми данными"""
        paginator = Paginator([], page_size=10)
        assert paginator.total_items == 0
        assert paginator.total_pages == 0
        assert paginator.get_current_page_data() == []

    def test_single_page_data(self):
        """Тест пагинации с данными на одну страницу"""
        data = [1, 2, 3]
        paginator = Paginator(data, page_size=10)
        assert paginator.total_pages == 1
        assert paginator.get_current_page_data() == [1, 2, 3]

    def test_page_info(self, sample_data):
        """Тест получения информации о странице"""
        paginator = Paginator(sample_data, page_size=10)
        info = paginator.get_page_info()
        assert "current_page" in info
        assert "total_pages" in info
        assert "total_items" in info
        assert info["current_page"] == 1
        assert info["total_pages"] == 5
        assert info["total_items"] == 50
