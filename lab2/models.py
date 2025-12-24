"""
Модели данных для базы данных SQLite.
Использует SQLAlchemy ORM для определения структуры таблиц.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Resource(Base):
    """
    Модель ресурса (человек, оборудование и т.д.).
    
    Атрибуты:
        id: Уникальный идентификатор ресурса
        name: Имя ресурса (например, "Иван Иванов", "Сервер #1")
        type: Тип ресурса (например, "разработчик", "дизайнер", "оборудование")
        available_hours: Доступное количество часов работы ресурса
    """
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    available_hours = Column(Float, nullable=False)
    
    # Связь с альтернативами (распределениями ресурсов)
    allocations = relationship("Allocation", back_populates="resource")


class Task(Base):
    """
    Модель задачи/проекта, требующей ресурсов.
    
    Атрибуты:
        id: Уникальный идентификатор задачи
        title: Название задачи
        required_hours: Требуемое количество часов для выполнения задачи
        priority: Приоритет задачи (1 - высший, 5 - низший)
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    required_hours = Column(Float, nullable=False)
    priority = Column(Integer, nullable=False)  # 1 - высший приоритет, 5 - низший
    
    # Связь с альтернативами (распределениями ресурсов)
    allocations = relationship("Allocation", back_populates="task")


class Alternative(Base):
    """
    Модель альтернативы распределения ресурсов.
    Содержит описание одного варианта распределения ресурсов по задачам.
    
    Атрибуты:
        id: Уникальный идентификатор альтернативы
        explanation: Текстовое пояснение, почему данная альтернатива предложена
        score: Оценочный балл альтернативы (для сортировки)
    """
    __tablename__ = "alternatives"
    
    id = Column(Integer, primary_key=True, index=True)
    explanation = Column(Text, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    
    # Связь с распределениями ресурсов
    allocations = relationship("Allocation", back_populates="alternative", cascade="all, delete-orphan")


class Allocation(Base):
    """
    Модель распределения ресурса на задачу в рамках альтернативы.
    Связывает ресурс, задачу и альтернативу, указывая количество часов.
    
    Атрибуты:
        id: Уникальный идентификатор распределения
        alternative_id: ID альтернативы, к которой относится это распределение
        resource_id: ID ресурса
        task_id: ID задачи
        hours: Количество часов, выделенных данному ресурсу на данную задачу
    """
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    alternative_id = Column(Integer, ForeignKey("alternatives.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    hours = Column(Float, nullable=False)
    
    # Связи с другими моделями
    alternative = relationship("Alternative", back_populates="allocations")
    resource = relationship("Resource", back_populates="allocations")
    task = relationship("Task", back_populates="allocations")


class UserChoice(Base):
    """
    Модель для сохранения выбранных пользователем альтернатив.
    Используется для обучения ML модели рекомендаций.
    
    Атрибуты:
        id: Уникальный идентификатор выбора
        alternative_id: ID выбранной альтернативы
        selected_at: Время выбора
        coverage: Процент покрытия задач
        priority_score: Оценка по приоритетам
        balance_score: Оценка равномерности
        overload_penalty: Штраф за перегрузку
        ml_score: Предсказанная ML моделью вероятность выбора
    """
    __tablename__ = "user_choices"
    
    id = Column(Integer, primary_key=True, index=True)
    alternative_id = Column(Integer, ForeignKey("alternatives.id"), nullable=False)
    selected_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Характеристики альтернативы на момент выбора (для обучения модели)
    coverage = Column(Float, nullable=False)
    priority_score = Column(Float, nullable=False)
    balance_score = Column(Float, nullable=False)
    overload_penalty = Column(Float, nullable=False)
    total_score = Column(Float, nullable=False)
    num_resources = Column(Integer, nullable=False)
    num_tasks = Column(Integer, nullable=False)
    ml_score = Column(Float, nullable=True)  # Предсказанная вероятность





