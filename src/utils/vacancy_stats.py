"""
Модуль для сбора и отображения статистики по вакансиям
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class VacancyStats:
    """
    Класс для сбора и отображения статистики по вакансиям

    Предоставляет методы для:
    - Подсчета статистики по зарплатам
    - Анализа распределения по компаниям
    - Отображения статистики по источникам
    - Анализа маппинга компаний
    """

    def __init__(self) -> None:
        """
        Инициализация статистики

        Создает экземпляр для работы со статистикой вакансий.
        """
        pass

    def calculate_salary_statistics(self, vacancies: List[Any]) -> Dict[str, int]:
        """Подсчет статистики по зарплатам"""
        salaries = []
        with_salary_count = 0
        without_salary_count = 0

        if not vacancies:
            return {"average": 0, "min": 0, "max": 0, "count": 0, "with_salary_count": 0, "without_salary_count": 0}

        for vacancy in vacancies:
            try:
                if hasattr(vacancy, "salary") and vacancy.salary:
                    salary_from = getattr(vacancy.salary, "amount_from", None)
                    salary_to = getattr(vacancy.salary, "amount_to", None)

                    # Защищаемся от Mock объектов, проверяя тип
                    if salary_from is not None and isinstance(salary_from, (int, float)) and salary_from > 0:
                        salaries.append(int(salary_from))
                        with_salary_count += 1
                    elif salary_to is not None and isinstance(salary_to, (int, float)) and salary_to > 0:
                        salaries.append(int(salary_to))
                        with_salary_count += 1
                    else:
                        without_salary_count += 1
                else:
                    without_salary_count += 1
            except (AttributeError, TypeError):
                # Обработка случаев с Mock объектами или некорректными данными
                without_salary_count += 1
                continue

        if not salaries:
            return {
                "average": 0,
                "min": 0,
                "max": 0,
                "count": 0,
                "with_salary_count": with_salary_count,
                "without_salary_count": without_salary_count,
            }

        return {
            "average": sum(salaries) // len(salaries),
            "min": min(salaries),
            "max": max(salaries),
            "count": len(salaries),
            "with_salary_count": with_salary_count,
            "without_salary_count": without_salary_count,
        }

    def get_top_employers(self, vacancies: List[Any], top_n: int = 10) -> List[Tuple[str, int]]:
        """Получение топ работодателей"""
        employer_counts: Dict[str, int] = {}
        for vacancy in vacancies:
            if vacancy.employer and vacancy.employer.name:
                name = vacancy.employer.name
                employer_counts[name] = employer_counts.get(name, 0) + 1

        # Сортируем по количеству вакансий
        sorted_employers = sorted(employer_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_employers[:top_n]

    def get_source_distribution(self, vacancies: List[Any]) -> Dict[str, int]:
        """Получение распределения по источникам"""
        source_counts: Dict[str, int] = {}
        for vacancy in vacancies:
            source = vacancy.source
            source_counts[source] = source_counts.get(source, 0) + 1

        return source_counts

    def display_company_stats(self, vacancies: List[Any], source_name: Optional[str] = None) -> None:
        """
        Отображение статистики по компаниям

        Args:
            vacancies: Список вакансий
            source_name: Название источника для заголовка
        """
        if not vacancies:
            print("Нет вакансий для отображения статистики")
            return

        print(f"Статистика по компаниям{' (' + source_name + ')' if source_name else ''}: {len(vacancies)} вакансий")

        # Подсчитываем вакансии по компаниям
        company_stats: Dict[str, int] = {}
        for vacancy in vacancies:
            try:
                # Получаем имя работодателя из разных возможных структур
                employer_name = None

                if isinstance(vacancy, dict):
                    # Обрабатываем словарь
                    employer = vacancy.get("employer")
                    if isinstance(employer, dict):
                        employer_name = employer.get("name")
                    elif hasattr(employer, "name"):
                        employer_name = employer.name
                    elif isinstance(employer, str):
                        employer_name = employer
                elif hasattr(vacancy, "employer"):
                    # Обрабатываем объект вакансии
                    employer = vacancy.employer
                    if isinstance(employer, dict):
                        employer_name = employer.get("name")
                    elif hasattr(employer, "name"):
                        employer_name = employer.name
                    elif isinstance(employer, str):
                        employer_name = employer

                if employer_name:
                    company_stats[employer_name] = company_stats.get(employer_name, 0) + 1
                else:
                    company_stats["Неизвестная компания"] = company_stats.get("Неизвестная компания", 0) + 1

            except Exception as e:
                print(f"Ошибка обработки вакансии для статистики: {e}")
                continue

        # Выводим топ компаний
        if company_stats:
            print("\nТоп компаний по количеству вакансий:")
            sorted_companies = sorted(company_stats.items(), key=lambda x: x[1], reverse=True)
            for company, count in sorted_companies[:10]:  # Показываем топ 10
                print(f"  {company}: {count} вакансий")
        else:
            print("Не удалось определить статистику по компаниям")


def calculate_statistics(vacancies: List[Any]) -> Dict[str, Any]:
    """Функция для подсчета общей статистики"""
    stats = VacancyStats()

    return {
        "salary_stats": stats.calculate_salary_statistics(vacancies),
        "top_employers": stats.get_top_employers(vacancies),
        "source_distribution": stats.get_source_distribution(vacancies),
        "total_count": len(vacancies),
    }


class VacancyStatsExtended:
    """Расширенные статические методы для работы с вакансиями"""

    @staticmethod
    def get_company_distribution(vacancies: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Получить распределение вакансий по компаниям

        Args:
            vacancies: Список вакансий

        Returns:
            Dict[str, int]: Словарь с компаниями и количеством вакансий
        """
        company_stats = defaultdict(int)

        for vacancy in vacancies:
            # Получаем название компании из разных источников
            company_name = VacancyStatsExtended._extract_company_name(vacancy)

            if company_name:
                company_stats[company_name] += 1

        return dict(company_stats)

    @staticmethod
    def _extract_company_name(vacancy: Dict[str, Any]) -> str:
        """
        Извлечь название компании из данных вакансии (приоритет - сырые данные API)

        Args:
            vacancy: Данные вакансии (сырые данные API или объект Vacancy)

        Returns:
            str: Название компании или "Неизвестная компания"
        """
        # ПРИОРИТЕТ 1: Объекты Vacancy - атрибут employer (новая структура)
        if hasattr(vacancy, "employer") and vacancy.employer:
            employer = vacancy.employer
            if isinstance(employer, dict):
                return employer.get("name", "Неизвестная компания")
            elif isinstance(employer, str):
                return employer
            return str(employer)

        # ПРИОРИТЕТ 2: Сырые данные HH.ru - employer.name
        if isinstance(vacancy, dict) and "employer" in vacancy:
            employer = vacancy["employer"]
            if isinstance(employer, dict) and "name" in employer and employer["name"]:
                return employer["name"]
            elif isinstance(employer, str) and employer.strip():
                return employer

        # ПРИОРИТЕТ 3: Сырые данные SuperJob - firm_name (с сохранением ID)
        if isinstance(vacancy, dict) and "firm_name" in vacancy:
            firm_name = vacancy.get("firm_name")
            if firm_name and str(firm_name).strip() and str(firm_name) != "None":
                # Дополнительно сохраняем ID работодателя если есть
                firm_id = vacancy.get("firm_id") or vacancy.get("client_id")
                if firm_id and hasattr(vacancy, "employer_id"):
                    vacancy.employer_id = str(firm_id)
                return str(firm_name)

        # ПРИОРИТЕТ 4: Объекты Vacancy - raw_data
        if hasattr(vacancy, "raw_data") and vacancy.raw_data:
            raw_data = vacancy.raw_data
            if isinstance(raw_data, dict) and "employer" in raw_data:
                employer = raw_data["employer"]
                if isinstance(employer, dict) and "name" in employer:
                    return employer["name"]

        # ПРИОРИТЕТ 5: Преобразованные данные - поле company
        if isinstance(vacancy, dict) and "company" in vacancy:
            company = vacancy["company"]
            if company and str(company).strip() and str(company) != "None":
                return str(company).title()

        return "Неизвестная компания"

    @staticmethod
    def display_company_stats(vacancies: List[Dict[str, Any]], source_name: str = "") -> None:
        """
        Отобразить статистику по компаниям

        Args:
            vacancies: Список вакансий
            source_name: Название источника для заголовка
        """
        if not vacancies:
            print("Нет вакансий для отображения статистики")
            return

        company_stats = VacancyStatsExtended.get_company_distribution(vacancies)

        if not company_stats:
            print("Не удалось извлечь информацию о компаниях")
            return

        VacancyStatsExtended._display_company_distribution(company_stats, len(vacancies), source_name)

    @staticmethod
    def _display_company_distribution(
        company_stats: Dict[str, int], total_vacancies: int, source_name: str = ""
    ) -> None:
        """
        Отобразить распределение компаний

        Args:
            company_stats: Словарь с распределением компаний
            total_vacancies: Общее количество вакансий
            source_name: Название источника для заголовка
        """
        print(f"\nРаспределение вакансий по компаниям{' (' + source_name + ')' if source_name else ''}:")
        print(f"Всего найдено {total_vacancies} вакансий от {len(company_stats)} компаний")
        print("-" * 60)

        # Сортируем по количеству вакансий (убывание)
        sorted_companies = sorted(company_stats.items(), key=lambda x: x[1], reverse=True)

        for company, count in sorted_companies:
            percentage = (count / total_vacancies) * 100
            print(f"  {company}: {count} вакансий ({percentage:.1f}%)")

        print("-" * 60)

    @staticmethod
    def display_source_stats(hh_vacancies: List[Dict[str, Any]], sj_vacancies: List[Dict[str, Any]]) -> None:
        """
        Отобразить статистику по каждому источнику отдельно

        Args:
            hh_vacancies: Вакансии с HH.ru
            sj_vacancies: Вакансии с SuperJob
        """
        total_hh = len(hh_vacancies)
        total_sj = len(sj_vacancies)
        total_all = total_hh + total_sj

        if total_all == 0:
            print("Нет вакансий для отображения статистики")
            return

        print(f"\nИтого найдено: {total_all} вакансий")
        print(f"HH.ru: {total_hh} вакансий")
        print(f"SuperJob: {total_sj} вакансий")

        # Показываем статистику по каждому источнику отдельно
        if hh_vacancies:
            VacancyStatsExtended.display_company_stats(hh_vacancies, "HH.ru")

        if sj_vacancies:
            VacancyStatsExtended.display_company_stats(sj_vacancies, "SuperJob")

    @staticmethod
    def analyze_company_mapping(vacancies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализ маппинга компаний для диагностики потери company_id

        Args:
            vacancies: Список вакансий для анализа

        Returns:
            Dict с результатами анализа
        """
        total_vacancies = len(vacancies)
        with_employer = 0
        without_employer = 0
        unique_employers = set()

        for vacancy in vacancies:
            employer_name = VacancyStatsExtended._extract_company_name(vacancy)

            if employer_name and employer_name != "Неизвестная компания":
                with_employer += 1
                unique_employers.add(employer_name)
            else:
                without_employer += 1

        return {
            "total_vacancies": total_vacancies,
            "with_employer": with_employer,
            "without_employer": without_employer,
            "employer_coverage": (with_employer / total_vacancies * 100) if total_vacancies > 0 else 0,
            "unique_employers": len(unique_employers),
            "employer_names": sorted(list(unique_employers)),
        }

    @staticmethod
    def display_company_mapping_analysis(vacancies: List[Dict[str, Any]]) -> None:
        """
        Отобразить анализ маппинга компаний

        Args:
            vacancies: Список вакансий для анализа
        """
        analysis = VacancyStatsExtended.analyze_company_mapping(vacancies)

        print("\nАнализ маппинга компаний:")
        print(f"Всего вакансий: {analysis['total_vacancies']}")
        print(f"С указанным работодателем: {analysis['with_employer']} ({analysis['employer_coverage']:.1f}%)")
        print(f"Без работодателя: {analysis['without_employer']}")
        print(f"Уникальных работодателей: {analysis['unique_employers']}")

        if analysis["employer_names"]:
            print("\nТоп-10 работодателей:")
            for i, employer in enumerate(analysis["employer_names"][:10], 1):
                print(f"  {i}. {employer}")

            if len(analysis["employer_names"]) > 10:
                print(f"  ... и еще {len(analysis['employer_names']) - 10} работодателей")
