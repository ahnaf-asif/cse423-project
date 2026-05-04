import random

from anomalies.base_anomaly import BaseAnomaly


class CalculatorSwapAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("CalcSwap")

    def get_eligible_entities(self, entities):
        return [e for e in entities if e.get_component("AnimState") is not None]

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)

        if not eligible:
            return []

        target_desk = random.choice(eligible)
        desk_state = target_desk.get_component("StudentDeskState")

        old_status = "Visible" if desk_state.calculator.is_visible else "Hidden"
        desk_state.calculator.is_visible = not desk_state.calculator.is_visible
        new_status = "Visible" if desk_state.calculator.is_visible else "Hidden"

        student_name = target_desk.get_component("AnimState").name
        print(
            f"[Anomaly] Calculator Swap for {student_name} at {target_desk.id}: {old_status} -> {new_status}"
        )

        return [target_desk]
