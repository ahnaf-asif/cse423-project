from core.component import Component

TIMER_DEFAULT_SECONDS = 60 * 60  # 60 minutes


class TimerState(Component):
    def __init__(self):
        self.total_seconds = float(TIMER_DEFAULT_SECONDS)
        self.is_running = True

    def reduce_five_minutes(self):
        self.total_seconds = max(0.0, self.total_seconds - 300.0)
        if self.total_seconds == 0.0:
            self.is_running = False

    def reset(self):
        self.total_seconds = float(TIMER_DEFAULT_SECONDS)
        self.is_running = True

    def get_display(self):
        """Returns (hours, minutes, seconds) as integers for display."""
        total = int(self.total_seconds)

        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return h, m, s
