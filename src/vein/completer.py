#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.history import FileHistory
from pygments.lexers.python import PythonLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()

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

class PortValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and (
            not text.isdigit() or
            not int(text) in range(65536)
        ):
            raise ValidationError(message='validation error')

@bindings.add('c-c')
def _(event):
    event.app.exit()
class Completer:
    def __init__(self, name: str):
        if "host" in name:
            self.candidate = ["localhost"] + list_ssh_hosts()
            self.validator = None
        elif "port" in name:
            self.candidate = ["7860", "8188", "22", "10022", "80", "443"]
            self.validator = PortValidator()
        else:
            self.candidate = []
            self.validator = None
        self.name = name
        history_dir = Path.home()/".local/share/vein/history"
        history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = history_dir / f"{self.name.replace(' ', '_')}"
        self.history = FileHistory(self.history_file)

    def __call__(self, default: str | None = None) -> str:
        if default is None:
            text = f"{self.name}: "
        else:
            text = f"{self.name} ({default}): "
        user_input = prompt(
            text,
            completer=FuzzyWordCompleter(self.candidate),
            lexer=PygmentsLexer(PythonLexer),
            history=self.history,
            validator=self.validator,
            key_bindings=bindings,
        )
        if user_input == "" and default is not None:
            user_input = default
        return user_input

if __name__ == "__main__":
    user_input = Completer("src port")("8188")
    print(user_input)

