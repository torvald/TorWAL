from typing import Tuple
from utils import cmd_output


class SystemInterface:
    def active_window(self) -> Tuple[str, str]:
        pass

    def idle_sec(self) -> int:
        pass

    def current_ssid(self) -> str:
        pass

# Choose your implementation in the config.py


class LinuxX(SystemInterface):
    envs = {"DISPLAY": ":0"}

    def active_window(self) -> Tuple[str, str]:
        active_window_id = cmd_output(
            "xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2", envs=self.envs
        ).strip()
        active_window = cmd_output(
            f"xprop -id {active_window_id} _NET_WM_NAME", envs=self.envs
        )
        active_window = active_window.replace("_NET_WM_NAME(UTF8_STRING) = ", "")
        active_window = active_window.strip('\t\n "')

        active_application = cmd_output(
            f"xprop -id {active_window_id} WM_CLASS", envs=self.envs
        )

        active_application = active_application.replace("WM_CLASS(STRING) = ", "")
        active_application = active_application.split(",")[-1].strip('\t\n "')
        return active_window, active_application

    def idle_sec(self) -> int:
        idle_ms = cmd_output("/usr/bin/xprintidle", envs=self.envs).strip()
        idle_sec = round(int(idle_ms) / 1000)
        return idle_sec

    def current_ssid(self) -> str:
        ssid = cmd_output("/usr/sbin/iwconfig | grep ESSID: | cut -d':' -f2 | tail -n 1").strip()
        ssid = ssid.replace('"', '')
        return ssid
        


class MacOS(SystemInterface):
    pass
