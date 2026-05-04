import random
from anomalies.base_anomaly import BaseAnomaly

class PenSwapAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("PenSwap")

    def get_eligible_entities(self, entities):
        eligible = []
        for e in entities:
            anim = e.get_component("AnimState")
            if anim and anim.pen_color == (1.0, 0.0, 0.0):
                eligible.append(e)
        return eligible

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        if not eligible:
            return []

        target_desk = random.choice(eligible)
        student_state = target_desk.get_component("AnimState")

        new_color = (0.0, 0.5, 1.0)
        print(f"[Anomaly] Pen Swap for {student_state.name}: Red -> Electric Blue")
        student_state.pen_color = new_color

        return [target_desk]
