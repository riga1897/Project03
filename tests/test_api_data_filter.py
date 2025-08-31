"""
Тесты для модуля фильтрации данных API
"""

import pytest

from src.utils.api_data_filter import APIDataFilter


class TestAPIDataFilter:
    """Тесты для класса APIDataFilter"""

    @pytest.fixture
    def sample_hh_data(self):
        """Фикстура с примером данных HH.ru"""
        return {
            "items": [
                {
                    "id": "12345",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/12345",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Python, Django", "responsibility": "Разработка веб-приложений"},
                    "employer": {"name": "Test Company"},
                    "area": {"name": "Москва"},
                    "experience": {"name": "От 1 года до 3 лет"},
                    "employment": {"name": "Полная занятость"},
                    "schedule": {"name": "Полный день"},
                    "published_at": "2024-01-15T10:00:00+0300",
                },
                {
                    "id": "67890",
                    "name": "Java Developer",
                    "alternate_url": "https://hh.ru/vacancy/67890",
                    "salary": None,
                    "snippet": {"requirement": "Java, Spring", "responsibility": "Backend разработка"},
                    "employer": {"name": "Another Company"},
                    "area": {"name": "СПб"},
                    "experience": {"name": "От 3 до 6 лет"},
                    "employment": {"name": "Полная занятость"},
                    "schedule": {"name": "Полный день"},
                    "published_at": "2024-01-16T10:00:00+0300",
                },
            ]
        }

    @pytest.fixture
    def sample_sj_data(self):
        """Фикстура с примером данных SuperJob"""
        return {
            "objects": [
                {
                    "id": 111,
                    "profession": "Python Developer",
                    "link": "https://superjob.ru/vacancy/111",
                    "payment_from": 120000,
                    "payment_to": 180000,
                    "currency": "rub",
                    "candidat": "Python, Flask",
                    "work": "Разработка API",
                    "firm_name": "SJ Company",
                    "town": {"title": "Москва"},
                    "experience": {"title": "От 1 года до 3 лет"},
                    "type_of_work": {"title": "Полная занятость"},
                    "place_of_work": {"title": "Полный день"},
                    "date_pub_timestamp": 1705312800,
                }
            ]
        }

    def test_filter_hh_data_by_salary_range(self):
        """Тест фильтрации данных HH по диапазону зарплаты"""
        filter_obj = APIDataFilter()
        test_data = [
            {
                "id": "1",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            },
            {
                "id": "2",
                "name": "Java Developer",
                "salary": {"from": 80000, "to": 120000, "currency": "RUR"},
            },
        ]

        result = filter_obj.filter_by_salary_range(test_data, min_salary=90000, source="hh")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_sj_data_by_salary_range(self):
        """Тест фильтрации данных SuperJob по диапазону зарплат"""
        filter_obj = APIDataFilter()
        test_data = [
            {
                "id": "1",
                "profession": "Python Developer",
                "payment_from": 100000,
                "payment_to": 150000,
                "currency": "rub",
            },
            {
                "id": "2",
                "profession": "Java Developer",
                "payment_from": 80000,
                "payment_to": 120000,
                "currency": "rub",
            },
        ]

        result = filter_obj.filter_by_salary_range(test_data, min_salary=90000, source="sj")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_by_keywords(self):
        """Тест фильтрации по ключевым словам"""
        filter_obj = APIDataFilter()
        test_data = [
            {
                "id": "1",
                "name": "Python Developer",
                "snippet": {"requirement": "Python Django", "responsibility": "Backend development"},
            },
            {
                "id": "2",
                "name": "Java Developer",
                "snippet": {"requirement": "Java Spring", "responsibility": "Enterprise development"},
            },
        ]

        result = filter_obj.filter_by_keywords(test_data, ["Python"])
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_by_location(self):
        """Тест фильтрации по локации"""
        filter_obj = APIDataFilter()
        test_data = [
            {"id": "1", "area": {"name": "Москва"}},
            {"id": "2", "area": {"name": "Санкт-Петербург"}},
        ]

        result = filter_obj.filter_by_location(test_data, ["Москва"])
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_by_experience(self):
        """Тест фильтрации по опыту"""
        filter_obj = APIDataFilter()
        test_data = [
            {"id": "1", "experience": {"name": "От 1 года до 3 лет"}},
            {"id": "2", "experience": {"name": "От 3 до 6 лет"}},
        ]

        result = filter_obj.filter_by_experience(test_data, ["От 1 года до 3 лет"])
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_by_employment_type(self):
        """Тест фильтрации по типу занятости"""
        filter_obj = APIDataFilter()
        test_data = [
            {"id": "1", "employment": {"name": "Полная занятость"}},
            {"id": "2", "employment": {"name": "Частичная занятость"}},
        ]

        result = filter_obj.filter_by_employment_type(test_data, ["Полная занятость"])
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_filter_by_company(self):
        """Тест фильтрации по компании"""
        filter_obj = APIDataFilter()
        test_data = [
            {"id": "1", "employer": {"name": "Яндекс"}},
            {"id": "2", "employer": {"name": "Сбер"}},
        ]

        result = filter_obj.filter_by_company(test_data, ["Яндекс"])
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_complex_filter_chain(self):
        """Тест цепочки фильтров"""
        filter_obj = APIDataFilter()
        test_data = [
            {
                "id": "1",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "employer": {"name": "Яндекс"},
                "area": {"name": "Москва"},
            },
            {
                "id": "2",
                "name": "Java Developer",
                "salary": {"from": 80000, "to": 120000, "currency": "RUR"},
                "employer": {"name": "Сбер"},
                "area": {"name": "Санкт-Петербург"},
            },
        ]

        # Применяем несколько фильтров
        result = filter_obj.filter_by_salary_range(test_data, min_salary=90000, source="hh")
        result = filter_obj.filter_by_company(result, ["Яндекс"])
        result = filter_obj.filter_by_location(result, ["Москва"])

        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_empty_filter_results(self):
        """Тест пустых результатов фильтрации"""
        filter_obj = APIDataFilter()
        test_data = [
            {"id": "1", "employer": {"name": "Яндекс"}},
            {"id": "2", "employer": {"name": "Сбер"}},
        ]

        result = filter_obj.filter_by_company(test_data, ["Тинькофф"])
        assert len(result) == 0

    def test_filter_with_empty_data(self):
        """Тест фильтрации пустых данных"""
        filter_obj = APIDataFilter()
        result = filter_obj.filter_by_keywords([], ["Python"])
        assert len(result) == 0

    def test_filter_invalid_data_structure(self):
        """Тест фильтрации некорректной структуры данных"""
        filter_obj = APIDataFilter()
        test_data = [
            {"id": "1"},  # Отсутствуют ключевые поля
            {"name": "Test"},  # Отсутствует id
        ]

        # Фильтр должен обработать некорректные данные без ошибок
        result = filter_obj.filter_by_keywords(test_data, ["Python"])
        assert isinstance(result, list)