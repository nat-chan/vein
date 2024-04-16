#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.history import FileHistory
from pathlib import Path

from paramiko import SSHConfig
from pathlib import Path

def list_ssh_hosts() -> list[str]:
    ssh_config_file = Path.home() / ".ssh/config"
    assert ssh_config_file.exists()
    ssh_config = SSHConfig()
    with ssh_config_file.open() as f:
        ssh_config.parse(f)
    hosts = [host.get("host") for host in ssh_config._config if "host" in host]
    flatten = sum(hosts, [])
    flatten = [host for host in flatten if "*" not in host]
    return flatten

class Completer:
    def __init__(self, name: str):
        if "host" in name:
            self.candidate = list_ssh_hosts()
        elif "port" in name:
            self.candidate = ["7860", "7861", "7862", "7863", "8188", "22", "10022", "80", "443"]
        else:
            self.candidate = []
        self.name = name
        history_dir = Path.home()/".local/share/vein/history"
        history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = history_dir / f"{self.name.replace(' ', '_')}"
        self.history = FileHistory(self.history_file)

    def __call__(self) -> str:
        user_input = prompt(
            f"{self.name} > ",
            completer=FuzzyWordCompleter(self.candidate),
            history=self.history)
        return user_input

if __name__ == "__main__":
    while True:
        user_input = Completer("src host")()
        print(user_input)

