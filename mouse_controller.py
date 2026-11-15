import ctypes
import threading
import time
from ctypes import wintypes

import pyautogui

user32 = ctypes.windll.user32


class MouseGuard:
    """鼠标锁定与解锁间隙内的安全鼠标动作封装。

    游戏脚本治疗期间需要把光标回弹锁定在固定位置，防止误拖；
    每次真正移动 / 点击 / 滚动前短暂解锁，动作完成后再重新锁定。

    示例::

        mouse = MouseGuard()
        mouse.lock()
        mouse.click(x, y)
        mouse.unlock()
    """

    def __init__(self):
        self._running = False
        self._lock_x = 0
        self._lock_y = 0
        self._thread = None

    def _guard_loop(self):
        """后台线程：持续把光标拉回锁定坐标。"""
        while self._running:
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            if pt.x != self._lock_x or pt.y != self._lock_y:
                user32.SetCursorPos(self._lock_x, self._lock_y)
            time.sleep(0.01)

    def lock(self):
        """记录当前光标位置并启动回弹锁定线程。"""
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        self._lock_x = pt.x
        self._lock_y = pt.y
        self._running = True
        self._thread = threading.Thread(target=self._guard_loop, daemon=True)
        self._thread.start()

    def unlock(self):
        """停止回弹锁定线程，并短暂等待线程退出。"""
        self._running = False
        time.sleep(0.05)

    def move_to(self, x, y, hold_delay=0.5):
        """解锁后移动到指定绝对坐标，再重新锁定并停留 hold_delay 秒。"""
        self.unlock()
        pyautogui.moveTo(x, y)
        self.lock()
        time.sleep(hold_delay)

    def click(self, x, y, move_delay=0.5, click_delay=1):
        """在指定绝对坐标安全点击：解锁 -> 移动 -> 锁定 -> 点击。"""
        self.unlock()
        pyautogui.moveTo(x, y)
        self.lock()
        time.sleep(move_delay)
        pyautogui.click(x, y)
        time.sleep(click_delay)

    def scroll(self, x, y, clicks, move_delay=0.5, scroll_delay=1):
        """在指定绝对坐标安全滚动滚轮：解锁 -> 移动 -> 锁定 -> 滚动。"""
        self.unlock()
        pyautogui.moveTo(x, y)
        self.lock()
        time.sleep(move_delay)
        pyautogui.scroll(clicks, x, y)
        time.sleep(scroll_delay)
