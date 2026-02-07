from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class UserProfile:
    gender: str
    age: int
    weight: float
    height: float
    activity_level: str
    goal: str
    diet_type: str
    
    def get_gender_index(self, genders: List[str]) -> int:
        if self.gender not in genders:
            raise ValueError(f"Gender '{self.gender}' not found in available options")
        return genders.index(self.gender)
    
    def get_activity_index(self, activities: List[str]) -> int:
        if self.activity_level not in activities:
            raise ValueError(f"Activity level '{self.activity_level}' not found in available options")
        return activities.index(self.activity_level)
    
    def get_goal_index(self, goals: List[str]) -> int:
        if self.goal not in goals:
            raise ValueError(f"Goal '{self.goal}' not found in available options")
        return goals.index(self.goal)

@dataclass
class NutritionResult:
    food_items: List[str]
    total_calories: int
    macros: Dict[str, str]
    health_score: int
    burn_off: Dict[str, int]
    is_diet_compliant: bool
    analysis: str
    suggestion: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NutritionResult':
        return cls(
            food_items=data.get('food_items', []),
            total_calories=data.get('total_calories', 0),
            macros=data.get('macros', {}),
            health_score=data.get('health_score', 0),
            burn_off=data.get('burn_off', {}),
            is_diet_compliant=data.get('is_diet_compliant', False),
            analysis=data.get('analysis', ''),
            suggestion=data.get('suggestion', '')
        )
