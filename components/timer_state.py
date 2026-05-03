from core.component import Component

TIMER_DEFAULT_SECONDS = 60 * 60  # 60 minutes


class TimerState(Component):
    def __init__(self):
        self.total_seconds = float(TIMER_DEFAULT_SECONDS)
        self.is_running = True  # Kept True so the colon continues to flicker

    def update(self, dt):
        # The automatic countdown logic has been removed.
        # The timer will now stay static until interacted with.
        pass

    def reduce_five_minutes(self):
        # Drops the timer by 5 minutes (300 seconds)
        self.total_seconds = max(0.0, self.total_seconds - 300.0)
        if self.total_seconds == 0.0:
            self.is_running = False

    def reset(self):
        self.total_seconds = float(TIMER_DEFAULT_SECONDS)
        self.is_running = True

    def get_display(self):
        """Returns (hours, minutes, seconds) as integers for display."""
        total = int(self.total_seconds)

        # If you specifically want it to display "00:60:00" instead of "01:00:00",
        # you can change the math below to: h = 0, m = total // 60
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return h, m, s
