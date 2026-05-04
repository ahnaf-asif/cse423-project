import random
from anomalies.base_anomaly import BaseAnomaly

class DancingAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("Dancing")

    def get_eligible_entities(self, entities):
        eligible = []
        for e in entities:
            anim = e.get_component("AnimState")
            if anim and not anim.is_dancing:
                eligible.append(e)
        return eligible

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        count = min(len(eligible), random.randint(1, 2))
        targets = random.sample(eligible, count)

        for desk in targets:
            student_state = desk.get_component("AnimState")
            print(f"[Anomaly] {student_state.name} has started DANCING!")
            student_state.is_dancing = True
            student_state.is_writing = False # Can't write and dance
            student_state.is_sitting = True # Still in chair, but dancing

        return targets
