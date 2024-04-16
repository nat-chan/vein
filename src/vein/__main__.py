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
from os import kill
from signal import SIGTERM

coloredlogs.install()
logger = logging.getLogger(__file__)

import rich
from rich.style import Style
from rich.align import Align
from rich.console import Group
from rich.text import Text
from rich_interactive.interactive_table import InteractiveTable as Table
from rich_interactive.interactive_panel import InteractivePanel as Panel
from rich_interactive.interactive_layout import InteractiveLayout as Layout

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
    def kill(self):
        kill(self.pid, SIGTERM)

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

def process_creator():
    try:
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
    finally:
        return ' '


def process_selecter() -> str:
    result = subprocess.run(
        "pgrep -a autossh",
        stdout=subprocess.PIPE,
        shell=True,
        text=True,
    )
    ssh_infos = process_string([line for line in result.stdout.strip().split("\n") if line])
    table = Table(
        title="autossh process",
        selected_row_style=Style(bgcolor="cyan"),
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
        sys.stdout.write('\033[?s')
        for i in itertools.count():
            out = io.StringIO()
            console = rich.console.Console(force_terminal=True, file=out)

            if 0 < i:
                ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                if not ready: continue
                char = sys.stdin.read(1)
                match char:
                    case '\x03' | '\x1b' | 'q':
                        return "q"
                    case 'x':
                        ssh_infos[table.selected_row].kill()
                        return 'x'
                    case 'c':
                        return 'c'
                    case 'j':
                        table.move_selection_down()
                    case 'k':
                        table.move_selection_up()
                    case _:
                        console.print(f"{char.__repr__()} pressed")
            
            # render
            _desc = {
                "j/k": "move selection",
                "x": "kill process",
                "c": "create tunnel",
                "q": "quit",
            }
            desc = sum([[(f"{k} ", "bold magenta"), f"{v} "] for k, v in _desc.items()], [])

            console.print(
                Align.center(
                    Group(
                        table,
                        Text.assemble(
                            *desc,
                            justify="center"
                        )
                    ),
                )
            )
            print("\033[2J\033[H", end="", flush=True)
            print(
                out.getvalue().replace("\n", "\r\n"),
                end="",
                flush=True
            )

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    state = ' '
    while state != 'q':
        if state == 'c':
            state = process_creator()
        else:
            state = process_selecter()
