import json
import math
import os
import random
from datetime import datetime
from json import loads
from pprint import pprint
import cv2
# import fontTools.ttLib.woff2
import numpy as np
import pygame
import pygame_gui


def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")


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

manager = []
for i in range(len(surface_list)):
    manager.append(pygame_gui.UIManager(surface_list[i]['ra'], 'theme.json'))
    manager[i].get_root_container().get_rect().topleft = surface_list[i]['lo']
manager.append(pygame_gui.UIManager((1920, 1080), 'theme.json'))

button_dict = {
    'fps': {
        'relative_rect': pygame.Rect((5, 5), (100, 30)),
        'text': 'FPS', 'manager': manager[0]
    },
    'xy0': {
        'relative_rect': pygame.Rect((110, 5), (150, 30)),
        'text': 'XY', 'manager': manager[0]
    },
    'getcap': {
        'relative_rect': pygame.Rect((300, 5), (200, 30)),
        'text': '-,-', 'manager': manager[0]
    },
    'exit': {
        'relative_rect': pygame.Rect((1800, 5), (120, 30)),
        'text': 'exit', 'manager': manager[0]
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
    '320x240': {
        'relative_rect': pygame.Rect((660, 5), (105, 30)),
        'text': '320x240', 'manager': manager[1]
    },

    'playstop': {
        'relative_rect': pygame.Rect((880, 5), (105, 30)),
        'text': 'STOP', 'manager': manager[1]
    },
    'save_frames': {
        'relative_rect': pygame.Rect((1800, 5), (120, 30)),
        'text': 'save frames', 'manager': manager[1]
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

n_log = 50
n_log_p = False
text_out_log = ['-'] * n_log
log_UILabel = []
for i in range(n_log):
    log_UILabel.append(pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 1056 - 20 * i), (1920, 30)),
                                                   text='-',
                                                   manager=manager[5]))

frames_uilabel = {
    'label':
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((30, 10), (400, 30)), text='', manager=manager[3]),
    'marquee_button':
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((30, 50), (40, 30)), text='m', manager=manager[3]),
    'selection_button':
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((80, 50), (40, 30)), text='s', manager=manager[3]),

    'entrybox':
        pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect((30, 90), (200, 30)), initial_text="", manager=manager[3]),
    'add_button':
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((230, 90), (70, 30)), text='add', manager=manager[3]),
    'error_label':
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((310, 90), (320, 30)), text='', manager=manager[3]),

    'buf_text': '',
    'tool_select': ''

}

frames_uilabel['marquee_button'].get_focus_set()
font = pygame.font.Font('freesansbold.ttf', 10)


class Frame:
    def __init__(self, name, x, y, dx, dy, w, h):
        self.name = name
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.original_w = w
        self.original_h = h
        self.used_w = None
        self.used_h = None

        self.x1 = self.x - self.dx / 2
        self.x2 = self.x + self.dx / 2
        self.y1 = self.y - self.dy / 2
        self.y2 = self.y + self.dy / 2

        self.status_list = ['nopart', 'ok', 'wrongpart', 'wrongpolarity']
        self.color_frame = (255, 255, 0)
        self.frame_select = False

    def __str__(self):
        return f'Frame({self.name}, {self.x:.2f}, {self.y:.2f})'

    def move_frame(self):
        self.x1 = self.x - self.dx / 2
        self.x2 = self.x + self.dx / 2
        self.y1 = self.y - self.dy / 2
        self.y2 = self.y + self.dy / 2
        self.settext()

    def resize_to_px(self, w, h):  # 1280x960
        self.used_w = w
        self.used_h = h

        self.rx = int(self.x * w)
        self.rdx = int(self.dx * w)
        self.ry = int(self.y * h)
        self.rdy = int(self.dy * h)

        self.rx1 = int(self.x1 * w)
        self.rx2 = int(self.x2 * w)
        self.ry1 = int(self.y1 * h)
        self.ry2 = int(self.y2 * h)

    def settext(self):
        pos = ''
        if self.frame_select:
            pos = [round(i, 3) for i in (self.x, self.y, self.dx, self.dy)]
        self.text = font.render(f'{self.name} {pos}', True, (0, 255, 0), (0, 0, 0))
        self.textRect = self.text.get_rect()
        self.resize_to_px(1280, 960)
        self.textRect.topleft = (self.rx1, self.ry1 + 65)



