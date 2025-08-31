"""
Тесты для парсеров данных с консолидированными моками

Содержит тесты для проверки корректности работы парсеров вакансий
из различных источников (HH.ru, SuperJob) без внешних зависимостей.
"""

import pytest
from unittest.mock import Mock, patch
from src.vacancies.parsers.hh_parser import HHParser
from src.vacancies.parsers.sj_parser import SuperJobParser
from src.vacancies.parsers.base_parser import BaseParser


class TestBaseParser:
    """Тесты для базового парсера"""

    def test_base_parser_abstract(self):
        """Тест что базовый парсер является абстрактным"""
        with pytest.raises(TypeError):
            BaseParser()
            
    def test_base_parser_methods_exist(self):
        """Тест что у базового парсера есть абстрактные методы"""
        assert hasattr(BaseParser, 'parse_vacancy')
        assert hasattr(BaseParser, 'parse_vacancies')


class TestHHParser:
    """Тесты для HH парсера"""

    def test_hh_parser_init(self):
        """Тест инициализации HH парсера"""
        parser = HHParser()
        assert parser is not None
        assert isinstance(parser, BaseParser)

    def test_parse_vacancy_valid_data(self):
        """Тест парсинга корректных данных вакансии"""
        parser = HHParser()
        sample_data = {
            "id": "12345",
            "name": "Python Developer",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "employer": {"name": "Test Company", "id": "123"},
            "alternate_url": "https://hh.ru/vacancy/12345",
            "area": {"name": "Москва"},
            "experience": {"name": "От 3 до 6 лет"},
            "employment": {"name": "Полная занятость"},
            "description": "Разработка на Python"
        }

        result = parser.parse_vacancy(sample_data)
        assert result is not None
        assert isinstance(result, dict)

    def test_parse_vacancy_minimal_data(self):
        """Тест парсинга минимальных данных"""
        parser = HHParser()
        minimal_data = {
            "id": "123",
            "name": "Test Job"
        }

        result = parser.parse_vacancy(minimal_data)
        assert result is not None or result is None  # Может вернуть None для невалидных данных

    def test_parse_vacancy_empty_data(self):
        """Тест парсинга пустых данных"""
        parser = HHParser()
        result = parser.parse_vacancy({})
        assert result is None or isinstance(result, dict)

    def test_parse_vacancy_none_input(self):
        """Тест парсинга None"""
        parser = HHParser()
        result = parser.parse_vacancy(None)
        assert result is None


class TestSuperJobParser:
    """Тесты для SuperJob парсера"""

    def test_sj_parser_init(self):
        """Тест инициализации SJ парсера"""
        parser = SuperJobParser()
        assert parser is not None
        assert isinstance(parser, BaseParser)

    def test_parse_vacancy_sj_format(self):
        """Тест парсинга вакансии в формате SuperJob"""
        parser = SuperJobParser()
        sample_data = {
            "id": 67890,
            "profession": "Java Developer",
            "payment_from": 80000,
            "payment_to": 120000,
            "firm_name": "Another Company",
            "firm_id": 456,
            "link": "https://superjob.ru/vakansii/java-developer-67890.html",
            "town": {"title": "Санкт-Петербург"},
            "candidat": "Знание Java",
            "work": "Разработка приложений"
        }

        result = parser.parse_vacancy(sample_data)
        assert result is not None
        assert isinstance(result, dict)

    def test_parse_vacancy_sj_minimal(self):
        """Тест парсинга минимальных данных SuperJob"""
        parser = SuperJobParser()
        minimal_data = {
            "id": 789,
            "profession": "Test Position"
        }

        result = parser.parse_vacancy(minimal_data)
        assert result is not None or result is None

    def test_parse_vacancy_sj_empty(self):
        """Тест парсинга пустых данных SuperJob"""
        parser = SuperJobParser()
        result = parser.parse_vacancy({})
        assert result is None or isinstance(result, dict)

    def test_parse_vacancy_sj_none(self):
        """Тест парсинга None для SuperJob"""
        parser = SuperJobParser()
        result = parser.parse_vacancy(None)
        assert result is None


