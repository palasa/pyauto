import schedule
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

import coodinates
import heal_config as config
from doctor_level import detect_doctor_level
from get_hp_mp_coordinate import read_hp_mp
from health_color import HealthColor
from log_utils import log
from mouse_controller import MouseGuard
from toast_notifier import ToastNotifier
from window_utils import (
    activate_window,
    find_first_window,
    get_window_pixel,
    get_window_rect,
    to_absolute,
)

# 0. 自动对进行挖矿/伐木/狩猎的采集人员进行治疗的脚本
# 1. 按照12345的顺序打开采集者窗口,每位采集人员打开组队，5个采集者需要站在同一个点，并且该点不能有其他人
# 2. 请将采集人员的窗口平铺，不要遮挡到窗口左上角的健康和标识健康状态的那个点，要根据那个点的颜色读取健康状态
# 3. 打开医生窗口,医生站在离采集者1格的位置，并且面对采集者
# 4. 打开医生的技能窗口并点击治疗技能,进入选择治疗等级列表页
# 5. 检测到有人受伤会弹窗提示，此时请停止鼠标操作，把鼠标交给脚本处理，等显示治疗结果页面(成功或失败)后，才可以再次使用鼠标

# ============ 运行配置（默认值取自 heal_config，可由启动界面回填） ============
check_interval: int = config.CHECK_INTERVAL        # 检测是否有人受伤的间隔，单位是秒
heal_recheck_delay: float = config.HEAL_RECHECK_DELAY  # 单次治疗后等待结果/血量刷新的秒数，再复查是否治好
doctor_name = config.DOCTOR_NAME
collector_type = config.COLLECTOR_TYPE
heal_strategy = config.HEAL_STRATEGY

collectors_names = config.build_collectors_names(collector_type)

notifier = ToastNotifier()
mouse = MouseGuard()


def pause_job(job):
    """暂停定时任务：把下次运行时间推到远期，治疗期间不会被调度。"""
    job.next_run = datetime.max


def resume_job(job):
    """恢复定时任务：从当前时刻起重新计算下一次运行时间。"""
    job.next_run = datetime.now() + timedelta(seconds=check_interval)


def collect_health_colors(windows):
    """依次读取各采集者窗口血量区域的颜色，返回颜色列表。"""
    rel_x, rel_y = coodinates.HEALTH_COLOR
    return [get_window_pixel(hwnd, rel_x, rel_y) for hwnd in windows]


def read_health_color(hwnd):
    """读取单个采集者窗口血量区域的颜色。"""
    rel_x, rel_y = coodinates.HEALTH_COLOR
    return get_window_pixel(hwnd, rel_x, rel_y)


def is_healthy(color):
    """判断血量颜色是否为健康（绿色）。"""
    return color == HealthColor.GREEN.value


def choose_skill_level(wound_color, doctor_level: int) -> int:
    """根据治疗策略与伤情选择本次使用的技能等级。

    MAX：永远使用医生最大等级；AUTO：白伤1级、黄伤6级、紫红伤10级，
    医生等级不足时回退到其拥有的最大等级。
    """
    if heal_strategy == "MAX":
        return doctor_level
    target = config.AUTO_LEVEL_BY_WOUND.get(wound_color, doctor_level)
    return min(target, doctor_level)


def _check_mp_available(doctor_hwnd, skill_level) -> bool:
    """治疗前校验医生蓝量是否足够释放该等级技能。

    蓝量不足时记录日志、弹窗提示并停止脚本；返回 True 表示可以继续本次治疗。
    """
    _, _, current_mp, _ = read_hp_mp(doctor_hwnd)
    cost = config.HEAL_MANA_COST[skill_level - 1]
    if current_mp >= cost:
        return True

    log(f"魔法不足：当前 {current_mp} 点，{skill_level} 级治疗技能需 {cost} 点，停止脚本", color="red")
    messagebox.showerror(
        "魔法不足",
        f"当前魔法 {current_mp} 点，{skill_level} 级治疗技能需要 {cost} 点魔法，蓝量不足。\n"
        "请补充魔法后重新执行脚本。",
    )
    _stop_script()
    return False


