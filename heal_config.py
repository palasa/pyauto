import os
import coodinates
from health_color import HealthColor

# ============ 默认运行配置 ============
CHECK_INTERVAL: int = 20          # 检测是否有人受伤的间隔，单位是秒
HEAL_RECHECK_DELAY: float = 1.0  # 单次治疗后等待结果/血量刷新的秒数，再复查是否治好
DOCTOR_NAME = "安侑真"
COLLECTOR_TYPE = "矿工"
# MAX：永远使用最大技能等级；AUTO：白伤1级、黄伤6级、紫红10级，等级不足时回退到最大等级
HEAL_STRATEGY = "MAX"

# 启动界面下拉可选项
DOCTOR_NAME_OPTIONS = ["安侑真", "田小娟", "医生"]
COLLECTOR_TYPE_OPTIONS = ["矿工", "伐木工", "猎人"]
# 治疗策略：内部值 -> 界面显示文本（下拉只展示中文，运行时仍按 MAX/AUTO 判断）
HEAL_STRATEGY_LABELS = {
    "MAX": "最大(烧技能)",
    "AUTO": "自动(省蓝高效)",
}
HEAL_STRATEGY_BY_LABEL = {label: value for value, label in HEAL_STRATEGY_LABELS.items()}
HEAL_STRATEGY_OPTIONS = list(HEAL_STRATEGY_LABELS.values())

# 被治疗者序号(1~5) -> 医生窗口内相对坐标
HEAL_PLAYER_POSITIONS = (
    coodinates.HEAL_FIRST_PLAYER,
    coodinates.HEAL_SECOND_PLAYER,
    coodinates.HEAL_THIRD_PLAYER,
    coodinates.HEAL_FOURTH_PLAYER,
    coodinates.HEAL_FIFTH_PLAYER,
)

# 治疗技能等级标记点（从上到下 1~10 级）
HEAL_LEVEL_POSITIONS = (
    coodinates.HEAL_LEVEL1,
    coodinates.HEAL_LEVEL2,
    coodinates.HEAL_LEVEL3,
    coodinates.HEAL_LEVEL4,
    coodinates.HEAL_LEVEL5,
    coodinates.HEAL_LEVEL6,
    coodinates.HEAL_LEVEL7,
    coodinates.HEAL_LEVEL8,
    coodinates.HEAL_LEVEL9,
    coodinates.HEAL_LEVEL10,
)

# 伤情颜色 -> 中文标签
WOUND_LABELS = {
    HealthColor.WHITE.value: "白伤",
    HealthColor.YELLOW.value: "黄伤",
    HealthColor.PURPLE.value: "紫伤",
    HealthColor.RED.value: "红伤",
}

# AUTO 策略：伤情颜色 -> 期望使用的技能等级
AUTO_LEVEL_BY_WOUND = {
    HealthColor.WHITE.value: 1,
    HealthColor.YELLOW.value: 6,
    HealthColor.PURPLE.value: 10,
    HealthColor.RED.value: 10,
}

# 各个等级的治疗耗蓝 
HEAL_MANA_COST = (
    15, 17, 20, 22, 25, 27, 30, 32, 35, 40
)

# 等级标记点黑色判定容差（参考黑色 (0,0,1)）
LEVEL_BLACK_TOLERANCE = 5

# 治疗等级列表标题栏模板路径与打开判定相似度下限（CCOEFF_NORMED，越大越相似）
SKILL_LEVEL_TPL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "images", "heal_skill_level.png"
)
SKILL_LEVEL_MATCH_THRESHOLD = 0.07


def build_collectors_names(collector_type: str) -> tuple:
    """按采集者类型生成 1~5 号采集者窗口名称。"""
    return tuple(f"{collector_type}{i}" for i in range(1, 6))