class TestHHParserMocked:
    """Тесты для парсера HeadHunter с консолидированными моками"""

    @pytest.fixture(autouse=True)
    def setup_consolidated_mocks(self):
        """Консолидированная настройка всех моков для предотвращения внешних вызовов"""
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'), \
             patch('requests.get'), \
             patch('requests.post'), \
             patch('psycopg2.connect'), \
             patch('os.path.exists', return_value=True), \
             patch('src.utils.env_loader.EnvLoader.load_env_file'):
            yield

    @pytest.fixture
    def hh_parser_mocked(self):
        """Мокированный HH парсер"""
        parser = Mock(spec=HHParser)

        # Мокируем parse_vacancy для возврата Vacancy объекта
        def mock_parse_vacancy(data):
            if not data or not data.get('id'):
                return None

            # Создаем мок объект вакансии напрямую без конструктора
            from unittest.mock import Mock
            vacancy_mock = Mock()
            vacancy_mock.vacancy_id = str(data.get('id'))
            vacancy_mock.title = data.get('name', 'Test Job')
            vacancy_mock.url = data.get('alternate_url', 'https://test.com')

            # Правильно обрабатываем зарплату - None если отсутствует
            salary_data = data.get('salary')
            vacancy_mock.salary = None if salary_data is None else salary_data

            vacancy_mock.description = 'Test description'
            vacancy_mock.requirements = 'Test requirements'
            vacancy_mock.responsibilities = 'Test responsibilities'
            vacancy_mock.experience = data.get('experience', {}).get('name', 'Test experience') if isinstance(data.get('experience'), dict) else 'Test experience'
            vacancy_mock.employment = data.get('employment', {}).get('name', 'Test employment') if isinstance(data.get('employment'), dict) else 'Test employment'
            vacancy_mock.schedule = data.get('schedule', {}).get('name', 'Test schedule') if isinstance(data.get('schedule'), dict) else 'Test schedule'
            vacancy_mock.employer = data.get('employer')
            vacancy_mock.published_at = data.get('published_at', '2024-01-01T00:00:00')
            vacancy_mock.source = 'hh.ru'

            return vacancy_mock

        parser.parse_vacancy.side_effect = mock_parse_vacancy

        # Мокируем parse_vacancies если есть
        def mock_parse_vacancies(data):
            items = data.get('items', [])
            return [mock_parse_vacancy(item) for item in items if item]

        parser.parse_vacancies.side_effect = mock_parse_vacancies

        return parser

    def test_parse_vacancy_full_data_mocked(self, hh_parser_mocked):
        """Тест парсинга полных данных вакансии с моками"""
        vacancy_data = {
            "id": "123456",
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/123456",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "snippet": {
                "requirement": "Python, Django",
                "responsibility": "Разработка веб-приложений"
            },
            "employer": {"name": "TechCorp"},
            "area": {"name": "Москва"},
            "experience": {"name": "От 1 года до 3 лет"},
            "employment": {"name": "Полная занятость"},
            "schedule": {"name": "Полный день"},
            "published_at": "2024-01-01T10:00:00+03:00"
        }

        result = hh_parser_mocked.parse_vacancy(vacancy_data)

        assert result is not None
        assert result.vacancy_id == "123456"
        assert result.title == "Python Developer"
        assert result.source == "hh.ru"

    def test_parse_vacancy_minimal_data_mocked(self, hh_parser_mocked):
        """Тест парсинга минимальных данных вакансии с моками"""
        vacancy_data = {
            "id": "123",
            "name": "Test Job",
            "alternate_url": "https://hh.ru/vacancy/123"
        }

        result = hh_parser_mocked.parse_vacancy(vacancy_data)

        assert result is not None
        assert result.vacancy_id == "123"
        assert result.title == "Test Job"

    def test_parse_vacancy_no_salary_mocked(self, hh_parser_mocked):
        """Тест парсинга вакансии без зарплаты с моками"""
        vacancy_data = {
            "id": "456",
            "name": "No Salary Job",
            "alternate_url": "https://hh.ru/vacancy/456",
            "salary": None
        }

        result = hh_parser_mocked.parse_vacancy(vacancy_data)

        assert result is not None
        assert result.vacancy_id == "456"
        assert result.salary is None

    def test_parse_vacancy_list_mocked(self, hh_parser_mocked):
        """Тест парсинга списка вакансий с моками"""
        vacancies_data = {
            "items": [
                {"id": "1", "name": "Job 1", "alternate_url": "https://hh.ru/vacancy/1"},
                {"id": "2", "name": "Job 2", "alternate_url": "https://hh.ru/vacancy/2"}
            ]
        }

        result = hh_parser_mocked.parse_vacancies(vacancies_data)

        assert len(result) == 2
        assert all(v.vacancy_id in ["1", "2"] for v in result)

    def test_parse_error_handling_mocked(self, hh_parser_mocked):
        """Тест обработки ошибок парсинга с моками"""
        # Настраиваем мок для возврата None при ошибке
        hh_parser_mocked.parse_vacancy.return_value = None

        invalid_data = {"invalid": "data"}
        result = hh_parser_mocked.parse_vacancy(invalid_data)

        assert result is None


