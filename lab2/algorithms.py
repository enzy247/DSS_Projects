"""
Алгоритмы генерации альтернатив распределения ресурсов.
Содержит логику для создания различных вариантов распределения ресурсов по задачам
с учетом приоритетов, загрузки ресурсов и других факторов.
"""

from typing import List, Dict, Tuple
from models import Resource, Task
import copy


def generate_alternatives(
    resources: List[Resource],
    tasks: List[Task]
) -> List[Dict]:
    """
    Генерация нескольких альтернатив распределения ресурсов по задачам.
    
    Создает различные варианты распределения, каждый со своим подходом:
    1. По приоритету задач (высокоприоритетные задачи получают ресурсы первыми)
    2. По равномерной загрузке (ресурсы загружаются равномерно)
    3. По специализации (ресурсы распределяются по типам)
    4. По минимизации перегрузки (избегаем перегрузки ресурсов)
    5. Жадный алгоритм с оптимизацией (максимизация покрытия)
    
    Args:
        resources: Список доступных ресурсов
        tasks: Список задач, требующих ресурсов
        
    Returns:
        List[Dict]: Список альтернатив, каждая содержит:
                    - "explanation": текстовое пояснение
                    - "score": оценочный балл
                    - "allocations": список распределений [{"resource_id": int, "task_id": int, "hours": float}]
    """
    alternatives = []
    
    if not resources or not tasks:
        return alternatives
    
    # Альтернатива 1: Распределение по приоритету задач
    alt1 = _priority_based_allocation(resources, tasks)
    if alt1:
        alternatives.append(alt1)
    
    # Альтернатива 2: Равномерное распределение ресурсов
    alt2 = _balanced_allocation(resources, tasks)
    if alt2:
        alternatives.append(alt2)
    
    # Альтернатива 3: Распределение с учетом специализации ресурсов
    alt3 = _specialization_based_allocation(resources, tasks)
    if alt3:
        alternatives.append(alt3)
    
    # Альтернатива 4: Минимизация перегрузки ресурсов
    alt4 = _minimize_overload_allocation(resources, tasks)
    if alt4:
        alternatives.append(alt4)
    
    # Альтернатива 5: Жадный алгоритм с оптимизацией
    alt5 = _greedy_optimized_allocation(resources, tasks)
    if alt5:
        alternatives.append(alt5)
    
    # Удаляем дубликаты и нормализуем распределения
    alternatives = _remove_duplicates(alternatives)
    alternatives = _normalize_allocations(alternatives)
    
    # Сортируем по баллу (лучшие первыми)
    alternatives.sort(key=lambda x: x["score"], reverse=True)
    
    return alternatives


