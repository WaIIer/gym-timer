from strings_en import Strings
from timer import Timer, EmomTimer
import tkinter as tk
from tkinter import StringVar
import threading
import time
import datetime
from datetime import timedelta
from globalconfig import GlobalConfig


class app(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.timer = None

        self.config(bg=GlobalConfig.background)
        self.apply_global_config()
        self.grid_setup()
        self.initialize_ui_elements()
        self.pack_ui()
        self.initialize_ui()

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
        time_str = str(delta)
        if not GlobalConfig.clock_hour:
            min_start = time_str.find(':') + 1
            time_str = time_str[min_start:]
        # TODO add other cases
        self.clock_stringvar.set(time_str[:time_str.find('.')+2])

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
            print(e)
            self.timer.kill = True
            return False

    def app_update(self) -> None:
        """
        Custom update code
        """
        if self.timer is None:
            print('Awaiting input')
            input()
            self.timer = Timer(timer_length=timedelta(
                seconds=10))
            self.timer.start()
        else:
            if not self.timer.running:
                print("Timer is not runing")
                self.timer = None
            else:
                self.set_clock(delta=self.timer.time_remaining)


if __name__ == "__main__":
    # window.attributes("-fullscreen", True)
    gym_app = app()
    while gym_app.update():
        pass
