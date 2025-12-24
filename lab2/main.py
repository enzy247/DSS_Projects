"""
Главный файл FastAPI приложения.
Содержит все API endpoints для работы с системой поддержки принятия решений.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

from database import get_db, init_db
from schemas import (
    ResourceCreate, Resource, ResourceUpdate,
    TaskCreate, Task, TaskUpdate,
    AlternativesListResponse, AlternativeResponse, AllocationResponse,
    DistributionStats, UserChoiceCreate, MLModelInfo
)
from crud import (
    create_resource, get_all_resources, get_resource,
    update_resource, delete_resource,
    create_task, get_all_tasks, get_task,
    update_task, delete_task,
    create_alternative, get_all_alternatives, get_alternative, delete_all_alternatives,
    calculate_distribution_stats, clear_all_data,
    save_user_choice, get_all_user_choices
)
from algorithms import generate_alternatives
from example_data import get_example_resources, get_example_tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    Инициализирует базу данных при запуске.
    """
    # Инициализация при запуске
    init_db()
    print("База данных инициализирована")
    yield
    # Очистка при завершении (если необходимо)
    pass


# Создание экземпляра FastAPI приложения
app = FastAPI(
    title="Система поддержки принятия решений (СППР)",
    description="Система для оптимизации планирования ресурсов",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS для возможности работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ========== Endpoints для работы с ресурсами ==========

@app.post("/resource", response_model=Resource, tags=["Ресурсы"])
def add_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """
    Добавление нового ресурса в систему.
    
    Args:
        resource: Данные ресурса (имя, тип, доступные часы)
        db: Сессия базы данных
        
    Returns:
        Resource: Созданный ресурс с ID
    """
    return create_resource(db, resource)


@app.get("/resources", response_model=List[Resource], tags=["Ресурсы"])
def get_resources(db: Session = Depends(get_db)):
    """
    Получение списка всех ресурсов.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Resource]: Список всех ресурсов
    """
    return get_all_resources(db)


@app.get("/resource/{resource_id}", response_model=Resource, tags=["Ресурсы"])
def get_resource_by_id(resource_id: int, db: Session = Depends(get_db)):
    """
    Получение ресурса по ID.
    
    Args:
        resource_id: ID ресурса
        db: Сессия базы данных
        
    Returns:
        Resource: Ресурс с указанным ID
        
    Raises:
        HTTPException: Если ресурс не найден
    """
    resource = get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с ID {resource_id} не найден")
    return resource


@app.put("/resource/{resource_id}", response_model=Resource, tags=["Ресурсы"])
def update_resource_by_id(
    resource_id: int,
    resource_update: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление ресурса по ID.
    
    Args:
        resource_id: ID ресурса для обновления
        resource_update: Данные для обновления (все поля опциональны)
        db: Сессия базы данных
        
    Returns:
        Resource: Обновленный ресурс
        
    Raises:
        HTTPException: Если ресурс не найден
    """
    resource = update_resource(
        db,
        resource_id,
        name=resource_update.name,
        type=resource_update.type,
        available_hours=resource_update.available_hours
    )
    if not resource:
        raise HTTPException(status_code=404, detail=f"Ресурс с ID {resource_id} не найден")
    return resource


@app.delete("/resource/{resource_id}", tags=["Ресурсы"])
def delete_resource_by_id(resource_id: int, db: Session = Depends(get_db)):
    """
    Удаление ресурса по ID.
    
    Args:
        resource_id: ID ресурса для удаления
        db: Сессия базы данных
        
    Returns:
        dict: Сообщение об успешном удалении
        
    Raises:
        HTTPException: Если ресурс не найден
    """
    if not delete_resource(db, resource_id):
        raise HTTPException(status_code=404, detail=f"Ресурс с ID {resource_id} не найден")
    return {"message": f"Ресурс с ID {resource_id} успешно удален"}


# ========== Endpoints для работы с задачами ==========

@app.post("/task", response_model=Task, tags=["Задачи"])
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Добавление новой задачи в систему.
    
    Args:
        task: Данные задачи (название, требуемые часы, приоритет)
        db: Сессия базы данных
        
    Returns:
        Task: Созданная задача с ID
    """
    return create_task(db, task)


@app.get("/tasks", response_model=List[Task], tags=["Задачи"])
def get_tasks(db: Session = Depends(get_db)):
    """
    Получение списка всех задач.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List[Task]: Список всех задач
    """
    return get_all_tasks(db)


@app.get("/task/{task_id}", response_model=Task, tags=["Задачи"])
def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    """
    Получение задачи по ID.
    
    Args:
        task_id: ID задачи
        db: Сессия базы данных
        
    Returns:
        Task: Задача с указанным ID
        
    Raises:
        HTTPException: Если задача не найдена
    """
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Задача с ID {task_id} не найдена")
    return task


@app.put("/task/{task_id}", response_model=Task, tags=["Задачи"])
def update_task_by_id(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление задачи по ID.
    
    Args:
        task_id: ID задачи для обновления
        task_update: Данные для обновления (все поля опциональны)
        db: Сессия базы данных
        
    Returns:
        Task: Обновленная задача
        
    Raises:
        HTTPException: Если задача не найдена
    """
    task = update_task(
        db,
        task_id,
        title=task_update.title,
        required_hours=task_update.required_hours,
        priority=task_update.priority
    )
    if not task:
        raise HTTPException(status_code=404, detail=f"Задача с ID {task_id} не найдена")
    return task


@app.delete("/task/{task_id}", tags=["Задачи"])
def delete_task_by_id(task_id: int, db: Session = Depends(get_db)):
    """
    Удаление задачи по ID.
    
    Args:
        task_id: ID задачи для удаления
        db: Сессия базы данных
        
    Returns:
        dict: Сообщение об успешном удалении
        
    Raises:
        HTTPException: Если задача не найдена
    """
    if not delete_task(db, task_id):
        raise HTTPException(status_code=404, detail=f"Задача с ID {task_id} не найдена")
    return {"message": f"Задача с ID {task_id} успешно удалена"}


# ========== Endpoints для работы с альтернативами ==========

@app.get("/alternatives", response_model=AlternativesListResponse, tags=["Альтернативы"])
def get_alternatives(db: Session = Depends(get_db)):
    """
    Получение списка альтернатив распределения ресурсов.
    
    Генерирует несколько вариантов распределения ресурсов по задачам,
    каждый с пояснением и оценкой. Альтернативы отсортированы по баллу
    (лучшие первыми).
    
    Args:
        db: Сессия базы данных
        
    Returns:
        AlternativesListResponse: Список альтернатив с распределениями
        
    Raises:
        HTTPException: Если нет ресурсов или задач в системе
    """
    # Получаем все ресурсы и задачи
    resources = get_all_resources(db)
    tasks = get_all_tasks(db)
    
    if not resources:
        raise HTTPException(
            status_code=400,
            detail="В системе нет ресурсов. Добавьте ресурсы через POST /resource"
        )
    
    if not tasks:
        raise HTTPException(
            status_code=400,
            detail="В системе нет задач. Добавьте задачи через POST /task"
        )
    
    # Удаляем старые альтернативы перед генерацией новых
    delete_all_alternatives(db)
    
    # Генерируем новые альтернативы
    alternatives_data = generate_alternatives(resources, tasks)
    
    # Сохраняем альтернативы в базу данных
    for alt_data in alternatives_data:
        create_alternative(
            db=db,
            explanation=alt_data["explanation"],
            score=alt_data["score"],
            allocations=alt_data["allocations"]
        )
    
    # Получаем сохраненные альтернативы с распределениями
    db_alternatives = get_all_alternatives(db)
    
    # Формируем ответ
    alternatives_response = []
    alternatives_dict = []  # Для ML модели
    
    for alt in db_alternatives:
        allocations_response = []
        for alloc in alt.allocations:
            allocations_response.append(AllocationResponse(
                resource_id=alloc.resource_id,
                resource_name=alloc.resource.name,
                task_id=alloc.task_id,
                task_title=alloc.task.title,
                hours=alloc.hours
            ))
        
        alt_response = AlternativeResponse(
            id=alt.id,
            explanation=alt.explanation,
            score=alt.score,
            allocations=allocations_response
        )
        alternatives_response.append(alt_response)
        
        # Подготавливаем данные для ML
        alternatives_dict.append({
            "id": alt.id,
            "explanation": alt.explanation,
            "score": alt.score,
            "allocations": [
                {
                    "resource_id": alloc.resource_id,
                    "task_id": alloc.task_id,
                    "hours": alloc.hours
                }
                for alloc in alt.allocations
            ]
        })
    
    # Получаем рекомендации от ML модели
    recommendations = None
    try:
        from ml_recommender import AlternativeRecommender
        recommender = AlternativeRecommender()
        if recommender.is_trained:
            ml_recommendations = recommender.recommend(alternatives_dict, resources, tasks)
            recommendations = [
                {
                    "alternative_id": rec["alternative"]["id"],
                    "recommendation_score": rec["recommendation_score"],
                    "is_recommended": rec["is_recommended"]
                }
                for rec in ml_recommendations
            ]
    except Exception as e:
        print(f"Ошибка получения рекомендаций ML: {e}")
    
    return AlternativesListResponse(
        alternatives=alternatives_response,
        total=len(alternatives_response),
        recommendations=recommendations
    )


@app.get("/alternative/{alternative_id}", response_model=AlternativeResponse, tags=["Альтернативы"])
def get_alternative_by_id(alternative_id: int, db: Session = Depends(get_db)):
    """
    Получение альтернативы по ID.
    
    Args:
        alternative_id: ID альтернативы
        db: Сессия базы данных
        
    Returns:
        AlternativeResponse: Альтернатива с указанным ID
        
    Raises:
        HTTPException: Если альтернатива не найдена
    """
    alt = get_alternative(db, alternative_id)
    if not alt:
        raise HTTPException(status_code=404, detail=f"Альтернатива с ID {alternative_id} не найдена")
    
    allocations_response = []
    for alloc in alt.allocations:
        allocations_response.append(AllocationResponse(
            resource_id=alloc.resource_id,
            resource_name=alloc.resource.name,
            task_id=alloc.task_id,
            task_title=alloc.task.title,
            hours=alloc.hours
        ))
    
    return AlternativeResponse(
        id=alt.id,
        explanation=alt.explanation,
        score=alt.score,
        allocations=allocations_response
    )


@app.get("/stats", response_model=DistributionStats, tags=["Статистика"])
def get_statistics(alternative_id: int = None, db: Session = Depends(get_db)):
    """
    Получение статистики распределения ресурсов.
    
    Args:
        alternative_id: ID альтернативы для анализа (опционально, по умолчанию берется лучшая)
        db: Сессия базы данных
        
    Returns:
        DistributionStats: Статистика распределения с предупреждениями
    """
    stats = calculate_distribution_stats(db, alternative_id)
    return DistributionStats(**stats)


@app.get("/export/alternatives", tags=["Экспорт"])
def export_alternatives(format: str = "json", db: Session = Depends(get_db)):
    """
    Экспорт альтернатив в различных форматах.
    
    Args:
        format: Формат экспорта ("json" или "csv")
        db: Сессия базы данных
        
    Returns:
        Response с файлом для скачивания или JSON данными
    """
    from fastapi.responses import Response, JSONResponse
    import csv
    import io
    
    alternatives = get_all_alternatives(db)
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Заголовки
        writer.writerow([
            "Альтернатива ID", "Балл", "Пояснение",
            "Ресурс", "Задача", "Часы"
        ])
        
        # Данные
        for alt in alternatives:
            explanation_short = alt.explanation[:50] + "..." if len(alt.explanation) > 50 else alt.explanation
            for alloc in alt.allocations:
                writer.writerow([
                    alt.id, alt.score, explanation_short,
                    alloc.resource.name, alloc.task.title, alloc.hours
                ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=alternatives.csv"}
        )
    
    else:  # JSON
        alternatives_data = []
        for alt in alternatives:
            allocations_data = []
            for alloc in alt.allocations:
                allocations_data.append({
                    "resource_id": alloc.resource_id,
                    "resource_name": alloc.resource.name,
                    "task_id": alloc.task_id,
                    "task_title": alloc.task.title,
                    "hours": alloc.hours
                })
            
            alternatives_data.append({
                "id": alt.id,
                "explanation": alt.explanation,
                "score": alt.score,
                "allocations": allocations_data
            })
        
        return JSONResponse(content={
            "alternatives": alternatives_data,
            "total": len(alternatives_data)
        })


# ========== Вспомогательные endpoints ==========

@app.post("/load-example-data", tags=["Вспомогательные"])
def load_example_data(db: Session = Depends(get_db)):
    """
    Загрузка примерных данных для тестирования системы.
    Создает несколько ресурсов и задач для демонстрации работы системы.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        dict: Сообщение об успешной загрузке данных
    """
    from example_data import get_example_resources, get_example_tasks
    
    # Добавляем примерные ресурсы
    example_resources = get_example_resources()
    for resource_data in example_resources:
        create_resource(db, resource_data)
    
    # Добавляем примерные задачи
    example_tasks = get_example_tasks()
    for task_data in example_tasks:
        create_task(db, task_data)
    
    return {
        "message": "Примерные данные успешно загружены",
        "resources_added": len(example_resources),
        "tasks_added": len(example_tasks)
    }


@app.post("/clear-all-data", tags=["Вспомогательные"])
def clear_all_data_endpoint(db: Session = Depends(get_db)):
    """
    Полная очистка всех данных из базы данных.
    Удаляет все ресурсы, задачи и альтернативы.
    ВНИМАНИЕ: Это действие необратимо!
    
    Args:
        db: Сессия базы данных
        
    Returns:
        dict: Статистика удаленных данных
        
    Raises:
        HTTPException: Если произошла ошибка при удалении
    """
    try:
        result = clear_all_data(db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении данных: {str(e)}"
        )


# ========== ML и рекомендации ==========

@app.post("/alternative/{alternative_id}/select", tags=["ML и рекомендации"])
def select_alternative(
    alternative_id: int,
    db: Session = Depends(get_db)
):
    """
    Сохранение выбранной пользователем альтернативы.
    Используется для обучения ML модели рекомендаций.
    
    Args:
        alternative_id: ID выбранной альтернативы
        db: Сессия базы данных
        
    Returns:
        dict: Сообщение об успешном сохранении
        
    Raises:
        HTTPException: Если альтернатива не найдена
    """
    from ml_recommender import AlternativeRecommender
    
    alt = get_alternative(db, alternative_id)
    if not alt:
        raise HTTPException(status_code=404, detail="Альтернатива не найдена")
    
    resources = get_all_resources(db)
    tasks = get_all_tasks(db)
    
    # Вычисляем характеристики альтернативы
    total_required = sum(t.required_hours for t in tasks)
    total_allocated = sum(a.hours for a in alt.allocations)
    coverage = total_allocated / total_required if total_required > 0 else 0
    
    # Приоритетный бонус
    priority_coverage = {}
    for alloc in alt.allocations:
        task_id = alloc.task_id
        if task_id not in priority_coverage:
            priority_coverage[task_id] = 0.0
        priority_coverage[task_id] += alloc.hours
    
    priority_score = 0.0
    if tasks:
        priority_scores = []
        for task in tasks:
            task_coverage = min(1.0, priority_coverage.get(task.id, 0) / task.required_hours)
            priority_weight = (6 - task.priority) / 5.0
            priority_scores.append(task_coverage * priority_weight)
        priority_score = sum(priority_scores) / len(priority_scores) if priority_scores else 0
    
    # Равномерность загрузки
    resource_load = {}
    for alloc in alt.allocations:
        if alloc.resource_id not in resource_load:
            resource_load[alloc.resource_id] = 0.0
        resource_load[alloc.resource_id] += alloc.hours
    
    utilizations = []
    for resource in resources:
        if resource.available_hours > 0:
            utilization = resource_load.get(resource.id, 0) / resource.available_hours
            utilizations.append(utilization)
    
    import numpy as np
    balance_score = 1.0 - np.std(utilizations) if utilizations else 0.5
    balance_score = max(0, min(1, balance_score))
    
    # Штраф за перегрузку
    overload_penalty = 0.0
    if total_required > 0:
        total_overload = sum(
            max(0, resource_load.get(r.id, 0) - r.available_hours)
            for r in resources
        )
        overload_penalty = min(1.0, total_overload / total_required)
    
    # Предсказание ML модели (если доступно)
    ml_score = None
    try:
        recommender = AlternativeRecommender()
        alt_dict = {
            "id": alt.id,
            "explanation": alt.explanation,
            "score": alt.score,
            "allocations": [
                {
                    "resource_id": a.resource_id,
                    "task_id": a.task_id,
                    "hours": a.hours
                }
                for a in alt.allocations
            ]
        }
        ml_score = recommender.predict_proba(alt_dict, resources, tasks)
    except Exception as e:
        print(f"Ошибка предсказания ML: {e}")
    
    # Сохраняем выбор
    save_user_choice(
        db=db,
        alternative_id=alternative_id,
        coverage=coverage,
        priority_score=priority_score,
        balance_score=balance_score,
        overload_penalty=overload_penalty,
        total_score=alt.score,
        num_resources=len(resources),
        num_tasks=len(tasks),
        ml_score=ml_score
    )
    
    return {
        "message": "Выбор сохранен для обучения ML модели",
        "alternative_id": alternative_id,
        "ml_prediction": ml_score
    }


@app.post("/ml/train", tags=["ML и рекомендации"])
def train_ml_model(db: Session = Depends(get_db)):
    """
    Обучение ML модели на исторических данных о выборах пользователей.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        dict: Результаты обучения модели
    """
    from ml_recommender import AlternativeRecommender
    
    try:
        # Получаем все выборы
        choices = get_all_user_choices(db)
        
        if len(choices) < 5:
            return {
                "status": "insufficient_data",
                "message": f"Недостаточно данных для обучения. Нужно минимум 5 выборов, получено {len(choices)}",
                "choices_count": len(choices)
            }
        
        # Получаем все альтернативы, которые были сгенерированы вместе с выбранными
        # Для этого нужно получить все альтернативы из тех же сессий
        # Упрощенный подход: используем только выбранные альтернативы как положительные примеры
        
        resources = get_all_resources(db)
        tasks = get_all_tasks(db)
        
        recommender = AlternativeRecommender()
        
        # Подготавливаем данные для обучения
        X = []
        y = []
        
        for choice in choices:
            # Получаем альтернативу
            alt = get_alternative(db, choice.alternative_id)
            if not alt:
                continue
            
            # Извлекаем признаки
            alt_dict = {
                "id": alt.id,
                "explanation": alt.explanation,
                "score": alt.score,
                "allocations": [
                    {
                        "resource_id": a.resource_id,
                        "task_id": a.task_id,
                        "hours": a.hours
                    }
                    for a in alt.allocations
                ]
            }
            
            features = recommender.extract_features(alt_dict, resources, tasks)
            X.append(features)
            y.append(1)  # Выбранная альтернатива = положительный пример
        
        # Добавляем отрицательные примеры (не выбранные альтернативы)
        # Берем случайные альтернативы из истории, которые не были выбраны
        all_alternatives = get_all_alternatives(db)
        selected_ids = {choice.alternative_id for choice in choices}
        
        # Добавляем несколько не выбранных альтернатив как отрицательные примеры
        negative_count = min(len(y), len([a for a in all_alternatives if a.id not in selected_ids]))
        for alt in all_alternatives:
            if alt.id not in selected_ids and len(y) < len(choices) * 2:
                alt_dict = {
                    "id": alt.id,
                    "explanation": alt.explanation,
                    "score": alt.score,
                    "allocations": [
                        {
                            "resource_id": a.resource_id,
                            "task_id": a.task_id,
                            "hours": a.hours
                        }
                        for a in alt.allocations
                    ]
                }
                features = recommender.extract_features(alt_dict, resources, tasks)
                X.append(features)
                y.append(0)  # Не выбранная = отрицательный пример
        
        # Обучаем модель
        result = recommender.train(X, y)
        
        return {
            **result,
            "choices_used": len(choices),
            "total_samples": len(X)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обучении модели: {str(e)}"
        )


@app.get("/ml/info", response_model=MLModelInfo, tags=["ML и рекомендации"])
def get_ml_model_info():
    """
    Получение информации о состоянии ML модели.
    
    Returns:
        MLModelInfo: Информация о модели
    """
    from ml_recommender import AlternativeRecommender
    
    try:
        recommender = AlternativeRecommender()
        info = recommender.get_model_info()
        
        # Получаем дополнительную информацию о точности
        import os
        if os.path.exists("ml_model.pkl"):
            # Можно добавить загрузку метрик из файла
            pass
        
        return MLModelInfo(**info)
    except Exception as e:
        return MLModelInfo(
            is_trained=False,
            ml_available=False,
            model_exists=False
        )


@app.get("/", tags=["Информация"])
def root():
    """
    Корневой endpoint - перенаправляет на веб-интерфейс.
    """
    from fastapi.responses import FileResponse
    import os
    return FileResponse("static/index.html")


@app.get("/api/info", tags=["Информация"])
def api_info():
    """
    API endpoint с информацией о системе.
    
    Returns:
        dict: Информация о системе и доступных endpoints
    """
    return {
        "message": "Система поддержки принятия решений (СППР) для оптимизации планирования ресурсов",
        "version": "1.0.0",
        "endpoints": {
            "resources": {
                "POST /resource": "Добавить ресурс",
                "GET /resources": "Получить все ресурсы"
            },
            "tasks": {
                "POST /task": "Добавить задачу",
                "GET /tasks": "Получить все задачи"
            },
            "alternatives": {
                "GET /alternatives": "Получить альтернативы распределения ресурсов"
            },
            "helpers": {
                "POST /load-example-data": "Загрузить примерные данные",
                "GET /docs": "Документация API (Swagger UI)"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

