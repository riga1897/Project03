"""
Медиатор для координации операций с вакансиями

Упрощает UserInterface от логики координации между компонентами
"""

import logging
from typing import Any, List, Optional

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

    def __init__(self, unified_api: UnifiedAPI, storage: Any):
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
            print(f"{i}. ID: {vacancy.id}")
            print(f"   Название: {vacancy.title or 'Не указано'}")
            if vacancy.employer:
                if isinstance(vacancy.employer, dict):
                    print(f"   Компания: {vacancy.employer.get('name', 'Неизвестная компания')}")
                elif hasattr(vacancy.employer, "name"):
                    print(f"   Компания: {vacancy.employer.name}")
                else:
                    print(f"   Компания: {str(vacancy.employer)}")
            print(f"   Ссылка: {vacancy.url}")
            print("-" * 40)
        if len(filtered_vacancies) > 5:
            print(f"... и еще {len(filtered_vacancies) - 5} вакансий")

        if confirm_action(f"Удалить {len(filtered_vacancies)} вакансий?"):
            # Удаляем вакансии по ID (batch операция)
            vacancy_ids = [v.id for v in filtered_vacancies]
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
            if vacancy.id == vacancy_id:
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
        print("4. Добавьте его в .env как SUPERJOB_API_KEY")
        print("\nПерезапустите приложение")
        print("\n" + "=" * 60)

        input("\nНажмите Enter для продолжения...")

    def get_vacancies_from_sources(self, search_query: str, sources: List[str], **kwargs: Any) -> List[Vacancy]:
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

            if not vacancy_data:
                print("Не удалось получить данные вакансий от API")
                return []

            # Конвертируем в объекты Vacancy с обработкой ошибок
            vacancies = []
            conversion_errors = 0

            for data in vacancy_data:
                try:
                    vacancy = Vacancy.from_dict(data)
                    vacancies.append(vacancy)
                except Exception as e:
                    conversion_errors += 1
                    logger.error(f"Ошибка конвертации вакансии: {e}")
                    continue

            if conversion_errors > 0:
                print(f"Не удалось конвертировать {conversion_errors} вакансий")

            if vacancies:
                print(f"Успешно конвертировано {len(vacancies)} вакансий в объекты Vacancy")
            else:
                print("Не удалось создать объекты вакансий из полученных данных")

            return vacancies

        except Exception as e:
            logger.error(f"Ошибка при получении вакансий из источников: {e}")
            print(f"Общая ошибка получения вакансий: {e}")
            return []

    def _display_post_processing_stats(self, vacancies: List[Vacancy], sources: Optional[List[str]]) -> None:
        """
        Показывает статистику ПОСЛЕ создания объектов Vacancy с правильными названиями компаний
        
        Args:
            vacancies: Готовые объекты Vacancy
            sources: Источники данных
        """
        try:
            from src.utils.vacancy_stats import VacancyStats
            
            # Определяем название для статистики
            if sources and len(sources) == 1:
                if sources[0].lower() in ["hh", "hh.ru", "headhunter"]:
                    source_name = "HH.ru - Целевые компании"
                elif sources[0].lower() in ["sj", "superjob", "superjob.ru"]:
                    source_name = "SuperJob - Целевые компании"
                else:
                    source_name = f"{sources[0].upper()} - Целевые компании"
            else:
                source_name = "Все источники - Целевые компании"
            
            stats = VacancyStats()
            stats.display_company_stats(vacancies, source_name)
            
        except Exception as e:
            logger.warning(f"Ошибка при отображении статистики после обработки: {e}")

    def get_vacancies_from_target_companies(
        self, search_query: str = "", sources: Optional[List[str]] = None, **kwargs: Any
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

            if not vacancy_data:
                print("API не вернул данных о вакансиях")
                return []

            print(f"API вернул {len(vacancy_data)} записей о вакансиях")

            # ИСПРАВЛЕНО: Обрабатываем данные через парсеры перед созданием объектов
            vacancies = []
            conversion_errors = 0

            # Разделяем данные по источникам для правильной обработки
            hh_data = [
                item
                for item in vacancy_data
                if item.get("source") == "hh.ru" or "api.hh.ru" in str(item.get("url", ""))
            ]
            sj_data = [
                item
                for item in vacancy_data
                if item.get("source") == "superjob.ru" or "superjob.ru" in str(item.get("url", ""))
            ]

            # Обрабатываем HH данные через HHParser
            if hh_data:
                try:
                    from src.vacancies.parsers.hh_parser import HHParser

                    hh_parser = HHParser()
                    hh_vacancies = hh_parser.parse_vacancies(hh_data)
                    vacancies.extend(hh_vacancies)
                    logger.info(f"Обработано {len(hh_vacancies)} вакансий HH через парсер")
                except Exception as e:
                    logger.error(f"Ошибка обработки HH данных через парсер: {e}")

            # Обрабатываем SJ данные через SJParser
            if sj_data:
                try:
                    from src.vacancies.parsers.sj_parser import SuperJobParser

                    sj_parser = SuperJobParser()
                    sj_vacancies = sj_parser.parse_vacancies(sj_data)
                    vacancies.extend(sj_vacancies)
                    logger.info(f"Обработано {len(sj_vacancies)} вакансий SJ через парсер")
                except Exception as e:
                    logger.error(f"Ошибка обработки SJ данных через парсер: {e}")

            # Если остались необработанные данные (другие источники), пытаемся создать через from_dict
            other_data = [item for item in vacancy_data if item not in hh_data and item not in sj_data]
            for data in other_data:
                try:
                    vacancy = Vacancy.from_dict(data)
                    vacancies.append(vacancy)
                except Exception as e:
                    conversion_errors += 1
                    logger.error(f"Ошибка конвертации вакансии: {e}")
                    continue

            if conversion_errors > 0:
                print(f"Не удалось конвертировать {conversion_errors} вакансий")

            if vacancies:
                print(f"Успешно конвертировано {len(vacancies)} вакансий в объекты Vacancy")
                
                # ИСПРАВЛЕНО: Показываем статистику ПОСЛЕ создания объектов с правильными названиями
                self._display_post_processing_stats(vacancies, sources)
            else:
                print("Не удалось создать объекты вакансий из полученных данных")

            return vacancies

        except Exception as e:
            logger.error(f"Ошибка при получении вакансий от целевых компаний: {e}")
            print(f"Общая ошибка получения вакансий: {e}")
            return []
