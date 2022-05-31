import os
import subprocess


def system_cmd(cmd, envs=None):
    proc = subprocess.run(
        cmd,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **(envs or {})},
    )
    return proc.returncode, proc.stdout, proc.stderr


def cmd_exitcode(cmd, envs=None):
    exit_code, _, _ = system_cmd(cmd, envs)
    return exit_code


def cmd_output(cmd, envs=None):
    _, output, _ = system_cmd(cmd, envs)
    return output


def histogram_bar(value, max_value):
    height = value / max_value
    delta = 1 / 7.0

    if height <= delta:
        return "▁"
    if height <= delta * 2:
        return "▂"
    if height <= delta * 3:
        return "▃"
    if height <= delta * 4:
        return "▄"
    if height <= delta * 5:
        return "▅"
    if height <= delta * 6:
        return "▆"
    if height > delta * 6:
        return "▇"
