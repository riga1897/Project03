"""
Конфигурация pytest для тестирования с полным покрытием.

Настраивает моки для всех I/O операций и внешних зависимостей.
"""

import os
import sys
from typing import Generator, Any
from unittest.mock import MagicMock, patch

import pytest

# Добавляем src в PATH для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# Глобальные моки для предотвращения реальных I/O операций
@pytest.fixture(autouse=True)
def mock_io_operations() -> Generator[dict[str, MagicMock], None, None]:
    """Автоматически мокает все I/O операции во всех тестах."""
    with patch('builtins.input') as mock_input, \
         patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('os.makedirs') as mock_makedirs, \
         patch('shutil.rmtree') as mock_rmtree, \
         patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.write_text') as mock_write, \
         patch('pathlib.Path.read_text') as mock_read:

        # Настраиваем базовые возвращаемые значения
        mock_input.return_value = "test_input"
        mock_get.return_value.json.return_value = {"items": []}
        mock_get.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        mock_post.return_value.status_code = 200
        mock_exists.return_value = True
        mock_read.return_value = "{}"

        yield {
            'input': mock_input,
            'get': mock_get,
            'post': mock_post,
            'makedirs': mock_makedirs,
            'rmtree': mock_rmtree,
            'mkdir': mock_mkdir,
            'exists': mock_exists,
            'write': mock_write,
            'read': mock_read
        }


@pytest.fixture
def mock_database() -> Generator[Any, None, None]:
    """Мок для всех операций с базой данных."""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = mock_conn
        yield mock_cursor


@pytest.fixture
def sample_vacancy_data() -> dict[str, Any]:
    """Образец данных вакансии для тестов."""
    return {
        "id": "test_123",
        "title": "Python Developer",
        "url": "https://test.com/vacancy/123",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "description": "Test description",
        "employer": {"name": "Test Company", "id": "company_123"},
        "area": "Москва",
        "experience": {"name": "1-3 года", "id": "exp_123"},
        "employment": {"name": "Полная занятость", "id": "emp_123"}
    }
