
import subprocess
import time

def execute_command(cmd_string, cwd=None, shell=True):
    sub = subprocess.Popen(cmd_string, cwd=cwd, stdin=subprocess.PIPE,stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, shell=shell, bufsize=4096)

    stdout_str = ''
    while sub.poll() is None:
        err= sub.stderr.read()
        stdout_str += str(sub.stdout.read(), encoding="UTF-8")
        if len(err)>0:
            raise Exception(err)
        time.sleep(0.1)

    return stdout_str








