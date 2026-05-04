import random
from anomalies.base_anomaly import BaseAnomaly

class CalcSwapAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("CalcSwap")

    def get_eligible_entities(self, entities):
        """Eligible entities are desks with students."""
        return [e for e in entities if e.get_component("AnimState") is not None]

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        # Affect at most 1 student
        target_desk = random.choice(eligible)
        desk_state = target_desk.get_component("StudentDeskState")
        student_state = target_desk.get_component("AnimState")
        
        if desk_state.calculator.is_visible:
            print(f"[Anomaly] CALCULATOR REMOVAL: {student_state.name} no longer has a calculator.")
            desk_state.calculator.is_visible = False
        else:
            print(f"[Anomaly] CALCULATOR ADDITION: {student_state.name} suddenly has a calculator.")
            desk_state.calculator.is_visible = True

        return [target_desk]
