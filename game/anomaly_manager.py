import random

from anomalies.alien_transform import AlienTransformAnomaly
from anomalies.calc_swap import CalcSwapAnomaly
from anomalies.cheat_sheet import CheatSheetAnomaly
from anomalies.dancing import DancingAnomaly
from anomalies.exam_swap import ExamSwapAnomaly
from anomalies.forged_id import ForgedIDAnomaly
from anomalies.ghost_reappear import GhostReappearAnomaly
from anomalies.pen_swap import PenSwapAnomaly
from anomalies.seat_swap import SeatSwapAnomaly
from anomalies.smartphone import SmartphoneAnomaly


class AnomalyManager:
    def __init__(self):
        self.weights = {
            "SeatSwap": 3.0,
            "AlienTransform": 5.0,
            "Dancing": 5.0,
            "Ghost": 5.0,
            "ExamSwap": 13.67,
            "CheatSheet": 13.67,
            "ForgedID": 13.67,
            "PenSwap": 13.67,
            "CalcSwap": 13.67,
            "Smartphone": 13.65,
        }

        self.anomaly_instances = {
            "SeatSwap": SeatSwapAnomaly(),
            "ForgedID": ForgedIDAnomaly(),
            "PenSwap": PenSwapAnomaly(),
            "AlienTransform": AlienTransformAnomaly(),
            "Dancing": DancingAnomaly(),
            "CheatSheet": CheatSheetAnomaly(),
            "ExamSwap": ExamSwapAnomaly(),
            "Ghost": GhostReappearAnomaly(),
            "Smartphone": SmartphoneAnomaly(),
            "CalcSwap": CalcSwapAnomaly(),
        }

    def get_probability_string(self):
        """Returns a formatted string of the current anomaly weights."""
        lines = ["Current Anomaly Probabilities:"]
        sorted_weights = sorted(self.weights.items(), key=lambda x: x[1], reverse=True)
        for name, weight in sorted_weights:
            lines.append(f"  - {name:15}: {weight:5.2f}%")
        return "\n".join(lines)

    def pick_anomaly(self):
        """Selects an anomaly based on the current probability distribution."""
        names = list(self.weights.keys())
        probs = list(self.weights.values())
        return random.choices(names, weights=probs, k=1)[0]

    def scale_probabilities(self, successful_anomaly):
        """Implements the 2% Rule and linear redistribution."""
        if successful_anomaly not in self.weights:
            return

        old_weight = self.weights[successful_anomaly]
        self.weights[successful_anomaly] = 2.0

        diff = old_weight - 2.0

        other_anomalies = [k for k in self.weights.keys() if k != successful_anomaly]
        total_other_weight = sum(self.weights[k] for k in other_anomalies)

        for k in other_anomalies:
            proportion = self.weights[k] / total_other_weight
            self.weights[k] += diff * proportion

    def apply_anomaly(self, anomaly_name, entities, game_manager):
        """
        Main entry point for triggering an anomaly.
        """
        if anomaly_name in self.anomaly_instances:
            instance = self.anomaly_instances[anomaly_name]

            # Special case for Ghost which needs game_manager context
            if anomaly_name == "Ghost":
                return instance.apply(entities, game_manager)

            return instance.apply(entities)

        print(f"[AnomalyManager] Warning: {anomaly_name} logic not implemented yet.")
        return []
