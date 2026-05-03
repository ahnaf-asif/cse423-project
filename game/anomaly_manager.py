import random

from anomalies.alien_transform import AlienTransformAnomaly
from anomalies.calculator_swap import CalculatorSwapAnomaly
from anomalies.dancing import DancingAnomaly
from anomalies.forged_id import ForgedIDAnomaly
from anomalies.pen_swap import PenSwapAnomaly
from anomalies.seat_swap import SeatSwapAnomaly
from anomalies.cheat_sheet import CheatSheetAnomaly
from anomalies.exam_swap import ExamSwapAnomaly
from anomalies.ghost_reappear import GhostReappearAnomaly
from anomalies.smartphone import SmartphoneAnomaly

class AnomalyManager:
    def __init__(self):
        # Initial probabilities as defined in GDD
        self.weights = {
            "Alien": 5.0,
            "Dancing": 5.0,
            "Ghost": 5.0,
            "SeatSwap": 12.14,
            "ExamSwap": 12.14,
            "CheatSheet": 12.14,
            "ForgedID": 12.14,
            "PenSwap": 12.14,
            "CalcSwap": 12.14,
            "Smartphone": 12.14,
        }

        # Instance registry for anomaly logic
        self.anomaly_instances = {
            "SeatSwap": SeatSwapAnomaly(),
            "ForgedID": ForgedIDAnomaly(),
            "PenSwap": PenSwapAnomaly(),
            "CalcSwap": CalculatorSwapAnomaly(),
            "AlienTransform": AlienTransformAnomaly(),
            "Dancing": DancingAnomaly(),
            "CheatSheet": CheatSheetAnomaly(),
            "ExamSwap": ExamSwapAnomaly(),
            "Ghost": GhostReappearAnomaly(),
            "Smartphone": SmartphoneAnomaly()
        }

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

        # Calculate how much weight we need to redistribute
        diff = old_weight - 2.0

        # Redistribute linearly among other 9 anomalies
        other_anomalies = [k for k in self.weights.keys() if k != successful_anomaly]
        total_other_weight = sum(self.weights[k] for k in other_anomalies)

        for k in other_anomalies:
            # Add a portion of the diff based on current relative weight
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
