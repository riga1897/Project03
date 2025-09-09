
import json
from collections import Counter

def analyze_companies():
    """Анализирует компании из SuperJob кэша и выводит топ-5 по количеству вакансий"""
    
    # Читаем данные из файла
    with open('data/cache/sj/sj_78a93d7419db2c85ba48e5c433f43c1e.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Извлекаем данные о компаниях
    companies_data = {}
    
    for vacancy in data['data']['objects']:
        client = vacancy.get('client', {})
        client_id = client.get('id', 0)
        firm_name = vacancy.get('firm_name', 'Неизвестно')
        
        # Если это анонимная вакансия (id = 0), используем firm_name как ключ
        if client_id == 0:
            key = f"Анонимная ({firm_name})"
            display_id = "0 (анонимная)"
        else:
            key = f"{firm_name}_{client_id}"
            display_id = str(client_id)
        
        if key not in companies_data:
            companies_data[key] = {
                'name': firm_name,
                'client_id': display_id,
                'count': 0
            }
        
        companies_data[key]['count'] += 1
    
    # Сортируем по количеству вакансий (убывание)
    sorted_companies = sorted(companies_data.values(), key=lambda x: x['count'], reverse=True)
    
    print("ТОП-5 компаний по количеству вакансий:")
    print("=" * 60)
    print(f"{'№':<3} {'Название':<40} {'Client ID':<15} {'Кол-во':<6}")
    print("-" * 60)
    
    for i, company in enumerate(sorted_companies[:5], 1):
        print(f"{i:<3} {company['name'][:38]:<40} {company['client_id']:<15} {company['count']:<6}")

if __name__ == "__main__":
    analyze_companies()
