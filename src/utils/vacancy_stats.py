
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
        Извлечь название компании из данных вакансии
        
        Args:
            vacancy: Данные вакансии
            
        Returns:
            str: Название компании или "Неизвестная компания"
        """
        # Для SuperJob
        if "firm_name" in vacancy:
            return vacancy.get("firm_name", "Неизвестная компания")
        
        # Для HeadHunter
        if "employer" in vacancy:
            employer = vacancy["employer"]
            if isinstance(employer, dict):
                return employer.get("name", "Неизвестная компания")
            elif isinstance(employer, str):
                return employer
                
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
            
        print(f"\n📊 Распределение вакансий по компаниям{' (' + source_name + ')' if source_name else ''}:")
        print(f"Всего найдено {len(vacancies)} вакансий от {len(company_stats)} компаний")
        print("-" * 60)
        
        # Сортируем по количеству вакансий (убывание)
        sorted_companies = sorted(company_stats.items(), key=lambda x: x[1], reverse=True)
        
        for company, count in sorted_companies:
            percentage = (count / len(vacancies)) * 100
            print(f"  {company}: {count} вакансий ({percentage:.1f}%)")
        
        print("-" * 60)
    
    @staticmethod
    def display_combined_stats(hh_vacancies: List[Dict[str, Any]], sj_vacancies: List[Dict[str, Any]]):
        """
        Отобразить объединенную статистику по компаниям из разных источников
        
        Args:
            hh_vacancies: Вакансии с HH.ru
            sj_vacancies: Вакансии с SuperJob
        """
        print("\n" + "=" * 80)
        print("📈 ОБЩАЯ СТАТИСТИКА ПО ИСТОЧНИКАМ")
        print("=" * 80)
        
        total_hh = len(hh_vacancies)
        total_sj = len(sj_vacancies)
        total_all = total_hh + total_sj
        
        if total_all == 0:
            print("Нет вакансий для отображения статистики")
            return
        
        print(f"HH.ru: {total_hh} вакансий ({(total_hh/total_all)*100:.1f}%)")
        print(f"SuperJob: {total_sj} вакансий ({(total_sj/total_all)*100:.1f}%)")
        print(f"Всего: {total_all} вакансий")
        
        # Показываем статистику по каждому источнику отдельно
        if hh_vacancies:
            VacancyStats.display_company_stats(hh_vacancies, "HH.ru")
            
        if sj_vacancies:
            VacancyStats.display_company_stats(sj_vacancies, "SuperJob")
            
        # Объединенная статистика по компаниям
        if total_all > 0:
            all_vacancies = hh_vacancies + sj_vacancies
            VacancyStats.display_company_stats(all_vacancies, "Все источники")
