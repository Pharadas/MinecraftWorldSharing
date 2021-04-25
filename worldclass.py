from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pydrive as drive
from apiclient import errors
from apiclient import http
import os
import subprocess
import pathlib
import json
from idSelector import listbox
import random
from zipfile import ZipFile
import zipfile
from datetime import datetime
from dateutil.tz import *
import time
import json
import math
import shutil
import plyer.platforms.win.notification
from plyer import notification
import io

class localMinecraftWorld:
    def __init__(self, name):
        self.name = name
        self.path = r'C:\Users\{}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds'.format(str(subprocess.check_output('whoami', shell=True)).split('\\')[-3]) + '\\' + self.name
        self.script_path = str(pathlib.Path().absolute())
        self.offset = (datetime.now(tzutc()).replace(tzinfo=None) - datetime.now()).total_seconds()

        FNULL = open(os.devnull, 'w')
        retcode = subprocess.call(r'mcpetool.exe leveldat get --path "' + self.path + '"', stdout=FNULL, stderr=subprocess.STDOUT)
        FNULL.close()

        if retcode != 0:
            self.state = False
            print('exit status', retcode)

        else:
            self.state = True

            time.sleep(5)

            self.date = os.path.getmtime(self.path)
            self.player_in_world = False

            with open(self.path + '\\' + 'levelname.txt', 'r') as world_name_title:
                self.title = world_name_title.read()

            self.leveldat = json.loads(subprocess.check_output('mcpetool.exe leveldat get --path "' + self.path + '"', shell=True))
            self.world_spawn_list = [i['value'] for i in self.leveldat['nbt'][0]['value'] if i['name'] == 'SpawnX' or i['name'] == 'SpawnY' or i['name'] == 'SpawnZ']
            self.world_gamemode = [i['value'] for i in self.leveldat['nbt'][0]['value'] if i['name'] == 'GameType'][0]

    def verifyPlayerMetadata(self):
        if os.path.isfile('selfasignedid.json'):
            with open('selfasignedid.json', 'r') as f:
                try:
                    self.player_metadata = json.loads(f.read())
                except:
                    print('didnt work')
                    if listbox():
                        self.player_metadata = json.loads(f.read())
                    else:
                        self.player_metadata = False
        elif listbox():
            print('file doesnt exist')
            with open('selfasignedid.json', 'r') as f:
                self.player_metadata = json.loads(f.read())
        else:
            self.player_metadata = False
        
        if os.path.isfile('selfasignedid.json') and os.path.isfile('msaid.json'):
            self.full_id = True
            self.msaid = 'player_' + str(self.player_metadata['nbt'][0]['value'][0]['value'])
            self.selfasignedid = 'player_' + str(self.player_metadata['nbt'][0]['value'][1]['value'])
            self.player_key = str(self.player_metadata['nbt'][0]['value'][-1]['value'])
 
        elif self.player_metadata:
            self.full_id = False
            self.msaid = 'player_'
            self.selfasignedid = 'player_' + str(self.player_metadata['nbt'][0]['value'][0]['value'])
            self.player_key = str(self.player_metadata['nbt'][0]['value'][-1]['value'])
 
        time.sleep(3)

        return self.player_metadata

    def randomPlayerKey(self):
        possible_key = '123456789abcdefghijklmnopqrstuvwxyz' 

        key_part_1 = [possible_key[random.randrange(35)] for i in range(8)]
        key_part_2 = [possible_key[random.randrange(35)] for i in range(4)]
        key_part_3 = [possible_key[random.randrange(35)] for i in range(4)]
        key_part_4 = [possible_key[random.randrange(35)] for i in range(4)]
        key_part_5 = [possible_key[random.randrange(35)] for i in range(12)]
        
        result = f'player_server_{"".join(key_part_1)}-{"".join(key_part_2)}-{"".join(key_part_3)}-{"".join(key_part_4)}-{"".join(key_part_5)}'

        return result

    def verifyPlayerExistance(self):
        world_keys_list = str(subprocess.check_output(f'mcpetool.exe db list --path "{self.path}"', shell=True)).split('\\n')
        
        with open('selfasignedid.json', 'r') as player_metadata:
            msaid_json = json.load(player_metadata)
            if len(msaid_json['nbt'][0]['value']) == 3:
                my_msaid = 'player_' + str(msaid_json['nbt'][0]['value'][0]['value'])
                my_selfasignedid = 'player_' + str(msaid_json['nbt'][0]['value'][1]['value'])
                print('player logged in')

            else:
                my_msaid = 'player_'
                my_selfasignedid = 'player_' + str(msaid_json['nbt'][0]['value'][0]['value'])
                print('player not logged in / parcial metadata')

        print(my_msaid.encode().hex())
        print(my_selfasignedid.encode().hex())

        if my_msaid.encode().hex() in world_keys_list or my_selfasignedid.encode().hex() in world_keys_list:
            print("instance of player's metadata in world")
            self.player_in_world = True
            return True

        else:
            print("no instance of player's metadata in this world")
            return False
    
    def addNewLocalPlayer(self):
        self.world_pos = [i['value'] for i in json.loads(subprocess.getoutput('mcpetool.exe leveldat get --path "' + self.path + '"'))['nbt'][0]['value'] if i['name'] == 'SpawnX' or i['name'] == 'SpawnY' or i['name'] == 'SpawnZ']
        self.world_gamemode = [i['value'] for i in json.loads(subprocess.getoutput('mcpetool.exe leveldat get --path "' + self.path + '"'))['nbt'][0]['value'] if i['name'] == 'GameType'][0]

        with open('data_for_local_player.json', 'r') as localplayer_cache_read:
            json_localplayer_cache = json.load(localplayer_cache_read)

            json_localplayer_cache['nbt'][0]['value'][[json_localplayer_cache['nbt'][0]['value'].index(i) for i in json_localplayer_cache['nbt'][0]['value'] if i['name'] == 'Pos'][0]]['value']['list'] = self.world_pos
            json_localplayer_cache['nbt'][0]['value'][[json_localplayer_cache['nbt'][0]['value'].index(i) for i in json_localplayer_cache['nbt'][0]['value'] if i['name'] == 'PlayerGameMode'][0]]['value'] = self.world_gamemode

            json_localplayer_cache = str(json_localplayer_cache).replace('None', 'null')

        with open('data_for_local_player.json', 'w') as write_local_player_modified:
            write_local_player_modified.write(json_localplayer_cache.replace("'", '"'))

        subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i data_for_local_player.json --json 7e6c6f63616c5f706c61796572')

        print('added new local player')

    def moveLocalPlayerToNewRemotePlayer(self): # Fix=== (u dum arse)
        subprocess.run('mcpetool.exe db get --path "' + self.path + '" --json 7e6c6f63616c5f706c61796572 > ' + self.script_path + '\\local_player.json', shell=True)

        if self.full_id:
            subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i ' + self.script_path + '\\msaid.json --json ' + self.msaid.encode().hex(), shell=True)
            subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i ' + self.script_path + '\\selfasignedid.json --json ' + self.selfasignedid.encode().hex(), shell=True)
        else:
            subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i ' + self.script_path + '\\msaid.json --json ' + self.selfasignedid.encode().hex(), shell=True)

        subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i ' + self.script_path + '\\local_player.json --json ' + self.player_key.encode().hex(), shell=True)
        print(self.player_key, self.player_key.encode().hex())

        print(self.verifyPlayerExistance())

    def moveLocalPlayerToExistingRemotePlayer(self):
        print('saving local player data')
        subprocess.run(f'mcpetool.exe db get --path "{self.path}" --json 7e6c6f63616c5f706c61796572 > local_player.json', shell=True)
        
        print('gettin local player')
        subprocess.run('mcpetool.exe db get --path "' + self.path + '" --json ' + '7e6c6f63616c5f706c61796572' + ' > ' + self.script_path + '\\local_player.json', shell=True)

        if self.full_id:
            print('getting msaid, normal:', self.msaid, 'hex:', self.msaid.encode().hex())
            idsJson = json.loads(subprocess.check_output(f'mcpetool.exe db get --path "{self.path}" --json {self.msaid.encode().hex()}'))
        else:
            print('getting selfasignedid, normal:', self.selfasignedid, 'hex:', self.selfasignedid.encode().hex())
            idsJson = json.loads(subprocess.check_output(f'mcpetool.exe db get --path "{self.path}" --json {self.selfasignedid.encode().hex()}'))
        
        playerdata_key = idsJson['nbt'][0]['value'][-1]['value']

        time.sleep(2)
        print('getting player data, normal:', playerdata_key, 'hex:', playerdata_key.encode().hex())
        subprocess.run(f'mcpetool.exe db put --path "{self.path}" -i local_player.json --json {playerdata_key.encode().hex()}')

    def moveRemotePlayerToLocalPlayer(self): # fix===============
        hex_metadata_key_msaid = self.msaid.encode().hex()
        hex_metadata_key_selfasignedid = self.selfasignedid.encode().hex()

        print(hex_metadata_key_msaid, hex_metadata_key_selfasignedid)
        print(self.path)

        if self.full_id:
            remote_player_metadata1 = subprocess.getoutput('mcpetool.exe db get --path "' + self.path + '" --json ' + hex_metadata_key_msaid)
            remote_player_metadata2 = subprocess.getoutput('mcpetool.exe db get --path "' + self.path + '" --json ' + hex_metadata_key_selfasignedid)
            print(remote_player_metadata1)
            print(remote_player_metadata2)
            player_data_key = json.loads(remote_player_metadata1)['nbt'][0]['value'][-1]['value'] if json.loads(remote_player_metadata1)['nbt'][0]['value'][-1]['value'] != '' else json.loads(remote_player_metadata2)['nbt'][0]['value'][-1]['value']

        else:
