# sample file for CodeQL pack tests
# we want to catch uses of eval and subprocess.run(shell=True)

import subprocess


def dangerous_eval(user_input):
    return eval(user_input)


def run_shell(cmd):
    subprocess.run(cmd, shell=True)