def scan_wounded(health_colors):
    """遍历血量颜色，将伤员信息合并为一条通知推送，并返回 [(序号, 颜色), ...]。"""
    wounded = []
    wound_descriptions = []
    for i, color in enumerate(health_colors):
        label = config.WOUND_LABELS.get(color)
        if label is not None:
            wound_descriptions.append(f"{collector_type}{i + 1}{label}")
        if color != HealthColor.GREEN.value:
            wounded.append((i + 1, color))
    if wound_descriptions:
        notifier.info("受伤", "、".join(wound_descriptions), "veryshort")
    return wounded


def heal_target(doctor_hwnd, collector_index, skill_level):
    """在医生窗口内完成对指定序号采集者的整套治疗点击流程。"""
    rect = get_window_rect(doctor_hwnd)

    # 点击自己脚下，获取窗口
    mouse.click(rect[0] + 320, rect[1] + 266)

    # 点击选定等级的治疗技能
    x, y = to_absolute(rect, config.HEAL_LEVEL_POSITIONS[skill_level - 1])
    mouse.click(x, y)

    # 鼠标移动到窗口中间，滚轮向下滚动，显示：采集者1/2/3/4/5
    mouse.scroll(rect[0] + 320, rect[1] + 240, -100)

    # 选中需要治疗的采集者（第一个伤员）
    x, y = to_absolute(rect, config.HEAL_PLAYER_POSITIONS[collector_index - 1])
    log(f"正在治疗{collector_type}{collector_index}", color="green")
    mouse.click(x, y)

    # 点击受伤人员名字进行治疗
    x, y = to_absolute(rect, coodinates.WOUND_PLAYER_HIMSELF)
    mouse.click(x, y)


def heal_until_cured(doctor_hwnd, collector_index, collector_hwnd):
    """反复治疗指定伤员，直到血条变绿为止。

    :param doctor_hwnd: 医生窗口句柄
    :param collector_index: 伤员序号(1~5)
    :param collector_hwnd: 伤员窗口句柄，用于治疗后复查血条颜色
    """
    global heal_attempts, heal_successes
    level = doctor_level
    if level is None:
        return
    attempt = 0
    while not _stop_event.is_set():
        attempt += 1
        wound_color = read_health_color(collector_hwnd)
        skill_level = choose_skill_level(wound_color, level)
        if not _check_mp_available(doctor_hwnd, skill_level):
            return
        heal_target(doctor_hwnd, collector_index, skill_level)
        heal_attempts += 1

        # 等待治疗结果与血量刷新，再复查该伤员窗口
        time.sleep(heal_recheck_delay)
        color = read_health_color(collector_hwnd)

        if is_healthy(color):
            heal_successes += 1
            log(f"{collector_type}{collector_index}已治好（第{attempt}次治疗，{skill_level}级技能）", color="green")
            return

        label = config.WOUND_LABELS.get(color, "未知伤情")
        log(f"{collector_type}{collector_index}尚未治好（{label}），第{attempt}次治疗未成功，继续治疗", color="green")


def task():
    """轮流查看矿工窗口，查看是否有人受伤，若有人受伤则激活医生窗口，使用技能治疗。"""

    if _stop_event.is_set():
        return

    # 获取当前5位采集者的受伤信息
    health_colors = collect_health_colors(collectors_windows)

    # 记录每位伤员信息
    wounded = scan_wounded(health_colors)

    if len(wounded) == 0:     # 无受伤人员，退出等待下一轮检查
        log("全员状况良好,等待下一轮检查")
        return

    try:
        pause_job(heal_job)     # 治疗期间暂停定时计时，避免重试耗时影响下一轮
        mouse.lock()            # 治疗开始：锁定鼠标，防止用户误碰拖动
        activate_window(doctor_window)
        time.sleep(1)
        # 逐个处理伤员：每人反复治疗直到血条变绿
        for index, _ in wounded:
            if _stop_event.is_set():
                break
            collector_hwnd = collectors_windows[index - 1]
            heal_until_cured(doctor_window, index, collector_hwnd)
        log("本轮治疗完毕，等待下一轮循环判断", color="green")
    finally:
        mouse.unlock()          # 无论成功还是报错，都解锁鼠标
        if heal_job is not None:
            resume_job(heal_job)    # 治疗结束，从当前时刻重新开始倒计时


