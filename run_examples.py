#!/usr/bin/env python3
"""
Демонстрационный скрипт всех возможностей координаторов

Запуск: python run_examples.py
"""

import asyncio
import logging
import sys
from typing import Dict, Any

# Настройка красивого логирования
class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для логов"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging():
    """Настройка красивого логирования"""
    # Создаем форматтер
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Настраиваем handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

def print_header(title: str, width: int = 80):
    """Печатает красивый заголовок"""
    print("\n" + "=" * width)
    print(f"🎯 {title}".center(width))
    print("=" * width)

def print_section(title: str):
    """Печатает заголовок секции"""
    print(f"\n🔸 {title}")
    print("-" * (len(title) + 3))

async def run_basic_examples():
    """Запускает базовые примеры"""
    print_header("БАЗОВЫЕ ПАТТЕРНЫ КООРДИНАТОРОВ")
    
    try:
        from coordinator_patterns import ServiceCoordinator, PipelineCoordinator, CoordinatorFactory
        
        print_section("Service Coordinator")
        
        # Простой пример сервис-координатора
        class TestService:
            def process(self, data):
                return f"Processed: {data}"
        
        coordinator = CoordinatorFactory.create_coordinator('service')
        coordinator.register_service('test', TestService())
        
        result = await coordinator.coordinate('process', 'test_data')
        print(f"✅ Service coordination result: {result.success}")
        
        print_section("Pipeline Coordinator")
        
        # Пример pipeline
        pipeline = CoordinatorFactory.create_coordinator('pipeline')
        
        def step1(data, context):
            print(f"  📝 Step 1: Validating {data}")
            return f"validated_{data}"
        
        def step2(data, context):
            print(f"  ⚡ Step 2: Processing {data}")  
            return f"processed_{data}"
        
        pipeline.add_step(step1)
        pipeline.add_step(step2)
        
        result = await pipeline.coordinate("raw_data")
        print(f"✅ Pipeline result: {result.data}")
        
    except ImportError as e:
        print(f"❌ Cannot import basic patterns: {e}")

async def run_practical_examples():
    """Запускает практические примеры"""
    print_header("ПРАКТИЧЕСКИЕ ПРИМЕРЫ")
    
    try:
        from coordinator_examples import (
            example_order_processing,
            example_data_pipeline, 
            example_microservices
        )
        
        print_section("E-commerce Order Processing")
        await example_order_processing()
        
        print_section("Data Processing Pipeline")
        await example_data_pipeline()
        
        print_section("Microservices Coordination")
        await example_microservices()
        
    except ImportError as e:
        print(f"❌ Cannot import practical examples: {e}")
    except Exception as e:
        print(f"❌ Error in practical examples: {e}")

async def run_best_practices():
    """Демонстрирует лучшие практики"""
    print_header("ЛУЧШИЕ ПРАКТИКИ")
    
    try:
        from coordinator_best_practices import example_best_practices
        
        await example_best_practices()
        
    except ImportError as e:
        print(f"❌ Cannot import best practices: {e}")
    except Exception as e:
        print(f"❌ Error in best practices: {e}")

async def run_di_integration():
    """Демонстрирует интеграцию с DI"""
    print_header("DEPENDENCY INJECTION ИНТЕГРАЦИЯ")
    
    try:
        from dependency_injection_integration import demonstrate_di_integration
        
        await demonstrate_di_integration()
        
    except ImportError as e:
        print(f"❌ Cannot import DI integration: {e}")
    except Exception as e:
        print(f"❌ Error in DI integration: {e}")

def show_menu():
    """Показывает интерактивное меню"""
    print_header("КООРДИНАТОРЫ В PYTHON - ДЕМОНСТРАЦИЯ")
    
    print("\n🎮 Выберите пример для запуска:")
    print("1. 📐 Базовые паттерны координаторов")
    print("2. 🛒 Практические примеры (E-commerce, Pipeline, Microservices)")
    print("3. 🏆 Лучшие практики (Circuit Breaker, Metrics, Retry)")
    print("4. 🔌 Интеграция с Dependency Injection")
    print("5. 🎯 Запустить все примеры")
    print("0. ❌ Выход")
    
    return input("\n👉 Ваш выбор: ").strip()

async def run_all_examples():
    """Запускает все примеры подряд"""
    print("🚀 Запуск всех примеров...")
    
    await run_basic_examples()
    await run_practical_examples() 
    await run_best_practices()
    await run_di_integration()
    
    print_header("✨ ВСЕ ПРИМЕРЫ ЗАВЕРШЕНЫ УСПЕШНО!")
    print("📖 Изучите исходный код примеров для более детального понимания")
    print("📚 Читайте COORDINATOR_GUIDE.md для полного руководства")

async def main():
    """Главная функция"""
    setup_logging()
    
    # Проверяем, переданы ли аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            await run_all_examples()
            return
        elif sys.argv[1] == "--help":
            print("Использование:")
            print("  python run_examples.py        # Интерактивное меню")
            print("  python run_examples.py --all  # Запуск всех примеров")
            print("  python run_examples.py --help # Показать помощь")
            return
    
    # Интерактивный режим
    while True:
        try:
            choice = show_menu()
            
            if choice == "0":
                print("👋 До свидания!")
                break
            elif choice == "1":
                await run_basic_examples()
            elif choice == "2":
                await run_practical_examples()
            elif choice == "3":
                await run_best_practices()
            elif choice == "4":
                await run_di_integration()
            elif choice == "5":
                await run_all_examples()
                break
            else:
                print("❌ Неверный выбор. Попробуйте еще раз.")
                
            input("\n⏸️ Нажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n👋 Прерывание по Ctrl+C")
            break
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            input("\n⏸️ Нажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)