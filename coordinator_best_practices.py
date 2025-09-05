"""
Лучшие практики работы с центральными координаторами в Python

Этот файл содержит рекомендации, паттерны и anti-паттерны
для эффективной работы с координаторами.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from contextlib import asynccontextmanager
from functools import wraps
import time
from collections import defaultdict

# ================================
# ЛУЧШИЕ ПРАКТИКИ И РЕКОМЕНДАЦИИ
# ================================

"""
🎯 ОСНОВНЫЕ ПРИНЦИПЫ КООРДИНАТОРОВ:

1. ЕДИНСТВЕННАЯ ОТВЕТСТВЕННОСТЬ (Single Responsibility)
   - Координатор должен только координировать, не выполнять бизнес-логику
   - Каждый координатор отвечает за конкретную предметную область

2. СЛАБАЯ СВЯЗАННОСТЬ (Loose Coupling)
   - Координатор не должен знать внутреннее устройство сервисов
   - Используйте интерфейсы и протоколы для взаимодействия

3. ОБРАТИМОСТЬ ОПЕРАЦИЙ (Compensating Actions)
   - Всегда предусматривайте откат операций при ошибках
   - Реализуйте паттерн Saga для сложных транзакций

4. НАБЛЮДАЕМОСТЬ (Observability)
   - Логируйте все важные события
   - Используйте метрики и трассировку
   - Добавляйте correlation ID для отслеживания запросов

5. ОТКАЗОУСТОЙЧИВОСТЬ (Resilience)
   - Используйте retry механизмы с exponential backoff
   - Реализуйте circuit breaker для нестабильных сервисов
   - Добавляйте timeout для всех операций
"""

# ================================
# ADVANCED КООРДИНАТОР С ЛУЧШИМИ ПРАКТИКАМИ
# ================================

class CoordinatorMetrics:
    """Метрики для координатора"""
    
    def __init__(self):
        self.operation_counts = defaultdict(int)
        self.operation_durations = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
    
    def record_operation(self, operation: str, duration: float, success: bool):
        """Записывает метрики операции"""
        self.operation_counts[operation] += 1
        self.operation_durations[operation].append(duration)
        
        if success:
            self.success_counts[operation] += 1
        else:
            self.error_counts[operation] += 1
    
    def get_success_rate(self, operation: str) -> float:
        """Возвращает процент успешных операций"""
        total = self.operation_counts[operation]
        if total == 0:
            return 0.0
        return (self.success_counts[operation] / total) * 100
    
    def get_average_duration(self, operation: str) -> float:
        """Возвращает среднее время выполнения операции"""
        durations = self.operation_durations[operation]
        return sum(durations) / len(durations) if durations else 0.0

def with_correlation_id(func):
    """Декоратор для добавления correlation ID к операциям"""
    
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Генерируем correlation ID если его нет
        correlation_id = kwargs.get('correlation_id', f"coord_{int(time.time() * 1000)}")
        kwargs['correlation_id'] = correlation_id
        
        # Устанавливаем в контекст
        self.set_context('correlation_id', correlation_id)
        self._logger.info(f"Starting operation with correlation_id: {correlation_id}")
        
        try:
            result = await func(self, *args, **kwargs)
            self._logger.info(f"Completed operation with correlation_id: {correlation_id}")
            return result
        except Exception as e:
            self._logger.error(f"Failed operation with correlation_id: {correlation_id}, error: {e}")
            raise
    
    return wrapper

def with_timeout(timeout_seconds: float):
    """Декоратор для добавления timeout к операциям"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """Декоратор для retry логики с exponential backoff"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        wait_time = delay * (backoff_factor ** attempt)
                        logging.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logging.error(f"All {max_retries + 1} attempts failed")
                        raise last_exception
        return wrapper
    return decorator