def _priority_based_allocation(
    resources: List[Resource],
    tasks: List[Task]
) -> Dict:
    """
    Альтернатива 1: Распределение ресурсов по приоритету задач.
    Высокоприоритетные задачи получают ресурсы в первую очередь.
    
    Args:
        resources: Список ресурсов
        tasks: Список задач
        
    Returns:
        Dict: Альтернатива с пояснением, баллом и распределениями
    """
    # Сортируем задачи по приоритету (1 - высший, 5 - низший)
    sorted_tasks = sorted(tasks, key=lambda t: t.priority)
    
    # Создаем копии для отслеживания оставшихся часов
    resource_hours = {r.id: r.available_hours for r in resources}
    task_requirements = {t.id: t.required_hours for t in tasks}
    
    allocations = []
    total_allocated = 0
    
    # Распределяем ресурсы, начиная с высокоприоритетных задач
    for task in sorted_tasks:
        remaining_need = task_requirements[task.id]
        
        # Пытаемся распределить ресурсы на эту задачу
        for resource in resources:
            if remaining_need <= 0:
                break
            
            if resource_hours[resource.id] > 0:
                # Выделяем часы на задачу
                hours_to_allocate = min(remaining_need, resource_hours[resource.id])
                allocations.append({
                    "resource_id": resource.id,
                    "task_id": task.id,
                    "hours": hours_to_allocate
                })
                resource_hours[resource.id] -= hours_to_allocate
                remaining_need -= hours_to_allocate
                total_allocated += hours_to_allocate
    
    # Вычисляем балл: учитываем покрытие задач и приоритеты
    total_required = sum(t.required_hours for t in tasks)
    coverage = total_allocated / total_required if total_required > 0 else 0
    
    # Бонус за покрытие высокоприоритетных задач
    priority_coverage = {}
    for alloc in allocations:
        task_id = alloc["task_id"]
        if task_id not in priority_coverage:
            priority_coverage[task_id] = 0.0
        priority_coverage[task_id] += alloc["hours"]
    
    priority_bonus = sum(
        (6 - t.priority) * min(1.0, priority_coverage.get(t.id, 0) / t.required_hours)
        for t in sorted_tasks
    ) / len(tasks) if tasks else 0
    
    # Штраф за перегрузку ресурсов
    overload_penalty = sum(
        max(0, sum(a["hours"] for a in allocations if a["resource_id"] == r.id) - r.available_hours)
        for r in resources
    ) / total_required if total_required > 0 else 0
    
    score = coverage * 50 + priority_bonus * 20 - overload_penalty * 30
    score = max(0, score)  # Не даем отрицательный балл
    
    explanation = (
        f"Распределение по приоритету задач. Высокоприоритетные задачи получают ресурсы первыми. "
        f"Покрыто {coverage*100:.1f}% требуемых часов. "
        f"Приоритет отдается задачам с приоритетом 1-{sorted_tasks[0].priority if sorted_tasks else 'N/A'}."
    )
    
    return {
        "explanation": explanation,
        "score": score,
        "allocations": allocations
    }


def _balanced_allocation(
    resources: List[Resource],
    tasks: List[Task]
) -> Dict:
    """
    Альтернатива 2: Равномерное распределение ресурсов по задачам.
    Каждая задача получает пропорциональную долю доступных ресурсов.
    
    Args:
        resources: Список ресурсов
        tasks: Список задач
        
    Returns:
        Dict: Альтернатива с пояснением, баллом и распределениями
    """
    total_available = sum(r.available_hours for r in resources)
    total_required = sum(t.required_hours for t in tasks)
    
    if total_available == 0 or total_required == 0:
        return None
    
    # Вычисляем пропорцию для каждой задачи
    task_proportions = {
        t.id: t.required_hours / total_required
        for t in tasks
    }
    
    resource_hours = {r.id: r.available_hours for r in resources}
    allocations = []
    total_allocated = 0
    
    # Распределяем ресурсы пропорционально потребностям задач
    for task in tasks:
        task_share = task_proportions[task.id] * total_available
        allocated_to_task = 0
        
        for resource in resources:
            if allocated_to_task >= task_share:
                break
            
            if resource_hours[resource.id] > 0:
                remaining_need = task_share - allocated_to_task
                hours_to_allocate = min(remaining_need, resource_hours[resource.id])
                
                allocations.append({
                    "resource_id": resource.id,
                    "task_id": task.id,
                    "hours": hours_to_allocate
                })
                resource_hours[resource.id] -= hours_to_allocate
                allocated_to_task += hours_to_allocate
                total_allocated += hours_to_allocate
    
    # Балл основан на равномерности распределения
    coverage = total_allocated / total_required if total_required > 0 else 0
    balance_score = 1.0 - _calculate_balance_variance(resources, allocations)
    
    # Проверяем равномерность покрытия задач
    task_coverage = {}
    for alloc in allocations:
        if alloc["task_id"] not in task_coverage:
            task_coverage[alloc["task_id"]] = 0.0
        task_coverage[alloc["task_id"]] += alloc["hours"]
    
    task_coverage_variance = 0.0
    if tasks:
        coverage_ratios = [
            task_coverage.get(t.id, 0) / t.required_hours
            for t in tasks
        ]
        mean_coverage = sum(coverage_ratios) / len(coverage_ratios)
        task_coverage_variance = sum((r - mean_coverage) ** 2 for r in coverage_ratios) / len(coverage_ratios)
    
    fairness_score = 1.0 - min(1.0, task_coverage_variance)
    
    score = coverage * 40 + balance_score * 25 + fairness_score * 15
    
    explanation = (
        f"Равномерное распределение ресурсов. Каждая задача получает пропорциональную долю "
        f"доступных ресурсов в соответствии с ее потребностями. "
        f"Покрыто {coverage*100:.1f}% требуемых часов. "
        f"Это обеспечивает справедливое распределение нагрузки между задачами."
    )
    
    return {
        "explanation": explanation,
        "score": score,
        "allocations": allocations
    }


