# -*- coding-utf-8 -*-

from urllib import parse, request
import sys
from lingr import Lingr


def notify(events):
    import subprocess

    for event in events:
        print(event.keys())
        print(event.get('message', 0))
        #subprocess.call(['notify-send', event['message']['text']])
