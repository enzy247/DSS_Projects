"""
Модуль с примерами данных для тестирования системы.
Содержит функции для создания тестовых ресурсов и задач.
"""

from schemas import ResourceCreate, TaskCreate


def get_example_resources():
    """
    Возвращает список примеров ресурсов для тестирования.
    
    Returns:
        List[ResourceCreate]: Список ресурсов
    """
    return [
        ResourceCreate(
            name="Иван Иванов",
            type="разработчик",
            available_hours=160.0
        ),
        ResourceCreate(
            name="Мария Петрова",
            type="дизайнер",
            available_hours=120.0
        ),
        ResourceCreate(
            name="Алексей Сидоров",
            type="разработчик",
            available_hours=140.0
        ),
        ResourceCreate(
            name="Анна Козлова",
            type="тестировщик",
            available_hours=100.0
        ),
        ResourceCreate(
            name="Дмитрий Волков",
            type="менеджер проекта",
            available_hours=80.0
        ),
    ]


def get_example_tasks():
    """
    Возвращает список примеров задач для тестирования.
    
    Returns:
        List[TaskCreate]: Список задач
    """
    return [
        TaskCreate(
            title="Разработка нового функционала",
            required_hours=200.0,
            priority=1
        ),
        TaskCreate(
            title="Дизайн пользовательского интерфейса",
            required_hours=80.0,
            priority=2
        ),
        TaskCreate(
            title="Тестирование системы",
            required_hours=120.0,
            priority=2
        ),
        TaskCreate(
            title="Документация проекта",
            required_hours=60.0,
            priority=3
        ),
        TaskCreate(
            title="Оптимизация производительности",
            required_hours=100.0,
            priority=3
        ),
    ]





