"""
Интеграционный сервис работы с вакансиями на основе DBManager

Полностью заменяет postgres_saver, объединяя все операции через SOLID-принципы.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from ..db_manager import DBManager
except ImportError:
    from src.storage.db_manager import DBManager

try:
    from .deduplication_service import DeduplicationService, SQLDeduplicationStrategy
except ImportError:
    from src.storage.services.deduplication_service import DeduplicationService, SQLDeduplicationStrategy

# Filtering service импорты закомментированы, так как не используются
# try:
#     from .filtering_service import (CompositeFilterStrategy, FilteringService, SalaryFilterStrategy,
#                                     TargetCompanyFilterStrategy)
# except ImportError:
#     from src.storage.services.filtering_service import (CompositeFilterStrategy, FilteringService,
#                                                         SalaryFilterStrategy, TargetCompanyFilterStrategy)

try:
    from .vacancy_processing_coordinator import VacancyProcessingCoordinator
except ImportError:
    from src.storage.services.vacancy_processing_coordinator import VacancyProcessingCoordinator

try:
    from .abstract_storage_service import AbstractVacancyStorageService
except ImportError:
    from src.storage.services.abstract_storage_service import AbstractVacancyStorageService

try:
    from ...vacancies.models import Vacancy
except ImportError:
    from src.vacancies.models import Vacancy

try:
    from ...config.target_companies import TargetCompanies
except ImportError:
    from src.config.target_companies import TargetCompanies

try:
    from ...utils.data_normalizers import normalize_area_data
except ImportError:
    from src.utils.data_normalizers import normalize_area_data

logger = logging.getLogger(__name__)


class VacancyStorageService(AbstractVacancyStorageService):
    """
    Основной сервис для работы с вакансиями - замена postgres_saver

    Реализует все операции с вакансиями через DBManager и SOLID-сервисы:
    - Фильтрация по целевым компаниям (только ID-основанная)
    - Дедупликация на уровне SQL
    - Оптимизированное сохранение в базу
    """

    def __init__(self, db_manager: Optional[DBManager] = None):
        """
        Инициализация сервиса

        Args:
            db_manager: Менеджер базы данных. Если None, создается по умолчанию
        """
        self.db_manager = db_manager or DBManager()

        # Инициализируем новый координатор обработки (заменяет старые сервисы)
        self.processing_coordinator = VacancyProcessingCoordinator(self.db_manager)

        # Оставляем старые сервисы для обратной совместимости
        self.deduplication_service = DeduplicationService(SQLDeduplicationStrategy())

        # Настраиваем стратегии фильтрации на основе конфигурации
        # from src.storage.services.filtering_strategies import FilteringStrategy  # type: ignore
        filter_strategies = []  # type: ignore

        # Добавляем фильтр по зарплате, если включен
        # if self._should_filter_by_salary():
        #     filter_strategies.append(SalaryFilterStrategy())
        #     logger.info("Включен фильтр по зарплате")

        # self.filtering_service = FilteringService(CompositeFilterStrategy(filter_strategies))  # type: ignore

        # Целевые компании для сопоставления
        self.target_companies = TargetCompanies.get_all_companies()

        logger.info(f"Инициализирован VacancyStorageService с {len(filter_strategies)} стратегиями фильтрации")

    def _should_filter_by_salary(self) -> bool:
        """Проверяет, нужно ли фильтровать по зарплате"""
        filter_env = os.getenv("FILTER_ONLY_WITH_SALARY", "false").lower()
        return filter_env in ("true", "1", "yes", "on")

    def filter_and_deduplicate_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Основной метод обработки вакансий
        Использует новый координатор с разделенными операциями

        Args:
            vacancies: Список вакансий для обработки

        Returns:
            Обработанные вакансии (отфильтрованные и без дубликатов)
        """
        if not vacancies:
            logger.info("Получен пустой список вакансий")
            return []

        logger.info(f"Начинаем обработку {len(vacancies)} вакансий с разделенными операциями")

        try:
            # Используем новый координатор с четким разделением ответственности
            processed_vacancies = self.processing_coordinator.process_vacancies(
                vacancies,
                apply_company_filter=True,  # ID-основанная фильтрация по компаниям
                apply_deduplication=True,  # SQL-дедупликация
            )

            if not processed_vacancies:
                logger.warning("Координатор не вернул ни одной вакансии")
                return []

            # Этап 3: Обогащение данными о компаниях (как и раньше)
            enriched_vacancies = self._enrich_with_company_data(processed_vacancies)

            logger.info(f"Обработка завершена: {len(vacancies)} -> {len(enriched_vacancies)} вакансий")
            return enriched_vacancies

        except Exception as e:
            logger.error(f"Ошибка при обработке вакансий: {e}")
            # В случае ошибки используем старый метод как fallback
            return self._legacy_filter_and_deduplicate(vacancies)

    def _legacy_filter_and_deduplicate(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """Старый метод обработки для fallback"""
        try:
            # Этап 1: Фильтрация
            filtered_vacancies = vacancies  # type: ignore  # filtering_service не инициализирован
            logger.info(f"Legacy фильтрация: {len(vacancies)} -> {len(filtered_vacancies)} вакансий")

            if not filtered_vacancies:
                logger.warning("После legacy фильтрации не осталось вакансий")
                return []

            # Этап 2: Дедупликация
            deduplicated_vacancies = self.deduplication_service.process(filtered_vacancies, self.db_manager)
            logger.info(f"Legacy дедупликация: {len(filtered_vacancies)} -> {len(deduplicated_vacancies)} вакансий")

            # Этап 3: Обогащение данными о компаниях
            enriched_vacancies = self._enrich_with_company_data(deduplicated_vacancies)

            return enriched_vacancies

        except Exception as e:
            logger.error(f"Ошибка в legacy обработке: {e}")
            return vacancies  # Возвращаем исходные данные при ошибке

    def _enrich_with_company_data(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Обогащает вакансии данными о целевых компаниях
        """
        try:
            # Получаем соответствия ID компаний из базы
            company_mapping = self._get_company_id_mapping()

            for vacancy in vacancies:
                company_id = self._find_company_id(vacancy, company_mapping)
                if company_id:
                    vacancy.company_id = company_id
                    # Дополнительно устанавливаем company_name для обратной совместимости
                    if hasattr(vacancy, "employer") and isinstance(vacancy.employer, dict):
                        employer_name = vacancy.employer.get("name")
                        if employer_name:
                            vacancy.company_name = employer_name

            return vacancies

        except Exception as e:
            logger.warning(f"Ошибка при обогащении данными о компаниях: {e}")
            return vacancies

    def _get_company_id_mapping(self) -> Dict[str, int]:
        """Получает соответствия ID компаний из базы"""
        try:
            with self.db_manager._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, hh_id, sj_id
                        FROM companies
                        WHERE hh_id IS NOT NULL OR sj_id IS NOT NULL
                    """
                    )

                    mapping = {}
                    for row in cursor.fetchall():
                        db_id, hh_id, sj_id = row
                        if hh_id:
                            mapping[str(hh_id)] = db_id
                        if sj_id:
                            mapping[str(sj_id)] = db_id

                    logger.info(f"Загружено {len(mapping)} соответствий ID компаний")
                    return mapping

        except Exception as e:
            logger.error(f"Ошибка получения соответствий компаний: {e}")
            return {}

    def _find_company_id(self, vacancy: Vacancy, company_mapping: Dict[str, int]) -> Optional[int]:
        """Находит ID компании по вакансии"""
        if not vacancy.employer:
            return None

        employer_id = None
        if isinstance(vacancy.employer, dict):
            employer_id = vacancy.employer.get("id")
        elif hasattr(vacancy.employer, "id"):
            employer_id = vacancy.employer.id

        if employer_id:
            return company_mapping.get(str(employer_id))

        return None

    def _log_salary_diagnostics(self, stage: str, vacancies: List[Vacancy]) -> None:
        """
        Подробная диагностика зарплат на каждом этапе
        """
        if not vacancies:
            print(f"\n🔍 [{stage}] Список вакансий пуст")
            return

        with_salary = 0
        without_salary = 0
        salary_examples: List[str] = []

        print(f"\n🔍 [{stage}] Анализ {len(vacancies)} вакансий:")

        for i, vacancy in enumerate(vacancies[:5]):  # Анализируем первые 5
            has_salary = False
            salary_info = "НЕТ"

            # Детальный анализ зарплаты
            if vacancy.salary:
                if isinstance(vacancy.salary, dict):
                    salary_from = vacancy.salary.get("from")
                    salary_to = vacancy.salary.get("to")
                    currency = vacancy.salary.get("currency", "RUR")

                    if salary_from or salary_to:
                        has_salary = True
                        parts = []
                        if salary_from:
                            parts.append(f"от {salary_from:,}")
                        if salary_to:
                            parts.append(f"до {salary_to:,}")
                        salary_info = f"{' '.join(parts)} {currency}"
                elif hasattr(vacancy.salary, "salary_from") or hasattr(vacancy.salary, "salary_to"):
                    salary_from = getattr(vacancy.salary, "salary_from", None)
                    salary_to = getattr(vacancy.salary, "salary_to", None)
                    currency = getattr(vacancy.salary, "currency", "RUR")

                    if salary_from or salary_to:
                        has_salary = True
                        parts = []
                        if salary_from:
                            parts.append(f"от {salary_from:,}")
                        if salary_to:
                            parts.append(f"до {salary_to:,}")
                        salary_info = f"{' '.join(parts)} {currency}"
                else:
                    salary_info = f"ОБЪЕКТ: {type(vacancy.salary)} = {vacancy.salary}"

            if has_salary:
                with_salary += 1
            else:
                without_salary += 1

            # Информация о работодателе
            employer_info = "НЕТ"
            if vacancy.employer:
                if isinstance(vacancy.employer, dict):
                    employer_name = vacancy.employer.get("name", "БЕЗ_НАЗВАНИЯ")
                    employer_id = vacancy.employer.get("id", "БЕЗ_ID")
                    employer_info = f"{employer_name} (ID: {employer_id})"
                else:
                    employer_info = f"ОБЪЕКТ: {type(vacancy.employer)}"

            print(f"  {i + 1}. '{vacancy.title[:50]}...' | Зарплата: {salary_info} | Компания: {employer_info}")

            if has_salary and len(salary_examples) < 3:
                salary_examples.append(f"{vacancy.title}: {salary_info}")

        print(f"\n📊 СТАТИСТИКА [{stage}]:")
        print(f"   С зарплатой: {with_salary}")
        print(f"   Без зарплаты: {without_salary}")
        print(f"   Общий процент с зарплатой: {(with_salary / len(vacancies) * 100):.1f}%")

        if salary_examples:
            print("\n💰 ПРИМЕРЫ ЗАРПЛАТ:")
            for example in salary_examples:
                print(f"   '{example}'...")

        print("-" * 80)

    def add_vacancy_batch_optimized(self, vacancies: List[Vacancy], search_query: Optional[str] = None) -> List[str]:
        """
        Оптимизированное пакетное добавление вакансий
        Заменяет одноименный метод в postgres_saver

        Args:
            vacancies: Список вакансий

        Returns:
            Список сообщений о результатах сохранения
        """
        if not vacancies:
            return []

        # Исправляем двойную вложенность списков на уровне VacancyStorageService
        if len(vacancies) == 1 and isinstance(vacancies[0], list):
            vacancies = vacancies[0]
            logger.debug(
                f"VacancyStorageService: исправлена двойная вложенность списка: получено {len(vacancies)} вакансий"
            )

        logger.info(f"Начинаем пакетное сохранение {len(vacancies)} вакансий")

        try:
            # Получаем соответствия ID компаний
            company_mapping = self._get_company_id_mapping()

            with self.db_manager._get_connection() as connection:
                with connection.cursor() as cursor:
                    success_count = 0
                    messages = []

                    # Пакетная вставка с обработкой конфликтов
                    insert_data = []
                    for vacancy in vacancies:
                        try:
                            data = self._prepare_vacancy_data(vacancy, company_mapping, search_query)
                            if data:
                                insert_data.append(data)
                        except Exception as e:
                            logger.warning(f"Ошибка подготовки данных вакансии {vacancy.vacancy_id}: {e}")

                    if insert_data:
                        # Используем ON CONFLICT DO UPDATE для обработки дубликатов
                        cursor.executemany(
                            """
                            INSERT INTO vacancies (
                                vacancy_id, title, url, salary_from, salary_to, salary_currency,
                                description, requirements, responsibilities, experience,
                                employment, schedule, area, source, published_at, company_id, search_query
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (vacancy_id) DO UPDATE SET
                                title = EXCLUDED.title,
                                url = EXCLUDED.url,
                                salary_from = EXCLUDED.salary_from,
                                salary_to = EXCLUDED.salary_to,
                                salary_currency = EXCLUDED.salary_currency,
                                description = EXCLUDED.description,
                                requirements = EXCLUDED.requirements,
                                responsibilities = EXCLUDED.responsibilities,
                                experience = EXCLUDED.experience,
                                employment = EXCLUDED.employment,
                                schedule = EXCLUDED.schedule,
                                area = EXCLUDED.area,
                                source = EXCLUDED.source,
                                published_at = EXCLUDED.published_at,
                                company_id = EXCLUDED.company_id,
                                updated_at = CURRENT_TIMESTAMP
                        """,
                            insert_data,
                        )

                        success_count = cursor.rowcount
                        connection.commit()

                    messages.append(f"Успешно сохранено {success_count} вакансий")
                    logger.info(f"Пакетное сохранение завершено: {success_count}/{len(vacancies)}")

                    return messages

        except Exception as e:
            logger.error(f"Ошибка при пакетном сохранении: {e}")
            return [f"Ошибка сохранения: {e}"]

    def _prepare_vacancy_data(
        self, vacancy: Vacancy, company_mapping: Dict[str, int], search_query: Optional[str] = None
    ) -> Optional[tuple]:
        """Подготавливает данные вакансии для вставки в БД"""
        try:
            # Обработка зарплаты
            salary_from = None
            salary_to = None
            salary_currency = None

            if vacancy.salary:
                if isinstance(vacancy.salary, dict):
                    salary_from = vacancy.salary.get("from")
                    salary_to = vacancy.salary.get("to")
                    salary_currency = vacancy.salary.get("currency")
                elif hasattr(vacancy.salary, "salary_from"):
                    salary_from = vacancy.salary.salary_from
                    salary_to = vacancy.salary.salary_to
                    salary_currency = vacancy.salary.currency

            # Поиск ID компании
            company_id = self._find_company_id(vacancy, company_mapping)

            # Обработка области
            area = normalize_area_data(vacancy.area) if vacancy.area else None

            # Обработка поля опыта - преобразуем объект Experience в строку
            experience_str = None
            if vacancy.experience:
                if hasattr(vacancy.experience, "get_name"):
                    experience_str = vacancy.experience.get_name()
                else:
                    experience_str = str(vacancy.experience)

            # Обработка поля трудоустройства - аналогично
            employment_str = None
            if vacancy.employment:
                if hasattr(vacancy.employment, "get_name"):
                    employment_str = vacancy.employment.get_name()
                else:
                    employment_str = str(vacancy.employment)

            # Обработка поля графика - аналогично
            schedule_str = None
            if vacancy.schedule:
                if hasattr(vacancy.schedule, "get_name"):
                    schedule_str = vacancy.schedule.get_name()
                else:
                    schedule_str = str(vacancy.schedule)

            # Обработка даты публикации
            published_at = None
            if vacancy.published_at:
                if hasattr(vacancy.published_at, "isoformat"):
                    published_at = vacancy.published_at
                elif isinstance(vacancy.published_at, str):
                    try:
                        from datetime import datetime

                        published_at = datetime.fromisoformat(vacancy.published_at.replace("Z", "+00:00"))
                    except Exception:
                        published_at = None

            return (
                vacancy.vacancy_id,
                vacancy.title,
                vacancy.url,
                salary_from,
                salary_to,
                salary_currency,
                vacancy.description,
                vacancy.requirements,
                vacancy.responsibilities,
                experience_str,
                employment_str,
                schedule_str,
                area,
                vacancy.source,
                published_at,
                company_id,
                search_query,
            )

        except Exception as e:
            logger.error(f"Ошибка подготовки данных вакансии: {e}")
            return None

    def save_vacancies(self, vacancies: Union[Vacancy, List[Vacancy]]) -> int:
        """
        Обратно совместимый метод сохранения
        Заменяет одноименный метод в postgres_saver
        """
        if not isinstance(vacancies, list):
            vacancies = [vacancies]

        messages = self.add_vacancy_batch_optimized(vacancies, search_query="")
        return len(messages)

    def load_vacancies(
        self, limit: Optional[int] = None, offset: int = 0, filters: Optional[Dict[str, Any]] = None
    ) -> List[Vacancy]:
        """
        Загрузка вакансий с поддержкой пагинации и фильтров
        Заменяет одноименный метод в postgres_saver
        """
        try:
            # Для обратной совместимости используем методы DBManager
            all_vacancies_data = self.db_manager.get_all_vacancies()

            # Преобразуем в объекты Vacancy (обратная совместимость)
            vacancies = []
            for data in all_vacancies_data:
                try:
                    vacancy = self._convert_dict_to_vacancy(data)
                    if vacancy:
                        vacancies.append(vacancy)
                except Exception as e:
                    logger.warning(f"Ошибка преобразования данных вакансии: {e}")

            # Применяем пагинацию
            if offset > 0:
                vacancies = vacancies[offset:]
            if limit:
                vacancies = vacancies[:limit]

            return vacancies

        except Exception as e:
            logger.error(f"Ошибка загрузки вакансий: {e}")
            return []

    def _convert_dict_to_vacancy(self, data: Dict[str, Any]) -> Optional[Vacancy]:
        """Преобразует словарь в объект Vacancy"""
        try:
            # Обрабатываем зарплату
            salary_data = None
            salary_info = data.get("salary_info", "")
            if salary_info and salary_info != "Не указана":
                # Парсим строку с зарплатой из БД
                import re

                salary_match = re.findall(r"\d+", salary_info)
                if salary_match:
                    if len(salary_match) >= 2:
                        salary_data = {"from": int(salary_match[0]), "to": int(salary_match[1]), "currency": "RUR"}
                    elif len(salary_match) == 1:
                        if "от" in salary_info:
                            salary_data = {"from": int(salary_match[0]), "currency": "RUR"}
                        else:
                            salary_data = {"to": int(salary_match[0]), "currency": "RUR"}

            # Обрабатываем работодателя
            from src.vacancies.models import Employer

            employer = None
            company_name = data.get("company_name")
            if company_name and company_name != "Неизвестная компания":
                employer = Employer(name=company_name, id=None, trusted=False, alternate_url=None)

            from datetime import datetime

            vacancy = Vacancy(
                vacancy_id=data.get("vacancy_id", ""),  # используем реальное имя поля
                name=data.get("title", ""),  # используем реальное имя поля
                alternate_url=data.get("url", ""),  # используем реальное имя поля
                salary=salary_data,
                description=data.get("description", ""),
                requirements=data.get("requirements", ""),
                responsibilities=data.get("responsibilities", ""),
                experience=data.get("experience") or None,
                employment=data.get("employment") or None,
                schedule=data.get("schedule") or None,
                employer=employer,
                source=data.get("source", ""),
                published_at=data.get("published_at"),
                updated_at=datetime.now(),
                area=data.get("area"),
                company_id=data.get("raw_company_id"),
            )

            # Дополнительные поля
            vacancy.area = data.get("area")
            if "raw_company_id" in data:
                vacancy.company_id = data["raw_company_id"]
            if company_name:
                vacancy.company_name = company_name

            return vacancy

        except Exception as e:
            logger.error(f"Ошибка преобразования в объект Vacancy: {e}")
            return None

    def get_vacancies_count(self) -> int:
        """Получает общее количество вакансий"""
        try:
            with self.db_manager._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM vacancies")
                    result = cursor.fetchone()
                    return int(result[0]) if result and result[0] is not None else 0
        except Exception as e:
            logger.error(f"Ошибка получения количества вакансий: {e}")
            return 0

    # Делегируем остальные методы к DBManager
    def create_tables(self) -> bool:
        """Создает таблицы"""
        return self.db_manager.create_tables()

    def populate_companies_table(self) -> bool:
        """Заполняет таблицу компаний"""
        return self.db_manager.populate_companies_table()

    def get_companies_and_vacancies_count(self) -> List[Tuple[Any, ...]]:
        """Получает статистику по компаниям"""
        return self.db_manager.get_companies_and_vacancies_count()

    def check_connection(self) -> bool:
        """Проверяет подключение к БД"""
        return self.db_manager.check_connection()

    def get_vacancies(self, filters: Optional[Dict[str, Any]] = None) -> List[Vacancy]:
        """
        Получает вакансии из хранилища с фильтрами
        Реализует абстрактный метод
        """
        return self.load_vacancies(filters=filters)

    def delete_vacancy(self, vacancy_id: str) -> bool:
        """
        Удаляет вакансию по ID
        Реализует абстрактный метод
        """
        try:
            with self.db_manager._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM vacancies WHERE vacancy_id = %s", (vacancy_id,))
                    deleted_count = cursor.rowcount
                    connection.commit()
                    return bool(deleted_count > 0)
        except Exception as e:
            logger.error(f"Ошибка удаления вакансии {vacancy_id}: {e}")
            return False

    def update_vacancy(self, vacancy_id: str, updates: Dict[str, Any]) -> bool:
        """
        Обновляет вакансию по ID
        Реализует абстрактный метод
        """
        if not updates:
            return False

        try:
            # Формируем SET часть запроса
            set_parts = []
            params = []
            for key, value in updates.items():
                set_parts.append(f"{key} = %s")
                params.append(value)

            if not set_parts:
                return False

            params.append(vacancy_id)
            query = (
                f"UPDATE vacancies SET {', '.join(set_parts)}, updated_at = CURRENT_TIMESTAMP WHERE vacancy_id = %s"
            )

            with self.db_manager._get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    updated_count = cursor.rowcount
                    connection.commit()
                    return bool(updated_count > 0)
        except Exception as e:
            logger.error(f"Ошибка обновления вакансии {vacancy_id}: {e}")
            return False

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Получает статистику хранилища
        Реализует абстрактный метод
        """
        try:
            total_vacancies = self.get_vacancies_count()
            companies_stats = self.get_companies_and_vacancies_count()

            return {
                "total_vacancies": total_vacancies,
                "total_companies": len(companies_stats),
                "companies_stats": companies_stats,
                "connection_status": self.check_connection(),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики хранилища: {e}")
            return {
                "total_vacancies": 0,
                "total_companies": 0,
                "companies_stats": [],
                "connection_status": False,
                "error": str(e),
            }