# 运行期窗口句柄、定时任务与后台线程状态，由启动界面按钮触发后赋值
doctor_window = None
collectors_windows = ()
heal_job = None
doctor_level: int | None = 10  # 检测到的医生最大治疗等级(1~10)，未检测到时为 None
_running = False
_stop_event = threading.Event()
_worker_thread = None

# 运行时长与治疗统计
_start_time = None            # 本次运行起点时间戳（time.time()）
_frozen_elapsed = 0.0         # 停止时冻结的已运行秒数
heal_attempts = 0             # 治疗尝试（扎针）次数
heal_successes = 0           # 成功治好的伤员数


def _read_positive_number(entry, field_name):
    """从输入框读取正整数，失败时弹出提示并返回 None。 """
    raw = entry.get().strip()
    try:
        value = float(raw)
    except ValueError:
        messagebox.showerror("输入错误", f"{field_name} 必须是数字：{raw or '（为空）'}")
        return None
    if value <= 0:
        messagebox.showerror("输入错误", f"{field_name} 必须大于 0")
        return None
    return int(value)


def _format_duration(seconds):
    """把秒数格式化为 X小时X分X秒。"""
    seconds = int(max(0, seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}小时{minutes}分{secs}秒"


def _run_schedule_loop():
    """后台线程：启动后先立即检查一次，之后按间隔持续调度，直到收到停止信号。"""
    if not _stop_event.is_set():
        task()
    while not _stop_event.is_set():
        schedule.run_pending()
        time.sleep(1)


def _stop_script():
    """停止定时任务与后台调度线程。"""
    global heal_job, _running, _worker_thread
    global _start_time, _frozen_elapsed
    if _start_time is not None:
        _frozen_elapsed = time.time() - _start_time
        _start_time = None
    _stop_event.set()
    schedule.clear()
    heal_job = None
    _running = False
    _worker_thread = None


def _on_toggle(btn, interval_entry, doctor_combo,
               collector_combo, strategy_combo):
    """开始/停止按钮回调：未运行则校验并启动后台调度；运行中则停止。"""
    global check_interval
    global doctor_name, collector_type, heal_strategy, collectors_names
    global doctor_window, collectors_windows
    global heal_job, _running, _worker_thread, doctor_level
    global _start_time, _frozen_elapsed, heal_attempts, heal_successes

    # 当前运行中：点击即停止
    if _running:
        _stop_script()
        btn.config(text="开始执行")
        return

    interval = _read_positive_number(interval_entry, "检查间隔(秒)", )
    if interval is None:
        return

    doctor = doctor_combo.get().strip()
    collector = collector_combo.get().strip()
    strategy = config.HEAL_STRATEGY_BY_LABEL.get(strategy_combo.get().strip())
    if not doctor or not collector or strategy is None:
        messagebox.showerror("输入错误", "医生名称、采集者类型、治疗策略不能为空")
        return

    # 回填配置
    check_interval = interval
    doctor_name = doctor
    collector_type = collector
    heal_strategy = strategy
    collectors_names = config.build_collectors_names(collector)

    # 检查医生窗口与五个采集者窗口是否都存在
    doctor_window = find_first_window(doctor_name)
    collectors_windows = tuple(find_first_window(name) for name in collectors_names)

    missing = []
    if doctor_window is None:
        missing.append(doctor_name)
    missing.extend(name for name, hwnd in zip(collectors_names, collectors_windows) if hwnd is None)

    if missing:
        messagebox.showerror("窗口未找到", "以下窗口未检测到，请确认游戏窗口已打开：\n" + "\n".join(missing))
        doctor_window = None
        collectors_windows = ()
        return

    # 检测医生当前最大治疗等级
    activate_window(doctor_window)
    time.sleep(1)
    doctor_level = detect_doctor_level(doctor_window)
    if doctor_level is None:
        messagebox.showerror(
            "治疗窗口未打开",
            "未检测到医生的治疗等级列表，请先打开治疗技能并进入等级选择窗口后再执行。",
        )
        doctor_window = None
        collectors_windows = ()
        return
    strategy_name = "自动" if heal_strategy == "AUTO" else "最大"
    white_lv = choose_skill_level(HealthColor.WHITE.value, doctor_level)
    yellow_lv = choose_skill_level(HealthColor.YELLOW.value, doctor_level)
    purple_lv = choose_skill_level(HealthColor.PURPLE.value, doctor_level)
    red_lv = choose_skill_level(HealthColor.RED.value, doctor_level)
    log(
        f"检测到医生最大治疗等级为{doctor_level}级，当前策略为{strategy_name}。"
        f"目前使用的治疗策略为：白{white_lv}级，黄{yellow_lv}级，紫{purple_lv}级，红{red_lv}级",
        color="green",
    )

    # 启动后台调度线程，界面保持显示，按钮切换为“停止”
    _stop_event.clear()
    schedule.clear()
    heal_job = schedule.every(check_interval).seconds.do(task)
    heal_attempts = 0
    heal_successes = 0
    _frozen_elapsed = 0.0
    _start_time = time.time()
    _worker_thread = threading.Thread(target=_run_schedule_loop, daemon=True)
    _worker_thread.start()
    _running = True
    btn.config(text="停止")


def launch_ui():
    """弹出启动配置界面，点击“开始执行”并通过窗口检查后返回。"""
    root = tk.Tk()
    root.title("自动治疗配置")
    root.resizable(False, False)

    form = ttk.Frame(root, padding=16)
    form.grid(sticky="nsew")

    ttk.Label(form, text="检查间隔(秒)：").grid(row=0, column=0, sticky="w", pady=6)
    interval_entry = ttk.Entry(form, width=20)
    interval_entry.insert(0, str(check_interval))
    interval_entry.grid(row=0, column=1, pady=6)

    ttk.Label(form, text="医生名称：").grid(row=1, column=0, sticky="w", pady=6)
    doctor_combo = ttk.Combobox(form, width=18, values=config.DOCTOR_NAME_OPTIONS, state="readonly")
    doctor_combo.set(doctor_name)
    doctor_combo.grid(row=1, column=1, pady=6)

    ttk.Label(form, text="采集者类型：").grid(row=2, column=0, sticky="w", pady=6)
    collector_combo = ttk.Combobox(form, width=18, values=config.COLLECTOR_TYPE_OPTIONS, state="readonly")
    collector_combo.set(collector_type)
    collector_combo.grid(row=2, column=1, pady=6)

    ttk.Label(form, text="治疗策略：").grid(row=3, column=0, sticky="w", pady=6)
    strategy_combo = ttk.Combobox(form, width=18, values=config.HEAL_STRATEGY_OPTIONS, state="readonly")
    strategy_combo.set(config.HEAL_STRATEGY_LABELS[heal_strategy])
    strategy_combo.grid(row=3, column=1, pady=6)

    run_label = ttk.Label(form, text="已运行 0小时0分0秒")
    run_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=6)

    stat_label = ttk.Label(form, text="已治疗 0 次，成功率 0.0%")
    stat_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=6)

    def _refresh_stats():
        if _running and _start_time is not None:
            elapsed = time.time() - _start_time
        else:
            elapsed = _frozen_elapsed
        run_label.config(text=f"已运行 {_format_duration(elapsed)}")
        pct = (heal_successes / heal_attempts * 100) if heal_attempts else 0.0
        stat_label.config(text=f"已治疗 {heal_attempts} 次，成功率 {pct:.1f}%")
        # 后台线程因缺蓝等原因停止后，主线程轮询把按钮复位为“开始执行”
        if not _running and start_btn.cget("text") == "停止":
            start_btn.config(text="开始执行")
        root.after(1000, _refresh_stats)

    start_btn = ttk.Button(
        form,
        text="开始执行",
        command=lambda: _on_toggle(
            start_btn, interval_entry, doctor_combo, collector_combo, strategy_combo
        ),
    )
    start_btn.grid(row=6, column=0, columnspan=2, pady=(12, 0), sticky="ew")

    _refresh_stats()

    # 关闭窗口时先停止后台调度线程，再销毁界面
    root.protocol("WM_DELETE_WINDOW", lambda: (_stop_script(), root.destroy()))

    root.mainloop()


if __name__ == "__main__":
    launch_ui()
