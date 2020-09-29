from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pydrive as drive
import subprocess
from datetime import datetime
from io import BytesIO
from dateutil.tz import *
import plyer.platforms.win.notification
from plyer import notification
import os
import pathlib
from worldClass import localMinecraftWorld, cloudMinecraftWorld
import math

print('Getting credentials \n ')

# =====AUTH=====
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
gauth.LocalWebserverAuth()

print('Gathering folder...')

minecraft_shared_worlds_folder = drive.ListFile({'q': "title = 'Minecraft shared worlds' and trashed=false"}).GetList()

try:
    id_parent_overhead = minecraft_shared_worlds_folder[0]['id']
except:
    id_parent_overhead = minecraft_shared_worlds_folder['id']

print('Getting timezone offset...')

offset = (datetime.now(tzutc()).replace(tzinfo=None) - datetime.now()).total_seconds()

print('Getting worlds info...')

worlds_path = r'C:\Users\{}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds'.format(str(subprocess.check_output('whoami' , shell=True)).split('\\')[-3])

def worldSync():
    minecraft_worlds = drive.ListFile({'q': "'%s' in parents and trashed=false" % id_parent_overhead}).GetList()

    for current_cloud_world in minecraft_worlds:
        cloud_world = cloudMinecraftWorld(current_cloud_world, id_parent_overhead, offset)
        print(f'Syncing {cloud_world.name}')

        if cloud_world.name in os.listdir(worlds_path):
            local_world = localMinecraftWorld(cloud_world.name)
            
            if local_world.state:
                # local newer than cloud
                if math.floor(local_world.date) > math.floor(cloud_world.unix_date):
                    print(f'Updating {local_world.title} in cloud')

                    local_world.localToCloudSetup()
                    local_world.updateWorldZip(drive, cloud_world.id, id_parent_overhead)

                    minecraft_worlds_1 = drive.ListFile({'q': "'%s' in parents and trashed=false" % id_parent_overhead}).GetList()
                    world_modification_time = [i['modifiedDate'] for i in minecraft_worlds_1 if i['id'] == cloud_world.id][0][:-1].split('T')

                    year_month_day = world_modification_time[0].split('-')
                    hour_minute_second = world_modification_time[-1].split(':')
                    milisecond = hour_minute_second[-1].split('.')
                    date_formated = [year_month_day, hour_minute_second[:2], milisecond]

                    timestamp = datetime(int(date_formated[0][0]), int(date_formated[0][1]), int(date_formated[0][2]), int(date_formated[1][0]), int(date_formated[1][1]), int(date_formated[2][0]), int(date_formated[2][1])).timestamp() - offset
                    os.utime(local_world.path, (timestamp, timestamp))
                    
                # cloud newer than local
                elif math.floor(cloud_world.unix_date) > math.floor(local_world.date):
                    print(f'Updating "{local_world.title}" in pc')
                    cloud_world.downloadAndUnzipWorld()
                    local_world.cloudToLocalSetup(cloud_world.date)
                
                elif math.floor(cloud_world.unix_date) == math.floor(local_world.date):
                    print(f'{local_world.title} up to date')

            else:
                print(f'{cloud_world.name} in use')

        # cloud world not in pc
        else:
            print(f'downloading {cloud_world.name}')
            cloud_world.downloadAndUnzipWorld()

            downloaded_world = localMinecraftWorld(cloud_world.name)
            downloaded_world.cloudToLocalSetup(cloud_world.date)
        