def _specialization_based_allocation(
    resources: List[Resource],
    tasks: List[Task]
) -> Dict:
    """
    Альтернатива 3: Распределение с учетом специализации ресурсов.
    Улучшенный алгоритм: пытается сопоставить типы ресурсов с задачами на основе ключевых слов.
    
    Args:
        resources: Список ресурсов
        tasks: Список задач
        
    Returns:
        Dict: Альтернатива с пояснением, баллом и распределениями
    """
    # Группируем ресурсы по типам
    resources_by_type = {}
    for resource in resources:
        if resource.type not in resources_by_type:
            resources_by_type[resource.type] = []
        resources_by_type[resource.type].append(resource)
    
    # Создаем словарь соответствий типов ресурсов и задач
    type_matching = {
        "разработчик": ["разработка", "код", "программирование", "функционал", "система"],
        "дизайнер": ["дизайн", "интерфейс", "ui", "ux", "макет"],
        "тестировщик": ["тестирование", "тест", "проверка", "qa"],
        "аналитик": ["анализ", "требования", "документация", "исследование"],
        "менеджер проекта": ["проект", "управление", "координация", "планирование"]
    }
    
    resource_hours = {r.id: r.available_hours for r in resources}
    task_requirements = {t.id: t.required_hours for t in tasks}
    resource_allocated = {r.id: 0.0 for r in resources}
    
    allocations = []
    total_allocated = 0
    type_matches = 0
    
    # Сортируем задачи по приоритету
    sorted_tasks = sorted(tasks, key=lambda t: (t.priority, -t.required_hours))
    
    for task in sorted_tasks:
        remaining_need = task_requirements[task.id]
        task_title_lower = task.title.lower()
        
        # Находим подходящие типы ресурсов для задачи
        suitable_types = []
        for resource_type, keywords in type_matching.items():
            if any(keyword in task_title_lower for keyword in keywords):
                suitable_types.append(resource_type)
        
        # Сначала пытаемся использовать подходящие типы ресурсов
        resources_to_try = []
        if suitable_types:
            for resource_type in suitable_types:
                if resource_type in resources_by_type:
                    resources_to_try.extend(resources_by_type[resource_type])
        else:
            # Если нет подходящих типов, используем все ресурсы
            resources_to_try = resources
        
        # Распределяем ресурсы на задачу
        for resource in resources_to_try:
            if remaining_need <= 0:
                break
            
            if resource_hours[resource.id] > 0:
                hours_to_allocate = min(remaining_need, resource_hours[resource.id])
                allocations.append({
                    "resource_id": resource.id,
                    "task_id": task.id,
                    "hours": hours_to_allocate
                })
                resource_hours[resource.id] -= hours_to_allocate
                resource_allocated[resource.id] += hours_to_allocate
                remaining_need -= hours_to_allocate
                total_allocated += hours_to_allocate
                
                # Проверяем, было ли это совпадение по типу
                if resource.type in suitable_types:
                    type_matches += 1
        
        # Если задача не полностью покрыта, используем остальные ресурсы
        if remaining_need > 0:
            for resource in resources:
                if remaining_need <= 0:
                    break
                if resource_hours[resource.id] > 0 and resource not in resources_to_try:
                    hours_to_allocate = min(remaining_need, resource_hours[resource.id])
                    allocations.append({
                        "resource_id": resource.id,
                        "task_id": task.id,
                        "hours": hours_to_allocate
                    })
                    resource_hours[resource.id] -= hours_to_allocate
                    resource_allocated[resource.id] += hours_to_allocate
                    remaining_need -= hours_to_allocate
                    total_allocated += hours_to_allocate
    
    total_required = sum(t.required_hours for t in tasks)
    coverage = total_allocated / total_required if total_required > 0 else 0
    
    # Балл учитывает покрытие, использование различных типов и совпадения
    type_diversity = len(set(r.type for r in resources if any(
        a["resource_id"] == r.id for a in allocations
    )))
    match_ratio = type_matches / len(allocations) if allocations else 0
    
    score = coverage * 40 + (type_diversity / len(resources_by_type)) * 20 if resources_by_type else coverage * 40
    score += match_ratio * 15
    
    explanation = (
        f"Распределение с учетом специализации ресурсов. "
        f"Учитываются типы ресурсов ({', '.join(resources_by_type.keys())}) "
        f"для оптимального их использования. Покрыто {coverage*100:.1f}% требуемых часов. "
        f"Использовано {type_diversity} различных типов ресурсов. "
        f"Совпадение по специализации: {match_ratio*100:.1f}%."
    )
    
    return {
        "explanation": explanation,
        "score": score,
        "allocations": allocations
    }


