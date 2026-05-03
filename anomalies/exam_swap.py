import random
from anomalies.base_anomaly import BaseAnomaly

class ExamSwapAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("ExamSwap")

    def get_eligible_entities(self, entities):
        """Eligible entities are desks with students who have an exam sheet."""
        eligible = []
        for e in entities:
            anim = e.get_component("AnimState")
            desk_state = e.get_component("StudentDeskState")
            if anim and desk_state and desk_state.exam_sheet.is_visible:
                eligible.append(e)
        return eligible

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        # Need at least 2 students to swap
        if len(eligible) < 2:
            return []

        # Select a pair
        pair = random.sample(eligible, 2)
        desk_a, desk_b = pair[0], pair[1]

        state_a = desk_a.get_component("StudentDeskState").exam_sheet
        state_b = desk_b.get_component("StudentDeskState").exam_sheet

        # Swap their extra_logs (Name and ID on the paper)
        logs_a = state_a.extra_logs
        logs_b = state_b.extra_logs

        state_a.extra_logs = logs_b
        state_b.extra_logs = logs_a

        name_a = desk_a.get_component("AnimState").name
        name_b = desk_b.get_component("AnimState").name

        print(f"[Anomaly] Swapped Exam Sheets between {name_a} ({desk_a.id}) and {name_b} ({desk_b.id})")
        return [desk_a, desk_b]
