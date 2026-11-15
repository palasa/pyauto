import threading
import time
from datetime import datetime, timedelta, timezone

from win11toast import toast, notify, update_progress
from winrt.windows.data.xml.dom import XmlDocument
from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification


# veryshort 档通知的自动过期秒数
_VERY_SHORT_SECONDS = 2
_DEFAULT_APP_ID = "Python"


class ToastNotifier:
    """win11toast 通知封装类"""
    def __init__(self):
        self.progress_tag = "heal_progress"  # 进度标识，用于更新进度通知

    @staticmethod
    def _get_time_prefix() -> str:
        """获取当前时间字符串，方便日志"""
        return datetime.now().strftime("[%H:%M:%S]")

    def _show_veryshort(self, title: str, message: str) -> None:
        """发送 2 秒后横幅自动收起的静默通知。

        底层 toast duration 仅支持 short/long 两档，无法直接指定秒数，
        这里构造通知并在 2 秒后调用 notifier.hide 收起横幅，同时设置
        expiration_time 让其从通知中心过期移除。
        """
        xml = (
            '<toast activationType="protocol" launch="http:" scenario="default" duration="short">'
            '<visual><binding template="ToastGeneric"></binding></visual>'
            '<audio silent="true"/></toast>'
        )
        document = XmlDocument()
        document.load_xml(xml)
        binding = document.select_single_node("//binding")

        title_node = document.create_element("text")
        title_node.inner_text = title
        binding.append_child(title_node)

        body_node = document.create_element("text")
        body_node.inner_text = message
        binding.append_child(body_node)

        notification = ToastNotification(document)
        notification.tag = f"veryshort-{id(notification)}"
        notification.expiration_time = datetime.now(timezone.utc) + timedelta(seconds=_VERY_SHORT_SECONDS)

        try:
            notifier = ToastNotificationManager.create_toast_notifier()
        except Exception:
            notifier = ToastNotificationManager.create_toast_notifier_with_id(_DEFAULT_APP_ID)
        notifier.show(notification)

        def _hide_after_delay() -> None:
            time.sleep(_VERY_SHORT_SECONDS)
            try:
                notifier.hide(notification)
            except Exception:
                pass

        threading.Thread(target=_hide_after_delay, daemon=True).start()

    def info(self, title: str, message: str, duration: str = "short") -> None:
        """普通信息通知，无音效。

        duration 取值："short" / "long" 走系统时长档；"veryshort" 2 秒后自动过期。
        """
        try:
            if duration == "veryshort":
                self._show_veryshort(title, message)
            else:
                toast(
                    title,
                    message,
                    duration=duration,
                    audio={"silent": True}
                )
            print(f"\033[92m[{self._get_time_prefix()}] [通知-INFO] {title} | {message}\033[0m")
        except Exception as e:
            print(f"\033[93m[{self._get_time_prefix()}] [通知失败] {e}\033[0m")

    def warn(self, title: str, message: str, duration: str = "long") -> None:
        """警告通知，提醒音效，时长更长"""
        try:
            toast(
                title,
                message,
                duration=duration
            )
            print(f"\033[91m[{self._get_time_prefix()}] [通知-WARN] {title} | {message}\033[0m")
        except Exception as e:
            print(f"\033[93m[{self._get_time_prefix()}] [通知失败] {e}\033[0m")

    def with_image(self, title: str, message: str, img_path: str, duration: str = "short") -> None:
        """带图片的通知（本地图片/网络图片）"""
        try:
            toast(
                title,
                message,
                image_src=img_path,
                duration=duration
            )
            print(f"\033[96m[{self._get_time_prefix()}] [通知-IMAGE] {title} | {message}\033[0m")
        except Exception as e:
            print(f"\033[93m[{self._get_time_prefix()}] [通知失败] {e}\033[0m")

    def start_progress(self, title: str, status: str = "正在处理") -> None:
        """初始化进度条通知"""
        try:
            notify(
                progress={
                    "title": title,
                    "status": status,
                    "value": 0.0,
                    "valueStringOverride": "0/100"
                },
                tag=self.progress_tag
            )
        except Exception as e:
            print(f"\033[93m[{self._get_time_prefix()}] [进度通知失败] {e}\033[0m")

    def update_progress(self, percent: float, text: str = "") -> None:
        """
        更新进度
        :param percent: 0.0 ~ 1.0
        :param text: 自定义显示文字，如 "50/100"
        """
        try:
            if percent >= 1.0:
                status = "✅ 完成"
            else:
                status = "进行中"
            update_progress(
                {
                    "value": percent,
                    "status": status,
                    "valueStringOverride": text if text else f"{int(percent*100)}%"
                },
                tag=self.progress_tag
            )
        except Exception as e:
            print(f"\033[93m[{self._get_time_prefix()}] [更新进度失败] {e}\033[0m")