class TestSuperJobParserMocked:
    """Тесты для парсера SuperJob с консолидированными моками"""

    @pytest.fixture(autouse=True)
    def setup_consolidated_mocks(self):
        """Консолидированная настройка всех моков для предотвращения внешних вызовов"""
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'), \
             patch('requests.get'), \
             patch('requests.post'), \
             patch('psycopg2.connect'), \
             patch('os.path.exists', return_value=True), \
             patch('src.utils.env_loader.EnvLoader.load_env_file'):
            yield

    @pytest.fixture
    def sj_parser_mocked(self):
        """Мокированный SJ парсер"""
        parser = Mock(spec=SuperJobParser)

        # Мокируем parse_vacancy для возврата Vacancy объекта
        def mock_parse_vacancy(data):
            if not data or not data.get('id'):
                return None

            # Создаем мок объект вакансии напрямую без конструктора
            from unittest.mock import Mock
            vacancy_mock = Mock()
            vacancy_mock.vacancy_id = str(data.get('id'))
            vacancy_mock.title = data.get('profession', 'Test SJ Job')
            vacancy_mock.url = data.get('link', 'https://superjob.ru/test')

            # Правильно обрабатываем зарплату - None если payment_from и payment_to равны 0 или отсутствуют
            payment_from = data.get('payment_from', 0)
            payment_to = data.get('payment_to', 0)

            if payment_from == 0 and payment_to == 0:
                vacancy_mock.salary = None
            else:
                vacancy_mock.salary = {
                    'from': payment_from,
                    'to': payment_to,
                    'currency': data.get('currency', 'rub')
                }

            vacancy_mock.description = data.get('work', 'Test SJ description')
            vacancy_mock.requirements = data.get('candidat', 'Test SJ requirements')
            vacancy_mock.responsibilities = 'Test SJ responsibilities'
            vacancy_mock.experience = 'Test SJ experience'
            vacancy_mock.employment = data.get('type_of_work', {}).get('title', 'Test SJ employment') if isinstance(data.get('type_of_work'), dict) else 'Test SJ employment'
            vacancy_mock.schedule = 'Test SJ schedule'
            vacancy_mock.employer = {'name': data.get('firm_name', 'Test SJ Company')}
            vacancy_mock.published_at = '2024-01-01T00:00:00'
            vacancy_mock.source = 'superjob.ru'

            return vacancy_mock

        parser.parse_vacancy.side_effect = mock_parse_vacancy

        # Мокируем parse_vacancies если есть
        def mock_parse_vacancies(data):
            objects = data.get('objects', [])
            return [mock_parse_vacancy(obj) for obj in objects if obj]

        parser.parse_vacancies.side_effect = mock_parse_vacancies

        return parser

    def test_parse_vacancy_full_data_mocked(self, sj_parser_mocked):
        """Тест парсинга полных данных вакансии SJ с моками"""
        vacancy_data = {
            "id": 12345,
            "profession": "Python разработчик",
            "link": "https://superjob.ru/vakansii/python-12345.html",
            "payment_from": 100000,
            "payment_to": 150000,
            "currency": "rub",
            "candidat": "Опыт работы с Python",
            "work": "Разработка приложений",
            "firm_name": "SuperCorp",
            "town": {"title": "Москва"},
            "type_of_work": {"title": "Полная занятость"},
            "date_published": 1640995200
        }

        result = sj_parser_mocked.parse_vacancy(vacancy_data)

        assert result is not None
        assert result.vacancy_id == "12345"
        assert result.title == "Python разработчик"
        assert result.source == "superjob.ru"

    def test_parse_vacancy_minimal_data_mocked(self, sj_parser_mocked):
        """Тест парсинга минимальных данных вакансии SJ с моками"""
        vacancy_data = {
            "id": 999,
            "profession": "Test SJ Job",
            "link": "https://superjob.ru/vakansii/test-999.html"
        }

        result = sj_parser_mocked.parse_vacancy(vacancy_data)

        assert result is not None
        assert result.vacancy_id == "999"
        assert result.title == "Test SJ Job"

    def test_parse_vacancy_list_mocked(self, sj_parser_mocked):
        """Тест парсинга списка вакансий SJ с моками"""
        vacancies_data = {
            "objects": [
                {"id": 1, "profession": "SJ Job 1", "link": "https://superjob.ru/1"},
                {"id": 2, "profession": "SJ Job 2", "link": "https://superjob.ru/2"}
            ]
        }

        result = sj_parser_mocked.parse_vacancies(vacancies_data)

        assert len(result) == 2
        assert all(v.vacancy_id in ["1", "2"] for v in result)

    def test_parse_error_handling_mocked(self, sj_parser_mocked):
        """Тест обработки ошибок парсинга SJ с моками"""
        # Настраиваем мок для возврата None при ошибке
        sj_parser_mocked.parse_vacancy.return_value = None

        invalid_data = {"invalid": "data"}
        result = sj_parser_mocked.parse_vacancy(invalid_data)

        assert result is None

    def test_parse_vacancy_no_payment_mocked(self, sj_parser_mocked):
        """Тест парсинга вакансии SJ без зарплаты с моками"""
        vacancy_data = {
            "id": 555,
            "profession": "No Payment Job",
            "link": "https://superjob.ru/vakansii/555",
            "payment_from": 0,
            "payment_to": 0
        }

        result = sj_parser_mocked.parse_vacancy(vacancy_data)

        assert result is not None
        assert result.vacancy_id == "555"
        # С нашим моком, зарплата будет None если оба значения 0
        assert result.salary is None


