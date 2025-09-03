"""
Единый SQL-модуль для консолидации фильтрации и дедупликации вакансий

Все операции фильтрации и дедупликации выполняются только здесь через SQL.
Никаких fallback методов или дублирования кода.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple

from src.config.target_companies import TargetCompanies
from src.storage.abstract_db_manager import AbstractDBManager
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class SQLFilterService:
    """
    Единственный сервис для всех операций фильтрации и дедупликации.
    Принцип Single Responsibility - только SQL операции с вакансиями.
    """

    def __init__(self, db_manager: AbstractDBManager):
        """
        Инициализация SQL-сервиса фильтрации

        Args:
            db_manager: Менеджер базы данных для выполнения SQL запросов
        """
        self.db_manager = db_manager
        self._target_hh_ids = self._load_target_company_ids("hh")
        self._target_sj_ids = self._load_target_company_ids("sj")

        logger.info(f"SQL Filter Service: HH IDs: {len(self._target_hh_ids)}, SJ IDs: {len(self._target_sj_ids)}")

    def _load_target_company_ids(self, source: str) -> Set[str]:
        """Загружает ID целевых компаний для указанного источника"""
        companies = TargetCompanies.get_all_companies()

        if source == "hh":
            return {str(comp.hh_id) for comp in companies if comp.hh_id}
        elif source == "sj":
            return {str(comp.sj_id) for comp in companies if comp.sj_id}

        return set()

    def filter_and_deduplicate_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Единая точка для фильтрации и дедупликации через SQL

        Args:
            vacancies: Список всех вакансий

        Returns:
            List[Vacancy]: Отфильтрованные и дедуплицированные вакансии
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем SQL фильтрацию для {len(vacancies)} вакансий")

        try:
            with self.db_manager._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу для входных данных
                    self._create_temp_vacancy_table(cursor, vacancies)

                    # Выполняем единый SQL запрос для фильтрации и дедупликации
                    filtered_vacancy_ids = self._execute_filter_query(cursor)

                    # Возвращаем только отфильтрованные вакансии
                    return self._build_filtered_vacancies(vacancies, filtered_vacancy_ids)

        except Exception as e:
            logger.error(f"Ошибка SQL фильтрации: {e}")
            return []

    def _create_temp_vacancy_table(self, cursor, vacancies: List[Vacancy]) -> None:
        """Создает временную таблицу с вакансиями для SQL обработки"""
        cursor.execute(
            """
            CREATE TEMP TABLE temp_filter_vacancies (
                vacancy_id VARCHAR(255) PRIMARY KEY,
                title_normalized TEXT,
                employer_id VARCHAR(50),
                employer_name_normalized TEXT,
                source VARCHAR(10),
                salary_from INTEGER,
                salary_to INTEGER,
                original_index INTEGER,
                description TEXT,
                requirements TEXT,
                responsibilities TEXT
            )
        """
        )

        # Подготавливаем данные для вставки
        vacancy_data = []
        for idx, vacancy in enumerate(vacancies):
            # Извлекаем ID работодателя
            employer_id = None
            employer_name = "Не указана"

            if vacancy.employer:
                if hasattr(vacancy.employer, "get_id"):
                    employer_id = vacancy.employer.get_id()
                if hasattr(vacancy.employer, "get_name"):
                    employer_name = vacancy.employer.get_name()

            # Парсим описание на требования и обязанности
            from src.utils.description_parser import DescriptionParser

            description = getattr(vacancy, "description", "") or ""
            requirements, responsibilities = DescriptionParser.extract_requirements_and_responsibilities(description)

            vacancy_data.append(
                (
                    vacancy.vacancy_id,
                    self._normalize_text(vacancy.title or ""),
                    employer_id,
                    self._normalize_text(employer_name),
                    getattr(vacancy, "source", "unknown"),
                    getattr(vacancy.salary, "salary_from", None) if vacancy.salary else None,
                    getattr(vacancy.salary, "salary_to", None) if vacancy.salary else None,
                    idx,
                    description,
                    requirements,
                    responsibilities,
                )
            )

        # Вставляем данные
        cursor.executemany(
            """
            INSERT INTO temp_filter_vacancies 
            (vacancy_id, title_normalized, employer_id, employer_name_normalized, source, 
             salary_from, salary_to, original_index, description, requirements, responsibilities)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            vacancy_data,
        )

        logger.info(f"Создана временная таблица с {len(vacancy_data)} записями")

    def _execute_filter_query(self, cursor) -> List[str]:
        """Выполняет единый SQL запрос для фильтрации по целевым компаниям и дедупликации"""

        # Формируем списки ID для SQL запроса
        hh_ids_list = ", ".join(f"'{id_}'" for id_ in self._target_hh_ids)
        sj_ids_list = ", ".join(f"'{id_}'" for id_ in self._target_sj_ids)

        query = f"""
        WITH filtered_by_companies AS (
            SELECT 
                vacancy_id,
                title_normalized,
                employer_name_normalized,
                original_index,
                ROW_NUMBER() OVER (
                    PARTITION BY title_normalized, employer_name_normalized 
                    ORDER BY original_index
                ) as row_num
            FROM temp_filter_vacancies
            WHERE (
                (source = 'hh' AND employer_id IN ({hh_ids_list if hh_ids_list else 'NULL'}))
                OR 
                (source = 'sj' AND employer_id IN ({sj_ids_list if sj_ids_list else 'NULL'}))
                OR 
                (employer_id IN ({hh_ids_list if hh_ids_list else 'NULL'}) OR employer_id IN ({sj_ids_list if sj_ids_list else 'NULL'}))
            )
        )
        SELECT vacancy_id 
        FROM filtered_by_companies 
        WHERE row_num = 1
        ORDER BY original_index
        """

        cursor.execute(query)
        results = cursor.fetchall()

        filtered_ids = [row[0] for row in results]
        logger.info(f"SQL фильтрация: {len(filtered_ids)} уникальных вакансий от целевых компаний")

        if not filtered_ids:
            logger.warning("SQL фильтр не нашел ни одной вакансии от целевых компаний")
            logger.info(f"Проверка: HH целевых компаний: {len(self._target_hh_ids)}, SJ: {len(self._target_sj_ids)}")

        return filtered_ids

    def _build_filtered_vacancies(self, original_vacancies: List[Vacancy], filtered_ids: List[str]) -> List[Vacancy]:
        """Строит итоговый список отфильтрованных вакансий"""
        vacancy_map = {v.vacancy_id: v for v in original_vacancies}

        filtered_vacancies = []
        for vacancy_id in filtered_ids:
            if vacancy_id in vacancy_map:
                filtered_vacancies.append(vacancy_map[vacancy_id])

        return filtered_vacancies

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Нормализация текста для сравнения"""
        if not text:
            return ""
        return text.lower().strip()

    def get_companies_vacancy_count(self) -> List[Tuple[str, int]]:
        """
        Получает статистику по целевым компаниям только через SQL

        Returns:
            List[Tuple[str, int]]: Список (название_компании, количество_вакансий)
        """
        try:
            with self.db_manager._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Формируем список всех целевых ID
                    all_target_ids = list(self._target_hh_ids.union(self._target_sj_ids))

                    if not all_target_ids:
                        return []

                    ids_placeholders = ", ".join(["%s"] * len(all_target_ids))

                    query = f"""
                    SELECT 
                        c.name as company_name,
                        COUNT(v.id) as vacancy_count
                    FROM companies c
                    LEFT JOIN vacancies v ON c.id = v.company_id
                    WHERE (c.hh_id IN ({ids_placeholders}) OR c.sj_id IN ({ids_placeholders}))
                    GROUP BY c.name, c.id
                    ORDER BY vacancy_count DESC, company_name
                    """

                    cursor.execute(query, all_target_ids + all_target_ids)
                    results = cursor.fetchall()

                    return [(row[0], row[1]) for row in results]

        except Exception as e:
            logger.error(f"Ошибка получения статистики компаний: {e}")
            return []
