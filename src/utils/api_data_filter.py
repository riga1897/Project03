"""
Модуль для фильтрации данных API
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

try:
    from .abstract_filter import AbstractDataFilter
except ImportError:
    from src.utils.abstract_filter import AbstractDataFilter

if TYPE_CHECKING:
    from src.vacancies.models import Vacancy


class APIDataFilter(AbstractDataFilter):
    """Класс для фильтрации данных API различных источников"""

    def filter_by_salary(
        self,
        data: List["Vacancy"],
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
    ) -> List["Vacancy"]:
        """
        Реализация абстрактного метода фильтрации по зарплате
        """
        return self.filter_by_salary_range(data, min_salary, max_salary)

    def filter_by_salary_range(
        self,
        data: List[Dict[str, Any]],
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
        source: str = "hh",
    ) -> List[Dict[str, Any]]:
        """
        Фильтрация по диапазону зарплаты

        Args:
            data: Список вакансий
            min_salary: Минимальная зарплата
            max_salary: Максимальная зарплата
            source: Источник данных (hh, sj)

        Returns:
            Отфильтрованный список вакансий
        """
        if not data:
            return []

        filtered = []
        for item in data:
            try:
                salary_info = self._extract_salary_info(item, source)
                if salary_info and self._salary_in_range(salary_info, min_salary, max_salary):
                    filtered.append(item)
            except (KeyError, TypeError, ValueError):
                continue

        return filtered

    def filter_by_keywords(self, data: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация по ключевым словам

        Args:
            data: Список вакансий
            keywords: Список ключевых слов для поиска

        Returns:
            Отфильтрованный список вакансий
        """
        if not data or not keywords:
            return data

        filtered = []
        for item in data:
            try:
                text_fields = self._get_searchable_text(item)
                if self._contains_keywords(text_fields, keywords):
                    filtered.append(item)
            except (KeyError, TypeError):
                continue

        return filtered

    def filter_by_location(self, data: List[Dict[str, Any]], locations: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация по местоположению

        Args:
            data: Список вакансий
            locations: Список городов/регионов

        Returns:
            Отфильтрованный список вакансий
        """
        if not data or not locations:
            return data

        filtered = []
        for item in data:
            try:
                item_location = self._extract_location(item)
                if item_location and any(loc.lower() in item_location.lower() for loc in locations):
                    filtered.append(item)
            except (KeyError, TypeError):
                continue

        return filtered

    def filter_by_experience(self, data: List[Dict[str, Any]], experience_levels: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация по опыту работы

        Args:
            data: Список вакансий
            experience_levels: Список уровней опыта

        Returns:
            Отфильтрованный список вакансий
        """
        if not data or not experience_levels:
            return data

        filtered = []
        for item in data:
            try:
                item_experience = self._extract_experience(item)
                if item_experience and item_experience in experience_levels:
                    filtered.append(item)
            except (KeyError, TypeError):
                continue

        return filtered

    def filter_by_employment_type(
        self, data: List[Dict[str, Any]], employment_types: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Фильтрация по типу занятости

        Args:
            data: Список вакансий
            employment_types: Список типов занятости

        Returns:
            Отфильтрованный список вакансий
        """
        if not data or not employment_types:
            return data

        filtered = []
        for item in data:
            try:
                item_employment = self._extract_employment_type(item)
                if item_employment and item_employment in employment_types:
                    filtered.append(item)
            except (KeyError, TypeError):
                continue

        return filtered

    def filter_by_company(self, data: List[Dict[str, Any]], companies: List[str]) -> List[Dict[str, Any]]:
        """
        Фильтрация по компании

        Args:
            data: Список вакансий
            companies: Список названий компаний

        Returns:
            Отфильтрованный список вакансий
        """
        if not data or not companies:
            return data

        filtered = []
        for item in data:
            try:
                company_name = self._extract_company_name(item)
                if company_name and any(comp.lower() in company_name.lower() for comp in companies):
                    filtered.append(item)
            except (KeyError, TypeError):
                continue

        return filtered

    def _extract_salary_info(self, item: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """Извлечение информации о зарплате"""
        if source.lower() == "hh":
            return item.get("salary")
        elif source.lower() == "sj":
            salary_from = item.get("payment_from")
            salary_to = item.get("payment_to")
            if salary_from or salary_to:
                return {"from": salary_from, "to": salary_to, "currency": item.get("currency", "rub")}
        return None

    def _salary_in_range(
        self, salary_info: Dict[str, Any], min_salary: Optional[int], max_salary: Optional[int]
    ) -> bool:
        """Проверка, попадает ли зарплата в диапазон"""
        salary_from = salary_info.get("from")
        salary_to = salary_info.get("to")

        if not salary_from and not salary_to:
            return False

        # Берем среднее значение если есть оба, иначе имеющееся
        if salary_from and salary_to:
            avg_salary = (salary_from + salary_to) / 2
        else:
            avg_salary = salary_from or salary_to

        if min_salary and avg_salary < min_salary:
            return False
        if max_salary and avg_salary > max_salary:
            return False

        return True

    def _get_searchable_text(self, item: Dict[str, Any]) -> str:
        """Получение текста для поиска"""
        text_parts = []

        # Название вакансии
        if "name" in item:
            text_parts.append(str(item["name"]))

        # Описание
        if "snippet" in item:
            snippet = item["snippet"]
            if isinstance(snippet, dict):
                text_parts.extend([snippet.get("requirement", ""), snippet.get("responsibility", "")])
            else:
                text_parts.append(str(snippet))

        # Для SuperJob
        if "candidat" in item:
            text_parts.append(str(item["candidat"]))

        return " ".join(text_parts).lower()

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Проверка наличия ключевых слов в тексте"""
        return any(keyword.lower() in text for keyword in keywords)

    def _extract_location(self, item: Dict[str, Any]) -> Optional[str]:
        """Извлечение местоположения"""
        try:
            from utils.data_normalizers import normalize_area_data
        except ImportError:
            from src.utils.data_normalizers import normalize_area_data

        # Защитная проверка типа данных
        if not isinstance(item, dict):
            return None

        return normalize_area_data(item.get("area"))

    def _extract_experience(self, item: Dict[str, Any]) -> Optional[str]:
        """Извлечение опыта работы"""
        try:
            from utils.data_normalizers import normalize_experience_data
        except ImportError:
            from src.utils.data_normalizers import normalize_experience_data

        # Защитная проверка типа данных
        if not isinstance(item, dict):
            return None

        return normalize_experience_data(item.get("experience"))

    def _extract_employment_type(self, item: Dict[str, Any]) -> Optional[str]:
        """Извлечение типа занятости"""
        try:
            from utils.data_normalizers import normalize_employment_data
        except ImportError:
            from src.utils.data_normalizers import normalize_employment_data

        # Защитная проверка типа данных
        if not isinstance(item, dict):
            return None

        return normalize_employment_data(item.get("employment"))

    def _extract_company_name(self, item: Dict[str, Any]) -> Optional[str]:
        """Извлечение названия компании"""
        try:
            from utils.data_normalizers import normalize_employer_data
        except ImportError:
            from src.utils.data_normalizers import normalize_employer_data

        # Защитная проверка типа данных
        if not isinstance(item, dict):
            return None

        # Проверяем employer (HH) или firm_name (SuperJob)
        employer = item.get("employer")
        if employer:
            return normalize_employer_data(employer)

        # Для SuperJob создаем структуру как для employer
        firm_name = item.get("firm_name")
        if firm_name:
            return normalize_employer_data({"name": firm_name})

        return None
