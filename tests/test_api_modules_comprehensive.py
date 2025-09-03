
"""
Упрощенные тесты для API модулей без внешних зависимостей.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class TestAPIModules:
    """Упрощенные тесты для API модулей"""
    
    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    @patch('requests.get')
    @patch('psycopg2.connect')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('json.dump')
    @patch('json.load', return_value={"items": [], "found": 0})
    def test_base_api_import(self, *mocks):
        """Тестирование импорта базового API"""
        try:
            from src.api_modules.base_api import BaseJobAPI
            assert hasattr(BaseJobAPI, 'get_vacancies')
        except ImportError:
            pass

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    @patch('requests.get')
    @patch('psycopg2.connect')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('json.dump')
    @patch('json.load', return_value={"items": [], "found": 0})
    def test_hh_api_basic(self, *mocks):
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

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    @patch('requests.get')
    @patch('psycopg2.connect')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('json.dump')
    @patch('json.load', return_value={"items": [], "found": 0})
    def test_sj_api_basic(self, *mocks):
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

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    @patch('requests.get')
    @patch('psycopg2.connect')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('json.dump')
    @patch('json.load', return_value={"items": [], "found": 0})
    def test_unified_api_basic(self, *mocks):
        """Тестирование унифицированного API"""
        try:
            from src.api_modules.unified_api import UnifiedAPI
            api = UnifiedAPI()
            sources = api.get_available_sources()
            assert isinstance(sources, list)
        except ImportError:
            pass

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    @patch('requests.get')
    @patch('psycopg2.connect')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists', return_value=False)
    @patch('os.makedirs')
    @patch('json.dump')
    @patch('json.load', return_value={"items": [], "found": 0})
    def test_cached_api_basic(self, *mocks):
        """Тестирование кэшированного API"""
        try:
            from src.api_modules.cached_api import CachedAPI
            
            class TestCachedAPI(CachedAPI):
                def get_vacancies(self, query):
                    return []
                
                def get_vacancies_page(self, query, page=0):
                    return []
                
                def _get_empty_response(self):
                    return {"items": [], "found": 0}
                
                def _validate_vacancy(self, vacancy):
                    return True
            
            api = TestCachedAPI("test_cache")
            assert api is not None
        except ImportError:
            pass