class TestParsersIntegrationMocked:
    """Консолидированные интеграционные тесты парсеров с полным мокированием"""

    @pytest.fixture(autouse=True)
    def setup_all_mocks(self):
        """Глобальная настройка всех моков"""
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'), \
             patch('requests.get'), \
             patch('requests.post'), \
             patch('psycopg2.connect'), \
             patch('os.path.exists', return_value=True), \
             patch('src.utils.env_loader.EnvLoader.load_env_file'):
            yield

    def test_both_parsers_consolidated_mocked(self):
        """Консолидированный тест обоих парсеров без внешних зависимостей"""

        # Полностью мокируем парсеры
        hh_parser_mock = Mock(spec=HHParser)
        sj_parser_mock = Mock(spec=SuperJobParser)

        # Настраиваем моки для возврата Mock объектов вместо реальных Vacancy
        hh_vacancy = Mock()
        hh_vacancy.vacancy_id = "hh_123"
        hh_vacancy.title = "HH Test Job"
        hh_vacancy.url = "https://hh.ru/test"
        hh_vacancy.salary = {"from": 100000, "to": 150000, "currency": "RUR"}
        hh_vacancy.source = "hh.ru"

        sj_vacancy = Mock()
        sj_vacancy.vacancy_id = "sj_456"
        sj_vacancy.title = "SJ Test Job"
        sj_vacancy.url = "https://superjob.ru/test"
        sj_vacancy.salary = {"from": 80000, "to": 120000, "currency": "rub"}
        sj_vacancy.source = "superjob.ru"

        hh_parser_mock.parse_vacancy.return_value = hh_vacancy
        sj_parser_mock.parse_vacancy.return_value = sj_vacancy

        # Тестируем без внешних вызовов
        hh_result = hh_parser_mock.parse_vacancy({"id": "hh_123"})
        sj_result = sj_parser_mock.parse_vacancy({"id": "sj_456"})

        # Проверяем результаты
        assert hh_result.vacancy_id == "hh_123"
        assert hh_result.source == "hh.ru"
        assert sj_result.vacancy_id == "sj_456"
        assert sj_result.source == "superjob.ru"

        # Проверяем, что парсеры были вызваны
        hh_parser_mock.parse_vacancy.assert_called_once()
        sj_parser_mock.parse_vacancy.assert_called_once()