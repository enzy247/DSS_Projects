"""
Примеры использования API системы поддержки принятия решений.
Этот файл содержит примеры вызовов API для тестирования системы.
"""

import requests
import json

# Базовый URL API
BASE_URL = "http://localhost:8000"


def print_response(response):
    """Красивый вывод ответа API."""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print("-" * 80)


# ========== Пример 1: Загрузка примерных данных ==========
print("=" * 80)
print("Пример 1: Загрузка примерных данных")
print("=" * 80)
response = requests.post(f"{BASE_URL}/load-example-data")
print_response(response)


# ========== Пример 2: Добавление ресурса ==========
print("\n" + "=" * 80)
print("Пример 2: Добавление нового ресурса")
print("=" * 80)
new_resource = {
    "name": "Петр Смирнов",
    "type": "разработчик",
    "available_hours": 150.0
}
response = requests.post(
    f"{BASE_URL}/resource",
    json=new_resource
)
print_response(response)


# ========== Пример 3: Добавление задачи ==========
print("\n" + "=" * 80)
print("Пример 3: Добавление новой задачи")
print("=" * 80)
new_task = {
    "title": "Рефакторинг кодовой базы",
    "required_hours": 90.0,
    "priority": 2
}
response = requests.post(
    f"{BASE_URL}/task",
    json=new_task
)
print_response(response)


# ========== Пример 4: Получение всех ресурсов ==========
print("\n" + "=" * 80)
print("Пример 4: Получение списка всех ресурсов")
print("=" * 80)
response = requests.get(f"{BASE_URL}/resources")
print_response(response)


# ========== Пример 5: Получение всех задач ==========
print("\n" + "=" * 80)
print("Пример 5: Получение списка всех задач")
print("=" * 80)
response = requests.get(f"{BASE_URL}/tasks")
print_response(response)


# ========== Пример 6: Получение альтернатив распределения ==========
print("\n" + "=" * 80)
print("Пример 6: Получение альтернатив распределения ресурсов")
print("=" * 80)
response = requests.get(f"{BASE_URL}/alternatives")
print_response(response)

# Выводим детали каждой альтернативы
if response.status_code == 200:
    data = response.json()
    print(f"\nВсего альтернатив: {data['total']}")
    for i, alt in enumerate(data['alternatives'], 1):
        print(f"\n--- Альтернатива {i} (Балл: {alt['score']:.2f}) ---")
        print(f"Пояснение: {alt['explanation']}")
        print(f"Распределения:")
        for alloc in alt['allocations']:
            print(f"  - {alloc['resource_name']} -> {alloc['task_title']}: {alloc['hours']:.1f} часов")


print("\n" + "=" * 80)
print("Примеры использования API завершены!")
print("=" * 80)
print("\nДля запуска этих примеров:")
print("1. Убедитесь, что сервер запущен: uvicorn main:app --reload")
print("2. Установите requests: pip install requests")
print("3. Запустите: python example_api_usage.py")





