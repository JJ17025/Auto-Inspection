import os
from datetime import datetime
from json import loads
from pprint import pprint

import cv2
import fontTools.ttLib.woff2
import numpy as np
import pygame
import pygame_gui

from pygame_gui.core import ObjectID


def mkdir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


IMG_FULL_PATH = 'img_full'
IMG_FRAME_PATH = 'img_frame'
MODEL_PATH = 'model'

mkdir(IMG_FULL_PATH)
mkdir(IMG_FRAME_PATH)
mkdir(MODEL_PATH)


def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")
def brightness(img):
    brigh = np.average(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    return f'{brigh:.0f}/90'


pygame.init()
pygame.display.set_caption('M/L for Auto-inspection')
display = pygame.display.set_mode((1920, 1080))

surface_list = [
    {
        'ra': (1920, 40),
        'lo': (0, 0),
        'surface.color': '#070719'
    },
    {
        'ra': (1920, 40),
        'lo': (0, 40),
        'surface.color': '#111133'
    },
    {
        'ra': (1280, 960),
        'lo': (0, 80),
        'surface.color': '#333333'
    },
    {
        'ra': (640, 960),
        'lo': (1280, 80),
        'surface.color': '#222222'
    },
    {
        'ra': (1920, 40),
        'lo': (0, 1040),
        'surface.color': '#111133'
    },

]
surface = []
for i in range(len(surface_list)):
    surface.append(pygame.Surface(surface_list[i]['ra']))
    surface[i].fill(pygame.Color(surface_list[i]['surface.color']))

surface_for_img_show_list = []
for i in range(3):
    surface_for_img_show_list.append({
        'ra': (326*300//326, 244*300//326),
        'lo': (1290, 200 + 260 * i),
        'surface.color': '#333333'
    })
    surface_for_img_show_list.append({
        'ra': (326*300//326, 244*300//326),
        'lo': (1605, 200 + 260 * i),
        'surface.color': '#333333'
    })

surface_for_img_show = []
for i in range(len(surface_for_img_show_list)):
    surface_for_img_show.append(pygame.Surface(surface_for_img_show_list[i]['ra']))
    surface_for_img_show[i].fill(pygame.Color(surface_for_img_show_list[i]['surface.color']))

manager = []
for i in range(len(surface_list)):
    manager.append(pygame_gui.UIManager(surface_list[i]['ra'], 'theme.json'))
    manager[i].get_root_container().get_rect().topleft = surface_list[i]['lo']
manager.append(pygame_gui.UIManager((1920, 1080), 'theme.json'))

button_dict = {
    'exit': {
        'relative_rect': pygame.Rect((1800, 5), (120, 30)),
        'text': 'exit', 'manager': manager[0]
    },
    'b_ok': {
        'relative_rect': pygame.Rect((10 + 125 * 0, 10), (120, 30)),
        'text': 'ok all', 'manager': manager[3]
    },
    'b_on': {
        'relative_rect': pygame.Rect((10 + 125 * 1, 10), (120, 30)),
        'text': 'no part all', 'manager': manager[3]
    },
    'b_wp': {
        'relative_rect': pygame.Rect((10 + 125 * 2, 10), (120, 30)),
        'text': 'wrong part all', 'manager': manager[3]
    },
    'b_wpo': {
        'relative_rect': pygame.Rect((10 + 125 * 3, 10), (120, 30)),
        'text': 'wrong po all', 'manager': manager[3]
    },
    'cl_all': {
        'relative_rect': pygame.Rect((10 + 125 * 4, 10), (120, 30)),
        'text': 'cle all', 'manager': manager[3]
    },
    'save': {
        'relative_rect': pygame.Rect((10 + 155 * 0, 50), (150, 50)),
        'text': 'save', 'manager': manager[3]
    },
    're': {
        'relative_rect': pygame.Rect((10 + 155 * 1, 50), (150, 50)),
        'text': 're', 'manager': manager[3]
    },
    'del': {
        'relative_rect': pygame.Rect((10 + 155 * 2, 50), (150, 50)),
        'text': 'del', 'manager': manager[3]
    },
    'fps': {
        'relative_rect': pygame.Rect((5, 5), (100, 30)),
        'text': 'FPS', 'manager': manager[0]
    },
    'bn': {
        'relative_rect': pygame.Rect((110, 5), (100, 30)),
        'text': 'bn', 'manager': manager[0]
    },
    'xy0': {
        'relative_rect': pygame.Rect((260, 5), (150, 30)),
        'text': 'XY', 'manager': manager[0]
    },
    'xy2': {
        'relative_rect': pygame.Rect((110, 5), (150, 30)),
        'text': '...', 'manager': manager[1]
    },
    'xy3': {
        'relative_rect': pygame.Rect((1300, 5), (150, 30)),
        'text': '...', 'manager': manager[1]
    },

    '3264x2448': {
        'relative_rect': pygame.Rect((330, 5), (105, 30)),
        'text': '3264x2448', 'manager': manager[1]
    },
    '1024x768': {
        'relative_rect': pygame.Rect((440, 5), (105, 30)),
        'text': '1024x768', 'manager': manager[1]
    },
    '800x600': {
        'relative_rect': pygame.Rect((550, 5), (105, 30)),
        'text': '800x600', 'manager': manager[1]
    },
    '1600x1200': {
        'relative_rect': pygame.Rect((660, 5), (105, 30)),
        'text': '1600x1200', 'manager': manager[1]
    },
    'n_log_pF': {
        'relative_rect': pygame.Rect((1800, 5), (50, 30)),
        'text': '2', 'manager': manager[4]
    },
    'n_log_pT': {
        'relative_rect': pygame.Rect((1850, 5), (50, 30)),
        'text': '2+', 'manager': manager[4]
    },
}

button = {}
for k, v in button_dict.items():
    button[k] = pygame_gui.elements.UIButton(relative_rect=v['relative_rect'], text=v['text'], manager=v['manager'])

# DropDownMenu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((350, 350), (150, 50)),
#                                                   options_list=['1600x900', '1920x1080'],
#                                                   starting_option='1600x900',
#                                                   manager=manager[2])
a = 340
n = 380-120
Label_dict = {
    '0': {
        'relative_rect': pygame.Rect((10, a + n * 0), (320, 30)),
        'text': '...',
        'manager': manager[3]
    },
    '2': {
        'relative_rect': pygame.Rect((10, a + n * 1), (320, 30)),
        'text': '...',
        'manager': manager[3]
    },
    '4': {
        'relative_rect': pygame.Rect((10, a + n * 2), (320, 30)),
        'text': '...',
        'manager': manager[3]
    },
    '1': {
        'relative_rect': pygame.Rect((320, a + n * 0), (320, 30)),
        'text': '...',
        'manager': manager[3]
    },
    '3': {
        'relative_rect': pygame.Rect((320, a + n * 1), (320, 30)),
        'text': '...',
        'manager': manager[3]
    },
    '5': {
        'relative_rect': pygame.Rect((320, a + n * 2), (320, 30)),
        'text': '...',
        'manager': manager[3]
    },
    'n_all': {
        'relative_rect': pygame.Rect((10, 920), (640 - 10 - 10, 30)),
        'text': '...',
        'manager': manager[3]
    },
}
imgfullfile = {}
for k, v in Label_dict.items():
    imgfullfile[k] = pygame_gui.elements.UILabel(relative_rect=v['relative_rect'], text=v['text'], manager=v['manager'])
    # imgfullfile[k].set_text(f'{v["text"]}')

n_log = 50
n_log_p = False
text_out_log = ['-'] * n_log
log_UILabel = []
for i in range(n_log):
    log_UILabel.append(pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 1056 - 20 * i), (1920, 30)),
                                                   text='-',
                                                   manager=manager[5]))

