import hou
import subprocess
import os
import re


def fix_path(old_path, new_sep='/'):
    """
    Will make sure all path have the same / or \.
    """
    _path = old_path.replace('\\', '/')
    _path = _path.replace('\\\\', '/')
    _path = _path.replace('//', '/')

    if _path.endswith('/'):
        _path = _path[:-1]

    _path = _path.replace('/', new_sep)

    new_path = _path
    return new_path


def fix_string(string):
    new = string.strip().replace(' ', '_')
    new = re.sub(r"[^A-Za-z0-9\_]+", '', new)
    return new


def error(message, severity=hou.severityType.Error):
    """
    Show & print error message with corresponding severity level.
    """
    print('{severity}: {message}'.format(severity=severity.name(), message=message))
    hou.ui.displayMessage(message, severity=severity)


def print_report(header, *body):    # Body will be a list of arguments
    """
    Print Reports in a nice way, for users.
    """
    final_header = ' {0} '.format(header)
    print('\n{header:-^50}'.format(header=final_header))

    for b in body:
        print('\t{0}'.format(b))

    print('-'*50)


def open_explorer(path):
    path = os.path.dirname(path)
    path = fix_path(path, os.path.sep)

    open_path = 'explorer {0}'.format(path)
    subprocess.Popen(open_path, shell=True)
    return