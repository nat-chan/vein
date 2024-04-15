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
import io
import itertools

coloredlogs.install()
logger = logging.getLogger(__file__)
import time

from rich.live import Live
from rich.table import Table
import rich
from rich.style import Style
from rich_interactive.interactive_table import InteractiveTable as Table

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

def main4():
    result = subprocess.run(
        "pgrep -a autossh",
        stdout=subprocess.PIPE,
        shell=True,
        text=True,
    )
    ssh_infos = process_string([line for line in result.stdout.strip().split("\n") if line])
    table = Table(
        selected_row_style=Style(bgcolor="red"),
    )
    table.add_column("pid")
    table.add_column("dst host")
    table.add_column("dst port")
    table.add_column("src host")
    table.add_column("src port")
    table.add_column("LR")
    for ssh_info in ssh_infos:
        table.add_row(
            f"{ssh_info.pid}",
            f"{ssh_info.dst_host}",
            f"{ssh_info.dst_port}",
            f"{ssh_info.src_host}",
            f"{ssh_info.src_port}",
            f"{ssh_info.LR}",
        )

    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        for i in itertools.count():
            if 0 < i:
                ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                if not ready: continue
                char = sys.stdin.read(1)
                match char:
                    case '\x1b':
                        break
                    case '\n':
                        break
                    case 'j':
                        table.move_selection_down()
                    case 'k':
                        table.move_selection_up()
                    case _:
                        pass
            
            # render
            out = io.StringIO()
            console = rich.console.Console(force_terminal=True, file=out)
            console.print(table)
            print(out.getvalue().replace("\n", "\r\n"), end="", flush=True)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main4()