clock = pygame.time.Clock()
is_running = True

###########################     cv     #################################################################

frames = loads(open(rf'frames pos.json').read())

status_list: list = ['nopart', 'ok', 'wrongpart', 'wrongpolarity', '']
status_short_list: list = ["no", "ok", "w_part", "w_po", '']

for k, v in frames.items():
    frames[k]['status'] = -1
    frames[k]['color_frame'] = (255, 255, 0)
    lo = v
    v['lo960'] = {
        'x1': int((lo['x'] - lo['dx'] / 2) * 1280),
        'y1': int((lo['y'] - lo['dy'] / 2) * 960),
        'x2': int((lo['x'] + lo['dx'] / 2) * 1280),
        'y2': int((lo['y'] + lo['dy'] / 2) * 960),
        'dx': int(lo['dx'] * 1280),
        'dy': int(lo['dy'] * 960)
    }
    Rect = (v['lo960']['x1'], v['lo960']['y1'], v['lo960']['dx'],
            v['lo960']['dy'])  # (left, top, width, height)

    font = pygame.font.Font('freesansbold.ttf', 10)
    v['text'] = font.render(k, True, (0, 255, 0), (255, 255, 255))
    v['textRect'] = v['text'].get_rect()
    v['textRect'].topleft = (v['lo960']['x1'], v['lo960']['y1'] + 80)


