"""
Главный интерфейс приложения с полной объектно-ориентированной архитектурой

Реализует все принципы SOLID:
- Single Responsibility: каждый класс отвечает за одну задачу
- Open/Closed: легко расширяется без изменения существующего кода
- Liskov Substitution: классы могут заменять друг друга
- Interface Segregation: специализированные интерфейсы
- Dependency Inversion: зависимость от абстракций
"""

from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable

from src.vacancies.models import Vacancy


@runtime_checkable
class VacancyProvider(Protocol):
    """Протокол для провайдеров вакансий"""

    def get_vacancies(self, query: str) -> List[Vacancy]:
        """Получение вакансий"""
        ...

    def get_source_name(self) -> str:
        """Название источника"""
        ...


@runtime_checkable
class VacancyProcessor(Protocol):
    """Протокол для обработки вакансий"""

    def process_vacancies(self, vacancies: List[Vacancy]) -> List[Vacancy]:
        """Обработка списка вакансий"""
        ...


@runtime_checkable
class VacancyStorage(Protocol):
    """Протокол для хранения вакансий"""

    def save_vacancies(self, vacancies: List[Vacancy]) -> bool:
        """Сохранение вакансий"""
        ...

    def load_vacancies(self) -> List[Vacancy]:
        """Загрузка вакансий"""
        ...


class MainApplicationInterface(ABC):
    """
    Главный интерфейс приложения
    Принцип Single Responsibility - координация работы компонентов
    """

    def __init__(self, provider: VacancyProvider, processor: VacancyProcessor, storage: VacancyStorage):
        """
        Инициализация с инжекцией зависимостей (Dependency Inversion)

        Args:
            provider: Провайдер получения вакансий
            processor: Процессор для обработки вакансий
            storage: Система хранения вакансий
        """
        self.provider = provider
        self.processor = processor
        self.storage = storage

    @abstractmethod
    def run_application(self) -> None:
        """Запуск основной логики приложения"""
        pass

    def execute_vacancy_workflow(self, query: str) -> List[Vacancy]:
        """
        Выполняет полный цикл работы с вакансиями

        Args:
            query: Поисковый запрос

        Returns:
            List[Vacancy]: Обработанные и сохраненные вакансии
        """
        # 1. Получение вакансий
        raw_vacancies = self.provider.get_vacancies(query)

        # 2. Обработка (фильтрация, дедупликация)
        processed_vacancies = self.processor.process_vacancies(raw_vacancies)

        # 3. Сохранение
        if self.storage.save_vacancies(processed_vacancies):
            return processed_vacancies

        return []


class ConsoleApplicationInterface(MainApplicationInterface):
    """
    Реализация консольного интерфейса приложения
    Принцип Open/Closed - расширяет базовый интерфейс
    """

    def run_application(self) -> None:
        """Запуск консольного приложения"""
        print("=== Приложение поиска вакансий ===")

        while True:
            try:
                print("\n1. Поиск вакансий")
                print("2. Просмотр сохраненных вакансий")
                print("3. Статистика по компаниям")
                print("0. Выход")

                choice = input("\nВыберите действие: ").strip()

                if choice == "1":
                    self._handle_vacancy_search()
                elif choice == "2":
                    self._handle_view_saved()
                elif choice == "3":
                    self._handle_company_stats()
                elif choice == "0":
                    print("Завершение работы...")
                    break
                else:
                    print("Неверный выбор")

            except KeyboardInterrupt:
                print("\nПрограмма прервана пользователем")
                break
            except Exception as e:
                print(f"Ошибка: {e}")

    def _handle_vacancy_search(self) -> None:
        """Обработка поиска вакансий"""
        query = input("Введите поисковый запрос: ").strip()
        if not query:
            print("Пустой запрос")
            return

        print(f"Поиск вакансий по запросу: '{query}'")
        vacancies = self.execute_vacancy_workflow(query)

        if vacancies:
            print(f"Найдено и обработано {len(vacancies)} вакансий")
            self._display_vacancy_summary(vacancies[:5])  # Показываем первые 5
        else:
            print("Вакансии не найдены")

    def _handle_view_saved(self) -> None:
        """Просмотр сохраненных вакансий"""
        vacancies = self.storage.load_vacancies()
        if vacancies:
            print(f"Всего сохранено {len(vacancies)} вакансий")
            self._display_vacancy_summary(vacancies[:10])
        else:
            print("Сохраненные вакансии не найдены")

    def _handle_company_stats(self) -> None:
        """Статистика по компаниям"""
        # Получаем статистику через специальный интерфейс
        try:
            from src.storage.services.sql_filter_service import SQLFilterService

            if isinstance(self.processor, SQLFilterService):
                stats = self.processor.get_companies_vacancy_count()
                if stats:
                    print("\n=== Статистика по целевым компаниям ===")
                    for company_name, count in stats[:10]:  # Топ 10
                        print(f"{company_name}: {count} вакансий")
                else:
                    print("Статистика не доступна")
            else:
                print("Статистика не поддерживается текущим процессором")
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")

    def _display_vacancy_summary(self, vacancies: List[Vacancy]) -> None:
        """Отображение краткой информации о вакансиях"""
        for i, vacancy in enumerate(vacancies, 1):
            employer_name = "Не указана"
            if vacancy.employer and hasattr(vacancy.employer, "name"):
                employer_name = vacancy.employer.name or employer_name

            salary_info = "Не указана"
            if vacancy.salary:
                try:
                    # Проверяем есть ли метод форматирования
                    if hasattr(vacancy.salary, "get_formatted_string") and callable(getattr(vacancy.salary, "get_formatted_string", None)):
                        salary_info = vacancy.salary.get_formatted_string()  # type: ignore
                    elif hasattr(vacancy.salary, "salary_info"):
                        salary_info = getattr(vacancy.salary, "salary_info", None) or "Не указана"
                    else:
                        # Базовое форматирование
                        from_amount = getattr(vacancy.salary, "salary_from", None)
                        to_amount = getattr(vacancy.salary, "salary_to", None)
                        if from_amount and to_amount:
                            salary_info = f"{from_amount} - {to_amount} RUR"
                        elif from_amount:
                            salary_info = f"от {from_amount} RUR"
                        elif to_amount:
                            salary_info = f"до {to_amount} RUR"
                except Exception:
                    salary_info = "Не указана"

            print(f"{i}. {vacancy.title}")
            print(f"   Компания: {employer_name}")
            print(f"   Зарплата: {salary_info}")
            print(f"   URL: {vacancy.url or 'Не указан'}")
            print()


class AdvancedApplicationInterface(MainApplicationInterface):
    """
    Продвинутый интерфейс с дополнительными возможностями
    Принцип Liskov Substitution - может заменить базовый интерфейс
    """

    def __init__(self, provider, processor, storage, analytics=None):
        super().__init__(provider, processor, storage)
        self.analytics = analytics

    def run_application(self) -> None:
        """Запуск продвинутого приложения с аналитикой"""
        # Реализация с расширенными возможностями
        pass

    def get_advanced_analytics(self) -> dict:
        """Получение расширенной аналитики"""
        if self.analytics:
            return self.analytics.generate_report()
        return {}
