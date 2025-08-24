"""
Модуль интерфейса взаимодействия с пользователем
"""

from typing import Optional

from src.database import DBManager, DatabaseSetup
from src.data_loader import DataLoader
from src.api.hh_api import HHApi # Импортируем HHApi для использования в run()


class UserInterface:
    """
    Класс пользовательского интерфейса.

    Реализует консольный интерфейс для взаимодействия с пользователем,
    используя методы классов DBManager и DataLoader.
    """

    def __init__(self) -> None:
        """Инициализация интерфейса."""
        self.api = HHApi()
        # Передаем debug_mode в DBManager при инициализации
        self.db_manager: DBManager = DBManager(debug_mode=False)
        self.data_loader: DataLoader = DataLoader(self.db_manager, self.api)

        # Кэш в памяти для быстрого доступа к данным
        self.memory_cache = {}

        # Настройка отладочных сообщений (по умолчанию отключена для пользователей)
        self.debug_mode = False


    def display_menu(self) -> None:
        """Отображает главное меню."""
        print("\n" + "=" * 60)
        print("СИСТЕМА АНАЛИЗА ВАКАНСИЙ HEADHUNTER")
        print("=" * 60)
        print("\n📋 Главное меню:")
        print("1. Загрузить данные с HeadHunter")
        print("2. Показать компании и количество вакансий")
        print("3. Показать все вакансии")
        print("4. Показать среднюю зарплату")
        print("5. Найти вакансии с зарплатой выше средней")
        print("6. Поиск вакансий по ключевому слову")
        print("7. Демонстрация всех возможностей")
        print("8. Управление кэшем")
        print("9. Статус кэша")
        print("10. Настройки отладки")
        print("11. Диагностика данных в базе")
        print("0. Выход")

    def show_companies(self) -> None:
        """Показывает компании и количество вакансий."""
        print("\n🏢 КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
        print("-" * 40)

        companies = self.db_manager.get_companies_and_vacancies_count()

        if not companies:
            print("Данные не найдены. Сначала загрузите данные (опция 1)")
            return

        print(f"Найдено компаний: {len(companies)}\n")

        for i, company in enumerate(companies, 1):
            print(f"{i:2}. {company['company_name']:<35} | {company['vacancies_count']:>3} вакансий")

    def show_all_vacancies(self) -> None:
        """Показывает все вакансии."""
        print("\n💼 ВСЕ ВАКАНЦИИ")
        print("-" * 40)

        vacancies = self.db_manager.get_all_vacancies()

        if not vacancies:
            print("Вакансии не найдены. Сначала загрузите данные (опция 1)")
            return

        print(f"Всего вакансий: {len(vacancies)}\n")

        # Подсчитаем статистику по зарплатам для отладки
        vacancies_with_salary = [v for v in vacancies if v.get('salary_from') or v.get('salary_to')]
        print(f"📊 Статистика: {len(vacancies_with_salary)} из {len(vacancies)} вакансий имеют зарплату")

        # Показываем первые 10 вакансий
        for i, vacancy in enumerate(vacancies[:10], 1):
            salary_info = "не указана"
            if vacancy.get('salary_from') or vacancy.get('salary_to'):
                parts = []
                if vacancy.get('salary_from'):
                    parts.append(f"от {vacancy['salary_from']:,}")
                if vacancy.get('salary_to'):
                    parts.append(f"до {vacancy['salary_to']:,}")
                currency = vacancy.get('salary_currency', 'RUR')
                salary_info = f"{' '.join(parts)} {currency}"

            print(f"{i}. {vacancy['vacancy_name']}")
            print(f"   Компания: {vacancy['company_name']}")
            print(f"   Зарплата: {salary_info}")
            if vacancy.get('salary_status'):
                print(f"   Статус зарплаты: {vacancy['salary_status']}")
            print(f"   Ссылка: {vacancy['vacancy_url']}")
            print()

        if len(vacancies) > 10:
            print(f"... показаны первые 10 из {len(vacancies)} вакансий")

    def show_avg_salary(self) -> None:
        """Показывает среднюю зарплату."""
        print("\n💰 СРЕДНЯЯ ЗАРПЛАТА")
        print("-" * 40)

        avg_salary = self.db_manager.get_avg_salary()

        if avg_salary:
            print(f"Средняя зарплата по всем вакансиям: {avg_salary:,.0f} руб.")
        else:
            print("Не удалось рассчитать среднюю зарплату")
            print("Возможно, в базе нет вакансий с указанной зарплатой")

    def show_high_salary_vacancies(self) -> None:
        """Показывает вакансии с зарплатой выше средней."""
        print("\n💎 ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
        print("-" * 40)

        vacancies = self.db_manager.get_vacancies_with_higher_salary()

        if not vacancies:
            print("Вакансии с зарплатой выше средней не найдены")
            return

        avg_salary = self.db_manager.get_avg_salary()
        if avg_salary:
            print(f"Средняя зарплата: {avg_salary:,.0f} руб.")

        print(f"Найдено вакансий: {len(vacancies)}\n")

        # Показываем топ-10
        for i, vacancy in enumerate(vacancies[:10], 1):
            salary = vacancy.get('calculated_salary', 0)
            print(f"{i:2}. {vacancy['vacancy_name'][:50]}")
            print(f"    Компания: {vacancy['company_name']}")
            print(f"    Зарплата: {salary:,.0f} руб.")
            print()

        if len(vacancies) > 10:
            print(f"... показаны первые 10 из {len(vacancies)} вакансий")

    def search_by_keyword(self) -> None:
        """Поиск вакансий по ключевому слову."""
        print("\n🔍 ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВОМУ СЛОВУ")
        print("-" * 40)

        keyword = input("Введите ключевое слово для поиска: ").strip()

        if not keyword:
            print("Ключевое слово не может быть пустым")
            return

        vacancies = self.db_manager.get_vacancies_with_keyword(keyword)

        if not vacancies:
            print(f"Вакансии с '{keyword}' в названии не найдены")
            return

        print(f"\nНайдено вакансий: {len(vacancies)}\n")

        # Показываем результаты
        for i, vacancy in enumerate(vacancies[:10], 1):
            print(f"{i:2}. {vacancy['vacancy_name']}")
            print(f"    Компания: {vacancy['company_name']}")

            # Зарплата
            salary_info = "не указана"
            if vacancy.get('salary_from') or vacancy.get('salary_to'):
                parts = []
                if vacancy.get('salary_from'):
                    parts.append(f"от {vacancy['salary_from']:,}")
                if vacancy.get('salary_to'):
                    parts.append(f"до {vacancy['salary_to']:,}")
                currency = vacancy.get('salary_currency', 'RUR')
                salary_info = f"{' '.join(parts)} {currency}"

            print(f"    Зарплата: {salary_info}")
            print(f"    Город: {vacancy.get('area_name', 'не указан')}")
            print()

        if len(vacancies) > 10:
            print(f"... показаны первые 10 из {len(vacancies)} вакансий")

    def demonstrate_all(self) -> None:
        """Демонстрирует все возможности системы."""
        print("\n🎯 ДЕМОНСТРАЦИЯ ВСЕХ ВОЗМОЖНОСТЕЙ")
        print("=" * 60)

        # 1. Компании и количество вакансий
        print("\n1️⃣ get_companies_and_vacancies_count()")
        companies = self.db_manager.get_companies_and_vacancies_count()
        if companies:
            print(f"   Найдено {len(companies)} компаний")
            for company in companies[:3]:
                print(f"   • {company['company_name']}: {company['vacancies_count']} вакансий")

        # 2. Все вакансии
        print("\n2️⃣ get_all_vacancies()")
        all_vacancies = self.db_manager.get_all_vacancies()
        if all_vacancies:
            print(f"   Всего вакансий в базе: {len(all_vacancies)}")

        # 3. Средняя зарплата
        print("\n3️⃣ get_avg_salary()")
        avg_salary = self.db_manager.get_avg_salary()
        if avg_salary:
            print(f"   Средняя зарплата: {avg_salary:,.0f} руб.")

        # 4. Вакансии выше средней
        print("\n4️⃣ get_vacancies_with_higher_salary()")
        high_salary = self.db_manager.get_vacancies_with_higher_salary()
        if high_salary:
            print(f"   Вакансий с зарплатой выше средней: {len(high_salary)}")

        # 5. Поиск по ключевым словам
        print("\n5️⃣ get_vacancies_with_keyword()")
        keywords = ['python', 'java', 'senior', 'junior']
        for keyword in keywords:
            results = self.db_manager.get_vacancies_with_keyword(keyword)
            print(f"   • '{keyword}': найдено {len(results)} вакансий")

        print("\n" + "=" * 60)

    def _clear_cache(self) -> None:
        """Очищает кэш данных."""
        # Очищаем через DataLoader
        if self.data_loader.clear_cache():
            if self.debug_mode:
                print("✅ Файловый кэш успешно очищен")
        else:
            if self.debug_mode:
                print("ℹ️  Файловый кэш уже пуст")

        # Очищаем кэш HH API если доступен
        try:
            self.api.clear_cache("hh")
            if self.debug_mode:
                print("✅ Кэш API HeadHunter очищен")
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️  Не удалось очистить кэш API: {e}")

    def _show_cache_status(self) -> None:
        """Показывает статус кэша."""
        print("\n" + "="*60)
        print("📊 СТАТУС КЭША")
        print("="*60)

        # Статус файлового кэша приложения через DataLoader
        cache_info = self.data_loader.get_cache_info()
        if cache_info['exists']:
            print(f"📁 Файловый кэш приложения: ✅ Существует ({cache_info['size_mb']} MB)")
            print(f"📊 Данные: {cache_info['companies_count']} компаний, {cache_info['vacancies_count']} вакансий")
            if cache_info['valid']:
                print("✅ Кэш действителен")
            else:
                print("⚠️ Кэш устарел")
        else:
            print("📁 Файловый кэш приложения: ❌ Отсутствует")

        # Статус кэша API
        try:
            cache_status = self.api.get_cache_status()

            print(f"🗂️  Директория кэша API: {cache_status.get('cache_dir', 'Неизвестно')}")
            print(f"📄 Файлов в кэше API: {cache_status.get('file_cache_count', 0)}")

            memory_cache = cache_status.get('memory_cache', {})
            if memory_cache:
                print(f"🧠 Кэш в памяти: {memory_cache.get('size', 0)}/{memory_cache.get('max_size', 0)} элементов")

            if cache_status.get('cache_files'):
                print("📋 Файлы кэша:")
                for file in cache_status['cache_files'][:5]:  # Показываем первые 5
                    print(f"   • {file}")
                if len(cache_status['cache_files']) > 5:
                    print(f"   ... и еще {len(cache_status['cache_files']) - 5}")

        except Exception as e:
            if self.debug_mode:
                print(f"⚠️  Ошибка получения статуса кэша API: {e}")

        print("="*60)


    def handle_cache_management(self) -> None:
        """Обрабатывает запросы на управление кэшем."""
        print("\n🔧 УПРАВЛЕНИЕ КЭШЕМ")
        print("-" * 40)
        print("1. Очистить кэш")
        print("2. Показать информацию о кэше")
        print("0. Назад в главное меню")

        choice = input("\nВыберите опцию: ").strip()

        if choice == '1':
            self._clear_cache()
            if self.debug_mode:
                print("Операция очистки кэша завершена.")
        elif choice == '2':
            self._show_cache_status()
        elif choice == '0':
            pass  # Возврат в главное меню
        else:
            print("⚠️ Неверная опция. Попробуйте снова.")

    def load_data_from_api(self) -> None:
        """Загружает данные из API HeadHunter с возможностью выбора ключевого слова и периода."""
        print("\n" + "="*60)
        print("ЗАГРУЗКА ДАННЫХ HEADHUNTER В POSTGRESQL")
        print("="*60)

        # Получаем ключевое слово от пользователя
        keyword = input("🎯 Введите ключевое слово для поиска вакансий (или Enter для всех): ").strip()

        if not keyword:
            keyword = "все" # Используем "все" для индикации, что поиск без ключевого слова
            if self.debug_mode:
                print("🔍 Будем загружать все вакансии компаний")
        else:
            if self.debug_mode:
                print(f"🎯 Поиск вакансий по ключевому слову: '{keyword}'")

        # Выбираем период публикации
        period = self._get_period_choice()
        if period is None:
            print("❌ Загрузка отменена")
            return

        if self.debug_mode:
            print(f"📅 Период поиска: последние {period} дней")
            print(f"\n📦 Настройка базы данных...")

        try:
            # Собираем данные через API с указанным периодом
            data = self.api.collect_data(keyword=keyword if keyword != "все" else None, period=period)

            if not data or not data.get('companies') or not data.get('vacancies'):
                print("❌ Не удалось получить данные из API")
                return

            # Сохраняем данные в кэше для дальнейшего использования
            self.data_loader.cache_data = data

            print(f"\n✅ Данные успешно загружены:")
            print(f"   📊 Компаний: {len(data['companies'])}")
            print(f"   💼 Вакансий: {len(data['vacancies'])}")
            print(f"   📅 За период: {period} дней")

            # Сохраняем данные в базу PostgreSQL
            print(f"\n📥 Сохранение данных в базу PostgreSQL...")
            # Запускаем загрузку данных с параметрами
            success = self.data_loader.load_data_with_params(
                use_cache=True,
                keyword=keyword if keyword != "все" else None,
                period=period
            )
            if success:
                print(f"✅ Данные успешно сохранены в базу данных!")
            else:
                print(f"⚠️ Ошибка сохранения в базу данных")

            if self.debug_mode:
                print(f"\n💾 Данные также сохранены в кэше памяти для быстрого доступа")

        except Exception as e:
            print(f"⚠️ Произошла ошибка: {e}")

    @staticmethod
    def _get_period_choice() -> Optional[int]:
        """
        Выбор периода публикации вакансий

        Returns:
            Optional[int]: Количество дней для поиска или None при отмене
        """
        try:
            print("\n📅 Выберите период публикации вакансий:")
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
                print("📅 Выбор периода отменен.")
                return None
            elif choice in period_map:
                return period_map[choice]
            elif choice == "6":
                try:
                    custom_period = int(input("Введите количество дней (1-365): "))
                    if 1 <= custom_period <= 365:
                        return custom_period
                    else:
                        print("⚠️ Некорректный период. Используется 15 дней по умолчанию.")
                        return 15
                except ValueError:
                    print("⚠️ Некорректный ввод. Используется 15 дней по умолчанию.")
                    return 15
            else:
                print("⚠️ Некорректный выбор. Используется 15 дней по умолчанию.")
                return 15

        except KeyboardInterrupt:
            print("\n📅 Выбор периода отменен.")
            return None

    def _debug_settings_menu(self) -> None:
        """Меню настроек отладки"""
        print("\n" + "="*60)
        print("НАСТРОЙКИ ОТЛАДКИ")
        print("="*60)

        current_status = "включен" if self.db_manager.debug_mode else "отключен"
        print(f"Текущий режим отладки: {current_status}")

        if self.db_manager.debug_mode:
            choice = input("\nОтключить режим отладки? (y/n): ").lower()
            if choice == 'y':
                self.db_manager.debug_mode = False
                print("✅ Режим отладки отключен")
        else:
            choice = input("\nВключить режим отладки? (y/n): ").lower()
            if choice == 'y':
                self.db_manager.debug_mode = True
                print("✅ Режим отладки включен")

        input("\nНажмите Enter для продолжения...")

    def _data_diagnostics_menu(self) -> None:
        """Диагностика данных в базе"""
        print("\n" + "="*60)
        print("ДИАГНОСТИКА ДАННЫХ В БАЗЕ")
        print("="*60)

        # Получаем статистику по зарплатам
        vacancies = self.db_manager.get_all_vacancies()
        companies = self.db_manager.get_companies_and_vacancies_count()

        print(f"📊 Общая статистика:")
        print(f"   • Компаний в базе: {len(companies)}")
        print(f"   • Вакансий в базе: {len(vacancies)}")

        # Анализ зарплат
        vacancies_with_salary = [v for v in vacancies if v.get('salary_from') or v.get('salary_to')]
        print(f"\n💰 Анализ зарплат:")
        print(f"   • Вакансий с зарплатой: {len(vacancies_with_salary)}")
        print(f"   • Вакансий без зарплаты: {len(vacancies) - len(vacancies_with_salary)}")
        print(f"   • Процент с зарплатой: {len(vacancies_with_salary)/len(vacancies)*100:.1f}%" if vacancies else "0%")

        # Примеры вакансий с зарплатой
        if vacancies_with_salary:
            print(f"\n💼 Примеры вакансий с зарплатой:")
            for i, v in enumerate(vacancies_with_salary[:3], 1):
                salary_parts = []
                if v.get('salary_from'):
                    salary_parts.append(f"от {v['salary_from']:,}")
                if v.get('salary_to'):
                    salary_parts.append(f"до {v['salary_to']:,}")
                salary_str = f"{' '.join(salary_parts)} {v.get('salary_currency', 'RUR')}"
                print(f"   {i}. {v['vacancy_name'][:50]}...")
                print(f"      Зарплата: {salary_str}")

        # Анализ компаний
        print(f"\n🏢 Топ-5 компаний по количеству вакансий:")
        for i, company in enumerate(companies[:5], 1):
            print(f"   {i}. {company['company_name']}: {company['vacancies_count']} вакансий")

        input("\nНажмите Enter для продолжения...")


    def run(self) -> None:
        """Запускает главный цикл интерфейса."""
        while True:
            self.display_menu()

            try:
                # Обновлен диапазон выбора опций
                choice = input("\nВыберите опцию (0-11): ").strip()

                if choice == '1':
                    self.load_data_from_api()
                elif choice == '2':
                    self.show_companies()
                elif choice == '3':
                    self.show_all_vacancies()
                elif choice == '4':
                    self.show_avg_salary()
                elif choice == '5':
                    self.show_high_salary_vacancies()
                elif choice == '6':
                    self.search_by_keyword()
                elif choice == '7':
                    self.demonstrate_all()
                elif choice == '8':
                    self.handle_cache_management()
                elif choice == '9':
                    self._show_cache_status()
                # Добавлен новый пункт меню для настроек отладки
                elif choice == "10":
                    self._debug_settings_menu()
                elif choice == '11':
                    self._data_diagnostics_menu()
                elif choice == '0':
                    print("\n👋 До свидания!")
                    break
                else:
                    print("❌ Неверный выбор. Попробуйте снова.")

                if choice != '0':
                    input("\nНажмите Enter для продолжения...")

            except KeyboardInterrupt:
                print("\n\n👋 Программа прервана пользователем")
                break
            except Exception as e:
                print(f"⚠️ Произошла ошибка: {e}")
                input("\nНажмите Enter для продолжения...")