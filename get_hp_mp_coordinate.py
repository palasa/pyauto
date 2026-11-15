import rectangles
from digit_match import grab_region_gray, recognize_gray, recognize_location
from window_utils import activate_window, find_first_window

DOCTOR_WINDOW_TITLE = "安侑真"

# 当前生命值、最大生命值、当前魔法值、最大魔法值
current_hp: int = 0
max_hp: int = 0
current_mp: int = 0
max_mp: int = 0

# 地图坐标：东向坐标(EAST)、南向坐标(SOUTH)
east_coord: int = 0
south_coord: int = 0


def _read_region(hwnd, region) -> int:
    """截取指定窗口相对区域，用血蓝模板匹配识别为整数。"""
    gray = grab_region_gray(hwnd, region)
    return recognize_gray(gray)


def _read_location_region(hwnd, region) -> int:
    """截取指定窗口相对区域，用坐标模板匹配识别为整数。"""
    gray = grab_region_gray(hwnd, region)
    return recognize_location(gray)


def read_hp_mp(hwnd) -> tuple[int, int, int, int]:
    """读取单个窗口的血蓝量。

    :return: (当前生命值, 最大生命值, 当前魔法值, 最大魔法值)
    """
    cur_hp = _read_region(hwnd, rectangles.CURRENT_HP)
    mx_hp = _read_region(hwnd, rectangles.MAX_HP)
    cur_mp = _read_region(hwnd, rectangles.CURRENT_MP)
    mx_mp = _read_region(hwnd, rectangles.MAX_MP)
    return cur_hp, mx_hp, cur_mp, mx_mp


def refresh_hp_mp(hwnd) -> tuple[int, int, int, int]:
    """识别医生窗口的血蓝量，回填四个全局变量。

    :param hwnd: 医生窗口句柄
    :return: (当前生命值, 最大生命值, 当前魔法值, 最大魔法值)
    """
    global current_hp, max_hp, current_mp, max_mp
    current_hp, max_hp, current_mp, max_mp = read_hp_mp(hwnd)
    return current_hp, max_hp, current_mp, max_mp


def get_location(hwnd) -> tuple[int, int]:
    """读取医生窗口地图坐标（东向 EAST、南向 SOUTH），回填全局坐标变量。

    :param hwnd: 窗口句柄
    :return: (东向坐标, 南向坐标)
    """
    global east_coord, south_coord
    east_coord = _read_location_region(hwnd, rectangles.EAST)
    south_coord = _read_location_region(hwnd, rectangles.SOUTH)
    return east_coord, south_coord


def main():
    """查找医生窗口，读取血蓝量与地图坐标并打印。"""
    hwnd = find_first_window(DOCTOR_WINDOW_TITLE)
    if hwnd is None:
        print(f"未找到窗口：{DOCTOR_WINDOW_TITLE}")
        return None

    activate_window(hwnd)
    current_hp, max_hp, current_mp, max_mp = refresh_hp_mp(hwnd)
    print(f"生命：{current_hp}/{max_hp}  魔法：{current_mp}/{max_mp}")

    east_coord, south_coord = get_location(hwnd)
    print(f"坐标：东 {east_coord}  南 {south_coord}")
    return current_hp, max_hp, current_mp, max_mp


if __name__ == "__main__":
    main()
