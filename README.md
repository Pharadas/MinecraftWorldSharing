# MinecraftWorldSharing
This tool tries to allow players to share worlds with other people through Google Drive,
it modifies the world in such a way that it remembers player's data and changes the worlds
accordingly.

The tool has 3 executables, the 'Id Selector' script which shows relevant information from every remote
player who has joined a world they currently have in their
%USERPROFILE%\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds
folder, it asks the player to identify one of these players and choose it so that the program can save
that player's metadata, and remember it for any time the player wants to share a world.

The second executable is the 'World Uploading' script, which modifies a chosen world (using the player's
saved metadata (if there's none, it will prompt 'Id Selector')) and saves it to any folder named 
'Minecraft Shared Worlds' in the player's Google Drive. The modification required is as follows:

- If the player has ever joined remotely to that world, it will save the local player's data
  to that id, and replace the local player with the default information for a new player
  (Considering the world's gamemode, spawnpoint, etc...)

- If the player has never joined remotely, it will create a random id, save the local player's data
  to that id, and replace the local player with the default information explained before.
  
The third executable is the 'Main.py' script, which runs in the background, it deals the comparison,
upload and download of the worlds in the 'Minecraft Shared Worlds folder'

- It compares the existance of all the worlds in the folder, against the local worlds folder.
- Modifies the worlds in order to correctly upload them or download them correctly.

The way it modifies the worlds is the following:

- If one of the player's worlds is newer than it's version in the Google Drive folder, and it
  has an instance of his id in the world (has joined remotely before), it will move the local 
  player's data to that id and leave the local player with the default information, and then
  upload the world.
  
- If one of the player's worlds is newer than it's version in the Google Drive folder, and it 
  doesnt have an instance of his id in the world, it will move the local player's data to a random
  id and then upload the world.
  
- If one of the player's worlds is older than it's version in the Google Drive folder, it will download
  it, and if it has and id that is recognized (by the saved id), it will take that id's data and move
  it to the local player.
  
- If one of the player's worlds is older than it's version in the Google Drive folder, it will download
  it, and if no id is recognized, it will be left as it is.
  
- If the world is not in the player's local folder it will download it, and if it recognizes an id, it
  will take that id's data and move it to the local player.

- If the world is not in the player's local folder it will download it, and if it doesnt recognize any ids, 
  it will be left as it is.
  
- The program won't do anything if both the local and cloud worlds are equally old.
