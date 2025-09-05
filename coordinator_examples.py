"""
Практические примеры использования координаторов в Python

Этот файл содержит конкретные примеры того, как использовать
паттерн координатора в реальных проектах.
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from coordinator_patterns import (
    ServiceCoordinator, 
    PipelineCoordinator, 
    TransactionalCoordinator,
    CoordinatorEvent,
    CoordinationResult
)

# ================================
# ПРИМЕР 1: ОБРАБОТКА ЗАКАЗОВ E-COMMERCE
# ================================

class InventoryService:
    """Сервис управления складом"""
    
    def __init__(self):
        self.inventory = {"product_1": 10, "product_2": 5}
    
    async def reserve_items(self, order_data: Dict) -> bool:
        """Резервирует товары для заказа"""
        print(f"📦 Reserving items: {order_data['items']}")
        for item_id, quantity in order_data['items'].items():
            if self.inventory.get(item_id, 0) < quantity:
                raise ValueError(f"Insufficient inventory for {item_id}")
            self.inventory[item_id] -= quantity
        return True
    
    async def release_items(self, order_data: Dict) -> bool:
        """Освобождает зарезервированные товары"""
        print(f"🔄 Releasing items: {order_data['items']}")
        for item_id, quantity in order_data['items'].items():
            self.inventory[item_id] += quantity
        return True

class PaymentService:
    """Сервис обработки платежей"""
    
    async def process_payment(self, order_data: Dict) -> Dict:
        """Обрабатывает платеж"""
        print(f"💳 Processing payment: ${order_data['total_amount']}")
        
        # Симуляция обработки платежа
        await asyncio.sleep(0.1)
        
        return {
            "transaction_id": "tx_12345",
            "amount": order_data['total_amount'],
            "status": "completed"
        }
    
    async def refund_payment(self, transaction_id: str) -> bool:
        """Возвращает платеж"""
        print(f"💸 Refunding payment: {transaction_id}")
        return True

class NotificationService:
    """Сервис уведомлений"""
    
    async def send_confirmation(self, order_data: Dict) -> bool:
        """Отправляет подтверждение заказа"""
        print(f"📧 Sending order confirmation to {order_data['customer_email']}")
        return True
    
    async def send_shipping_notification(self, order_data: Dict) -> bool:
        """Отправляет уведомление о доставке"""
        print(f"🚚 Sending shipping notification to {order_data['customer_email']}")
        return True

class OrderCoordinator(ServiceCoordinator):
    """Координатор для обработки заказов"""
    
    def __init__(self):
        super().__init__()
        self.setup_services()
        self.setup_event_handlers()
    
    def setup_services(self):
        """Настраивает сервисы и их зависимости"""
        # Регистрируем сервисы с зависимостями
        self.register_service("inventory", InventoryService())
        self.register_service("payment", PaymentService(), dependencies=["inventory"])
        self.register_service("notification", NotificationService(), dependencies=["payment"])
    
    def setup_event_handlers(self):
        """Настраивает обработчики событий"""
        self.register_handler(CoordinatorEvent.STARTED, self._on_order_started)
        self.register_handler(CoordinatorEvent.COMPLETED, self._on_order_completed)
        self.register_handler(CoordinatorEvent.FAILED, self._on_order_failed)
    
    async def _on_order_started(self, event: CoordinatorEvent, data: Any):
        """Обработчик начала обработки заказа"""
        print(f"🚀 Order processing started: {data}")
    
    async def _on_order_completed(self, event: CoordinatorEvent, result: CoordinationResult):
        """Обработчик успешного завершения заказа"""
        print(f"✅ Order processing completed successfully!")
    
    async def _on_order_failed(self, event: CoordinatorEvent, result: CoordinationResult):
        """Обработчик ошибки в обработке заказа"""
        print(f"❌ Order processing failed: {result.errors}")
        # Здесь можно добавить логику компенсации
        await self._compensate_failed_order(result)
    
    async def _compensate_failed_order(self, result: CoordinationResult):
        """Компенсация неуспешного заказа"""
        print("🔄 Starting compensation process...")
        
        # Освобождаем зарезервированные товары
        inventory_service = self._services.get("inventory")
        if inventory_service and "inventory" in result.data:
            try:
                await inventory_service.release_items(result.metadata.get("order_data"))
            except Exception as e:
                print(f"⚠️ Compensation error: {e}")

async def example_order_processing():
    """Пример обработки заказа"""
    print("=" * 50)
    print("🛒 E-COMMERCE ORDER PROCESSING EXAMPLE")
    print("=" * 50)
    
    coordinator = OrderCoordinator()
    
    # Данные заказа
    order_data = {
        "order_id": "ORD_001",
        "customer_email": "customer@example.com",
        "items": {"product_1": 2, "product_2": 1},
        "total_amount": 150.00
    }
    
    # Устанавливаем контекст
    coordinator.set_context("order_data", order_data)
    
    # Обрабатываем заказ
    if order_data["items"]["product_1"] <= 10:  # Успешный случай
        result = await coordinator.coordinate("reserve_items", order_data)
        if result.success:
            await coordinator.coordinate("process_payment", order_data)
            await coordinator.coordinate("send_confirmation", order_data)
    else:
        # Случай с недостаточным количеством товара
        order_data["items"]["product_1"] = 15  # Превышаем доступное количество
        result = await coordinator.coordinate("reserve_items", order_data)

# ================================
# ПРИМЕР 2: PIPELINE ОБРАБОТКИ ДАННЫХ
# ================================

class DataValidationStep:
    """Шаг валидации данных"""
    
    def __call__(self, data: Dict, context: Dict) -> Dict:
        print(f"🔍 Validating data: {list(data.keys())}")
        
        # Проверяем обязательные поля
        required_fields = ['name', 'email', 'age']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Добавляем метку валидации
        data['_validated'] = True
        return data

class DataEnrichmentStep:
    """Шаг обогащения данных"""
    
    def __call__(self, data: Dict, context: Dict) -> Dict:
        print(f"⚡ Enriching data for: {data.get('name')}")
        
        # Добавляем дополнительную информацию
        data['full_name'] = f"{data.get('name')} (Customer)"
        data['age_group'] = 'adult' if data.get('age', 0) >= 18 else 'minor'
        data['processed_at'] = "2024-01-01T00:00:00Z"
        
        return data

class DataPersistenceStep:
    """Шаг сохранения данных"""
    
    def __call__(self, data: Dict, context: Dict) -> Dict:
        print(f"💾 Persisting data for: {data.get('full_name')}")
        
        # Имитируем сохранение в базу данных
        customer_id = f"CUST_{hash(data['email']) % 10000:04d}"
        data['customer_id'] = customer_id
        
        # Сохраняем в контекст для последующего использования
        context['saved_customer_id'] = customer_id
        
        return data

async def example_data_pipeline():
    """Пример pipeline обработки данных"""
    print("\n" + "=" * 50)
    print("🔄 DATA PROCESSING PIPELINE EXAMPLE")
    print("=" * 50)
    
    coordinator = PipelineCoordinator()
    
    # Добавляем шаги в pipeline
    coordinator.add_step(DataValidationStep())
    coordinator.add_step(DataEnrichmentStep())
    coordinator.add_step(DataPersistenceStep())
    
    # Обрабатываем данные
    raw_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 25
    }
    
    result = await coordinator.coordinate(raw_data, source="web_form")
    
    if result.success:
        print(f"✅ Pipeline completed! Customer ID: {coordinator.get_context('saved_customer_id')}")
        print(f"📊 Final data: {result.data}")
    else:
        print(f"❌ Pipeline failed: {result.errors}")

# ================================
# ПРИМЕР 3: МИКРОСЕРВИСНАЯ АРХИТЕКТУРА
# ================================

class UserService:
    """Сервис пользователей"""
    
    async def get_user(self, user_id: str) -> Dict:
        print(f"👤 Getting user: {user_id}")
        return {
            "user_id": user_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
    
    async def update_user_stats(self, user_id: str, action: str) -> bool:
        print(f"📈 Updating user stats: {user_id} - {action}")
        return True

class ProductService:
    """Сервис товаров"""
    
    async def get_product(self, product_id: str) -> Dict:
        print(f"📦 Getting product: {product_id}")
        return {
            "product_id": product_id,
            "name": "Awesome Product",
            "price": 99.99
        }
    
    async def update_product_views(self, product_id: str) -> bool:
        print(f"👀 Updating product views: {product_id}")
        return True

class RecommendationService:
    """Сервис рекомендаций"""
    
    async def get_recommendations(self, user_data: Dict, product_data: Dict) -> List[Dict]:
        print(f"🎯 Getting recommendations for user: {user_data['name']}")
        return [
            {"product_id": "rec_1", "name": "Recommended Product 1", "score": 0.95},
            {"product_id": "rec_2", "name": "Recommended Product 2", "score": 0.87}
        ]

class MicroserviceCoordinator(ServiceCoordinator):
    """Координатор микросервисов"""
    
    def __init__(self):
        super().__init__()
        self.setup_microservices()
    
    def setup_microservices(self):
        """Настраивает микросервисы"""
        self.register_service("user", UserService())
        self.register_service("product", ProductService())
        self.register_service("recommendation", RecommendationService(), 
                            dependencies=["user", "product"])
    
    async def get_user_product_recommendations(self, user_id: str, product_id: str) -> CoordinationResult:
        """Получает рекомендации для пользователя на основе продукта"""
        
        try:
            # Получаем данные пользователя и продукта параллельно
            user_service = self._services["user"]
            product_service = self._services["product"]
            recommendation_service = self._services["recommendation"]
            
            # Параллельные запросы
            user_data, product_data = await asyncio.gather(
                user_service.get_user(user_id),
                product_service.get_product(product_id)
            )
            
            # Обновляем статистику параллельно
            stats_updates = await asyncio.gather(
                user_service.update_user_stats(user_id, "view_product"),
                product_service.update_product_views(product_id),
                return_exceptions=True
            )
            
            # Получаем рекомендации
            recommendations = await recommendation_service.get_recommendations(
                user_data, product_data
            )
            
            return CoordinationResult(
                success=True,
                data={
                    "user": user_data,
                    "product": product_data,
                    "recommendations": recommendations
                },
                metadata={
                    "stats_updated": all(isinstance(r, bool) and r for r in stats_updates)
                }
            )
            
        except Exception as e:
            return CoordinationResult(
                success=False,
                errors=[str(e)],
                metadata={"user_id": user_id, "product_id": product_id}
            )

async def example_microservices():
    """Пример работы с микросервисами"""
    print("\n" + "=" * 50)
    print("🏗️ MICROSERVICES COORDINATION EXAMPLE")
    print("=" * 50)
    
    coordinator = MicroserviceCoordinator()
    
    result = await coordinator.get_user_product_recommendations("user_123", "prod_456")
    
    if result.success:
        print("✅ Microservices coordination completed!")
        print(f"👤 User: {result.data['user']['name']}")
        print(f"📦 Product: {result.data['product']['name']}")
        print(f"🎯 Recommendations count: {len(result.data['recommendations'])}")
        for rec in result.data['recommendations']:
            print(f"  - {rec['name']} (score: {rec['score']})")
    else:
        print(f"❌ Microservices coordination failed: {result.errors}")

# ================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА
# ================================

async def main():
    """Запускает все примеры"""
    print("🎉 COORDINATOR PATTERNS EXAMPLES")
    print("These examples demonstrate different coordination patterns in Python\n")
    
    # Запускаем примеры
    await example_order_processing()
    await example_data_pipeline()
    await example_microservices()
    
    print("\n" + "=" * 50)
    print("✨ All examples completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())