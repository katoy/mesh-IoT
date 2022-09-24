import requests
import urllib
from urllib.request import urlopen
import json
import os
import platform
import sys

# IFTTT を呼び出す
def ifttt_webhook(name, desc):
    payload = {"value1": name, "value2": "", "value3": desc }
    url = "" # EDIT
    if len(url) == 0:
        print("#----- IFTTT の webhook が未設定です")
    else:
        response = requests.post(url, data=payload)

# コンソールに通知を出す(for Mac)
def notify(name, desc):
    if platform.system() == 'Darwin':
        os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(desc, name))
    ifttt_webhook(name, desc)

message = ''
if len(sys.argv) > 1:
    message = sys.argv[1]
notify("notify", message)
