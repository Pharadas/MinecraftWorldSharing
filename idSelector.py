import subprocess
import os
import pathlib
from tkinter import *
from pymsgbox import *
import json
import codecs
import time

value = True

def listbox(): # shows player relevant information from saved worlds and lets him choose his character, this saves his metadata for later use
    print('Loading worlds for metadata selection')

    user = str(subprocess.check_output('whoami' , shell=True)).split('\\')[-3]
    base_path = r'C:\Users\{}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds'.format(user)

    current_player = ''

    top = Tk()

    def player_data(thing):
        global value

        if playerMetadata_listbox.get(ACTIVE) == '======No estoy en esta lista======':
            
            value = False

            top.quit()
            top.destroy()

        elif playerMetadata_listbox.get(ACTIVE)[:14] == 'player_server_':

            newtop = Tk()

            filepath = str(pathlib.Path().absolute())

            chosen_player = str(playerMetadata_listbox.get(ACTIVE))
            chosen_player_id = str(playerMetadata_listbox.get(ACTIVE)).encode()
            chosen_player_key = chosen_player_id.hex()

            for i in worlds_dict:
                if chosen_player_key in worlds_dict[i][0]:
                    active_world = i

            def choose_player(thing):
                global value
                
                if Lb2.get(ACTIVE) == '======================Click HERE if this is YOU======================':
                    value = True
                    for i in worlds_dict[active_world][1]:
                        player_metadata = subprocess.check_output('mcpetool.exe db get --path "' + base_path + '\\' + active_world + '" ' + i + ' -json')
                        player_metadata_json = json.loads(player_metadata)

                        if player_metadata_json['nbt'][0]['value'][-1]['value'] == chosen_player:
                            player_metadata = player_metadata_json
                            
                            if len(player_metadata_json['nbt'][0]['value']) == 3:
                                if player_metadata_json['nbt'][0]['value'][0]['value'].encode().hex() == i[14:]:

                                    with open('msaid.json', 'w') as myid:
                                        myid.write(str(player_metadata).replace("'", '"'))
                                else:
                                    with open('selfasignedid.json', 'w') as myid:
                                        myid.write(str(player_metadata).replace("'", '"'))
                            else:
                                with open('selfasignedid.json', 'w') as myid:
                                    myid.write(str(player_metadata).replace("'", '"'))

                    print('saved metadata succesfully')

                    try:
                        newtop.destroy()
                        top.destroy()
                    except:
                        pass


            Lb2 = Listbox(newtop, bg='black', height=40, width=100, fg='white')

            chosen_player_data = subprocess.check_output('mcpetool.exe db get --path "' + base_path + '\\' + active_world + '" ' + chosen_player_key + ' -json')
            chosen_player_data_list = str(chosen_player_data).split(r'\n')
            chosen_player_data_dict = json.loads(chosen_player_data.decode('ascii'))

            player_info_dict = {}

            for i in range(len(chosen_player_data_dict['nbt'][0]['value'])):
                player_info_dict[chosen_player_data_dict['nbt'][0]['value'][i]['name']] = i

            Lb2.insert(0, '===ARMOR===')

            armor_pieces = ['helmet = ', 'chestplate = ', 'leggings = ', 'boots = ']

            for i in range(4):
                armor_piece = chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Armor']]['value']['list'][i][2]['value'][10:].split('_')
                if armor_piece[0] != '':
                    Lb2.insert(END, armor_pieces[i] + armor_piece[0] + ' ' + armor_piece[-1])
                else:
                    Lb2.insert(END, armor_pieces[i] + 'bare')

            Lb2.insert(END, '')
            Lb2.insert(END, '===ATTRIBUTES===')

            attributes = chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Attributes']]['value']['list']

            player_attributes_dict = {}

            for i in range(len(attributes)):
                player_attributes_dict[str(attributes[i][3]['value'])] = i

            # HEALTH
            Lb2.insert(END, 'Health = ' + str(attributes[player_attributes_dict['minecraft:health']][1]['value']) + ' / ' + str(attributes[player_attributes_dict['minecraft:health']][2]['value']))
            # HUNGER
            Lb2.insert(END, 'Hunger = ' + str(attributes[player_attributes_dict['minecraft:player.hunger']][1]['value']) + ' / ' + str(attributes[player_attributes_dict['minecraft:player.hunger']][2]['value']))
            # EXPERIENCE LEVEL
            Lb2.insert(END, 'Experience level = ' + str(attributes[player_attributes_dict['minecraft:player.level']][1]['value'] + attributes[player_attributes_dict['minecraft:player.experience']][1]['value']))
            # DEAD?
            try:
                if chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Dead']]['value'] == 0:
                    Lb2.insert(END, 'Not dead')
                else:
                    Lb2.insert(END, 'Dead')
            except:
                Lb2.insert(END, 'Not dead')

            # DIMENSION
            dimensions = ['Overworld', 'Nether', 'End']
            if chosen_player_data_dict['nbt'][0]['value'][player_info_dict["DimensionId"]]['value'] < 3:
                Lb2.insert(END, 'Dimension = ' + dimensions[chosen_player_data_dict['nbt'][0]['value'][player_info_dict["DimensionId"]]['value']])
            else:
                Lb2.insert(END, 'Dimension = ' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict["DimensionId"]]['value']))

            # GAMEMODE
            gamemodes_ids = {'1': 'Survival',
                             '2': 'Adventure',
                             '5':'Creative'}

            Lb2.insert(END, 'Gamemode = ' + gamemodes_ids[str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict["PlayerGameMode"]]['value'])])

            # EFFECTS
            Lb2.insert(END, ' ')
            Lb2.insert(END, '===EFFECTS===')
            effects = ['', 'Speed', 'Slowness', 'Haste', 'Mining Fatigue', 'Strength', 'Instant Health', 'Instant Damage', 'Jump Boost', 'Nausea', 'Regeneration', 'Resistance', 'FireResistance', 'Water Breathing', 'Invisibility', 'Blindness', 'Night Vision', 'Hunger', 'Weakness',  'Poison', 'Wither', 'HealthBoost', 'Absorption', 'Saturation', 'Glowing', 'Levitation', 'Luck', 'BadLuck']
            if 'ActiveEffects' in player_info_dict: 
                for i in chosen_player_data_dict['nbt'][0]['value'][player_info_dict['ActiveEffects']]['value']['list']:
                    Lb2.insert(END, effects[int(i[7]['value'])])
            else: 
                Lb2.insert(END, 'No effects')

            # INVENTORY
            
            Lb2.insert(END, '')
            Lb2.insert(END, '===INVENTORY===')

            for i in range(35):
                if re.search('^minecraft:', str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Inventory']]['value']['list'][i][2]['value'])) != None:
                    block_name_list = chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Inventory']]['value']['list'][i][2]['value'][10:].split('_')
                    block_name = ' '.join(block_name_list)
                    Lb2.insert(END, '-' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Inventory']]['value']['list'][i][0]['value']) + ' ' + block_name)
                elif re.search('^minecraft:', str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Inventory']]['value']['list'][i][3]['value'])) != None:
                    block_name_list = chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Inventory']]['value']['list'][i][3]['value'][10:].split('_')
                    block_name = ' '.join(block_name_list)
                    Lb2.insert(END, '-' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Inventory']]['value']['list'][i][1]['value']) + ' ' + block_name)

            Lb2.insert(END, '')
            Lb2.insert(END, '===ENDER CHEST===')

            for i in range(26):
                if re.search('^minecraft:', str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['EnderChestInventory']]['value']['list'][i][2])) != None:
                    block_name_list = chosen_player_data_dict['nbt'][0]['value'][player_info_dict['EnderChestInventory']]['value']['list'][i][2][10:].split('_')
                    block_name = ' '.join(block_name_list)
                    Lb2.insert(END, '-' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['EnderChestInventory']]['value']['list'][i][0]) + ' ' + block_name)
                elif re.search('^minecraft:', str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['EnderChestInventory']]['value']['list'][i][3]['value'])) != None:
                    block_name_list = chosen_player_data_dict['nbt'][0]['value'][player_info_dict['EnderChestInventory']]['value']['list'][i][3]['value'][10:].split('_')
                    block_name = ' '.join(block_name_list)
                    Lb2.insert(END, '-' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['EnderChestInventory']]['value']['list'][i][1]['value']) + ' ' + block_name)

            Lb2.insert(END, '')
            Lb2.insert(END, '===POSITION===')

            Lb2.insert(END, 'x = ' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Pos']]['value']['list'][0]))
            Lb2.insert(END, 'y = ' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Pos']]['value']['list'][1]))
            Lb2.insert(END, 'z = ' + str(chosen_player_data_dict['nbt'][0]['value'][player_info_dict['Pos']]['value']['list'][2]))

            Lb2.insert(END, '')
            Lb2.insert(END, '======================Click HERE if this is YOU======================')

            Lb2.bind("<Double-1>", choose_player)
            Lb2.bind("<Return>", choose_player)

            Lb2.pack()
            newtop.mainloop()

    playerMetadata_listbox = Listbox(top, bg='black', height=20, width=50, fg='white')

    worlds_list = []
    worlds_dict = {}

    for file in os.listdir(base_path):

        print('loading world ' + file)

        world_key_list = subprocess.check_output('mcpetool.exe db list --path "' + base_path + '/' + str(file) + '"', shell=True)

        world_key_list = str(world_key_list).split(r'\n')

        ids = 0

        worlds_list.append(file)
        
        remote_players_metadata_keys = []
        remote_players_data_keys = []

        for key in world_key_list:
            if key[0:14] == '706c617965725f' and len(key) > 99:
                remote_players_data_keys.append(key)
            elif key[0:14] == '706c617965725f' and len(key) < 99:
                remote_players_metadata_keys.append(key)
                ids += 1

        if ids != 0:

            with open(base_path + '/' + str(file) + '/' + 'levelname.txt', 'r') as world:
                worldname = world.readline()

            playerMetadata_listbox.insert(END, worldname)

            for i in remote_players_data_keys:
                key_bytes = codecs.decode(str(i), 'hex')
                key_string = key_bytes.decode('utf-8')
                playerMetadata_listbox.insert(END, key_string)
                
            worlds_dict[file] = [remote_players_data_keys, remote_players_metadata_keys]

            playerMetadata_listbox.insert(END, '')
            playerMetadata_listbox.insert(END, '')

    playerMetadata_listbox.insert(END, '======No estoy en esta lista======')

    playerMetadata_listbox.bind("<Double-1>", player_data)
    playerMetadata_listbox.bind("<Return>", player_data)

    playerMetadata_listbox.pack()
    top.mainloop()

    if ids != 0:
        return value
    else:
        return False