import mss
import win32com.client
import win32con
import win32gui


def find_windows_by_title(keyword):
    """查找所有标题包含 keyword 的窗口，返回 [(hwnd, title), ...]。"""
    hwnd_list = []

    def callback(hwnd, extra):
        title = win32gui.GetWindowText(hwnd)
        if keyword in title:
            hwnd_list.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, None)
    return hwnd_list


def find_first_window(keyword):
    """返回标题包含 keyword 的第一个窗口句柄；未找到时返回 None。"""
    windows = find_windows_by_title(keyword)
    return windows[0][0] if windows else None


def get_window_rect(hwnd):
    """返回窗口矩形 (left, top, right, bottom)。"""
    return win32gui.GetWindowRect(hwnd)


def to_absolute(rect, rel):
    """窗口相对坐标 (rel_x, rel_y) 换算为屏幕绝对坐标 (abs_x, abs_y)。"""
    left, top, _, _ = rect
    rel_x, rel_y = rel
    return left + rel_x, top + rel_y


def get_window_pixel(hwnd, rel_x, rel_y):
    """读取窗口内相对坐标 (rel_x, rel_y) 处像素的 RGB 颜色。"""
    if not win32gui.IsWindow(hwnd):
        print("【错误】hwnd 无效，不是有效窗口")
        return None

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    abs_x = left + rel_x
    abs_y = top + rel_y

    with mss.MSS() as sct:
        monitor = {"top": abs_y, "left": abs_x, "width": 1, "height": 1}
        img = sct.grab(monitor)
        r, g, b = img.pixel(0, 0)
        return (r, g, b)


def activate_window(hwnd):
    """激活并前置指定窗口，绕过前台锁定限制。"""
    foreground_window = win32gui.GetForegroundWindow()
    if foreground_window == hwnd:
        return
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    # 这个 trick 绕过前台锁定
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)
