print('loading...')

from tkinter import *
import subprocess
import os
import pathlib
import json
from zipfile import ZipFile
import zipfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pydrive as drive
from datetime import datetime
import time
import shutil
from pkg_resources import get_distribution
from googleapiclient import discovery
from worldClass import localMinecraftWorld

print('Getting credentials \n ')

# =====AUTH=====
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
gauth.LocalWebserverAuth()

user = str(subprocess.check_output('whoami' , shell=True)).split('\\')[-3]
base_path = r'C:\Users\{}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds'.format(user)

worlds_upload = Tk()
playerMetadata_listbox = Listbox(worlds_upload, bg='black', height=20, width=50, fg='white')

print('Gathering folder...')

minecraft_shared_worlds_folder = drive.ListFile({'q': "title = 'Minecraft shared worlds'"}).GetList()
try:
    id_parent_overhead = minecraft_shared_worlds_folder[0]['id']
except:
    id_parent_overhead = minecraft_shared_worlds_folder['id']

print('Getting worlds info...')
minecraft_worlds = drive.ListFile({'q': "'%s' in parents" % id_parent_overhead}).GetList()
cloud_worlds = [i['title'][:-4] for i in minecraft_worlds]

def uploadWorld(cs):
    selected_world = playerMetadata_listbox.curselection()
    world = localMinecraftWorld(worldsnamesdict[str(playerMetadata_listbox.get(ACTIVE))])
    world.localToCloudSetup()

    world.uploadWorldZip(drive, id_parent_overhead)

    print(f'{world.title} uploaded correctly')
    
    playerMetadata_listbox.delete(selected_world)

worldsnamesdict = {}

print(os.listdir(base_path))
print(cloud_worlds)

for local_world in os.listdir(base_path):
    if local_world not in cloud_worlds:
        with open(base_path + '\\' + local_world + '\\levelname.txt', 'r') as worldNameFile:
            worldName = worldNameFile.read()
        worldsnamesdict[worldName] = local_world
        playerMetadata_listbox.insert(END, worldName)

playerMetadata_listbox.bind("<Double-1>", uploadWorld)
playerMetadata_listbox.pack()
worlds_upload.mainloop()