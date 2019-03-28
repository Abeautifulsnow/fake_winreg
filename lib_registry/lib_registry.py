from typing import Any, List
from winreg import *


def get_number_of_subkeys(key):
    # type: (HKEYType) -> int
    """
    param key : one of the winreg HKEY_* constants :
                HKEY_CLASSES_ROOT, HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, HKEY_DYN_DATA,
                HKEY_LOCAL_MACHINE, HKEY_PERFORMANCE_DATA, HKEY_USERS

    >>> result = get_number_of_subkeys(HKEY_USERS)
    >>> result > 1
    True

    """
    number_of_subkeys, number_of_values, last_modified_win_timestamp = QueryInfoKey(key)
    return number_of_subkeys


def get_ls_user_sids():
    # type: () -> List[str]
    """
    >>> get_ls_user_sids()  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ['.DEFAULT', 'S-1-5-18', 'S-1-5-19', 'S-1-5-20', ...]

    """
    ls_user_sids = []
    n_sub_keys = get_number_of_subkeys(key=HKEY_USERS)
    for i in range(n_sub_keys):
        subkey = EnumKey(HKEY_USERS, i)
        ls_user_sids.append(subkey)
    return sorted(ls_user_sids)


def get_username_from_sid(sid):
    # type: (str) -> str
    """
    >>> get_username_from_sid(sid='S-1-5-20')
    'NetworkService'
    """
    reg = get_registry_connection('HKEY_LOCAL_MACHINE')
    key = OpenKey(reg, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{}'.format(sid))
    # value types see https://docs.python.org/3.4/library/winreg.html#value-types
    val, value_type = QueryValueEx(key, 'ProfileImagePath')
    username = val.rsplit('\\', 1)[1]
    return username


def get_value(key_name, subkey_name):
    # type: (str, str) -> Any
    """
    >>> ### key and subkey exist
    >>> sid = 'S-1-5-20'
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_value(key, 'ProfileImagePath')
    '%systemroot%\\\\ServiceProfiles\\\\NetworkService'

    >>> ### key does not exist
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft_XXX\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_value(key, 'ProfileImagePath')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    FileNotFoundError: ...

    >>> ### subkey does not exist
    >>> sid = 'S-1-5-20'
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_value(key, 'does_not_exist')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    FileNotFoundError: ...

    """
    reg = get_registry_connection(key_name)
    key_without_hive = get_key_name_without_hive(key_name)
    key = OpenKey(reg, key_without_hive)
    val_type = QueryValueEx(key, subkey_name)
    result = val_type[0]
    return result


def get_registry_connection(key_name):
    # type: (str) -> HKEYType
    """
    >>> get_registry_connection('HKCR')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> get_registry_connection('HKCC')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> get_registry_connection('HKCU')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> get_registry_connection('HKDD')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> get_registry_connection('HKLM')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> get_registry_connection('HKPD')  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> get_registry_connection('HKU')   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>

    >>> sid='S-1-5-20'
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_registry_connection(key)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_registry_connection(key)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>
    >>> key = 'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows NT/CurrentVersion/ProfileList/{}'.format(sid)
    >>> get_registry_connection(key)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    <PyHKEY object at ...>

    """
    key_name = key_name.strip('/')
    key_name = key_name.strip('\\')
    reg = None
    if key_name.startswith('HKEY_CLASSES_ROOT') or key_name.startswith('HKCR'):
        reg = ConnectRegistry(None, HKEY_CLASSES_ROOT)
    elif key_name.startswith('HKEY_CURRENT_CONFIG') or key_name.startswith('HKCC'):
        reg = ConnectRegistry(None, HKEY_CURRENT_CONFIG)
    elif key_name.startswith('HKEY_CURRENT_USER') or key_name.startswith('HKCU'):
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
    elif key_name.startswith('HKEY_DYN_DATA') or key_name.startswith('HKDD'):
        reg = ConnectRegistry(None, HKEY_DYN_DATA)
    elif key_name.startswith('HKEY_LOCAL_MACHINE') or key_name.startswith('HKLM'):
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    elif key_name.startswith('HKEY_PERFORMANCE_DATA') or key_name.startswith('HKPD'):
        reg = ConnectRegistry(None, HKEY_PERFORMANCE_DATA)
    elif key_name.startswith('HKEY_USERS') or key_name.startswith('HKU'):
        reg = ConnectRegistry(None, HKEY_USERS)
    return reg


def get_key_name_without_hive(key_name):
    # type: (str) -> str
    """
    >>> sid='S-1-5-20'
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_key_name_without_hive(key)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    'SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\ProfileList\\\\S-1-5-20'
    >>> key = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid)
    >>> get_key_name_without_hive(key)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    'SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\ProfileList\\\\S-1-5-20'
    >>> key = 'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows NT/CurrentVersion/ProfileList/{}'.format(sid)
    >>> get_key_name_without_hive(key)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    'SOFTWARE/Microsoft/Windows NT/CurrentVersion/ProfileList/S-1-5-20'
    """

    l_hive_names = ['HKEY_LOCAL_MACHINE', 'HKLM', 'HKEY_CURRENT_USER', 'HKCU'
                    'HKEY_CLASSES_ROOT', 'HKCR', 'HKEY_CURRENT_CONFIG', 'HKCC',
                    'HKEY_DYN_DATA', 'HKDD', 'HKEY_USERS', 'HKU',
                    'HKEY_PERFORMANCE_DATA', 'HKPD']
    result = key_name
    for hive_name in l_hive_names:
        if key_name.startswith(hive_name):
            result = remove_prefix_including_first_slash_or_backslash(key_name)
            break
    return result


def key_exist(key_name):
    # type: (str) -> bool
    """
    >>> sid='S-1-5-20'
    >>> key_exist('HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\{}'.format(sid))
    True
    >>> key_exist('HKEY_LOCAL_MACHINE\\Software\\Wine')
    False

    """
    reg = get_registry_connection(key_name)
    key_without_hive = get_key_name_without_hive(key_name)
    try:
        OpenKey(reg, key_without_hive)
        return True
    except (FileNotFoundError, Exception):
        return False


def remove_prefix_including_first_slash_or_backslash(input_str):
    # type: (str) -> str
    """
    >>> remove_prefix_including_first_slash_or_backslash('test')
    'test'
    >>> remove_prefix_including_first_slash_or_backslash('test/')
    ''
    >>> remove_prefix_including_first_slash_or_backslash('/test/')
    'test/'

    >>> remove_prefix_including_first_slash_or_backslash('test\\\\')
    ''
    >>> remove_prefix_including_first_slash_or_backslash('test/test2/test3')
    'test2/test3'
    >>> remove_prefix_including_first_slash_or_backslash('test\\test3\\test4')
    'test\\test3\\test4'

    """
    result = input_str
    if '\\' in input_str:
        result = input_str.split('\\', 1)[1]
    elif '/' in input_str:
        result = input_str.split('/', 1)[1]
    return result