class AdvancedCoordinator(ABC):
    """Продвинутый координатор с лучшими практиками"""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(f"{self.__class__.__name__}({name})")
        self._metrics = CoordinatorMetrics()
        self._context: Dict[str, Any] = {}
        self._circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        self._compensating_actions: List[Callable] = []
    
    def add_circuit_breaker(self, service_name: str, failure_threshold: int = 5, 
                           recovery_timeout: int = 60):
        """Добавляет circuit breaker для сервиса"""
        self._circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            logger=self._logger
        )
    
    def add_compensating_action(self, action: Callable):
        """Добавляет действие компенсации"""
        self._compensating_actions.append(action)
    
    async def execute_compensating_actions(self):
        """Выполняет все действия компенсации в обратном порядке"""
        for action in reversed(self._compensating_actions):
            try:
                if asyncio.iscoroutinefunction(action):
                    await action()
                else:
                    action()
                self._logger.info(f"Executed compensating action: {action.__name__}")
            except Exception as e:
                self._logger.error(f"Compensating action failed: {e}")
    
    @with_correlation_id
    @with_timeout(30.0)  # 30 секунд timeout по умолчанию
    async def coordinate_with_metrics(self, operation: str, *args, **kwargs):
        """Координирует операцию с метриками"""
        start_time = time.time()
        success = False
        
        try:
            result = await self.coordinate(operation, *args, **kwargs)
            success = result.success if hasattr(result, 'success') else True
            return result
        except Exception as e:
            self._logger.error(f"Coordination failed: {e}")
            await self.execute_compensating_actions()
            raise
        finally:
            duration = time.time() - start_time
            self._metrics.record_operation(operation, duration, success)
            
            # Логируем метрики
            success_rate = self._metrics.get_success_rate(operation)
            avg_duration = self._metrics.get_average_duration(operation)
            self._logger.info(f"Operation {operation}: success_rate={success_rate:.1f}%, "
                            f"avg_duration={avg_duration:.3f}s")
    
    def get_metrics(self) -> CoordinatorMetrics:
        """Возвращает метрики координатора"""
        return self._metrics
    
    def set_context(self, key: str, value: Any) -> None:
        """Устанавливает контекстное значение"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Получает контекстное значение"""
        return self._context.get(key, default)
    
    @abstractmethod
    async def coordinate(self, operation: str, *args, **kwargs):
        """Основной метод координации"""
        pass

# ================================
# CIRCUIT BREAKER PATTERN
# ================================

class CircuitBreakerState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Блокировка запросов
    HALF_OPEN = "half_open"  # Тестирование восстановления

class CircuitBreaker:
    """Реализация паттерна Circuit Breaker"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, logger=None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.logger = logger or logging.getLogger(__name__)
    
    async def call(self, func: Callable, *args, **kwargs):
        """Выполняет вызов через Circuit Breaker"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info("Circuit breaker moved to HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Проверяет, стоит ли попытаться сбросить circuit breaker"""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Обрабатывает успешный вызов"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        if self.state != CircuitBreakerState.CLOSED:
            self.logger.info("Circuit breaker moved to CLOSED state")
    
    def _on_failure(self):
        """Обрабатывает неудачный вызов"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")

# ================================
# DEPENDENCY INJECTION CONTAINER
# ================================

T = TypeVar('T')

class DIContainer:
    """Простой DI контейнер для координаторов"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_instance(self, name: str, instance: Any):
        """Регистрирует экземпляр сервиса"""
        self._services[name] = instance
    
    def register_factory(self, name: str, factory: Callable[[], Any]):
        """Регистрирует фабрику для создания сервиса"""
        self._factories[name] = factory
    
    def register_singleton(self, name: str, factory: Callable[[], Any]):
        """Регистрирует singleton сервис"""
        if name not in self._singletons:
            self._singletons[name] = factory()
        return self._singletons[name]
    
    def get(self, name: str) -> Any:
        """Получает сервис по имени"""
        # Проверяем зарегистрированные экземпляры
        if name in self._services:
            return self._services[name]
        
        # Проверяем singletons
        if name in self._singletons:
            return self._singletons[name]
        
        # Проверяем фабрики
        if name in self._factories:
            return self._factories[name]()
        
        raise ValueError(f"Service '{name}' not found in DI container")
    
    def wire_coordinator(self, coordinator: 'DIAwareCoordinator'):
        """Внедряет зависимости в координатор"""
        coordinator.set_container(self)

class DIAwareCoordinator(AdvancedCoordinator):
    """Координатор с поддержкой Dependency Injection"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._container: Optional[DIContainer] = None
    
    def set_container(self, container: DIContainer):
        """Устанавливает DI контейнер"""
        self._container = container
    
    def get_service(self, service_name: str) -> Any:
        """Получает сервис из DI контейнера"""
        if self._container is None:
            raise RuntimeError("DI container not set")
        return self._container.get(service_name)
    
    async def coordinate_with_di(self, operation: str, service_names: List[str], *args, **kwargs):
        """Координирует операцию с использованием DI"""
        services = {}
        
        # Получаем все необходимые сервисы
        for service_name in service_names:
            try:
                services[service_name] = self.get_service(service_name)
            except Exception as e:
                self._logger.error(f"Failed to get service '{service_name}': {e}")
                return CoordinationResult(
                    success=False,
                    errors=[f"Service dependency error: {e}"],
                    metadata={"operation": operation}
                )
        
        # Выполняем операцию с сервисами
        return await self._execute_operation_with_services(operation, services, *args, **kwargs)
    
    async def _execute_operation_with_services(self, operation: str, services: Dict[str, Any], 
                                             *args, **kwargs):
        """Выполняет операцию с предоставленными сервисами"""
        # Этот метод должен быть переопределен в наследниках
        pass

