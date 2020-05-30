class GlobalConfig:
    fullscreen: bool = False
    digit_font: str = 'DSEG7 Modern-Regular'
    text_font: str = None
    background: str = 'gray1'
    digit_color: str = 'red2'
    digit_size: int = 100
    text_size: int = 30
    text_color: str = 'snow'
    clock_hour: bool = False
    clock_ms_digits: int = 1  # set to 0 to disable ms
    web_server: bool = True
    server_port: int = 5050
    message_bits: int = 64
    encoding: str = 'ascii'
