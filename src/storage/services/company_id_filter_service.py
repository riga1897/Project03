"""
Сервис фильтрации вакансий по ID целевых компаний (hh_id и sj_id)

Реализует строгую ID-основанную фильтрацию без fallback методов.
Принцип Single Responsibility - только фильтрация по ID компаний.
"""

import logging
from typing import List, Set, Tuple

from src.config.target_companies import TargetCompanies
from src.storage.abstract_db_manager import AbstractDBManager
from src.vacancies.models import Vacancy

from .abstract_filter_service import AbstractFilterService

logger = logging.getLogger(__name__)


class CompanyIDFilterService(AbstractFilterService):
    """
    Сервис фильтрации по ID компаний (hh_id и sj_id)
    Принцип Single Responsibility - только ID-основанная фильтрация
    """

    def __init__(self, db_manager: AbstractDBManager):
        """
        Инициализация сервиса

        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager
        self._target_hh_ids = self._load_target_company_ids("hh")
        self._target_sj_ids = self._load_target_company_ids("sj")

        logger.info(f"Company ID Filter: HH IDs: {len(self._target_hh_ids)}, SJ IDs: {len(self._target_sj_ids)}")

    def _load_target_company_ids(self, source: str) -> Set[str]:
        """Загружает ID целевых компаний для указанного источника"""
        companies = TargetCompanies.get_all_companies()

        if source == "hh":
            return {str(comp.hh_id) for comp in companies if comp.hh_id}
        elif source == "sj":
            return {str(comp.sj_id) for comp in companies if comp.sj_id}

        return set()

    def filter_by_company_ids(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Фильтрует вакансии ТОЛЬКО по ID целевых компаний

        Args:
            vacancies: Список вакансий для фильтрации

        Returns:
            List[Vacancy]: Вакансии от целевых компаний (по ID)
        """
        if not vacancies:
            return []

        logger.info(f"Начинаем фильтрацию по ID компаний: {len(vacancies)} вакансий")

        try:
            with self.db_manager._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Создаем временную таблицу для входных данных
                    self._create_temp_table(cursor, vacancies)

                    # Выполняем SQL запрос для фильтрации по ID
                    filtered_vacancy_ids = self._execute_id_filter_query(cursor)

                    # Возвращаем только отфильтрованные вакансии
                    return self._build_filtered_vacancies(vacancies, filtered_vacancy_ids)

        except Exception as e:
            logger.error(f"Ошибка фильтрации по ID компаний: {e}")
            # В случае ошибки возвращаем пустой список (строгий подход)
            return []

    def _create_temp_table(self, cursor, vacancies: List[Vacancy]) -> None:
        """Создает временную таблицу для фильтрации по ID"""
        cursor.execute(
            """
            CREATE TEMP TABLE temp_company_filter (
                vacancy_id VARCHAR(255) PRIMARY KEY,
                employer_id VARCHAR(50),
                source VARCHAR(10),
                original_index INTEGER
            )
        """
        )

        # Подготавливаем данные для вставки
        filter_data = []
        for idx, vacancy in enumerate(vacancies):
            # Извлекаем ID работодателя
            employer_id = None

            if vacancy.employer:
                if hasattr(vacancy.employer, "get_id"):
                    employer_id = vacancy.employer.get_id()
                elif hasattr(vacancy.employer, "id"):
                    employer_id = vacancy.employer.id
                elif isinstance(vacancy.employer, dict):
                    employer_id = vacancy.employer.get("id")
                elif hasattr(vacancy.employer, "employer_id"):
                    employer_id = vacancy.employer.employer_id

            # Дополнительно проверяем поле employer_id на уровне вакансии
            if not employer_id and hasattr(vacancy, "employer_id"):
                employer_id = vacancy.employer_id

            filter_data.append(
                (
                    vacancy.vacancy_id,
                    str(employer_id) if employer_id else None,
                    getattr(vacancy, "source", "unknown").lower(),
                    idx,
                )
            )

        # Вставляем данные
        cursor.executemany(
            """
            INSERT INTO temp_company_filter
            (vacancy_id, employer_id, source, original_index)
            VALUES (%s, %s, %s, %s)
        """,
            filter_data,
        )

        logger.info(f"Создана временная таблица для фильтрации: {len(filter_data)} записей")

    def _execute_id_filter_query(self, cursor) -> List[str]:
        """Выполняет SQL запрос для фильтрации ТОЛЬКО по ID компаний"""

        # Формируем списки ID для SQL запроса
        hh_ids_list = ", ".join(f"'{id_}'" for id_ in self._target_hh_ids)
        sj_ids_list = ", ".join(f"'{id_}'" for id_ in self._target_sj_ids)

        # Если нет целевых ID - возвращаем пустой результат
        if not hh_ids_list and not sj_ids_list:
            logger.warning("Нет целевых ID компаний для фильтрации")
            return []

        query_parts = []

        # Фильтрация по HH ID
        if hh_ids_list:
            query_parts.append(f"(source LIKE '%hh%' AND employer_id IN ({hh_ids_list}))")

        # Фильтрация по SJ ID
        if sj_ids_list:
            query_parts.append(
                f"((source LIKE '%sj%' OR source LIKE '%superjob%') AND employer_id IN ({sj_ids_list}))"
            )

        # Если источник неизвестен, проверяем оба списка
        if hh_ids_list and sj_ids_list:
            query_parts.append(
                f"(source NOT LIKE '%hh%' AND source NOT LIKE '%sj%' AND "
                f"source NOT LIKE '%superjob%' AND (employer_id IN ({hh_ids_list}) OR employer_id IN ({sj_ids_list})))"
            )
        elif hh_ids_list:
            query_parts.append(
                f"(source NOT LIKE '%hh%' AND source NOT LIKE '%sj%' AND source NOT LIKE '%superjob%' AND employer_id IN ({hh_ids_list}))"
            )
        elif sj_ids_list:
            query_parts.append(
                f"(source NOT LIKE '%hh%' AND source NOT LIKE '%sj%' AND source NOT LIKE '%superjob%' AND employer_id IN ({sj_ids_list}))"
            )

        if not query_parts:
            return []

        query = f"""
        SELECT vacancy_id
        FROM temp_company_filter
        WHERE employer_id IS NOT NULL AND ({' OR '.join(query_parts)})
        ORDER BY original_index
        """

        cursor.execute(query)
        results = cursor.fetchall()

        filtered_ids = [row[0] for row in results]
        logger.info(f"ID-фильтрация: найдено {len(filtered_ids)} вакансий от целевых компаний")

        if not filtered_ids:
            logger.warning("ID-фильтр не нашел ни одной вакансии от целевых компаний")
            logger.info(f"Доступные целевые ID - HH: {len(self._target_hh_ids)}, SJ: {len(self._target_sj_ids)}")

            # Диагностика: показываем несколько примеров ID из входных данных
            cursor.execute(
                "SELECT DISTINCT employer_id, source FROM temp_company_filter WHERE employer_id IS NOT NULL LIMIT 10"
            )
            sample_ids = cursor.fetchall()
            logger.info(f"Примеры ID из входных данных: {sample_ids}")

        return filtered_ids

    def _build_filtered_vacancies(self, original_vacancies: List[Vacancy], filtered_ids: List[str]) -> List[Vacancy]:
        """Строит итоговый список отфильтрованных по ID вакансий"""
        vacancy_map = {v.vacancy_id: v for v in original_vacancies}

        filtered_vacancies = []
        for vacancy_id in filtered_ids:
            if vacancy_id in vacancy_map:
                filtered_vacancies.append(vacancy_map[vacancy_id])

        logger.info(f"ID-фильтрация завершена: {len(original_vacancies)} -> {len(filtered_vacancies)} вакансий")
        return filtered_vacancies

    def get_target_company_stats(self) -> Tuple[Set[str], Set[str]]:
        """
        Возвращает статистику по целевым компаниям

        Returns:
            Tuple[Set[str], Set[str]]: (HH ID, SJ ID) целевых компаний
        """
        return self._target_hh_ids, self._target_sj_ids
