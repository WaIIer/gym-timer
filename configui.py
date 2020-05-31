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


class DrirectionEnum(Enum):
    UP = -1
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class ClockModes(Enum):
    AMRAP = 0
    EMOM = 1
    TIMER = 2
    STOPWATCH = 3


class ClockConfig:
    mode = ClockModes.AMRAP
    direction = 'DOWN'
    seconds = [0]
    rest = [0]
    rounds = 1

    @staticmethod
    def set_timer_length(seconds: int, round: int = 0):
        if ClockConfig.mode == ClockModes.AMRAP:
            ClockConfig.seconds = [seconds]

    @staticmethod
    def set_rest_length(seconds: int, round: int = 0):
        if ClockConfig.mode == ClockModes.AMRAP:
            ClockConfig.rest = [seconds]

    @staticmethod
    def preview() -> str:
        rounds_str = 'rounds' if ClockConfig.rounds > 1 else 'round'
        if ClockConfig.mode == ClockModes.AMRAP:
            ret = f'{ClockConfig.rounds} {rounds_str} of {ClockConfig.length_str(ClockConfig.seconds[0])}'
            if ClockConfig.rest[0] > 0:
                ret += f'with {ClockConfig.length_str(ClockConfig.rest[0])} between rounds'
            return ret
        return ''

    @staticmethod
    def length_str(seconds: int) -> str:
        if seconds < 60:
            return f'{seconds} seconds'
        elif seconds < 3600:
            mins, secs = divmod(seconds, 60)
            return f'{mins}:{str(secs).zfill(2)}'
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        return f'{hours}:{str(mins).zfill(2)}:{str(secs).zfill(2)}'


class ConfigUi(tk.Frame):

    def __init__(self, master: tk.Tk):
        self.count = 0
        super(ConfigUi, self).__init__(master)
        self.config(
            bg=GlobalConfig.background,
            pady=10
        )
        self.pack(fill=tk.BOTH)

        self.queue = []

        self.grid_options = []
        self.labels = []
        self.labels.append([])
        self.add_option(OptionLabel(self, Strings.config_mode), 0)
        self.add_option(OptionLabel(self, Strings.config_amrap, onselected=self.on_amrap_selected), 0)
        self.add_option(OptionLabel(self, Strings.config_emom), 0)
        self.add_option(OptionLabel(self, Strings.config_timer), 0)
        self.add_option(OptionLabel(self, Strings.config_stopwatch), 0)

        self.hovered: OptionLabel = self.labels[0][1]
        self.hovred_pos = (1, 0)
        self.hovered.hover()

        ServerController.on_update = self.config_on_server_update

    def add_option(self, option_label, row):
        while len(self.labels) <= row:
            self.labels.append([])
        self.labels[row].append(option_label)
        col = len(self.labels[row]) - 1
        option_label.grid(row=row, column=col)
        if col != 0 and option_label.selectable:
            self.grid_options.append((col, row))
        elif col == 0:
            option_label.config(anchor=tk.W)

    def flash_hovered(self):
        for row in self.labels:
            for label in row:
                if not label.hovered:
                    continue
                label.hide_text()
                self.after(400, label.show_text)

    def select_hovered(self):
        self.hovered.select()

    def type_selected(self):
        self.preview_label = WideLabel(self, '', width_cols=3)
        self.labels = [self.labels[0]]
        self.grid_options = [(x, y) for x, y in self.grid_options if y == 0]

    def on_amrap_selected(self):
        self.type_selected()
        ClockConfig.mode = ClockModes.AMRAP
        self.add_option(OptionLabel(self, Strings.config_length), 1)
        self.add_option(TimeInputLabel(self, onnumberinput=self.on_time_digit), 1)  # round length
        self.add_option(OptionLabel(self, Strings.config_down, selectable=False), 1)

        self.add_option(OptionLabel(self, Strings.config_rounds, selectable=False), 2)
        self.add_option(NumberInputLabel(self, 2, onnumberinput=self.on_rounds_digit), 2)  # round input
        self.add_option(OptionLabel(self, Strings.config_down, selectable=False), 2)

        self.add_option(OptionLabel(self, Strings.config_rest, selectable=False), 3)
        self.add_option(TimeInputLabel(self, onnumberinput=self.on_rest_digit), 3)
        self.add_option(OptionLabel(self, Strings.config_down, selectable=False), 3)

        self.add_option(OptionLabel(self, Strings.config_preview, selectable=False), 4)
        self.add_option(self.preview_label, 4)

        self.hover(1, 1)

    def move(self, direction: DrirectionEnum) -> bool:
        x, y = self.hovred_pos
        if direction == DrirectionEnum.UP or direction == DrirectionEnum.DOWN:
            y += direction.value
            if x < 0 or x > len(self.labels):
                return False
            while x >= 1:
                if (x, y) in self.grid_options:
                    self.hover(x, y)
                    return True
                x -= 1
            return False
        if direction == DrirectionEnum.RIGHT:
            x += 1
        else:
            x -= 1
        if (x, y) in self.grid_options:
            self.hover(x, y)
            return True
        return False

    def hover(self, x, y):
        self.hovred_pos = (x, y)
        self.hovered.unhover()
        self.hovered = self.labels[y][x]
        self.hovered.hover()
        return True

    def config_on_server_update(self, msg: str):
        msg = msg.upper()
        if msg == 'UP':
            self.move(DrirectionEnum.UP)
        elif msg == 'DOWN':
            self.move(DrirectionEnum.DOWN)
        elif msg == 'RIGHT':
            self.move(DrirectionEnum.RIGHT)
        elif msg == 'LEFT':
            self.move(DrirectionEnum.LEFT)
        elif msg == 'STOP':
            self.queue.append(self.select_hovered)
        elif msg.isdigit():
            if self.hovered.number_input:
                self.queue.append(lambda: self.hovered.insert_digit(msg))

    def on_time_digit(self, seconds: int) -> None:
        ClockConfig.seconds = [seconds]
        self.queue.append(lambda: self.preview_label.set_text(ClockConfig.preview()))
        print(ClockConfig.preview())

    def on_rounds_digit(self, number: int) -> None:
        ClockConfig.rounds = number
        self.queue.append(lambda: self.preview_label.set_text(ClockConfig.preview()))
        print(ClockConfig.preview())

    def on_rest_digit(self, seconds: int) -> None:
        ClockConfig.rest = [seconds]
        self.queue.append(lambda: self.preview_label.set_text(ClockConfig.preview()))
        print(ClockConfig.preview())


