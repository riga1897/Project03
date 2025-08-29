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

    def test_filter_hh_data_by_salary_range(self, sample_hh_data):
        """Тест фильтрации данных HH по диапазону зарплаты"""
        filter_obj = APIDataFilter()

        # Фильтруем вакансии с зарплатой от 90000
        filtered = filter_obj.filter_by_salary_range(sample_hh_data["items"], min_salary=90000)

        assert len(filtered) == 1
        assert filtered[0]["id"] == "12345"

    def test_filter_sj_data_by_salary_range(self, sample_sj_data):
        """Тест фильтрации данных SJ по диапазону зарплаты"""
        filter_obj = APIDataFilter()

        # Фильтруем вакансии с зарплатой до 200000
        filtered = filter_obj.filter_by_salary_range(sample_sj_data["objects"], max_salary=200000, source="sj")

        assert len(filtered) == 1
        assert filtered[0]["id"] == 111

    def test_filter_by_keywords(self, sample_hh_data):
        """Тест фильтрации по ключевым словам"""
        filter_obj = APIDataFilter()

        # Поиск по ключевому слову "Python"
        filtered = filter_obj.filter_by_keywords(sample_hh_data["items"], keywords=["Python"])

        assert len(filtered) == 1
        assert filtered[0]["name"] == "Python Developer"

    def test_filter_by_location(self, sample_hh_data):
        """Тест фильтрации по местоположению"""
        filter_obj = APIDataFilter()

        # Фильтрация по городу Москва
        filtered = filter_obj.filter_by_location(sample_hh_data["items"], locations=["Москва"])

        assert len(filtered) == 1
        assert filtered[0]["area"]["name"] == "Москва"

    def test_filter_by_experience(self, sample_hh_data):
        """Тест фильтрации по опыту работы"""
        filter_obj = APIDataFilter()

        # Фильтрация по опыту "От 1 года до 3 лет"
        filtered = filter_obj.filter_by_experience(sample_hh_data["items"], experience_levels=["От 1 года до 3 лет"])

        assert len(filtered) == 1
        assert filtered[0]["experience"]["name"] == "От 1 года до 3 лет"

    def test_filter_by_employment_type(self, sample_hh_data):
        """Тест фильтрации по типу занятости"""
        filter_obj = APIDataFilter()

        # Фильтрация по полной занятости
        filtered = filter_obj.filter_by_employment_type(sample_hh_data["items"], employment_types=["Полная занятость"])

        assert len(filtered) == 2  # Обе вакансии с полной занятостью

    def test_filter_by_company(self, sample_hh_data):
        """Тест фильтрации по компании"""
        filter_obj = APIDataFilter()

        # Фильтрация по конкретной компании
        filtered = filter_obj.filter_by_company(sample_hh_data["items"], companies=["Test Company"])

        assert len(filtered) == 1
        assert filtered[0]["employer"]["name"] == "Test Company"

    def test_complex_filter_chain(self, sample_hh_data):
        """Тест цепочки фильтров"""
        filter_obj = APIDataFilter()

        # Применяем несколько фильтров подряд
        vacancies = sample_hh_data["items"]

        # Фильтр по ключевому слову
        vacancies = filter_obj.filter_by_keywords(vacancies, ["Developer"])

        # Фильтр по городу
        vacancies = filter_obj.filter_by_location(vacancies, ["Москва"])

        # Фильтр по занятости
        vacancies = filter_obj.filter_by_employment_type(vacancies, ["Полная занятость"])

        assert len(vacancies) == 1
        assert vacancies[0]["name"] == "Python Developer"

    def test_empty_filter_results(self, sample_hh_data):
        """Тест фильтра, который не возвращает результатов"""
        filter_obj = APIDataFilter()

        # Поиск несуществующего ключевого слова
        filtered = filter_obj.filter_by_keywords(sample_hh_data["items"], keywords=["NonExistentKeyword"])

        assert len(filtered) == 0

    def test_filter_with_empty_data(self):
        """Тест фильтрации пустых данных"""
        filter_obj = APIDataFilter()

        # Фильтрация пустого списка
        filtered = filter_obj.filter_by_keywords([], keywords=["Python"])

        assert len(filtered) == 0

    def test_filter_invalid_data_structure(self):
        """Тест фильтрации некорректной структуры данных"""
        filter_obj = APIDataFilter()

        # Некорректная структура данных
        invalid_data = [{"invalid": "structure"}]

        # Фильтр должен обработать некорректные данные без ошибок
        filtered = filter_obj.filter_by_keywords(invalid_data, keywords=["Python"])

        assert len(filtered) == 0