# ================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ BEST PRACTICES
# ================================

class ResilientOrderCoordinator(DIAwareCoordinator):
    """Отказоустойчивый координатор заказов с лучшими практиками"""
    
    def __init__(self):
        super().__init__("resilient_order")
        self.setup_circuit_breakers()
    
    def setup_circuit_breakers(self):
        """Настраивает circuit breakers для сервисов"""
        self.add_circuit_breaker("payment", failure_threshold=3, recovery_timeout=30)
        self.add_circuit_breaker("inventory", failure_threshold=5, recovery_timeout=60)
        self.add_circuit_breaker("notification", failure_threshold=10, recovery_timeout=120)
    
    @with_retry(max_retries=3, delay=1.0, backoff_factor=2.0)
    async def coordinate(self, operation: str, *args, **kwargs):
        """Координирует операцию с retry логикой"""
        
        if operation == "process_order":
            return await self._process_order_resilient(*args, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _process_order_resilient(self, order_data: Dict, **kwargs):
        """Отказоустойчивая обработка заказа"""
        
        correlation_id = kwargs.get('correlation_id', 'unknown')
        self._logger.info(f"Processing order {order_data['order_id']} [{correlation_id}]")
        
        try:
            # Получаем сервисы через DI
            inventory_service = self.get_service("inventory")
            payment_service = self.get_service("payment")
            notification_service = self.get_service("notification")
            
            # Шаг 1: Резервируем товары с circuit breaker
            inventory_cb = self._circuit_breakers["inventory"]
            reservation_result = await inventory_cb.call(
                inventory_service.reserve_items, order_data
            )
            
            # Добавляем компенсацию для резервирования
            self.add_compensating_action(
                lambda: inventory_service.release_items(order_data)
            )
            
            # Шаг 2: Обрабатываем платеж с circuit breaker
            payment_cb = self._circuit_breakers["payment"]
            payment_result = await payment_cb.call(
                payment_service.process_payment, order_data
            )
            
            # Добавляем компенсацию для платежа
            self.add_compensating_action(
                lambda: payment_service.refund_payment(payment_result["transaction_id"])
            )
            
            # Шаг 3: Отправляем уведомления (не критично, можно игнорировать ошибки)
            try:
                notification_cb = self._circuit_breakers["notification"]
                await notification_cb.call(
                    notification_service.send_confirmation, order_data
                )
            except Exception as e:
                self._logger.warning(f"Notification failed (non-critical): {e}")
            
            return CoordinationResult(
                success=True,
                data={
                    "order_id": order_data["order_id"],
                    "reservation": reservation_result,
                    "payment": payment_result
                },
                metadata={"correlation_id": correlation_id}
            )
            
        except Exception as e:
            self._logger.error(f"Order processing failed [{correlation_id}]: {e}")
            return CoordinationResult(
                success=False,
                errors=[str(e)],
                metadata={"correlation_id": correlation_id, "order_id": order_data.get("order_id")}
            )

# Импорт для типизации (только для примера)
from coordinator_patterns import CoordinationResult

async def example_best_practices():
    """Пример использования best practices"""
    print("\n" + "=" * 60)
    print("🏆 COORDINATOR BEST PRACTICES EXAMPLE")
    print("=" * 60)
    
    # Настраиваем DI контейнер
    container = DIContainer()
    
    # Регистрируем сервисы
    from coordinator_examples import InventoryService, PaymentService, NotificationService
    
    container.register_instance("inventory", InventoryService())
    container.register_instance("payment", PaymentService())  
    container.register_instance("notification", NotificationService())
    
    # Создаем координатор
    coordinator = ResilientOrderCoordinator()
    container.wire_coordinator(coordinator)
    
    # Обрабатываем заказ
    order_data = {
        "order_id": "ORD_RESILIENT_001",
        "customer_email": "customer@example.com",
        "items": {"product_1": 2},
        "total_amount": 100.0
    }
    
    result = await coordinator.coordinate_with_metrics(
        "process_order", 
        order_data,
        correlation_id="test_correlation_123"
    )
    
    if result.success:
        print("✅ Resilient order processing completed!")
        print(f"📊 Metrics: {coordinator.get_metrics().__dict__}")
    else:
        print(f"❌ Order processing failed: {result.errors}")

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Запускаем пример
    asyncio.run(example_best_practices())