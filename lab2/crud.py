"""
CRUD операции для работы с базой данных.
Содержит функции для создания, чтения, обновления и удаления записей.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from models import Resource, Task, Alternative, Allocation, UserChoice
from schemas import ResourceCreate, TaskCreate


# ========== Операции с ресурсами ==========

def create_resource(db: Session, resource: ResourceCreate) -> Resource:
    """
    Создание нового ресурса в базе данных.
    
    Args:
        db: Сессия базы данных
        resource: Данные ресурса для создания
        
    Returns:
        Resource: Созданный ресурс
    """
    db_resource = Resource(
        name=resource.name,
        type=resource.type,
        available_hours=resource.available_hours
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


def get_resource(db: Session, resource_id: int) -> Optional[Resource]:
    """
    Получение ресурса по ID.
    
    Args:
        db: Сессия базы данных
        resource_id: ID ресурса
        
    Returns:
        Resource или None, если ресурс не найден
    """
    return db.query(Resource).filter(Resource.id == resource_id).first()


def get_all_resources(db: Session) -> List[Resource]:
    """
    Получение всех ресурсов из базы данных.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Resource]: Список всех ресурсов
    """
    return db.query(Resource).all()


def update_resource(
    db: Session,
    resource_id: int,
    name: Optional[str] = None,
    type: Optional[str] = None,
    available_hours: Optional[float] = None
) -> Optional[Resource]:
    """
    Обновление ресурса в базе данных.
    
    Args:
        db: Сессия базы данных
        resource_id: ID ресурса для обновления
        name: Новое имя (опционально)
        type: Новый тип (опционально)
        available_hours: Новое количество часов (опционально)
        
    Returns:
        Resource или None, если ресурс не найден
    """
    db_resource = get_resource(db, resource_id)
    if not db_resource:
        return None
    
    if name is not None:
        db_resource.name = name
    if type is not None:
        db_resource.type = type
    if available_hours is not None:
        db_resource.available_hours = available_hours
    
    db.commit()
    db.refresh(db_resource)
    return db_resource


def delete_resource(db: Session, resource_id: int) -> bool:
    """
    Удаление ресурса из базы данных.
    
    Args:
        db: Сессия базы данных
        resource_id: ID ресурса для удаления
        
    Returns:
        bool: True если ресурс удален, False если не найден
    """
    db_resource = get_resource(db, resource_id)
    if not db_resource:
        return False
    
    db.delete(db_resource)
    db.commit()
    return True


# ========== Операции с задачами ==========

def create_task(db: Session, task: TaskCreate) -> Task:
    """
    Создание новой задачи в базе данных.
    
    Args:
        db: Сессия базы данных
        task: Данные задачи для создания
        
    Returns:
        Task: Созданная задача
    """
    db_task = Task(
        title=task.title,
        required_hours=task.required_hours,
        priority=task.priority
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    """
    Получение задачи по ID.
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи
        
    Returns:
        Task или None, если задача не найдена
    """
    return db.query(Task).filter(Task.id == task_id).first()


def get_all_tasks(db: Session) -> List[Task]:
    """
    Получение всех задач из базы данных.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Task]: Список всех задач
    """
    return db.query(Task).all()


def update_task(
    db: Session,
    task_id: int,
    title: Optional[str] = None,
    required_hours: Optional[float] = None,
    priority: Optional[int] = None
) -> Optional[Task]:
    """
    Обновление задачи в базе данных.
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи для обновления
        title: Новое название (опционально)
        required_hours: Новое количество часов (опционально)
        priority: Новый приоритет (опционально)
        
    Returns:
        Task или None, если задача не найдена
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    if title is not None:
        db_task.title = title
    if required_hours is not None:
        db_task.required_hours = required_hours
    if priority is not None:
        db_task.priority = priority
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """
    Удаление задачи из базы данных.
    
    Args:
        db: Сессия базы данных
        task_id: ID задачи для удаления
        
    Returns:
        bool: True если задача удалена, False если не найдена
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True


# ========== Операции с альтернативами ==========

def create_alternative(
    db: Session,
    explanation: str,
    score: float,
    allocations: List[dict]
) -> Alternative:
    """
    Создание новой альтернативы с распределениями ресурсов.
    
    Args:
        db: Сессия базы данных
        explanation: Текстовое пояснение альтернативы
        score: Оценочный балл альтернативы
        allocations: Список словарей с данными распределений:
                     [{"resource_id": int, "task_id": int, "hours": float}, ...]
        
    Returns:
        Alternative: Созданная альтернатива
    """
    db_alternative = Alternative(
        explanation=explanation,
        score=score
    )
    db.add(db_alternative)
    db.flush()  # Получаем ID альтернативы
    
    # Создаем распределения ресурсов
    for alloc_data in allocations:
        db_allocation = Allocation(
            alternative_id=db_alternative.id,
            resource_id=alloc_data["resource_id"],
            task_id=alloc_data["task_id"],
            hours=alloc_data["hours"]
        )
        db.add(db_allocation)
    
    db.commit()
    db.refresh(db_alternative)
    return db_alternative


def get_all_alternatives(db: Session) -> List[Alternative]:
    """
    Получение всех альтернатив, отсортированных по баллу (лучшие первыми).
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Alternative]: Список альтернатив, отсортированный по убыванию score
    """
    return db.query(Alternative).order_by(desc(Alternative.score)).all()


def delete_all_alternatives(db: Session) -> None:
    """
    Удаление всех альтернатив из базы данных.
    Используется перед генерацией новых альтернатив.
    Сначала удаляет все распределения (Allocation).
    
    Args:
        db: Сессия базы данных
    """
    # Сначала удаляем все распределения
    db.query(Allocation).delete()
    db.commit()
    
    # Затем удаляем альтернативы
    db.query(Alternative).delete()
    db.commit()


def delete_all_resources(db: Session) -> int:
    """
    Удаление всех ресурсов из базы данных.
    Сначала удаляет все связанные распределения (Allocation).
    
    Args:
        db: Сессия базы данных
        
    Returns:
        int: Количество удаленных ресурсов
    """
    # Сначала удаляем все распределения, связанные с ресурсами
    db.query(Allocation).delete()
    db.commit()
    
    count = db.query(Resource).count()
    db.query(Resource).delete()
    db.commit()
    return count


def delete_all_tasks(db: Session) -> int:
    """
    Удаление всех задач из базы данных.
    Сначала удаляет все связанные распределения (Allocation).
    
    Args:
        db: Сессия базы данных
        
    Returns:
        int: Количество удаленных задач
    """
    # Сначала удаляем все распределения, связанные с задачами
    db.query(Allocation).delete()
    db.commit()
    
    count = db.query(Task).count()
    db.query(Task).delete()
    db.commit()
    return count


def save_user_choice(
    db: Session,
    alternative_id: int,
    coverage: float,
    priority_score: float,
    balance_score: float,
    overload_penalty: float,
    total_score: float,
    num_resources: int,
    num_tasks: int,
    ml_score: Optional[float] = None
) -> UserChoice:
    """
    Сохранение выбранной пользователем альтернативы для обучения ML модели.
    
    Args:
        db: Сессия базы данных
        alternative_id: ID выбранной альтернативы
        coverage: Процент покрытия задач
        priority_score: Оценка по приоритетам
        balance_score: Оценка равномерности
        overload_penalty: Штраф за перегрузку
        total_score: Общий балл альтернативы
        num_resources: Количество ресурсов
        num_tasks: Количество задач
        ml_score: Предсказанная ML моделью вероятность (опционально)
        
    Returns:
        UserChoice: Сохраненный выбор
    """
    choice = UserChoice(
        alternative_id=alternative_id,
        coverage=coverage,
        priority_score=priority_score,
        balance_score=balance_score,
        overload_penalty=overload_penalty,
        total_score=total_score,
        num_resources=num_resources,
        num_tasks=num_tasks,
        ml_score=ml_score
    )
    db.add(choice)
    db.commit()
    db.refresh(choice)
    return choice


def get_all_user_choices(db: Session) -> List[UserChoice]:
    """
    Получение всех выборов пользователя для обучения ML модели.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[UserChoice]: Список всех выборов
    """
    return db.query(UserChoice).order_by(desc(UserChoice.selected_at)).all()


def clear_all_data(db: Session) -> dict:
    """
    Полная очистка всех данных из базы данных.
    Удаляет все ресурсы, задачи и альтернативы.
    Важно: удаление происходит в правильном порядке из-за внешних ключей.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        dict: Статистика удаленных данных
    """
    # Подсчитываем количество перед удалением
    resources_count = db.query(Resource).count()
    tasks_count = db.query(Task).count()
    alternatives_count = db.query(Alternative).count()
    
    # Удаляем в правильном порядке:
    # 1. Сначала все распределения (Allocation) - они ссылаются на все остальное
    db.query(Allocation).delete()
    db.commit()
    
    # 2. Затем альтернативы
    db.query(Alternative).delete()
    db.commit()
    
    # 3. Потом ресурсы
    db.query(Resource).delete()
    db.commit()
    
    # 4. И наконец задачи
    db.query(Task).delete()
    db.commit()
    
    return {
        "resources_deleted": resources_count,
        "tasks_deleted": tasks_count,
        "alternatives_deleted": alternatives_count,
        "message": "Все данные успешно удалены"
    }


def get_alternative(db: Session, alternative_id: int) -> Optional[Alternative]:
    """
    Получение альтернативы по ID.
    
    Args:
        db: Сессия базы данных
        alternative_id: ID альтернативы
        
    Returns:
        Alternative или None, если альтернатива не найдена
    """
    return db.query(Alternative).filter(Alternative.id == alternative_id).first()


# ========== Статистика и аналитика ==========

def calculate_distribution_stats(
    db: Session,
    alternative_id: Optional[int] = None
) -> dict:
    """
    Расчет статистики распределения ресурсов.
    
    Args:
        db: Сессия базы данных
        alternative_id: ID альтернативы (если None, берется лучшая альтернатива)
        
    Returns:
        dict: Словарь со статистикой
    """
    resources = get_all_resources(db)
    tasks = get_all_tasks(db)
    
    if alternative_id:
        alternative = get_alternative(db, alternative_id)
    else:
        alternatives = get_all_alternatives(db)
        alternative = alternatives[0] if alternatives else None
    
    if not alternative:
        return {
            "total_resources": len(resources),
            "total_tasks": len(tasks),
            "total_available_hours": sum(r.available_hours for r in resources),
            "total_required_hours": sum(t.required_hours for t in tasks),
            "total_allocated_hours": 0.0,
            "overall_coverage_percent": 0.0,
            "resource_stats": [],
            "task_stats": [],
            "warnings": ["Нет альтернатив для анализа"]
        }
    
    # Статистика по ресурсам
    resource_allocated = {r.id: 0.0 for r in resources}
    for alloc in alternative.allocations:
        resource_allocated[alloc.resource_id] += alloc.hours
    
    resource_stats = []
    warnings = []
    
    for resource in resources:
        allocated = resource_allocated.get(resource.id, 0.0)
        utilization = (allocated / resource.available_hours * 100) if resource.available_hours > 0 else 0
        overload = allocated > resource.available_hours
        
        if overload:
            warnings.append(
                f"⚠️ Ресурс '{resource.name}' перегружен: "
                f"выделено {allocated:.1f} часов из {resource.available_hours:.1f} доступных"
            )
        
        resource_stats.append({
            "resource_id": resource.id,
            "resource_name": resource.name,
            "available_hours": resource.available_hours,
            "allocated_hours": allocated,
            "utilization_percent": utilization,
            "overload": overload
        })
    
    # Статистика по задачам
    task_allocated = {t.id: 0.0 for t in tasks}
    for alloc in alternative.allocations:
        task_allocated[alloc.task_id] += alloc.hours
    
    task_stats = []
    for task in tasks:
        allocated = task_allocated.get(task.id, 0.0)
        coverage = (allocated / task.required_hours * 100) if task.required_hours > 0 else 0
        
        if allocated < task.required_hours:
            warnings.append(
                f"⚠️ Задача '{task.title}' не полностью покрыта: "
                f"выделено {allocated:.1f} часов из {task.required_hours:.1f} требуемых"
            )
        
        task_stats.append({
            "task_id": task.id,
            "task_title": task.title,
            "required_hours": task.required_hours,
            "allocated_hours": allocated,
            "coverage_percent": coverage,
            "priority": task.priority
        })
    
    total_available = sum(r.available_hours for r in resources)
    total_required = sum(t.required_hours for t in tasks)
    total_allocated = sum(resource_allocated.values())
    overall_coverage = (total_allocated / total_required * 100) if total_required > 0 else 0
    
    if total_required > total_available:
        warnings.append(
            f"⚠️ Недостаточно ресурсов: требуется {total_required:.1f} часов, "
            f"доступно {total_available:.1f} часов"
        )
    
    return {
        "total_resources": len(resources),
        "total_tasks": len(tasks),
        "total_available_hours": total_available,
        "total_required_hours": total_required,
        "total_allocated_hours": total_allocated,
        "overall_coverage_percent": overall_coverage,
        "resource_stats": resource_stats,
        "task_stats": task_stats,
        "warnings": warnings
    }

