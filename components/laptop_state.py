from core.component import Component

WORK_DURATION = 5.0

TYPING_TEXT = (
    "Exam Supervision Log\n"
    "--------------------\n"
    "Room: 204B\n"
    "Invigilator: On Duty\n"
    "Status: Monitoring active...\n"
    "Notes: All students seated.\n"
    "Next round: In progress...\n"
)


class LaptopState(Component):
    def __init__(self):
        self.is_visible = True
        self.is_being_used = False  # True while the full-screen takeover is active
        self.is_work_done = False  # Flips to True when timer completes
        self.work_timer = 0.0  # Accumulates dt while is_being_used is True
        self.typed_chars = 0  # How many characters have been revealed so far

    def start_work(self):
        self.is_being_used = True
        self.is_work_done = False
        self.work_timer = 0.0
        self.typed_chars = 0

    def update(self, dt):
        if not self.is_being_used or self.is_work_done:
            return

        self.work_timer += dt

        # Reveal characters proportionally across the full duration
        progress = min(self.work_timer / WORK_DURATION, 1.0)
        self.typed_chars = int(progress * len(TYPING_TEXT))

        if self.work_timer >= WORK_DURATION:
            self.typed_chars = len(TYPING_TEXT)
            self.is_work_done = True

    def finish(self):
        """Called when player dismisses the screen after work is done."""
        self.is_being_used = False
        self.is_work_done = False
        self.work_timer = 0.0
        self.typed_chars = 0
