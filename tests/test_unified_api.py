#!/usr/bin/env python3
"""
Тесты для модуля unified_api.py
"""

import logging
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.api_modules.unified_api import UnifiedAPI
from src.vacancies.parsers.sj_parser import SuperJobParser


class TestUnifiedAPI:
    """Тесты для класса UnifiedAPI"""

    @pytest.fixture
    def unified_api(self):
        """Создание экземпляра UnifiedAPI для тестов"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh_api:
            with patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj_api:
                with patch('src.api_modules.unified_api.SuperJobParser') as mock_parser:
                    api = UnifiedAPI()
                    api.hh_api = mock_hh_api
                    api.sj_api = mock_sj_api
                    api.parser = mock_parser
                    return api

    def test_unified_api_initialization(self):
        """Тест инициализации UnifiedAPI"""
        with patch('src.api_modules.unified_api.HeadHunterAPI') as mock_hh_api:
            with patch('src.api_modules.unified_api.SuperJobAPI') as mock_sj_api:
                with patch('src.api_modules.unified_api.SuperJobParser') as mock_parser:
                    api = UnifiedAPI()

                    assert api.hh_api is not None
                    assert api.sj_api is not None
                    assert api.parser is not None
                    assert "hh" in api.apis
                    assert "sj" in api.apis
                    assert api.apis["hh"] == api.hh_api
                    assert api.apis["sj"] == api.sj_api

    def test_get_available_sources(self, unified_api):
        """Тест получения доступных источников"""
        sources = unified_api.get_available_sources()

        assert "hh" in sources
        assert "sj" in sources
        assert len(sources) == 2

    def test_validate_sources_valid(self, unified_api):
        """Тест валидации валидных источников"""
        valid_sources = ["hh", "sj"]
        result = unified_api.validate_sources(valid_sources)

        assert result == valid_sources

    def test_validate_sources_invalid(self, unified_api):
        """Тест валидации невалидных источников"""
        invalid_sources = ["hh", "invalid", "sj"]
        result = unified_api.validate_sources(invalid_sources)

        # Невалидные источники должны быть отфильтрованы
        assert "invalid" not in result
        assert "hh" in result
        assert "sj" in result

    def test_validate_sources_empty(self):
        """Тест валидации пустого списка источников"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            api_instance = UnifiedAPI()
            result = api_instance.validate_sources([])
            # UnifiedAPI может возвращать доступные источники при пустом списке
            assert isinstance(result, list)

    def test_validate_sources_none(self):
        """Тест валидации None как списка источников"""
        with patch('src.api_modules.unified_api.HeadHunterAPI'), \
             patch('src.api_modules.unified_api.SuperJobAPI'), \
             patch('src.api_modules.unified_api.SuperJobParser'):
            api_instance = UnifiedAPI()
            try:
                result = api_instance.validate_sources(None)
                assert isinstance(result, list)
            except TypeError:
                # Ожидаемая ошибка при передаче None
                assert True

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_default_sources(self, mock_logger, unified_api):
        """Тест получения вакансий с источниками по умолчанию"""
        # Мокаем get_available_sources
        unified_api.get_available_sources = Mock(return_value=["hh", "sj"])

        # Мокаем API ответы
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}, {"id": "2"}]):
            result = unified_api.get_vacancies_from_sources("Python")

            assert len(result) == 2
            mock_logger.info.assert_called()

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_specific_sources(self, mock_logger, unified_api):
        """Тест получения вакансий с указанными источниками"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh"])

        # Мокаем API ответ
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}]):
            result = unified_api.get_vacancies_from_sources("Python", sources=["hh"])

            assert len(result) == 1
            unified_api.validate_sources.assert_called_once_with(["hh"])

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_hh_only(self, mock_logger, unified_api):
        """Тест получения вакансий только с HH"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh"])

        # Мокаем API ответ
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}]):
            result = unified_api.get_vacancies_from_sources("Python", sources=["hh"])

            assert len(result) == 1
            unified_api.hh_api.get_vacancies.assert_called_once()
            unified_api.sj_api.get_vacancies.assert_not_called()

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_sj_only(self, mock_logger, unified_api):
        """Тест получения вакансий только с SuperJob"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["sj"])

        # Мокаем API ответ
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "2"}]):
            result = unified_api.get_vacancies_from_sources("Python", sources=["sj"])

            assert len(result) == 1
            unified_api.hh_api.get_vacancies.assert_not_called()
            unified_api.sj_api.get_vacancies.assert_called_once()

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_hh_error(self, mock_logger, unified_api):
        """Тест обработки ошибки HH API"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh", "sj"])

        # Мокаем ошибку HH API
        unified_api.hh_api.get_vacancies.side_effect = Exception("HH API error")
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "2"}]):
            result = unified_api.get_vacancies_from_sources("Python")

            assert len(result) == 1
            mock_logger.error.assert_called_with("Ошибка получения вакансий с HH.ru: HH API error")

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_sj_error(self, mock_logger, unified_api):
        """Тест обработки ошибки SuperJob API"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh", "sj"])

        # Мокаем успешный HH API и ошибку SuperJob API
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]
        unified_api.sj_api.get_vacancies.side_effect = Exception("SuperJob API error")

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}]):
            result = unified_api.get_vacancies_from_sources("Python")

            assert len(result) == 1
            mock_logger.error.assert_called_with("Ошибка получения вакансий с SuperJob: SuperJob API error")

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_no_results(self, mock_logger, unified_api):
        """Тест получения вакансий без результатов"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh", "sj"])

        # Мокаем пустые ответы API
        unified_api.hh_api.get_vacancies.return_value = []
        unified_api.sj_api.get_vacancies.return_value = []

        result = unified_api.get_vacancies_from_sources("Python")

        assert result == []
        mock_logger.info.assert_called_with("Вакансии не найдены")

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_sj_period_sync(self, mock_logger, unified_api):
        """Тест синхронизации параметров периода для SuperJob"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["sj"])

        # Мокаем API ответ
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "2"}]):
            result = unified_api.get_vacancies_from_sources("Python", sources=["sj"], period=30)

            assert len(result) == 1
            # Проверяем, что параметр period был преобразован в published
            unified_api.sj_api.get_vacancies.assert_called_once()
            call_args = unified_api.sj_api.get_vacancies.call_args
            assert "published" in call_args[1]
            assert call_args[1]["published"] == 30
            assert "period" not in call_args[1]

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_filtering_and_deduplication(self, mock_logger, unified_api):
        """Тест фильтрации и дедупликации вакансий"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh", "sj"])

        # Мокаем API ответы
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}, {"id": "2"}]):
            result = unified_api.get_vacancies_from_sources("Python")

            assert len(result) == 2
            mock_logger.info.assert_any_call("Всего получено 2 вакансий, применяем фильтрацию и дедупликацию через SQL")
            mock_logger.info.assert_any_call("После SQL-фильтрации и дедупликации: 2 уникальных вакансий от целевых компаний")

    @patch('src.api_modules.unified_api.logger')
    def test_get_vacancies_from_sources_no_target_companies(self, mock_logger, unified_api):
        """Тест получения вакансий без целевых компаний"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh", "sj"])

        # Мокаем API ответы
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем пустую фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[]):
            result = unified_api.get_vacancies_from_sources("Python")

            assert result == []
            mock_logger.info.assert_called_with("Не найдено вакансий от целевых компаний")

    def test_filter_by_target_companies(self, unified_api):
        """Тест фильтрации по целевым компаниям"""
        # Мокаем TargetCompanies
        with patch('src.config.target_companies.TargetCompanies') as mock_target_companies:
            mock_target_companies.get_hh_ids.return_value = ["company1", "company2"]
            mock_target_companies.get_sj_ids.return_value = ["company3"]

            # Тестовые вакансии
            test_vacancies = [
                {"id": "1", "employer": {"id": "company1"}, "source": "hh"},
                {"id": "2", "employer": {"id": "company2"}, "source": "hh"},
                {"id": "3", "employer": {"id": "company3"}, "source": "sj"},
                {"id": "4", "employer": {"id": "unknown"}, "source": "hh"},
            ]

            result = unified_api._filter_by_target_companies(test_vacancies)

            # Должны остаться только вакансии от целевых компаний
            assert len(result) == 3
            company_ids = [v["employer"]["id"] for v in result]
            assert "company1" in company_ids
            assert "company2" in company_ids
            assert "company3" in company_ids
            assert "unknown" not in company_ids

    def test_filter_by_target_companies_empty_input(self, unified_api):
        """Тест фильтрации пустого списка вакансий"""
        with patch('src.config.target_companies.TargetCompanies') as mock_target_companies:
            mock_target_companies.get_hh_ids.return_value = ["company1"]
            mock_target_companies.get_sj_ids.return_value = ["company2"]

            result = unified_api._filter_by_target_companies([])

            assert result == []

    def test_filter_by_target_companies_no_target_companies(self, unified_api):
        """Тест фильтрации без целевых компаний"""
        with patch('src.config.target_companies.TargetCompanies') as mock_target_companies:
            mock_target_companies.get_hh_ids.return_value = []
            mock_target_companies.get_sj_ids.return_value = []

            test_vacancies = [
                {"id": "1", "employer": {"id": "company1"}, "source": "hh"},
            ]

            result = unified_api._filter_by_target_companies(test_vacancies)

            assert result == []

    def test_filter_by_target_companies_missing_employer(self, unified_api):
        """Тест фильтрации вакансий без информации о работодателе"""
        with patch('src.config.target_companies.TargetCompanies') as mock_target_companies:
            mock_target_companies.get_hh_ids.return_value = ["company1"]
            mock_target_companies.get_sj_ids.return_value = ["company2"]

            # Вакансии без employer или с неполной информацией
            test_vacancies = [
                {"id": "1", "source": "hh"},  # Без employer
                {"id": "2", "employer": {}, "source": "hh"},  # Пустой employer
                {"id": "3", "employer": {"name": "Company"}, "source": "hh"},  # Без id
            ]

            result = unified_api._filter_by_target_companies(test_vacancies)

            # Такие вакансии должны быть отфильтрованы
            assert result == []

    def test_filter_by_target_companies_mixed_sources(self, unified_api):
        """Тест фильтрации вакансий из разных источников"""
        with patch('src.config.target_companies.TargetCompanies') as mock_target_companies:
            mock_target_companies.get_hh_ids.return_value = ["hh_company1", "hh_company2"]
            mock_target_companies.get_sj_ids.return_value = ["sj_company1"]

            # Вакансии из разных источников
            test_vacancies = [
                {"id": "1", "employer": {"id": "hh_company1"}, "source": "hh"},
                {"id": "2", "employer": {"id": "hh_company2"}, "source": "hh"},
                {"id": "3", "employer": {"id": "sj_company1"}, "source": "sj"},
                {"id": "4", "employer": {"id": "other_company"}, "source": "hh"},
            ]

            result = unified_api._filter_by_target_companies(test_vacancies)

            # Должны остаться вакансии от целевых компаний обоих источников
            assert len(result) == 3
            sources = [v["source"] for v in result]
            assert "hh" in sources
            assert "sj" in sources

    def test_get_vacancies_from_sources_with_additional_kwargs(self, unified_api):
        """Тест получения вакансий с дополнительными параметрами"""
        # Мокаем валидацию источников
        unified_api.validate_sources = Mock(return_value=["hh", "sj"])

        # Мокаем API ответы
        unified_api.hh_api.get_vacancies.return_value = [{"id": "1", "source": "hh"}]
        unified_api.sj_api.get_vacancies.return_value = [{"id": "2", "source": "sj"}]

        # Мокаем фильтрацию
        with patch.object(unified_api, '_filter_by_target_companies', return_value=[{"id": "1"}, {"id": "2"}]):
            additional_kwargs = {
                "per_page": 50,
                "experience": "3-6",
                "salary_from": 100000,
                "period": 30
            }

            result = unified_api.get_vacancies_from_sources("Python", **additional_kwargs)

            assert len(result) == 2

            # Проверяем, что параметры переданы в API
            unified_api.hh_api.get_vacancies.assert_called_once_with("Python", **additional_kwargs)
            unified_api.sj_api.get_vacancies.assert_called_once()

            # Проверяем, что period был преобразован в published для SuperJob
            sj_call_args = unified_api.sj_api.get_vacancies.call_args
            assert "published" in sj_call_args[1]
            assert sj_call_args[1]["published"] == 30
            assert "period" not in sj_call_args[1]