class OptionLabel(tk.Label):

    def __init__(self, master: tk.Frame, text: str, selectable: bool = True, onselected=None):
        super(OptionLabel, self).__init__(master)
        self.selected = False
        self.hovered = False
        self.empty = not bool(text)
        self.normal_color = GlobalConfig.text_color
        self.selectable = selectable and not self.empty
        self.on_selected = onselected
        self.string_var = StringVar(self, value=text)

        self.config(
            # justify=tk.LEFT,
            anchor=tk.CENTER,
            pady=5,
            padx=3,
            width=GlobalConfig.config_col_width,
            textvariable=self.string_var,
        )
        self._config()
        self.number_input = False

    def set_text(self, s: str):
        self.string_var.set(s)

    def _config(self):
        self.config(
            bg=GlobalConfig.background,
            fg=self.normal_color,
            # height=1,
            font=(GlobalConfig.text_font, 30),
        )

    def select(self):
        if not self.selected:
            self.selected = True
            self.config(
                bg=GlobalConfig.config_selected_bg_color,
                fg=GlobalConfig.background,
                highlightcolor=GlobalConfig.background
            )
        if self.on_selected:
            self.on_selected()

    def deselect(self):
        self.selected = False
        self._config()

    def hover(self):
        self.hovered = True

    def unhover(self):
        self.hovered = False

    def show_text(self):
        if not self.selected:
            self.config(fg=self.normal_color)

    def hide_text(self):
        self.config(fg=GlobalConfig.background)


class WideLabel(OptionLabel):
    def __init__(self, master, text, width_cols: int, selectable=True, onselected=None):
        super().__init__(master, text, selectable=selectable, onselected=onselected)
        self.config(
            width=width_cols*GlobalConfig.config_col_width,
        )


class TimeInputLabel(OptionLabel):
    def __init__(self, master, onnumberinput=lambda num: None):
        super(TimeInputLabel, self).__init__(master, Strings.config_time_zeros)
        self.string_var.set(value=Strings.config_time_zeros)
        self.normal_color = GlobalConfig.digit_color
        self.digits = ['0' for i in range(4)]
        self.config(
            font=(GlobalConfig.digit_font, 30),
            fg=self.normal_color)
        self.number_input = True
        self.onnumberinput = onnumberinput

    def insert_digit(self, digit: str):
        self.digits = self.digits[0:3]
        self.digits.insert(0, digit)
        self.string_var.set('{}{}:{}{}'.format(self.digits[3], self.digits[2],
                                               self.digits[1], self.digits[0]))
        self.onnumberinput(self.get_seconds())

    def get_seconds(self) -> int:
        digits = [int(digit) for digit in self.digits]
        seconds = digits[0] + 10*digits[1]
        minutes = digits[2] + 10*digits[3]
        return seconds + 60*minutes


class NumberInputLabel(OptionLabel):
    def __init__(self, master, digits: int = 2, onnumberinput=lambda num: None):
        super(NumberInputLabel, self).__init__(master, '0'*digits)
        self.string_var.set(value='0'*digits)
        self.normal_color = GlobalConfig.digit_color
        self.digits = ['0' for i in range(digits)]
        self.config(
            font=(GlobalConfig.digit_font, 30),
            fg=self.normal_color)
        self.number_input = True
        self.onnumberinput = onnumberinput

    def insert_digit(self, digit: str):
        self.digits = [self.digits[1]]
        self.digits.append(digit)
        self.string_var.set(''.join(self.digits))
        self.onnumberinput(int(self.string_var.get()))


class DemoWindow(tk.Tk):

    def __init__(self):
        super(DemoWindow, self).__init__()
        self.config(bg=GlobalConfig.background)
        self.config_ui = ConfigUi(self)
        self.start_time = time.time()
        run_server()

    def update(self):
        try:
            super().update()
            if time.time() - self.start_time > .9:
                self.config_ui.flash_hovered()
                self.start_time = time.time()
            for f in self.config_ui.queue:
                f()
            self.config_ui.queue = []
            return True
        except Exception as e:
            print(e)
            stop_server()
            return False

    def initialize_server(self):
        """
        Start and setup webserver
        """

        if not GlobalConfig.web_server:
            return

        def on_server_msg(msg: str) -> None:
            msg = msg.upper()
            print(msg)

        run_server()


if __name__ == '__main__':
    t = DemoWindow()
    while t.update():
        pass