class Frames:
    def __init__(self, frames_file_name=None):
        self.frames = {}

        if frames_file_name:
            with open(frames_file_name, 'r') as file_read:
                frames: dict = json.load(file_read)

            for name, frame in frames.items():
                '''
                {
                    "a1":{"x": 0.5, "y": 0.5, "dx": 0.1, "dy": 0.2, "w": 100, "h": 100},
                    "a2":{"x": 0.8, "y": 0.5, "dx": 0.1, "dy": 0.2, "w": 100, "h": 100}
                }
                '''
                print(name, frame)
                self.add_frame(name, **frame)

    def __str__(self):
        return f'Frames{tuple(self.frames.keys())}'

    def add_frame(self, name, **frame_properties):
        self.frames[name] = Frame(name, **frame_properties)
        self.frames[name].settext()

    def save_frame_pos(self):
        all_frames_dict = {}
        for name, frame in self.frames.items():
            frame_dict = {}
            print(frame)
            frame_dict['x'] = frame.x
            frame_dict['y'] = frame.y
            frame_dict['dx'] = frame.dx
            frame_dict['dy'] = frame.dy
            frame_dict['w'] = frame.original_w
            frame_dict['h'] = frame.original_h
            all_frames_dict[name] = frame_dict

        with open('frames pos.json', 'w') as file:
            file.write(json.dumps(all_frames_dict, indent=4))


clock = pygame.time.Clock()
is_running = True

###########################     cv     #################################################################


frames = Frames('frames pos.json')
print(frames)
VideoCap = 1
cap = cv2.VideoCapture(VideoCap)
cap.set(3, 3264)

w = cap.get(3)
h = cap.get(4)


def capture():
    # s, IMG = cap.read()
    s = False
    if s == False:
        IMG = cv2.imread(r'Save Image\230922 174728.png')
    img = IMG.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img, IMG


def save_setting_frames():
    frames.save_frame_pos()


def add_frame():
    global frames_setup
    x1 = min(frames_setup['x1'], frames_setup['x2'])
    x2 = max(frames_setup['x1'], frames_setup['x2'])
    y1 = min(frames_setup['y1'], frames_setup['y2'])
    y2 = max(frames_setup['y1'], frames_setup['y2'])

    x = (x1 + (x2 - x1) / 2) / 1280
    y = (y1 + (y2 - y1) / 2) / 960
    dx = (x2 - x1) / 1280
    dy = (y2 - y1) / 960

    name = frames_uilabel['buf_text']

    print(y2 - y1)
    if x2 - x1 < 5 or y2 - y1 < 5:
        frames_uilabel['error_label'].set_text('error: frame too narrow.')
    elif name == '':
        frames_uilabel['error_label'].set_text('error: Specifies the name of the frame.')
    else:
        frames.frames[name] = Frame(name, x, y, dx, dy, w, h)
        frames.frames[name].settext()
        frames.frames[name].resize_to_px(1280, 960)

        frames_uilabel['error_label'].set_text('')
        frames_uilabel['entrybox'].set_text(name[:-1] + chr(ord(name[-1]) + 1))
        frames_uilabel['buf_text'] = name[:-1] + chr(ord(name[-1]) + 1)
        frames_setup = {'x1': 0, 'x2': 0, 'y1': 0, 'y2': 0}


frames_list = []
frames_setup = {'x1': 0, 'x2': 0, 'y1': 0, 'y2': 0}

