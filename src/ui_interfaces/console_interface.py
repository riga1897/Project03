import logging
from typing import List, Optional

from src.api_modules.unified_api import UnifiedAPI
from src.config.ui_config import ui_pagination_config
from src.storage.storage_factory import StorageFactory
from src.ui_interfaces.vacancy_display_handler import VacancyDisplayHandler
from src.ui_interfaces.vacancy_search_handler import VacancySearchHandler
from src.utils.menu_manager import create_main_menu, print_menu_separator, print_section_header
from src.utils.ui_helpers import confirm_action, display_vacancy_info, get_user_input, parse_salary_range
from src.utils.ui_navigation import quick_paginate
from src.utils.vacancy_formatter import VacancyFormatter
from src.utils.vacancy_operations import VacancyOperations
from src.vacancies.models import Vacancy

# from src.storage.json_saver import JSONSaver # Удален JSONSaver


# Импортируем DBManager и DBManagerDemo для демонстрации
try:
    from src.storage.db_manager import DBManager
    from src.utils.db_manager_demo import DBManagerDemo
except ImportError:
    DBManager = None
    DBManagerDemo = None


logger = logging.getLogger(__name__)


class UserInterface:
    """
    Класс для взаимодействия с пользователем через консоль

    Теперь использует принцип единственной ответственности -
    только управляет навигацией по меню и делегирует операции
    специализированным обработчикам.
    """

    def __init__(self, storage=None, db_manager=None):
        """Инициализация пользовательского интерфейса"""
        # Removed unused import: AppConfig
        # Removed unused import: VacancyOperationsCoordinator

        self.unified_api = UnifiedAPI()

        # Инициализация хранилища
        if storage is None:
            storage = StorageFactory.get_default_storage()
        self.storage = storage

        # Инициализируем только PostgreSQL хранилище
        self.db_storage = self.storage

        self.menu_manager = create_main_menu()
        self.vacancy_ops = VacancyOperations()

        # Инициализация обработчиков
        self.search_handler = VacancySearchHandler(self.unified_api, self.storage)
        self.display_handler = VacancyDisplayHandler(self.storage)
        # Removed unused import: VacancyOperationsCoordinator
        from src.ui_interfaces.vacancy_operations_coordinator import VacancyOperationsCoordinator

        self.operations_coordinator = VacancyOperationsCoordinator(self.unified_api, self.storage)

        # DB Manager для демонстрации
        self.db_manager = db_manager
        if self.db_manager and DBManagerDemo:
            self.demo = DBManagerDemo(self.db_manager)
        else:
            self.demo = None

    def run(self) -> None:
        """Основной цикл взаимодействия с пользователем"""
        print_section_header("Добро пожаловать в поисковик вакансий!")

        while True:
            try:
                choice = self._show_menu()

                if choice == "1":
                    self._search_vacancies()
                elif choice == "2":
                    self._show_saved_vacancies()
                elif choice == "3":
                    self._get_top_saved_vacancies_by_salary()
                elif choice == "4":
                    self._search_saved_vacancies_by_keyword()
                elif choice == "5":
                    self._advanced_search_vacancies()
                elif choice == "6":
                    self._filter_saved_vacancies_by_salary()
                elif choice == "7":
                    self._delete_saved_vacancies()  # Изменено: используется operations_coordinator

                elif choice == "8":
                    self._clear_api_cache()

                elif choice == "9":
                    self._configure_superjob_api()
                elif choice == "10":
                    if self.db_manager and self.demo:
                        print("\n" + "=" * 60)
                        print("ДЕМОНСТРАЦИЯ DBMANAGER")
                        print("=" * 60)
                        self.demo.run_full_demo()
                        print("=" * 60)
                    else:
                        print("\nБаза данных недоступна. Демонстрация DBManager невозможна.")
                        print("Проверьте подключение к PostgreSQL и перезапустите приложение.")

                elif choice == "0":
                    print("Спасибо за использование! До свидания!")
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")

            except KeyboardInterrupt:
                print("\n\nРабота прервана пользователем. До свидания!")
                break
            except Exception as e:
                logger.error(f"Ошибка в пользовательском интерфейсе: {e}")
                print(f"Произошла ошибка: {e}")
                # Добавляем небольшую задержку чтобы избежать бесконечного цикла ошибок
                import time

                time.sleep(0.1)

    def _show_menu(self) -> str:
        """
        Отображение главного меню

        Returns:
            str: Выбор пользователя
        """
        print("\n")
        print_menu_separator()
        print("Выберите действие:")
        print("1. Поиск вакансий по запросу (выбор источника + запрос к API)")
        print("2. Показать все сохраненные вакансии")
        print("3. Топ N сохраненных вакансий по зарплате")
        print("4. Поиск в сохраненных вакансиях по ключевому слову")
        print("5. Расширенный поиск (несколько ключевых слов)")
        print("6. Фильтр сохраненных вакансий по зарплате")
        print("7. Удалить сохраненные вакансии")
        print("8. Очистить кэш API")
        print("9. Настройка SuperJob API")
        if DBManager and DBManagerDemo:
            print("10. Демонстрация DBManager (анализ данных в БД)")
        print("0. Выход")
        print_menu_separator()

        return input("Ваш выбор: ").strip()

    def _search_vacancies(self) -> None:
        """Поиск вакансий по запросу пользователя"""
        self.operations_coordinator.handle_vacancy_search()  # Изменено: используется operations_coordinator

    def _show_saved_vacancies(self) -> None:
        """Отображение сохраненных вакансий с постраничным просмотром"""
        self.operations_coordinator.handle_show_saved_vacancies()  # Изменено: используется operations_coordinator

    def _get_top_saved_vacancies_by_salary(self) -> None:
        """Получение топ N сохраненных вакансий по зарплате"""
        self.operations_coordinator.handle_top_vacancies_by_salary()  # Изменено: используется operations_coordinator

    def _search_saved_vacancies_by_keyword(self) -> None:
        """Поиск в сохраненных вакансиях с ключевым словом в описании"""
        self.operations_coordinator.handle_search_saved_by_keyword()  # Изменено: используется operations_coordinator

    def _advanced_search_vacancies(self) -> None:
        """Расширенный поиск по вакансиям"""
        try:
            # Используем self.storage для получения вакансий
            vacancies = self.storage.get_vacancies()  # Изменено: используется storage

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            print("\nРасширенный поиск:")
            print("Введите ключевые слова через запятую, пробел или используйте операторы AND/OR")
            print("Примеры:")
            print("  - python django postgresql (поиск по любому из слов)")
            print("  - python, django, postgresql (поиск по любому из слов)")
            print("  - python AND django (поиск по всем словам)")
            print("  - python OR java (поиск по любому из слов)")

            query = get_user_input("Введите поисковый запрос: ")

            if not query:
                return

            # Определяем тип поиска
            if "," in query and " AND " not in query.upper() and " OR " not in query.upper():
                # Поиск по нескольким ключевым словам через запятую
                keywords = [kw.strip() for kw in query.split(",")]
                filtered_vacancies = self.vacancy_ops.filter_vacancies_by_multiple_keywords(vacancies, keywords)
                print(f"\nПоиск по ключевым словам: {', '.join(keywords)}")
            else:
                # Продвинутый поиск с операторами
                filtered_vacancies = self.vacancy_ops.search_vacancies_advanced(vacancies, query)
                print(f"\nРезультаты поиска по запросу: '{query}'")

            if not filtered_vacancies:
                print("Вакансии по указанным критериям не найдены.")
                return

            print(f"Найдено {len(filtered_vacancies)} вакансий:")

            # Постраничный просмотр
            # Создаем экземпляр VacancyFormatter
            vacancy_formatter = VacancyFormatter()

            quick_paginate(
                filtered_vacancies,
                formatter=vacancy_formatter.format_vacancy_info,
                header="Результаты расширенного поиска",
                items_per_page=ui_pagination_config.get_items_per_page("search"),
            )

        except Exception as e:
            logger.error(f"Ошибка при расширенном поиске: {e}")
            print(f"Ошибка при поиске: {e}")

    def _filter_saved_vacancies_by_salary(self) -> None:
        """Фильтрация сохраненных вакансий по зарплате"""
        try:
            # Используем self.storage для получения вакансий
            vacancies = self.storage.get_vacancies()  # Изменено: используется storage

            if not vacancies:
                print("Нет сохраненных вакансий.")
                return

            print("\nВыберите тип фильтрации:")
            print("1. Минимальная зарплата")
            print("2. Максимальная зарплата")
            print("3. Диапазон зарплат")

            choice = input("Ваш выбор: ").strip()

            # filtered_vacancies = []

            if choice == "1":
                try:
                    min_salary = int(input("Введите минимальную зарплату: "))
                    filtered_vacancies = self.vacancy_ops.filter_vacancies_by_min_salary(vacancies, min_salary)
                    print(f"\nВакансии с зарплатой от {min_salary} руб.:")
                except ValueError:
                    print("Введите корректное число!")
                    return

            elif choice == "2":
                try:
                    max_salary = int(input("Введите максимальную зарплату: "))
                    filtered_vacancies = self.vacancy_ops.filter_vacancies_by_max_salary(vacancies, max_salary)
                    print(f"\nВакансии с зарплатой до {max_salary} руб.:")
                except ValueError:
                    print("Введите корректное число!")
                    return

            elif choice == "3":
                salary_range = input("Введите диапазон зарплат (пример: 100000 - 150000): ").strip()
                parsed_range = parse_salary_range(salary_range)
                if parsed_range:
                    min_salary, max_salary = parsed_range
                    filtered_vacancies = self.vacancy_ops.filter_vacancies_by_salary_range(
                        vacancies, min_salary, max_salary
                    )
                    print(f"\nВакансии с зарплатой в диапазоне {min_salary} - {max_salary} руб.:")
                else:
                    return

            else:
                print("Неверный выбор.")
                return

            if not filtered_vacancies:
                print("Вакансии с указанными критериями зарплаты не найдены.")
                return

            # Сортируем по убыванию зарплаты
            sorted_vacancies = self.vacancy_ops.sort_vacancies_by_salary(filtered_vacancies)

            print(f"Найдено {len(sorted_vacancies)} вакансий:")

            # Постраничный просмотр
            # Создаем экземпляр VacancyFormatter
            vacancy_formatter = VacancyFormatter()

            quick_paginate(
                sorted_vacancies,
                formatter=vacancy_formatter.format_vacancy_info,
                header="Вакансии по зарплате",
                items_per_page=ui_pagination_config.get_items_per_page("search"),
            )

        except Exception as e:
            logger.error(f"Ошибка при фильтрации по зарплате: {e}")
            print(f"Ошибка при фильтрации: {e}")

    def _delete_saved_vacancies(self) -> None:
        """Удаление сохраненных вакансий"""
        self.operations_coordinator.handle_delete_vacancies()  # Изменено: используется operations_coordinator

    def _clear_api_cache(self) -> None:
        """Очистка кэша API"""
        self.operations_coordinator.handle_cache_cleanup()  # Изменено: используется operations_coordinator

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

            period_map = {"1": 1, "2": 3, "3": 7, "4": 15, "5": 30, "": 15}  # По умолчанию

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

    def _setup_superjob_api(self) -> None:
        """Настройка SuperJob API"""
        self.operations_coordinator.handle_superjob_setup()  # Изменено: используется operations_coordinator

    @staticmethod
    def _display_vacancies(vacancies: List[Vacancy], start_number: int = 1) -> None:
        """
        Отображение списка вакансий

        Args:
            vacancies: Список вакансий для отображения
            start_number: Начальный номер для нумерации
        """
        for i, vacancy in enumerate(vacancies, start_number):
            display_vacancy_info(vacancy, i)

    @staticmethod
    def _display_vacancies_with_pagination(vacancies: List[Vacancy]) -> None:
        """
        Отображение вакансий с постраничным просмотром

        Args:
            vacancies: Список вакансий для отображения
        """

        def format_vacancy(vacancy, number=None) -> str:
            return VacancyFormatter.format_vacancy_info(vacancy, number)

        quick_paginate(vacancies, formatter=format_vacancy, header="Вакансии", items_per_page=10)

    def _show_vacancies_for_deletion(self, vacancies: List[Vacancy], keyword: str) -> None:
        """
        Отображение вакансий для удаления с возможностью выбора

        Args:
            vacancies: Список вакансий для удаления
            keyword: Ключевое слово для удаления
        """
        page_size = 10
        total_pages = (len(vacancies) + page_size - 1) // page_size
        current_page = 1

        while True:
            # Вычисляем индексы для текущей страницы
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(vacancies))
            current_vacancies = vacancies[start_idx:end_idx]

            print(f"\n--- Страница {current_page} из {total_pages} ---")
            print(f"Вакансии {start_idx + 1}-{end_idx} из {len(vacancies)} с ключевым словом '{keyword}':")
            print("-" * 80)

            # Отображаем вакансии с номерами
            for i, vacancy in enumerate(current_vacancies, start_idx + 1):
                print(f"{i}. ID: {vacancy.id}")
                print(f"   Название: {vacancy.name or 'Не указано'}")
                if vacancy.employer:
                    print(f"   Компания: {vacancy.employer.get('name', 'Не указана')}")
                salary_display = str(vacancy.salary) if vacancy.salary else "Не указана"
                if salary_display != "Зарплата не указана":
                    print(f"   Зарплата: {salary_display}")
                else:
                    print("   Зарплата: Не указана")
                print(f"   Ссылка: {vacancy.url}")
                print("-" * 40)

            # Меню навигации и действий
            print("\n" + "=" * 60)
            print("Действия:")
            print("a - Удалить ВСЕ вакансии с этим ключевым словом")
            print("1-10 - Удалить конкретную вакансию по номеру на странице")
            print("8-9, 2-5 - Удалить диапазон вакансий (например: 8-9)")
            if current_page > 1:
                print("p - Предыдущая страница")
            if current_page < total_pages:
                print("n - Следующая страница")
            print("q - Назад в предыдущее меню.")
            print("=" * 60)

            choice = input("Ваш выбор: ").strip().lower()

            if choice == "q":
                print("Удаление отменено.")
                break
            elif choice == "a":
                if confirm_action(f"Удалить ВСЕ {len(vacancies)} вакансий с ключевым словом '{keyword}'?"):
                    # Используем storage для удаления
                    deleted_count = self.storage.delete_vacancies_by_keyword(keyword)  # Изменено: используется storage
                    if deleted_count > 0:
                        print(f"Удалено {deleted_count} вакансий.")
                    else:
                        print("Не удалось удалить вакансии.")
                break
            elif choice == "n" and current_page < total_pages:
                current_page += 1
            elif choice == "p" and current_page > 1:
                current_page -= 1
            elif "-" in choice and choice not in ["n", "p"]:
                # Обработка диапазона (например: 8-9)
                try:
                    start_str, end_str = choice.split("-", 1)
                    start_num = int(start_str.strip())
                    end_num = int(end_str.strip())

                    if start_num > end_num:
                        start_num, end_num = end_num, start_num

                    if 1 <= start_num <= len(vacancies) and 1 <= end_num <= len(vacancies):
                        # Получаем вакансии для удаления
                        vacancies_to_delete = []
                        for num in range(start_num, end_num + 1):
                            vacancies_to_delete.append(vacancies[num - 1])

                        print(f"\nВакансии для удаления (номера {start_num}-{end_num}):")
                        for i, vacancy in enumerate(vacancies_to_delete, start_num):
                            print(f"{i}. ID: {vacancy.id}")
                            print(f"   Название: {vacancy.name or 'Не указано'}")
                            if vacancy.employer:
                                print(f"   Компания: {vacancy.employer.get('name', 'Не указана')}")
                            print(f"   Ссылка: {vacancy.url}")
                            print("-" * 40)

                        if confirm_action(f"Удалить {len(vacancies_to_delete)} вакансий?"):
                            deleted_count = 0
                            for vacancy in vacancies_to_delete:
                                # Используем storage для удаления
                                if self.storage.delete_vacancy_by_id(
                                    vacancy.id
                                ):  # Изменено: используется storage
                                    vacancies.remove(vacancy)
                                    deleted_count += 1

                            if deleted_count > 0:
                                print(f"Удалено {deleted_count} вакансий.")
                                if not vacancies:
                                    print("Все вакансии с данным ключевым словом удалены.")
                                    break
                                # Пересчитываем страницы
                                total_pages = (len(vacancies) + page_size - 1) // page_size
                                if current_page > total_pages:
                                    current_page = total_pages
                            else:
                                print("Не удалось удалить вакансии.")
                        else:
                            print("Удаление отменено.")
                    else:
                        print(f"Введите диапазон в пределах от 1 до {len(vacancies)}")
                except ValueError:
                    print("Неверный формат диапазона. Используйте формат: 8-9")
            elif choice.isdigit():
                vacancy_num = int(choice)
                if 1 <= vacancy_num <= len(vacancies):
                    vacancy_to_delete = vacancies[vacancy_num - 1]
                    print("\nВакансия для удаления:")
                    print(f"ID: {vacancy_to_delete.id}")
                    print(f"Название: {vacancy_to_delete.title or 'Не указано'}")
                    if vacancy_to_delete.employer:
                        print(f"Компания: {vacancy_to_delete.employer.get('name', 'Не указана')}")
                    salary_display = str(vacancy_to_delete.salary) if vacancy_to_delete.salary else "Не указана"
                    if salary_display != "Зарплата не указана":
                        print(f"Зарплата: {salary_display}")
                    else:
                        print("Зарплата: Не указана")
                    print(f"Ссылка: {vacancy_to_delete.url}")

                    if confirm_action("Удалить эту вакансию?"):
                        # Используем storage для удаления
                        if self.storage.delete_vacancy_by_id(
                            vacancy_to_delete.id
                        ):  # Изменено: используется storage
                            print("Вакансия успешно удалена.")
                            # Удаляем из локального списка и обновляем отображение
                            vacancies.remove(vacancy_to_delete)
                            if not vacancies:
                                print("Все вакансии с данным ключевым словом удалены.")
                                break
                            # Пересчитываем страницы
                            total_pages = (len(vacancies) + page_size - 1) // page_size
                            if current_page > total_pages:
                                current_page = total_pages
                        else:
                            print("Ошибка при удалении вакансии.")
                    else:
                        print("Удаление отменено.")
                else:
                    print(f"Введите номер от 1 до {len(vacancies)}")
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _demo_db_manager(self) -> None:
        """Демонстрация функциональности DBManager"""
        try:
            print("\n" + "=" * 60)
            print("ДЕМОНСТРАЦИЯ КЛАССА DBManager")
            print("=" * 60)
            print("Этот раздел демонстрирует специфические методы для работы с БД PostgreSQL")
            print("согласно требованиям проекта:")
            print("• get_companies_and_vacancies_count()")
            print("• get_all_vacancies()")
            print("• get_avg_salary()")
            print("• get_vacancies_with_higher_salary()")
            print("• get_vacancies_with_keyword()")
            print("=" * 60)

            if self.db_manager and self.demo:
                self.demo.run_full_demo()
            else:
                print("\nБаза данных недоступна. Демонстрация DBManager невозможна.")
                print("Проверьте подключение к PostgreSQL и перезапустите приложение.")

        except ImportError as e:
            logger.error(f"Ошибка импорта модулей DBManager: {e}")
            print(f"Ошибка импорта модулей DBManager: {e}")
            print("Убедитесь, что все модули установлены корректно")
        except Exception as e:
            logger.error(f"Ошибка при демонстрации DBManager: {e}")
            print(f"Произошла ошибка при демонстрации DBManager: {e}")
            print("\nВозможные причины:")
            print("• Нет подключения к базе данных")
            print("• Нет данных в базе данных")
            print("• Ошибка в SQL-запросах")

        input("\nНажмите Enter для возврата в главное меню...")

    @staticmethod
    def _configure_superjob_api() -> None:
        """Настройка SuperJob API"""
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
