"""
100% покрытие parsers модулей: base_parser.py, hh_parser.py, sj_parser.py
Реальные импорты из src/, все I/O операции замокированы
"""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Реальные импорты для покрытия
from src.vacancies.parsers.base_parser import BaseParser
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.vacancies.models import Vacancy


class TestBaseParser:
    """100% покрытие BaseParser"""

    def test_cannot_instantiate_base_parser(self):
        """Тест что абстрактный класс BaseParser нельзя инстанцировать"""
        with pytest.raises(TypeError) as exc_info:
            BaseParser()
        assert "Can't instantiate abstract class" in str(exc_info.value)

    def test_concrete_parser_implementation(self):
        """Тест конкретной реализации BaseParser"""
        
        class ConcreteParser(BaseParser):
            def parse_vacancy(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
                """Покрывает строку 19 (pass)"""
                return {"parsed": raw_data}
            
            def parse_vacancies(self, raw_vacancies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                """Покрывает строку 32 (pass)"""
                return [self.parse_vacancy(vacancy) for vacancy in raw_vacancies]
        
        parser = ConcreteParser()
        
        # Тест parse_vacancy
        result_single = parser.parse_vacancy({"test": "data"})
        assert result_single == {"parsed": {"test": "data"}}
        
        # Тест parse_vacancies
        result_multiple = parser.parse_vacancies([{"test1": "data1"}, {"test2": "data2"}])
        assert len(result_multiple) == 2
        assert result_multiple[0] == {"parsed": {"test1": "data1"}}
        assert result_multiple[1] == {"parsed": {"test2": "data2"}}

    def test_incomplete_parser_implementation_fails(self):
        """Тест что неполная реализация BaseParser вызывает ошибку"""
        
        class IncompleteParser(BaseParser):
            def parse_vacancy(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
                return {}
            # Не реализуем parse_vacancies
        
        with pytest.raises(TypeError) as exc_info:
            IncompleteParser()
        assert "abstract method" in str(exc_info.value) or "abstract methods" in str(exc_info.value)


class TestHHParser:
    """100% покрытие HHParser"""

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    def test_hh_parser_init(self, mock_cache):
        """Тест инициализации HHParser - покрывает строки 14-16"""
        parser = HHParser("custom_cache_dir")
        
        mock_cache.assert_called_with("custom_cache_dir")
        assert parser.base_url == "https://api.hh.ru/vacancies"

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    def test_hh_parser_init_default_cache(self, mock_cache):
        """Тест инициализации с дефолтным cache_dir"""
        parser = HHParser()
        
        mock_cache.assert_called_with("data/cache/hh")

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    def test_parse_vacancies_empty_list(self, mock_cache):
        """Тест parse_vacancies с пустым списком - покрывает строки 20-21"""
        parser = HHParser()
        
        result = parser.parse_vacancies([])
        
        assert result == []

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parse_vacancies_valid_data(self, mock_from_dict, mock_cache):
        """Тест parse_vacancies с валидными данными - покрывает строки 22-59"""
        parser = HHParser()
        
        # Мокируем Vacancy.from_dict для возврата mock объекта
        mock_vacancy = Mock()
        mock_from_dict.return_value = mock_vacancy
        
        raw_data = [
            {
                "id": "123",
                "name": "Python Developer",
                "alternate_url": "https://hh.ru/vacancy/123",
                "description": "Test description"
            }
        ]
        
        with patch('src.vacancies.parsers.hh_parser.logger') as mock_logger:
            result = parser.parse_vacancies(raw_data)
            
            assert len(result) == 1
            assert result[0] == mock_vacancy
            mock_from_dict.assert_called_once()
            mock_logger.info.assert_called()

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    def test_parse_vacancies_missing_required_fields(self, mock_cache):
        """Тест пропуска вакансий без обязательных полей - покрывает строки 31-33"""
        parser = HHParser()
        
        raw_data = [
            {"id": "123"},  # Нет name и alternate_url
            {"name": "Test Job"}  # Нет alternate_url
        ]
        
        with patch('src.vacancies.parsers.hh_parser.logger') as mock_logger:
            result = parser.parse_vacancies(raw_data)
            
            assert result == []
            assert mock_logger.warning.call_count == 2

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parse_vacancies_adds_source(self, mock_from_dict, mock_cache):
        """Тест добавления источника - покрывает строки 36-37"""
        parser = HHParser()
        mock_from_dict.return_value = Mock()
        
        raw_data = [{
            "id": "123",
            "name": "Python Developer", 
            "alternate_url": "https://hh.ru/vacancy/123"
        }]
        
        parser.parse_vacancies(raw_data)
        
        # Проверяем что source был добавлен
        called_args = mock_from_dict.call_args[0][0]
        assert called_args["source"] == "hh.ru"

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parse_vacancies_enriches_description_from_snippet(self, mock_from_dict, mock_cache):
        """Тест обогащения description из snippet - покрывает строки 40-48"""
        parser = HHParser()
        mock_from_dict.return_value = Mock()
        
        raw_data = [{
            "id": "123",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123",
            "snippet": {
                "requirement": "Python, Django",
                "responsibility": "Разработка API"
            }
        }]
        
        parser.parse_vacancies(raw_data)
        
        called_args = mock_from_dict.call_args[0][0]
        expected_desc = "Требования: Python, Django Обязанности: Разработка API"
        assert called_args["description"] == expected_desc

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    @patch('src.vacancies.models.Vacancy.from_dict', side_effect=Exception("Parse error"))
    def test_parse_vacancies_handles_exception(self, mock_from_dict, mock_cache):
        """Тест обработки исключений при парсинге - покрывает строки 55-57"""
        parser = HHParser()
        
        raw_data = [{
            "id": "123",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123"
        }]
        
        with patch('src.vacancies.parsers.hh_parser.logger') as mock_logger:
            result = parser.parse_vacancies(raw_data)
            
            assert result == []
            mock_logger.warning.assert_called()

    @patch('src.utils.cache.FileCache')
    def test_parse_vacancy_single(self, mock_cache):
        """Тест parse_vacancy для одной вакансии - покрывает строки 71-137"""
        parser = HHParser()
        
        raw_data = {
            "id": "123",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "snippet": {"requirement": "Python", "responsibility": "Coding"},
            "employer": {"name": "Tech Company"},
            "area": {"name": "Москва"},
            "experience": {"name": "1-3 года"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"}
        }
        
        result = parser.parse_vacancy(raw_data)
        
        assert isinstance(result, dict)
        assert "vacancy_id" in result


class TestSuperJobParser:
    """100% покрытие SuperJobParser"""

    def test_sj_parser_init(self):
        """Тест инициализации SuperJobParser"""
        parser = SuperJobParser()
        assert isinstance(parser, SuperJobParser)

    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parse_vacancies_valid_data(self, mock_from_dict):
        """Тест parse_vacancies с валидными данными - покрывает строки 24-43"""
        parser = SuperJobParser()
        
        mock_vacancy = Mock()
        mock_from_dict.return_value = mock_vacancy
        
        raw_data = [{"id": 123, "profession": "Python Developer"}]
        
        with patch('src.vacancies.parsers.sj_parser.logger') as mock_logger:
            result = parser.parse_vacancies(raw_data)
            
            assert len(result) == 1
            assert result[0] == mock_vacancy
            mock_logger.info.assert_called()

    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parse_vacancies_adds_source(self, mock_from_dict):
        """Тест добавления источника - покрывает строки 29-30"""
        parser = SuperJobParser()
        mock_from_dict.return_value = Mock()
        
        raw_data = [{"id": 123, "profession": "Developer"}]
        
        parser.parse_vacancies(raw_data)
        
        called_args = mock_from_dict.call_args[0][0]
        assert called_args["source"] == "superjob.ru"

    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parse_vacancies_preserves_existing_source(self, mock_from_dict):
        """Тест сохранения существующего источника"""
        parser = SuperJobParser()
        mock_from_dict.return_value = Mock()
        
        raw_data = [{"id": 123, "profession": "Developer", "source": "custom.ru"}]
        
        parser.parse_vacancies(raw_data)
        
        called_args = mock_from_dict.call_args[0][0]
        assert called_args["source"] == "custom.ru"

    @patch('src.vacancies.models.Vacancy.from_dict', side_effect=ValueError("Validation error"))
    def test_parse_vacancies_handles_value_error(self, mock_from_dict):
        """Тест обработки ValueError - покрывает строки 35-37"""
        parser = SuperJobParser()
        
        raw_data = [{"id": 123, "profession": "Developer"}]
        
        with patch('src.vacancies.parsers.sj_parser.logger') as mock_logger:
            result = parser.parse_vacancies(raw_data)
            
            assert result == []
            mock_logger.warning.assert_called()

    @patch('src.vacancies.models.Vacancy.from_dict', side_effect=Exception("Unknown error"))
    def test_parse_vacancies_handles_general_exception(self, mock_from_dict):
        """Тест обработки общих исключений - покрывает строки 38-40"""
        parser = SuperJobParser()
        
        raw_data = [{"id": 123, "profession": "Developer"}]
        
        with patch('src.vacancies.parsers.sj_parser.logger') as mock_logger:
            result = parser.parse_vacancies(raw_data)
            
            assert result == []
            mock_logger.error.assert_called()

    def test_convert_to_unified_format_with_salary(self):
        """Тест convert_to_unified_format с зарплатой - покрывает строки 56-64"""
        # Создаем mock vacancy с зарплатой
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "sj123"
        mock_vacancy.title = "SJ Developer"
        mock_vacancy.url = "https://superjob.ru/vacancy/123"
        mock_vacancy.description = "Test description"
        mock_vacancy.requirements = "Test requirements"
        
        # Мокируем salary
        mock_salary = Mock()
        mock_salary.to_dict.return_value = {"from": 80000, "to": 120000, "period": "месяц"}
        mock_vacancy.salary = mock_salary
        
        result = SuperJobParser.convert_to_unified_format(mock_vacancy)
        
        assert result["id"] == "sj123"
        assert result["name"] == "SJ Developer"
        assert result["title"] == "SJ Developer"
        assert result["url"] == "https://superjob.ru/vacancy/123"
        assert result["alternate_url"] == "https://superjob.ru/vacancy/123"
        assert result["salary"]["period"] == "месяц"
        assert result["description"] == "Test description"
        assert result["requirements"] == "Test requirements"
        assert result["responsibilities"] == "Test description"

    def test_convert_to_unified_format_without_salary(self):
        """Тест convert_to_unified_format без зарплаты - покрывает строку 57"""
        mock_vacancy = Mock()
        mock_vacancy.vacancy_id = "sj456"
        mock_vacancy.title = "SJ Manager"
        mock_vacancy.url = "https://superjob.ru/vacancy/456"
        mock_vacancy.description = "Manager description"
        mock_vacancy.requirements = "Manager requirements"
        mock_vacancy.salary = None
        
        result = SuperJobParser.convert_to_unified_format(mock_vacancy)
        
        assert result["salary"] is None

    def test_parse_vacancy_method_inheritance(self):
        """Тест что parse_vacancy наследуется от BaseParser"""
        parser = SuperJobParser()
        
        # Проверяем что метод существует (наследуется от базового класса)
        assert hasattr(parser, 'parse_vacancy')
        assert callable(parser.parse_vacancy)


class TestParsersIntegration:
    """Интеграционные тесты для всех парсеров"""

    def test_all_parsers_implement_base_interface(self):
        """Тест что все парсеры реализуют BaseParser интерфейс"""
        # Проверяем HHParser
        with patch('src.vacancies.parsers.hh_parser.FileCache'):
            hh_parser = HHParser()
            assert isinstance(hh_parser, BaseParser)
            assert hasattr(hh_parser, 'parse_vacancy')
            assert hasattr(hh_parser, 'parse_vacancies')
        
        # Проверяем SuperJobParser
        sj_parser = SuperJobParser()
        assert isinstance(sj_parser, BaseParser)
        assert hasattr(sj_parser, 'parse_vacancy')
        assert hasattr(sj_parser, 'parse_vacancies')

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    @patch('src.vacancies.models.Vacancy.from_dict')
    def test_parsers_handle_similar_data_structures(self, mock_from_dict, mock_cache):
        """Тест что разные парсеры могут обрабатывать похожие структуры данных"""
        mock_from_dict.return_value = Mock()
        
        # Общие данные для тестирования
        common_data = [{"id": "test", "name": "Test Job", "alternate_url": "http://test.com"}]
        
        hh_parser = HHParser()
        sj_parser = SuperJobParser()
        
        # Оба парсера должны обработать данные без ошибок
        hh_result = hh_parser.parse_vacancies(common_data)
        sj_result = sj_parser.parse_vacancies(common_data)
        
        assert len(hh_result) == 1
        assert len(sj_result) == 1

    def test_parsers_error_handling_consistency(self):
        """Тест консистентности обработки ошибок во всех парсерах"""
        with patch('src.vacancies.parsers.hh_parser.FileCache'):
            hh_parser = HHParser()
        sj_parser = SuperJobParser()
        
        # Пустые данные должны возвращать пустой список
        assert hh_parser.parse_vacancies([]) == []
        assert sj_parser.parse_vacancies([]) == []
        
        # None данные должны обрабатываться корректно
        try:
            hh_result = hh_parser.parse_vacancies(None)
        except (TypeError, AttributeError):
            pass  # Ожидаемое поведение
        
        try:
            sj_result = sj_parser.parse_vacancies(None)  
        except (TypeError, AttributeError):
            pass  # Ожидаемое поведение

    @patch('src.vacancies.parsers.hh_parser.FileCache')
    def test_hh_parser_snippet_processing_edge_cases(self, mock_cache):
        """Тест граничных случаев обработки snippet в HH парсере"""
        parser = HHParser()
        
        # Только requirement
        with patch('src.vacancies.models.Vacancy.from_dict') as mock_from_dict:
            mock_from_dict.return_value = Mock()
            
            raw_data = [{
                "id": "123",
                "name": "Test Job",
                "alternate_url": "http://test.com",
                "snippet": {"requirement": "Python"}
            }]
            
            parser.parse_vacancies(raw_data)
            
            called_args = mock_from_dict.call_args[0][0]
            assert "Требования: Python" in called_args["description"]

        # Только responsibility
        with patch('src.vacancies.models.Vacancy.from_dict') as mock_from_dict:
            mock_from_dict.return_value = Mock()
            
            raw_data = [{
                "id": "124",
                "name": "Test Job 2",
                "alternate_url": "http://test.com",
                "snippet": {"responsibility": "Coding"}
            }]
            
            parser.parse_vacancies(raw_data)
            
            called_args = mock_from_dict.call_args[0][0] 
            assert "Обязанности: Coding" in called_args["description"]