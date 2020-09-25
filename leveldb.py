print('Yeah, im runnin, what about it?')

import os
import ctypes
import pywintypes
import pythoncom
import winerror
import subprocess
import time
import psutil
from worldsync import worldSync
import pathlib
import shutil

try:
    import winreg
except ImportError:
    # Python 2
    import _winreg as winreg
    bytes = lambda x: str(buffer(x))

from ctypes import wintypes
from win32com.shell import shell, shellcon
from win32com.propsys import propsys, pscon

# KNOWNFOLDERID
# https://msdn.microsoft.com/en-us/library/dd378457
# win32com defines most of these, except the ones added in Windows 8.
FOLDERID_AppsFolder = pywintypes.IID('{1e87508d-89c2-42f0-8a7e-645a0f50ca58}')

# win32com is missing SHGetKnownFolderIDList, so use ctypes.

_ole32 = ctypes.OleDLL('ole32')
_shell32 = ctypes.OleDLL('shell32')

_REFKNOWNFOLDERID = ctypes.c_char_p
_PPITEMIDLIST = ctypes.POINTER(ctypes.c_void_p)

_ole32.CoTaskMemFree.restype = None
_ole32.CoTaskMemFree.argtypes = (wintypes.LPVOID,)

_shell32.SHGetKnownFolderIDList.argtypes = (
    _REFKNOWNFOLDERID, # rfid
    wintypes.DWORD,    # dwFlags
    wintypes.HANDLE,   # hToken
    _PPITEMIDLIST)     # ppidl

def get_known_folder_id_list(folder_id, htoken=None):
    if isinstance(folder_id, pywintypes.IIDType):
        folder_id = bytes(folder_id)
    pidl = ctypes.c_void_p()
    try:
        _shell32.SHGetKnownFolderIDList(folder_id, 0, htoken,
            ctypes.byref(pidl))
        return shell.AddressAsPIDL(pidl.value)
    except WindowsError as e:
        if e.winerror & 0x80070000 == 0x80070000:
            # It's a WinAPI error, so re-raise it, letting Python
            # raise a specific exception such as FileNotFoundError.
            raise ctypes.WinError(e.winerror & 0x0000FFFF)
        raise
    finally:
        if pidl:
            _ole32.CoTaskMemFree(pidl)

def enum_known_folder(folder_id, htoken=None):
    id_list = get_known_folder_id_list(folder_id, htoken)
    folder_shell_item = shell.SHCreateShellItem(None, None, id_list)
    items_enum = folder_shell_item.BindToHandler(None,
        shell.BHID_EnumItems, shell.IID_IEnumShellItems)
    for item in items_enum:
        yield item

def list_known_folder(folder_id, htoken=None):
    result = []
    for item in enum_known_folder(folder_id, htoken):
        result.append(item.GetDisplayName(shellcon.SIGDN_NORMALDISPLAY))
    result.sort(key=lambda x: x.upper())
    return result

def create_shortcut(shell_item, shortcut_path):
    id_list = shell.SHGetIDListFromObject(shell_item)
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None,
        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    shortcut.SetIDList(id_list)
    persist = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
    persist.Save(shortcut_path, 0)

def get_package_families():
    families = set()
    subkey = (r'Software\Classes\Local Settings\Software\Microsoft'
              r'\Windows\CurrentVersion\AppModel\Repository\Families')
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as hkey:
        index = 0
        while True:
            try:
                families.add(winreg.EnumKey(hkey, index))
            except OSError as e:
                if e.winerror != winerror.ERROR_NO_MORE_ITEMS:
                    raise
                break
            index += 1
    return families

def update_app_shortcuts(target_dir):
    package_families = get_package_families()
    for item in enum_known_folder(FOLDERID_AppsFolder):
        try:
            property_store = item.BindToHandler(None,
                shell.BHID_PropertyStore, propsys.IID_IPropertyStore)
            app_user_model_id = property_store.GetValue(
                pscon.PKEY_AppUserModel_ID).ToString()
        except pywintypes.error:
            continue
        # AUID template: Packagefamily!ApplicationID
        if '!' not in app_user_model_id:
            continue
        package_family, app_id = app_user_model_id.rsplit('!', 1)
        if package_family not in package_families:
            continue
        name = item.GetDisplayName(shellcon.SIGDN_NORMALDISPLAY)
        shortcut_path = os.path.join(target_dir, '%s.lnk' % name)
        create_shortcut(item, shortcut_path)

desktop = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0)
target_dir = os.path.join(desktop, 'Windows Store Apps')
if not os.path.exists(target_dir):
    os.mkdir(target_dir)
    update_app_shortcuts(target_dir)

os.startfile(target_dir + r'\Minecraft.lnk')

time.sleep(5)

while 'Minecraft.Windows.exe' in (p.name() for p in psutil.process_iter()):
    print('still running')
    worldSync()
    time.sleep(10)
    print(' ')
print('game closed, ending program')

for i in range(5):
    try:
        time.sleep(1)
        shutil.rmtree(str(pathlib.Path().absolute()) + '\\zipped-worlds\\')
        print('Cache ereased')
        break
    except:
        pass