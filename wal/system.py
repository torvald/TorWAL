from utils import cmd_output


class SystemInterface:
    def active_window(self) -> str:
        pass

    def idle_sec(self) -> int:
        pass


# Choose your implementation in the config.py


class LinuxX(SystemInterface):
    def active_window(self) -> str:
        envs = {"DISPLAY": ":0"}
        active_window_id = cmd_output(
            "xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2", envs
        ).strip()
        active_window = cmd_output(f"xprop -id {active_window_id} _NET_WM_NAME")
        active_window = active_window.replace('_NET_WM_NAME(UTF8_STRING) = "', "")
        active_window = active_window.strip()[:-1]
        return active_window

    def idle_sec(self) -> int:
        idle_ms = cmd_output("/usr/bin/xprintidle").strip()
        idle_sec = round(int(idle_ms) / 1000)
        return idle_sec


class MacOS(SystemInterface):
    pass
