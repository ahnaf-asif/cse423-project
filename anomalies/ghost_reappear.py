import random
import copy
from anomalies.base_anomaly import BaseAnomaly

class GhostReappearAnomaly(BaseAnomaly):
    def __init__(self):
        super().__init__("Ghost")

    def get_eligible_entities(self, entities, disqualified_list):
        """
        Eligible entities are the desks belonging to disqualified students
        that are CURRENTLY empty.
        """
        eligible = []
        for desk_id, student_state, desk_evidence in disqualified_list:
            # Find the desk entity in the live room
            desk = next((e for e in entities if e.id == desk_id), None)
            # If the desk is currently empty, it can be haunted
            if desk and desk.get_component("AnimState") is None:
                eligible.append((desk, student_state))
        return eligible

    def apply(self, entities, game_manager):
        # We need the disqualified list from game_manager
        eligible = self.get_eligible_entities(entities, game_manager.disqualified_students)

        if not eligible:
            return []

        # Select one ghost to return
        target_desk, dirty_student_state = random.choice(eligible)

        # Pull the CLEAN state from the baseline snapshot
        snap = game_manager.baseline_manager.snapshot.get(target_desk.id)
        if not snap or not snap["anim_state"]:
            return [] # Should not happen based on eligibility

        clean_student_state = snap["anim_state"]

        print(f"[Anomaly] GHOST REAPPEARANCE: {clean_student_state.name} has returned to {target_desk.id} in their BASELINE state.")

        # Mark as writing explicitly
        clean_student_state.is_writing = True

        # Place the CLEAN state back in the room
        target_desk.add_component("AnimState", clean_student_state)

        # Restore the desk items from baseline as well
        target_desk.add_component("StudentDeskState", copy.deepcopy(snap["desk_state"]))

        # Remove from disqualified list (searching by student state reference)
        game_manager.disqualified_students = [item for item in game_manager.disqualified_students if item[1] != dirty_student_state]

        return [target_desk]

