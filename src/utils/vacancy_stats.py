
"""
Модуль для сбора и отображения статистики по вакансиям
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class VacancyStats:
    """Класс для сбора и отображения статистики по вакансиям"""

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
            company_name = VacancyStats._extract_company_name(vacancy)
            
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
        # ПРИОРИТЕТ 1: Сырые данные HH.ru - employer.name
        if isinstance(vacancy, dict) and "employer" in vacancy:
            employer = vacancy["employer"]
            if isinstance(employer, dict) and "name" in employer and employer["name"]:
                return employer["name"]
            elif isinstance(employer, str) and employer.strip():
                return employer
        
        # ПРИОРИТЕТ 2: Сырые данные SuperJob - firm_name
        if isinstance(vacancy, dict) and "firm_name" in vacancy:
            firm_name = vacancy.get("firm_name")
            if firm_name and firm_name.strip():
                return firm_name
        
        # ПРИОРИТЕТ 3: Объекты Vacancy - атрибут employer
        if hasattr(vacancy, 'employer') and vacancy.employer:
            employer = vacancy.employer
            if isinstance(employer, dict):
                return employer.get("name", "Неизвестная компания")
            elif isinstance(employer, str):
                return employer
            return str(employer)
        
        # ПРИОРИТЕТ 4: Объекты Vacancy - raw_data
        if hasattr(vacancy, 'raw_data') and vacancy.raw_data:
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
    def display_company_stats(vacancies: List[Dict[str, Any]], source_name: str = ""):
        """
        Отобразить статистику по компаниям
        
        Args:
            vacancies: Список вакансий
            source_name: Название источника для заголовка
        """
        if not vacancies:
            print("Нет вакансий для отображения статистики")
            return
            
        company_stats = VacancyStats.get_company_distribution(vacancies)
        
        if not company_stats:
            print("Не удалось извлечь информацию о компаниях")
            return
            
        VacancyStats._display_company_distribution(company_stats, len(vacancies), source_name)
    
    @staticmethod
    def _display_company_distribution(company_stats: Dict[str, int], total_vacancies: int, source_name: str = ""):
        """
        Отобразить распределение компаний
        
        Args:
            company_stats: Словарь с распределением компаний
            total_vacancies: Общее количество вакансий
            source_name: Название источника для заголовка
        """
        print(f"\n📊 Распределение вакансий по компаниям{' (' + source_name + ')' if source_name else ''}:")
        print(f"Всего найдено {total_vacancies} вакансий от {len(company_stats)} компаний")
        print("-" * 60)
        
        # Сортируем по количеству вакансий (убывание)
        sorted_companies = sorted(company_stats.items(), key=lambda x: x[1], reverse=True)
        
        for company, count in sorted_companies:
            percentage = (count / total_vacancies) * 100
            print(f"  {company}: {count} вакансий ({percentage:.1f}%)")
        
        print("-" * 60)
    
    @staticmethod
    def display_source_stats(hh_vacancies: List[Dict[str, Any]], sj_vacancies: List[Dict[str, Any]]):
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
        
        print(f"\n📊 Итого найдено: {total_all} вакансий")
        print(f"HH.ru: {total_hh} вакансий")
        print(f"SuperJob: {total_sj} вакансий")
        
        # Показываем статистику по каждому источнику отдельно
        if hh_vacancies:
            VacancyStats.display_company_stats(hh_vacancies, "HH.ru")
            
        if sj_vacancies:
            VacancyStats.display_company_stats(sj_vacancies, "SuperJob")
