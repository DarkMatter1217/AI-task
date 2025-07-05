# utils/recommendation_engine.py
import random
from typing import List, Dict

class RecommendationEngine:
    def __init__(self, catalog: List[Dict]):
        self.catalog = catalog

    def recommend_problems(self, weak_areas: List[str], count: int = 5) -> List[Dict]:
        matches = [p for p in self.catalog if any(tag in weak_areas for tag in p.get("tags", []))]
        source = matches if matches else self.catalog
        return random.sample(source, min(count, len(source)))

    def generate_study_schedule(self, weak_areas: List[str], time_per_day: int, days: int = 7) -> Dict[str, List[str]]:
        schedule = {}
        for i in range(days):
            topic = weak_areas[i % len(weak_areas)]
            problem = random.choice(self.recommend_problems([topic], 3))["title"]
            schedule[f"Day {i+1}"] = [f"Review {topic}", f"Solve {problem}"]
        return schedule
