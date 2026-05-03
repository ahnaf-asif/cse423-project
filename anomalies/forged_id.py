import random
from anomalies.base_anomaly import BaseAnomaly

class ForgedIDAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("ForgedID")

    def get_eligible_entities(self, entities):
        """Eligible entities are desks that have a student (AnimState)."""
        return [e for e in entities if e.get_component("AnimState") is not None]

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        # At most 1 student can be affected
        target_desk = random.choice(eligible)
        student_state = target_desk.get_component("AnimState")

        print(f"[Anomaly] Forged ID for {student_state.name}: {student_state.id_number} -> 69420")
        student_state.id_number = "69420"

        return [target_desk]