<<<<<<< HEAD
            remote_player_metadata2 = subprocess.getoutput('mcpetool.exe db get --path "' + self.path + '" --json ' + hex_metadata_key_selfasignedid)
            player_data_key = json.loads(remote_player_metadata2)['nbt'][0]['value'][-1]['value']

        print(player_data_key, player_data_key.encode().hex())
        print('done1')
        remote_player_data = subprocess.getoutput('mcpetool.exe db get --path "' + self.path + '" --json ' + player_data_key.encode().hex() + ' > ' + self.script_path + r'\remote_player.json')
        print('done2')
        subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i remote_player.json --json 7e6c6f63616c5f706c61796572', shell=True)
        print('done 3, revelations')
=======
            remote_player_metadata = subprocess.getoutput('mcpetool.exe db get --path "' + self.path + '" --json ' + hex_metadata_key_selfasignedid)
            player_data_key = json.loads(remote_player_metadata)['nbt'][0]['value'][-1]['value']

        print(player_data_key, player_data_key.encode().hex())
        remote_player_data = subprocess.getoutput('mcpetool.exe db get --path "' + self.path + '" --json ' + player_data_key.encode().hex() + ' > ' + self.script_path + '\\remote_player.json')
        print('works')
        subprocess.run('mcpetool.exe db put --path "' + self.path + '" -i ' + self.script_path + '\\remote_player.json --json 7e6c6f63616c5f706c61796572', shell=True)

