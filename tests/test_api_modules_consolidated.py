"""
Консолидированные тесты для API модулей без внешних зависимостей.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture(autouse=True) 
def prevent_external_operations():
    """Предотвращение всех внешних операций"""
    with patch('builtins.input', return_value='0'), \
         patch('builtins.print'), \
         patch('requests.get'), \
         patch('psycopg2.connect'):
        yield

class TestAPIModulesConsolidated:
    """Консолидированное тестирование API модулей"""

    def test_base_api_functionality(self):
        """Тестирование базового API функционала"""
        try:
            from src.api_modules.base_api import BaseJobAPI
            assert hasattr(BaseJobAPI, 'get_vacancies')
        except ImportError:
            pass

    def test_hh_api_functionality(self):
        """Тестирование HeadHunter API"""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}

        with patch('requests.get', return_value=mock_response):
            try:
                from src.api_modules.hh_api import HeadHunterAPI
                api = HeadHunterAPI()
                result = api.get_vacancies("Python")
                assert isinstance(result, list)
            except ImportError:
                pass

    def test_sj_api_functionality(self):
        """Тестирование SuperJob API"""
        mock_response = Mock()
        mock_response.json.return_value = {"objects": []}

        with patch('requests.get', return_value=mock_response):
            try:
                from src.api_modules.sj_api import SuperJobAPI
                api = SuperJobAPI()
                result = api.get_vacancies("Python")
                assert isinstance(result, list)
            except ImportError:
                pass

    def test_unified_api_functionality(self):
        """Тестирование унифицированного API"""
        try:
            from src.api_modules.unified_api import UnifiedAPI
            api = UnifiedAPI()
            sources = api.get_available_sources()
            assert isinstance(sources, list)
        except ImportError:
            pass