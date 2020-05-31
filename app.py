from strings_en import Strings
from timer import Timer, EmomTimer
import tkinter as tk
from tkinter import StringVar
import threading
import time
import datetime
from datetime import timedelta
from webserver import ServerController, run_server, stop_server
from globalconfig import GlobalConfig
from enum import Enum
from lib import int_list_to_int
import inspect


class AppState(Enum):
    INIT = 0
    RUNNING = 1
    CONFIG = 2
    PAUSED = 3
    WAITING = 4


class TimeUpdate:
    def __init__(self, hour=-1, min=-1, sec=-1, ms=-1):
        self.hour = hour
        self.min = min
        self.sec = sec
        self.ms = ms

    def get_time_delta(self) -> timedelta:
        return timedelta(hours=int(self.hour),
                         minutes=int(self.min),
                         seconds=int(self.sec),
                         milliseconds=int(self.ms))

    def update_last_update(self, previous) -> bool:
        changed = False

        if self.hour != -1 and previous.hour != self.hour:
            previous.hour = self.hour
            changed = True
        if self.min != -1 and previous.min != self.min:
            previous.min = self.min
            changed = True
        if self.sec != -1 and previous.sec != self.sec:
            previous.sec = self.sec
            changed = True
        if self.ms != -1 and previous.ms != self.ms:
            previous.ms = self.ms
            changed = True
        return changed

    def contains_placeholder(self) -> bool:
        return self.ms == -1 or self.sec == -1 or self.min == -1 or self.hour == -1

    def __str__(self):
        ret = ''
        if GlobalConfig.clock_hour:
            ret += f'{self.hour}:'
        ret += f'{self.min}:{self.sec}'
        if GlobalConfig.clock_ms_digits > 0:
            ret += f'.{self.ms}'
        return ret


