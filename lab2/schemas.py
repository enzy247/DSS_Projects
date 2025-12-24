"""
Pydantic схемы для валидации данных API.
Используются для сериализации/десериализации данных при работе с FastAPI.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ResourceBase(BaseModel):
    """Базовая схема ресурса."""
    name: str = Field(..., description="Имя ресурса")
    type: str = Field(..., description="Тип ресурса")
    available_hours: float = Field(..., gt=0, description="Доступные часы работы")


class ResourceCreate(ResourceBase):
    """Схема для создания ресурса."""
    pass


class Resource(ResourceBase):
    """Схема ресурса с ID (для ответов API)."""
    id: int
    
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Базовая схема задачи."""
    title: str = Field(..., description="Название задачи")
    required_hours: float = Field(..., gt=0, description="Требуемые часы")
    priority: int = Field(..., ge=1, le=5, description="Приоритет (1-5, где 1 - высший)")


class TaskCreate(TaskBase):
    """Схема для создания задачи."""
    pass


class Task(TaskBase):
    """Схема задачи с ID (для ответов API)."""
    id: int
    
    class Config:
        from_attributes = True


class AllocationResponse(BaseModel):
    """Схема распределения ресурса на задачу."""
    resource_id: int
    resource_name: str
    task_id: int
    task_title: str
    hours: float
    
    class Config:
        from_attributes = True


class AlternativeResponse(BaseModel):
    """Схема альтернативы распределения ресурсов."""
    id: int
    explanation: str
    score: float
    allocations: List[AllocationResponse]
    
    class Config:
        from_attributes = True


class AlternativesListResponse(BaseModel):
    """Схема списка альтернатив."""
    alternatives: List[AlternativeResponse]
    total: int
    recommendations: Optional[List[Dict]] = None
    recommendations: Optional[List[Dict]] = None


class UserChoiceCreate(BaseModel):
    """Схема для сохранения выбора пользователя."""
    alternative_id: int


class MLModelInfo(BaseModel):
    """Информация о ML модели."""
    is_trained: bool
    ml_available: bool
    model_exists: bool
    accuracy: Optional[float] = None
    training_samples: Optional[int] = None


class ResourceUpdate(BaseModel):
    """Схема для обновления ресурса."""
    name: Optional[str] = Field(None, description="Имя ресурса")
    type: Optional[str] = Field(None, description="Тип ресурса")
    available_hours: Optional[float] = Field(None, gt=0, description="Доступные часы работы")


class TaskUpdate(BaseModel):
    """Схема для обновления задачи."""
    title: Optional[str] = Field(None, description="Название задачи")
    required_hours: Optional[float] = Field(None, gt=0, description="Требуемые часы")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Приоритет (1-5, где 1 - высший)")


class ResourceStats(BaseModel):
    """Статистика по ресурсу."""
    resource_id: int
    resource_name: str
    available_hours: float
    allocated_hours: float
    utilization_percent: float
    overload: bool


class TaskStats(BaseModel):
    """Статистика по задаче."""
    task_id: int
    task_title: str
    required_hours: float
    allocated_hours: float
    coverage_percent: float
    priority: int


class DistributionStats(BaseModel):
    """Общая статистика распределения."""
    total_resources: int
    total_tasks: int
    total_available_hours: float
    total_required_hours: float
    total_allocated_hours: float
    overall_coverage_percent: float
    resource_stats: List[ResourceStats]
    task_stats: List[TaskStats]
    warnings: List[str]

