print('Opening Minecraft')

from worldsync import worldSync
from minecraft_launcher import  setup
import psutil
import shutil
import time
import pathlib

try:
    with open('Options.txt', 'r') as options_file:
        delay_time = int(time.read().split(':')[-1])
except:
    delay_time = 15

setup()

while 'Minecraft.Windows.exe' in (p.name() for p in psutil.process_iter()):
    print('still running')
    worldSync()
    print(' ')
    time.sleep(delay_time)

print('game closed, ending program')

for i in range(5):
    try:
        time.sleep(1)
        shutil.rmtree(str(pathlib.Path().absolute()) + '\\zipped-worlds\\')
        print('Cache ereased')
        break
    except:
        pass