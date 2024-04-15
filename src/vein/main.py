#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import coloredlogs, logging
coloredlogs.install()
logger = logging.getLogger(__file__)
import pytermgui as ptg

CONFIG = """
config:
    InputField:
        styles:
            prompt: dim italic
            cursor: '@72'
    Label:
        styles:
            value: dim bold

    Window:
        styles:
            border: '60'
            corner: '60'

    Container:
        styles:
            border: '96'
            corner: '96'
"""

def submit(*args, **kwargs):
    print(*args, **kwargs)

with ptg.YamlLoader() as loader:
    loader.load(CONFIG)

with ptg.WindowManager() as manager:
    window = (
        ptg.Window(
            "",
            ptg.InputField("7860", prompt="port: "),
            ptg.InputField("marisa", prompt="src host: "),
            ptg.InputField("127.0.0.1", prompt="dst host: "),
            ptg.InputField("L", prompt="L/R: "),
            "",
            ["Submit", lambda *_: submit(manager, window)],
            width=60,
            box="DOUBLE",
        )
        .set_title("[210 bold]New connection")
        .center()
    )

    manager.add(window)