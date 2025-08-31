"""
Медиатор для координации операций с вакансиями

Упрощает UserInterface от логики координации между компонентами
"""

import logging
from typing import List

from src.api_modules.unified_api import UnifiedAPI
from src.ui_interfaces.source_selector import SourceSelector
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.utils.ui_helpers import confirm_action, get_user_input
from src.utils.vacancy_formatter import VacancyFormatter
from src.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class VacancyOperationsCoordinator:
    """
    Медиатор для координации операций с вакансиями

    Упрощает UserInterface от сложной логики координации между компонентами.
    Централизует взаимодействие между поиском, отображением и сохранением вакансий.
    """

    def __init__(self, unified_api: UnifiedAPI, storage):
        """
        Инициализация координатора

        Args:
            unified_api: Унифицированный API для работы с источниками
            storage: Хранилище данных
        """
        self.unified_api = unified_api
        self.storage = storage
        self.source_selector = SourceSelector()

        # Инициализируем обработчики
        self.search_handler = VacancySearchHandler(unified_api, storage)
        self.display_handler = VacancyDisplayHandler(storage)

    def handle_vacancy_search(self) -> None:
        """Координирует полный процесс поиска вакансий"""
        self.search_handler.search_vacancies()

    def handle_show_saved_vacancies(self) -> None:
        """Координирует отображение сохраненных вакансий"""
        self.display_handler.show_all_saved_vacancies()

    def handle_top_vacancies_by_salary(self) -> None:
        """Координирует получение топ вакансий по зарплате"""
        self.display_handler.show_top_vacancies_by_salary()

    def handle_search_saved_by_keyword(self) -> None:
        """Координирует поиск в сохраненных вакансиях"""
        self.display_handler.search_saved_vacancies_by_keyword()

    def handle_cache_cleanup(self) -> None:
        """Координирует очистку кэша API"""
        try:
            sources = self.source_selector.get_user_source_choice()
            if not sources:
                return

            self.source_selector.display_sources_info(sources)
            if confirm_action("Вы уверены, что хотите очистить кэш выбранных источников?"):
                # Формируем словарь для очистки кэша
                cache_sources = {"hh": "hh.ru" in sources, "sj": "superjob.ru" in sources}

                self.unified_api.clear_cache(cache_sources)
                print("Кэш выбранных источников успешно очищен.")
            else:
                print("Очистка кэша отменена.")
        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")
            print(f"Ошибка при очистке кэша: {e}")

    def handle_delete_vacancies(self) -> None:
        """Координирует удаление сохраненных вакансий"""
        try:
            vacancies = self.storage.get_vacancies()

            if not vacancies:
                print("Нет сохраненных вакансий для удаления.")
                return

            print(f"\nСохраненных вакансий: {len(vacancies)}")
            print("\nВыберите способ удаления:")
            print("1. Удалить все сохраненные вакансии")
            print("2. Удалить вакансии по ключевому слову")
            print("3. Удалить конкретную вакансию по ID")
            print("0. Отмена")

            choice = input("Ваш выбор: ").strip()

            if choice == "1":
                self._handle_delete_all_vacancies()
            elif choice == "2":
                self._handle_delete_by_keyword(vacancies)
            elif choice == "3":
                self._handle_delete_by_id(vacancies)
            elif choice == "0":
                print("Назад в предыдущее меню.")
            else:
                print("Неверный выбор. Попробуйте снова.")

        except Exception as e:
            logger.error(f"Ошибка при удалении вакансий: {e}")
            print(f"Ошибка при удалении: {e}")

    def _handle_delete_all_vacancies(self) -> None:
        """Обработка удаления всех вакансий"""
        if confirm_action("Вы уверены, что хотите удалить ВСЕ сохраненные вакансии?"):
            if self.storage.delete_all_vacancies():
                print("Все сохраненные вакансии успешно удалены.")
            else:
                print("Ошибка при удалении вакансий.")
        else:
            print("Удаление отменено.")

    def _handle_delete_by_keyword(self, vacancies: List[Vacancy]) -> None:
        """Обработка удаления вакансий по ключевому слову"""
        from src.utils.ui_helpers import filter_vacancies_by_keyword

        keyword = get_user_input("Введите ключевое слово для удаления связанных вакансий: ")
        if not keyword:
            return

        filtered_vacancies = filter_vacancies_by_keyword(vacancies, keyword)
        if not filtered_vacancies:
            print(f"Вакансии с ключевым словом '{keyword}' не найдены.")
            return

        print(f"\nНайдено {len(filtered_vacancies)} вакансий с ключевым словом '{keyword}'")

        # Показываем первые несколько вакансий для подтверждения
        print("\nПример найденных вакансий:")
        for i, vacancy in enumerate(filtered_vacancies[:5], 1):
            print(f"{i}. ID: {vacancy.vacancy_id}")
            print(f"   Название: {vacancy.title or 'Не указано'}")
            if vacancy.employer:
                if isinstance(vacancy.employer, dict):
                    print(f"   Компания: {vacancy.employer.get('name', 'Неизвестная компания')}")
                else:
                    print(f"   Компания: {vacancy.employer}")
            print(f"   Ссылка: {vacancy.url}")
            print("-" * 40)
        if len(filtered_vacancies) > 5:
            print(f"... и еще {len(filtered_vacancies) - 5} вакансий")

        if confirm_action(f"Удалить {len(filtered_vacancies)} вакансий?"):
            # Удаляем вакансии по ID (batch операция)
            vacancy_ids = [v.vacancy_id for v in filtered_vacancies]
            deleted_count = self.storage.delete_vacancies_batch(vacancy_ids)
            if deleted_count > 0:
                print(f"Удалено {deleted_count} вакансий.")
            else:
                print("Не удалось удалить вакансии.")
        else:
            print("Удаление отменено.")

    def _handle_delete_by_id(self, vacancies: List[Vacancy]) -> None:
        """Обработка удаления вакансии по ID"""
        print("\nДля просмотра ID вакансий используйте пункт 2 (Показать все сохраненные вакансии)")
        vacancy_id = get_user_input("Введите полный ID вакансии для удаления: ")
        if not vacancy_id:
            return

        # Найдем вакансию для подтверждения
        vacancy_to_delete = None
        for vacancy in vacancies:
            if vacancy.vacancy_id == vacancy_id:
                vacancy_to_delete = vacancy
                break

        if vacancy_to_delete:
            self._show_vacancy_for_confirmation(vacancy_to_delete)

            if confirm_action("Удалить эту вакансию?"):
                if self.storage.delete_vacancy_by_id(vacancy_id):
                    print("Вакансия успешно удалена.")
                else:
                    print("Ошибка при удалении вакансии.")
            else:
                print("Удаление отменено.")
        else:
            print("Вакансия с указанным ID не найдена.")

    def _show_vacancy_for_confirmation(self, vacancy: Vacancy) -> None:
        """Показать информацию о вакансии для подтверждения удаления"""
        print("\nВакансия для удаления:")
        formatter = VacancyFormatter()
        print(formatter.format_vacancy_info(vacancy))

    @staticmethod
    def handle_superjob_setup() -> None:
        """Координирует настройку SuperJob API"""
        import os

        print("\n" + "=" * 60)
        print("НАСТРОЙКА SUPERJOB API")
        print("=" * 60)

        current_key = os.getenv("SUPERJOB_API_KEY")
        if current_key and current_key != "v3.r.137440105.example.test_tool":
            print("SuperJob API ключ уже настроен")
        else:
            print("SuperJob API ключ не настроен или используется тестовый")

        print("\nДля получения API ключа SuperJob:")
        print("1. Перейдите на https://api.superjob.ru/register/")
        print("2. Зарегистрируйте ваше приложение")
        print("3. Получите Secret key")
        print("4. Добавьте его в Secrets как SUPERJOB_API_KEY")
        print("\nИнструкция по добавлению секретов:")
        print("• Откройте панель Secrets в левом меню")
        print("• Нажмите 'New Secret'")
        print("• Введите Key: SUPERJOB_API_KEY")
        print("• Введите Value: ваш настоящий API ключ")
        print("• Нажмите 'Add Secret'")
        print("• Перезапустите приложение")
        print("\n" + "=" * 60)

        input("\nНажмите Enter для продолжения...")

    def get_vacancies_from_sources(self, search_query: str, sources: List[str], **kwargs) -> List[Vacancy]:
        """
        Получение вакансий из выбранных источников

        Args:
            search_query: Поисковый запрос
            sources: Список источников для поиска
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Vacancy]: Список найденных вакансий
        """
        try:
            # Получаем данные через унифицированный API
            vacancy_data = self.unified_api.get_vacancies_from_sources(
                search_query=search_query, sources=sources, **kwargs
            )

            # Конвертируем в объекты Vacancy
            vacancies = [Vacancy.from_dict(data) for data in vacancy_data]

            if vacancies:
                # Сохраняем найденные вакансии
                update_messages = self.storage.add_vacancy(vacancies)

                # Получаем реальное количество вакансий в БД после сохранения
                total_in_db = len(self.storage.get_vacancies())

                if update_messages:
                    # Показываем детали операций
                    for message in update_messages[:10]:  # Показываем первые 10
                        print(f"  • {message}")

                    if len(update_messages) > 10:
                        remaining = len(update_messages) - 10
                        print(f"  • ... и еще {remaining} операций")

                print(f"Общее количество вакансий в базе данных: {total_in_db}")

            return vacancies

        except Exception as e:
            logger.error(f"Ошибка при получении вакансий из источников: {e}")
            return []

    def get_vacancies_from_target_companies(
        self, search_query: str = "", sources: List[str] = None, **kwargs
    ) -> List[Vacancy]:
        """
        Получение вакансий только от целевых компаний

        Args:
            search_query: Поисковый запрос (опционально)
            sources: Список источников для поиска
            **kwargs: Дополнительные параметры поиска

        Returns:
            List[Vacancy]: Список найденных вакансий от целевых компаний
        """
        try:
            # Получаем данные через унифицированный API
            vacancy_data = self.unified_api.get_vacancies_from_target_companies(
                search_query=search_query, sources=sources, **kwargs
            )

            # Конвертируем в объекты Vacancy
            vacancies = [Vacancy.from_dict(data) for data in vacancy_data]

            if vacancies:
                # Сохраняем найденные вакансии
                update_messages = self.storage.add_vacancy(vacancies)

                # Получаем реальное количество вакансий в БД после сохранения
                total_in_db = len(self.storage.get_vacancies())

                if update_messages:
                    # Показываем детали операций
                    for message in update_messages[:10]:  # Показываем первые 10
                        print(f"  • {message}")

                    if len(update_messages) > 10:
                        remaining = len(update_messages) - 10
                        print(f"  • ... и еще {remaining} операций")

                print(f"Общее количество вакансий в базе данных: {total_in_db}")

            return vacancies

        except Exception as e:
            logger.error(f"Ошибка при получении вакансий от целевых компаний: {e}")
            return []
