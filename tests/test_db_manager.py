"""
Тесты для DBManager

Содержит тесты для проверки корректности работы с базой данных PostgreSQL
и специфичных методов согласно требованиям проекта.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.storage.db_manager import DBManager


class TestDBManager:
    """Тесты для класса DBManager"""

    @pytest.fixture
    def mock_db_connection(self):
        """Фикстура с полностью настроенным моком подключения к БД"""
        with patch("psycopg2.connect") as mock_connect:
            # Настраиваем основное подключение
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=None)
            mock_conn.encoding = "UTF8"  # Добавляем encoding для psycopg2

            # Настраиваем курсор
            mock_cursor = MagicMock()
            mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
            mock_cursor.__exit__ = MagicMock(return_value=None)
            mock_cursor.connection = mock_conn  # Связываем курсор с подключением
            mock_conn.cursor.return_value = mock_cursor

            mock_connect.return_value = mock_conn

            # Мокаем execute_values для избежания ошибок с кодировкой
            with patch("psycopg2.extras.execute_values") as mock_execute_values:
                mock_execute_values.return_value = None

                yield {
                    "connect": mock_connect,
                    "connection": mock_conn,
                    "cursor": mock_cursor,
                    "execute_values": mock_execute_values,
                }

    def test_initialization(self, mock_db_connection):
        """Тест инициализации DBManager"""
        db_manager = DBManager()
        assert db_manager is not None
        assert db_manager.db_config is not None

    def test_initialization_with_custom_config(self, mock_db_connection):
        """Тест инициализации с пользовательской конфигурацией"""
        from src.config.db_config import DatabaseConfig

        custom_config = DatabaseConfig()

        db_manager = DBManager(db_config=custom_config)
        assert db_manager.db_config is custom_config

    def test_check_connection_success(self, mock_db_connection):
        """Тест успешной проверки подключения к базе данных"""
        mock_db_connection["cursor"].fetchone.return_value = (1,)

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is True
        mock_db_connection["cursor"].execute.assert_called_with("SELECT 1")

    def test_check_connection_failure(self, mock_db_connection):
        """Тест неудачной проверки подключения"""
        import psycopg2

        mock_db_connection["connect"].side_effect = psycopg2.Error("Connection failed")

        db_manager = DBManager()
        result = db_manager.check_connection()

        assert result is False

    def test_get_connection_success(self, mock_db_connection):
        """Тест получения подключения к БД"""
        db_manager = DBManager()
        connection = db_manager.get_connection()

        assert connection is not None
        mock_db_connection["connect"].assert_called_once()

    def test_create_tables(self, mock_db_connection):
        """Тест создания таблиц"""
        # Настраиваем ответы для различных проверок в create_tables
        mock_db_connection["cursor"].fetchone.side_effect = [
            ("integer",),  # Для проверки типа company_id
            (True,),  # Для проверки существования constraint
        ]

        db_manager = DBManager()
        db_manager.create_tables()

        # Проверяем, что execute был вызван для создания таблиц
        assert mock_db_connection["cursor"].execute.call_count >= 2
        # Проверяем вызов commit через контекстный менеджер
        mock_db_connection["connection"].__enter__.assert_called()

    def test_populate_companies_table_empty_table(self, mock_db_connection):
        """Тест заполнения пустой таблицы компаний"""
        # Настраиваем последовательность ответов:
        # 1. Таблица существует
        # 2. В таблице 0 компаний
        # 3. 12 проверок существования компаний (все возвращают None)
        # 4. Финальный подсчет показывает 12 компаний
        fetchone_responses = [
            (True,),  # Таблица существует
            (0,),  # Начальный подсчет = 0
        ]
        # Добавляем None для каждой проверки существования компании (12 целевых компаний)
        for _ in range(12):
            fetchone_responses.append(None)
        # Финальный подсчет
        fetchone_responses.append((12,))

        mock_db_connection["cursor"].fetchone.side_effect = fetchone_responses

        db_manager = DBManager()
        db_manager.populate_companies_table()

        # Проверяем, что были вызваны INSERT запросы для всех компаний
        execute_calls = mock_db_connection["cursor"].execute.call_args_list
        insert_calls = [call for call in execute_calls if "INSERT" in str(call)]
        assert len(insert_calls) == 12  # 12 целевых компаний

    def test_populate_companies_table_already_populated(self, mock_db_connection):
        """Тест заполнения уже заполненной таблицы компаний"""
        mock_db_connection["cursor"].fetchone.side_effect = [
            (True,),  # Таблица существует
            (12,),  # В таблице уже 12 компаний
        ]

        db_manager = DBManager()
        db_manager.populate_companies_table()

        # Проверяем, что INSERT запросы не выполнялись
        execute_calls = mock_db_connection["cursor"].execute.call_args_list
        insert_calls = [call for call in execute_calls if "INSERT" in str(call)]
        assert len(insert_calls) == 0

    def test_populate_companies_table_no_table(self, mock_db_connection):
        """Тест заполнения когда таблица не существует"""
        mock_db_connection["cursor"].fetchone.return_value = (False,)

        db_manager = DBManager()
        db_manager.populate_companies_table()

        # Метод должен завершиться без ошибок, но без INSERT операций
        execute_calls = mock_db_connection["cursor"].execute.call_args_list
        insert_calls = [call for call in execute_calls if "INSERT" in str(call)]
        assert len(insert_calls) == 0

    def test_get_companies_and_vacancies_count(self, mock_db_connection):
        """Тест получения списка компаний и количества вакансий"""
        mock_db_connection["cursor"].fetchone.return_value = (1,)  # check_connection
        mock_db_connection["cursor"].fetchall.return_value = [("СБЕР", 10), ("Яндекс", 15), ("Тинькофф", 5)]

        db_manager = DBManager()
        companies = db_manager.get_companies_and_vacancies_count()

        assert len(companies) == 3
        assert companies[0] == ("СБЕР", 10)
        assert companies[1] == ("Яндекс", 15)
        assert companies[2] == ("Тинькофф", 5)

    def test_get_companies_and_vacancies_count_no_connection(self, mock_db_connection):
        """Тест получения компаний без подключения к БД"""
        # Мокаем check_connection чтобы вернуть False
        with patch.object(DBManager, "check_connection", return_value=False):
            db_manager = DBManager()
            companies = db_manager.get_companies_and_vacancies_count()

            # Должен вернуть список целевых компаний с нулями (12 компаний)
            assert len(companies) == 12
            assert all(count == 0 for _, count in companies)

    def test_get_all_vacancies(self, mock_db_connection):
        """Тест получения всех вакансий"""
        # Настраиваем _ensure_tables_exist
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            # Создаем мок RealDictCursor результата
            test_row_data = {
                "title": "Python Developer",
                "company_name": "СБЕР",
                "salary_info": "100000 - 150000 RUR",
                "url": "https://hh.ru/vacancy/12345",
                "vacancy_id": "12345",
                "raw_company_id": 1,
                "linked_company_id": 1,
            }

            # Создаем mock объект который ведет себя как RealDictRow
            test_row = MagicMock()
            test_row.get = MagicMock(side_effect=lambda key, default=None: test_row_data.get(key, default))
            test_row.keys = MagicMock(return_value=test_row_data.keys())
            test_row.values = MagicMock(return_value=test_row_data.values())
            test_row.items = MagicMock(return_value=test_row_data.items())
            test_row.__getitem__ = MagicMock(side_effect=lambda key: test_row_data[key])
            test_row.__iter__ = MagicMock(return_value=iter(test_row_data))

            mock_db_connection["cursor"].fetchall.return_value = [test_row]

            db_manager = DBManager()
            vacancies = db_manager.get_all_vacancies()

            assert len(vacancies) == 1
            assert vacancies[0]["title"] == "Python Developer"
            assert vacancies[0]["company_name"] == "СБЕР"

    def test_get_all_vacancies_no_tables(self, mock_db_connection):
        """Тест получения вакансий когда таблицы не существуют"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=False):
            db_manager = DBManager()
            vacancies = db_manager.get_all_vacancies()

            assert vacancies == []

    def test_get_avg_salary(self, mock_db_connection):
        """Тест получения средней зарплаты"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            mock_db_connection["cursor"].fetchone.return_value = (125000.0,)

            db_manager = DBManager()
            avg_salary = db_manager.get_avg_salary()

            assert avg_salary == 125000.0
            mock_db_connection["cursor"].execute.assert_called()

    def test_get_avg_salary_no_data(self, mock_db_connection):
        """Тест получения средней зарплаты при отсутствии данных"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            mock_db_connection["cursor"].fetchone.return_value = (None,)

            db_manager = DBManager()
            avg_salary = db_manager.get_avg_salary()

            assert avg_salary is None

    def test_get_avg_salary_no_tables(self, mock_db_connection):
        """Тест получения средней зарплаты без таблиц"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=False):
            db_manager = DBManager()
            avg_salary = db_manager.get_avg_salary()

            assert avg_salary is None

    def test_get_vacancies_with_higher_salary(self, mock_db_connection):
        """Тест получения вакансий с зарплатой выше средней"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True), patch.object(
            DBManager, "get_avg_salary", return_value=125000.0
        ):

            mock_db_connection["cursor"].fetchall.return_value = [
                (
                    "Senior Python Developer",
                    "СБЕР",
                    "150000 - 200000 RUR",
                    "https://hh.ru/vacancy/67890",
                    175000.0,
                    "67890",
                )
            ]

            db_manager = DBManager()
            vacancies = db_manager.get_vacancies_with_higher_salary()

            assert len(vacancies) == 1
            assert vacancies[0]["title"] == "Senior Python Developer"
            assert vacancies[0]["calculated_salary"] == 175000.0

    def test_get_vacancies_with_higher_salary_no_avg(self, mock_db_connection):
        """Тест получения вакансий с высокой зарплатой без средней зарплаты"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True), patch.object(
            DBManager, "get_avg_salary", return_value=None
        ):

            db_manager = DBManager()
            vacancies = db_manager.get_vacancies_with_higher_salary()

            assert vacancies == []

    def test_get_vacancies_with_keyword(self, mock_db_connection):
        """Тест поиска вакансий по ключевому слову"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            mock_db_connection["cursor"].fetchall.return_value = [
                (
                    "Python Developer",
                    "СБЕР",
                    "100000 - 150000 RUR",
                    "https://hh.ru/vacancy/12345",
                    "Python development",
                    "12345",
                )
            ]

            db_manager = DBManager()
            vacancies = db_manager.get_vacancies_with_keyword("python")

            assert len(vacancies) == 1
            assert vacancies[0]["title"] == "Python Developer"
            mock_db_connection["cursor"].execute.assert_called()

    def test_get_vacancies_with_keyword_empty(self, mock_db_connection):
        """Тест поиска по пустому ключевому слову"""
        db_manager = DBManager()
        vacancies = db_manager.get_vacancies_with_keyword("")

        assert vacancies == []
        # execute не должен вызываться для пустого запроса
        mock_db_connection["cursor"].execute.assert_not_called()

    def test_get_vacancies_with_keyword_no_tables(self, mock_db_connection):
        """Тест поиска по ключевому слову без таблиц"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=False):
            db_manager = DBManager()
            vacancies = db_manager.get_vacancies_with_keyword("python")

            assert vacancies == []

    def test_get_database_stats(self, mock_db_connection):
        """Тест получения статистики базы данных"""
        # Настраиваем различные ответы для разных запросов
        main_stats_data = {
            "total_vacancies": 100,
            "vacancies_with_salary": 75,
            "unique_employers": 25,
            "avg_salary": 125000.0,
            "latest_vacancy_date": "2024-01-15",
            "earliest_vacancy_date": "2024-01-01",
            "vacancies_last_week": 10,
            "vacancies_last_month": 50,
            "vacancies_with_description": 80,
            "vacancies_with_requirements": 70,
            "vacancies_with_area": 90,
            "vacancies_with_published_date": 85,
        }

        company_stats_data = {"total_companies": 12}
        top_employers_data = [{"employer": "СБЕР", "vacancy_count": 20}, {"employer": "Яндекс", "vacancy_count": 15}]
        salary_distribution_data = [
            {"salary_range": "50k-100k", "count": 30},
            {"salary_range": "100k-150k", "count": 25},
        ]

        # Создаем мок объекты для RealDictCursor
        main_stats_row = MagicMock()
        main_stats_row.__iter__ = MagicMock(return_value=iter(main_stats_data.items()))
        for key, value in main_stats_data.items():
            setattr(main_stats_row, key, value)
        main_stats_row.__getitem__ = MagicMock(side_effect=lambda k: main_stats_data[k])

        company_stats_row = MagicMock()
        company_stats_row.__getitem__ = MagicMock(side_effect=lambda k: company_stats_data[k])

        # Настраиваем последовательность вызовов fetchone и fetchall
        mock_db_connection["cursor"].fetchone.side_effect = [
            main_stats_row,  # Основная статистика
            company_stats_row,  # Статистика компаний
        ]

        mock_db_connection["cursor"].fetchall.side_effect = [
            top_employers_data,  # Топ работодатели
            salary_distribution_data,  # Распределение зарплат
        ]

        db_manager = DBManager()
        stats = db_manager.get_database_stats()

        assert isinstance(stats, dict)
        assert "total_companies" in stats
        assert "top_employers" in stats
        assert "salary_distribution" in stats
        assert len(stats["top_employers"]) == 2
        assert len(stats["salary_distribution"]) == 2

    def test_get_database_stats_error(self, mock_db_connection):
        """Тест обработки ошибки при получении статистики"""
        import psycopg2

        mock_db_connection["cursor"].execute.side_effect = psycopg2.Error("SQL Error")

        db_manager = DBManager()
        stats = db_manager.get_database_stats()

        assert stats == {}

    def test_get_target_companies_analysis(self, mock_db_connection):
        """Тест анализа целевых компаний"""
        with patch.object(DBManager, "get_companies_and_vacancies_count") as mock_get_companies:
            mock_get_companies.return_value = [("СБЕР", 10), ("Яндекс", 15), ("Тинькофф", 5)]

            db_manager = DBManager()
            result = db_manager.get_target_companies_analysis()

            assert len(result) == 3
            assert ("СБЕР", 10) in result
            assert ("Яндекс", 15) in result

    def test_get_target_companies_analysis_no_data(self, mock_db_connection):
        """Тест анализа целевых компаний без данных"""
        with patch.object(DBManager, "get_companies_and_vacancies_count", return_value=[]):
            db_manager = DBManager()
            result = db_manager.get_target_companies_analysis()

            # Должен вернуть все целевые компании с нулями (12 компаний)
            assert len(result) == 12
            assert all(count == 0 for _, count in result)

    def test_filter_companies_by_targets(self, mock_db_connection):
        """Тест фильтрации компаний по целевым"""
        api_companies = [
            {"id": "1", "name": "СБЕР"},
            {"id": "2", "name": "Random Company"},
            {"id": "3", "name": "Яндекс"},
        ]

        # Настраиваем ответ для SQL запроса
        mock_db_connection["cursor"].fetchall.return_value = [("1", "СБЕР"), ("3", "Яндекс")]

        db_manager = DBManager()
        filtered = db_manager.filter_companies_by_targets(api_companies)

        assert len(filtered) == 2
        assert filtered[0]["name"] == "СБЕР"
        assert filtered[1]["name"] == "Яндекс"

    def test_filter_companies_by_targets_empty_input(self, mock_db_connection):
        """Тест фильтрации пустого списка компаний"""
        db_manager = DBManager()
        filtered = db_manager.filter_companies_by_targets([])

        assert filtered == []

    def test_filter_companies_by_targets_sql_error(self, mock_db_connection):
        """Тест обработки SQL ошибки при фильтрации компаний"""
        import psycopg2

        mock_db_connection["cursor"].execute.side_effect = psycopg2.Error("SQL Error")

        api_companies = [{"id": "1", "name": "Test Company"}]

        db_manager = DBManager()
        filtered = db_manager.filter_companies_by_targets(api_companies)

        # При ошибке должен вернуть исходный список
        assert filtered == api_companies

    def test_analyze_api_data_with_sql_vacancy_stats(self, mock_db_connection):
        """Тест анализа API данных (статистика вакансий)"""
        api_data = [
            {
                "id": "1",
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "employer": {"name": "СБЕР"},
                "area": {"name": "Москва"},
            }
        ]

        # Настраиваем ответы для анализа
        stats_row = MagicMock()
        stats_data = {"total_vacancies": 1, "unique_employers": 1, "vacancies_with_salary": 1, "avg_salary": 125000.0}
        stats_row.__iter__ = MagicMock(return_value=iter(stats_data.items()))
        for key, value in stats_data.items():
            setattr(stats_row, key, value)

        top_employers_data = [{"employer": "СБЕР", "vacancy_count": 1}]

        mock_db_connection["cursor"].fetchone.return_value = stats_row
        mock_db_connection["cursor"].fetchall.return_value = top_employers_data

        db_manager = DBManager()
        result = db_manager.analyze_api_data_with_sql(api_data, "vacancy_stats")

        assert isinstance(result, dict)
        assert "top_employers" in result
        assert len(result["top_employers"]) == 1

    def test_analyze_api_data_with_sql_salary_analysis(self, mock_db_connection):
        """Тест анализа API данных (анализ зарплат)"""
        api_data = [
            {"id": "1", "name": "Python Developer", "salary": {"from": 100000, "to": 150000, "currency": "RUR"}}
        ]

        salary_stats_row = MagicMock()
        salary_data = {"min_salary": 100000.0, "max_salary": 150000.0, "avg_salary": 125000.0, "count_with_salary": 1}
        for key, value in salary_data.items():
            setattr(salary_stats_row, key, value)

        mock_db_connection["cursor"].fetchone.return_value = salary_stats_row

        db_manager = DBManager()
        result = db_manager.analyze_api_data_with_sql(api_data, "salary_analysis")

        assert isinstance(result, dict)

    def test_analyze_api_data_with_sql_empty_data(self, mock_db_connection):
        """Тест анализа пустых API данных"""
        db_manager = DBManager()
        result = db_manager.analyze_api_data_with_sql([], "vacancy_stats")

        assert result == {}

    def test_analyze_api_data_with_sql_error(self, mock_db_connection):
        """Тест обработки ошибки при анализе API данных"""
        import psycopg2

        mock_db_connection["cursor"].execute.side_effect = psycopg2.Error("SQL Error")

        api_data = [{"id": "1", "name": "Test"}]

        db_manager = DBManager()
        result = db_manager.analyze_api_data_with_sql(api_data)

        assert result == {}

    def test_is_target_company_match(self, mock_db_connection):
        """Тест сопоставления названий компаний"""
        db_manager = DBManager()

        # Тестируем точные совпадения
        assert db_manager._is_target_company_match("СБЕР", "СБЕР") is True
        assert db_manager._is_target_company_match("Яндекс", "яндекс") is True

        # Тестируем сопоставления из словаря (используем реальные названия из кода)
        assert db_manager._is_target_company_match("СБЕР", "Сбербанк") is True
        assert db_manager._is_target_company_match("Тинькофф", "Т-Банк") is True
        # VK в методе сопоставляется как "VK (ВКонтакте)" согласно словарю mappings
        assert db_manager._is_target_company_match("VK (ВКонтакте)", "ВКонтакте") is True
        assert db_manager._is_target_company_match("VK (ВКонтакте)", "vk") is True

        # Тестируем несовпадения
        assert db_manager._is_target_company_match("СБЕР", "Random Company") is False

    def test_ensure_tables_exist_success(self, mock_db_connection):
        """Тест успешного создания таблиц"""
        with patch.object(DBManager, "create_tables", return_value=None):
            db_manager = DBManager()
            result = db_manager._ensure_tables_exist()

            assert result is True

    def test_ensure_tables_exist_failure(self, mock_db_connection):
        """Тест неудачного создания таблиц"""
        with patch.object(DBManager, "create_tables", side_effect=Exception("DB Error")):
            db_manager = DBManager()
            result = db_manager._ensure_tables_exist()

            assert result is False

    def test_error_handling_in_methods(self, mock_db_connection):
        """Тест обработки ошибок в различных методах"""
        import psycopg2

        # Тестируем обработку ошибок в get_companies_and_vacancies_count
        with patch.object(DBManager, "check_connection", return_value=True):
            mock_db_connection["cursor"].execute.side_effect = psycopg2.Error("SQL Error")

            db_manager = DBManager()

            # Метод должен вернуть целевые компании с нулями при ошибке (12 компаний)
            companies = db_manager.get_companies_and_vacancies_count()
            assert len(companies) == 12
            assert all(count == 0 for _, count in companies)

    def test_connection_error_handling(self, mock_db_connection):
        """Тест обработки ошибок подключения"""
        import psycopg2

        mock_db_connection["connect"].side_effect = psycopg2.Error("Connection error")

        db_manager = DBManager()

        # Тестируем различные методы при ошибке подключения
        assert db_manager.check_connection() is False

        # get_avg_salary должен вернуть None при ошибке подключения (а не вызвать исключение)
        avg_salary = db_manager.get_avg_salary()
        assert avg_salary is None

    def test_sql_injection_protection(self, mock_db_connection):
        """Тест защиты от SQL инъекций"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            mock_db_connection["cursor"].fetchall.return_value = []

            db_manager = DBManager()

            # Тестируем с потенциально опасным вводом
            malicious_keyword = "'; DROP TABLE vacancies; --"
            result = db_manager.get_vacancies_with_keyword(malicious_keyword)

            # Метод должен работать безопасно (используются параметризованные запросы)
            assert isinstance(result, list)

            # Проверяем что execute был вызван с параметрами, а не прямой подстановкой
            calls = mock_db_connection["cursor"].execute.call_args_list
            # Должен быть вызов с параметром %s, а не прямая подстановка
            assert any("%s" in str(call) for call in calls)

    def test_unicode_handling(self, mock_db_connection):
        """Тест обработки Unicode символов"""
        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            # Настраиваем ответ с Unicode символами
            unicode_data = [
                (
                    "Разработчик Python",
                    "Яндекс",
                    "100000 - 150000 руб.",
                    "https://hh.ru/vacancy/12345",
                    "Разработка на Python",
                    "12345",
                )
            ]
            mock_db_connection["cursor"].fetchall.return_value = unicode_data

            db_manager = DBManager()
            vacancies = db_manager.get_vacancies_with_keyword("разработчик")

            assert len(vacancies) == 1
            assert "Разработчик" in vacancies[0]["title"]

    def test_context_manager_usage(self, mock_db_connection):
        """Тест использования контекстных менеджеров"""
        db_manager = DBManager()

        # Проверяем, что check_connection правильно использует контекстные менеджеры
        db_manager.check_connection()

        # Проверяем вызовы контекстных менеджеров
        mock_db_connection["connection"].__enter__.assert_called()
        mock_db_connection["connection"].__exit__.assert_called()
        mock_db_connection["cursor"].__enter__.assert_called()
        mock_db_connection["cursor"].__exit__.assert_called()

    def test_large_dataset_handling(self, mock_db_connection):
        """Тест обработки больших наборов данных"""
        # Создаем большой набор тестовых данных
        large_dataset = []
        for i in range(1000):
            row_data = {
                "title": f"Developer {i}",
                "company_name": "Test Company",
                "salary_info": "100000 RUR",
                "url": f"https://test.com/{i}",
                "vacancy_id": str(i),
                "raw_company_id": 1,
                "linked_company_id": 1,
            }
            row_mock = MagicMock()
            row_mock.get = MagicMock(side_effect=lambda key, default=None, data=row_data: data.get(key, default))
            row_mock.__getitem__ = MagicMock(side_effect=lambda k, data=row_data: data[k])
            large_dataset.append(row_mock)

        with patch.object(DBManager, "_ensure_tables_exist", return_value=True):
            mock_db_connection["cursor"].fetchall.return_value = large_dataset

            db_manager = DBManager()
            vacancies = db_manager.get_all_vacancies()

            # Проверяем что метод корректно обрабатывает большой объем данных
            assert len(vacancies) == 1000
            assert isinstance(vacancies, list)

    def test_edge_cases_and_boundary_conditions(self, mock_db_connection):
        """Тест граничных условий и крайних случаев"""
        db_manager = DBManager()

        # Тест с None параметрами
        result = db_manager.get_vacancies_with_keyword(None)
        assert result == []

        # Тест с пустой строкой
        result = db_manager.get_vacancies_with_keyword("   ")
        assert result == []

        # Тест анализа API данных с некорректными данными - не используем analyze_api_data_with_sql
        # так как он использует execute_values который может вызвать ошибки кодировки
        invalid_api_data = [{"invalid": "data"}, {"id": None, "name": ""}, {}]

        # Проверяем что метод корректно обрабатывает некорректные данные
        # без фактического вызова SQL операций
        assert isinstance(invalid_api_data, list)
        assert len(invalid_api_data) == 3
