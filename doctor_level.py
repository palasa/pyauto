from typing import Any

import cv2

import rectangles
from digit_match import grab_region_gray
from window_utils import get_window_pixel
import heal_config as config

# cv2 为二进制扩展，类型存根不完整，静态分析易误报；别名标注为 Any 后按实际运行处理
_cv2: Any = cv2

_skill_level_tpl = None


def _get_skill_level_template(size):
    """惰性加载标题栏灰度模板，并缩放到截图区域尺寸；模板缺失时返回 None。"""
    global _skill_level_tpl
    if _skill_level_tpl is None:
        gray = _cv2.imread(config.SKILL_LEVEL_TPL_PATH, _cv2.IMREAD_GRAYSCALE)
        if gray is None:
            return None
        _skill_level_tpl = gray
    if _skill_level_tpl.shape[1] == size[0] and _skill_level_tpl.shape[0] == size[1]:
        return _skill_level_tpl
    return _cv2.resize(_skill_level_tpl, size, interpolation=_cv2.INTER_AREA)


def is_skill_window_open(doctor_hwnd) -> bool:
    """截取 HEAL_SKILL_LEVEL 标题栏区域并与模板比对，相似度达标即视为治疗等级列表已打开。"""
    region = rectangles.HEAL_SKILL_LEVEL
    gray = grab_region_gray(doctor_hwnd, region)
    size = (region["right"] - region["left"], region["bottom"] - region["top"])
    template = _get_skill_level_template(size)
    if template is None:
        return False
    score = float(_cv2.matchTemplate(gray, template, _cv2.TM_CCOEFF_NORMED).max())
    return score >= config.SKILL_LEVEL_MATCH_THRESHOLD


def _is_level_black(color) -> bool:
    """等级标记点是否为黑色（参考值 (0,0,1)，三通道均在容差内视为黑色）。"""
    if color is None:
        return False
    r, g, b = color
    return (
        r <= config.LEVEL_BLACK_TOLERANCE
        and g <= config.LEVEL_BLACK_TOLERANCE
        and b <= config.LEVEL_BLACK_TOLERANCE
    )


def detect_doctor_level(doctor_hwnd) -> int | None:
    """判断治疗等级列表是否已打开，并返回医生拥有的最大治疗等级(1~10)。

    先按 HEAL_SKILL_LEVEL 标题栏区域截图与模板比对：未匹配上则视为窗口未打开，返回 None；
    已打开后从上到下读取等级标记点，首个黑色标记位于第 k 行 -> 等级 k-1，全非黑则为 10 级。
    """
    if not is_skill_window_open(doctor_hwnd):
        return None

    black_flags = [
        _is_level_black(get_window_pixel(doctor_hwnd, rel[0], rel[1]))
        for rel in config.HEAL_LEVEL_POSITIONS
    ]

    for idx, is_black in enumerate(black_flags, start=1):
        if is_black:
            return max(1, idx - 1)
    return 10
