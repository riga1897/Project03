"""
Репозиторий для операций с вакансиями.
Реализует принцип единственной ответственности (SRP) и инверсию зависимостей (DIP).
"""

import logging
from typing import Any, Dict, List, Optional

from src.storage.abstract import AbstractVacancyStorage
from src.vacancies.abstract import AbstractVacancy

from .database_connection import DatabaseConnection
from .vacancy_validator import VacancyValidator

logger = logging.getLogger(__name__)


class VacancyRepository(AbstractVacancyStorage):
    """
    Репозиторий для работы с вакансиями в базе данных.

    Использует внедрение зависимостей для подключения к БД и валидации.
    Отвечает только за CRUD операции с вакансиями.
    """

    def __init__(self, db_connection: DatabaseConnection, validator: VacancyValidator):
        """
        Инициализация репозитория

        Args:
            db_connection: Объект управления подключениями к БД
            validator: Валидатор данных вакансий
        """
        self._db_connection = db_connection
        self._validator = validator

    def add_vacancy(self, vacancy: AbstractVacancy) -> bool:
        """
        Добавляет вакансию в хранилище

        Args:
            vacancy: Объект вакансии для добавления

        Raises:
            ValueError: Если вакансия не прошла валидацию
            ConnectionError: При ошибках подключения к БД
        """
        # Валидация перед сохранением
        if not self._validator.validate_vacancy(vacancy):
            errors = self._validator.get_validation_errors()
            raise ValueError(f"Вакансия не прошла валидацию: {', '.join(errors)}")

        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Упрощенная вставка - в реальной реализации будет полный SQL
                    insert_query = """
                        INSERT INTO vacancies (
                            vacancy_id, title, url, salary_from, salary_to, salary_currency,
                            description, requirements, responsibilities, experience,
                            employment, area, source, employer_name
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (vacancy_id) DO NOTHING
                    """

                    # Извлечение данных из объекта вакансии
                    salary_from = getattr(vacancy.salary, "salary_from", None) if vacancy.salary else None
                    salary_to = getattr(vacancy.salary, "salary_to", None) if vacancy.salary else None
                    salary_currency = getattr(vacancy.salary, "currency", None) if vacancy.salary else None

                    cursor.execute(
                        insert_query,
                        (
                            vacancy.vacancy_id,
                            vacancy.title,
                            vacancy.url,
                            salary_from,
                            salary_to,
                            salary_currency,
                            getattr(vacancy, "description", None),
                            getattr(vacancy, "requirements", None),
                            getattr(vacancy, "responsibilities", None),
                            getattr(vacancy, "experience", None),
                            getattr(vacancy, "employment", None),
                            getattr(vacancy, "area", None),
                            getattr(vacancy, "source", None),
                            str(getattr(vacancy, "employer", None)) if getattr(vacancy, "employer", None) else None,
                        ),
                    )

                conn.commit()
                logger.debug(f"Вакансия {vacancy.vacancy_id} успешно добавлена")
                return True

        except Exception as e:
            logger.error(f"Ошибка добавления вакансии {vacancy.vacancy_id}: {e}")
            return False

    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[AbstractVacancy]:
        """
        Возвращает список вакансий из хранилища с учетом фильтров

        Args:
            filters: Словарь с критериями фильтрации

        Returns:
            List[AbstractVacancy]: Список вакансий
        """
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Базовый запрос
                    query = "SELECT * FROM vacancies"
                    params = []

                    # Применение фильтров
                    if filters:
                        where_conditions = []

                        if "company_id" in filters and filters["company_id"]:
                            where_conditions.append("company_id = %s")
                            params.append(filters["company_id"])

                        if "min_salary" in filters and filters["min_salary"]:
                            where_conditions.append("(salary_from >= %s OR salary_to >= %s)")
                            params.extend([filters["min_salary"], filters["min_salary"]])

                        if "source" in filters and filters["source"]:
                            where_conditions.append("source = %s")
                            params.append(filters["source"])

                        if where_conditions:
                            query += " WHERE " + " AND ".join(where_conditions)

                    query += " ORDER BY created_at DESC"

                    cursor.execute(query, params)
                    rows = cursor.fetchall()

                    # Конвертация в объекты вакансий
                    # Здесь должна быть фабрика для создания объектов AbstractVacancy
                    vacancies = []
                    for row in rows:
                        # Упрощенное создание - в реальности будет через фабрику
                        from src.vacancies.models import Vacancy

                        vacancy_data = dict(row)
                        vacancy = Vacancy.from_dict(vacancy_data)
                        vacancies.append(vacancy)

                    # Type casting для совместимости с AbstractVacancy
                    from typing import cast

                    return cast(List[AbstractVacancy], vacancies)

        except Exception as e:
            logger.error(f"Ошибка получения вакансий: {e}")
            raise

    def delete_vacancy(self, vacancy: AbstractVacancy) -> None:
        """
        Удаляет вакансию из хранилища

        Args:
            vacancy: Объект вакансии для удаления
        """
        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM vacancies WHERE vacancy_id = %s", (vacancy.vacancy_id,))
                    conn.commit()

                    if cursor.rowcount > 0:
                        logger.debug(f"Вакансия {vacancy.vacancy_id} успешно удалена")
                    else:
                        logger.warning(f"Вакансия {vacancy.vacancy_id} не найдена для удаления")

        except Exception as e:
            logger.error(f"Ошибка удаления вакансии {vacancy.vacancy_id}: {e}")
            raise

    def check_vacancies_exist_batch(self, vacancies: List[AbstractVacancy]) -> Dict[str, bool]:
        """
        Проверяет существование множества вакансий одним запросом

        Args:
            vacancies: Список вакансий для проверки

        Returns:
            Dict[str, bool]: Словарь {vacancy_id: exists}
        """
        if not vacancies:
            return {}

        try:
            vacancy_ids = [v.vacancy_id for v in vacancies]
            placeholders = ", ".join(["%s"] * len(vacancy_ids))

            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"SELECT vacancy_id FROM vacancies WHERE vacancy_id IN ({placeholders})", vacancy_ids
                    )

                    existing_ids = {row["vacancy_id"] for row in cursor.fetchall()}

                    return {vacancy_id: vacancy_id in existing_ids for vacancy_id in vacancy_ids}

        except Exception as e:
            logger.error(f"Ошибка проверки существования вакансий: {e}")
            raise

    def add_vacancy_batch_optimized(
        self, vacancies: List[AbstractVacancy], search_query: Optional[str] = None
    ) -> List[str]:
        """
        Оптимизированное batch-добавление вакансий

        Args:
            vacancies: Список вакансий для добавления

        Returns:
            List[str]: Список ID успешно добавленных вакансий
        """
        if not vacancies:
            return []

        # Валидация всех вакансий
        validation_results = self._validator.validate_batch(vacancies)
        valid_vacancies = [v for v in vacancies if validation_results.get(v.vacancy_id, False)]

        if not valid_vacancies:
            logger.warning("Нет валидных вакансий для добавления")
            return []

        added_ids = []

        try:
            with self._db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Batch insert с помощью execute_values
                    from psycopg2.extras import execute_values

                    insert_data = []
                    for vacancy in valid_vacancies:
                        salary_from = getattr(vacancy.salary, "salary_from", None) if vacancy.salary else None
                        salary_to = getattr(vacancy.salary, "salary_to", None) if vacancy.salary else None
                        salary_currency = getattr(vacancy.salary, "currency", None) if vacancy.salary else None

                        insert_data.append(
                            (
                                vacancy.vacancy_id,
                                vacancy.title,
                                vacancy.url,
                                salary_from,
                                salary_to,
                                salary_currency,
                                getattr(vacancy, "description", None),
                                getattr(vacancy, "requirements", None),
                                getattr(vacancy, "responsibilities", None),
                                getattr(vacancy, "experience", None),
                                getattr(vacancy, "employment", None),
                                getattr(vacancy, "area", None),
                                getattr(vacancy, "source", None),
                                (
                                    str(getattr(vacancy, "employer", None))
                                    if getattr(vacancy, "employer", None)
                                    else None
                                ),
                            )
                        )

                    execute_values(
                        cursor,
                        """
                        INSERT INTO vacancies (
                            vacancy_id, title, url, salary_from, salary_to, salary_currency,
                            description, requirements, responsibilities, experience,
                            employment, area, source, employer_name
                        ) VALUES %s
                        ON CONFLICT (vacancy_id) DO NOTHING
                        """,
                        insert_data,
                    )

                    added_ids = [v.vacancy_id for v in valid_vacancies]
                    conn.commit()

                    logger.info(f"Batch добавлено {len(added_ids)} вакансий")

        except Exception as e:
            logger.error(f"Ошибка batch добавления вакансий: {e}")
            raise

        return added_ids
