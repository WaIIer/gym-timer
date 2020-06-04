import sys
import tkinter as tk


class GlobalConfig:
    ypadding = 10
    xpadding = 10
    fullscreen: bool = False
    digit_font: str = 'DSEG7 Modern-Regular'
    text_font: str = None
    background: str = 'gray1'
    digit_color: str = 'red2'
    digit_size: int = 100
    text_size: int = 30
    text_color: str = 'white'
    clock_hour: bool = False
    clock_ms_digits: int = 1  # set to 0 to disable ms
    web_server: bool = True
    server_port: int = 5051
    message_bits: int = 64
    encoding: str = 'ascii'
    output_timer: bool = False
    beep: bool = True
    countdown_length: int = 3
    beep_file: str = 'ping1.wav'
    config_hover_border_color = 'white'
    config_selected_bg_color = 'white'
    config_selected_text_color = 'black'
    config_col_width = 10
    blocking_beep: bool = False

    countdown_time = 3


# RPi specific config
if sys.platform == "linux":
    GlobalConfig.digit_font = 'DSEG7 Modern'
    GlobalConfig.fullscreen = True
    GlobalConfig.digit_size = 300
    GlobalConfig.clock_ms_digits: int = 0  # set to 0 to disable ms
    GlobalConfig.ypadding = 200
    blocking_beep = True
