
from datetime import timedelta


class Strings:
    start_button_text = "START"
    timer_text = str(timedelta(seconds=0))
    minutes = "Minutes"
    window_name: str = "Gym Timer"
    config = "Config"
    running = "Running"
    waiting = "Waiting"
    paused = "Paused"
    countdown = "Starting..."

    @staticmethod
    def round_x(x: int):
        return f'Round {x}'

    rest = "Rest"

    config_mode = "Mode:"
    config_amrap = "AMRAP"
    config_emom = "EMOM"
    config_timer = "Timer"
    config_rounds = "Rounds"
    config_stopwatch = "Stopwatch"
    config_length = "Length:"
    config_round_length = "Round Length:"
    config_every = "Every:"
    config_for = "For:"
    config_time_zeros = "00:00"
    config_rest = "Rest:"
    config_down = "\u21e9"
    config_preview = "Preview:"
    config_confirm = "Confirm"