def _minimize_overload_allocation(
    resources: List[Resource],
    tasks: List[Task]
) -> Dict:
    """
    Альтернатива 4: Минимизация перегрузки ресурсов.
    Старается распределить нагрузку так, чтобы ни один ресурс не был перегружен.
    
    Args:
        resources: Список ресурсов
        tasks: Список задач
        
    Returns:
        Dict: Альтернатива с пояснением, баллом и распределениями
    """
    total_required = sum(t.required_hours for t in tasks)
    total_available = sum(r.available_hours for r in resources)
    
    if total_available == 0:
        return None
    
    # Вычисляем идеальную нагрузку на ресурс
    ideal_load_per_resource = total_required / len(resources) if resources else 0
    
    resource_hours = {r.id: r.available_hours for r in resources}
    resource_allocated = {r.id: 0.0 for r in resources}
    task_requirements = {t.id: t.required_hours for t in tasks}
    
    allocations = []
    
    # Сортируем задачи по приоритету и размеру
    sorted_tasks = sorted(tasks, key=lambda t: (t.priority, -t.required_hours))
    
    for task in sorted_tasks:
        remaining_need = task_requirements[task.id]
        
        # Выбираем ресурсы с наименьшей текущей загрузкой
        while remaining_need > 0:
            # Находим ресурс с минимальной загрузкой, у которого еще есть свободные часы
            available_resources = [
                r for r in resources
                if resource_hours[r.id] > 0 and resource_allocated[r.id] < ideal_load_per_resource * 1.2
            ]
            
            if not available_resources:
                # Если нет идеальных ресурсов, берем любой доступный
                available_resources = [r for r in resources if resource_hours[r.id] > 0]
            
            if not available_resources:
                break
            
            # Выбираем ресурс с минимальной загрузкой
            best_resource = min(
                available_resources,
                key=lambda r: resource_allocated[r.id]
            )
            
            hours_to_allocate = min(
                remaining_need,
                resource_hours[best_resource.id],
                ideal_load_per_resource * 1.2 - resource_allocated[best_resource.id]
            )
            
            if hours_to_allocate > 0:
                allocations.append({
                    "resource_id": best_resource.id,
                    "task_id": task.id,
                    "hours": hours_to_allocate
                })
                resource_hours[best_resource.id] -= hours_to_allocate
                resource_allocated[best_resource.id] += hours_to_allocate
                remaining_need -= hours_to_allocate
    
    total_allocated = sum(a["hours"] for a in allocations)
    coverage = total_allocated / total_required if total_required > 0 else 0
    
    # Балл учитывает покрытие и равномерность загрузки
    overload_penalty = sum(
        max(0, resource_allocated[r.id] - r.available_hours)
        for r in resources
    )
    balance = 1.0 - (overload_penalty / total_required) if total_required > 0 else 1.0
    score = coverage * 40 + balance * 35
    
    explanation = (
        f"Распределение с минимизацией перегрузки ресурсов. "
        f"Нагрузка распределяется равномерно, избегая перегрузки отдельных ресурсов. "
        f"Покрыто {coverage*100:.1f}% требуемых часов. "
        f"Максимальная загрузка ресурса: {max(resource_allocated.values()):.1f} часов."
    )
    
    return {
        "explanation": explanation,
        "score": score,
        "allocations": allocations
    }


