import random
from anomalies.base_anomaly import BaseAnomaly

class AlienTransformAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("AlienTransform")

    def get_eligible_entities(self, entities):
        """Eligible entities are desks with students who are NOT already aliens or ghosts."""
        eligible = []
        for e in entities:
            anim = e.get_component("AnimState")
            if anim and not anim.is_alien and not anim.is_ghost:
                eligible.append(e)
        return eligible

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        # Affect 1 or 2 students
        count = min(len(eligible), random.randint(1, 2))
        targets = random.sample(eligible, count)

        for desk in targets:
            student_state = desk.get_component("AnimState")
            print(f"[Anomaly] Transforming {student_state.name} into an ALIEN!")
            student_state.is_alien = True

        return targets
