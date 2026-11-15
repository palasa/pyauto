from datetime import datetime

# 日志颜色 ANSI 码
LOG_COLORS = {
    "white": "\033[97m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
}


def log(message, color="white"):
    """带时间戳的统一日志打印。

    :param message: 日志内容
    :param color: 日志颜色，可选 "white"（默认）/ "green" / "yellow" / "red"
    """
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color_code = LOG_COLORS.get(color, "")
    print(f"{color_code}[{time_str}]{message}\033[0m")
