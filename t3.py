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


def p(*args, sep=' ', end='\n',**kwargs):
    for arg in args:
        print(f'{PINK}{arg}{ENDC}', sep, sep='', end='')
    print(end='\n')



