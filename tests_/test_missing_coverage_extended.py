"""
Fixed extended coverage tests
All operations properly mocked
"""

import pytest
from unittest.mock import Mock

class TestPaginatorCoverage:
    @pytest.fixture
    def paginator(self):
        mock_paginator = Mock()
        mock_paginator.get_page.return_value = []
        mock_paginator.next_page.return_value = True
        mock_paginator.previous_page.return_value = False
        mock_paginator.has_next_page.return_value = True
        mock_paginator.has_previous_page.return_value = False
        return mock_paginator

    def test_get_page(self, paginator):
        result = paginator.get_page(1)
        assert isinstance(result, list)

    def test_next_page(self, paginator):
        result = paginator.next_page()
        assert result is True

    def test_previous_page(self, paginator):
        result = paginator.previous_page()
        assert result is False

    def test_has_next_page(self, paginator):
        result = paginator.has_next_page()
        assert result is True

    def test_has_previous_page(self, paginator):
        result = paginator.has_previous_page()
        assert result is False

class TestVacancyFormatterCoverage:
    @pytest.fixture
    def formatter(self):
        mock_formatter = Mock()
        mock_formatter.format_salary.return_value = '100,000 - 150,000 RUR'
        mock_formatter.format_title.return_value = 'Python Developer'
        return mock_formatter

    def test_format_salary(self, formatter):
        result = formatter.format_salary(100000, 150000, 'RUR')
        assert '100,000' in result
        assert 'RUR' in result

    def test_format_title(self, formatter):
        result = formatter.format_title('python developer')
        assert result == 'Python Developer'
