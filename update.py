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

import subprocess
import os
import sys


def install_requests_and_soup():
    result = subprocess.run('pip freeze', capture_output=True, text=True)
    if 'beautifulsoup4' and 'requests' not in [lib.split('==')[0] for lib in result.stdout.split('\n')]:
        result = subprocess.run('pip install requests', capture_output=True, text=True)
        if result.stdout:
            print(GREEN, '\n'.join([f for f in result.stdout.split('\n') if 'Successfully' in f]), ENDC, sep='')
        else:
            print(FAIL, '\n'.join([f for f in result.stderr.split('\n') if 'ERROR:' in f]), ENDC, sep='')
            input(f'{WARNING}connect internet to download library and Open the program again.{ENDC}')

        result = subprocess.run('pip install beautifulsoup4', capture_output=True, text=True)
        if result.stdout:
            print(GREEN, '\n'.join([f for f in result.stdout.split('\n') if 'Successfully' in f]), ENDC, sep='')
        else:
            print(FAIL, '\n'.join([f for f in result.stderr.split('\n') if 'ERROR:' in f]), ENDC, sep='')
            input(f'{WARNING}connect internet to download library and Open the program again.{ENDC}')


def update_a_program():
    import requests
    from bs4 import BeautifulSoup

    result = subprocess.run('git status', capture_output=True, text=True)
    if result.stdout.split('\n')[1] == 'nothing to commit, working tree clean':
        all_file = 'unchanged'
    else:
        all_file = 'change'
        print(WARNING, UNDERLINE, 'พบ file ถูกแก้ไข', ENDC, sep='')
        print(WARNING, '\n'.join(f.strip('\t') for f in result.stdout.split('\n') if '\t' in f), ENDC, sep='')

    try:
        r = requests.get('https://github.com/JJ17025/Auto-Inspection/commit/m2')
        req = 'ok'
    except:
        print(FAIL, 'Request to github error', ENDC, sep='')
        req = 'not ok'

    if req == 'ok':
        soup = BeautifulSoup(r.content, 'html.parser')
        new_v = soup.find('span', {'class': 'sha user-select-contain'}).text

        result = subprocess.run('git log --oneline', capture_output=True, text=True)
        old_v = result.stdout[:7]
        if new_v != old_v:
            print(FAIL, 'old_v: ', old_v, ENDC, sep='')
            print(GREEN, 'new_v: ', new_v, ENDC, sep='')
            if all_file == 'unchanged':
                result = subprocess.run('git pull origin m2', capture_output=True, text=True)
                print(result.stdout)
            print(GREEN, 'Update program OK.', ENDC, sep='')
        else:
            print(GREEN, 'Program is the latest version.', ENDC, sep='')


def activate_venv_and_run_program():
    venv_activate_script = '.venv/Scripts/activate.bat'
    if not os.path.exists(venv_activate_script):
        print(f"Error: Virtual environment activate script not found at {venv_activate_script}")
        sys.exit(1)

    activate_cmd = f'call {venv_activate_script}'
    python_cmd = 'python'
    main_py_path = 'main.py'
    combined_command = f'{activate_cmd} && {python_cmd} {main_py_path}'

    try:
        subprocess.run(combined_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(FAIL, f"Error executing main.py: {e}", ENDC, sep='')


if __name__ == "__main__":
    install_requests_and_soup()
    update_a_program()
    activate_venv_and_run_program()
