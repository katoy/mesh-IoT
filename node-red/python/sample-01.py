# See
#  https://github.com/namgk/node-red-contrib-pythonshell

import sys
import datetime

print("Got arguments: ", sys.argv)

# タイムスタンプ  → datetime
dt = datetime.datetime.fromtimestamp(int(sys.argv[1]) / 1000)
# datetime  → 文字列型
s = dt.strftime("%Y-%m-%d %H:%M:%S")
print("日時: ", s)