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


class app(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.initialize_variables()
        self.config(bg=GlobalConfig.background)
        self.apply_global_config()
        self.grid_setup()
        self.initialize_ui_elements()
        self.pack_ui()
        self.initialize_ui()
        self.initialize_server()

    def initialize_variables(self) -> None:
        self.timer: Timer = None
        self.alive = True
        self.display_seconds = -1.0

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
        td_seconds = delta.total_seconds()
        if td_seconds == self.display_seconds:
            return
        if td_seconds == 0:
            self.display_seconds = td_seconds
            self.set_clock_stringvar(0, 0, 0)
            return

        seconds = td_seconds
        hrs = int(seconds // 3600)
        seconds = seconds % 3600
        mins = int(seconds // 60)
        seconds = seconds % 60
        self.set_clock_stringvar(hrs, mins, seconds)

    def set_clock_stringvar(self, hrs: int, mins: int, secs: float) -> None:
        clock_str = ''
        if GlobalConfig.clock_hour:
            clock_str += f'{str(hrs)}:'
        clock_str += f'{str(mins).zfill(2)}:'
        if GlobalConfig.clock_ms_digits > 0:
            clock_str += '{0:0{1}.{2}f}'.format(
                secs, GlobalConfig.clock_ms_digits+3,
                GlobalConfig.clock_ms_digits)
        else:
            clock_str += str(int(secs))

        self.clock_stringvar.set(clock_str)

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

    def app_update(self) -> None:
        """
        Custom update code
        """
        if self.timer is None:
            self.timer = Timer(timer_length=timedelta(seconds=120))
            self.set_clock(self.timer.time_remaining)
        elif self.timer.running:
            self.set_clock(self.timer.time_remaining)
        elif self.timer.finished:
            self.timer.restart()

    def initialize_server(self):
        """
        Start and setup webserver
        """

        if not GlobalConfig.web_server:
            return

        def on_server_msg(msg: str) -> None:
            msg = msg.upper()
            print(msg)
            if msg == 'START':
                self.timer.start()

        ServerController.on_update = on_server_msg
        run_server()

    def kill_app(self, e: Exception) -> bool:
        """
        Kill the app and close other threads, etc.
        """
        print(e)
        self.timer.kill = True
        self.alive = False
        stop_server()
        return False


if __name__ == "__main__":
    # window.attributes("-fullscreen", True)
    gym_app = app()
    while gym_app.update():
        pass