>>>>>>> 0247a299da3bf133256eceed1fcbb65cca1171bf
        print('moved remote player to local player')

    def localToCloudSetup(self):
        shutil.make_archive('zipped-worlds\\' + self.name, 'zip', self.path)

        if self.verifyPlayerMetadata():
            print('player metadata exists')
            if self.verifyPlayerExistance():
                print('player in world')
                self.moveLocalPlayerToExistingRemotePlayer()
                print('moved local player data to existing remote player data')
            else:
                print('player not in world')
                self.moveLocalPlayerToNewRemotePlayer()
                print('moved local player data to new remote player data')
        
        notification.notify('Minecraft Shared Worlds', 'Updated "' + self.title + '" in cloud', timeout=5)

    def cloudToLocalSetup(self, cloud_date):
        cloud_date = cloud_date.split('T')
        year_month_day = cloud_date[0].split('-')
        hour_minute_second = cloud_date[-1].split(':')
        milisecond = hour_minute_second[-1].split('.')
        date_separated = [year_month_day, hour_minute_second[:2], milisecond]
        
        timestamp = datetime(int(date_separated[0][0]), int(date_separated[0][1]), int(date_separated[0][2]), int(date_separated[1][0]), int(date_separated[1][1]), int(date_separated[2][0]), int(date_separated[2][1])).timestamp() - self.offset
        os.utime(self.path, (timestamp, timestamp))

        print('metadata:', self.verifyPlayerMetadata())
        print('player:',  self.verifyPlayerExistance())

        if self.verifyPlayerMetadata() and self.verifyPlayerExistance():
            print('player metadata existing and player in world')
            print(self.moveRemotePlayerToLocalPlayer())
            print('moved remote player to local player')
        else:
            self.addNewLocalPlayer()
            print('added new local player')

        notification.notify('Minecraft Shared Worlds', 'Updated "' + self.title + '" in pc', timeout=5)

    def updateWorldZip(self, drive, id, parent_id):
        world = drive.CreateFile({'id': id, 'title': self.name + '.zip', 'parents': [{'id': parent_id}]})
        world.SetContentFile('zipped-worlds\\' + self.name + '.zip')
        world.Upload()
        print('succesfully uploaded ' + self.title)
    
    def uploadWorldZip(self, drive, parent_id):
        world = drive.CreateFile({'title': self.name + '.zip', 'parents': [{'id': parent_id}], 'modifiedDate': 'T'.join(str(time.strftime(r'%Y-%m-%d %H:%M:%S', time.localtime(self.date + self.offset)) + 'Z').split(' '))})
        print(self.script_path + '\\zipped-worlds\\' + self.name + '.zip')
        world.SetContentFile('zipped-worlds\\' + self.name + '.zip')
        world.Upload()

class cloudMinecraftWorld:
    def __init__(self, cloud_world_object, parent_id, offset):
        self.cloud_object = cloud_world_object
        self.script_path = str(pathlib.Path().absolute())
        self.date = cloud_world_object['modifiedDate'][:-1]
        self.unix_date = time.mktime(time.strptime(' '.join(self.date.split('T')), r'%Y-%m-%d %H:%M:%S.%f')) - offset
        self.name = cloud_world_object['title'][:-4]
        self.path = r'C:\Users\{}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds'.format(str(subprocess.check_output('whoami', shell=True)).split('\\')[-3])
        self.id = cloud_world_object['id']
        self.parent_id = parent_id

    def downloadAndUnzipWorld(self):
        toUnzipBytesContent = io.BytesIO(self.cloud_object.GetContentString(encoding='cp862').encode('cp862'))

        time.sleep(2)

        readZipfile = zipfile.ZipFile(toUnzipBytesContent, "r")
        readZipfile.extractall(self.path + '\\' + self.name)
        readZipfile.close()
        print('world extracted to ' + self.path + '\\' + self.name)

        time.sleep(2)
