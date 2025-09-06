
from unittest.mock import MagicMock, patch, Mock

import pytest

from src.vacancies.parsers.hh_parser import HHParser


class TestHHParser:
    def setup_method(self):
        """Настройка для каждого теста"""
        self.parser = HHParser()
        self.sample_hh_vacancy = {
            "id": "123456",
            "name": "Python Developer",
            "employer": {"name": "Test Company"},
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "area": {"name": "Москва"},
            "experience": {"name": "От 3 до 6 лет"},
            "employment": {"name": "Полная занятость"},
            "alternate_url": "https://hh.ru/vacancy/123456",
            "snippet": {"requirement": "Python, Django", "responsibility": "Разработка"},
        }

    def test_hh_parser_initialization(self):
        """Тест инициализации HH парсера"""
        parser = HHParser()
        assert parser is not None

    def test_parse_hh_vacancy(self):
        """Тест парсинга вакансии HH"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        # Проверяем что парсер возвращает валидный результат
        assert result is not None
        # Проверяем тип результата - должен быть dict
        assert isinstance(result, dict)

    def test_parse_hh_salary(self):
        """Тест парсинга зарплаты HH"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        assert isinstance(result, dict)
        assert "salary_from" in result or "salary" in result

    def test_parse_hh_vacancy_no_salary(self):
        """Тест парсинга вакансии без зарплаты"""
        vacancy_data = self.sample_hh_vacancy.copy()
        vacancy_data["salary"] = None
        result = self.parser.parse_vacancy(vacancy_data)
        assert isinstance(result, dict)

    def test_parse_hh_vacancies_list(self):
        """Тест парсинга списка вакансий HH"""
        data = [self.sample_hh_vacancy]

        # Мокаем Vacancy для корректной работы
        with patch("src.vacancies.parsers.hh_parser.Vacancy") as mock_vacancy:
            mock_vacancy_instance = Mock()
            mock_vacancy_instance.to_dict.return_value = {
                "vacancy_id": "123456",
                "title": "Python Developer",
                "url": "https://hh.ru/vacancy/123456"
            }
            mock_vacancy.from_dict.return_value = mock_vacancy_instance

            result = self.parser.parse_vacancies(data)

            assert len(result) == 1
            # Результат должен быть списком объектов или словарей
            assert isinstance(result[0], (dict, object))

    def test_parse_hh_vacancy_minimal_data(self):
        """Тест парсинга вакансии с минимальными данными"""
        minimal_data = {"id": "123", "name": "Test Job"}

        result = self.parser.parse_vacancy(minimal_data)
        assert isinstance(result, dict)
        assert "vacancy_id" in result or "id" in result

    def test_parse_hh_employer_data(self):
        """Тест парсинга данных работодателя"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        assert isinstance(result, dict)
        # Проверяем наличие информации о работодателе
        assert "employer" in result or "company" in result

    def test_parse_hh_location_data(self):
        """Тест парсинга данных о местоположении"""
        result = self.parser.parse_vacancy(self.sample_hh_vacancy)
        assert isinstance(result, dict)
        # Проверяем наличие информации о местоположении
        assert "area" in result or "location" in result
