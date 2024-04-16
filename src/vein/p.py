#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.history import FileHistory
from pathlib import Path


# 単語の候補
my_completer = FuzzyWordCompleter(
    ["apple", "goole", "japan", "hoge", "hello world", "good morning"]
)

class Completer:
    def __init__(self, name: str):
        self.name = name
        history_dir = Path.home()/".local/share/vein/history"
        history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = history_dir / f"{self.name.replace(' ', '_')}"
        self.history = FileHistory(self.history_file)

    def __call__(self) -> str:
        user_input = prompt(
            f"{self.name} > ",
            completer=my_completer,
            history=self.history)
        return user_input

while 1:
    user_input = Completer("src port")()
    print(user_input)