VideoCap = 1
cap = cv2.VideoCapture(VideoCap)
cap.set(3, 3264)

w = cap.get(3)
h = cap.get(4)

## show file ###########################################################################################
files_path = []
def re():
    print('re')
    global files_path
    files_path = os.listdir(IMG_FULL_PATH)
    files_path = list(set(file.split('.')[0] for file in files_path if file.endswith('.png')) &
                      set(file.split('.')[0] for file in files_path if file.endswith('.txt')))
    files_path = sorted(files_path, reverse=True)
    print(files_path)

    if len(files_path) == 0:
        imgfullfile['n_all'].set_text(f'There are no files in the folder.')
    elif len(files_path) == 1:
        imgfullfile['n_all'].set_text(f'There is 1 file in the folder.')
    else:
        imgfullfile['n_all'].set_text(f'There are {len(files_path)} files in the folder.')

    for i in range(6):
        if len(files_path) > i:
            imgfullfile[f'{i}'].set_text(f'{files_path[i]}')
            p = cv2.imread(rf"{IMG_FULL_PATH}\{files_path[i]}.png")
            p = cv2.resize(p, (326*300//326, 244*300//326))
            p = cv2.cvtColor(p, cv2.COLOR_BGR2RGB)
            surface_for_img_show[i] = cvimage_to_pygame(p)
        else:
            imgfullfile[f'{i}'].set_text('-')
            surface_for_img_show[i].fill(pygame.Color(surface_for_img_show_list[i]['surface.color']))


re()

################################################################################################
while is_running:
    time_delta = clock.tick(30) / 1000.0

    s, IMG = cap.read()
    if s == False:
        IMG = cv2.imread('BG.png')
    bn = brightness(IMG)

    img = IMG.copy()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # resize -----------------------------------------------------------------------------------
    img = cv2.resize(img, (1280, 960))
    surface[2] = cvimage_to_pygame(img)

    # print(img.shape)  # = (960, 1280, 3)
    ### mouse location  ########################################################################################
    x, y = pygame.mouse.get_pos()
    key = pygame.key.get_pressed()
    # if any(np.array(key)):
    #     print(np.where(np.array(key))[0].tolist())
    button['xy0'].set_text(f'XY {x}, {y}')
    button['fps'].set_text(f'FPS {1 / time_delta:.0f}')
    button['bn'].set_text(bn)

    xx, yy = x, y - 80
    if not (0 <= xx <= 1280 and 0 <= yy <= 960):
        xx = yy = -1
    button['xy2'].set_text(f"{xx}/{yy}")
    xxx, yyy = x - 1280, y - 80
    if not (0 <= xxx <= 640 and 0 <= yyy <= 960):
        xxx = yyy = -1
    button['xy3'].set_text(f"{xxx}/{yyy}")

    click_mouse = 0
    ###########################################################################################################
    for event in pygame.event.get():
        # manager process_events
        for m in manager:
            m.process_events(event)

        if event.type == 1025:  # 1025-MouseButtonDown
            click_mouse = event.dict['button']

        for i in range(n_log - 1):
            text_out_log[n_log - 1 - i] = text_out_log[n_log - 2 - i]
        text_out_log[0] = f'{event}'

        for i in range(n_log):
            if not n_log_p and i > 1:
                log_UILabel[i].set_text(f'')
            else:
                log_UILabel[i].set_text(f'{text_out_log[i]}')

        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button['exit']:
                is_running = False
            if event.ui_element == button['b_ok']:
                for k, v in frames.items():
                    v['status'] = 1
            if event.ui_element == button['b_on']:
                for k, v in frames.items():
                    v['status'] = 0
            if event.ui_element == button['b_wp']:
                for k, v in frames.items():
                    v['status'] = 2
            if event.ui_element == button['b_wpo']:
                for k, v in frames.items():
                    v['status'] = 3
            if event.ui_element == button['cl_all']:
                for k, v in frames.items():
                    v['status'] = -1

            if event.ui_element == button['save']:
                string = ''
                for k, v in frames.items():
                    if v['status'] != len(status_list) - 1 and v['status'] != - 1:
                        lo = v
                        string += f"{k}:{status_list[v['status']]}:{lo['x']}:{lo['y']}:{lo['dx']}:{lo['dy']}\n"
                if string:
                    filename = datetime.now().strftime('%m%d-%H%M%S')
                    path = f"{IMG_FULL_PATH}/{filename}"

                    cv2.imwrite(f'{path}.png', IMG)
                    open(f'{path}.txt', 'w').write(string)

                    imgs = os.listdir(IMG_FRAME_PATH)
                    print(imgs)
                    print(string)
                else:
                    print('no input')
                re()

            if event.ui_element == button['re']:
                print('re')
                re()

            if event.ui_element == button['del']:
                if files_path:
                    os.remove(f"{IMG_FULL_PATH}/{files_path[0]}.txt")
                    os.remove(f"{IMG_FULL_PATH}/{files_path[0]}.png")
                else:
                    print('There are no files in the folder.')
                re()

            if event.ui_element == button['1600x1200']:
                cap = cv2.VideoCapture(VideoCap)
                cap.set(3, 1600)
            if event.ui_element == button['800x600']:
                cap = cv2.VideoCapture(VideoCap)
                cap.set(3, 800)
            if event.ui_element == button['1024x768']:
                cap = cv2.VideoCapture(VideoCap)
                cap.set(3, 1024)
            if event.ui_element == button['3264x2448']:
                cap = cv2.VideoCapture(VideoCap)
                cap.set(3, 3264)

            if event.ui_element == button['n_log_pF']:
                n_log_p = False
            if event.ui_element == button['n_log_pT']:
                n_log_p = True

        # if event.type == pygame.MOUSEMOTION:
    ###################################################################################
    for k, v in frames.items():
        lo = v['lo960']
        if lo['x1'] < xx < lo['x2'] and lo['y1'] < yy < lo['y2']:
            v['color_frame'] = (255, 0, 0)
            if click_mouse in [5, 7, 9, 11, 13]:  # หมุนลูกกลิ้ง
                v['status'] += 1
                if v['status'] > len(status_list) - 1:
                    v['status'] = 0
            if click_mouse in [4, 6, 8, 10, 12]:  # หมุนลูกกลิ้ง
                v['status'] -= 1
                if v['status'] < 0:
                    v['status'] = len(status_list) - 1
            if click_mouse == 3:  # คลิกขวา
                v['status'] = - 1
        else:
            v['color_frame'] = (255, 255, 0)

        text_co = (255, 255, 100)
        text = f'{k}{status_short_list[v["status"]]}'
        if v['status'] == 0:
            text_co = (255, 0, 0)
        if v['status'] == 1:
            text_co = (0, 255, 0)
        if v['status'] == 2:
            text_co = (255, 0, 255)
        if v['status'] == 3:
            text_co = (0, 255, 255)

        v['text'] = font.render(f'{text}', True, text_co, (10, 10, 10))

    ###########################################################################################################
    # ---  frames กรอบเหลือง  --------------------------------
    for k, v in frames.items():
        pygame.draw.rect(surface[2],
                         v['color_frame'],
                         pygame.Rect(v['lo960']['x1'], v['lo960']['y1'], v['lo960']['dx'], v['lo960']['dy']),
                         1)

    ###########################################################################################################
    for i in range(len(surface)):
        display.blit(surface[i], surface_list[i]['lo'])
    for i in range(len(surface_for_img_show)):
        display.blit(surface_for_img_show[i], surface_for_img_show_list[i]['lo'])

    for k, v in frames.items():
        display.blit(v['text'], v['textRect'])

    for m in manager:
        m.update(time_delta)
        m.draw_ui(display)

    pygame.display.update()
