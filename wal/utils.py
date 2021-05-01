import os
import subprocess


def system_cmd(cmd, envs=None):

    os_env = os.environ.copy()
    if envs:
        for key, value in envs.items():
            os_env[key] = value

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
        env=os_env,
    )

    std_out, std_err = proc.communicate()

    return proc.returncode, std_out, std_err


def cmd_exitcode(cmd, envs=None):
    exit_code, _, _ = system_cmd(cmd, envs)
    return exit_code


def cmd_output(cmd, envs=None):
    _, output, _ = system_cmd(cmd, envs)
    return output
