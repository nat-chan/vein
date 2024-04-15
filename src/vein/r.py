#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import coloredlogs, logging
import sys
import select
import termios
import tty
import subprocess
from pydantic import BaseModel
import rich.prompt

coloredlogs.install()
logger = logging.getLogger(__file__)
import time

from rich.live import Live
from rich.table import Table

def main():
    table = Table()
    table.add_column("PID")
    table.add_column("Option")
    table.add_column("Level")

    with Live(table, refresh_per_second=4):  # update 4 times a second to feel fluid
        for row in range(10**9):
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                input_char = sys.stdin.read(1)
                break
            time.sleep(0.1)  # arbitrary delay
            # update the renderable internally
            table.add_row(f"{row}", f"description {row}", "[red]ERROR")

        table.add_row(f"{row}", f"description {row}", input_char)

def save_screen() -> None:
    sys.stdout.write('\033[?47h')
#    sys.stdout.write('\033[?s')
    sys.stdout.flush()

def restore_screen() -> None:
    sys.stdout.write('\033[?47l')
#    sys.stdout.write('\033[?u')
    sys.stdout.flush()



class ssh_info(BaseModel):
    pid: int
    src_host: str
    dst_host: str
    src_port: int
    dst_port: int
    LR: str

# 文字列処理
def process_string(lines: list[str]) -> list[ssh_info]:
    result: list[ssh_info] = list()
    for line in lines:
        splitted = line.split()
        pid = int(splitted[0])
        LR = splitted[2][-1]
        dst_host = splitted[4]
        src_port, src_host, dst_port = splitted[3].split(":")
        result.append(ssh_info(
            pid=pid,
            LR=LR,
            dst_host=dst_host,
            src_port=int(src_port),
            dst_port=int(dst_port),
            src_host=src_host,
        ))
    return result

def pformat(ssh_info: ssh_info) -> str:
    return f"{ssh_info.pid} {ssh_info.src_host} {ssh_info.dst_host} {ssh_info.src_port}:{ssh_info.src_host}:{ssh_info.dst_port} {ssh_info.LR}"


def main2() -> str:
    save_screen()
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    print("\x1b[2J\x1b[H", end="", flush=True)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            lines: list[str] = list()
            ready, _, _ = select.select([sys.stdin], [], [], 0.4)
            result = subprocess.run(
                "pgrep -a autossh",
                stdout=subprocess.PIPE,
                shell=True,
                text=True,
            )
            lines += [
                pformat(ssh_info) for ssh_info in
                process_string(result.stdout.strip().split("\n"))
            ]
            if ready:
                char = sys.stdin.read(1)
                match char:
                    case '\x1b':
                        return char
                    case _:
                        lines.append( f"{char} pressed!" )
            lines.append("> ")
            print("\x1b[2J\x1b[H"+"\r\n".join(lines), end="", flush=True)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        restore_screen()

def main3():

    while True:
        dst_port = rich.prompt.IntPrompt.ask(
            "dst_port",
            default=8188,
        )
        if dst_port in range(65536):
            break

    while True:
        dst_host = rich.prompt.Prompt.ask(
            "dst_host",
            default="marisa",
        )
        if True:
            break

    while True:
        src_port = rich.prompt.IntPrompt.ask(
            "src_port",
            default=dst_port,
        )
        if src_port in range(65536):
            break

    while True:
        src_host = rich.prompt.Prompt.ask(
            "src_host",
            default="localhost",
        )
        if True:
            break
    cmd = f"autossh -fNL {dst_port}:{src_host}:{src_port} {dst_host}"
    result = subprocess.run(cmd, shell=True)
    assert result.returncode == 0


if __name__ == "__main__":
    main2()
    main3()
