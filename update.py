BLACK = '\033[90m'
FAIL = '\033[91m'
GREEN = '\033[92m'
WARNING = '\033[93m'
BLUE = '\033[94m'
PINK = '\033[95m'
CYAN = '\033[96m'
ENDC = '\033[0m'
BOLD = '\033[1m'
ITALICIZED = '\033[3m'
UNDERLINE = '\033[4m'
import requests
from bs4 import BeautifulSoup
import subprocess
import os


def update_a_program():
    os.system('echo %cd%')

    result = subprocess.run('git status', capture_output=True, text=True)
    if result.stdout.split('\n')[1] == 'nothing to commit, working tree clean':
        print(GREEN, 'All files have not been changed.', ENDC, sep='')
        r = requests.get('https://github.com/JJ17025/Auto-Inspection/commit/m2')
        soup = BeautifulSoup(r.content, 'html.parser')
        new_v = soup.find('span', {'class': 'sha user-select-contain'}).text

        result = subprocess.run('git log --oneline', capture_output=True, text=True)
        old_v = result.stdout[:7]
        if new_v != old_v:
            print(FAIL, 'old_v', old_v, ENDC, sep='')
            print(GREEN, 'new_v', new_v, ENDC, sep='')
            result = subprocess.run('git pull origin m2', capture_output=True, text=True)
            print(result.stdout)
        else:
            print(GREEN, 'programe is the latest version.', ENDC, sep='')
    else:
        print(WARNING, 'file have been changed.', ENDC, sep='')