def _calculate_balance_variance(
    resources: List[Resource],
    allocations: List[Dict]
) -> float:
    """
    Вычисление дисперсии загрузки ресурсов для оценки равномерности распределения.
    
    Args:
        resources: Список ресурсов
        allocations: Список распределений
        
    Returns:
        float: Нормализованная дисперсия (0 - идеально равномерно, 1 - очень неравномерно)
    """
    resource_load = {r.id: 0.0 for r in resources}
    
    for alloc in allocations:
        resource_load[alloc["resource_id"]] += alloc["hours"]
    
    loads = [
        resource_load[r.id] / r.available_hours if r.available_hours > 0 else 0
        for r in resources
    ]
    
    if not loads:
        return 0.0
    
    mean_load = sum(loads) / len(loads)
    variance = sum((load - mean_load) ** 2 for load in loads) / len(loads)
    
    # Нормализуем к диапазону [0, 1]
    return min(1.0, variance)


def _greedy_optimized_allocation(
    resources: List[Resource],
    tasks: List[Task]
) -> Dict:
    """
    Альтернатива 5: Жадный алгоритм с оптимизацией покрытия.
    Максимизирует покрытие задач, используя наиболее эффективные ресурсы.
    
    Args:
        resources: Список ресурсов
        tasks: Список задач
        
    Returns:
        Dict: Альтернатива с пояснением, баллом и распределениями
    """
    # Сортируем задачи по приоритету и размеру (важные и большие первыми)
    sorted_tasks = sorted(tasks, key=lambda t: (t.priority, -t.required_hours))
    
    resource_hours = {r.id: r.available_hours for r in resources}
    task_requirements = {t.id: t.required_hours for t in tasks}
    resource_allocated = {r.id: 0.0 for r in resources}
    
    allocations = []
    total_allocated = 0
    
    # Жадный алгоритм: для каждой задачи выбираем лучший доступный ресурс
    for task in sorted_tasks:
        remaining_need = task_requirements[task.id]
        
        while remaining_need > 0:
            # Находим ресурсы, которые могут помочь с этой задачей
            available_resources = [
                r for r in resources
                if resource_hours[r.id] > 0.1  # Минимальный порог
            ]
            
            if not available_resources:
                break
            
            # Выбираем ресурс с максимальной эффективностью
            # Эффективность = доступные часы / текущая загрузка (если загружен)
            best_resource = max(
                available_resources,
                key=lambda r: (
                    resource_hours[r.id] / max(resource_allocated[r.id], 1.0),
                    resource_hours[r.id]  # При равной эффективности берем больше часов
                )
            )
            
            hours_to_allocate = min(
                remaining_need,
                resource_hours[best_resource.id]
            )
            
            if hours_to_allocate > 0.1:  # Игнорируем очень маленькие распределения
                allocations.append({
                    "resource_id": best_resource.id,
                    "task_id": task.id,
                    "hours": hours_to_allocate
                })
                resource_hours[best_resource.id] -= hours_to_allocate
                resource_allocated[best_resource.id] += hours_to_allocate
                remaining_need -= hours_to_allocate
                total_allocated += hours_to_allocate
    
    total_required = sum(t.required_hours for t in tasks)
    coverage = total_allocated / total_required if total_required > 0 else 0
    
    # Балл учитывает покрытие и эффективность использования ресурсов
    efficiency = sum(
        min(1.0, resource_allocated[r.id] / r.available_hours)
        for r in resources
        if r.available_hours > 0
    ) / len(resources) if resources else 0
    
    priority_coverage = sum(
        (6 - t.priority) * min(1.0, (task_requirements[t.id] - (task_requirements[t.id] - sum(
            a["hours"] for a in allocations if a["task_id"] == t.id
        ))) / task_requirements[t.id])
        for t in sorted_tasks
    ) / len(tasks) if tasks else 0
    
    score = coverage * 50 + efficiency * 25 + priority_coverage * 15
    
    explanation = (
        f"Жадный алгоритм с оптимизацией покрытия. Максимизирует покрытие задач, "
        f"используя наиболее эффективные ресурсы. Покрыто {coverage*100:.1f}% требуемых часов. "
        f"Эффективность использования ресурсов: {efficiency*100:.1f}%."
    )
    
    return {
        "explanation": explanation,
        "score": score,
        "allocations": allocations
    }


