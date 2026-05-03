import random
from anomalies.base_anomaly import BaseAnomaly

class SeatSwapAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("SeatSwap")

    def get_eligible_entities(self, entities):
        """Eligible entities are desks that have a student (AnimState)."""
        return [e for e in entities if e.get_component("AnimState") is not None]

    def apply(self, entities):
        eligible = self.get_eligible_entities(entities)
        
        # Need at least 2 students to swap
        if len(eligible) < 2:
            return []

        # Randomly select a pair (GDD says 'Two students swap places')
        # Though the user mentioned 'up to 3', a swap is traditionally a pair.
        # I'll implement it as a pair swap for now.
        pair = random.sample(eligible, 2)
        desk_a, desk_b = pair[0], pair[1]

        # Swap their AnimState components
        state_a = desk_a.get_component("AnimState")
        state_b = desk_b.get_component("AnimState")

        desk_a.add_component("AnimState", state_b)
        desk_b.add_component("AnimState", state_a)

        print(f"[Anomaly] Swapped seats of {state_b.name} and {state_a.name}")
        return [desk_a, desk_b]
