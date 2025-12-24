"""
ML модуль для рекомендации альтернатив на основе исторических данных.
Использует Random Forest для предсказания вероятности выбора альтернативы.
"""

import numpy as np
from typing import List, Dict
from models import Resource, Task
import os
import json

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Предупреждение: scikit-learn не установлен. ML функции будут недоступны.")


class AlternativeRecommender:
    """
    ML модель для рекомендации альтернатив на основе исторических данных.
    Обучена на выборах пользователей для предсказания предпочтений.
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.model_path = "ml_model.pkl"
        self.feature_names = [
            'coverage', 'priority_score', 'balance_score', 'overload_penalty',
            'total_score', 'num_allocations', 'num_resources', 'num_tasks',
            'total_required', 'total_available', 'resource_utilization_std'
        ]
        
        if ML_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=50,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            # Пытаемся загрузить сохраненную модель
            self._load_model()
    
    def _load_model(self):
        """Загрузка сохраненной модели из файла."""
        if ML_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.is_trained = True
            except Exception as e:
                print(f"Ошибка загрузки модели: {e}")
                self.is_trained = False
    
    def _save_model(self):
        """Сохранение модели в файл."""
        if ML_AVAILABLE and self.model and self.is_trained:
            try:
                joblib.dump(self.model, self.model_path)
            except Exception as e:
                print(f"Ошибка сохранения модели: {e}")
    
    def extract_features(
        self,
        alternative: Dict,
        resources: List[Resource],
        tasks: List[Task]
    ) -> np.ndarray:
        """
        Извлечение признаков из альтернативы для ML модели.
        
        Args:
            alternative: Альтернатива с распределениями
            resources: Список ресурсов
            tasks: Список задач
            
        Returns:
            np.ndarray: Вектор признаков
        """
        allocations = alternative.get("allocations", [])
        
        # 1. Покрытие задач
        total_required = sum(t.required_hours for t in tasks)
        total_allocated = sum(a["hours"] for a in allocations)
        coverage = total_allocated / total_required if total_required > 0 else 0
        
        # 2. Приоритетный бонус
        priority_coverage = {}
        for alloc in allocations:
            task_id = alloc["task_id"]
            if task_id not in priority_coverage:
                priority_coverage[task_id] = 0.0
            priority_coverage[task_id] += alloc["hours"]
        
        priority_score = 0.0
        if tasks:
            priority_scores = []
            for task in tasks:
                task_coverage = min(1.0, priority_coverage.get(task.id, 0) / task.required_hours)
                priority_weight = (6 - task.priority) / 5.0  # Нормализация 1-5 к 0-1
                priority_scores.append(task_coverage * priority_weight)
            priority_score = sum(priority_scores) / len(priority_scores) if priority_scores else 0
        
        # 3. Равномерность загрузки ресурсов
        resource_load = {}
        for alloc in allocations:
            resource_id = alloc["resource_id"]
            if resource_id not in resource_load:
                resource_load[resource_id] = 0.0
            resource_load[resource_id] += alloc["hours"]
        
        utilizations = []
        for resource in resources:
            if resource.available_hours > 0:
                utilization = resource_load.get(resource.id, 0) / resource.available_hours
                utilizations.append(utilization)
        
        balance_score = 1.0 - np.std(utilizations) if utilizations else 0.5
        balance_score = max(0, min(1, balance_score))  # Нормализация
        
        resource_utilization_std = np.std(utilizations) if utilizations else 0.5
        
        # 4. Штраф за перегрузку
        overload_penalty = 0.0
        if total_required > 0:
            total_overload = sum(
                max(0, resource_load.get(r.id, 0) - r.available_hours)
                for r in resources
            )
            overload_penalty = total_overload / total_required
            overload_penalty = min(1.0, overload_penalty)  # Ограничиваем максимум
        
        # 5. Общий балл альтернативы
        total_score = alternative.get("score", 0.0)
        
        # 6. Количество распределений
        num_allocations = len(allocations)
        
        # 7. Количество ресурсов и задач
        num_resources = len(resources)
        num_tasks = len(tasks)
        
        # 8. Общие метрики
        total_available = sum(r.available_hours for r in resources)
        
        # Возвращаем вектор признаков
        features = np.array([
            coverage,                    # 0: Покрытие задач
            priority_score,              # 1: Приоритетный бонус
            balance_score,               # 2: Равномерность загрузки
            overload_penalty,           # 3: Штраф за перегрузку
            total_score / 100.0,        # 4: Нормализованный общий балл
            num_allocations / 50.0,      # 5: Нормализованное количество распределений
            num_resources / 20.0,       # 6: Нормализованное количество ресурсов
            num_tasks / 20.0,           # 7: Нормализованное количество задач
            total_required / 1000.0,    # 8: Нормализованные требуемые часы
            total_available / 1000.0,   # 9: Нормализованные доступные часы
            resource_utilization_std    # 10: Стандартное отклонение загрузки
        ])
        
        return features
    
    def train(self, X: List[np.ndarray], y: List[int]) -> Dict:
        """
        Обучение модели на исторических данных.
        
        Args:
            X: Матрица признаков (список векторов признаков)
            y: Метки (1 - выбрано, 0 - не выбрано)
            
        Returns:
            Dict: Результаты обучения (accuracy, status)
        """
        if not ML_AVAILABLE:
            return {"status": "error", "message": "ML библиотеки не установлены"}
        
        if len(X) < 5:  # Минимум 5 примеров для обучения
            return {
                "status": "insufficient_data",
                "message": f"Недостаточно данных для обучения. Нужно минимум 5, получено {len(X)}",
                "accuracy": 0.0
            }
        
        try:
            X_array = np.array(X)
            y_array = np.array(y)
            
            # Если все метки одинаковые, добавляем немного разнообразия
            if len(set(y_array)) < 2:
                return {
                    "status": "insufficient_variety",
                    "message": "Недостаточно разнообразия в данных для обучения",
                    "accuracy": 0.0
                }
            
            # Разделение на обучающую и тестовую выборки
            if len(X) >= 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_array, y_array, test_size=0.2, random_state=42, stratify=y_array
                )
            else:
                # Если данных мало, используем все для обучения
                X_train, X_test, y_train, y_test = X_array, X_array, y_array, y_array
            
            # Обучение модели
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Оценка точности
            accuracy = self.model.score(X_test, y_test)
            
            # Сохранение модели
            self._save_model()
            
            return {
                "status": "success",
                "message": "Модель успешно обучена",
                "accuracy": float(accuracy),
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка при обучении: {str(e)}",
                "accuracy": 0.0
            }
    
    def predict_proba(
        self,
        alternative: Dict,
        resources: List[Resource],
        tasks: List[Task]
    ) -> float:
        """
        Предсказание вероятности выбора альтернативы.
        
        Args:
            alternative: Альтернатива
            resources: Список ресурсов
            tasks: Список задач
            
        Returns:
            float: Вероятность выбора (0-1)
        """
        if not ML_AVAILABLE:
            return 0.5
        
        if not self.is_trained:
            return 0.5  # Если модель не обучена, возвращаем среднюю вероятность
        
        try:
            features = self.extract_features(alternative, resources, tasks)
            proba = self.model.predict_proba([features])[0]
            
            # Возвращаем вероятность класса "выбрано" (1)
            if len(proba) > 1:
                return float(proba[1])
            else:
                return float(proba[0])
        except Exception as e:
            print(f"Ошибка предсказания: {e}")
            return 0.5
    
    def recommend(
        self,
        alternatives: List[Dict],
        resources: List[Resource],
        tasks: List[Task],
        top_n: int = 3
    ) -> List[Dict]:
        """
        Рекомендация лучших альтернатив на основе ML модели.
        
        Args:
            alternatives: Список альтернатив
            resources: Список ресурсов
            tasks: Список задач
            top_n: Количество рекомендаций
            
        Returns:
            List[Dict]: Рекомендуемые альтернативы с вероятностями
        """
        if not alternatives:
            return []
        
        recommendations = []
        
        for alt in alternatives:
            proba = self.predict_proba(alt, resources, tasks)
            recommendations.append({
                "alternative": alt,
                "recommendation_score": proba,
                "is_recommended": proba > 0.6  # Порог рекомендации
            })
        
        # Сортируем по вероятности
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return recommendations[:top_n]
    
    def get_model_info(self) -> Dict:
        """
        Получение информации о модели.
        
        Returns:
            Dict: Информация о состоянии модели
        """
        return {
            "is_trained": self.is_trained,
            "ml_available": ML_AVAILABLE,
            "model_path": self.model_path,
            "model_exists": os.path.exists(self.model_path) if ML_AVAILABLE else False
        }

