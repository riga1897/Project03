import logging
from typing import List, Optional

from src.api_modules.unified_api import UnifiedAPI
from src.storage.json_saver import JSONSaver
from src.storage.postgresql_storage import PostgreSQLStorage
from src.ui_interfaces.source_selector import SourceSelector
from src.utils.ui_helpers import confirm_action, get_user_input
from src.utils.ui_navigation import quick_paginate
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class VacancySearchHandler:
    """
    Обработчик операций поиска вакансий

    Отвечает за логику поиска вакансий через API,
    их отображение и сохранение.
    """

    def __init__(self, unified_api: UnifiedAPI, storage: PostgreSQLStorage):
        """
        Инициализация обработчика поиска

        Args:
            unified_api: Унифицированный API для получения вакансий
            storage: Сервис сохранения данных (PostgreSQLStorage)
        """
        self.unified_api = unified_api
        self.storage = storage  # Используем PostgreSQLStorage
        self.source_selector = SourceSelector()

    def search_vacancies(self) -> None:
        """Поиск вакансий по запросу пользователя"""
        # Выбор источников
        sources = self.source_selector.get_user_source_choice()
        if not sources:
            return

        self.source_selector.display_sources_info(sources)

        # Ввод поискового запроса
        query = get_user_input("\nВведите поисковый запрос: ")
        if not query:
            return

        # Выбор периода
        period = self._get_period_choice()
        if period is None:
            return

        print(f"\nИщем вакансии от целевых компаний по запросу: '{query}' за последние {period} дней...")

        # Получение вакансий
        try:
            all_vacancies = self._fetch_vacancies_from_sources(sources, query, period)

            if not all_vacancies:
                print("Вакансии не найдены ни на одном из источников.")
                return

            print(f"\nВсего найдено {len(all_vacancies)} вакансий")

            # Обработка результатов
            self._handle_search_results(all_vacancies, query)

        except Exception as e:
            logger.error(f"Ошибка поиска вакансий: {e}")
            print(f"Произошла ошибка при поиске: {e}")

    def _fetch_vacancies_from_sources(self, sources: set, query: str, period: int) -> List[Vacancy]:
        """
        Получение вакансий из выбранных источников только от целевых компаний

        Args:
            sources: Множество выбранных источников
            query: Поисковый запрос
            period: Период поиска в днях

        Returns:
            List[Vacancy]: Список найденных вакансий от целевых компаний
        """
        print("Поиск вакансий только от целевых компаний...")

        # Конвертируем set в list для передачи в UnifiedAPI
        sources_list = list(sources)

        # Получаем вакансии от целевых компаний через унифицированный API
        try:
            vacancies_data = self.unified_api.get_vacancies_from_target_companies(
                search_query=query,
                sources=sources_list,
                period=period
            )

            # Конвертируем Dict обратно в объекты Vacancy
            from src.vacancies.models import Vacancy
            all_vacancies = [Vacancy.from_dict(item) for item in vacancies_data]

            if all_vacancies:
                print(f"Найдено {len(all_vacancies)} вакансий от целевых компаний")
            else:
                print("Вакансии от целевых компаний не найдены")

            return all_vacancies

        except Exception as e:
            print(f"Ошибка получения вакансий от целевых компаний: {e}")
            return []

    def _handle_search_results(self, vacancies: List[Vacancy], query: str) -> None:
        """
        Обработка результатов поиска - отображение и сохранение

        Args:
            vacancies: Список найденных вакансий
            query: Поисковый запрос
        """
        self._handle_vacancies_preview_and_save(vacancies, query)

    def _handle_vacancies_preview_and_save(self, vacancies: List[Vacancy], query: str) -> None:
        """
        Обработка предпросмотра и сохранения вакансий

        Args:
            vacancies: Список найденных вакансий
            query: Поисковый запрос
        """
        # Проверяем, какие вакансии уже есть в базе
        duplicate_info = self._check_existing_vacancies(vacancies)

        # Выводим информацию о дублях
        self._display_duplicate_info(duplicate_info)

        # Предпросмотр вакансий
        show_vacancies = confirm_action("Показать найденные вакансии?")
        if show_vacancies:

            def format_vacancy(vacancy: Vacancy, number: Optional[int] = None) -> str:
                if vacancy is None:
                    raise ValueError("Received a vacancy object of None type.")
                return VacancyFormatter.format_vacancy_info(vacancy, number)

            quick_paginate(
                vacancies,
                formatter=format_vacancy,
                header=f"Найденные вакансии от целевых компаний по запросу '{query}'",
                items_per_page=5,
            )

        # Предлагаем сохранить только новые вакансии
        if duplicate_info["new_vacancies"]:
            if confirm_action(f"Сохранить {len(duplicate_info['new_vacancies'])} новых вакансий?"):
                self._save_vacancies(duplicate_info["new_vacancies"])
            else:
                print("Новые вакансии не сохранены")
        elif duplicate_info["total_count"] > 0:
            print("Нет новых вакансий для сохранения.")

    def _save_vacancies(self, vacancies: List[Vacancy]) -> None:
        """
        Сохранение вакансий в хранилище

        Args:
            vacancies: Список вакансий для сохранения
        """
        # Сохраняем новые вакансии оптимизированным методом
        update_messages = self.storage.add_vacancy_batch_optimized(vacancies)

        for message in update_messages:
            print(f"  • {message}")

        print()  # Пустая строка для лучшего форматирования

    def _check_existing_vacancies(self, vacancies: List[Vacancy]) -> dict:
        """
        Проверяет, какие из вакансий уже есть в базе данных.

        Args:
            vacancies: Список вакансий для проверки.

        Returns:
            dict: Словарь с информацией о дубликатах и новых вакансиях
        """
        if not vacancies:
            return {
                "total_count": 0,
                "duplicates": [],
                "new_vacancies": [],
                "duplicate_count": 0,
                "new_count": 0
            }

        print(f"Проверка {len(vacancies)} вакансий на дубликаты...")

        # Используем batch-метод для проверки дубликатов
        existence_map = self.storage.check_vacancies_exist_batch(vacancies)

        duplicates = []
        new_vacancies = []

        for vacancy in vacancies:
            if existence_map.get(vacancy.vacancy_id, False):
                duplicates.append(vacancy)
            else:
                new_vacancies.append(vacancy)

        return {
            "total_count": len(vacancies),
            "duplicates": duplicates,
            "new_vacancies": new_vacancies,
            "duplicate_count": len(duplicates),
            "new_count": len(new_vacancies)
        }

    @staticmethod
    def _display_duplicate_info(duplicate_info: dict) -> None:
        """
        Выводит информацию о найденных дубликатах вакансий.

        Args:
            duplicate_info: Словарь с информацией о дубликатах.
        """
        total_count = duplicate_info["total_count"]
        duplicate_count = duplicate_info["duplicate_count"]
        new_count = duplicate_info["new_count"]

        if total_count == 0:
            print("Не найдено ни одной вакансии.")
            return

        if duplicate_count == total_count:
            print(f"Все {total_count} вакансий уже существуют в базе данных.")
        elif duplicate_count > 0:
            print(f"{duplicate_count} вакансий из {total_count} уже есть в базе данных.")
            print(f"Можно сохранить {new_count} новых вакансий.")
        else:
            print(f"Все {total_count} вакансий - новые.")

    @staticmethod
    def _get_period_choice() -> Optional[int]:
        """
        Выбор периода публикации вакансий

        Returns:
            Optional[int]: Количество дней для поиска или None при отмене
        """
        try:
            print("\nВыберите период публикации вакансий:")
            print("1. 1 день")
            print("2. 3 дня")
            print("3. 7 дней")
            print("4. 15 дней (по умолчанию)")
            print("5. 30 дней")
            print("6. Ввести свой период")
            print("0. Отмена")

            choice = input("Ваш выбор (по умолчанию 15 дней): ").strip()

            period_map = {"1": 1, "2": 3, "3": 7, "4": 15, "5": 30, "": 15}

            if choice == "0":
                print("Выбор периода отменен.")
                return None
            elif choice in period_map:
                return period_map[choice]
            elif choice == "6":
                try:
                    custom_period = int(input("Введите количество дней (1-365): "))
                    if 1 <= custom_period <= 365:
                        return custom_period
                    else:
                        print("Некорректный период. Используется 15 дней по умолчанию.")
                        return 15
                except ValueError:
                    print("Некорректный ввод. Используется 15 дней по умолчанию.")
                    return 15
            else:
                print("Некорректный выбор. Используется 15 дней по умолчанию.")
                return 15

        except KeyboardInterrupt:
            print("\nВыбор периода отменен.")
            return None