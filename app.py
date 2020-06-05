from strings_en import Strings
from timer import Timer, EmomTimer, CountdownTimer
import tkinter as tk
from tkinter import StringVar
import threading
import time
import datetime
from datetime import timedelta
from webserver import ServerController, run_server, stop_server, MsgEnum
from globalconfig import GlobalConfig
from enum import Enum
from lib import int_list_to_int, AppState, TimeUpdate
import inspect
from configui import ConfigUi, DrirectionEnum, ClockConfig, ClockModes
import traceback


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

        self.state = AppState.CLOCK

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
        self.current_clock_time: datetime.datetime = datetime.datetime.now()
        self.config_current_digit: int = 0
        self.config_digits = []
        self.job_queue = []
        self.timer_queue = []
        self.last_state: AppState = AppState.INVALID
        self.state_cycles = {state: 0 for state in AppState}

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
        if not GlobalConfig.fullscreen:
            self.geometry("1366x768")

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
        self.frame.config(padx=GlobalConfig.xpadding, pady=GlobalConfig.ypadding, bg=GlobalConfig.background)

        self.clock_label.config(
            font=(GlobalConfig.digit_font, GlobalConfig.digit_size),
            bg=GlobalConfig.background,
            fg=GlobalConfig.digit_color,
        )
        self.clock_label.grid(row=self.digit_row, column=0, pady=20)

        self.info_label.grid(row=self.info_row)
        self.info_label.config(
            font=(GlobalConfig.text_font, GlobalConfig.text_size),
            bg=GlobalConfig.background,
            fg=GlobalConfig.text_color,
            pady=20)
        self.info_stringvar.set('Waiting...')

    def initialize_ui(self) -> None:
        """
        Set initial value for UI elements
        """
        self.clock_stringvar.set('00:00.0')

    def transition(self, other: AppState, transition_data: [] = None) -> None:
        self.last_state = self.state
        self.state = other
        self.transition_data = transition_data if transition_data else None
        self.reset_cycle_conters()

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

    def set_clock_preserved(self, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        try:
            self.last_time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            hour_str = ''
            if GlobalConfig.clock_hour:
                hour_str = f'{str(hours).zfill(1)}:'
            min_sec_str = f'{str(minutes).zfill(2)}:{str(seconds).zfill(2)}'
            if GlobalConfig.clock_ms_digits > 0:
                self.clock_stringvar.set(hour_str + min_sec_str + '.' + ('0' * GlobalConfig.clock_ms_digits))
            else:
                self.clock_stringvar.set(hour_str + min_sec_str)
        except Exception:
            return

    def update_clock(self) -> None:
        self.clock_stringvar.set(str(self.last_time_update))

    def show_current_time(self) -> None:
        self.clock_stringvar.set(self.current_clock_time.strftime("%H:%M:%S"))

    def zero_clock(self) -> None:
        self.clock_stringvar.set(str(TimeUpdate('00', '00', '00', '0'*GlobalConfig.clock_ms_digits)))

    def init_config(self) -> None:
        self.set_clock(timedelta(seconds=0.0))

        def config_on_server_update(msg: str) -> None:
            msg = msg.upper()
            if (msg == MsgEnum.START.value) and self.config_digits:
                while len(self.config_digits) < self.config_max_digits:
                    self.config_digits.insert(0, 0)
                return
            elif msg.isdigit():
                self.config_digits.append(int(msg))
            elif msg == MsgEnum.CONFIG.value:
                self.job_queue.append(self.show_advancedconfig_ui)
            elif msg == MsgEnum.POWER.value:
                self.transition(AppState.CLOCK)

        self.info_stringvar.set(Strings.config)
        self.config_max_digits = 6 if GlobalConfig.clock_hour else 4
        self.config_current_digit = 0
        self.config_digits = self.transition_data if self.transition_data else []
        ServerController.on_update = config_on_server_update

    def show_advancedconfig_ui(self) -> None:
        self.frame.pack_forget()
        self.advancedconfig_ui = ConfigUi(self, onconfirm=self.on_advancedconfig_confirm)
        self.advancedconfig_ui.pack()
        self.transition(AppState.ADVANCEDCONFIG)

    def hide_advancedconfig_ui(self) -> None:
        if self.advancedconfig_ui:
            self.advancedconfig_ui.pack_forget()
            self.frame.pack()
            self.advancedconfig_ui = None

    def run_config(self) -> None:
        if self.config_current_digit == len(self.config_digits):
            return
        self.show_microwave_time(self.config_digits)
        self.config_current_digit = len(self.config_digits)
        if self.config_current_digit == self.config_max_digits:
            self.timer_length = self.last_time_delta
            self.transition(AppState.RUNNING)

    def init_advancedconfig(self) -> None:
        self.advancedconfig_flash_time = int(time.monotonic())
        ServerController.on_update = self.advancedconfig_ui.config_on_server_update

    def run_advancedconfig(self) -> None:
        if int(time.time()) != self.advancedconfig_flash_time:
            self.advancedconfig_ui.flash_hovered()
            self.advancedconfig_flash_time = int(time.time())
        if self.advancedconfig_ui.queue:
            [f() for f in self.advancedconfig_ui.queue]
            self.advancedconfig_ui.queue = []

    def init_advancedtimer(self) -> None:
        self.hide_advancedconfig_ui()
        if self.last_state is not AppState.PAUSED:
            self.timer_queue = ClockConfig.generate_timers()
            self.timer_queue.insert(0, CountdownTimer())
            self.timer = None

        def advancedtimer_on_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == MsgEnum.STOP.value:
                pass
            if msg == MsgEnum.PAUSE.value:
                self.timer.pause()
                self.transition(AppState.PAUSED)
            if msg == MsgEnum.RESTART.value:
                self.job_queue.append(lambda: self.timer.restart())

        ServerController.on_update = advancedtimer_on_server_update

    def run_advanedtimer(self) -> None:
        if not self.timer:
            if not self.timer_queue:
                self.transition(AppState.CONFIG)
                return
            self.timer = self.timer_queue.pop(0)
            self.info_stringvar.set(self.timer.name)
            self.timer.start()
        if not self.timer.finished:
            self.set_clock(self.timer.time_remaining)
        else:
            self.kill_timer(self.timer)
            self.timer = None

    def init_clock(self) -> None:
        def clock_on_server_update(msg):
            msg = msg.upper()
            if msg.isdigit():
                self.transition(AppState.CONFIG, transition_data=[int(msg)])
            elif msg == MsgEnum.CONFIG.value:
                self.job_queue.append(self.show_advancedconfig_ui)
            elif msg == MsgEnum.POWER.value:
                self.transition(AppState.HIDDEN)
        ServerController.on_update = clock_on_server_update
        self.current_clock_time = self.datetime_now()
        self.info_stringvar.set(Strings.config)
        self.show_current_time()

    def run_clock(self) -> None:
        current_date_time = self.datetime_now()
        if current_date_time != self.current_clock_time:
            self.current_clock_time = current_date_time
            self.show_current_time()

    @staticmethod
    def datetime_now() -> datetime.datetime:
        return datetime.datetime.now()

    def on_advancedconfig_confirm(self) -> None:
        self.transition(AppState.ADVANCEDTIMER)

    def init_running(self) -> None:
        self.info_stringvar.set(Strings.running)

        def running_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == MsgEnum.PAUSE.value:
                self.timer.pause()
                self.transition(AppState.PAUSED)
            if msg == MsgEnum.STOP.value:
                self
            if msg == MsgEnum.RESTART.value:
                self.restart_timer()

        ServerController.on_update = running_server_update
        if not self.timer:
            self.timer = Timer(self.timer_length)
            self.timer.start()

    def run_running(self) -> None:
        self.set_clock(self.timer.time_remaining)
        if self.timer.finished:
            self.kill_timer(self.timer)
            self.transition(AppState.CONFIG)

    def init_waiting(self) -> None:
        self.info_stringvar.set(Strings.waiting)

        def waiting_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == MsgEnum.RESTART.value:
                self.restart_timer()
            elif msg == MsgEnum.CONFIG.value:
                self.transition(AppState.CONFIG)

        ServerController.on_update = waiting_server_update
        self.state_cycles[AppState.WAITING] = 1

    def init_paused(self) -> None:
        self.info_stringvar.set(Strings.paused)

        self.set_clock(self.timer.time_remaining)

        def paused_on_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == MsgEnum.PLAY.value:
                self.transition(self.last_state)
                print('resuming')
                self.timer.resume()
            elif msg == MsgEnum.RESTART.value:
                self.restart_timer()
            elif msg == MsgEnum.CONFIG.value:
                self.transition(AppState.CONFIG)

        ServerController.on_update = paused_on_server_update

    def run_paused(self) -> None:
        self.set_clock(self.timer.time_remaining)

    def init_hidden(self) -> None:
        self.clock_stringvar.set('')
        self.info_stringvar.set('')

        def hidden_on_server_update(msg: str) -> None:
            msg = msg.upper()
            if msg == MsgEnum.POWER.value:
                self.transition(self.last_state)
        ServerController.on_update = hidden_on_server_update

    def run_hidden(self) -> None:
        pass

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
        self.kill_timer(self.timer)
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
            self.set_clock_preserved(seconds=secs)
        elif len(num_list) <= 4:
            secs = int_list_to_int(num_list[-2:])
            mins = int_list_to_int(num_list[:-2])
            self.set_clock_preserved(minutes=mins, seconds=secs)
        else:
            hrs = int_list_to_int(num_list[:-4])
            min_sec = num_list[-4:]
            secs = int_list_to_int(min_sec[-2:])
            mins = int_list_to_int(min_sec[:-2])
            self.set_clock_preserved(seconds=secs, minutes=mins, hours=hrs)

    def reset_cycle_conters(self) -> None:
        for key in self.state_cycles:
            self.state_cycles[key] = -1

    def kill_timer(self, timer: Timer) -> None:
        if timer:
            timer.kill = True
            timer.join()
            timer = None
            self.zero_clock()

    def restart_timer(self) -> None:
        if self.timer:
            self.timer.restart()
            self.transition(AppState.PAUSED)
        else:
            self.timer = Timer(self.timer_length)
            self.timer.start()
            self.transition(AppState.RUNNING)

    def increment_cycles(self, state: AppState) -> None:
        try:
            self.state_cycles[state] += 1
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
        elif self.state == AppState.RUNNING:
            if self.state_cycles[AppState.RUNNING] == 0:
                self.init_running()
            else:
                self.run_running()
        elif self.state == AppState.ADVANCEDCONFIG:
            if self.state_cycles[AppState.ADVANCEDCONFIG] == 0:
                self.init_advancedconfig()
            else:
                self.run_advancedconfig()
        elif self.state == AppState.ADVANCEDTIMER:
            if self.state_cycles[AppState.ADVANCEDTIMER] == 0:
                self.init_advancedtimer()
            else:
                self.run_advanedtimer()
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
        elif self.state == AppState.CLOCK:
            if self.state_cycles[AppState.CLOCK] == 0:
                self.init_clock()
            else:
                self.run_clock()
        elif self.state == AppState.HIDDEN:
            if self.state_cycles[AppState.HIDDEN] == 0:
                self.init_hidden()
            else:
                self.run_hidden()
        else:
            pass

        if self.job_queue:
            [f() for f in self.job_queue]
            self.job_queue = []

        self.increment_cycles(self.state)

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
            print(self.state)
            return self.kill_app(e)


if __name__ == "__main__":
    # window.attributes("-fullscreen", True)
    gym_app = app()
    while gym_app.update():
        pass