class app(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.state = AppState.INIT

        self.initialize_variables()
        self.config(bg=GlobalConfig.background)
        self.apply_global_config()
        self.grid_setup()
        self.initialize_ui_elements()
        self.pack_ui()
        self.initialize_ui()
        self.initialize_server()

        self.state = AppState.CONFIG

    def initialize_variables(self) -> None:
        self.timer: Timer = None
        self.alive = True
        self.display_seconds = -1.0
        self.display_ms = -1.0
        self.clock_str = ''
        self.last_time_update = TimeUpdate(0, 0, 0, 0)
        self.td_seconds = 0
        self.td_ms = 0
        self.last_time_delta = timedelta()
        self.timer_length = timedelta()
        self.state_cycles = {
            AppState.INIT: 0,
            AppState.RUNNING: 0,
            AppState.CONFIG: 0,
            AppState.PAUSED: 0,
            AppState.WAITING: 0,
        }

    def grid_setup(self) -> None:
        """
        Assign row numbers
        """
        self.digit_row = 0
        self.info_row = 1

    def apply_global_config(self) -> None:
        """
        Apply configuration from glboalconfig.py
        """
        self.attributes("-fullscreen", GlobalConfig.fullscreen)

    def initialize_ui_elements(self) -> None:
        """
        Initialize UI compoents to be implmeneted
        in other functions
        """
        self.frame = tk.Frame(master=self)

        self.clock_stringvar = StringVar()
        self.clock_label = tk.Label(master=self.frame,
                                    textvar=self.clock_stringvar)

        self.info_stringvar = StringVar()
        self.info_label = tk.Label(master=self.frame,
                                   textvar=self.info_stringvar)

    def pack_ui(self) -> None:
        """
        Put items into the window
        """
        self.frame.pack()
        self.frame.config(padx=10, pady=10, bg=GlobalConfig.background)

        self.clock_label.config(
            font=(GlobalConfig.digit_font, GlobalConfig.digit_size),
            bg=GlobalConfig.background,
            fg=GlobalConfig.digit_color,
        )
        self.clock_label.grid(row=self.digit_row, column=0)

        self.info_label.grid(row=self.info_row)
        self.info_label.config(
            font=(GlobalConfig.text_font, GlobalConfig.text_size),
            bg=GlobalConfig.background,
            fg=GlobalConfig.text_color)
        self.info_stringvar.set('Waiting...')

    def initialize_ui(self) -> None:
        """
        Set initial value for UI elements
        """
        self.clock_stringvar.set('00:00.0')

    def set_clock(self, delta: timedelta) -> None:
        """
        Set the value of the clock based on the supplied timdelta
        and the parameters in global config
        """
        try:
            self.last_time_delta = delta
            time_delta_str = str(delta)
            hours, minutes, seconds = time_delta_str.split(':')
            if '.' in seconds:
                seconds, mseconds = seconds.split('.')
                mseconds = mseconds[:GlobalConfig.clock_ms_digits]
            else:
                mseconds = '0'
            self.last_time_update = TimeUpdate(hours, minutes, seconds, mseconds)
            self.update_clock()
        except Exception:
            print(delta)

    def update_clock(self) -> None:
        self.clock_stringvar.set(str(self.last_time_update))

    def zero_clock(self) -> None:
        self.clock_stringvar.set(str(TimeUpdate('00', '00', '00', '0'*GlobalConfig.clock_ms_digits)))

    def update(self):
        """
        Used to run application
        call tk's update
        """

        try:
            super().update()
            self.app_update()
            return True
        except Exception as e:
            # On exception close app
            return self.kill_app(e)

    def init_config(self) -> None:
        self.set_clock(timedelta(seconds=0.0))
        self.reset_cycle_conters()

        def set_time(msg: str) -> None:
            if ((not msg) or msg == 'START') and self.td_seconds > 0:
                while len(self.config_digits) < self.config_max_digits:
                    self.config_digits.insert(0, 0)
                return
            try:
                digit = int(msg[0])
            except Exception:
                return
            self.config_digits.append(digit)

        self.info_stringvar.set(Strings.config)
        self.config_max_digits = 6 if GlobalConfig.clock_hour else 4
        self.config_current_digit = 0
        self.config_digits = []
        ServerController.on_update = set_time

    def run_config(self) -> None:
        if self.config_current_digit == len(self.config_digits):
            return
        self.show_microwave_time(self.config_digits)
        self.config_current_digit = len(self.config_digits)
        if self.config_current_digit == self.config_max_digits:
            self.timer_length = self.last_time_delta
            self.state = AppState.RUNNING

    def init_running(self) -> None:
        self.reset_cycle_conters()
        self.info_stringvar.set(Strings.running)

        def running_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == 'PAUSE':
                self.timer.pause()
                self.state = AppState.PAUSED
            if msg == 'STOP':
                self
            if msg == 'RESTART':
                self.restart_timer()

        ServerController.on_update = running_server_update
        if not self.timer:
            self.timer = Timer(self.timer_length)
            self.timer.start()

    def run_running(self) -> None:
        self.set_clock(self.timer.time_remaining)
        if self.timer.finished:
            self.kill_timer()
            self.state = AppState.WAITING

    def init_waiting(self) -> None:
        self.info_stringvar.set(Strings.waiting)
        self.reset_cycle_conters()

        def waiting_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == 'RESTART':
                self.restart_timer()
            elif msg == 'CONFIG':
                self.state = AppState.CONFIG

        ServerController.on_update = waiting_server_update
        self.state_cycles[AppState.WAITING] = 1

    def init_paused(self) -> None:
        self.info_stringvar.set(Strings.paused)
        self.reset_cycle_conters()
        self.set_clock(self.timer.time_remaining)

        def paused_on_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == 'RESUME' or msg == 'RUN':
                self.state = AppState.RUNNING
                print('resuming')
                self.timer.resume()
            elif msg == 'RESTART':
                self.restart_timer()
            elif msg == 'CONFIG':
                self.state = AppState.CONFIG

        ServerController.on_update = paused_on_server_update

    def run_paused(self) -> None:
        self.set_clock(self.timer.time_remaining)

    def initialize_server(self):
        """
        Start and setup webserver
        """

        if not GlobalConfig.web_server:
            return

        def on_server_msg(msg: str) -> None:
            msg = msg.upper()
            print(msg)

        ServerController.on_update = on_server_msg
        run_server()

    def kill_app(self, e: Exception) -> bool:
        """
        Kill the app and close other threads, etc.
        """
        print(e)
        if self.timer:
            self.timer.kill = True
        self.alive = False
        stop_server()
        return False

    def show_microwave_time(self, num_list: []) -> None:
        """
        [1] -> 00:01
        [1, 2] -> 00:12
        [1, 2, 3] -> 1:23
        [1, 2, 3, 4] -> 12:34
        """
        if len(num_list) == 0:
            return
        if len(num_list) <= 2:
            secs = int_list_to_int(num_list)
            self.set_clock(timedelta(seconds=secs))
        elif len(num_list) <= 4:
            secs = int_list_to_int(num_list[-2:])
            mins = int_list_to_int(num_list[:-2])
            self.set_clock(timedelta(seconds=secs, minutes=mins))
        else:
            hrs = int_list_to_int(num_list[:-4])
            min_sec = num_list[-4:]
            secs = int_list_to_int(min_sec[-2:])
            mins = int_list_to_int(min_sec[:-2])
            self.set_clock(timedelta(seconds=secs, minutes=mins, hours=hrs))

    def reset_cycle_conters(self) -> None:
        for key in self.state_cycles:
            self.state_cycles[key] = 0

    def kill_timer(self) -> None:
        if self.timer:
            self.timer.kill = True
            self.timer.join()
            self.timer = None
            self.zero_clock()

    def restart_timer(self) -> None:
        if self.timer:
            self.timer.restart()
            self.state = AppState.PAUSED
        else:
            self.timer = Timer(self.timer_length)
            self.timer.start()
            self.state = AppState.RUNNING

    def increment_cycles(self, state: AppState) -> None:
        try:
            self.state_cycles[state] = (self.state_cycles[state] % 1000000) + 1
        except Exception:
            return

    def app_update(self) -> None:
        """
        Custom update code
        """

        if self.state == AppState.CONFIG:
            if self.state_cycles[AppState.CONFIG] == 0:
                self.init_config()
            else:
                self.run_config()
            self.increment_cycles(AppState.CONFIG)
        elif self.state == AppState.RUNNING:
            if self.state_cycles[AppState.RUNNING] == 0:
                self.init_running()
            else:
                self.run_running()
            self.increment_cycles(AppState.RUNNING)
        elif self.state == AppState.WAITING:
            if self.state_cycles[AppState.WAITING] == 0:
                self.init_waiting()
            else:
                pass
        elif self.state == AppState.PAUSED:
            if self.state_cycles[AppState.PAUSED] == 0:
                self.init_paused()
            else:
                self.run_paused()
            self.increment_cycles(AppState.PAUSED)
        else:
            pass


if __name__ == "__main__":
    # window.attributes("-fullscreen", True)
    gym_app = app()
    while gym_app.update():
        pass
