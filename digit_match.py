"""基于模板匹配的点阵数字识别模块。

流程：截取区域灰度图 -> 二值化 -> 连通域切分（过滤汉字/斜杠/杂点）
-> 单字归一化到固定画布 -> 与 images/hp_mp_0.png ~ hp_mp_9.png 模板做 IoU 比对，
取相似度最高的数字。模板为同一套固定点阵字体的放大截图，运行时无需 OCR。
"""

import os
from typing import Any

import cv2
import mss
import numpy as np
import win32gui
from PIL import Image

# cv2 为二进制扩展，类型存根不完整，静态分析易误报；别名标注为 Any 后按实际运行处理
_cv2: Any = cv2

_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images/hp_mp_digits")
_LOC_IMG_DIR = os.path.join(os.path.dirname(_IMG_DIR), "location_digits")

# 归一化画布尺寸：所有单字块与模板都缩放到该尺寸后再比对
_CANVAS = 16

# 数字连通域过滤阈值（原始小像素下的实测范围）
_MIN_AREA = 15
_MIN_H, _MAX_H = 7, 10
_MIN_W, _MAX_W = 3, 6

# 坐标数字连通域过滤阈值（深底浅字，窄数字 1 面积偏小，阈值相应放宽）
_LOC_MIN_AREA = 8
_LOC_MIN_H, _LOC_MAX_H = 7, 10
_LOC_MIN_W, _LOC_MAX_W = 2, 6

_templates: dict[int, np.ndarray] | None = None
_loc_templates: dict[int, np.ndarray] | None = None


def _load_templates() -> dict[int, np.ndarray]:
    """读取 images 目录下 0-9 模板，去杂点、裁空白并归一化到固定画布。"""
    templates: dict[int, np.ndarray] = {}
    for digit in range(10):
        path = os.path.join(_IMG_DIR, f"hp_mp_{digit}.png")
        gray = _cv2.imread(path, _cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise FileNotFoundError(f"数字模板缺失：{path}")
        bw = (gray < 128).astype(np.uint8)

        # 只保留面积最大的连通域，去掉模板顶部的孤立杂点
        n, labels, stats, _ = _cv2.connectedComponentsWithStats(bw, 8)
        if n > 1:
            big = 1 + int(np.argmax(stats[1:, _cv2.CC_STAT_AREA]))
            bw = (labels == big).astype(np.uint8)

        ys, xs = np.where(bw > 0)
        crop = bw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        templates[digit] = _normalize(crop)
    return templates


def _get_templates() -> dict[int, np.ndarray]:
    """惰性加载并缓存模板。"""
    global _templates
    if _templates is None:
        _templates = _load_templates()
    return _templates


def _load_loc_templates() -> dict[int, np.ndarray]:
    """读取 location_digits 目录下 0-9 坐标模板（深底浅字，取亮前景），去杂点、裁空白并归一化。"""
    templates: dict[int, np.ndarray] = {}
    for digit in range(10):
        path = os.path.join(_LOC_IMG_DIR, f"{digit}.png")
        gray = _cv2.imread(path, _cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise FileNotFoundError(f"坐标数字模板缺失：{path}")
        bw = (gray > 128).astype(np.uint8)

        # 只保留面积最大的连通域，去掉模板上的孤立杂点
        n, labels, stats, _ = _cv2.connectedComponentsWithStats(bw, 8)
        if n > 1:
            big = 1 + int(np.argmax(stats[1:, _cv2.CC_STAT_AREA]))
            bw = (labels == big).astype(np.uint8)

        ys, xs = np.where(bw > 0)
        crop = bw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        templates[digit] = _normalize(crop)
    return templates


def _get_loc_templates() -> dict[int, np.ndarray]:
    """惰性加载并缓存坐标模板。"""
    global _loc_templates
    if _loc_templates is None:
        _loc_templates = _load_loc_templates()
    return _loc_templates


def _normalize(block: np.ndarray) -> np.ndarray:
    """把单字二值块缩放到固定画布并重新二值化。"""
    norm = _cv2.resize(block, (_CANVAS, _CANVAS), interpolation=_cv2.INTER_AREA)
    return (norm > 0.5).astype(np.uint8)


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个二值矩阵的交并比（IoU），取值 0~1，越大越相似。"""
    inter = int(np.logical_and(a, b).sum())
    union = int(np.logical_or(a, b).sum())
    return inter / union if union else 0.0


def match_digit(block: np.ndarray) -> tuple[int, float]:
    """对单个数字块做模板匹配，返回 (最匹配数字, IoU 分数)。"""
    norm = _normalize(block)
    best_digit, best_score = -1, -1.0
    for digit, tpl in _get_templates().items():
        score = _iou(norm, tpl)
        if score > best_score:
            best_digit, best_score = digit, score
    return best_digit, best_score


def recognize_gray(gray: np.ndarray) -> int:
    """对灰度区域图切分连通块并逐位识别，拼接为整数；识别不到数字时返回 0。"""
    bw = (gray < 128).astype(np.uint8)
    n, labels, stats, _ = _cv2.connectedComponentsWithStats(bw, 8)

    blocks: list[tuple[int, np.ndarray]] = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if _MIN_H <= h <= _MAX_H and _MIN_W <= w <= _MAX_W and area >= _MIN_AREA:
            crop = (labels[y:y + h, x:x + w] == i).astype(np.uint8)
            blocks.append((int(x), crop))

    blocks.sort(key=lambda item: item[0])
    digits = [str(match_digit(crop)[0]) for _, crop in blocks]
    return int("".join(digits)) if digits else 0


def match_location_digit(block: np.ndarray) -> tuple[int, float]:
    """对单个坐标数字块做坐标模板匹配，返回 (最匹配数字, IoU 分数)。"""
    norm = _normalize(block)
    best_digit, best_score = -1, -1.0
    for digit, tpl in _get_loc_templates().items():
        score = _iou(norm, tpl)
        if score > best_score:
            best_digit, best_score = digit, score
    return best_digit, best_score


def recognize_location(gray: np.ndarray) -> int:
    """对坐标灰度区域（深底浅字）切分连通块并逐位识别，拼接为整数；识别不到数字时返回 0。"""
    bw = (gray > 128).astype(np.uint8)
    n, labels, stats, _ = _cv2.connectedComponentsWithStats(bw, 8)

    blocks: list[tuple[int, np.ndarray]] = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if _LOC_MIN_H <= h <= _LOC_MAX_H and _LOC_MIN_W <= w <= _LOC_MAX_W and area >= _LOC_MIN_AREA:
            crop = (labels[y:y + h, x:x + w] == i).astype(np.uint8)
            blocks.append((int(x), crop))

    blocks.sort(key=lambda item: item[0])
    digits = [str(match_location_digit(crop)[0]) for _, crop in blocks]
    return int("".join(digits)) if digits else 0


def grab_region_gray(hwnd, region) -> np.ndarray:
    """截取窗口相对区域，返回原始尺寸的灰度 numpy 数组（不放大）。"""
    left, top, _, _ = win32gui.GetWindowRect(hwnd)
    abs_x = left + region["left"]
    abs_y = top + region["top"]
    width = region["right"] - region["left"]
    height = region["bottom"] - region["top"]

    with mss.MSS() as sct:
        sct_img = sct.grab({"top": abs_y, "left": abs_x, "width": width, "height": height})
    arr = np.array(sct_img)[:, :, :3][..., ::-1]  # BGRA -> RGB
    return np.array(Image.fromarray(arr).convert("L"))