key_unicode = None
play = True
################################################################################################
while is_running:
    time_delta = clock.tick(60) / 1000.0

    if play == True:
        img, IMG = capture()

    # resize -----------------------------------------------------------------------------------
    img = cv2.resize(img, (1280, 960))
    surface[2] = cvimage_to_pygame(img)

    ### mouse location  ########################################################################################
    x, y = pygame.mouse.get_pos()
    button['xy0'].set_text(f'XY {x}, {y}')
    button['fps'].set_text(f'FPS {1 / time_delta:.0f}')
    button['getcap'].set_text(f'shape {IMG.shape[:2]}')

    xx, yy = x, y - 80
    if xx > 1280 - 1:
        xx = 1280 - 1
    if xx < 0:
        xx = 0
    if yy > 960 - 1:
        yy = 960 - 1
    if yy < 0:
        yy = 0
    button['xy2'].set_text(f"{xx}/{yy}")

    xxx, yyy = x - 1280, y - 80
    if not (0 <= xxx <= 640 and 0 <= yyy <= 960):
        xxx = yyy = -1
    button['xy3'].set_text(f"{xxx}/{yyy}")

    x1, x2, y1, y2 = frames_setup['x1'], frames_setup['x2'], frames_setup['y1'], frames_setup['y2']
    frames_uilabel['label'].set_text(
        f"{[x1, y1, x2, y2]}  {x1 / 1280:.2f} {y1 / 960:.2f} {x2 / 1280:.2f} {y2 / 960:.2f}")

    click_mouse = 0
    ###########################################################################################################
    for event in pygame.event.get():
        if event.type == 768:  # press the keyboard button
            key_unicode = event.dict['unicode']
            key_scancode = event.dict['scancode']
            if key_unicode == '\r':
                add_frame()
            if key_unicode == '\x7f':  # press delete
                print(1)
                pass

            if key_unicode in '+-*/':
                for name, frame in frames.frames.items():
                    if frame.frame_select:
                        if key_unicode == '-':
                            frame.dy -= 0.001
                        if key_unicode == '+':
                            frame.dy += 0.001
                        if key_unicode == '/':
                            frame.dx -= 0.001
                        if key_unicode == '*':
                            frame.dx += 0.001
                        frame.move_frame()

            if key_scancode in [82, 81, 80, 79]:
                for name, frame in frames.frames.items():
                    if frame.frame_select:
                        if key_scancode == 82:
                            frame.y -= 0.001
                        if key_scancode == 81:
                            frame.y += 0.001
                        if key_scancode == 80:
                            frame.x -= 0.001
                        if key_scancode == 79:
                            frame.x += 0.001
                        frame.move_frame()

        if event.type == 769:
            key_unicode = None

        # manager process_events
        for m in manager:
            m.process_events(event)

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

        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_element == frames_uilabel['entrybox']:
            frames_uilabel['buf_text'] = event.text.replace('\n', '').replace('\r', '')
            frames_uilabel['entrybox'].set_text(frames_uilabel['buf_text'])

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button['exit']:
                is_running = False
            if event.ui_element == button['save_frames']:
                save_setting_frames()

            if event.ui_element == frames_uilabel['marquee_button']:
                frames_uilabel['tool_select'] = 'marquee_button'
                frames_uilabel['marquee_button'].disable()
                frames_uilabel['selection_button'].enable()

            if event.ui_element == frames_uilabel['selection_button']:
                frames_uilabel['tool_select'] = 'marquee_button'
                frames_uilabel['selection_button'].disable()
                frames_uilabel['marquee_button'].enable()

            if event.ui_element == frames_uilabel['add_button']:
                add_frame()

            if event.ui_element == button['playstop']:
                if button['playstop'].text == 'STOP':
                    button['playstop'].set_text('PLAY')
                    play = False
                elif button['playstop'].text == 'PLAY':
                    button['playstop'].set_text('STOP')
                    play = True

            if event.ui_element == button['320x240']:
                if IMG.shape[:2] != (240, 320):
                    cap = cv2.VideoCapture(VideoCap)
                    cap.set(3, 320)
                img, IMG = capture()

            if event.ui_element == button['800x600']:
                if IMG.shape[:2] != (600, 800):
                    cap = cv2.VideoCapture(VideoCap)
                    cap.set(3, 800)
                img, IMG = capture()

            if event.ui_element == button['1024x768']:
                if IMG.shape[:2] != (768, 1024):
                    cap = cv2.VideoCapture(VideoCap)
                    cap.set(3, 1024)
                img, IMG = capture()

            if event.ui_element == button['3264x2448']:
                if IMG.shape[:2] != (2448, 3264):
                    cap = cv2.VideoCapture(VideoCap)
                    cap.set(3, 3264)
                img, IMG = capture()

            if event.ui_element == button['n_log_pF']:
                n_log_p = False
            if event.ui_element == button['n_log_pT']:
                n_log_p = True
        ### อยู่ใน sf2  #############################################################
        if 0 < xx < 1280 - 1 and 0 < yy < 960 - 1:
            if event.type == 1025:  # คลิกเมาส์1
                click_mouse = event.dict['pos']
                frames_setup['x1'], frames_setup['y1'] = xx, yy
                frames_setup['x2'], frames_setup['y2'] = xx, yy
            if event.type == 1024:  # ลากเมาส์
                if event.dict['buttons'] == (1, 0, 0):  # คลิกเมาส์1 ค้าง
                    frames_setup['x2'], frames_setup['y2'] = xx, yy
            if event.type == 1026:  # ปล่อยคลิกเมาส์1
                frames_setup['x2'], frames_setup['y2'] = xx, yy
                print(frames_setup['x1'], frames_setup['y1'])

        ### เมาส์ชี้ที่กรอบ ######################################################
        for name, frame in frames.frames.items():
            frame.resize_to_px(1280, 960)
            if frame.rx1 < xx < frame.rx2 and frame.ry1 < yy < frame.ry2:
                frame.color_frame = (255, 0, 255)
                if event.type == pygame.MOUSEBUTTONUP:
                    # if frame.frame_select == True:
                    #     frame.frame_select = False
                    # else:
                    frame.frame_select = True

                if key_unicode == '\x7f':
                    frames.frames.pop(name)
                    break

            else:
                frame.color_frame = (255, 255, 0)
                if event.type == pygame.MOUSEBUTTONUP:
                    frame.frame_select = False

    ###########################################################################################################

    ###########################################################################################################
    # ---  frames กรอบแดง  --------------------------------

    x1 = min(frames_setup['x1'], frames_setup['x2'])
    x2 = max(frames_setup['x1'], frames_setup['x2'])
    y1 = min(frames_setup['y1'], frames_setup['y2'])
    y2 = max(frames_setup['y1'], frames_setup['y2'])
    pygame.draw.rect(surface[2], (255, 0, 0), pygame.Rect(x1, y1, x2 - x1, y2 - y1), 1)
    # ---  frames กรอบเหลือง  --------------------------------
    for name, frame in frames.frames.items():
        # print(k, fr[k].rx1, fr[k].ry1, fr[k].rdx, fr[k].rdy)
        if frame.frame_select == True:
            pygame.draw.rect(surface[2],
                             (255, 255, 255),
                             pygame.Rect(frame.rx1 - 2, frame.ry1 - 2, frame.rdx + 4, frame.rdy + 4),
                             3)
            pygame.draw.rect(surface[2],
                             (0, 0, 0),
                             pygame.Rect(frame.rx1 - 1, frame.ry1 - 1, frame.rdx + 2, frame.rdy + 2),
                             2)
        pygame.draw.rect(surface[2],
                         frame.color_frame,
                         pygame.Rect(frame.rx1, frame.ry1, frame.rdx, frame.rdy),
                         1)

    # ---  เส้นประ  --------------------------------
    if 0 < xx < 1280 - 1 and 0 < yy < 960 - 1:  # อยู่ใน sf2
        pygame.draw.line(surface[2], (255, 255, 255), (xx, 0), (xx, 960), 1)
        pygame.draw.line(surface[2], (255, 255, 255), (0, yy), (1280, yy), 1)
        for i in range(0, 960, 10):
            pygame.draw.line(surface[2],
                             (random.randint(0, 200), random.randint(0, 100), random.randint(0, 200)),
                             (xx, i), (xx, i + 5), 1)
        for i in range(0, 1280, 10):
            pygame.draw.line(surface[2],
                             (random.randint(0, 200), random.randint(0, 100), random.randint(0, 200)),
                             (i, yy), (i + 5, yy), 1)
    ###########################################################################################################
    for i in range(len(surface)):
        display.blit(surface[i], surface_list[i]['lo'])

    # ---  text (frames กรอบเหลือง)  --------------------------------
    for name, frame in frames.frames.items():
        display.blit(frame.text, frame.textRect)

    for m in manager:
        m.update(time_delta)
        m.draw_ui(display)

    pygame.display.update()