def _remove_duplicates(alternatives: List[Dict]) -> List[Dict]:
    """
    Удаление дубликатов альтернатив.
    Две альтернативы считаются дубликатами, если их распределения идентичны.
    
    Args:
        alternatives: Список альтернатив
        
    Returns:
        List[Dict]: Список альтернатив без дубликатов
    """
    seen = set()
    unique_alternatives = []
    
    for alt in alternatives:
        # Создаем уникальный ключ на основе распределений
        allocations_key = tuple(
            sorted(
                (a["resource_id"], a["task_id"], round(a["hours"], 1))
                for a in alt["allocations"]
            )
        )
        
        if allocations_key not in seen:
            seen.add(allocations_key)
            unique_alternatives.append(alt)
        else:
            # Если дубликат найден, оставляем альтернативу с лучшим баллом
            for i, existing_alt in enumerate(unique_alternatives):
                existing_key = tuple(
                    sorted(
                        (a["resource_id"], a["task_id"], round(a["hours"], 1))
                        for a in existing_alt["allocations"]
                    )
                )
                if existing_key == allocations_key and alt["score"] > existing_alt["score"]:
                    unique_alternatives[i] = alt
                    break
    
    return unique_alternatives


def _normalize_allocations(alternatives: List[Dict]) -> List[Dict]:
    """
    Нормализация распределений: удаление очень маленьких распределений (< 0.5 часов)
    и объединение распределений одного ресурса на одну задачу.
    
    Args:
        alternatives: Список альтернатив
        
    Returns:
        List[Dict]: Список альтернатив с нормализованными распределениями
    """
    normalized = []
    
    for alt in alternatives:
        # Группируем распределения по ресурсу и задаче
        grouped = {}
        for alloc in alt["allocations"]:
            key = (alloc["resource_id"], alloc["task_id"])
            if key not in grouped:
                grouped[key] = 0.0
            grouped[key] += alloc["hours"]
        
        # Создаем нормализованные распределения (убираем очень маленькие)
        normalized_allocations = [
            {
                "resource_id": resource_id,
                "task_id": task_id,
                "hours": round(hours, 1)
            }
            for (resource_id, task_id), hours in grouped.items()
            if hours >= 0.5  # Минимальный порог
        ]
        
        if normalized_allocations:
            normalized.append({
                "explanation": alt["explanation"],
                "score": alt["score"],
                "allocations": normalized_allocations
            })
    
    return normalized





